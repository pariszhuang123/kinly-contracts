---
Domain: Homes
Capability: shopping_list
Scope: backend
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.1
Audience: internal
Last updated: 2026-03-26
---

# Shopping List API Contract v1.1

Backend RPC shapes and invariants for the shared shopping list (one active list
per home). Mirrors product contract behaviors, aligns with Home Units v1, and
integrates with Share expenses.

## 1. Entities (storage expectations)

- Quota integration:
  - `public.home_usage_metric` includes `shopping_item_photos`.
  - `public.home_usage_counters.shopping_item_photos` tracks active
    shopping-item photos.
  - `public.home_plan_limits` includes free-plan limit for
    `shopping_item_photos` (default `10`).

- `shopping_lists`
  - Unique partial index: `UNIQUE(home_id) WHERE is_active = true`.
  - `updated_at` maintained by trigger.
  - One active list per home remains canonical. This contract does NOT introduce
    multiple list headers per home.

- `shopping_list_items`
  - Invariants:
    - `is_completed = true` -> `completed_by_user_id` and `completed_at` are
      NOT NULL.
    - `is_completed = false` -> both are NULL.
    - `reference_photo_path` once non-null MUST remain non-null; only
      replacement is allowed (no delete-to-null).
    - `reference_photo_path` must match `households/%` when present.
    - Active views exclude `archived_at IS NOT NULL`.
    - Scope is item-level, not list-level.
    - `scope_type IN ('house', 'unit')`.
    - `scope_type = 'house'` -> `unit_id IS NULL`.
    - `scope_type = 'unit'` -> `unit_id IS NOT NULL`.
  - `updated_at` maintained by trigger.
  - Recommended Home Units extension:
    - `scope_type text not null default 'house'`
    - `unit_id uuid null` FK -> `home_units(id)`
  - Product-scoped rules:
    - Shopping-list default scope is `house`.
    - If the caller has no active shared unit, the allowed alternate scope is
      the caller's personal unit.
    - If the caller has an active shared unit, the allowed alternate scope is
      that shared unit.
    - Personal-unit shopping-list scope is therefore a fallback for members who
      are not in a shared unit.

- `shopping_list_purchase_memory`
  - One row per unique item name per home. Tracks purchase history for
    overbuying reminders.
  - Key: `UNIQUE(home_id, canonical_name)`.
  - `canonical_name = lower(btrim(shopping_list_items.name))` - exact match only
    in v1.
  - `purchase_count` - number of distinct purchase events (one per canonical
    name per archive call).
  - `last_purchased_by_user_id` - the `completed_by_user_id` from the archived
    item (buyer, not archiver). No FK constraint; resolved via `LEFT JOIN` to
    `profiles`.
  - `warning_window_days` - seeded at row creation from defaults (see product
    contract `shopping_list_purchase_memory_v1`), immutable in v1.
  - Constraints:
    - `CHECK (canonical_name <> '')`
    - `CHECK (purchase_count >= 1)`
    - `CHECK (warning_window_days >= 1)`
    - `CHECK (first_purchased_at <= last_purchased_at)`
  - `home_id` FK -> `homes(id)` with `ON DELETE CASCADE`.
  - RLS enabled, direct access revoked for `authenticated`; reads/writes are
    RPC-only.
  - `updated_at` maintained by trigger.

## 2. RPCs

All RPCs enforce membership with `public._assert_home_member(p_home_id)` or an
equivalent membership join on item-scoped calls.

### 2.1 `shopping_list_get_for_home(p_home_id uuid)`

Returns the active list and caller-visible unarchived items for the home.

- Filters:
  - `home_id = p_home_id`
  - `archived_at IS NULL`
  - `is_completed = false OR completed_by_user_id = auth.uid()`
- If no active list exists, returns an empty active-list object with `id = null`
  and `items = []`.
- `list` includes counters:
  - `items_unarchived_count`
  - `items_uncompleted_count`
- Item payload SHOULD include:
  - `scope_type`
  - `unit_id`
  - `unit_name` when applicable
- Completion visibility is caller-scoped:
  - caller sees `is_completed = true` only for items they completed
  - for items completed by other members, response masks completion
    (`is_completed = false`, `completed_by_user_id = null`,
    `completed_by_avatar_id = null`, `completed_at = null`)
  - `items_uncompleted_count` is also caller-scoped using the same visibility
    rule
- Ordering: uncompleted first, then completed by `completed_at DESC` (server MAY
  implement; client can reorder).

### 2.2 `shopping_list_add_item(p_home_id uuid, p_name text, p_quantity text default NULL, p_details text default NULL, p_reference_photo_path text default NULL, p_scope_type text default 'house', p_unit_id uuid default NULL)`

- Lazily creates an active list if missing for the home.
- Inserts item with `is_completed = false`, `archived_at = NULL`.
- Scope defaults to `house`.
- Allowed scope behavior:
  - `p_scope_type = 'house'` -> `p_unit_id MUST be NULL`
  - `p_scope_type = 'unit'` -> `p_unit_id MUST be non-NULL`
  - if caller has an active shared unit, `p_unit_id` may reference only that
    shared unit
  - if caller has no active shared unit, `p_unit_id` may reference only the
    caller's personal unit
- If `p_reference_photo_path` is provided, sets `reference_added_by_user_id =
  auth.uid()`.
- If `p_reference_photo_path` is provided, path MUST start with `households/`.
- Adding an item with a photo increments
  `home_usage_counters.shopping_item_photos` and enforces quota.
- Reject empty or whitespace-only `p_name` (`invalid_name`).
- Purchase memory lookup:
  - after insert, look up `shopping_list_purchase_memory` for matching
    `canonical_name = lower(btrim(p_name))` in the same home
  - if a match exists and `days_since_last_purchase < warning_window_days`,
    include:

```json
{
  "purchase_memory": {
    "purchase_count": 4,
    "last_purchased_at": "2026-03-10T14:22:00.000Z",
    "last_purchased_by_display_name": "Paris",
    "days_since_last_purchase": 13,
    "warning_window_days": 14
  }
}
```

  - `days_since_last_purchase` is computed server-side
  - `last_purchased_by_display_name` is nullable
  - if no match or outside the warning window, `purchase_memory` is `null`
  - the lookup is non-blocking; item creation still succeeds if lookup/profile
    resolution fails

### 2.3 `shopping_list_update_item(p_item_id uuid, p_name text default NULL, p_quantity text default NULL, p_details text default NULL, p_is_completed boolean default NULL, p_reference_photo_path text default NULL, p_replace_photo boolean default false, p_scope_type text default NULL, p_unit_id uuid default NULL)`

Supports rename, quantity/details edit, tick/untick, photo replace, and
optional item re-scoping.

- `NULL` input for `p_name`, `p_quantity`, or `p_details` means "no change".
- `NULL` input for `p_scope_type` / `p_unit_id` means "no scope change".
- If item re-scoping is supported:
  - `p_scope_type = 'house'` -> effective `unit_id MUST resolve to NULL`
  - `p_scope_type = 'unit'` -> `p_unit_id MUST reference a scope the caller is
    allowed to target under the same rules as add-item
- Completion is first-completer-wins:
  - tick: when `p_is_completed = true` on an uncompleted item, set
    `is_completed = true`, `completed_by_user_id = auth.uid()`,
    `completed_at = now()`
  - tick by the same completer again is idempotent
  - tick or untick by a different member when already completed MUST raise
    `item_already_completed_by_other`
  - untick by the same completer clears completion fields
- Photo rules:
  - if `p_replace_photo = true` and `p_reference_photo_path` is provided, set
    `reference_photo_path = p_reference_photo_path`,
    `reference_added_by_user_id = auth.uid()`
  - if no prior photo exists, providing `p_reference_photo_path` sets it
  - if `p_reference_photo_path` is provided, path MUST start with `households/`
  - first-ever photo add enforces/increments `shopping_item_photos`
  - photo replacement does not increment usage
  - deletion is forbidden; attempts to clear to NULL raise
    `photo_delete_not_allowed`

### 2.4 `shopping_list_prepare_expense_for_user(p_home_id uuid)`

Prefills Share expense for the caller's completed items.

- Selection:
  - `home_id = p_home_id`
  - `archived_at IS NULL`
  - `is_completed = true`
  - `completed_by_user_id = auth.uid()`
  - `linked_expense_id IS NULL`
- Returns a single row or zero rows with:
  - `default_description text`
  - `default_notes text`
  - `item_ids uuid[]`
  - `item_count int`
- No time-window gating in v1.

### 2.5 `shopping_list_link_items_to_expense_for_user(p_home_id uuid, p_expense_id uuid, p_item_ids uuid[])`

Links caller-completed items to a newly created Share expense and archives them.

- `p_expense_id` MUST belong to `p_home_id` and be created by `auth.uid()`.
- Update WHERE:
  - `home_id = p_home_id`
  - `id = ANY(p_item_ids)`
  - `archived_at IS NULL`
  - `is_completed = true`
  - `completed_by_user_id = auth.uid()`
  - `linked_expense_id IS NULL`
- Sets:
  - `linked_expense_id = p_expense_id`
  - `archived_at = now()`
  - `archived_by_user_id = auth.uid()`
- Locks expense row (`FOR UPDATE`) before first-link check.
- Side effect: increments `home_usage_counters.active_expenses` by `+1` only
  when this call creates the first shopping-list link for that expense.
- No active-expenses quota check is applied in this RPC.
- Purchase-memory side effect: UPSERT into `shopping_list_purchase_memory` for
  archived rows (see 2.8).

### 2.6 `shopping_list_archive_items_for_user(p_home_id uuid, p_item_ids uuid[])`

Archives caller-completed items without expense linkage.

- Update WHERE:
  - `home_id = p_home_id`
  - `id = ANY(p_item_ids)`
  - `archived_at IS NULL`
  - `completed_by_user_id = auth.uid()`
- Sets:
  - `archived_at = now()`
  - `archived_by_user_id = auth.uid()`
- Purchase-memory side effect: UPSERT into `shopping_list_purchase_memory` for
  archived rows (see 2.8).

### 2.7 `shopping_list_archive_item(p_item_id uuid)`

Archives a single item so it stops showing in the active shopping list.

- Loads the item by `p_item_id`; missing or already archived rows raise
  `item_not_found`.
- Enforces home membership using the item's `home_id`.
- Does not require `completed_by_user_id = auth.uid()`.
- Sets `archived_at = now()`, `archived_by_user_id = auth.uid()`.
- Purchase-memory side effect:
  - if the archived item has `is_completed = true`, UPSERT into
    `shopping_list_purchase_memory`
  - if `is_completed = false`, no memory write occurs

### 2.8 Purchase memory UPSERT (shared side-effect)

This section defines the purchase-memory write behavior shared by 2.5, 2.6, and
2.7. It runs in the same transaction as the archive `UPDATE`.

- Driven from the rows actually modified by the archive (`UPDATE ... RETURNING`)
- Only rows where `is_completed = true` are eligible
- Group eligible rows by `canonical_name = lower(btrim(name))`
- For each distinct `canonical_name`:
  - Insert (first purchase):
    - `purchase_count = 1`
    - `first_purchased_at = now()`
    - `last_purchased_at = now()`
    - `display_name = item.name`
    - `last_purchased_by_user_id = item.completed_by_user_id`
    - `warning_window_days` seeded from defaults (fallback `14`)
  - Update (repeat purchase):
    - `purchase_count = purchase_count + 1`
    - `last_purchased_at = now()`
    - `display_name = item.name`
    - `last_purchased_by_user_id = item.completed_by_user_id`
    - `warning_window_days` is NOT overwritten
- When multiple items share the same `canonical_name` in one batch,
  `display_name` and `last_purchased_by_user_id` come from the item with the
  latest `created_at` (ties by `id` ascending)
- `last_purchased_by_user_id` is set to the item's `completed_by_user_id`, not
  `auth.uid()`
- If the UPSERT fails, the entire transaction rolls back

## 3. RLS / access control

- Tables have RLS enabled and direct access revoked for `authenticated`;
  writes/reads are RPC-only.
- Membership is enforced inside RPCs with `_assert_home_member` and scoped
  predicates.
- Internal helpers `_home_assert_quota(uuid, jsonb)` and
  `_home_usage_apply_delta(uuid, jsonb)` are not executable by `authenticated`.

## 4. Error codes (canonical)

- `invalid_name` - name missing or blank
- `invalid_scope_type` - `p_scope_type` is not one of the allowed values
- `invalid_unit_scope` - `p_unit_id` is invalid for the requested scope or the
  caller is not allowed to target that unit
- `invalid_reference_photo_path` - photo path is present but not under
  `households/`
- `photo_delete_not_allowed` - attempt to clear existing
  `reference_photo_path` to NULL
- `NOT_HOME_MEMBER` - caller not in the home
- `item_not_found` - item missing or archived when updating
- `item_already_completed_by_other` - caller attempted to complete/untick an
  item already completed by another member
- `invalid_expense` - provided expense is not owned by caller in the same home
- `PAYWALL_LIMIT_SHOPPING_ITEM_PHOTOS` - adding a new shopping item photo would
  exceed plan quota

## 5. Coupling / notes

- Share expense creation lives in `contracts/api/kinly/share/expenses_v2.md`;
  shopping list only prepares/links/archives items
- Purchase memory behavior is defined in product contract
  `contracts/product/kinly/shared/shopping_list_purchase_memory_v1.md`
- Unit-scope behavior aligns to
  `contracts/api/kinly/homes/home_units_api_v1.md` and
  `contracts/product/kinly/mobile/home_units_v1.md`
- Matches product contract `shopping_list_contract_v1` and architecture
  contract `architecture/contracts/shopping_list_contract.md`
