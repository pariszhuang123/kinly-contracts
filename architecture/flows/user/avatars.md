---
Domain: Flows
Capability: Avatars
Scope: platform
Artifact-Type: architecture
Stability: evolving
Status: draft
Version: v1.0
---

# Flow — Per-Home Unique Avatars

Contract: v1 (see `docs/contracts/homes_v1.md`)
Diagram: `docs/diagrams/avatar_uniqueness.mmd`

## Rules
- Every active member of a home must have a distinct avatar (per home).
- On first join/create, assign an available avatar automatically.
- Members may change their avatar from a limited palette that excludes avatars in use in that home.
- When joining another home, if the member’s preferred avatar is taken there, assign a different available avatar for that home.

## Preconditions
- Caller is authenticated.
- Home is active; caller becomes or already is an active member (leftAt = NULL).

## Postconditions
- `members.avatar_key` is set and unique among active members in the home.

## Flows

### Auto-assign on join
Given user U joined active home H
When system assigns an available avatar
Then U.members.avatar_key is set to a palette key not used by any other active member of H

### Change avatar (self-service)
Given user U is an active member of H
When U selects an avatar from the available palette (excluding those in use)
Then U.members.avatar_key is updated; uniqueness holds

### Move to another home
Given U is an active member of H1 with avatar A
When U joins H2 where avatar A is already taken
Then system assigns a different available avatar for U in H2

## Errors
- Invalid avatar key (not in catalog) → Invalid.
- Avatar already in use in this home → Conflict.

## Test Plan Map
- Auto-assign gives an available key; uniqueness index enforces.
- Change avatar to available key succeeds; to used key fails.
- Joining second home with collision results in a different key.
