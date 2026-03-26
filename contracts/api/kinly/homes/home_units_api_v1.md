---
Domain: Homes
Capability: Home Units
Scope: backend
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v2.0
---

# Home Units API Contract v1

Status: Draft

Scope: Reusable coordination and liability units inside a home. A unit can be
**personal** (exactly one current membership) or **shared** (two or more current
memberships). Units are used for shopping-list item scoping, expense liability
allocation, settlement visibility, and Today-screen presentation. Chores remain
individual-scoped and are not unit-owned in v1.

## Purpose

This contract introduces a home-scoped grouping model that works with existing
canonical tables rather than replacing them.

Core intent:
- Every current membership has exactly one personal unit.
- Members may also belong to a shared unit.
- Unit-based expense allocation is the default model.
- Personal units make "individual debtor" a special case of unit-based
  allocation rather than a separate mental model.
- Internal cost sharing inside a shared unit is out of scope for v1.

## Existing Canonical Tables Used By This Contract

This contract does NOT redefine the following existing canonical tables:
- `public.memberships`
- `public.profiles`
- `public.shopping_lists`
- `public.shopping_list_items`
- `public.expenses`
- `public.expense_splits`
- `public.expense_plans`
- `public.chores`

This contract adds unit-specific structures around those tables rather than
replacing them.

## Design Principles

- **RPC-first architecture** - all mutations go through SECURITY DEFINER
  functions with `search_path = ''`. All object references inside those
  functions MUST be fully schema-qualified.
- **Deny-by-default** - direct table access is revoked from `anon`,
  `authenticated`, and `PUBLIC`; only RPCs are granted to `authenticated`.
- **Membership-scoped unit identity** - unit membership MUST attach to
  `memberships.id`, not directly to `profiles.id`, because unit participation is
  tied to a home-membership episode rather than global user identity.
- **Profile UI, membership semantics** - the app MAY expose unit management from
  a profile/settings surface, but backend unit changes remain home-scoped
  membership operations, not profile mutations.
- **Units, not raw users, are the default liability target** - personal units
  represent individually liable members; shared units represent grouped debtors.
- **Debtor-based compatibility is allowed** - existing direct
  `expense_splits(debtor_user_id)` flows may continue where explicitly needed,
  but unit-based expense allocation is the preferred model for homes using home
  units.
- **Personal units are automatic** - every current membership SHOULD have
  exactly one active personal unit, auto-provisioned on home join/rejoin.
- **Integrity at the DB layer** - critical invariants MUST be enforced via
  table-level constraints, partial indexes, foreign keys, and deferred
  constraint triggers, not only in RPC logic.
- **Archived units are historical** - active membership-shape invariants apply
  only to active units (`archived_at IS NULL`). Archived units are frozen
  historical records and may still be referenced by historical expenses or
  shopping-list items.

## New Entities

### HomeUnit

| Field | Type | Notes |
|---|---|---|
| `id` | `uuid` | PK, `gen_random_uuid()` |
| `home_id` | `uuid` | FK -> `homes(id)`, CASCADE |
| `unit_type` | `text` | `'personal'` or `'shared'` |
| `name` | `text` | Required stored display name; 1-100 chars after trim |
| `personal_membership_id` | `uuid|null` | FK -> `memberships(id)`; set iff `unit_type = 'personal'` |
| `representative_membership_id` | `uuid|null` | FK -> `memberships(id)`; optional UI display hint only |
| `created_by_user_id` | `uuid|null` | FK -> `profiles(id)` |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | Auto-touched on UPDATE |
| `archived_at` | `timestamptz|null` | Soft-delete |

**Table-level constraints (CHECK):**
- `unit_type IN ('personal', 'shared')`
- `unit_type = 'personal'` -> `personal_membership_id IS NOT NULL`
- `unit_type = 'shared'` -> `personal_membership_id IS NULL`
- `char_length(btrim(name)) BETWEEN 1 AND 100`

**Indexes:**
- Unique partial index: one active personal unit per membership per home
  - `(home_id, personal_membership_id)` WHERE
    `unit_type = 'personal' AND archived_at IS NULL`
- `home_id` WHERE `archived_at IS NULL`
- `representative_membership_id` WHERE `archived_at IS NULL`

### HomeUnitMember

| Field | Type | Notes |
|---|---|---|
| `unit_id` | `uuid` | FK -> `home_units(id)`, CASCADE |
| `membership_id` | `uuid` | FK -> `memberships(id)`, CASCADE |
| `created_at` | `timestamptz` | |

**PK:** `(unit_id, membership_id)`

**Recommended integrity:** if practical, carry `home_id` and use composite
foreign keys so the DB can enforce same-home alignment between
`home_unit_members`, `home_units`, and `memberships`.

### ExpenseUnitSplit

| Field | Type | Notes |
|---|---|---|
| `expense_id` | `uuid` | FK -> `expenses(id)`, CASCADE |
| `unit_id` | `uuid` | FK -> `home_units(id)`, RESTRICT |
| `weight` | `numeric(12,6)\|null` | Optional source weight for audit |
| `amount_cents` | `bigint` | > 0; persisted source of truth |
| `created_at` | `timestamptz` | |

**PK:** `(expense_id, unit_id)`

**Table-level constraints (CHECK):**
- `amount_cents > 0`
- `weight IS NULL OR weight > 0`

## Unit Naming

`home_units.name` MUST be non-null for all active and archived units.

### Personal units

Personal units MUST be auto-provisioned with a stored display name.

Default naming rule:
1. If the member's `profiles.full_name` is present, the system SHOULD derive a
   short personal label from it.
2. Otherwise, use `'Personal'`.

Clients MUST NOT infer personal-unit identity from a null name.
Personal-unit identity is defined by `unit_type = 'personal'`.

### Shared units

Shared units MUST have an explicit caller-supplied name at creation time.
Shared-unit names are not required to be unique within a home.

## Enums

### UnitType
`personal | shared`

### ExpenseAllocationMode
`unit_based | debtor_based`

### ShoppingItemScopeType
`house | unit`

## Active Unit Invariants

For active units (`archived_at IS NULL`):

1. Every current membership MUST have exactly one active personal unit.
2. A personal unit MUST have exactly one current `home_unit_members` row.
3. For personal units, that row's `membership_id` MUST equal
   `personal_membership_id`.
4. Each current membership MAY belong to zero or one active shared unit.
5. A shared unit MUST have at least two current `home_unit_members` rows.
6. If `representative_membership_id` is set, it MUST be a current member of the
   unit.
7. Every `home_unit_members.membership_id` MUST reference a current membership
   in the same home.

Archived units are historical records and are exempt from active
membership-shape rules.

## Deferred Constraint Trigger: `_validate_home_unit_membership_shape`

Fires `AFTER INSERT OR UPDATE OR DELETE` on:
- `home_unit_members`
- `home_units`
- `memberships`

`DEFERRABLE INITIALLY DEFERRED` so that multi-row operations within a single
transaction can satisfy constraints at commit time.

The trigger MUST validate the active-unit invariants above.

## Membership Integrity

### Current-membership model

`public.memberships` is the source of truth for whether a person is currently in
a home.

The contract assumes:
- `memberships.valid_to IS NULL` means current membership
- a person leaving a home is represented by setting `valid_to`
- a person rejoining later is represented by a new `memberships` row

### Rejoin model

Unit participation MUST be tied to a specific `memberships.id`.
If a user leaves and later rejoins, the new membership gets a fresh personal
unit and may have different shared-unit participation.

### Shared-unit participation limit

For product simplicity in v1, a current membership MAY belong to at most one
active shared unit at a time.

This keeps Today visibility, shopping-list scope, and liability semantics
unambiguous.

## Member Join Lifecycle

Implemented as an `AFTER INSERT` trigger on `memberships` for rows that are
current on insert.

Calls the internal helper `_home_units__ensure_personal(p_home_id, p_membership_id)`.
This helper does NOT require `auth.uid()` and is not exposed as a public RPC.

When a user rejoins a home via a new membership row, the same trigger fires and
creates a fresh personal unit for that new membership.

## Member Departure Lifecycle

Implemented as an `AFTER UPDATE` statement-level trigger with transition tables
on `memberships`.

All cleanup MUST occur in the same transaction.

### Step 1: Identify departing memberships

Collect membership rows whose `valid_to` transitioned from `NULL` to non-NULL`.

### Step 2: Shared unit cleanup

For all active shared units containing a departing membership:
1. Set `representative_membership_id = NULL` when it references the departing
   membership.
2. Delete the corresponding `home_unit_members` rows.
3. Recount current members.
4. Archive any shared unit whose remaining current member count is now less
   than 2.

### Step 3: Personal unit cleanup

For each departing membership's active personal unit:
1. Delete its `home_unit_members` row.
2. Set `archived_at = now()` on the personal unit.

### Step 4: Validation

The deferred constraint trigger re-validates at commit. Since archived units are
exempt, archived personal units with zero members and shared units auto-archived
after dropping below two members remain valid historical records.

## Shopping List Integration

`public.shopping_lists` remains the canonical one-active-list-per-home
container.

This contract does NOT create multiple shopping-list headers per home.

Unit scoping, if enabled, MUST live on `shopping_list_items`, not on
`shopping_lists`.

### Recommended shopping-list item extension

Add the following to `shopping_list_items`:
- `scope_type text not null default 'house'`
- `unit_id uuid null`

Constraints:
- `scope_type IN ('house', 'unit')`
- `scope_type = 'house'` -> `unit_id IS NULL`
- `scope_type = 'unit'` -> `unit_id IS NOT NULL`

This allows one active shopping list per home while supporting:
- whole-house items
- personal-unit items only for members who do not belong to an active shared
  unit
- shared-unit items for members who do belong to an active shared unit

Recommended mobile/product behavior:
- shopping-list item scope defaults to `house`
- if the viewer has no active shared unit, allowed alternate scope is their
  personal unit
- if the viewer has an active shared unit, allowed alternate scope is that
  shared unit
- the UI SHOULD expose the current scope as a visible, changeable control rather
  than hiding it

If a referenced unit is later archived, the item may remain as historical
context.

## Expense Integration

`public.expenses` remains the canonical parent record for expense instances.

This contract does NOT create a parallel `home_spends` table.

### Expense allocation modes

Expenses MAY be created in one of two modes:

#### Unit-based allocation

The canonical default for homes using home units.

Liability is assigned to `home_units` through `expense_unit_splits`.
A personal unit represents one individually liable member.
A shared unit represents multiple members acting as one liability bucket.

If a caller selects a shared unit during expense creation, the system MUST treat
that unit as a single explicit debtor target and MUST NOT infer or enforce
internal per-member allocation within that unit.

Recommended mobile/product behavior:
- if the current member belongs to an active shared unit, unit-based expense
  creation SHOULD preselect that shared unit
- the member MUST still be able to switch to their personal unit before
  submission

#### Debtor-based allocation

A compatibility mode for direct person-by-person liabilities.

Liability is assigned directly through existing `expense_splits(debtor_user_id)`.
This mode exists for cases where the creator explicitly wants named individual
debtors instead of unit buckets.

### Unit-based expense invariants

For each unit-based expense:
- all `expense_unit_splits.unit_id` values MUST belong to the same home as
  `expenses.home_id`
- `SUM(expense_unit_splits.amount_cents)` MUST equal `expenses.amount_cents`
- archived units may remain referenced historically
- overpayment MUST be rejected if the product supports partial payments against
  a unit balance

### Weight-based and amount-based allocation

Unit-based expenses may accept either:
- explicit `amount_cents` per unit, or
- weights that are converted into concrete `amount_cents` at creation time

Regardless of input mode, the concrete persisted source of truth is
`expense_unit_splits.amount_cents`.

### Single expenses

A single expense uses:
- one `expenses` row
- one or more `expense_unit_splits` rows

### Recurring expenses

Recurring templates continue to use `public.expense_plans`.

Each generated recurring cycle MUST:
- create a new `expenses` row
- create a snapshot set of `expense_unit_splits` rows for that expense instance

Historical or already-generated cycle allocations MUST NOT be rewritten merely
because unit composition changes later.

## Settlement and Today-Screen Behavior

Today surfaces are concerned with open liabilities up to the present, not with
internal allocation inside a shared unit.

### Core Today rules

1. Today MUST show only unresolved liabilities.
2. Each expense MUST be rendered according to its explicit debtor target.
3. If the debtor target is a personal unit, the expense appears as a personal
   liability.
4. If the debtor target is a shared unit, the expense appears as a shared
   liability for all current members of that unit.
5. Fully settled shared liabilities MUST no longer appear in Today.
6. The UI MUST NOT infer or display internal per-member amounts for a shared
   unit unless those amounts were explicitly created as separate liabilities.

### Shared-unit Today behavior

If an expense is charged to `Alice + Bob` as a shared unit, Today MUST show that
expense as owed by the shared unit, not as two inferred personal debts.

Example:
- `Tim` charges `Power bill` to shared unit `Alice + Bob`
- Today for Alice shows `Power bill` under shared liabilities
- Today for Bob shows the same shared liability
- if either Alice or Bob pays the shared unit balance in full, that shared
  liability is removed from Today for both members

### Personal-unit Today behavior

If an expense is charged to Alice's personal unit, Today MUST show it only as
Alice's personal liability. It MUST NOT appear for Bob merely because Bob is in
the same home.

### Example presentation model

Today SHOULD prefer a single list of open liabilities, with each row carrying a
liability tag rather than forcing separate sections.

Recommended row tags:
- `Personal`
- `Shared`

For a shared liability row, the UI MAY show:
- unit name
- expense description
- unit amount due
- paid so far
- remaining amount

The UI MAY show payment events made by specific members against a shared-unit
liability, but that does not create or imply internal per-member debt.

## Chore Integration

`public.chores` remains canonical.

Chores remain assigned to `assignee_user_id` and are NOT unit-owned in v1.
Unit membership MAY be used for filtering or UI grouping, but chores remain
person-scoped.

## Profile and Settings Integration

The app MAY expose home-unit management from a profile or settings screen.

That does NOT make home-unit participation part of the `profiles` data model.

Rules:
- username, avatar, and other global identity fields remain profile mutations
- creating, joining, leaving, renaming, or archiving a shared unit remain
  home-scoped unit RPC actions
- unit participation MUST NOT be stored as a direct field on `profiles`
- unit participation SHOULD NOT be hidden inside a generic `profiles_update`
  RPC

## RPC Direction

All RPCs below are `SECURITY DEFINER` with `search_path = ''`. All object
references MUST be fully schema-qualified.

**Auth baseline:** caller MUST be authenticated.

### `home_units_ensure_personal_for_membership`

Ensures one active personal unit exists for a current membership.
Used primarily by join lifecycle logic. Public exposure is optional; if exposed,
it MUST remain idempotent.

| Param | Type | Required | Notes |
|---|---|---|---|
| `p_home_id` | `uuid` | yes | |
| `p_membership_id` | `uuid` | yes | Must be a current membership in `p_home_id` |
| `p_name` | `text` | no | Optional custom personal-unit label |

**Returns:** `uuid` - unit ID.

### `home_units_create_shared`

Creates a shared unit containing two or more current memberships.

The creator MAY specify the full initial membership set during creation. That
initial set becomes the shared unit's membership immediately if the create call
succeeds.

This is different from post-create membership changes:
- initial member selection at create time is allowed
- adding a member to an already-created shared unit MUST NOT happen silently in
  v1

| Param | Type | Required | Notes |
|---|---|---|---|
| `p_home_id` | `uuid` | yes | |
| `p_name` | `text` | yes | Non-empty after trim, max 100 chars |
| `p_membership_ids` | `uuid[]` | yes | At least 2 distinct current memberships |
| `p_representative_membership_id` | `uuid` | no | Must be in `p_membership_ids` if set |

**Returns:** `uuid` - new unit ID.

**Validations:**
- `p_membership_ids` MUST contain at least 2 distinct current memberships in the
  same home
- the creator's current membership SHOULD be included unless an explicit admin
  path is later defined
- no specified membership may already belong to another active shared unit

### `home_units_update_shared`

Updates mutable shared-unit metadata.

Supported updates in v1:
- rename shared unit
- update `representative_membership_id`

| Param | Type | Required | Notes |
|---|---|---|---|
| `p_home_id` | `uuid` | yes | |
| `p_unit_id` | `uuid` | yes | Must be an active shared unit in the home |
| `p_name` | `text` | no | Optional replacement name |
| `p_representative_membership_id` | `uuid` | no | Must be a current member of the unit if set |

**Returns:** `void`

### `home_units_join_shared`

Adds the caller's current membership to an existing shared unit.

This RPC is intended for profile/settings flows where a member joins a unit
already created by another member in the same home.

This RPC is NOT the mechanism used for the initial membership set at create
time.

| Param | Type | Required | Notes |
|---|---|---|---|
| `p_home_id` | `uuid` | yes | |
| `p_unit_id` | `uuid` | yes | Must be an active shared unit in the home |

**Returns:** `void`

**Validations:**
- caller MUST have a current membership in `p_home_id`
- caller MUST NOT already belong to another active shared unit
- caller MUST NOT already be a member of `p_unit_id`

### `home_units_leave_shared`

Removes the caller's current membership from their active shared unit.

| Param | Type | Required | Notes |
|---|---|---|---|
| `p_home_id` | `uuid` | yes | |
| `p_unit_id` | `uuid` | yes | Must be an active shared unit in the home |

**Returns:** `void`

**Behavior:**
- remove caller's `home_unit_members` row for the shared unit
- clear `representative_membership_id` if it points to the caller
- if remaining current member count is less than 2, archive the shared unit

### `home_units_archive_shared`

Soft-archives a shared unit.
Personal units MUST NOT be archived via public RPC; they are archived by the
departure lifecycle.

| Param | Type | Required | Notes |
|---|---|---|---|
| `p_home_id` | `uuid` | yes | |
| `p_unit_id` | `uuid` | yes | Must be an active shared unit in the home |

**Returns:** `void`

### `expenses_create_with_unit_splits`

Creates an `expenses` row and corresponding `expense_unit_splits` rows.
Supports either amount-based or weight-based unit allocation.

| Param | Type | Required | Notes |
|---|---|---|---|
| `p_home_id` | `uuid` | yes | |
| `p_description` | `text` | yes | Maps to `expenses.description` |
| `p_notes` | `text` | no | Maps to `expenses.notes` |
| `p_amount_cents` | `bigint` | yes | Must be > 0 |
| `p_start_date` | `date` | yes | Maps to `expenses.start_date` |
| `p_unit_splits` | `jsonb` | yes | Non-empty JSON array |

**Returns:** `uuid` - expense ID.

### `expenses_get_unit_summary`

Returns settlement summary for a unit-based expense, broken down by unit.

| Param | Type | Required | Notes |
|---|---|---|---|
| `p_home_id` | `uuid` | yes | |
| `p_expense_id` | `uuid` | yes | Must belong to `p_home_id` |

**Returns:** `jsonb`

### `today_get_expense_liabilities`

Returns open unit liabilities visible to the current member for Today surfaces.

| Param | Type | Required | Notes |
|---|---|---|---|
| `p_home_id` | `uuid` | yes | |
| `p_as_of` | `date` | no | Defaults to current date |

**Returns:** `jsonb`

**Response shape:**

```json
{
  "liabilities": [
    {
      "liability_kind": "personal",
      "expense_id": "uuid",
      "unit_id": "uuid",
      "unit_name": "Personal",
      "description": "Wifi top-up",
      "amount_cents": 1800,
      "remaining_cents": 1800
    },
    {
      "liability_kind": "shared",
      "expense_id": "uuid",
      "unit_id": "uuid",
      "unit_name": "Alice + Bob",
      "description": "Power bill",
      "amount_cents": 6000,
      "paid_cents": 2000,
      "remaining_cents": 4000
    }
  ]
}
```

Rows SHOULD be ordered by operational relevance, for example:
1. overdue or due-soon first
2. then most recently created/opened
3. tie-break by `expense_id`

## Schema Impact Summary

This contract aims to minimise schema churn.

### New tables required

The minimum new tables are:
- `home_units`
- `home_unit_members`
- `expense_plan_units`
- `expense_unit_splits`

Total minimum new tables: **4**

### Existing tables to extend, not replace

Recommended extensions:
- `shopping_list_items`
  - add `scope_type`
  - add `unit_id`

No new shopping-list header table is required.
No new expense parent table is required.
No new chore table is required.

## RPC Reuse and Versioning Strategy

This contract aims to reuse existing RPCs wherever the semantic shape remains
compatible, and introduce a new version only when input/output meaning changes
materially.

### Existing RPCs that should be reused with additive changes where possible

- `shopping_list_add_item`
  - add optional `p_scope_type` and `p_unit_id`
- `shopping_list_update_item`
  - add optional `p_scope_type` and `p_unit_id` only if item re-scoping is
    meant to be supported in v1
- `shopping_list_get_for_home`
  - extend response rows to include `scope_type`, `unit_id`, and optional
    `unit_name`
- `chores_update_v2`, `chores_list_for_home`, `chores_get_for_home`
  - no unit ownership change required; reuse as-is unless UI filtering later
    needs unit-aware read helpers

### Existing RPCs that likely require a new version

- `expenses_create_v3`
- `expenses_edit_v3`
- `expenses_get_current_owed`
- `expenses_get_for_edit`

Reason:
- the existing expense contract is explicitly debtor-user based
- unit-based liability changes the meaning of splits, Today visibility, and edit
  payloads
- adding unit allocation as hidden optional behavior behind existing payloads is
  likely to create ambiguous semantics

Recommended approach:
- keep existing debtor-based expense RPCs stable
- introduce a new expense version when adding unit-based allocation support
- allow the new version to support both `unit_based` and `debtor_based` modes if
  backwards compatibility at the product level is still needed

### Existing RPCs that do not need a new version

- shopping-list RPCs, if unit scoping is introduced only as optional additive
  fields
- chore RPCs, because chores remain person-scoped

### New RPCs justified by the new concept

The minimum new unit-specific RPCs are:
- `home_units_create_shared`
- `home_units_update_shared`
- `home_units_join_shared`
- `home_units_leave_shared`
- `home_units_archive_shared`

`home_units_ensure_personal_for_membership` SHOULD remain internal unless a
clear user-facing repair or admin use case exists.

A dedicated `home_units_list_for_home` read RPC is NOT required by default.
Prefer extending existing home-scoped reads with optional unit fields or
optional `p_unit_id` filtering where that keeps semantics clear.

`today_get_expense_liabilities` is optional. If an existing Today RPC can be
extended without semantic confusion, prefer reusing it. If Today currently has
no expense-liability RPC with compatible shape, a dedicated read RPC is
acceptable.

## Product Rules

1. Every current membership SHOULD have exactly one active personal unit.
2. A person who is not part of any shared unit still has a personal unit and is
   represented entirely through that personal unit.
3. A current membership MAY belong to zero or one active shared unit.
4. Shared units MUST contain at least two current memberships while active.
5. Unit names are not required to be unique within a home.
6. Expense liability is predominantly implemented via units.
7. Personal-unit liability and individually charged liability are the same thing
   in the unit model.
8. If members are grouped into a shared unit and that shared unit is selected
   during expense creation, liability MUST be tracked at the shared-unit level.
9. Internal cost sharing inside a shared unit is out of scope for v1.
10. Debtor-based expense allocation may remain as an explicit compatibility mode,
   but it is not the default mental model for homes using home units.
11. Shopping-list scoping, when unit-aware, belongs on items rather than list
    headers.
12. Chores remain individual-scoped, not unit-owned.
13. Home-unit management may be surfaced from profile/settings UI, but remains
    implemented as home-scoped unit RPCs rather than profile mutations.
14. The creator of a shared unit MAY choose the initial member set during
    creation, but post-create forced assignment of another member into an
    existing shared unit is out of scope for v1.
15. When a membership ends, its personal unit is archived and any affected
    shared unit that drops below two current members is archived.
16. Today surfaces show open liabilities according to explicit debtor target,
    not inferred internal sharing.

## Permissions

### Table-level access

| Table | `anon` | `authenticated` | `PUBLIC` | Notes |
|---|---|---|---|---|
| `home_units` | REVOKE ALL | REVOKE ALL | REVOKE ALL | RPC only |
| `home_unit_members` | REVOKE ALL | REVOKE ALL | REVOKE ALL | RPC only |
| `expense_unit_splits` | REVOKE ALL | REVOKE ALL | REVOKE ALL | RPC only |

### Function-level access

For every public RPC function:
1. `REVOKE EXECUTE ON FUNCTION ... FROM PUBLIC`
2. `GRANT EXECUTE ON FUNCTION ... TO authenticated`

For every internal helper:
1. `REVOKE EXECUTE ON FUNCTION ... FROM PUBLIC`
2. Do NOT grant to `authenticated`

## Naming Conventions

- All table columns, RPC parameters, and JSON response keys use `snake_case`.
- Public RPC function names use the pattern `home_{domain}_{verb}` or
  `expenses_{verb}_{scope}` where appropriate.
- Internal helper names use `_home_units__...`.
- Unit-based money values SHOULD use integer cents where they align to existing
  canonical expense tables.

## Assumptions

- `public.homes(id)` exists.
- `public.memberships(id, user_id, home_id, valid_to)` exists.
- `public.profiles(id)` exists.
- `public.expenses` and `public.expense_plans` remain canonical for single and
  recurring expense instances.
- `public.shopping_lists` remains one-active-list-per-home.
- `public.shopping_list_items` is the correct place for unit-aware shopping-list
  scope.

## Out of Scope (v1)

- Internal cost sharing within a shared unit.
- Automatic inferred personal sub-splits inside a shared-unit charge.
- Rewriting historical expense allocations after unit membership changes.
- Unit-owned chores.
- Multi-level nested units.
- Immutable historical snapshots of unit names and membership labels.
