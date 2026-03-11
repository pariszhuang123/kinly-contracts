---
Domain: Homes
Capability: House Directory
Scope: shared
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
---

# House Directory Contract v1

Status: Proposed

Scope: Shared home operational reference data for wifi access, home service
accounts, and home links, including derived renewal reminders.

Audience: Product, design, engineering, AI agents.

Depends on:
- Homes v2 (membership and role model)
- Personal Directory capability (separate person-scoped information)
- House Norms capability (separate behavior/social agreements)

## 1. Purpose

House Directory provides a calm, structured source of truth for shared
household operations.

House Directory MUST support:
- wifi access details
- home service/account references
- home-related external links
- derived renewal reminders for time-bound home accounts

## 2. Scope and boundaries

In scope:
- shared home operations, not person-specific records
- link-based references, not file hosting
- reminder logic derived from account term windows

Out of scope:
- House Norms content and workflows
- standalone House Rules policy workflows
- personal bank/emergency/document records
- document binary upload and hosting

## 3. Core entities (shared semantics)

### 3.1 Wifi profile
- A home MAY have at most one wifi profile.
- Wifi profile includes `ssid` and optional `password`.
- QR payload is derived from stored wifi values.

### 3.2 Home account
- Represents one home service record:
  - `rent`
  - `wifi`
  - `electricity`
  - `gas`
  - `water`
  - `other`
- `other` requires a non-empty `custom_label`.
- Each account includes `provider_name`, `link_url`, and optional term dates.
- `rent` MUST include both `term_start_date` and `term_end_date`.

### 3.3 Home link
- Represents a curated external home link with tags:
  - `rent`
  - `bond`
  - `utilities`
  - `other`
- Tag `other` requires `custom_tag`.
- Link rows are URL references only.

### 3.4 Renewal reminder
- Renewal reminders are derived, not user-authored.
- Reminder eligibility requires both `term_start_date` and `term_end_date`.
- Default reminder date is `term_end_date - 3 calendar months` (date-only).
- Reminder is valid only when `term_start_date <= reminder_at < term_end_date`.
- If the computed reminder date is before term start, reminder MUST NOT exist.

## 4. Reminder lifecycle invariants

- Reminder identity is scoped to:
  - `account_id`
  - `reminder_kind`
  - `term_start_date`
  - `term_end_date`
- Dismissal applies only to that identity.
- If term dates change, a new reminder identity MUST be used.
- A dismissed reminder for an old term MUST NOT suppress a new valid reminder.
- If current UTC date is after `term_end_date`, the reminder is not active for
  Today surfacing.

## 5. Access and privacy rules

- Read access: current home members.
- Write access: current home owner only.
- Wifi password is a sensitive operational secret:
  - storage is allowed for home operations
  - value MUST be masked by default in UI
  - value MUST NOT be emitted to telemetry payloads
  - only authorized home members may view/copy it

## 6. Cross-capability relationships

- House Directory stores shared operational facts.
- House Norms stores shared behavioral expectations.
- Personal Directory stores person-specific records.
- Contracts MUST remain separated; cross-links are allowed, duplication is not.

## 7. Contract test scenarios

- `rent` account creation without term dates is rejected.
- Reminder is absent when computed reminder date precedes term start.
- Expired terms are not surfaced as active reminders in Today.
- Term change creates a new reminder identity and does not reuse old dismissal.
- Wifi password appears masked by default and is absent from telemetry.

```contracts-json
{
  "domain": "house_directory",
  "version": "v1",
  "entities": {
    "WifiProfile": {},
    "HomeAccount": {},
    "HomeLink": {},
    "HomeReminderState": {}
  },
  "functions": {},
  "rls": []
}
```
