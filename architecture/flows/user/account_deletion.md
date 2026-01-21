---
Domain: Flows
Capability: Account Deletion
Scope: platform
Artifact-Type: architecture
Stability: evolving
Status: draft
Version: v1.0
---

# Flow — Account Deletion (Admin-Approved)

Contracts: v1 (`docs/contracts/users_v1.md`, `docs/contracts/homes_v1.md`)
Diagram: `docs/diagrams/user/account_deletion.md`

## Preconditions
- User is authenticated and requests deletion via Edge Function.

## Postconditions
- If approved:
  - For each owned home with no other active members: home is set inactive and `deactivatedAt` set; owner membership marked `leftAt`.
  - For each non-owned active membership: membership marked `leftAt`.
  - Auth user deleted; `user_profile` anonymized; access revoked.
- If blocked: user/admin must transfer ownership of homes where other active members exist.

## Flow (Given/When/Then)
Given an authenticated user
When they submit an account deletion request
Then an admin reviews and approves; an Edge Function deletes the Auth user and anonymizes PII, unless active memberships exist

## Steps
1. App calls Edge Function `users.selfDelete()`.
2. Edge lists caller's active memberships and owned homes.
3. Edge performs DB changes first, then Auth deletion:
   - For each owned home with other active members: select new owner (earliest active member; tiebreaker lowest userId) and call `homes.transferOwner`.
   - For each owned home with no other members: set `home.isActive = false` and `home.deactivatedAt = now()`; set owner membership `leftAt = now()`.
   - For each non-owned active membership: set `leftAt = now()`.
   - Update `user_profile`: NULL PII fields; set `deactivatedAt`.
   - Finally, call Auth API to delete user.
4. App signs out user if still signed in and confirms completion.

## Error Cases
- Auth deletion or DB anonymization fails: function returns error; DB changes are idempotent; retry deletes Auth user.

## Test Plan Map
- Owned homes with other active members: function auto-transfers ownership to the earliest active member.
- Homes with no other active members are deactivated and owner membership is closed during deletion.
- Non-owned memberships are closed during deletion.
- Successful deletion anonymizes PII and denies subsequent access via RLS.