---
Domain: Homes
Capability: House Directory Mobile
Scope: frontend
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
---

# House Directory Mobile Contract v1

Status: Proposed

Scope: Mobile app behavior for rendering and mutating House Directory data.

Audience: Product, design, engineering, AI agents.

Depends on:
- House Directory Contract v1
- House Directory API v1

## 1. Screen structure

House Directory screen SHOULD present these sections in order:
1. Wifi
2. Services
3. House notes

Today surface MAY include renewal reminder cards sourced from API reminders.

## 2. Wifi section rules

- Wifi card defaults collapsed.
- Card supports expand/collapse for QR visibility.
- SSID copy action MUST be available.
- Mobile clients MUST treat wifi password as write-only owner input in v1.
- Member read flows MUST NOT expect plaintext password in API responses.
- If an owner enters or updates a password, the input MUST be masked by default
  and reveal requires explicit user action.
- Security type is not user-entered in v1.
- If password is empty/null, UI treats wifi as open network in QR payload.

## 3. Service card rules

Must show:
- provider name
- account type label
- term dates when present
- renewal reminder only when valid and active
- custom label when `service_type='other'`
- account reference when present
- link action when `link_url` is present
- notes preview only when notes are present and the surface is explicitly
  intended to show free-form service notes

## 4. House notes rules

- Display title and note details preview.
- Optional URL action may be shown when `reference_url` is present.
- Optional photo thumbnail may be shown when `photo_path` is present.
- Notes are for flexible home context, not structured provider data.
- Note photo capture should use the app photo flow and store only the storage
  path in app data.
- If adding a note photo would exceed plan quota, the app MUST present the
  paywall gate before retrying the action.
- Replacing an existing note photo MUST NOT count as an additional paid usage
  event.

## 5. Validation and mutation UX

- Submit actions must be blocked until required fields are valid.
- `other` account type requires `custom_label`.
- `rent` account requires both term dates.
- End date before start date is rejected client-side when detectable.
- House note requires non-empty `title` and `details`.
- House note URL is optional but must be valid when present.
- API error envelope `{ code, message, details }` MUST be surfaced with calm,
  non-technical copy.

## 6. Reminder visibility rules

A renewal reminder is shown on Today only when all are true:
- reminder date is valid for the term window
- current UTC date is on or after reminder date
- reminder state matches current term identity
- reminder state status is `active`
- current member has not already acknowledged the reminder

If reminder is invalid because computed date is before term start:
- no reminder text
- no reminder card

Acknowledgement behavior:
- acknowledging reminder hides it only for the current member
- acknowledgement does not dismiss the reminder globally

Dismissal behavior:
- only owners may dismiss reminders
- dismissing reminder removes it for that specific term identity for all
  members
- if term dates or reminder timing change materially and a new active reminder
  is created, the card may reappear and prior acknowledgements are cleared

## 7. Loading, empty, and error states

- Empty state SHOULD explain that House Directory is a shared operational space.
- Loading state should preserve layout stability.
- Error state should support retry and avoid destructive assumptions.
- Sensitive values (wifi password) must not be shown in logs/crash payloads.

## 8. Analytics and privacy

- Allowed events may track generic actions (expand wifi card, copy ssid,
  reminder dismissed).
- Analytics payloads MUST NOT include:
  - wifi password
  - account_reference raw value
  - free-form notes text
  - external URL query parameters with secrets

## 9. Contract test scenarios

- Wifi password is masked on initial render.
- Wifi member read flow does not expose or depend on plaintext password.
- Rent card does not submit without both term dates.
- Reminder card not shown for invalid pre-start reminder.
- Member acknowledgement hides reminder only for that member.
- Reminder card disappears after owner dismissal for current term identity.
- Reminder card can reappear after term update creates new identity.
- Member can read; owner-only actions are disabled or blocked for non-owner.

## 10. References

- [House Directory Contract v1](../shared/house_directory_v1.md)
- [House Directory API v1](../../../api/kinly/homes/house_directory_api_v1.md)
