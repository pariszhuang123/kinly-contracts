---
Domain: Templates
Capability: Planning Skeleton
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Planning Skeleton — BLoC/Repo (SPARC P Phase)

Use this file to sketch structure before coding. Keep it minimal and focused on contracts and seams.

## Feature
- Title:
- Contract version: v1 (link to `docs/contracts/homes_v1.md`)

## Repository Interface
- Name: `<Feature>Repository`
- Methods (signatures + throws):
  - `Future<Return> methodName(Arg a)` → calls `rpc.name(args)`; errors: `Forbidden`, `NotFound`, `Conflict`
  - ...
- Maps to RPCs:
  - `rpc.name` ↔ `methodName`
- DTOs/contracts used:
  - Input: ...
  - Output: ...

## BLoC
- Events:
  - `EventName(arg)` → description
- States:
  - `Initial | Loading | Success(model) | Failure(error)`
- Transitions (optional):
  - `EventName` + `state` → `nextState` (side effects: repo.methodX)

## Error Mapping
- Repo errors → UI/BLoC failures:
  - `Forbidden` → `JoinError.revoked` (example)
  - `NotFound` → `JoinError.codeUnknown`
  - `Conflict` → `JoinError.alreadyMember`

## Dependencies
- Supabase RPCs: list
- Other repos/services: list

## Out of Scope
- Non‑goals for this slice.
