---
Domain: Contracts
Capability: Shopping List Contract
Scope: platform
Artifact-Type: architecture
Stability: evolving
Status: draft
Version: v1.0
---

# Shopping List Contracts v1

(Kinly — Shared Household Shopping Lists)

## 0. Scope

Each home has one shared shopping list. Housemates can:

- Add items
- Add optional info (quantity, notes, photo reference)
- Tick/untick items (each tick recorded with who ticked it)
- Press Done Shopping to clear only their ticked items
- Optionally convert their ticked items into a Share expense (with auto-prefill)

## 1. Entities

### 1.1. shopping_lists

One active list per home (MVP).

| Column             | Type        | Description                             |
| :----------------- | :---------- | :-------------------------------------- |
| id                 | uuid PK     |                                         |
| home_id            | uuid FK     | public.homes. Home this list belongs to |
| name               | text        | Usually "Groceries"                     |
| is_active          | boolean     | Only one active per home                |
| created_by_user_id | uuid FK     | auth.users. Creator                     |
| created_at         | timestamptz | Default now()                           |
| updated_at         | timestamptz | Trigger maintained                      |

**Rules**

- Unique active list per home: `UNIQUE(home_id) WHERE is_active = true`
- Only home members may access (via RPC).

### 1.2. shopping_list_items

Individual shared items within the list.

| Column                     | Type          | Description                           |
| :------------------------- | :------------ | :------------------------------------ |
| id                         | uuid PK       |                                       |
| shopping_list_id           | uuid FK       |                                       |
| home_id                    | uuid FK       | Denormalised for simple RLS           |
| created_by_user_id         | uuid FK       | Who added the item                    |
| name                       | text NOT NULL | Short label e.g. “Oat milk”           |
| quantity                   | text          | Optional (“2”, “5kg”, “family pack”)  |
| details                    | text          | Optional NOTE / comment for the house |
| reference_photo_path       | text          | Optional Supabase object path         |
| reference_added_by_user_id | uuid          | Who added photo                       |
| is_completed               | boolean       | Default false                         |
| completed_by_user_id       | uuid          | Who ticked it                         |
| completed_at               | timestamptz   | When ticked                           |
| linked_expense_id          | uuid          | If part of a Share expense            |
| archived_at                | timestamptz   | When removed from the list            |
| archived_by_user_id        | uuid          | Who archived                          |
| updated_at                 | timestamptz   | Trigger maintained                    |
| created_at                 | timestamptz   | Default now()                         |

**Invariants**

- When `is_completed = true` ⇒ `completed_by_user_id` + `completed_at` must be
  non-null.
- When `is_completed = false` ⇒ both must be null.
- `archived_at IS NOT NULL` ⇒ item never appears in active list.
- `linked_expense_id` can only go from NULL → some value (write-once).

## 2. Read RPCs (DTOs)

### 2.1. shopping_list_get_for_home(p_home_id)

Fetch active list + items (for Today screen + Shopping Mode).

**Returns**

- List details
- Item fields
- Avatar for who ticked it

**Important:**

- `archived_at IS NULL` items only.

**Includes:**

- `completed_by_avatar_id` (via join to `public.profiles.avatar_id`)

**Thumbnail detection:**

- If `reference_photo_path` is not null → front-end shows tiny photo icon

**Ordering**

1. Uncompleted first
2. Then completed grouped by `completed_at` DESC

## 3. Write RPCs (Basic List Actions)

### 3.1. shopping_list_add_item(...)

Adds item with:

- name (required)
- quantity (optional)
- details (optional)

Created with:

- `is_completed = false`
- `archived_at = NULL`

### 3.2. shopping_list_update_item(...)

Allows updating:

- name
- quantity
- details
- is_completed
- reference_photo_path

**Tick / Untick logic**

- When ticking:
  - `is_completed = true`
  - `completed_by_user_id = auth.uid()`
  - `completed_at = now()`
- When unticking:
  - `is_completed = false`
  - `completed_by_user_id = NULL`
  - `completed_at = NULL`

**Photo logic**

- If updating photo:
  - Set `reference_added_by_user_id = auth.uid()`

## 4. Done Shopping + Share Integration

### 4.1. shopping_list_prepare_expense_for_user(...)

Returns:

- default_description
- default_notes (bullet list)
- item_ids
- item_count

**Selection criteria:**

- Same home
- `archived_at IS NULL`
- `is_completed = true`
- `completed_by_user_id = auth.uid()` ← Only my ticks
- Completed within N hours (default 12)
- Not already linked to an expense

If no items → return 0 rows.

### 4.2. shopping_list_link_items_to_expense_for_user(...)

After Share expense is created:

1. Archive items
2. Link expense

Only apply to items completed by current user:

```sql
WHERE
  home_id = p_home_id
  AND id = ANY(p_item_ids)
  AND archived_at IS NULL
  AND completed_by_user_id = auth.uid()
```

Set:

- `linked_expense_id = p_expense_id`
- `archived_at = now()`
- `archived_by_user_id = auth.uid()`

### 4.3. shopping_list_archive_items_for_user(...)

If “Done shopping → No expense”: Archive only my ticked items:

- `archived_at = now()`
- `archived_by_user_id = auth.uid()`

Only items where:

- `completed_by_user_id = auth.uid()`
- `archived_at IS NULL`

**No per-user ownership limits; anyone in the home can edit.** Safety for “my
ticks only” handled in RPCs.