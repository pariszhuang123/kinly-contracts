---
Domain: Shared
Capability: Shared Calendar
Scope: shared
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
Canonical-Id: shared_calendar
Relates-To: contracts/api/kinly/homes/shared_calendar_api_v1.md
---

# Shared Calendar Contract v1

Status: Draft
Scope: Product contract for a shared calendar visible to all house members, with event scoping to house or unit (using the [home_units model](../../../api/kinly/homes/home_units_api_v1.md)).

## Domain overview

A home-level shared calendar allows members to create, view, and manage events that are visible to the entire house or scoped to a specific unit. Recurrence follows the same `recurrenceEvery` + `recurrenceUnit` pattern established in [chores_v2](../mobile/chores_v2.md), with an optional recurrence end rule of **Never** or **On date**. Reminders trigger push notifications before event start.

## Timezone authority

All calendar date/time logic uses the **home timezone** as the single authority.

- The home timezone is stored on the `homes` table as a new `timezone` column (IANA format, e.g. `Australia/Sydney`). See [schema addition](#schema-addition-homes-timezone).
- "Today", recurrence computation, occurrence expansion, and reminder scheduling all evaluate in the home timezone.
- Members in different physical timezones see the same calendar day and event times.

### Schema addition: `homes.timezone`

The `homes` table does **not** currently have a timezone column. This contract requires adding:

- `timezone text NOT NULL` — IANA timezone string (e.g. `'Australia/Sydney'`).
- Default: `'UTC'` (or determined at home creation based on the owner's locale/device).
- Existing homes MUST be backfilled.
- The value MUST be validated against the IANA timezone database on write (create/update/backfill). Invalid timezone strings MUST be rejected.
- The mechanism for setting/changing the home timezone is out of scope for this contract.

### DST handling

All local time computations use **wall-clock semantics**:
- **Spring-forward gap** (e.g. 02:00–03:00 doesn't exist): nonexistent local times shift forward to the next valid local instant.
- **Fall-back overlap** (e.g. 01:00–02:00 occurs twice): ambiguous local times resolve to the **earlier** offset (first occurrence).
- This applies to reminder trigger times, Today resolution, and recurrence computation.

## Allowed event types (v1)

| Type | Single-day | Multi-day | Recurring |
|---|---|---|---|
| One-off single-day | ✓ | | |
| One-off multi-day (all-day spans) | | ✓ | |
| Recurring single-day | | | ✓ |
| ~~Recurring multi-day~~ | | | **banned in v1** |

Constraints:
- When `recurrenceEvery` is set, `endDate` MUST equal `startDate`.
- When `recurrenceEvery` is set, `recurrenceEndsOn` MAY be `NULL` (`Never`) or a date on/after `startDate`.
- `startDate + startTime` MUST be strictly before `endDate + endTime` (combined datetime comparison).

## Multi-day events

Multi-day events are treated as **all-day date spans** in list and Today surfaces.

- The base event stores `startDate`, `endDate`, `startTime`, `endTime` for the full event definition.
- In occurrence rows (list/Today), multi-day events produce one row per day in the span. Each row carries `isStartDay` and `isEndDay` flags:
  - Start day: `isStartDay = true`, `isEndDay = false`
  - Middle days: both `false`
  - End day: `isStartDay = false`, `isEndDay = true`
  - Single-day: both `true`
- Clients use `isStartDay` / `isEndDay` to determine which time to display (start time on first day, end time on last day, all-day label on middle days).

### Multi-day occurrence ordering

Occurrence rows are ordered using a sort bucket to match standard calendar UX (all-day events above timed events):

| Day type | Sort bucket | Sort time |
|---|---|---|
| Middle day (all-day) | 0 | `00:00` |
| Start day | 1 | `startTime` |
| End day | 1 | `endTime` |
| Single-day / recurring | 1 | `startTime` |

Bucket 0 sorts before bucket 1. Within each bucket, sort by time, then `createdAt`. The server response is display-ready; clients MUST NOT re-sort.

## Entities

### CalendarEvent

- `id` (uuid)
- `homeId` (uuid)
- `createdByUserId` (uuid)
- `title` (text) — required, trimmed length 1–140
- `scopeType` (text) — `'house'` or `'unit'`; defaults to `'house'`
- `unitId` (uuid|null) — set when `scopeType = 'unit'`; FK -> `home_units(id, home_id)` composite
- `startDate` (date)
- `endDate` (date)
- `startTime` (time)
- `endTime` (time)
- `description` (text|null)
- `location` (text|null) — free text; client SHOULD trigger OS location picker / map intent
- `url` (text|null) — validated URL format
- `recurrenceEvery` (int|null) — `NULL` for one-off; `>= 1` for recurring
- `recurrenceUnit` (text|null) — one of `day|week|month|year`; `NULL` for one-off
- `recurrenceEndsOn` (date|null) — `NULL` means the series repeats indefinitely (`Never` in UI); when set, no occurrence may be generated after this date
- `nextOccurrence` (date|null) — next scheduled date; backend-managed; used for Today fast-path and cron advancement only
- `anchorDayOfMonth` (int|null) — original day-of-month anchor used to preserve RFC-compatible month/year recurrence intent
- `state` (text) — `'active'` or `'cancelled'`
- `cancelledAt` (timestamptz|null)
- `createdAt` (timestamptz)
- `updatedAt` (timestamptz)

> Note: there is no `draft` state. Events are created directly as `active` and remain editable by the creator.

Client presets (not server defaults):
- `startDate` = today (home tz)
- `endDate` = today
- `startTime` = now rounded up to next hour (home tz)
- `endTime` = `startTime + 1 hour`
- `scopeType` = `'house'`

### CalendarEventReminder

- `id` (uuid)
- `calendarEventId` (uuid) — FK -> `calendar_events(id)`, CASCADE
- `value` (int) — `>= 1`
- `unit` (text) — `'minutes'` or `'hours'`
- `createdAt` (timestamptz)

Constraints:
- `value >= 1`
- `unit IN ('minutes', 'hours')`
- Max 5 reminders per event (enforced by RPC)
- Duplicate `(value, unit)` pairs within the same event MUST be rejected
- Reminder offset MUST NOT exceed 23 hours: `value <= 1380` when `unit = 'minutes'`, `value <= 23` when `unit = 'hours'`. This ensures the cron job (every 15 min) always has time to schedule reminders for recurring events after advancing `nextOccurrence`.

### CalendarEventDetailDto

Subset used on detail/edit screens:

- `id: uuid`
- `homeId: uuid`
- `createdByUserId: uuid`
- `title: string`
- `scopeType: text`
- `unitId: uuid | null`
- `startDate: date`
- `endDate: date`
- `startTime: time`
- `endTime: time`
- `description: string | null`
- `location: string | null`
- `url: string | null`
- `recurrenceEvery: int | null`
- `recurrenceUnit: text | null`
- `recurrenceEndsOn: date | null`
- `state: text`
- `cancelledAt: timestamptz | null`
- `reminders: CalendarEventReminderDto[]`
- `creator: CalendarEventCreatorInlineDto`

> Note: does **not** include `nextOccurrence`, `anchorDayOfMonth`, `createdAt`, `updatedAt`. Clients MUST NOT rely on those being present.

#### CalendarEventReminderDto

- `id: uuid`
- `value: int`
- `unit: text`

#### CalendarEventCreatorInlineDto

- `id: uuid` (user id)
- `fullName: string`
- `avatarStoragePath: string | null`

### CalendarEventOccurrenceDto

Returned by list/today RPCs. Represents one occurrence of an event (one row per visible date).

- `eventId: uuid`
- `occurrenceDate: date`
- `startTime: time`
- `endTime: time`
- `title: string`
- `scopeType: text`
- `unitId: uuid | null`
- `location: string | null`
- `isRecurring: boolean`
- `isStartDay: boolean`
- `isEndDay: boolean`
- `creatorUserId: uuid`
- `creatorFullName: string`
- `creatorAvatarStoragePath: string | null`

For single-day and recurring events: `isStartDay = true`, `isEndDay = true`.
For multi-day events: see [Multi-day events](#multi-day-events).

## Enums

- `CalendarEventState` = `active | cancelled`

## Validation and business rules

### Recurrence (matches chores_v2)
- `recurrenceEvery` IS NULL iff `recurrenceUnit` IS NULL.
- `recurrenceEndsOn` MUST be `NULL` for one-off events.
- When set:
  - `recurrenceEvery >= 1`
  - `recurrenceUnit IN ('day','week','month','year')`
  - `endDate` MUST equal `startDate` (recurring multi-day banned in v1)
  - `recurrenceEndsOn`, when present, MUST be on/after `startDate`
- Initial schedule computation (create/update):
  - `local_today = (now() AT TIME ZONE home_tz)::date`
  - `base_date = COALESCE(startDate, local_today)`
  - One-off: `nextOccurrence = base_date`
  - Recurring: compute the first occurrence on/after `base_date`, then roll forward until `nextOccurrence >= local_today`
  - If the next recurring occurrence would fall after `recurrenceEndsOn`, `nextOccurrence = NULL`
  - `nextOccurrence` is updated by the backend only

### Recurrence end behavior

Recurring events expose an `Ends` choice in product surfaces:

- `Never` -> `recurrenceEndsOn = NULL`
- `On date` -> `recurrenceEndsOn = <date>`

Rules:

- `Never` does **not** materialize unlimited rows. The backend stores one base event row plus reminder rows. Occurrence rows are derived only for the requested query window.
- When a series is changed from `Never` to `On date`, all derived occurrences after `recurrenceEndsOn` disappear immediately from range queries and Today.
- When a series is changed from `Never` to `On date`, `nextOccurrence` is recomputed. If no future occurrence exists on/before `recurrenceEndsOn`, `nextOccurrence` becomes `NULL`.
- An ended recurring series remains the same event record. It is not converted to `cancelled`; it simply has no future occurrences.
- When a series is changed from `On date` back to `Never`, `nextOccurrence` is recomputed from the current schedule and future reminders are rescheduled.

### Recurrence stepping rules (unit-specific)

All recurrence computation (create, update, cron advancement, range expansion) MUST use a **single shared backend helper** to guarantee consistency. The stepping rules per unit are:

- **`day`**: add `recurrenceEvery` calendar days. Pure integer date arithmetic.
- **`week`**: add `recurrenceEvery * 7` calendar days. Pure integer date arithmetic.
- **`month`**: add `recurrenceEvery` calendar months from the **original `startDate`**. Step `n` = `startDate + (n * recurrenceEvery) months`, preserving the original day-of-month intent. If the target month does not contain that day, that occurrence is **skipped** rather than clamped.
- **`year`**: add `recurrenceEvery` calendar years from the **original `startDate`**. Step `n` = `startDate + (n * recurrenceEvery) years`, preserving the original day-of-month intent. If the target year/month does not contain that day (for example Feb 29 in a non-leap year), that occurrence is **skipped** rather than clamped.

Occurrences MUST NOT be generated before `startDate`. When the query range starts before `startDate`, expansion begins at step `n = 0`.

### RFC-compatible invalid-date behavior

For monthly and yearly recurrence, the backend preserves the original `anchorDayOfMonth` from `startDate`, but follows RFC-compatible invalid-date behavior:

- if the target month/year contains the anchored day, emit the occurrence
- if the target month/year does **not** contain the anchored day, skip that occurrence
- skipped dates are not replaced with the month's last day

Examples:
- Jan 31 monthly → Mar 31 → May 31 → Jul 31
- Jan 30 monthly → Mar 30 → Apr 30 → May 30 (February is skipped)
- Feb 29 yearly → Feb 29 in leap years only; non-leap years are skipped

### Recurring event cadence advancement

Unlike chores (which advance on "complete"), calendar events advance automatically via a **cron job running every 15 minutes**.

- Job name: `calendar_events_advance_recurring`
- Schedule: `*/15 * * * *` (every 15 minutes)
- Behavior: for each active recurring event where `next_occurrence < local_today` (home tz), advance `next_occurrence` to the next date strictly on/after `local_today` using the shared recurrence helper. Schedule reminder notification jobs using the **one-lookahead rule** (see below).
- This ensures recurring events appear on their next due date in Today within at most 15 minutes of the local day flip.
- Re-running the job is idempotent.

### One-lookahead reminder scheduling (recurring events)

Recurring reminders that fire on the previous calendar day (e.g. a 12-hour reminder for an 08:00 event fires at 20:00 the night before) would be missed if reminders were only scheduled for the current occurrence at advancement time. To prevent this:

- Whenever a recurring event is **created, updated, or advanced by the cron job**, reminder notification jobs are scheduled for **both the current occurrence AND the immediately following occurrence**.
- The immediately following occurrence is scheduled only if it exists and does not fall after `recurrenceEndsOn`.
- The 23-hour offset cap bounds the lookahead window — one extra occurrence is always sufficient.
- On update, cancel, or lifecycle cleanup, pending jobs for **both** scheduled occurrence horizons are cleared.
- The existing send-time verification + idempotency key `(event_id, reminder_id, occurrence_date)` prevents duplicate or stale sends.

Example: daily event at 08:00, 12-hour reminder.
- Cron advances `nextOccurrence` to Apr 10 and schedules reminders for Apr 10 (fires Apr 9 at 20:00) **and** Apr 11 (fires Apr 10 at 20:00).
- Next cron run advances to Apr 11, clears old jobs, schedules for Apr 11 + Apr 12. The Apr 10 20:00 job already fired and is idempotent.

### Occurrence expansion for range queries

Range queries (list RPC) MUST NOT depend on mutable `nextOccurrence`. Instead, occurrences are **derived at query time** from immutable fields using the shared recurrence helper:

- `startDate` — series anchor
- `recurrenceEvery` — step size
- `recurrenceUnit` — step unit
- `anchorDayOfMonth` — original day-of-month anchor for RFC-compatible month/year recurrence
- `recurrenceEndsOn` — inclusive upper bound for recurring occurrence generation

Algorithm:
1. If `range_start <= startDate`, begin at step `n = 0`.
2. Otherwise, estimate the step count to reach `range_start` and generate the occurrence at that step (using unit-specific rules above).
3. If the generated date is before `range_start`, increment `n` and regenerate.
4. Continue stepping forward, emitting one occurrence row per step, until the generated date exceeds `range_end`.
5. If `recurrenceEndsOn` is set, stop emitting once the generated date would be later than `recurrenceEndsOn`.
6. Occurrences before `startDate` MUST NOT be emitted.

`nextOccurrence` is used **only** by:
- The Today RPC for the fast-path `next_occurrence = local_today` filter
- The cron job for determining which events need advancement

### Scope/visibility
- `scopeType = 'house'`: event is visible to all current home members.
- `scopeType = 'unit'`: event is visible only to current members of that unit.
- **Create/update scope targeting**: `unitId` MUST equal the caller's **exact resolved allowed unit** per [home_units_api_v1](../../../api/kinly/homes/home_units_api_v1.md) scope resolution rules.
- **Existing event visibility/editability**: uses actual current membership in `event.unitId`. The creator must currently be a member of the event's unit to view, edit, or cancel it. If the creator is no longer in the unit, the event behaves as `NOT_FOUND` for them.
- Backend MUST reject archived units, wrong-home units, and units the creator does not belong to.
- Composite FK `(unit_id, home_id)` -> `home_units(id, home_id)` enforces same-home integrity.

### Unit archive lifecycle
- If a unit is archived after event creation, all **active** unit-scoped events for that unit are **auto-cancelled** (`state = 'cancelled'`, `cancelledAt = now()`, `nextOccurrence = NULL`). Pending reminder jobs are cleared.
- This avoids the privacy leak of broadening visibility to the whole house.

### Creator leaves unit lifecycle
- When the event creator leaves or is removed from a unit (but remains in the home), all **active** unit-scoped events where `createdByUserId` matches the departing member AND `unitId` matches the unit are **auto-cancelled** (`state = 'cancelled'`, `cancelledAt = now()`, `nextOccurrence = NULL`). Pending reminder jobs are cleared.
- This prevents orphaned unit-scoped events that nobody can manage.

### Creator departure lifecycle
- When a member leaves or is kicked from a home, all **active** calendar events where `createdByUserId` matches the departing member are **auto-cancelled** (`state = 'cancelled'`, `cancelledAt = now()`, `nextOccurrence = NULL`). Pending reminder jobs are cleared.
- This prevents orphaned events that nobody can edit or cancel.
- This lifecycle MUST be triggered as a side effect of membership closure (same pattern as `_expense_plans_terminate_for_member_change` in [share_recurring_api_v1](../../../api/kinly/share/share_recurring_api_v1.md)).

### Reminders
- Stored as rows in `calendar_event_reminders`.
- Each reminder has `value` (int >= 1) and `unit` (`'minutes'` | `'hours'`).
- Max 5 reminders per event.
- Duplicate `(value, unit)` pairs within the same event MUST be rejected.
- Reminder offset MUST NOT exceed 23 hours (`value * unit <= 23 hours`). Offsets exceeding this cap MUST be rejected with `INVALID_INPUT`.
- **Multi-day events**: reminders are anchored to `startDate + startTime` only (the beginning of the event), not to each visible day in the span.
- Backend schedules push notifications at `startTime - (value * unit)` on the event's `startDate`, evaluated in home timezone.
- **Midnight crossing**: when the computed trigger time underflows midnight (e.g. 00:15 event with a 1-hour reminder), the notification fires at 23:15 on the **previous calendar day**. This is the correct behavior.
- Reminder recipients are resolved **at send time** based on current visibility (house membership or unit membership at that moment).
- **Send-time verification**: the notification worker MUST re-check authoritative state before firing. A reminder is delivered only if: the event still exists, `state = 'active'`, the reminder row still exists, and the occurrence date still matches the event's current schedule. This prevents stale notifications after update/cancel/lifecycle changes.
- If the computed trigger time is already in the past at create/update time, that reminder is skipped for the current occurrence (but scheduled for future occurrences of recurring events).
- Reminders follow the same push eligibility rules as [daily_notifications_phase1](../mobile/daily_notifications_phase1.md): requires active device token, `os_permission = allowed`.
- Idempotency key: `(event_id, reminder_id, occurrence_date)` — prevents duplicate sends.
- Recurring events: reminders are scheduled for the next occurrence when the cron job advances `nextOccurrence`.
- Cancelled events: all pending reminder notification jobs are cleared.

### Permissions
- Any home member (or unit member for unit-scoped events) can **view** events.
- Only the creator (`createdByUserId`) can **edit** or **cancel** an event, AND the creator must currently have visibility (home member for house-scoped; unit member for unit-scoped). If the creator cannot see the event, it behaves as `NOT_FOUND`.
- Cancelling sets `state = 'cancelled'`, `cancelledAt = now()`, `nextOccurrence = NULL`.

### Title
- Required, non-empty after trim, max 140 characters.

### URL
- When provided, MUST be a valid URL format. Backend MUST validate.

### Dates and times
- `startDate + startTime` MUST be strictly before `endDate + endTime` (combined datetime comparison). This replaces the weaker `endDate >= startDate` constraint.
- When `startDate = endDate`: this naturally requires `endTime > startTime`.
- When `startDate < endDate`: `startTime` and `endTime` are independent (e.g. start at 18:00, end at 09:00 the next day is valid).
- `startTime` and `endTime` are required parameters with no server default.
- `startDate` and `endDate` default to `local_today` (home tz) when omitted, computed in the RPC (not as table defaults).

## Product rules

1. Events are created directly as `active`. There is no draft state.
2. Active events remain editable by the creator (full-replacement updates; all mutable fields sent each time).
3. Events scoped to `house` are visible to every current home member.
4. Events scoped to `unit` are visible only to current members of that unit, following exact `home_units` scope resolution.
5. Any home member can create an event; scope defaults to `house`.
6. Only the event creator can edit or cancel an event, and only while they have visibility.
7. Reminders trigger push notifications to all members who can view the event **at send time**, delivered at `startTime - (value * unit)` in home timezone. Reminders that cross midnight fire on the previous calendar day. For multi-day events, reminders anchor to `startDate + startTime` only.
8. The notification worker MUST verify event state and reminder existence before delivering. Stale jobs are silently dropped.
9. Recurring events follow the same `recurrenceEvery` + `recurrenceUnit` pattern as chores. Backend computes `nextOccurrence`. A cron job running every 15 minutes advances past-due occurrences.
10. Recurring events MAY end either `Never` or `On date` via `recurrenceEndsOn`. `Never` means no upper bound; it does not create infinite stored rows.
11. Changing a recurring series from `Never` to `On date` trims all future derived occurrences after that date and recomputes `nextOccurrence`.
12. Recurring multi-day events are not allowed in v1.
13. Multi-day events are treated as all-day date spans in list/Today surfaces with `isStartDay`/`isEndDay` flags.
14. Monthly/yearly recurrence follows RFC-compatible invalid-date skipping. If a target month/year does not contain the anchored day, that occurrence is skipped rather than clamped.
15. The `location` field is free text; the client SHOULD trigger the OS location picker or map intent to assist input.
16. Max 5 reminders per event. Duplicate `(value, unit)` pairs are rejected. Offset capped at 23 hours.
17. If a unit is archived, its unit-scoped events are auto-cancelled (not broadened to house).
18. If the creator leaves the unit (but stays in the home), their unit-scoped events for that unit are auto-cancelled.
19. If the creator leaves the home, all their active events are auto-cancelled.
20. Range queries derive occurrences from immutable series fields at query time. Clients receive display-ready occurrence rows without needing client-side recurrence math. Max query span is 366 days.
21. All recurrence computation uses a single shared backend helper for consistency.

## Today screen integration

Events appear in the Today flow when:
- **One-off (single or multi-day)**: `start_date <= local_today AND end_date >= local_today` AND `state = 'active'`
- **Recurring (single-day)**: `next_occurrence = local_today` AND `state = 'active'`

Where `local_today = (now() AT TIME ZONE home_tz)::date`.

The Today RPC returns **occurrence rows** (`CalendarEventOccurrenceDto`), not base event rows.

Ordering: sort bucket (all-day first), then time, then `createdAt`. See [Multi-day occurrence ordering](#multi-day-occurrence-ordering).

Visibility: house-scoped events visible to all members; unit-scoped events visible only to unit members.

## List (range query) behavior

The list RPC returns **occurrence rows** for a requested date range. The backend expands occurrences at query time from immutable fields:
- One-off single-day events that fall within the range
- One-off multi-day events: one occurrence row per day in the overlap of `[startDate, endDate]` and the query range, with `isStartDay`/`isEndDay` flags
- Recurring single-day events: all occurrences within the range, computed by stepping from `startDate` using unit-specific RFC-compatible rules with invalid-date skipping for monthly/yearly recurrences. Occurrences before `startDate` are never emitted.

Maximum query span: **366 days** (`p_end_date - p_start_date <= 366`). Requests exceeding this MUST be rejected with `INVALID_INPUT`.

Ordering: `occurrenceDate ASC`, then sort bucket (all-day first), then time, then `createdAt`.

This allows the client to render week/month calendar views directly from the response without client-side recurrence math.

## Out of scope (v1)

- **Google Calendar integration**: personal calendar shows busy/free only, shared calendar events sync to personal calendar, and changes to shared calendar propagate to personal calendar.
- Attendee RSVP or accept/decline.
- Event attachments or images.
- Recurring multi-day events.
- Recurring event exception editing (edit/cancel a single occurrence of a recurring series).
- Calendar color-coding or categories.
- Home timezone management UI (mechanism for setting/changing `homes.timezone`).
- Per-occurrence time overrides for multi-day events.
