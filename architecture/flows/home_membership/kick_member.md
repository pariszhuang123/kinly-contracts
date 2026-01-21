---
Domain: Flows
Capability: Kick Member
Scope: platform
Artifact-Type: architecture
Stability: evolving
Status: draft
Version: v1.0
---

# Flow — Kick Member

Contract: v1 (see `docs/contracts/homes_v1.md`)
Diagram: `docs/diagrams/kick_member.mmd`

## Preconditions
- Caller is the owner of the home.
- Home is active.
- Target user is an active member of the home and is not the owner.

## Postconditions
- Target member’s membership.leftAt is set to now().
- Home remains active (owner still present).

## Flow (Given/When/Then)
Given owner O of active home H and active member M (M != O)
When O calls members.kick(H, M)
Then M’s membership.leftAt is set and M loses access to H

## Steps
1. Authorize: caller is owner of H; H is active.
2. Validate target: M is an active member of H and M != owner.
3. Update membership for M: set leftAt = now().
4. Return OK.

## Error Cases
- Forbidden: caller is not the owner.
- Forbidden: home inactive.
- Not Found/No-op: target is not an active member of H.
- Forbidden: target is the owner.

## Test Plan Map
- Owner kicks member → membership.leftAt set.
- Non-owner tries to kick → forbidden.
- Attempt to kick owner → forbidden.
- Attempt to kick non-member/inactive member → not found/no-op.