---
Domain: Shared
Capability: Shared Calendar
Scope: backend
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
Canonical-Id: shared_calendar
Relates-To: contracts/product/kinly/shared/shared_calendar_v1.md
---

# Shared Calendar API Contract v1

Backend RPC shapes and invariants for the shared calendar feature. Provides RPCs to create, update, cancel, and query calendar events scoped to a home or unit, with optional recurrence and reminder notifications.

## 1. Timezone Authority

All date/time logic uses the **home timezone** (IANA string stored on `homes` table).

- "Today", recurrence computation, occurrence expansion, and reminder scheduling all evaluate as `(now() AT TIME ZONE home_tz)::date`.
- RPCs MUST NOT use raw `current_date` for home-tz-dependent logic.

### 1.1 Schema addition: `homes.timezone`

The `homes` table does not currently have a timezone column. This contract requires adding:

| Column | Type | Notes |
|---|---|---|
| `timezone` | `text` | IANA timezone string (e.g. `'Australia/Sydney'`), NOT NULL, default `'UTC'` |

- Existing homes MUST be backfilled (default `'UTC'` or inferred from owner locale).
- The value MUST be validated against the IANA timezone database on write. Invalid timezone strings MUST be rejected.
- The mechanism for setting/changing the home timezone is out of scope for this contract.

### 1.2 DST handling

All local time computations use **wall-clock semantics**:
- **Spring-forward gap**: nonexistent local times shift forward to the next valid local instant.
- **Fall-back overlap**: ambiguous local times resolve to the **earlier** offset (first occurrence).
- This applies to reminder trigger times, Today resolution, and recurrence computation.

## 2. Schema

### 2.1 `calendar_events` table

| Column | Type | Notes |
|---|---|---|
| `id` | `uuid` | PK, `gen_random_uuid()` |
| `home_id` | `uuid` | FK -> `homes(id)`, CASCADE |
| `created_by_user_id` | `uuid` | FK -> `profiles(id)` |
| `title` | `text` | Required, 1-140 chars after trim |
| `scope_type` | `text` | `'house'` or `'unit'`, default `'house'` |
| `unit_id` | `uuid|null` | Composite FK -> `home_units(id, home_id)`; set iff `scope_type = 'unit'` |
| `start_date` | `date` | NOT NULL, no table default (computed by RPC) |
| `end_date` | `date` | NOT NULL, no table default (computed by RPC) |
| `start_time` | `time` | NOT NULL, no table default |
| `end_time` | `time` | NOT NULL, no table default |
| `description` | `text|null` | |
| `location` | `text|null` | Free text |
| `url` | `text|null` | Validated URL |
| `recurrence_every` | `int|null` | >= 1 when set; `NULL` for one-off |
| `recurrence_unit` | `text|null` | `day`/`week`/`month`/`year`; `NULL` for one-off |
| `recurrence_ends_on` | `date|null` | `NULL` means no upper bound (`Never` in UI); when set, no occurrence may be generated after this date |
| `next_occurrence` | `date|null` | Next scheduled date; backend-managed; used for Today fast-path and cron advancement only |
| `anchor_day_of_month` | `int|null` | Original day-of-month anchor for RFC-compatible month/year recurrence; set iff `recurrence_unit IN ('month','year')` |
| `state` | `text` | `'active'` or `'cancelled'` |
| `cancelled_at` | `timestamptz|null` | |
| `created_at` | `timestamptz` | default `now()` |
| `updated_at` | `timestamptz` | Auto-touched on UPDATE |

Table-level constraints:
- `state IN ('active', 'cancelled')`
- `scope_type IN ('house', 'unit')`
- `scope_type = 'house'` -> `unit_id IS NULL`
- `scope_type = 'unit'` -> `unit_id IS NOT NULL`
- `char_length(btrim(title)) BETWEEN 1 AND 140`
- `(start_date, start_time) < (end_date, end_time)` — combined datetime comparison
- `recurrence_every IS NULL` iff `recurrence_unit IS NULL`
- `recurrence_ends_on IS NULL` when `recurrence_every IS NULL`
- `recurrence_unit IN ('day', 'week', 'month', 'year')` when set
- `recurrence_every >= 1` when set
- When `recurrence_every IS NOT NULL`: `end_date = start_date` (recurring multi-day banned)
- When `recurrence_ends_on IS NOT NULL`: `recurrence_ends_on >= start_date`
- `anchor_day_of_month` IS NOT NULL iff `recurrence_unit IN ('month', 'year')`
- `anchor_day_of_month BETWEEN 1 AND 31` when set

Indexes:
- `(home_id, state)` where `state = 'active'` — active event lookups
- `(home_id, next_occurrence)` where `state = 'active'` — recurring Today queries and cron advancement
- `(home_id, start_date, end_date)` where `state = 'active'` — one-off range queries
- `(created_by_user_id)` where `state = 'active'` — creator departure cleanup
- `(unit_id)` where `state = 'active' AND unit_id IS NOT NULL` — unit archive and unit-departure cleanup
- Unique composite key on `(id, home_id)` for same-home foreign keys

### 2.2 `calendar_event_reminders` table

| Column | Type | Notes |
|---|---|---|
| `id` | `uuid` | PK, `gen_random_uuid()` |
| `event_id` | `uuid` | FK -> `calendar_events(id)`, CASCADE |
| `value` | `int` | >= 1 |
| `unit` | `text` | `'minutes'` or `'hours'` |
| `created_at` | `timestamptz` | default `now()` |

Table-level constraints:
- `unit IN ('minutes', 'hours')`
- `value >= 1`
- Reminder offset cap: `(unit = 'minutes' AND value <= 1380) OR (unit = 'hours' AND value <= 23)`
- Unique index on `(event_id, value, unit)` — prevents duplicate reminder pairs
- Max 5 reminders per event (enforced by RPC)

## 3. RPCs

All RPCs are `SECURITY DEFINER` with `search_path = ''` and fully schema-qualified object references. Read and create RPCs enforce membership with `public._assert_home_member(p_home_id)`. Update, cancel, and get RPCs resolve `home_id` from the event row, then assert membership. Unit-scoped events additionally validate the caller is a **current member of the event's unit** for all operations (view, edit, cancel). If the caller cannot see a unit-scoped event, it behaves as `NOT_FOUND`.

### 3.1 `calendar_events_create`

Creates a calendar event in `active` state.

| Param | Type | Required | Notes |
|---|---|---|---|
| `p_home_id` | `uuid` | yes | |
| `p_title` | `text` | yes | 1-140 chars after trim |
| `p_scope_type` | `text` | no | default `'house'` |
| `p_unit_id` | `uuid` | when scope_type = 'unit' | Must be caller's allowed unit |
| `p_start_date` | `date` | no | default `local_today` (home tz) |
| `p_end_date` | `date` | no | default `p_start_date` |
| `p_start_time` | `time` | yes | |
| `p_end_time` | `time` | yes | |
| `p_description` | `text` | no | NULL to leave empty |
| `p_location` | `text` | no | NULL to leave empty |
| `p_url` | `text` | no | NULL to leave empty; validated URL format |
| `p_recurrence_every` | `int` | no | Paired with unit |
| `p_recurrence_unit` | `text` | no | Paired with every |
| `p_recurrence_ends_on` | `date` | no | `NULL` for `Never`; when set must be on/after `p_start_date` |
| `p_reminders` | `jsonb` | no | Array of `{value, unit}`, max 5; `[]` or omit for none |

Returns:

| Column | Type | Notes |
|---|---|---|
| `id` | `uuid` | |
| `home_id` | `uuid` | |
| `created_by_user_id` | `uuid` | |
| `title` | `text` | |
| `scope_type` | `text` | |
| `unit_id` | `uuid|null` | |
| `start_date` | `date` | |
| `end_date` | `date` | |
| `start_time` | `time` | |
| `end_time` | `time` | |
| `description` | `text|null` | |
| `location` | `text|null` | |
| `url` | `text|null` | |
| `recurrence_every` | `int|null` | |
| `recurrence_unit` | `text|null` | |
| `recurrence_ends_on` | `date|null` | |
| `state` | `text` | Always `'active'` |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

Behavior:
- Resolves `home_tz` from `homes.timezone` for `p_home_id`.
- Computes `local_today = (now() AT TIME ZONE home_tz)::date`.
- `start_date = COALESCE(p_start_date, local_today)`.
- `end_date = COALESCE(p_end_date, start_date)`.
- Inserts event with `state = 'active'` immediately.
- Validates `(start_date, start_time) < (end_date, end_time)`.
- Validates URL format if `p_url` is provided.
- Validates `p_unit_id` is caller's exact resolved allowed unit (not archived, same home) per `home_units` scope resolution.
- When recurring: validates `end_date = start_date`. Sets `anchor_day_of_month = extract(day from start_date)` when `recurrence_unit IN ('month','year')`. Computes `next_occurrence` using the shared recurrence helper and caps future generation at `p_recurrence_ends_on` when provided.
- Validates reminder offset cap (each reminder `value * unit <= 23 hours`).
- Inserts reminder rows from `p_reminders`. Rejects if > 5 or duplicate `(value, unit)` pairs.
- Schedules reminder notification jobs for the current/first occurrence. Skips reminders whose trigger time is already in the past. Multi-day event reminders anchor to `start_date + start_time` only.
- `Never` recurrence does not create unbounded stored rows. Only the base event row and reminder rows are stored; occurrences are derived on query.

### 3.2 `calendar_events_update`

**Full-replacement** update of an existing calendar event. All mutable fields MUST be sent. To clear a nullable field, send `null` explicitly. To clear reminders, send `[]`.

| Param | Type | Required | Notes |
|---|---|---|---|
| `p_event_id` | `uuid` | yes | |
| `p_title` | `text` | yes | 1-140 chars after trim |
| `p_scope_type` | `text` | yes | |
| `p_unit_id` | `uuid|null` | yes | NULL when scope_type = 'house' |
| `p_start_date` | `date` | yes | |
| `p_end_date` | `date` | yes | |
| `p_start_time` | `time` | yes | |
| `p_end_time` | `time` | yes | |
| `p_description` | `text|null` | yes | NULL to clear |
| `p_location` | `text|null` | yes | NULL to clear |
| `p_url` | `text|null` | yes | NULL to clear; validated URL format |
| `p_recurrence_every` | `int|null` | yes | NULL to make one-off; paired with unit |
| `p_recurrence_unit` | `text|null` | yes | NULL to make one-off; paired with every |
| `p_recurrence_ends_on` | `date|null` | yes | NULL for `Never`; on update, trims all future occurrences after this date |
| `p_reminders` | `jsonb` | yes | Array of `{value, unit}`; `[]` to clear |

Returns: same column shape as create.

Behavior:
- Resolves `home_id` from the event row. Asserts caller is a home member via `_assert_home_member`.
- For unit-scoped events: asserts caller is a current member of the event's unit. Otherwise `NOT_FOUND`.
- Only the creator (`created_by_user_id = auth.uid()`) can update. Otherwise `FORBIDDEN`.
- Only `state = 'active'` events can be updated.
- Validates `(start_date, start_time) < (end_date, end_time)`.
- Validates reminder offset cap.
- Replaces all mutable fields with the provided values (full replacement, not patch).
- Replaces reminders (delete all existing + re-insert from `p_reminders`).
- Updates `anchor_day_of_month` when `recurrence_unit IN ('month','year')`.
- Recomputes `next_occurrence` when recurrence or date fields change, using the shared recurrence helper.
- If the series is changed from `Never` to `On date` and no future occurrence remains on/before `p_recurrence_ends_on`, `next_occurrence` becomes `NULL` while the event remains `active`.
- If the series is changed from `On date` back to `Never`, `next_occurrence` is recomputed without an upper bound.
- Clears all pending reminder notification jobs and reschedules for current/next occurrence. Multi-day event reminders anchor to `start_date + start_time` only.

### 3.3 `calendar_events_cancel`

Cancels a calendar event.

| Param | Type | Required | Notes |
|---|---|---|---|
| `p_event_id` | `uuid` | yes | |

Returns: `uuid` — cancelled event ID.

Behavior:
- Resolves `home_id` from the event row. Asserts caller is a home member via `_assert_home_member`.
- For unit-scoped events: asserts caller is a current member of the event's unit. Otherwise `NOT_FOUND`.
- Only the creator can cancel. Otherwise `FORBIDDEN`.
- Only `state = 'active'` events can be cancelled.
- Sets `state = 'cancelled'`, `cancelled_at = now()`, `next_occurrence = NULL`.
- Clears all pending reminder notification jobs for this event.

### 3.4 `calendar_events_list_for_home`

Returns occurrence rows for all non-cancelled events visible to the caller in the requested date range.

| Param | Type | Required | Notes |
|---|---|---|---|
| `p_home_id` | `uuid` | yes | |
| `p_start_date` | `date` | yes | Range start (inclusive) |
| `p_end_date` | `date` | yes | Range end (inclusive); `p_end_date >= p_start_date`; max span 366 days |

Returns `setof`:

| Column | Type | Notes |
|---|---|---|
| `event_id` | `uuid` | |
| `occurrence_date` | `date` | The specific date this occurrence falls on |
| `start_time` | `time` | From base event |
| `end_time` | `time` | From base event |
| `title` | `text` | |
| `scope_type` | `text` | |
| `unit_id` | `uuid|null` | |
| `location` | `text|null` | |
| `is_recurring` | `boolean` | `true` when `recurrence_every IS NOT NULL` |
| `is_start_day` | `boolean` | `true` if this is the event's start date |
| `is_end_day` | `boolean` | `true` if this is the event's end date |
| `creator_user_id` | `uuid` | |
| `creator_full_name` | `text` | Joined from profiles |
| `creator_avatar_storage_path` | `text|null` | Joined from profiles |

Behavior:
- Validates `p_end_date >= p_start_date` and `p_end_date - p_start_date <= 366`. Otherwise `INVALID_INPUT`.
- **Occurrence expansion at query time** from immutable fields (does NOT use `next_occurrence`):
  - **One-off single-day**: one row if `start_date` is within range. `is_start_day = true`, `is_end_day = true`.
  - **One-off multi-day**: one row per day in the overlap of `[start_date, end_date]` and `[p_start_date, p_end_date]`. `is_start_day` / `is_end_day` set per position in the span.
- **Recurring single-day**: all occurrences within range, derived using the shared recurrence helper. Occurrences before `start_date` are never emitted. `is_start_day = true`, `is_end_day = true` for each.
- When `recurrence_ends_on` is set, recurring occurrences later than `recurrence_ends_on` MUST NOT be emitted.
- House-scoped events: visible to all home members.
- Unit-scoped events: visible only to members of that unit (filtered per caller).
- Ordering: `occurrence_date ASC`, then sort bucket (middle-day/all-day rows in bucket 0 before timed rows in bucket 1), then time (`start_time` for start/single days, `end_time` for end days, `00:00` for middle days), then `created_at ASC`.

### Recurrence stepping rules (used by expansion, cron, and create/update)

All recurrence computation MUST use a **single shared backend helper**. Unit-specific stepping:

- **`day`**: add `recurrence_every` calendar days. Pure integer date arithmetic.
- **`week`**: add `recurrence_every * 7` calendar days. Pure integer date arithmetic.
- **`month`**: step `n` = `start_date + (n * recurrence_every) months`, preserving the original day-of-month intent from `anchor_day_of_month`. If the target month does not contain that day, that occurrence is skipped.
- **`year`**: step `n` = `start_date + (n * recurrence_every) years`, preserving the original day-of-month intent from `anchor_day_of_month`. If the target year/month does not contain that day, that occurrence is skipped.

### Occurrence expansion algorithm (recurring)

Given a recurring event with `start_date`, `recurrence_every`, `recurrence_unit`, `anchor_day_of_month`, optional `recurrence_ends_on` and a query range `[range_start, range_end]`:

1. If `range_start <= start_date`, begin at step `n = 0`.
2. Otherwise, estimate step count to reach `range_start` and generate the occurrence at that step using unit-specific rules above.
3. If the generated date is before `range_start`, increment `n` by 1 and regenerate.
4. Continue stepping forward, emitting one occurrence row per step, until the generated date exceeds `range_end`.
5. If `recurrence_ends_on` is set, stop emitting once the generated date would be later than `recurrence_ends_on`.
6. Occurrences before `start_date` MUST NOT be emitted (enforced by `n >= 0`).

### 3.5 `calendar_events_get`

Returns a single event detail with reminders.

| Param | Type | Required | Notes |
|---|---|---|---|
| `p_event_id` | `uuid` | yes | |

Returns:

```json
{
  "id": "uuid",
  "home_id": "uuid",
  "created_by_user_id": "uuid",
  "title": "text",
  "scope_type": "text",
  "unit_id": "uuid|null",
  "start_date": "date",
  "end_date": "date",
  "start_time": "time",
  "end_time": "time",
  "description": "text|null",
  "location": "text|null",
  "url": "text|null",
  "recurrence_every": "int|null",
  "recurrence_unit": "text|null",
  "recurrence_ends_on": "date|null",
  "state": "text",
  "cancelled_at": "timestamptz|null",
  "reminders": [
    { "id": "uuid", "value": 1, "unit": "hours" }
  ],
  "creator": {
    "id": "uuid",
    "full_name": "text",
    "avatar_storage_path": "text|null"
  }
}
```

Behavior:
- Resolves `home_id` from the event row. Asserts caller is a home member via `_assert_home_member`.
- For unit-scoped events: asserts caller is a current member of the event's unit. Otherwise `NOT_FOUND`.
- Returns `NOT_FOUND` if event does not exist or caller cannot see it.

### 3.6 `calendar_events_today`

Returns occurrence rows for today (home timezone).

| Param | Type | Required | Notes |
|---|---|---|---|
| `p_home_id` | `uuid` | yes | |

Returns: same `setof` shape as `calendar_events_list_for_home`.

Behavior:
- Computes `local_today = (now() AT TIME ZONE home_tz)::date`.
- One-off: visible when `start_date <= local_today AND end_date >= local_today`.
- Recurring: visible when `next_occurrence = local_today`.
- Filtered by visibility (house or unit membership).
- Ordering: sort bucket (all-day/middle-day rows first), then time, then `created_at ASC`.

## 4. Recurring Event Cadence Advancement

Unlike chores (which advance on "complete"), calendar events advance automatically via a cron job.

- Job name: `calendar_events_advance_recurring`
- Schedule: `*/15 * * * *` (every 15 minutes)
- Command: `SELECT public.calendar_events_advance_due();`
- Behavior:
  - For each active recurring event, compute `local_today = (now() AT TIME ZONE home_tz)::date` using the event's home timezone.
  - Where `next_occurrence < local_today`: advance `next_occurrence` to the next date strictly on/after `local_today` using the shared recurrence helper.
  - If the next computed occurrence would fall after `recurrence_ends_on`, set `next_occurrence = NULL` and clear future reminder jobs instead of advancing further.
  - Schedule reminder notification jobs for the **new** occurrence.
- Idempotent: re-running produces the same result.
- Implementation note: the job iterates per-home to correctly apply each home's timezone.
- Uses the same shared recurrence helper as create/update/range expansion.

### 4.1 RFC-compatible invalid-date rule

For `recurrence_unit = 'month'` or `'year'`:
- `anchor_day_of_month` stores the original `start_date` day-of-month (1–31).
- Each occurrence targets `anchor_day_of_month` in the target month/year.
- If the target month/year does not contain that day, the occurrence is skipped.
- The anchor is always preserved; invalid dates are not replaced with the last day of the month.
- Each step adds months/years from the **original `start_date`**, not from the previous emitted occurrence.

Examples:
- Jan 31 monthly: Mar 31 → May 31 → Jul 31
- Jan 30 monthly: Mar 30 → Apr 30 → May 30
- Feb 29 yearly: only leap years emit an occurrence

## 5. RLS / Access Control

| Table | `anon` | `authenticated` | `PUBLIC` | Notes |
|---|---|---|---|---|
| `calendar_events` | REVOKE ALL | REVOKE ALL | REVOKE ALL | RPC only |
| `calendar_event_reminders` | REVOKE ALL | REVOKE ALL | REVOKE ALL | RPC only |

Function-level access:
1. `REVOKE EXECUTE ON FUNCTION ... FROM PUBLIC`
2. `GRANT EXECUTE ON FUNCTION ... TO authenticated`

Internal helpers (e.g. `_calendar_events_cancel_for_member_change`, `_calendar_events_cancel_for_unit_departure`, `calendar_events_advance_due`):
1. `REVOKE EXECUTE ... FROM PUBLIC`
2. Do NOT grant to `authenticated`

## 6. Error Codes

| Code | RPC | Condition |
|---|---|---|
| `NOT_HOME_MEMBER` | all | Caller not an active member of the event's home |
| `INVALID_UNIT_SCOPE` | create, update | Unit does not exist, is archived, is in a different home, or caller is not a member |
| `INVALID_INPUT` | create, update, list | Title empty/too long, `(start_date, start_time) >= (end_date, end_time)`, URL malformed, recurring with `end_date != start_date`, reminder offset > 23h, range reversed or > 366 days |
| `NOT_FOUND` | get, update, cancel | Event does not exist, or caller cannot see it (including unit-scoped events where caller is not a unit member) |
| `FORBIDDEN` | update, cancel | Caller has visibility but is not the creator |
| `REMINDER_LIMIT` | create, update | More than 5 reminders or duplicate `(value, unit)` pair |

## 7. Reminder Notification Scheduling

- When an event is created/updated with reminders, backend schedules notification jobs.
- Each reminder triggers a push notification at `start_time - (value * unit)` on the event's `start_date`, evaluated in **home timezone**.
- **Multi-day events**: reminders anchor to `start_date + start_time` only (the beginning of the event), not to each visible day in the span.
- **Midnight crossing**: when the computed trigger time underflows midnight (e.g. 00:15 event with a 1-hour reminder), the notification fires at 23:15 on the **previous calendar day**. This is correct and expected behavior.
- **Reminder offset cap**: max 23 hours (`value * unit <= 23 hours`). This ensures the cron job always has time to schedule reminders for recurring events after advancing `next_occurrence`.
- Recipient resolution: at **send time**, resolve all current members who can see the event (house members for house-scoped; unit members for unit-scoped). This ensures membership changes between scheduling and sending are respected.
- **Send-time verification**: the notification worker MUST re-check authoritative state before delivering a reminder. A reminder is delivered **only if**: (1) the event still exists, (2) `state = 'active'`, (3) the reminder row still exists in `calendar_event_reminders`, and (4) the occurrence date still matches the event's current schedule. Stale jobs that fail these checks are silently dropped. This prevents notifications for cancelled, updated, or lifecycle-changed events even if queue cleanup races.
- Push eligibility follows [daily_notifications_phase1](../../../product/kinly/mobile/daily_notifications_phase1.md) rules: requires active device token, `os_permission = allowed`.
- Idempotency key: `(event_id, reminder_id, occurrence_date)` — prevents duplicate sends per reminder per occurrence.
- If the computed trigger time is already in the past at create/update time, that reminder is skipped for the current occurrence but scheduled for future occurrences of recurring events.
- Recurring events: after the cron job advances `next_occurrence`, reminders are scheduled for the new occurrence date.
- Event cancellation or update: all pending reminder notification jobs for this event are cleared and (for update) rescheduled.

## 8. Lifecycle Side Effects

### 8.1 Unit archive

When a unit is archived:
- All **active** calendar events where `unit_id` matches the archived unit are **auto-cancelled** (`state = 'cancelled'`, `cancelled_at = now()`, `next_occurrence = NULL`).
- All pending reminder notification jobs for those events are cleared.
- This avoids broadening visibility to the whole house (privacy-safe).

### 8.2 Creator leaves unit

When the event creator leaves or is removed from a unit (but remains in the home):
- All **active** calendar events where `created_by_user_id` matches the departing member AND `unit_id` matches the unit are **auto-cancelled** (`state = 'cancelled'`, `cancelled_at = now()`, `next_occurrence = NULL`).
- All pending reminder notification jobs for those events are cleared.
- Implementation: triggered as a side effect of unit membership removal, via internal helper `_calendar_events_cancel_for_unit_departure(p_user_id, p_unit_id)`.

### 8.3 Creator departure from home

When a member leaves or is kicked from a home:
- All **active** calendar events where `created_by_user_id` matches the departing member AND `home_id` matches are **auto-cancelled** (`state = 'cancelled'`, `cancelled_at = now()`, `next_occurrence = NULL`).
- All pending reminder notification jobs for those events are cleared.
- Implementation: triggered as a side effect of membership closure, via internal helper `_calendar_events_cancel_for_member_change(p_user_id, p_home_id)`. Same pattern as `_expense_plans_terminate_for_member_change` in [share_recurring_api_v1](../share/share_recurring_api_v1.md).

## 9. Coupling / Notes

- Product contract: [shared_calendar_v1](../../../product/kinly/shared/shared_calendar_v1.md)
- Unit model: [home_units_api_v1](home_units_api_v1.md) (scope resolution, composite FK, archived-unit behavior)
- Recurrence pattern: [chores_v2](../../../product/kinly/mobile/chores_v2.md) (same `recurrence_every`/`recurrence_unit` model)
- Notification infra: [daily_notifications_phase1](../../../product/kinly/mobile/daily_notifications_phase1.md) (FCM, device tokens, push eligibility)
- Creator departure pattern: [share_recurring_api_v1](../share/share_recurring_api_v1.md) (`_expense_plans_terminate_for_member_change`)

## 10. Assumptions

- `public.homes(id)` exists. `homes.timezone text NOT NULL` will be added by this contract.
- `public.profiles(id, full_name, avatar_storage_path)` exists.
- `public.home_units(id, home_id)` exists with composite unique key.
- `public.memberships(id, user_id, home_id, valid_to)` exists.
- `public.home_unit_members(unit_id, membership_id)` exists for unit membership checks.
- Notification infrastructure (FCM Edge Function, device tokens, notification sends) from `daily_notifications_phase1` is available.
- Membership closure hooks exist or can be extended (same mechanism used by expenses).
- Unit membership removal hooks exist or can be extended (for creator-leaves-unit lifecycle).

## 11. Out of Scope (v1)

- Google Calendar integration (busy/free sync, bidirectional propagation)
- Recurring multi-day events
- Recurring event exception editing (edit/cancel a single occurrence)
- Attendee RSVP or accept/decline
- Event attachments or images
- Calendar color-coding or categories
- Home timezone management UI
- Per-occurrence time overrides for multi-day events
