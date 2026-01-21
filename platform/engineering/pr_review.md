---
Domain: Engineering
Capability: Pr Review
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# PR & Review Policy (MVP)

## Requirements
- Use `.github/pull_request_template.md`.
- Link Spec, Pseudocode, Planning Skeleton, Contract version.
- Add CI run URL; Reflect/Continue sections are mandatory.
- Follow feature-first layout (`lib/features/...`); avoid cross-feature changes unless necessary.
- Add appropriate labels (feature, area, type, risk).

## Reviews
- ≥1 reviewer; add role reviewers per touched area:
  - `db/**` — DB + Planner
  - `lib/core/deep_linking/**` — Deep Linking + Planner
  - `.github/workflows/**` — Release + Planner
  - `lib/features/*/repositories/**` (contracts/DTOs) — BLoC + DB
  - `docs/contracts/**` — DB + Repositories
  - `docs/adr/**` — Planner (+ relevant roles)
- Keep PRs small and focused; prefer stacked PRs for larger work.

## Merge
- CI green (format, analyze, test, build).
- Artifacts/screens if applicable.

## Guardrails (must pass review)
- No direct Supabase/HTTP in UI or BLoC.
- All UI strings via `S.of(context)`; no hard-coded strings.
- Cross-feature imports only via `lib/core/**`.
- Contracts/DTOs are versioned and referenced in PR.
- No public endpoints for invites/joins; writes only via approved RPCs.

## Size & Scope
- Aim <400 LOC changed (excludes generated/lock files).
- Single concern per PR (feature, fix, or infra).

## Evidence & Tests
- Screenshots/GIFs for user-facing changes.
- Tests match DoD:
  - Widget tests for affected screens.
  - BLoC/repository unit tests for logic touched.
  - DB changes: RLS + RPC tests and migrations included.

## Special Cases
- Schema/migrations: require DB + Planner approval; include RLS policies and tests.
- Deep linking: require Deep Linking + Planner approval.
- CI/Infra: require Release + Planner approval.

## Trunk-Based + TDD
- Work in short-lived branches; open PRs early and small.
- Practice TDD for business logic (BLoC and repositories) and add widget tests for visible UI changes.
- Incomplete features land behind flags or remain unreferenced until complete.

## Coverage Gates
- CI enforces coverage:
  - Overall minimum: 95% (excludes generated and boilerplate).
  - Strict minimum: 100% for `lib/features/*/bloc/**` and `lib/features/*/repositories/**`.
- Exclusions: `**/*.g.dart`, `**/*.freezed.dart`, `lib/l10n/**`, `**/generated_plugin_registrant.dart`, `lib/core/design_system/**`.