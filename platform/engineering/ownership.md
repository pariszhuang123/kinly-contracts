---
Domain: Engineering
Capability: Ownership
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Code Ownership (MVP)

Map areas of the repo to review roles.

## Areas (feature-first)
- `lib/features/*/ui/**`: Flutter UI — UI role
- `lib/features/*/bloc/**`: BLoC — BLoC role
- `lib/features/*/repositories/**`: Repositories — BLoC/DB roles
- `lib/core/deep_linking/**`: Deep Linking — Deep Linking + Planner
- `lib/core/**`: Core/shared (config, router, i18n, design system) — relevant owners; Planner for cross-cutting
- `db/**`: Migrations/RLS/RPC — DB role (+ Planner)
- `docs/adr/**`: ADRs — Planner (+ relevant roles)
- `docs/contracts/**`: Contracts — DB + Repositories
- `.github/workflows/**`: CI/workflows — Release role (+ Planner)

## Notes
- Structure is feature-first: `lib/features/{auth,homes,invites,...}/{ui,bloc,repositories,models}`
- Shared code lives under `lib/core/**`. Cross-feature imports should go via core.