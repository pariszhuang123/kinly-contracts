---
Domain: Testing
Capability: Rpc Addenda
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# RPC Test Addenda — Rotate, Kick, Leave, Transfer

Purpose: Extend `docs/testing/rpc.md` with detailed cases for `invites.rotate`, `members.kick`, and nuanced leave/transfer checks.

invites.rotate(homeId)
- Owner happy path: returns new invite with fresh unique code; previous active invite becomes invalid.
- Non-owner: forbidden.
- No current invite: creates one and returns it.
- Concurrency: two concurrent rotates do not produce two active invites (unique partial index holds); one fails cleanly.
- Join with old code: immediately forbidden/not found after rotate.

invites.revoke(homeId)
- Owner: sets `revokedAt`; does not create replacement. `getOrCreate` later will create one.
- Non-owner: forbidden.

members.kick(homeId, userId)
- Owner happy path: target is active non-owner member; sets `leftAt`.
- Non-owner caller: forbidden.
- Target is owner: forbidden.
- Target not active member: not found/no-op.

homes.leave(homeId)
- Member leaves (not last): sets caller `leftAt`; home remains active.
- Owner leaves as last active member: sets `leftAt`, sets `isActive=false`, `deactivatedAt=now()`.
- Owner with other active members: forbidden until transfer.

homes.transferOwner(homeId, newOwnerId)
- Owner to active member: updates `ownerId`.
- Non-owner caller: forbidden.
- Target not active member: invalid/not found.
- Inactive home: forbidden.

Invariants exercised by RPCs
- Exactly one active invite per home.
- A user has at most one active membership across all homes.
