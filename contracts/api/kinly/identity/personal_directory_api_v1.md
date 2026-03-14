---
Domain: Identity
Capability: Personal Directory API
Scope: backend
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
---

# Personal Directory API v1

Status: Proposed

Scope: Backend RPCs, storage invariants, and access rules for Personal
Directory.

Audience: Product, design, engineering, AI agents.

Depends on:
- Personal Directory Contract v1
- Homes v2

## 1. Access model

- Caller MUST be authenticated for all RPCs.
- Own-record mutations enforce `auth.uid() = owner_user_id`.
- Read RPCs for another member's directory require shared active home
  membership.
- Read RPCs for the caller's own directory require only authentication
  (no home membership needed).
- Direct client table DML MUST be denied; tables are RPC-only.

## 2. Canonical enums

### 2.1 `personal_directory_note_type`
- `emergency_contact`
- `allergies`
- `other`

## 3. Storage model and invariants

### 3.1 `personal_directory_bank_accounts`

Required fields:
- `id uuid pk`
- `user_id uuid fk profiles(id)`
- `account_holder_name text`
- `account_number text`
- `created_at timestamptz`
- `updated_at timestamptz`

Required constraints:
- one bank account per user: `unique(user_id)`
- `account_holder_name` must be non-empty after trim, max length `120`
- `account_number` must be non-empty after trim, max length `50`
- rows MUST NOT be deleted; only updated in place

### 3.2 `personal_directory_notes`

Required fields:
- `id uuid pk`
- `user_id uuid fk profiles(id)`
- `note_type text`
- `custom_title text null`
- `contact_name text null`
- `phone_number text null`
- `details text null`
- `photo_path text null`
- `archived_at timestamptz null`
- `created_at timestamptz`
- `updated_at timestamptz`

Required constraints:
- `note_type` in canonical enum list
- `note_type='other'` requires non-empty trimmed `custom_title` length
  `1..80`
- non-`other` types require `custom_title is null`
- `note_type='emergency_contact'` requires non-empty `contact_name` and
  non-empty `phone_number`
- `contact_name` and `phone_number` MUST be null for non-`emergency_contact`
  types
- `details` is required (non-empty after trim) for `allergies` and `other`
- `details` is optional for `emergency_contact`
- `photo_path` may be null; if present it must be a storage reference under
  `users/%/personal_directory/`
- at most one photo path per active note row in v1
- at most one active (non-archived) note per user for `emergency_contact`
- at most one active (non-archived) note per user for `allergies`
- at most 20 active (non-archived) notes per user for `other`
- `contact_name` max length `120`
- `phone_number` max length `30`
- `details` max length `2000`

### 3.3 `personal_directory_nudge_dismissals`

Required fields:
- `user_id uuid fk profiles(id)`
- `home_id uuid fk homes(id)`
- `dismissed_at timestamptz`

Required constraints:
- primary key: `(user_id, home_id)`
- at most one dismissal per user per home

Behavioral invariants:
- a dismissed nudge MUST NOT reappear for the same `(user_id, home_id)`
- nudge MAY re-surface when the user joins a different home (different
  `home_id`)

## 4. RPC contract

### 4.1 `get_personal_directory_bank_account() -> jsonb`

Caller: authenticated user (own record).

Returns:
- `bank_account` object or `null` if not yet created

Canonical response shape:

```json
{
  "ok": true,
  "bank_account": {
    "id": "uuid",
    "account_holder_name": "text",
    "account_number": "text",
    "created_at": "timestamptz",
    "updated_at": "timestamptz"
  }
}
```

### 4.2 `upsert_personal_directory_bank_account(p_account_holder_name text, p_account_number text) -> jsonb`

Caller: authenticated user (own record).

Behavior:
- creates the bank account if none exists; updates in place if one exists
- both fields are required and trimmed for validation
- response returns the full bank account object

### 4.3 `get_personal_directory_notes(p_target_user_id uuid|null default null) -> jsonb`

Caller: authenticated user.

Behavior:
- if `p_target_user_id` is null or equals `auth.uid()`, returns the
  caller's own notes
- if `p_target_user_id` is a different user, caller MUST share an active
  home with that user; otherwise returns `NOT_HOME_MEMBER`
- archived notes are excluded

Returns:
- `notes` array ordered by: default types first (`emergency_contact`,
  `allergies` in that order), then `other` notes by `created_at` desc,
  then `id`

Canonical response shape:

```json
{
  "ok": true,
  "user_id": "uuid",
  "notes": [
    {
      "id": "uuid",
      "note_type": "text",
      "title": "text",
      "contact_name": "text|null",
      "phone_number": "text|null",
      "details": "text|null",
      "photo_path": "text|null",
      "created_at": "timestamptz",
      "updated_at": "timestamptz"
    }
  ]
}
```

Note: `title` in the response is derived from `note_type` label for default
types or from `custom_title` for `other`.

### 4.4 `get_member_bank_account(p_target_user_id uuid) -> jsonb`

Caller: authenticated user sharing an active home with the target user.

Purpose: used by the expenses-to-pay surface to retrieve a specific
member's bank account for payment.

Behavior:
- if `p_target_user_id = auth.uid()`, returns the caller's own bank
  account without a home membership check
- otherwise, caller MUST share an active home with `p_target_user_id`;
  returns `NOT_HOME_MEMBER` if not
- returns `bank_account` object or `null` if the target has not added one

Canonical response shape:

```json
{
  "ok": true,
  "user_id": "uuid",
  "bank_account": {
    "id": "uuid",
    "account_holder_name": "text",
    "account_number": "text"
  }
}
```

### 4.5 `upsert_personal_directory_note(p_note_id uuid|null default null, p_note_type text, p_custom_title text|null default null, p_contact_name text|null default null, p_phone_number text|null default null, p_details text|null default null, p_photo_path text|null default null) -> jsonb`

Caller: authenticated user (own record).

Behavior:
- create (when `p_note_id` is null) or update (when `p_note_id` matches
  an existing active note owned by the caller)
- `note_type` MUST NOT change on update; if the supplied `p_note_type`
  differs from the existing note's type, return
  `PERSONAL_DIRECTORY_NOTE_TYPE_CHANGE_FORBIDDEN` — the user must archive
  and recreate instead
- enforces type uniqueness on creation: rejects if an active note of the
  same default type already exists
- enforces `other` note cap on creation: rejects if 20 active `other`
  notes already exist
- `emergency_contact` requires `p_contact_name` and `p_phone_number`;
  `p_details` is optional
- `allergies` and `other` require `p_details`
- `other` requires `p_custom_title`
- `photo_path` must match `users/%/personal_directory/` when present
- photos are free; no paywall enforcement

### 4.6 `archive_personal_directory_note(p_note_id uuid) -> jsonb`

Caller: authenticated user (own record).

Behavior:
- soft-archives the note by setting `archived_at`
- idempotent shape via `already_archived`
- only the owning user can archive their own notes

### 4.7 `get_personal_directory_nudge(p_home_id uuid) -> jsonb`

Caller: authenticated user with active membership in the given home.

Behavior:
- checks whether the personal directory completeness nudge should be shown
- the nudge is eligible when ALL of the following are true:
  - at least one of: no bank account, no active `emergency_contact` note,
    or no active `allergies` note
  - the nudge has not been dismissed for this `(user_id, home_id)`
- when eligible, returns a `missing` array listing which records are absent

Returns:
- `show` boolean
- `missing` array of missing record labels (empty when `show` is false)

Canonical response shape:

```json
{
  "ok": true,
  "show": true,
  "missing": ["bank_account", "emergency_contact", "allergies"]
}
```

### 4.8 `dismiss_personal_directory_nudge(p_home_id uuid) -> jsonb`

Caller: authenticated user with active membership in the given home.

Behavior:
- records a dismissal for `(auth.uid(), p_home_id)`
- idempotent: dismissing an already-dismissed nudge returns
  `already_dismissed=true`

## 5. Error envelope and codes

Error envelope:

```json
{ "code": "STRING_CODE", "message": "Human readable", "details": {} }
```

Required codes:
- `UNAUTHORIZED`
- `NOT_HOME_MEMBER`
- `PERSONAL_DIRECTORY_INVALID_ENUM`
- `PERSONAL_DIRECTORY_INVALID_INPUT`
- `PERSONAL_DIRECTORY_BANK_ACCOUNT_REQUIRED_FIELDS`
- `PERSONAL_DIRECTORY_NOTE_REQUIRED_FIELDS`
- `PERSONAL_DIRECTORY_EMERGENCY_CONTACT_REQUIRED_FIELDS`
- `PERSONAL_DIRECTORY_OTHER_TITLE_REQUIRED`
- `PERSONAL_DIRECTORY_OTHER_TITLE_FORBIDDEN`
- `PERSONAL_DIRECTORY_CONTACT_FIELDS_FORBIDDEN`
- `PERSONAL_DIRECTORY_NOTE_TYPE_CONFLICT`
- `PERSONAL_DIRECTORY_NOTE_TYPE_CHANGE_FORBIDDEN`
- `PERSONAL_DIRECTORY_OTHER_NOTE_LIMIT_REACHED`
- `PERSONAL_DIRECTORY_NOTE_NOT_FOUND`
- `PERSONAL_DIRECTORY_NOTE_INVALID_PHOTO_PATH`

## 6. Privacy and security requirements

- Bank account `account_number` is sensitive operational data.
- Logging and telemetry MUST NOT include `account_number` values.
- `get_member_bank_account` MUST enforce shared home membership.
- Own-record RPCs MUST enforce `auth.uid()` ownership.

## 7. Contract test scenarios

- Authenticated user reads own bank account (returns object or null).
- Upsert bank account creates on first call; updates on subsequent calls.
- Bank account upsert without `account_holder_name` fails with
  `PERSONAL_DIRECTORY_BANK_ACCOUNT_REQUIRED_FIELDS`.
- Bank account upsert without `account_number` fails with
  `PERSONAL_DIRECTORY_BANK_ACCOUNT_REQUIRED_FIELDS`.
- Home member reads another member's notes via `get_personal_directory_notes`.
- Non-home-member cannot read another user's notes; returns `NOT_HOME_MEMBER`.
- Home member reads another member's bank account via `get_member_bank_account`.
- Non-home-member cannot read another user's bank account; returns
  `NOT_HOME_MEMBER`.
- `get_member_bank_account` returns null when target has no bank account.
- User with no home reads own bank account and notes successfully.
- Emergency contact note without `contact_name` or `phone_number` fails
  with `PERSONAL_DIRECTORY_EMERGENCY_CONTACT_REQUIRED_FIELDS`.
- Emergency contact note without `details` succeeds.
- Allergies/other note without `details` fails with
  `PERSONAL_DIRECTORY_NOTE_REQUIRED_FIELDS`.
- Other note without `custom_title` fails with
  `PERSONAL_DIRECTORY_OTHER_TITLE_REQUIRED`.
- Non-other note with `custom_title` fails with
  `PERSONAL_DIRECTORY_OTHER_TITLE_FORBIDDEN`.
- Non-emergency-contact note with `contact_name` or `phone_number` fails
  with `PERSONAL_DIRECTORY_CONTACT_FIELDS_FORBIDDEN`.
- Creating a second active `emergency_contact` fails with
  `PERSONAL_DIRECTORY_NOTE_TYPE_CONFLICT`.
- Creating a second active `allergies` fails with
  `PERSONAL_DIRECTORY_NOTE_TYPE_CONFLICT`.
- Creating a 21st active `other` note fails with
  `PERSONAL_DIRECTORY_OTHER_NOTE_LIMIT_REACHED`.
- Note with invalid `photo_path` fails with
  `PERSONAL_DIRECTORY_NOTE_INVALID_PHOTO_PATH`.
- Archive note sets `archived_at`; archived notes excluded from reads.
- Archive is idempotent (`already_archived`).
- `get_member_bank_account` with own user ID succeeds without home membership.
- Updating a note with a different `note_type` fails with
  `PERSONAL_DIRECTORY_NOTE_TYPE_CHANGE_FORBIDDEN`.
- User cannot mutate another user's notes or bank account.
- Notes response is ordered: `emergency_contact`, `allergies`, then
  `other` by `created_at` desc.
- Bank account values are excluded from telemetry payloads.
- `get_personal_directory_nudge` returns `show=true` with `missing` list
  when any of bank account, emergency contact, or allergies is absent and
  nudge not dismissed for this home.
- `get_personal_directory_nudge` returns `show=false` when all records
  exist or nudge already dismissed.
- `dismiss_personal_directory_nudge` persists dismissal for the home.
- Dismiss is idempotent (`already_dismissed`).
- Dismissed nudge does not reappear for the same home.
- Nudge reappears after joining a different home.

## 8. References

- [Personal Directory Contract v1](../../../product/kinly/shared/personal_directory_v1.md)
- [Homes v2](../homes/homes_v2.md)

```contracts-json
{
  "domain": "personal_directory_api",
  "version": "v1",
  "entities": {
    "PersonalDirectoryBankAccount": {},
    "PersonalDirectoryNote": {},
    "PersonalDirectoryNudgeDismissal": {}
  },
  "functions": {
    "personalDirectory.getBankAccount": {
      "type": "rpc",
      "caller": "authenticated",
      "impl": "public.get_personal_directory_bank_account",
      "args": {},
      "returns": "jsonb"
    },
    "personalDirectory.upsertBankAccount": {
      "type": "rpc",
      "caller": "authenticated",
      "impl": "public.upsert_personal_directory_bank_account",
      "args": {
        "p_account_holder_name": "text",
        "p_account_number": "text"
      },
      "returns": "jsonb"
    },
    "personalDirectory.getNotes": {
      "type": "rpc",
      "caller": "authenticated",
      "impl": "public.get_personal_directory_notes",
      "args": {
        "p_target_user_id": "uuid|null"
      },
      "returns": "jsonb"
    },
    "personalDirectory.getMemberBankAccount": {
      "type": "rpc",
      "caller": "authenticated",
      "impl": "public.get_member_bank_account",
      "args": {
        "p_target_user_id": "uuid"
      },
      "returns": "jsonb"
    },
    "personalDirectory.upsertNote": {
      "type": "rpc",
      "caller": "authenticated",
      "impl": "public.upsert_personal_directory_note",
      "args": {
        "p_note_id": "uuid|null",
        "p_note_type": "text",
        "p_custom_title": "text|null",
        "p_contact_name": "text|null",
        "p_phone_number": "text|null",
        "p_details": "text|null",
        "p_photo_path": "text|null"
      },
      "returns": "jsonb"
    },
    "personalDirectory.archiveNote": {
      "type": "rpc",
      "caller": "authenticated",
      "impl": "public.archive_personal_directory_note",
      "args": {
        "p_note_id": "uuid"
      },
      "returns": "jsonb"
    },
    "personalDirectory.getNudge": {
      "type": "rpc",
      "caller": "authenticated",
      "impl": "public.get_personal_directory_nudge",
      "args": {
        "p_home_id": "uuid"
      },
      "returns": "jsonb"
    },
    "personalDirectory.dismissNudge": {
      "type": "rpc",
      "caller": "authenticated",
      "impl": "public.dismiss_personal_directory_nudge",
      "args": {
        "p_home_id": "uuid"
      },
      "returns": "jsonb"
    }
  },
  "rls": []
}
```
