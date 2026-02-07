---
Domain: Homes
Capability: shopping_list
Scope: platform
Artifact-Type: architecture
Stability: evolving
Status: draft
Version: v1.0
---

# Shopping List Architecture Contract v1

This architecture contract is aligned to `contracts/api/kinly/homes/shopping_list_api_v1.md` and captures system-level invariants and RPC behavior for shared shopping lists.

## 0. Scope

One active shared shopping list per home.
Household members can:

- Add items with optional quantity/details/photo reference
- Tick/untick items (single completion owner per item)
- Run Done Shopping actions on their own completed items only
- Optionally link their completed items to a Share expense

## 1. Data model and invariants

### 1.1 `shopping_lists`

- One active list per home enforced by unique partial index:
  - `UNIQUE(home_id) WHERE is_active = true`
- `updated_at` is trigger-maintained.

### 1.2 `shopping_list_items`

Core columns include:

- identity and ownership: `id`, `shopping_list_id`, `home_id`, `created_by_user_id`
- content: `name`, `quantity`, `details`, `reference_photo_path`, `reference_added_by_user_id`
- completion: `is_completed`, `completed_by_user_id`, `completed_at`
- settlement/archive: `linked_expense_id`, `archived_at`, `archived_by_user_id`
- timestamps: `created_at`, `updated_at`

Invariants:

- `is_completed = true` implies `completed_by_user_id` and `completed_at` are non-null.
- `is_completed = false` implies `completed_by_user_id` and `completed_at` are null.
- Active list views must exclude `archived_at IS NOT NULL`.
- `reference_photo_path` is replace-only once set; delete-to-null is forbidden.
- `reference_photo_path` must match `households/%` when present.
- `updated_at` is trigger-maintained.

## 2. Quotas and usage counters

Shopping list photo usage is integrated with home plan limits:

- `public.home_usage_metric` includes `shopping_item_photos`.
- `public.home_usage_counters.shopping_item_photos` tracks active shopping-item photos.
- `public.home_plan_limits` includes free-plan limit for `shopping_item_photos` (default `10`).

Behavior:

- Adding first-ever photo to an item consumes quota and increments counter.
- Replacing an existing photo does not increment usage.

## 3. Access model

- Tables have RLS enabled.
- Direct access for `authenticated` is revoked for shopping list tables.
- Reads/writes are RPC-only.
- Membership is enforced inside RPCs using `public._assert_home_member(p_home_id)` or equivalent scoped membership checks for item-scoped calls.
- Internal helpers `_home_assert_quota(uuid, jsonb)` and `_home_usage_apply_delta(uuid, jsonb)` are not executable by `authenticated`.

## 4. RPC architecture behavior

### 4.1 `shopping_list_get_for_home(p_home_id uuid)`

- Returns active list and unarchived items for `p_home_id`.
- If no active list exists, returns empty active-list object (`id = null`) and `items = []`.
- `list` includes counters:
  - `items_unarchived_count`
  - `items_uncompleted_count`
- Includes `completed_by_avatar_id` via `public.profiles.avatar_id` join.
- Ordering target: uncompleted first, then completed by `completed_at DESC`.

### 4.2 `shopping_list_add_item(...)`

- Lazily creates active list when missing.
- Creates item with `is_completed = false` and `archived_at = NULL`.
- Rejects blank/whitespace names (`invalid_name`).
- If photo path is provided, it must start with `households/` and sets `reference_added_by_user_id = auth.uid()`.
- Adding an item with a first photo enforces/increments `shopping_item_photos` quota.

### 4.3 `shopping_list_update_item(...)`

- Supports edits to `name`, `quantity`, `details`, `is_completed`, and photo replacement.
- `NULL` for `p_name`, `p_quantity`, `p_details` means no change.
- Tick sets completion ownership to `auth.uid()` and stamps `completed_at = now()`.
- Untick clears completion fields.
- Photo path must start with `households/` when provided.
- Delete-to-null photo attempts are rejected (`photo_delete_not_allowed`).
- First photo add enforces/increments photo quota; replacement does not increment.

### 4.4 `shopping_list_prepare_expense_for_user(p_home_id uuid)`

Selection criteria:

- `home_id = p_home_id`
- `archived_at IS NULL`
- `is_completed = true`
- `completed_by_user_id = auth.uid()`
- `linked_expense_id IS NULL`

Returns one row or zero rows containing:

- `default_description`
- `default_notes`
- `item_ids`
- `item_count`

No time-window gating in v1.

### 4.5 `shopping_list_link_items_to_expense_for_user(...)`

- Requires `p_expense_id` belongs to `p_home_id` and was created by `auth.uid()`.
- Update predicate includes:
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
- Side effect: increments `home_usage_counters.active_expenses` by `+1` only when first shopping-list link is created for that expense.
- No active-expenses quota check in this RPC.

### 4.6 `shopping_list_archive_items_for_user(...)`

- Archives without expense link.
- Predicate includes:
  - `home_id = p_home_id`
  - `id = ANY(p_item_ids)`
  - `archived_at IS NULL`
  - `completed_by_user_id = auth.uid()`
- Sets `archived_at = now()` and `archived_by_user_id = auth.uid()`.

## 5. Canonical errors

- `invalid_name`
- `invalid_reference_photo_path`
- `photo_delete_not_allowed`
- `NOT_HOME_MEMBER`
- `item_not_found`
- `invalid_expense`
- `PAYWALL_LIMIT_SHOPPING_ITEM_PHOTOS`

## 6. Coupling

- Share expense creation remains defined in `contracts/api/kinly/share/expenses_v2.md`.
- Shopping list integration covers prepare/link/archive boundaries only.
