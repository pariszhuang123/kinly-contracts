---
Domain: Testing
Capability: Conventions
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Testing Conventions (MVP)

## Layers
- Unit: Repositories and BLoC.
- Widget: ≥1 per screen (Welcome, Create, Join, Today).
- Integration: RPC edges and guards.

## Naming
- Encode intent: `homes_join_validCode_addsMember_whenUserInactive`.
- Group by feature/flow.

## Traceability
- Update Traceability Map in your spec/pseudocode for each Given/When/Then.

## RLS/RPC
- Use `docs/testing/rls.md` and `docs/testing/rpc.md` as sources for cases.
