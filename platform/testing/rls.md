---
Domain: Testing
Capability: Rls
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# RLS Test Plan — Home MVP

Scope: Validate Row Level Security for Home, Member, Invite with the permanent-invite model.

Test users
- owner: active member of Home A
- member: active member of Home A (non-owner)
- stranger: not a member of Home A
- leaver: left Home A (leftAt set)

Tables
- home
- member
- invite

Required cases
- Member allowed: active members (owner, member) can read their home, list active members, and fetch current invite.
- Non-member denied: stranger cannot read Home A rows, members, or invite.
- Inactive home denied: once last member leaves (isActive=false), all reads denied to everyone.
- Historical membership visibility: listByHome returns historical memberships only to active members; after deactivation, no access.

Operations matrix (indicative)
- home: SELECT allowed to active members only; INSERT/UPDATE/DELETE via RPCs only.
- member: SELECT allowed to active members of that home; INSERT/UPDATE via RPCs only; DELETE never directly.
- invite: SELECT allowed to active members; INSERT/UPDATE via RPCs only.

Notes
- Enforce “one active membership per user” via unique partial index (userId, leftAt NULL).
- Ensure policies check `isActive` and `revokedAt IS NULL` where applicable.
