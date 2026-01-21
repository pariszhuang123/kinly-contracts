---
Domain: Flows
Capability: Invite Rotation
Scope: platform
Artifact-Type: architecture
Stability: evolving
Status: draft
Version: v1.0
---

# Flow — Invite Rotation (Revoke and Reissue)

Contract: v1 (see `docs/contracts/homes_v1.md`)
Diagram: `docs/diagrams/invite_rotation.mmd`

## Primary Flow: invites.rotate (owner wants a fresh code now)

### Preconditions
- Caller is the home owner.
- Home is active.

### Postconditions
- Current active invite (if any) is revoked (old code invalid).
- A new invite row is created with a fresh unique code.
- The new active invite is returned to the client for sharing.

### Flow (Given/When/Then)
Given owner O of active home H (with or without an active invite I)
When O calls invites.rotate(H)
Then any existing active invite is revoked and a new active invite I2 is created and returned

### Steps
1. Authorize: caller is owner of H and H is active.
2. Revoke current active invite (if any): `revokedAt = now()`.
3. Insert a new invite with a fresh unique `code` for H.
4. Return the new invite (including `code`).

### Error Cases
- Forbidden: caller is not owner or not a member.
- Forbidden: home inactive.
- Concurrency: unique partial index ensures at most one active invite; rotate runs in a transaction.

### Test Plan Map
- invites.rotate by owner → returns new code; old code invalid.
- invites.rotate by non-owner → forbidden.
- invites.rotate when no active invite → creates and returns one.
- homes.join with old code after rotate → not found/forbidden.

## Secondary Flow: invites.revoke (disable without replacement)

Use when the owner wants to invalidate the current code and not immediately issue a new one.

### Steps
1. Authorize: caller is owner of H and H is active.
2. Set `revokedAt = now()` on the current active invite.
3. Return OK (no new invite is created).

### Follow-up
- A later call to `invites.getOrCreate(H)` will create a new invite if none is active.

### Error Cases
- Forbidden: caller is not owner or not a member.
- Forbidden: home inactive.