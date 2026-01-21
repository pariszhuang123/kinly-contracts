---
Domain: Flows
Capability: Join
Scope: platform
Artifact-Type: architecture
Stability: evolving
Status: draft
Version: v1.0
---

# Flow — Join Home (Pseudocode)

Contract: v1 (see `docs/contracts/homes_v1.md`)
Diagram: `docs/diagrams/join_flow.mmd`

## Preconditions
- User is authenticated.
- User has no active membership.
- Invite code exists, invite.revokedAt IS NULL, and home.isActive = true.

## Postconditions
- User becomes an active member of target home.
- member.leftAt = NULL; home.isActive remains true.

## Flow (Given/When/Then)
Given user U without active membership and valid invite code C
When U calls homes.join(C)
Then insert active membership for U in the invite's home

Steps
1. Fetch invite by code C; error if not found.
2. Validate invite.revokedAt IS NULL; error if revoked.
3. Validate home.isActive = true; error if inactive.
4. Ensure U has no active membership (unique index/guard); error if exists.
5. Insert member row (leftAt = NULL, role = member if not owner).
6. Return success (home, membership summary).

## Error Cases
- NotFound: code unknown.
- Forbidden: invite revoked.
- Forbidden: home inactive.
- Conflict: user already has active membership.

## Test Plan Map
- homes.join(code): happy path creates active membership.
- homes.join with revoked code: forbidden.
- homes.join with inactive home: forbidden.
- homes.join when user already member: constraint violation.
