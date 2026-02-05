---
Domain: Homes
Capability: shopping_list
Scope: shared
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
Audience: internal
Last updated: 2026-02-05
---

# Shopping List Product Contract v1

## 1. Purpose & scope
- Define the shared shopping list experience for homes: one active list per home; everyone can contribute and mark progress.
- Align behaviors with existing Share expenses module without duplicating its logic; this contract only covers list behaviors and when we hand off to Share.

## 2. Goals
- Quick, low-friction list for daily household shopping.
- Preserve authorship of ticks (avatar shows who marked complete).
- Let any member clear *their* completed items, optionally by creating a Share expense.

## 3. Non-goals
- Budgeting, receipt OCR, price tracking, or splitting logic (handled by Share module after handoff).
- Multiple concurrent lists per home (explicitly out of scope for v1).
- Real-time collaborative editing guarantees beyond last-write-wins.

## 4. Entities & invariants
- **shopping_list** (one active per home)
  - name defaults to "Groceries"; MUST remain editable.
  - Invariant: `home_id` has exactly one row where `is_active = true`; new homes auto-seed one active list. Archive instead of delete.
- **shopping_list_item**
  - Required: `name`.
  - Optional: `quantity`, `details`, `reference_photo_path`.
  - Completion state is single-writer: `is_completed` + `completed_by_user_id` + `completed_at` represent one user's tick.
  - Invariants:
    - If `is_completed = true`, both `completed_by_user_id` and `completed_at` MUST be present.
    - If `is_completed = false`, both MUST be null.
    - If `reference_photo_path` is ever set, it MUST remain non-null thereafter; only replacement with a new photo is allowed.
    - Active views exclude `archived_at IS NOT NULL`.

## 5. Core behaviors
- **Viewing**
  - Show unarchived items for the active list; order newest first by default, client MAY allow manual reorder.
  - Row chrome: checkbox, name, and small indicators when `quantity`, `details`, or `reference_photo_path` exist.
  - Tapping row opens a detail sheet (quantity, details, photo preview if present).

- **Adding items**
  - Any member MAY add; empty/whitespace-only names MUST be rejected client-side.
  - If the active list is missing (edge case), creation MUST lazily create it before inserting the item.

- **Reference photo**
  - Adding/replacing a photo sets `reference_photo_path` and `reference_added_by_user_id` to the actor.
  - Deletion is not supported: once a photo exists, the only permitted change is replacing it with a new photo (never clearing to null). Client should expose this as “Replace photo”, not “Remove”.

- **Tick / untick**
  - Any member MAY tick or untick any item.
  - Tick sets `is_completed = true`, `completed_by_user_id = actor`, `completed_at = now()`.
  - Untick clears completion fields and sets `is_completed = false`.
  - A new tick by another member overrides previous `completed_by_user_id` (single owner at a time); UI should update avatar accordingly.

## 6. "Done shopping" actions (per-user)
- CTA is enabled only when `my_completed_count > 0` (items where `is_completed = true` and `completed_by_user_id = me` and `archived_at IS NULL`).
- Two mutually exclusive flows, both scoped to **my** completed items only:
  1) **Create Share expense**
     - Prefill description/notes from my completed items; backend returns `item_ids` and suggested text.
     - On confirmation, items are linked (`linked_expense_id`) and archived with `archived_at = now()` and `archived_by_user_id = me`.
  2) **Clear without expense**
     - Archives only my completed items (`archived_at` + `archived_by_user_id = me`).
- Safeguards: server-side updates MUST filter by `completed_by_user_id = auth.uid()` and `archived_at IS NULL` to prevent clearing others' ticks.

## 7. Error and edge handling
- If `Done shopping` is tapped with zero eligible items (race condition), surface a non-blocking toast "No completed items to clear" and no-ops.
- Upload failures for photos MUST leave existing photo unchanged; show a retry affordance.
- List creation failure (rare) should show generic "Couldn't create list right now" and allow retry; do not create duplicate lists client-side.

## 8. Permissions & privacy
- RLS: home membership required for all reads/writes on list and items.
- Avatars for `completed_by_user_id` MAY be shown; no other PII stored on items.

## 9. Telemetry (privacy-safe)
- SHOULD log: `shopping_list_item_added`, `shopping_list_item_completed`, `shopping_list_done_prepare`, `shopping_list_done_archive`, `shopping_list_done_linked_to_expense`.
- MUST NOT log free-form text fields (`name`, `details`, `quantity` contents) or photo paths.

## 10. Dependencies & links
- Couples to Share expenses module for optional settlement; this contract stops at prefill + linkage.
- No required coupling to chores/house tasks modules.
