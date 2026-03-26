---
Domain: Shared
Capability: Share Recurring Product
Scope: shared
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.1
---

# Kinly Share - One-Off & Recurring Expenses (Product) v1.1

Purpose: product-facing rules and UX expectations for one-off and recurring
expenses, now aligned with Home Units v1. API/DB details live in
`contracts/api/kinly/share/expenses_v2.md`.

## Core Principles (product lens)

- Plans define intent; expenses are immutable snapshots once active.
- Drafts are creator-only and quota-free; activation is a one-way door.
- Expenses support two allocation target modes:
  - `unit_based` - preferred for homes using Home Units
  - `debtor_based` - compatibility mode for direct person-by-person charging
- In `unit_based` mode:
  - a personal unit represents one individually liable member
  - a shared unit represents one grouped debtor bucket
  - the app does not infer internal cost sharing inside a shared unit
- Creator cannot be the sole liable target on an activated expense.
- Cron always generates cycles; paywall blocks user-triggered activation, not
  cron.
- Termination stops future cycles; history remains payable.

## Allocation Modes

### Unit-based allocation

This is the preferred product path when Home Units are enabled.

Behavior:
- expense create/edit lets the user target units
- if the current member belongs to an active shared unit, the grouped-by-unit
  mode SHOULD be preselected
- the user MAY still switch to a personal unit before submit
- if a shared unit is selected, all current members of that shared unit see the
  resulting shared liability
- the app MUST NOT show inferred equal-share debt inside that shared unit unless
  an explicit internal split product is introduced later

### Debtor-based allocation

This remains a compatibility path for cases where the user explicitly wants to
charge named individuals rather than units.

Behavior:
- expense create/edit may expose a grouped-by-unit toggle or equivalent mode
  control
- when not grouped by unit, the app may show direct individual debtors instead

## Lifecycle (user-facing)

- Draft -> Activate one-off:
  - validate allocation
  - set active
  - immutable thereafter

- Draft -> Activate recurring:
  - create plan
  - convert draft to `converted`
  - generate first cycle immediately
  - cron generates future cycles

- Terminate:
  - creator stops future cycles
  - past cycles remain payable

## Recurring Rules

- A recurring plan stores the allocation intent source:
  - debtor-based source for debtor mode
  - unit-based source for unit mode
- Each generated cycle snapshots that allocation into the cycle expense.
- Historical or already-generated cycles MUST NOT be rewritten merely because:
  - a shared unit changes membership
  - a member leaves the home
  - a member joins a different shared unit later

## Surface Expectations

- Recurring cycles appear in Today and Explore as regular active expenses.
- Expense rows MUST carry enough metadata for the UI to distinguish:
  - `Personal`
  - `Shared`
  - debtor-based direct charges, where still supported
- Shared liabilities appear as one open row for all current members of that
  shared unit.
- If a shared liability is fully settled by any member, it disappears from Today
  for all members of that shared unit.
- `expenses_get_for_edit` MUST expose enough information to reconstruct the
  chosen allocation mode and targets.
- Cron-generated cycles must not trigger user paywall interruptions; user-driven
  activation still enforces quota.

## Today Expectations

- Today SHOULD show a single list of open liabilities.
- Each row MUST include a visible liability label such as:
  - `Personal`
  - `Shared`
- If an expense targets a personal unit:
  - it appears only for that member
- If an expense targets a shared unit:
  - it appears for all current members of that shared unit
  - it shows the shared unit name
  - it shows unit-level remaining amount, not inferred per-member debt

## Shopping List Coupling

- Shopping-list item scope remains separate from expense allocation, but the two
  should feel consistent to the user.
- Shopping-list default scope is `House`.
- Item scope may later hand off into expense creation, but the app MUST NOT
  imply that a shopping-list item scoped to `Shared` also defines an internal
  split inside that shared unit.

## Paywall & Usage (product slice)

- Drafts do not consume `active_expenses`.
- First cycle activation enforces quota.
- Cron cycles bypass quota checks but still increment usage.
- Full payment decrements active usage where the backend contract says it does.

## Copy / UX Notes

- Reflect recurring state in subtitles, for example "Every month", via l10n.
- Use non-blocking messaging for cancel/terminate confirmations.
- Keep creator form state intact when hitting paywall; retry post-entitlement
  using the same inputs.
- When unit-based mode is active, copy should clearly frame the target as:
  - one personal unit, or
  - one shared unit
  and not as an inferred split between people.

## Non-goals

- Internal cost sharing within a shared unit
- Silent reassignment of existing expense liabilities when unit composition
  changes
- Mandatory debtor-based charging when a shared unit exists
