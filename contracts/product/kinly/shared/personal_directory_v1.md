---
Domain: Identity
Capability: Personal Directory
Scope: shared
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
---

# Personal Directory Contract v1

Status: Proposed

Scope: User-owned reference data — bank account and personal info notes —
that the user manages independently of any home. Records are automatically
visible to members of the user's active home.

Audience: Product, design, engineering, AI agents.

Depends on:
- Homes v2 (membership and role model, for home-based visibility)
- House Directory capability (separate home-scoped operational data)

## 1. Purpose

Personal Directory gives each user a place to manage their own reference
data — primarily bank details for housemate payments and personal notes
(emergency contacts, allergy info, etc.).

A user's personal directory exists at the user level, not the home level.
The user can access and edit it even without belonging to any home. When the
user is a member of an active home, their personal directory is
automatically visible to all members of that home. A user can only be in
one home at a time; if they leave and join another home, their existing
directory carries forward to the new home.

Personal Directory MUST support:
- one bank account per user
- personal info notes per user
- visibility to all members of the user's active home

## 2. Scope and boundaries

In scope:
- user-owned records independent of any specific home
- accessible and editable by the user even with no active home membership
- automatically visible to all current members of the user's active home
- only the owning user can create, update, or archive their own records
- soft-archive lifecycle for notes

Out of scope:
- shared home operations (covered by House Directory)
- household behavioural agreements (covered by House Norms)
- cross-country / international payment details
- multiple bank accounts per user (v1 allows one)
- file uploads or multi-attachment workflows

## 3. Core entities

### 3.1 Bank account

Each user MAY have at most one active bank account record (user-scoped,
not home-scoped).

Purpose: provide housemates the details needed to make domestic payments
(rent splits, bill splits, reimbursements).

Fields:
- `account_holder_name` (required) — name on the account
- `account_number` (required) — the full local account identifier
  (e.g. `02-1234-0123456-00` in NZ, sort code + account in UK)

Validation rules:
- Both `account_holder_name` and `account_number` MUST be present.
- `account_holder_name` MUST be auto-suggested from the member's profile
  display name but MUST be editable (legal name may differ).
- `account_number` is a free-form string — format varies by country and
  is not validated beyond non-empty.

Immutability:
- Once a bank account is created it MUST NOT be removed.
- The user MAY replace (update) the values at any time.
- There is no archive or delete action for bank accounts.

Copy-paste UX:
- When a housemate owes money to the user, the Today expenses-to-pay
  surface MUST show the payee's `account_holder_name` and
  `account_number` inline.
- Both values MUST support a single-tap copy action so the payer can
  paste directly into their banking app.
- The owner always sees their own bank account in their personal directory
  view for management (add/edit).
- Other members do NOT see bank account details in the personal directory
  view — they appear only on the expenses-to-pay surface when there is
  an outstanding balance.

No bank account empty state:
- If the payee has not added a bank account, the expenses-to-pay surface
  MUST show a message prompting the payer to contact the payee verbally
  and suggest they add their bank details via their personal directory.

Privacy:
- `account_number` SHOULD be partially masked in default views and fully
  revealed on explicit user action or on the expenses-to-pay surface.
- Values MUST NOT be emitted to telemetry payloads.

### 3.2 Personal note

Represents a piece of personal reference information the member publishes
for their housemates to see.

Each note has a `note_type`:
- `emergency_contact` — emergency phone number, next-of-kin
- `allergies` — food or medical allergies, location of medication
- `other` — freeform; requires non-empty `custom_title`

Type uniqueness:
- At most one active note per default type (`emergency_contact`,
  `allergies`) per user.
- At most **20** active `other` notes per user.

Emergency contact fields:
- `emergency_contact` notes include additional fields:
  - `contact_name` (required) — who to call (e.g. "Mum", "Dr. Smith")
  - `phone_number` (required) — tap-to-call number
- `details` is optional for `emergency_contact` (e.g. "call first if
  unresponsive, then text Dad").
- `phone_number` MUST support a tap-to-call action in the UI so
  housemates can call directly without copying/pasting.

Each note includes:
- `note_type` (required)
- `title` — auto-derived from `note_type` label for default types;
  required as `custom_title` when `note_type='other'`
- `details` (required)
- optional `photo_path`

Examples:
- emergency_contact → contact_name: "Mum", phone: 021 123 4567,
  details (optional): "call first, then text Dad on 021 987 6543"
- allergies → "Severe peanut allergy — EpiPen in top kitchen drawer"
- other ("Parking spot") → "Bay 14, level B2" + photo of parking map
- other ("Work schedule") → "WFH Mondays and Fridays"
- other ("Spare key") → "Under the blue pot by the back door"

Display order:
- Default-type notes (`emergency_contact`, `allergies`) MUST appear first,
  in the order listed above.
- `other` notes appear below default types, sorted by creation date
  (newest first).

Photo rules:
- `photo_path` is a storage reference under `users/%/personal_directory/`,
  not a public CDN URL.
- A note MAY exist without a photo.
- At most one photo is attached per active note row in v1.
- Photos on personal directory notes are **free** — no paywall or usage
  metric. The 20-note cap on `other` notes naturally bounds storage.

Validation rules:
- `note_type` MUST be one of the allowed values.
- `details` MUST be non-empty for `allergies` and `other` types.
- `details` is optional for `emergency_contact`.
- `emergency_contact` requires non-empty `contact_name` and `phone_number`.
- `note_type='other'` requires non-empty `custom_title`.
- Notes are soft-archived with `archived_at`.

## 4. Navigation and entry point

- With an active home: Hub → House Directory → member avatar and name card.
  Tapping a member card opens that member's personal directory (read-only
  for other members; editable for the owner).
- Without an active home: accessible via the user's own avatar icon.
- The owner can always reach their own personal directory from their own
  card.

## 5. Completeness nudge (Today surface)

Today MAY show a single completeness nudge card when the user's personal
directory is missing any of: bank account, emergency contact, or allergies.
The nudge lists which records are still missing so the user knows what to
add.

Nudge rules:
- The nudge is a single card (not one per missing record).
- The nudge is dismissible.
- A dismissed nudge MUST NOT reappear in the same home membership.
- The nudge MAY re-surface after the user joins a new home.

## 6. Access and privacy rules

- Owner access: the authenticated user can always read and mutate their own
  personal directory, regardless of home membership status.
- Home-member read access: all current members of an active home can view
  the personal directory of every other member in that home.
- Write access (create, update, archive): only the owning user can mutate
  their own records. No other user — including a home owner — has write
  access.
- RPCs MUST enforce `auth.uid() = owner_user_id` for all mutation
  operations.
- Bank account number is operationally shared but sensitive:
  - UI SHOULD partially mask by default in list views
  - full reveal requires explicit user tap/action
  - values MUST NOT appear in telemetry or logging payloads

## 7. Data lifecycle

- Records are scoped to `user_id` only — one personal directory per user,
  visible to the user's active home.
- Leaving or being removed from a home does NOT affect personal directory
  records (they persist at the user level).
- Joining a new home automatically makes the user's existing personal
  directory visible to that home's members.
- When a user's account is deactivated, all personal directory records
  MUST be included in the account-deletion data removal scope.
- Archived notes are excluded from list reads.

## 8. Cross-capability relationships

- House Directory stores shared operational facts (wifi, services, house
  notes).
- Personal Directory stores person-specific records visible to the house.
- House Norms stores shared behavioural expectations.
- Contracts MUST remain separated; cross-links are allowed, duplication is
  not.

## 9. Contract test scenarios

- User can create, read, and update their own bank account.
- User can create, read, update, and archive their own personal notes.
- User with no active home can still manage their personal directory.
- Owner sees their own bank account in their personal directory view.
- All home members can read any member's personal notes.
- Other members do NOT see bank account in the directory view; it appears
  only on the expenses-to-pay surface.
- No member can mutate another member's personal directory records.
- Home owner cannot edit another member's personal directory.
- Bank account creation without `account_holder_name` is rejected.
- Bank account creation without `account_number` is rejected.
- Only one bank account per user is allowed.
- Bank account cannot be removed once created; only replaced.
- Expenses-to-pay surface shows payee bank name and account with copy
  actions.
- If payee has no bank account, expenses-to-pay surface shows a verbal
  contact prompt.
- Only one active `emergency_contact` note per user is allowed.
- Only one active `allergies` note per user is allowed.
- At most 20 active `other` notes per user; creation beyond 20 is rejected.
- Default-type notes appear above `other` notes in display order.
- `other` notes are sorted newest first.
- Emergency contact `phone_number` supports tap-to-call.
- Emergency contact without `contact_name` or `phone_number` is rejected.
- Emergency contact without `details` is accepted.
- Personal note creation without `details` is rejected.
- Personal note with `note_type='other'` and no `custom_title` is rejected.
- Photos on personal directory notes are free (no paywall).
- Archived notes are excluded from list reads.
- Leaving a home does not affect the user's personal directory records.
- Joining a new home makes existing records visible to that home's members.
- Account deletion removes all personal directory records.
- Bank account values are excluded from telemetry payloads.
- Today nudge appears when any of bank account, emergency contact, or
  allergies is missing.
- Nudge lists which specific records are missing.
- Dismissed nudge does not reappear in the same home membership.
- Nudge reappears after joining a different home.

## 10. References

- [Personal Directory API v1](../../../api/kinly/identity/personal_directory_api_v1.md)
- [House Directory Contract v1](house_directory_v1.md)
- [Homes v2](../../../api/kinly/homes/homes_v2.md)

```contracts-json
{
  "domain": "personal_directory",
  "version": "v1",
  "entities": {
    "PersonalBankAccount": {},
    "PersonalNote": {}
  },
  "functions": {},
  "rls": []
}
```
