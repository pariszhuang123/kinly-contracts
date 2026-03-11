---
Domain: Homes
Capability: House Directory API
Scope: backend
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
---

# House Directory API v1

Status: Proposed

Scope: Backend RPC, storage invariants, reminder-state semantics, and access
rules for House Directory.

Audience: Product, design, engineering, AI agents.

Depends on:
- House Directory Contract v1
- Homes v2

## 1. Access model

- Caller MUST be authenticated for all RPCs.
- Read RPCs require current home membership.
- Mutations are owner-only for the target home.
- Direct client table DML SHOULD be denied when using RPC-only architecture.

## 2. Canonical enums

### 2.1 `home_directory_account_type`
- `rent`
- `wifi`
- `electricity`
- `gas`
- `water`
- `other`

### 2.2 `home_directory_link_tag`
- `rent`
- `bond`
- `utilities`
- `other`

### 2.3 `home_directory_reminder_kind`
- `renewal`

### 2.4 `home_directory_reminder_status`
- `active`
- `dismissed`

### 2.5 `home_directory_recurrence_unit`
- `day`
- `week`
- `month`
- `year`

## 3. Storage model and invariants

### 3.1 `home_directory_wifi`

Required fields:
- `id uuid pk`
- `home_id uuid fk homes(id)`
- `ssid text`
- `password text null`
- `created_by_user_id uuid`
- `updated_by_user_id uuid`
- `created_at timestamptz`
- `updated_at timestamptz`

Required constraints:
- one wifi row per home: `unique(home_id)`
- ssid length: `1..64`
- password may be null or empty

QR payload rules:
- no password: `WIFI:T:nopass;S:<ssid>;;`
- with password: `WIFI:T:WPA;S:<ssid>;P:<password>;;`
- escape in `ssid/password`: `\`, `;`, `,`, `:`

### 3.2 `home_directory_accounts`

Required fields:
- `id uuid pk`
- `home_id uuid fk homes(id)`
- `account_type text`
- `custom_label text null`
- `provider_name text`
- `account_reference text null`
- `link_url text`
- `term_start_date date null`
- `term_end_date date null`
- `recurrence_every integer null`
- `recurrence_unit text null`
- `notes text null`
- `inspection_recurrence_every integer null`
- `inspection_recurrence_unit text null`
- `created_by_user_id uuid`
- `updated_by_user_id uuid`
- `created_at timestamptz`
- `updated_at timestamptz`

Required constraints:
- `account_type` in canonical enum list
- `account_type='other'` requires non-empty trimmed `custom_label` length `1..40`
- non-`other` accounts require `custom_label is null`
- `term_end_date` requires `term_start_date`
- if both term dates exist: `term_start_date < term_end_date`
- `account_type='rent'` requires both term dates
- recurrence fields appear as a pair (both null or both non-null)
- if recurrence exists: `recurrence_every >= 1` and valid unit
- inspection recurrence fields apply only to `rent`
- if inspection recurrence exists: paired, `>= 1`, valid unit

### 3.3 `home_directory_account_reminder_states`

Required fields:
- `id uuid pk`
- `home_id uuid fk homes(id)`
- `account_id uuid fk home_directory_accounts(id)`
- `reminder_kind text`
- `status text default 'active'`
- `term_start_date date`
- `term_end_date date`
- `reminder_at date`
- `shown_at timestamptz null`
- `dismissed_at timestamptz null`
- `notification_sent_at timestamptz null`
- `created_at timestamptz`
- `updated_at timestamptz`

Required constraints:
- `reminder_kind='renewal'`
- `status in ('active','dismissed')`
- unique identity:
  - `account_id`
  - `reminder_kind`
  - `term_start_date`
  - `term_end_date`
- reminder date validity:
  - `term_start_date <= reminder_at`
  - `reminder_at < term_end_date`

### 3.4 `home_directory_links`

Required fields:
- `id uuid pk`
- `home_id uuid fk homes(id)`
- `title text`
- `url text`
- `tag text`
- `custom_tag text null`
- `start_date date null`
- `end_date date null`
- `created_by_user_id uuid`
- `updated_by_user_id uuid`
- `created_at timestamptz`
- `updated_at timestamptz`

Required constraints:
- `tag` in canonical enum list
- `tag='other'` requires non-empty trimmed `custom_tag` length `1..24`
- non-`other` tags require `custom_tag is null`
- `end_date` requires `start_date`
- if both dates exist: `start_date < end_date`

## 4. Renewal reminder semantics

- Eligible when both term dates exist.
- Compute `renewal_reminder_at = term_end_date - interval '3 months'`.
- Reminder is valid only when:
  - `renewal_reminder_at >= term_start_date`
  - `renewal_reminder_at < term_end_date`
- If invalid, reminder state MUST NOT exist as active for that term.
- Current-date comparisons use UTC calendar date in v1.

Deterministic behavior requirement:
- Implementation MAY materialize state on write or lazily on read/sync.
- Product behavior MUST be equivalent to:
  - valid current-term reminder state exists
  - invalid reminder state does not exist
  - term changes reset reminder identity

## 5. RPC contract

### 5.1 `get_house_directory(p_home_id uuid) -> jsonb`

Caller: member.

Returns:
- wifi profile (0 or 1)
- accounts
- links
- reminder states for current term identities
- `today_reminders` projection MAY be included

### 5.2 `upsert_home_directory_wifi(p_home_id uuid, p_ssid text, p_password text|null) -> jsonb`

Caller: owner-only.

Behavior:
- upserts the single wifi row by `home_id`
- returns canonical wifi payload and derived QR payload

### 5.3 `upsert_home_directory_account(...) -> jsonb`

Caller: owner-only.

Behavior:
- create/update account with invariant checks
- recompute reminder validity for the account term window
- ensure reminder-state behavior matches deterministic rules

### 5.4 `dismiss_home_directory_reminder(p_home_id uuid, p_account_id uuid, p_reminder_kind text, p_term_start_date date, p_term_end_date date) -> jsonb`

Caller: owner-only.

Behavior:
- dismisses reminder for the exact identity tuple only
- sets `status='dismissed'` and `dismissed_at=now()`
- no effect on future term identities

### 5.5 `list_today_home_reminders(p_home_id uuid) -> jsonb`

Caller: member.

Includes reminder only when:
- account term is not expired
- reminder date is valid
- current UTC date is on/after `reminder_at`
- reminder state for current term identity exists
- reminder state is not dismissed

## 6. Error envelope and codes

Error envelope:

```json
{ "code": "STRING_CODE", "message": "Human readable", "details": {} }
```

Required codes:
- `UNAUTHORIZED`
- `NOT_HOME_MEMBER`
- `FORBIDDEN_OWNER_ONLY`
- `HOUSE_DIRECTORY_INVALID_ENUM`
- `HOUSE_DIRECTORY_INVALID_TERM_RANGE`
- `HOUSE_DIRECTORY_RENT_TERM_REQUIRED`
- `HOUSE_DIRECTORY_INVALID_RECURRENCE`
- `HOUSE_DIRECTORY_OTHER_LABEL_REQUIRED`
- `HOUSE_DIRECTORY_OTHER_TAG_REQUIRED`
- `HOUSE_DIRECTORY_REMINDER_INVALID`
- `HOUSE_DIRECTORY_REMINDER_NOT_FOUND`

## 7. Privacy and security requirements

- Wifi password is sensitive operational data.
- API responses SHOULD only include password for authorized member contexts.
- Logging and telemetry MUST NOT include plaintext wifi password.
- Returned data MUST exclude unrelated personal directory records.

## 8. Contract test scenarios

- Rent upsert without term dates fails with `HOUSE_DIRECTORY_RENT_TERM_REQUIRED`.
- End date before start date fails with `HOUSE_DIRECTORY_INVALID_TERM_RANGE`.
- Short term producing pre-start reminder yields no active reminder state.
- Expired term does not appear in `list_today_home_reminders`.
- Dismissed old-term reminder does not suppress new-term reminder after term edit.
- Owner mutation succeeds; member mutation fails with `FORBIDDEN_OWNER_ONLY`.

## 9. References

- [House Directory Contract v1](../../../product/kinly/shared/house_directory_v1.md)
- [Homes v2](./homes_v2.md)

```contracts-json
{
  "domain": "house_directory_api",
  "version": "v1",
  "entities": {
    "HomeDirectoryWifi": {},
    "HomeDirectoryAccount": {},
    "HomeDirectoryAccountReminderState": {},
    "HomeDirectoryLink": {}
  },
  "functions": {
    "houseDirectory.get": {
      "type": "rpc",
      "caller": "member",
      "impl": "public.get_house_directory",
      "returns": "jsonb"
    },
    "houseDirectory.upsertWifi": {
      "type": "rpc",
      "caller": "owner-only",
      "impl": "public.upsert_home_directory_wifi",
      "returns": "jsonb"
    },
    "houseDirectory.upsertAccount": {
      "type": "rpc",
      "caller": "owner-only",
      "impl": "public.upsert_home_directory_account",
      "returns": "jsonb"
    },
    "houseDirectory.dismissReminder": {
      "type": "rpc",
      "caller": "owner-only",
      "impl": "public.dismiss_home_directory_reminder",
      "returns": "jsonb"
    },
    "houseDirectory.listTodayReminders": {
      "type": "rpc",
      "caller": "member",
      "impl": "public.list_today_home_reminders",
      "returns": "jsonb"
    }
  },
  "rls": []
}
```
