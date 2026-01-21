---
Domain: Testing
Capability: Rpc
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# RPC/Edge Test Plan — Home MVP

Scope: Happy paths and guard paths for Home and Invite RPCs.

Conventions
- Given / When / Then format
- Use isolated users and homes per test

homes.create()
- Given unauthenticated → When call → Then unauthorized
- Given user U → When create() → Then home created, ownerUserId=U, active member row, isActive=true

invites.getOrCreate(homeId)
- Given owner or member → When call → Then returns active invite with code; creates if none
- Given stranger → When call → Then unauthorized/forbidden
- Given inactive home → When call → Then forbidden

invites.revoke(homeId)
- Given owner → When call → Then previous invite.revokedAt set; subsequent getOrCreate returns new code
- Given member (non-owner) → When call → Then forbidden

homes.join(code)
- Given valid active code and user not in any active home → When call → Then user becomes active member
- Given code for inactive home → Then forbidden
- Given revoked code → Then forbidden
- Given user already has an active membership → Then constraint violation

homes.transferOwner(homeId, newOwnerId)
- Given owner and newOwnerId is active member → When call → Then roles updated accordingly
- Given non-owner caller → Then forbidden
- Given newOwnerId not active → Then forbidden

homes.leave(homeId)
- Given active member (not last) → When call → Then member.leftAt set, home remains active
- Given last active member → When call → Then member.leftAt set, home.isActive=false, home.deactivatedAt set

members.listActiveByHome(homeId)
- Given active member → When call → Then returns only leftAt=NULL
- Given stranger → Then forbidden

members.listByHome(homeId)
- Given active member → When call → Then returns historical + active
- Given stranger → Then forbidden