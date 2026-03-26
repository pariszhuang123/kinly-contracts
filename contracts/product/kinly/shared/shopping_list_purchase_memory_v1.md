---
Domain: Homes
Capability: shopping_list
Scope: shared
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
Audience: internal
Last updated: 2026-03-23
---

# Shopping List Purchase Memory Contract v1

## 1. Purpose & scope

- Build a lightweight purchase-memory layer on top of the existing shopping list so the home accumulates knowledge about **what has been bought before, when, and how often**.
- Use this memory to surface gentle reminders when a member adds an item the home has already purchased, helping households avoid overbuying and wasted money.
- This contract covers the memory data model, warning-window logic, reminder UX rules, and integration points with existing shopping list RPCs. It does NOT cover budgeting, price tracking, or receipt OCR.

## 2. Goals

- Reduce accidental overbuying by surfacing "You bought this before" context at the moment of adding an item.
- Build a per-home purchase history passively — no extra user effort required.
- Keep the experience non-blocking: reminders inform, they never prevent adding an item.
- Use per-item warning windows so reminders are contextually relevant (milk within 7 days matters; rice within 7 days does not).

## 3. Non-goals

- Price tracking or price comparison.
- Receipt scanning / OCR.
- Automatic reorder or subscription management.
- Suggesting quantities based on consumption patterns (future consideration).
- Cross-home memory (memory is strictly per-home).
- Full grocery taxonomy or forced categorisation during the add-item flow.
- AI-first classification (v1 is deterministic only).

## 4. Data model

### 4.1 `shopping_list_purchase_memory`

One row per unique item name per home (canonical, case-insensitive match).

| Column | Type | Nullable | Description |
|---|---|---|---|
| `id` | uuid | NOT NULL | PK, auto-generated |
| `home_id` | uuid | NOT NULL | FK → homes, ON DELETE CASCADE |
| `canonical_name` | text | NOT NULL | Lowercased, trimmed item name used for matching; derived from `shopping_list_items.name` at archive time |
| `display_name` | text | NOT NULL | Most recently used casing/spelling of the name |
| `purchase_count` | integer | NOT NULL | Number of distinct purchase events (one increment per canonical name per archive call, regardless of how many duplicate-named items are archived in the same batch) |
| `first_purchased_at` | timestamptz | NOT NULL | Timestamp of the first archive event |
| `last_purchased_at` | timestamptz | NOT NULL | Timestamp of the most recent archive event |
| `last_purchased_by_user_id` | uuid | NOT NULL | The `completed_by_user_id` from the archived item — represents who bought it, not who archived it |
| `warning_window_days` | integer | NOT NULL | Number of days after last purchase during which a reminder is relevant; seeded from defaults (§4.3) at row creation, immutable in v1 |
| `created_at` | timestamptz | NOT NULL | Row creation time |
| `updated_at` | timestamptz | NOT NULL | Trigger-maintained |

Constraints:
- `UNIQUE(home_id, canonical_name)` — also serves as the primary lookup index for the add-item read path; no additional index is needed.
- `CHECK (canonical_name <> '')`
- `CHECK (purchase_count >= 1)`
- `CHECK (warning_window_days >= 1)`
- `CHECK (first_purchased_at <= last_purchased_at)`
- `home_id` FK → `homes(id)` with `ON DELETE CASCADE`
- `last_purchased_by_user_id` has no FK constraint. The referenced user may be deleted or leave the home; the column retains the original UUID as a dangling reference. The read path resolves it via a `LEFT JOIN` to `profiles` — if the user no longer exists, `last_purchased_by_display_name` is returned as `null`.

Access model:
- RLS enabled, direct access revoked for `authenticated`.
- All reads and writes are RPC-only, consistent with `shopping_list_items` access model.

### 4.2 Canonicalisation rules (v1)

- `canonical_name = lower(btrim(shopping_list_items.name))`.
- No stemming, lemmatisation, or fuzzy matching in v1 — exact canonical match only.
- Future versions MAY add alias-based matching (see §12).

### 4.3 Warning window defaults

When a memory row is first created, `warning_window_days` is seeded by matching the `canonical_name` against the default table below. If no match is found, a fallback of **14 days** is used.

**Important:** With v1 exact matching, only items whose `lower(btrim(name))` exactly matches one of these strings will receive a non-default window. This list is intentionally kept short — most items will receive the 14-day fallback, which is acceptable for v1.

#### 7 days (perishable / fast turnover)

`milk`, `bread`, `bananas`, `lettuce`, `tomatoes`, `chicken`, `eggs`

#### 30 days (household consumables)

`toilet paper`, `paper towels`

#### 60 days (pantry staples)

`pasta`, `rice`, `flour`, `sugar`

#### Fallback

Any `canonical_name` not in the above list defaults to **14 days**.

`warning_window_days` is seeded once at row creation and is **immutable in v1**. Future versions MAY allow households to tune their own windows per item.

## 5. When memory is written (passive collection)

Memory rows are created or updated as a **side-effect of archiving** — the existing "Done shopping" flows already represent a purchase event:

- `shopping_list_archive_items_for_user` (clear without expense)
- `shopping_list_link_items_to_expense_for_user` (clear with expense)
- `shopping_list_archive_item` (single-item archive)

### 5.1 Write rules

On each archive call, for every item being archived where `is_completed = true`:

1. Derive `canonical_name` from `shopping_list_items.name`.
2. Group archived items by `canonical_name` within the same archive call.
3. For each distinct `canonical_name`, UPSERT into `shopping_list_purchase_memory`:
   - **Insert** (first purchase): set `purchase_count = 1`, `first_purchased_at = now()`, `last_purchased_at = now()`, `display_name = item.name`, `last_purchased_by_user_id = item.completed_by_user_id`, seed `warning_window_days` from defaults (§4.3).
   - **Update** (repeat purchase): increment `purchase_count` by 1 (not by number of duplicate-named items), update `last_purchased_at = now()`, `display_name = item.name`, `last_purchased_by_user_id = item.completed_by_user_id`. Do NOT overwrite `warning_window_days`.

### 5.2 Attribution

`last_purchased_by_user_id` MUST be set to `completed_by_user_id` from the archived item — the person who ticked the item as done (i.e., who bought it). It MUST NOT be set to `auth.uid()` because `shopping_list_archive_item` allows archiving another member's completed item.

### 5.3 Transactional integrity

- Memory UPSERTs MUST run in the same transaction as the archive `UPDATE`.
- UPSERTs MUST be driven from the rows actually modified by the archive (i.e., the `UPDATE ... RETURNING` result), not from input parameters, to avoid counting rows that were already archived or did not match.

### 5.4 Exclusions

- Items archived without `is_completed = true` (e.g., single-item archive of an uncompleted item via `shopping_list_archive_item`) MUST NOT write to purchase memory — only completed-then-archived items count as "purchased".

### 5.5 Failure behaviour

- Memory UPSERTs run in the same transaction as the archive `UPDATE` (§5.3).
- If the memory UPSERT fails, the entire transaction (including the archive) rolls back. This is intentional — memory integrity is preferred over silent data loss.
- The user can retry the archive operation. This is acceptable because archive + memory failures are expected to be rare (constraint violations on a simple UPSERT).
- Implementations MUST NOT wrap the memory UPSERT in a swallowed exception block. If memory cannot be written, the archive should not silently proceed with missing history.

### 5.6 Historical backfill

- No backfill of existing archived items is performed at deployment time.
- Purchase memory starts accumulating from the first archive operation after the feature is deployed.
- This is a deliberate simplification for v1. Future versions MAY offer a one-time backfill migration if the data is valuable.

## 6. When memory is read (reminders)

### 6.1 Trigger: adding an item

When a member adds an item via `shopping_list_add_item`, the backend MUST look up `shopping_list_purchase_memory` for a matching `canonical_name` in the same home.

If a match exists **and** `days_since_last_purchase < warning_window_days`, the add-item response MUST include a `purchase_memory` object:

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

If no match exists, or `days_since_last_purchase >= warning_window_days`, `purchase_memory` is `null`. The comparison is strict less-than (`<`) so that e.g. milk bought exactly 7 days ago with a 7-day window does NOT trigger a reminder — the window has expired.

Field notes:
- `days_since_last_purchase` is computed server-side as `floor(extract(epoch from (now() - last_purchased_at)) / 86400)`. The server is the single authority; clients MUST NOT recompute.
- `last_purchased_by_display_name` is nullable — if the purchasing member has left the home or has no profile, this field is `null` and the client MUST omit the "by {name}" portion of the copy.
- The memory lookup is **non-blocking**: item creation succeeds even if the memory lookup or profile join fails. In case of lookup failure, `purchase_memory` is returned as `null`.

### 6.2 API contract alignment

The `purchase_memory` response field is defined in `shopping_list_api_v1.md` §2.2 (wire format) and `architecture/contracts/shopping_list_contract.md` §4.2 (system-level behaviour). This contract defines the field semantics and UX rules.

### 6.3 Reminder UX rules

- Reminders are **non-blocking**: the item is always added regardless of memory match.
- Warnings MUST be phrased as suggestions, not hard claims.
- Client SHOULD surface a brief inline hint below the newly added item when `purchase_memory` is non-null.
- Suggested copy patterns (client chooses best fit):
  - `"Bought once before — {days_since_last_purchase} days ago by {name}"` (when `purchase_count = 1` and display name available)
  - `"Bought {purchase_count} times — last bought {days_since_last_purchase} days ago by {name}"` (when `purchase_count > 1` and display name available)
  - `"Last bought {days_since_last_purchase} days ago"` (when display name unavailable)
  - `"Bought today by {name}"` (when `days_since_last_purchase = 0`)
  - `"You may already have this at home"` (soft variant)
- The hint SHOULD auto-dismiss after ~5 seconds or on user interaction.
- Client SHOULD NOT re-show a hint for the same `canonical_name` within the same user session / interaction burst (e.g., if user adds "Milk", sees hint, removes it, and re-adds "Milk" immediately).
- **Emphasis tiers** (client-side):
  - If `days_since_last_purchase < 3`, use amber/warning tone ("bought very recently").
  - If `days_since_last_purchase < warning_window_days * 0.5`, use gentle highlight.
  - Otherwise, use neutral informational tone.

Bad copy examples (MUST NOT use):
- "Duplicate item detected"
- "You already have this"
- "Cannot add item"

### 6.4 Trigger: viewing the list (optional, future)

- v1 does NOT surface memory on list view or item detail.
- Future versions MAY add a "purchase history" section to item detail sheets.

## 7. Permissions & privacy

- RLS: same as `shopping_list_items` — home membership required, RPC-only access.
- Purchase memory is home-scoped, not user-scoped; all home members can see all purchase history for the home.
- `last_purchased_by_user_id` is resolved to a display name via `profiles` join — same pattern as `completed_by_avatar_id`. Display name is nullable (member may have left).

## 8. Telemetry (privacy-safe)

- SHOULD log: `purchase_memory_hint_shown`, `purchase_memory_hint_dismissed`.
- MUST NOT log item names, quantities, or any free-text fields.

## 9. Edge cases

- **Home member leaves and rejoins**: memory persists (it's home-scoped, not user-scoped). `last_purchased_by_display_name` becomes null if the member is no longer in the home.
- **Item renamed before archive**: the name at archive time is what gets recorded.
- **Bulk archive with multiple items of the same canonical name**: counts as **one** purchase event (+1 to `purchase_count`), not one per duplicate-named row. `display_name` and `last_purchased_by_user_id` are taken from the item with the latest `created_at` within the batch (most recently added item wins). Ties are broken by `id` ascending.
- **No purchase memory rows yet for home**: first archive creates the first rows; no migration needed for existing homes.
- **Ambiguous items** (e.g., "coconut milk" — canned vs beverage): v1 treats as a single canonical name. No disambiguation. Soft reminders only. Future alias layer MAY split into distinct canonical items.
- **Home deleted**: all memory rows cascade-deleted via `ON DELETE CASCADE` on `home_id` FK.
- **Concurrent archive calls**: UPSERT with `ON CONFLICT` handles concurrent writes safely; last writer wins for `display_name` and `last_purchased_by_user_id`.

## 10. Invariants

- Raw item `name` is always preserved on `shopping_list_items` — memory is additive, never mutates the source item.
- Users MUST always be able to add an item even when a reminder appears.
- `canonical_name` may match a well-known seeded key or may be an arbitrary user-entered string — both are valid.
- Warning windows are defined per memory row, seeded at creation, and immutable in v1.
- Purchase memory is derived from completed-then-archived items only.
- Warnings MUST remain soft and overridable.
- `purchase_count` represents distinct purchase events (archive calls), not individual item rows.
- `last_purchased_by_user_id` represents the completer (buyer), not the archiver.

## 11. Dependencies & links

- Extends `shopping_list_contract_v1` — same entities, same archive flows.
- Couples to archive RPCs in `shopping_list_api_v1` §2.5–§2.8 as the write trigger.
- `purchase_memory` response field defined in `shopping_list_api_v1` §2.2 and `architecture/contracts/shopping_list_contract.md` §4.2.
- No dependency on Share expenses module — memory is recorded regardless of whether items are linked to an expense.

## 12. Future considerations (out of scope for v1)

### v1.1 — Alias-based matching

- Introduce a `shopping_list_canonical_aliases` table mapping normalised aliases to canonical item keys (e.g., `tp` → `toilet_paper`, `loo roll` → `toilet_paper`).
- Add a `canonical_item_key` column to `shopping_list_purchase_memory` for backfill and richer matching.
- Normalisation layer: lowercasing, brand removal, unit removal, filler-word removal.
- Keyword fallback rules for high-frequency compound items (e.g., `contains beef AND mince` → `beef_mince`).
- Expand the warning-window seed list once normalisation improves match rates.
- Matching priority: exact canonical_name → alias lookup → keyword fallback → unmatched.

### Later

- Household-specific tuneable warning windows.
- Fuzzy / plural-aware name matching ("Milk" ≈ "Milks").
- "Replenishment due" notifications (push/daily digest when warning window is exceeded).
- Per-item consumption rate tracking and `avg_days_between_purchases`.
- Quantity-aware memory ("you usually buy 2L of milk").
- Cross-home memory for users in multiple homes.
- AI fallback for unmatched items with confidence scoring.
- Admin/user reclassification of unmatched items.
