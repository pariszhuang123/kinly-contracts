---
Domain: Engineering
Capability: Module Guardrails
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Module Guardrails Checklist

This checklist turns `modules.yml` into enforceable boundaries and kill-switch safety. Wire these into CI and local pre-push. Dependency/layering rules now live in `docs/engineering/architecture_guardrails_v1_1.md`; treat this file as the manifest/kill-switch companion to that contract.

## Manifest
- Validate `modules.yml` schema (required fields, unknown modules, duplicate table/RPC names).
- Fail if a module listed in code (folder under `lib/features` or `lib/core`) is missing from `modules.yml`, or vice versa.

## Import boundaries (Flutter/Dart)
- Enforce cross-module imports go only through each module’s `public_api.dart`; forbid deep imports into another module’s internals.
- Allowlist module-level dependencies from `depends_on` in `modules.yml`; block any other cross-module import edges.
- Shared enums/DTOs live in the owning module or `lib/core/**/enums` per AGENTS; lint that no other location defines enums.

## RPC ownership
- Static check Supabase RPCs: owner RPCs touch only owned tables + `core`; orchestration RPCs call only owner RPCs (no direct writes to other modules).
- Generate an RPC allowlist per module from `modules.yml` and fail if client code calls an out-of-allowlist RPC.
- Validate versioning: RPC names ending `_v1`/`_v2` require a `removal_after` metadata entry and telemetry gate before removal.

## Data ownership
- One owner per table: match tables to modules from `modules.yml`.
- Cross-module foreign keys must be nullable with `ON DELETE SET NULL` (or soft refs without FK); fail on hard required FKs across modules.
- Flag unique constraints spanning multiple modules’ tables/columns.

## Killability and flags
- For each killable module, run a test shard with `kill_switch_flag` off; app should boot, routes/tiles hidden, repos return FeatureDisabled instead of throwing.
- For plan-gated modules, run tests with missing entitlements and ensure guards stop RPCs/UI.
- Validate navigation: no routes from other modules link to a disabled module when its flag is off.

## UI/Accessibility/I18n (existing guardrails to keep)
- `dart format`, `dart analyze`, `flutter test`.
- `dart run tool/check_i18n.dart`, `dart run tool/check_directionality.dart`, `dart run tool/check_enums.dart`, `dart run tool/check_design_system.dart`.
- `bash tool/check_colors.sh` (aggregated color guard + unused color token check).
- No raw Material/FAB/progress; only Kinly primitives. Loaders via `kinly_loader.dart`; strings via `S.of(context)`.

## Telemetry & logging
- Lint against `print`/`debugPrint`; require DI logger.
- Emit module + RPC names for calls to catch cross-module leaks in dev/test.

## Automation hooks
- Add a `tool/check_modules.dart` (or similar) that:
  - Parses `modules.yml`.
  - Builds import/RPC/table allowlists.
  - Fails on violations above.
- Add a `tool/test_matrix.dart` target to rerun minimal suites with each module flag off (can be smoke tests to start).