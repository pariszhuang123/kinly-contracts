---
Domain: Testing
Capability: Chores
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Chores Test Plan (MVP)

Scope: validate the Supabase schema/RPCs, repository wiring, and contract guarantees for the chores domain slice introduced in `chores_v1`.

## 1. Database / RPC tests

Use pgTAP (preferred) or `supabase db test` harness to exercise the new RPCs under RLS.

### Access control
- [ ] Direct `INSERT/UPDATE/DELETE` on `public.chores` is blocked for `authenticated`.
- [ ] Non-members calling any `chores_*` RPC receive `FORBIDDEN`.
- [ ] Storage `households` bucket policies allow uploads only when the key prefix matches a home the caller belongs to; cross-home attempts fail.

### Lifecycle flows
1. **Create**
   - [ ] `chores_create` inserts a row with `state='draft'` when no assignee is supplied and `state='active'` when an assignee is provided, sets `next_occurrence` honoring fixed cadence, and emits `chore_events.event_type='create'`.
   - [ ] `home_usage_counters.active_chores` increments by 1 (and `chore_photos` increments if an expectation photo path is supplied).
2. **Update**
   - [ ] `chores_update` enforces an assignee, flips state to `active`, recomputes `next_occurrence` / `recurrence_cursor`, and only emits `event_type='activate'|'update'` when meaningful fields change.
   - [ ] Adding/removing expectation photos updates `home_usage_counters.chore_photos` (+1/-1 respectively).
3. **Assignee list**
   - [ ] `home_assignees_list` returns only active members of the specified home, includes avatar paths, and enforces `_assert_home_member`.
4. **Complete**
   - [ ] `chore_complete` requires the current assignee, lands one-off chores in `state='completed'`, `next_occurrence=NULL`, `event_type='complete'`.
   - [ ] Recurring chores advance to the first date >= today, keep `state='active'`, emit `complete`, and respond with the new `next_occurrence`.
   - [ ] One-off completion decrements `home_usage_counters.active_chores`; recurring completions keep the counter steady.
5. **Cancel**
   - [ ] Cancelling allowed only for draft/active states, emits `event_type='cancel'`, and decrements `home_usage_counters.active_chores`.
6. **List**
   - [ ] `chores_list_for_home` omits cancelled chores and completed one-offs. (Ordering now `start_date DESC` then `created_at DESC` until the next-occurrence view ships.)
   - [ ] `today_flow_list(home_id, state)` enforces `_assert_home_member`, returns rows ordered by `start_date ASC` / `created_at ASC`, and scopes `state='active'` results to chores assigned to `auth.uid()` while drafts omit the assignee filter.

### Edge cases
- [ ] Invalid expectation photo paths fail with `INVALID_MEDIA_PATH`.
- [ ] `chores_update` rejects non-members and enforces the assignee belongs to the same home.
- [ ] Completing a cancelled chore raises `ALREADY_FINALIZED` (or equivalent business error).
- [ ] Paywall enforcement (free homes only, configured via `home_plan_limits` + `_home_assert_quota`):
  - Creating the 21st active chore returns `PAYWALL_LIMIT_ACTIVE_CHORES`; enabling premium (`home_entitlements.plan='premium'` with `expires_at` in the future) lifts the cap.
  - Adding the 16th expectation photo via create/update returns `PAYWALL_LIMIT_CHORE_PHOTOS`; removing a photo frees the slot.
  - Counters stay consistent after each flow (no negative values, premium homes bypass the checks but counters still update).

## 2. Dart repository tests

Write unit tests around `SupabaseChoresRepository` using `mocktail`/`Mockito` for `SupabaseClient`:
- [ ] Each method calls the expected RPC name with snake_case params (including omission when values are `null`).
- [ ] Successful responses (Map/List) convert to `Chore` objects with enum + date parsing.
- [ ] Malformed payloads throw `ChoreException(unknown)`.
- [ ] Supabase `PostgrestException` codes map to the correct `ChoreErrorCode` values.

## 3. Future BLoC/widget tests (placeholder)

Once BLoC/UI flows exist:
- Chore creation BLoC test: verifies optimistic state, media upload handshake, and error surfacing for validation codes.
- Assignment interaction test: ensures UI enforces single assignee, handles `PAYWALL_LIMIT_*`, and refreshes `home_assignees_list` when membership rolls.
- Recurrence completion test: simulates completing a recurring chore and ensures the next occurrence date appears without duplicates.