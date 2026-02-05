---
Domain: Homes
Capability: shopping_list
Scope: backend
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
Audience: internal
Last updated: 2026-02-05
---

# Shopping List API Contract v1

Backend RPC shapes and invariants for the shared shopping list (one active list per home). Mirrors product contract behaviors and integrates with Share expenses.

## 1. Entities (storage expectations)
- `shopping_lists`
  - Unique partial index: `UNIQUE(home_id) WHERE is_active = true`.
- `shopping_list_items`
  - Invariants:
    - `is_completed = true` ⇒ `completed_by_user_id` & `completed_at` NOT NULL.
    - `is_completed = false` ⇒ both NULL.
    - `reference_photo_path` once non-null MUST remain non-null; only replacement is allowed (no delete-to-null).
    - Active views exclude `archived_at IS NOT NULL`.

## 2. RPCs
All RPCs enforce home membership via RLS.

### 2.1 `shopping_list_get_for_home(p_home_id uuid)`
Returns the active list and all unarchived items for the home.
- Filters: `home_id = p_home_id` AND `archived_at IS NULL`.
- Response fields include `completed_by_user_id` and `completed_by_avatar_id` (join to `public.profiles.avatar_id`).
- Ordering: uncompleted first, then completed by `completed_at DESC` (server MAY implement; client can reorder).

### 2.2 `shopping_list_add_item(p_home_id uuid, p_name text, p_quantity text default NULL, p_details text default NULL, p_reference_photo_path text default NULL)`
- Lazily creates an active list if missing for the home.
- Inserts item with `is_completed = false`, `archived_at = NULL`.
- If `p_reference_photo_path` provided, sets `reference_added_by_user_id = auth.uid()`.
- Reject empty/whitespace-only `p_name` (raise `invalid_name`).

### 2.3 `shopping_list_update_item(p_item_id uuid, p_name text default NULL, p_quantity text default NULL, p_details text default NULL, p_is_completed boolean default NULL, p_reference_photo_path text default NULL, p_replace_photo boolean default false)`
Supports rename, quantity/details edit, tick/untick, and photo replace.
- Tick: when `p_is_completed = true` ⇒ set `is_completed = true`, `completed_by_user_id = auth.uid()`, `completed_at = now()`.
- Untick: when `p_is_completed = false` ⇒ clear completion fields and set `is_completed = false`.
- Photo rules:
  - If `p_replace_photo = true` AND `p_reference_photo_path` provided ⇒ set `reference_photo_path = p_reference_photo_path`, `reference_added_by_user_id = auth.uid()`.
  - If no prior photo exists, providing `p_reference_photo_path` sets it (same fields as above).
  - Deletion is forbidden: calls MUST NOT set `reference_photo_path = NULL`; attempts should raise `photo_delete_not_allowed`.
- Rows scoped by home membership via RLS.

### 2.4 `shopping_list_prepare_expense_for_user(p_home_id uuid)`
Prefills Share expense for the caller’s completed items.
- Selection:
  - `home_id = p_home_id`
  - `archived_at IS NULL`
  - `is_completed = true`
  - `completed_by_user_id = auth.uid()`
  - `linked_expense_id IS NULL`
- Returns single row or 0 rows with: `default_description text`, `default_notes text`, `item_ids uuid[]`, `item_count int`.
- No time-window gating in v1.

### 2.5 `shopping_list_link_items_to_expense_for_user(p_home_id uuid, p_expense_id uuid, p_item_ids uuid[])`
Links caller-completed items to a newly created Share expense and archives them.
- Update WHERE:
  - `home_id = p_home_id`
  - `id = ANY(p_item_ids)`
  - `archived_at IS NULL`
  - `completed_by_user_id = auth.uid()`
- Sets `linked_expense_id = p_expense_id`, `archived_at = now()`, `archived_by_user_id = auth.uid()`.

### 2.6 `shopping_list_archive_items_for_user(p_home_id uuid, p_item_ids uuid[])`
Archives caller-completed items without expense linkage.
- Update WHERE: `home_id = p_home_id` AND `id = ANY(p_item_ids)` AND `archived_at IS NULL` AND `completed_by_user_id = auth.uid()`.
- Sets `archived_at = now()`, `archived_by_user_id = auth.uid()`.

## 3. RLS / access control
- Table policies: home members only for SELECT/INSERT/UPDATE on `shopping_lists` and `shopping_list_items`.
- RPCs rely on policies; no cross-home access should succeed.

## 4. Error codes (canonical)
- `invalid_name` — name missing/blank.
- `photo_delete_not_allowed` — attempt to clear existing `reference_photo_path` to NULL.
- `not_member` — caller not in the home.
- `item_not_found` — item missing or archived when updating.

## 5. Coupling / notes
- Share expense creation lives in `contracts/api/kinly/share/expenses_v2.md`; shopping list only prepares/link/archives items.
- Matches product contract `shopping_list_contract_v1` and architecture contract `architecture/contracts/shopping_list_contract.md`.
