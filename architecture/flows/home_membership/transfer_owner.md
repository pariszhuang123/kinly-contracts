---
Domain: Flows
Capability: Transfer Owner
Scope: platform
Artifact-Type: architecture
Stability: evolving
Status: draft
Version: v1.0
---

# Flow — Transfer Owner

Contract: v1 (see `docs/contracts/homes_v1.md`)
Diagrams: `docs/diagrams/transfer_owner_flow.mmd`, `docs/diagrams/transfer_owner_sequence.mmd`

## Preconditions
- Caller is the current owner of the home.
- Home is active.
- Target user (`newOwnerId`) is an active member of the same home (leftAt IS NULL).

## Postconditions
- `homes.ownerId` is set to `newOwnerId`.
- Membership rows remain otherwise unchanged (both remain active members).
- Invites remain unaffected.

## Flow (Given/When/Then)
Given owner O and active member N of active home H
When O calls `homes.transferOwner(H, N)`
Then `homes.ownerId` becomes N and H remains active

## Steps
1. Authorize: caller is the current owner of H; H is active.
2. Validate: `newOwnerId` is an active member of H (leftAt IS NULL).
3. Update: set `homes.ownerId = newOwnerId`.
4. Return OK.

## Error Cases
- Forbidden: caller is not the current owner.
- Forbidden: home inactive.
- Not Found/Invalid: `newOwnerId` is not an active member of H.

## Test Plan Map
- Successful transfer: owner → member; ownerId updated.
- Non-owner attempts transfer → forbidden.
- Transfer to non-member/inactive member → invalid/not found.
- Home inactive → forbidden.
