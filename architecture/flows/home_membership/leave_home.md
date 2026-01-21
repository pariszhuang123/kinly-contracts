---
Domain: Flows
Capability: Leave Home
Scope: platform
Artifact-Type: architecture
Stability: evolving
Status: draft
Version: v1.0
---

# Flow — Leave Home

Contract: v1 (see `docs/contracts/homes_v1.md`)
Diagram: `docs/diagrams/leave_home.mmd`

## Preconditions
- Caller is an active member of the home.
- Home is active.

## Postconditions
- Caller’s membership.leftAt is set to now().
- If caller was the last active member, the home becomes inactive:
  - home.isActive = false
  - home.deactivatedAt = now()
  - Any active invite becomes invalid (revokedAt is set or considered invalid due to inactive home).

## Flow (Given/When/Then)
Given user U is an active member of active home H
When U calls homes.leave(H)
Then U’s membership.leftAt is set; and if U was the last active member then H is deactivated

## Steps
1. Authorize: U is an active member of H; H is active.
2. If U is the owner of H:
   - If H has other active members, forbid (must transfer ownership first).
   - Else (U is the sole active member): set membership.leftAt = now(); set home inactive and set deactivatedAt.
3. If U is not the owner: set membership.leftAt = now().
4. If no active members remain after the update: set home inactive and set deactivatedAt.
5. Return OK.

## Error Cases
- Forbidden: caller is not an active member.
- Forbidden: home is inactive.
- Forbidden: owner attempts to leave while other active members exist (must transfer ownership first).

## Test Plan Map
- Member leaves → membership.leftAt set; home remains active if others remain.
- Owner leaves as sole active member → membership.leftAt set; home deactivated.
- Owner leaves while other active members exist → forbidden; transfer required first.
- homes.leave on inactive home → forbidden.
