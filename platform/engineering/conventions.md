---
Domain: Engineering
Capability: Conventions
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Engineering Conventions (MVP)

## Code & Naming
- BLoC: `XxxBloc`, events `XxxRequested/Submitted/Toggled`, states `XxxInitial/Loading/Success/Failure`.
- Repositories: `XxxRepository` with async methods mapping to RPCs.
- DTOs: `XxxDto`, use contracts in `docs/contracts/homes_v1.md`.
- Errors: explicit error enums or sealed classes (e.g., `JoinError`).

## Lint/Format
- Use `flutter format` and `dart analyze` (CI-enforced).
- Prefer `flutter_lints` in `analysis_options.yaml`.

## Structure
- UI → BLoC → Repository → Supabase (RPC/PostgREST).
- No direct Supabase/HTTP in UI/BLoC.

## I18n
- All UI strings via `S.of(context)`.

## Contracts & ADRs
- Pin to v1 contracts; breaking changes require new version + ADR.
