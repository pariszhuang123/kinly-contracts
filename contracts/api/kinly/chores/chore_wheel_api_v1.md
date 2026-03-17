---
Domain: Shared
Capability: Chores
Scope: backend
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
---

# Chore Wheel API Contract v1

Backend RPC shapes and invariants for the chore wheel feature. Provides a single query RPC to fetch wheel-eligible chores. Assignment is handled by the existing `chores_update_v2` RPC with the new `p_assignment_method` parameter (see [chores_v2](../../../product/kinly/mobile/chores_v2.md)).

## 1. Schema Addition

### `assignment_method` column on `public.chores`

- Type: `text`, nullable, default `NULL`.
- CHECK constraint: `assignment_method IN ('manual', 'wheel')`.
- `NULL` — legacy chores / never explicitly assigned (treated as manual).
- `'manual'` — assigned by a member directly.
- `'wheel'` — assigned via the chore wheel.
- Set via `chores_update_v2` when `p_assignment_method` is provided.

## 2. RPCs

All RPCs enforce membership with `public._assert_home_member(p_home_id)`.

### 2.1 `chores_wheel_eligible(p_home_id uuid)`

Returns all wheel-eligible chores for a home, combining new drafts and re-spin candidates in a single result set.

- Selection (union of two pools):
  - **New drafts**: `home_id = p_home_id` AND `state = 'draft'`
  - **Re-spin candidates**: `home_id = p_home_id` AND `state = 'active'` AND `assignment_method = 'wheel'` AND `recurrence_unit = 'week'` AND `next_occurrence < current_date`
- Ordering: `created_at ASC`.
- Returns rows with columns:

| Column | Type | Notes |
|---|---|---|
| `id` | `uuid` | Chore ID |
| `home_id` | `uuid` | |
| `name` | `text` | |
| `state` | `public.chore_state` | `'draft'` or `'active'` |
| `assignee_user_id` | `uuid \| null` | `NULL` for drafts |
| `assignee_full_name` | `text \| null` | Joined from profiles; `NULL` for drafts |
| `assignee_avatar_storage_path` | `text \| null` | Joined from profiles; `NULL` for drafts |
| `created_at` | `timestamptz` | Used for spin ordering |

- Returns empty array when no eligible chores exist.
- The client uses `count >= 3` to decide whether to show the wheel option.

## 3. Assignment Flow (existing RPCs)

The wheel does **not** introduce new write RPCs. Assignment uses `chores_update_v2`:

- The client MUST pass `p_assignment_method = 'wheel'` for **every** chore in the wheel session — no client-side branching needed.
- The backend decides what to persist: `assignment_method = 'wheel'` is stored **only if** `recurrence_unit = 'week'`. For non-weekly chores (one-off, daily, etc.), the backend silently treats it as `'manual'`.
- **Draft → active**: sets `assignee_user_id`, transitions `state` to `active`.
- **Re-spin (active → active)**: updates `assignee_user_id` to the new member.
- **Manual override**: any subsequent call to `chores_update_v2` without `p_assignment_method` (or with `'manual'`) flips `assignment_method` to `'manual'`, removing the chore from future wheel sessions.

## 4. RLS / Access Control

- `public.chores` has RLS enabled; `anon`/`authenticated` direct access revoked.
- `chores_wheel_eligible` is a `SECURITY DEFINER` RPC; membership enforced via `_assert_home_member`.
- Write access via existing `chores_update_v2` (already documented in chores_v2 contract).

## 5. Error Codes

| Code | RPC | Condition |
|---|---|---|
| `NOT_HOME_MEMBER` | `chores_wheel_eligible` | Caller is not an active member of `p_home_id` |

No additional error codes beyond those already defined in `chores_update_v2`.

## 6. Coupling / Notes

- Product contract: [chore_wheel_v1](../../../product/kinly/mobile/chore_wheel_v1.md)
- Schema amendment and `p_assignment_method` param: [chores_v2](../../../product/kinly/mobile/chores_v2.md)
- The wheel spin animation and randomness are client-side; the backend only serves the eligible list and receives final assignments.
