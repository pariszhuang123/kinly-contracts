---
Domain: Shared
Capability: Chores
Scope: frontend
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
---

# Chore Wheel v1

Status: Draft (gamified chore assignment via spinning wheel)  
Scope: Adds an optional spinning-wheel assignment flow on top of the existing weekly chore system. The wheel introduces randomness and engagement to chore distribution within a home.

## Product Goal

Make weekly chore assignment more fun and engaging by turning it into a shared moment — a spinning wheel that randomly assigns chores to home members. Removes the friction of "who assigns the tasks" by letting the wheel decide.

## Schema Dependency

This contract depends on the `assignment_method` column added to `public.chores` in [chores_v2](chores_v2.md):
- `assignment_method IN ('manual', 'wheel')`, nullable, default `NULL`.
- The client always passes `assignment_method = 'wheel'` for all chores in a wheel session. The backend persists `'wheel'` only for weekly recurring chores; non-weekly chores are silently treated as `'manual'`.
- Manual re-assignment of a wheel-managed chore flips `assignment_method` to `'manual'`, removing it from future wheel sessions.

## Eligibility

The wheel option MUST appear when the **wheel-eligible chore count** is 3 or more.

Wheel-eligible chores are the union of:

| Source | Filter |
|---|---|
| New drafts | `state = 'draft'` (any recurrence type) |
| Re-spin candidates | `state = 'active'` AND `assignment_method = 'wheel'` AND `recurrence_unit = 'week'` AND `next_occurrence < current_date` |

Both pools are combined into a **single wheel session**.

The `next_occurrence < current_date` filter (strictly less than) on re-spin candidates provides a **1-day grace period**: on the day a chore is due, the current assignee has the chance to complete it. Only if the chore remains incomplete the following day does it enter the re-spin pool. Chores completed on their due day have `nextOccurrence` rolled forward and naturally drop out.

Additional guards:
- The wheel MUST NOT appear if fewer than 2 home members exist.
- The wheel is optional — members MAY still assign chores manually.

## Wheel Mechanics

### Wheel Display
- The wheel MUST display each home member as a segment.
- Each segment MUST show the member's **avatar** and **username**.
- Segment sizing MUST be equal (fully random; no weighting in v1).

### Spin Flow
1. Any active home member taps "Spin the Wheel" to begin.
2. Eligible chores are presented in **creation-time order** (`created_at ASC`).
3. For each chore:
   a. The chore name is displayed above the wheel.
   b. The wheel animates a spin.
   c. The wheel lands on a random member.
   d. A brief result card is shown: **"[Chore Name] → [Member Name]"**.
   e. The next chore is queued automatically.
4. A single member MAY receive all chores or none — distribution is **fully random** with no balancing in v1.

### Results Screen
- After all chores have been spun, a **results summary** MUST be displayed.
- The summary MUST group by member, showing:
  - Member avatar and username.
  - Number of chores assigned.
  - List of specific chore names.
- A **"Confirm"** action finalises all assignments.
- A **"Re-spin"** action discards results and restarts the session.
- A **"Cancel"** action dismisses without persisting anything.

### Confirmation & Persistence
- On confirm, for each chore in the session the client calls `chores_update_v2` with `assignmentMethod = 'wheel'` and the selected `assigneeUserId`. No client-side branching is needed.
- The backend decides what to persist: `assignment_method = 'wheel'` is stored only for weekly recurring chores. Non-weekly chores (one-off, daily, etc.) are silently treated as `'manual'` and will not appear in future re-spin sessions.
  - **Draft chores**: transitions `state` from `draft` → `active`.
  - **Re-spin chores**: updates `assigneeUserId` to the new member, stays `active`.
- All updates are fire-and-forget per chore (no batch RPC). Failures on individual chores are handled per the concurrency rules below.
- If the user cancels or dismisses before confirming, no assignments are persisted.

## Weekly Re-spin Lifecycle

The wheel does **not** require chores to return to `state = 'draft'`. Instead:

1. Chores assigned via the wheel have `assignment_method = 'wheel'`.
2. When a weekly recurring chore's cycle completes, the existing recurrence logic rolls `nextOccurrence` forward. The assignee stays the same.
3. If **nobody re-spins** that week, the current assignee keeps the chore. No disruption.
4. The day after `nextOccurrence` (i.e., `next_occurrence < current_date`), if the chore was not completed, it reappears as a re-spin candidate alongside any new drafts.
5. On confirm, those chores get a new (or same) random assignee.
6. If a member **manually re-assigns** a wheel-managed chore (e.g., via the edit screen), `assignment_method` flips to `'manual'` and the chore no longer appears in future wheel sessions.

This means the wheel is **opt-in every week** — it never forces a re-assignment.

## Randomness

- v1 uses **uniform random** selection — every member has equal probability per spin regardless of prior results within the same session.
- No fairness balancing, history weighting, or exclusion rules in v1.

## Partial Abandon

- The spin session is entirely client-side until confirm.
- If the app is killed, crashes, or the user navigates away mid-spin, the session is lost.
- No assignments are persisted. The user can re-open and spin again.

## Concurrent Spin

- No backend spin-lock in v1.
- Two members MAY initiate a spin simultaneously.
- On confirm, each `chores_update_v2` call operates independently:
  - **Draft → active**: first confirmer wins. If the chore is already active when the second confirmer's call arrives, the update still succeeds (re-assigns the chore; last-writer-wins).
  - **Active → active (re-spin)**: last-writer-wins. The result is still a valid assignment.
- If any individual update fails (e.g., chore was cancelled between spin and confirm), the client SHOULD show a toast for the failed chore and proceed with the rest.

## Constraints

- Minimum 2 home members to show the wheel.
- Minimum 3 wheel-eligible chores to show the wheel.
- Chore ordering in the spin queue: `created_at ASC`.
- The spin animation is client-side only; the backend receives final assignments via existing `chores_update_v2` RPC.
- Members who join mid-week will appear on the wheel the next time a spin is initiated; they simply have no chores for the current week if a spin already occurred.

## Out of Scope (v1)

- Weighted probability based on past assignments or preferences.
- Allowing members to opt out of specific chores.
- Multi-home wheel sessions.
- Push notifications for wheel results.
- Undo/re-spin for individual chore assignments (only full re-spin).
- Backend spin-lock or session coordination.
