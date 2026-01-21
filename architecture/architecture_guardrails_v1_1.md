---
Domain: Architecture Guardrails V1 1.Md
Capability: Architecture Guardrails
Scope: platform
Artifact-Type: architecture
Stability: evolving
Status: draft
Version: v1.1
---

# Architecture Guardrails Contract v1.1 (Kinly)

Status: Proposed  
Owner: Planner (policy), Release (CI enforcement), all agents (compliance)  
Scope: `lib/**` (Flutter app), `tool/**` (linters/checks), CI workflows

This contract supersedes overlapping guidance in `docs/engineering/module_guardrails.md` for dependency/layering rules. That file continues to own the `modules.yml` manifest and kill-switch matrix; defer to it for module ownership specifics.

## Goals
- Keep Kinly maintainable under multi-agent (or solo) development by enforcing:
  - Dependency direction (layering + import boundaries)
  - Modularization (feature boundaries + stable public APIs)
  - Abstraction discipline (DTO containment, DI wiring)
  - Complexity budgets (nesting depth + cyclomatic caps)

Non-goals: Clean Architecture rewrite, banning SDK use, or perfectly classifying every file. Path-based rules are sufficient.

## Composable system boundary
Structural UI composition rules live in `docs/contracts/kinly_composable_system_v1.md`. This guardrail contract focuses on dependency direction and layering; it does not define slots, registries, or surface composition.

## Modules and Layers
- Modules: `lib/core/**` (shared/feature-agnostic) and `lib/features/<feature>/**` (feature modules).
- Layers inside a feature:
  - UI: presentation only; minimal logic.
  - BLoC: coordinates use-cases; state + events.
  - Domain: business rules + types + ports (interfaces).
  - Data: concrete implementations (Supabase/HTTP/SDK/storage/mappers).
- Public API (barrel): `lib/features/<feature>/<feature>.dart` exports cross-module surface. Tests may use `lib/features/<feature>/<feature>_testing.dart`.

### Transitional data layout
`lib/data/repositories/**` remains a shared data surface until per-feature `data/` folders and barrels are created. Enforce the rules below now; plan to migrate to feature-local `data/` as debt paydown.

## Dependency Direction (hard)
1) Core must not depend on features. No `lib/core/**` import from `lib/features/**`.

2) Feature layering (within `lib/features/<f>/...`):
   - UI may import: `features/<f>/bloc/**`, `core/**`, Flutter UI packages, and `features/<f>/domain/types/**` only. UI must not import any `data/**`.
   - BLoC may import: `features/<f>/domain/**`, `core/**`. BLoC must not import `data/**`.
   - Domain may import: `core/domain/**` and pure core helpers (no Flutter/platform), Dart SDK, and whitelisted pure-Dart deps. Domain must not import Flutter, platform/network/DB SDKs, or other features.
   - Data may import: `features/<f>/domain/**`, `core/**`, external SDKs. Data must not be imported by UI/BLoC.

3) Cross-feature imports go through barrels only: `import 'package:kinly/features/<other>/<other>.dart';` (or `<other>_testing.dart` in tests). Deep imports into another feature’s internals are forbidden.

## Modularization
- Other features must not rely on internal paths. Extend the owning feature’s barrel or move truly shared concepts to `core/domain/**`.
- Any symbol used outside a feature must be exported via its barrel.

## Abstraction Discipline
- Ports not concretes: BLoC/Domain depend on interfaces in `domain/ports/**`; implementations live in `data/**`.
- DTOs stay in data: UI/BLoC/Domain consume domain models only; mapping happens in `data/mappers/**` or repository implementations.
- Core stability: Only place feature-agnostic, reusable APIs in `core/**`; treat them as mini-public APIs with doc comments and basic tests.
- DI composition: wiring lives only in `lib/core/di/compose.dart`, `lib/app/router/**` (navigation composition), and `lib/features/<f>/<f>_di.dart`; UI/BLoC must not instantiate data concretes directly.

## Complexity Budgets (hard)
- Nesting depth: max 3 per function. Violations require `// @guardrail-exception: nesting-depth (<reason>)` and Planner sign-off.
- Cyclomatic complexity: keep existing `tool/check_complexity_budget.dart` caps (warn at 11/61; fail at 16/91; BLoC handlers warn 13/fail 18).
- Mandatory extraction when thresholds fail.

## Domain dependency whitelist
- Allowed in Domain: Dart SDK, `meta`, `collection`, `equatable`, `async`, `clock` (pure-Dart helpers). No Flutter/Supabase/HTTP/platform packages.

## Exceptions
- Format: `// @guardrail-exception: <rule> (<reason>)` adjacent to the function or import. Planner must approve. Tests should rarely need exceptions; prefer refactors.

## Enforcement (CI/local)
- Commands:
  - `dart run tool/check_dependency_rules.dart`
  - `dart run tool/check_nesting_depth.dart`
  - `dart run tool/check_complexity_budget.dart`
  - Existing design/i18n/directionality/copy/enums checks per AGENTS/DoD.
- Scope: `lib/**` excluding generated code (`lib/generated/**`, `*.g.dart`, `*.freezed.dart`). Tests may import `<feature>_testing.dart` only.

## Definition of Done (architecture-impacting PRs)
- Updated barrels for any cross-feature surface.
- Updated allowlists/rules if new cross-feature dependencies are introduced.
- Short ADR note if blast radius touches 3+ module roots.
- CI green on all guardrail commands above.