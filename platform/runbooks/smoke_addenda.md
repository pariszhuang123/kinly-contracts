---
Domain: Runbooks
Capability: Smoke Addenda
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Post-Deploy Smoke — Additional Scenarios

Purpose: Complement `docs/runbooks/smoke.md` with quick checks for invites, leave, and kick.

## Invite Rotate / Revoke
- Preconditions: Owner U1, active Home H.
- Rotate
  1. U1 calls `invites.rotate(H)`; capture returned code C2.
  2. Verify old code C1 is invalid for U3; C2 allows join for U3.
  3. Verify only one active invite exists for H.
- Revoke
  1. U1 calls `invites.revoke(H)`.
  2. Verify `invites.getOrCreate(H)` later returns a new code; old code invalid.

## Leave Home
- Member leaves
  1. U2 (non-owner) leaves H.
  2. Verify U2 `leftAt` set; H remains active (U1 still present).
- Owner leaves as last member
  1. Ensure U1 is sole active member; U1 leaves.
  2. Verify H becomes inactive; any active invite becomes invalid.

## Kick Member
1. U1 (owner) invites/has U2 as active member.
2. U1 kicks U2.
3. Verify U2 `leftAt` set and loses access immediately.
4. Verify kicking owner is forbidden.

## Basic Invariants
- Exactly one active invite per home at any time.
- Only owner can rotate/revoke invites and kick members.
- Non-members cannot read home/members/invite.
