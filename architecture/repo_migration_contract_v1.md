---
Domain: Repo Migration Contract V1.Md
Capability: Repo Migration Contract
Scope: platform
Artifact-Type: architecture
Stability: evolving
Status: draft
Version: v1.0
---

# Repo Migration Contract v1

Status: Proposed  
Owner: Planner (policy), Release (CI enforcement), Codex + Humans (execution)  
Scope: Flutter app (`lib/**`), DI composition, import graph tooling  
Breaking change: Yes (architectural)

## 1. Goal
Migrate `lib/data/repositories/**` into owning features to enforce:
- Clear repository ownership
- Domain ports per feature
- Feature-local data implementations (Supabase/SDK)
- Cross-feature access only via feature barrels
- Feature-owned DI wiring
- Enforcement via import-graph tooling

## 2. Non-Goals
- Not a Clean Architecture rewrite
- Not forcing all shared logic into `core/**`
- Not changing runtime behavior/APIs unless required by ownership
- Not optimizing performance/queries as part of migration

## 3. Target Feature Structure
```
lib/features/<feature>/
  domain/
    ports/<name>_repository.dart   # interfaces only
    models/                        # optional, pure domain
    usecases/                      # optional
  data/
    supabase/<name>_repository_supabase.dart
    mappers/, dtos/                # optional
    <feature>_data.dart            # optional DI barrel only
  ui/
  bloc/
  <feature>.dart                   # feature barrel (domain/public API)
  <feature>_di.dart                # feature DI installer
```
Barrel rules:
- `<feature>.dart` exports domain/public API only.
- `data/**` is private to the feature.
- `<feature>_data.dart` (if present) is DI-only, never used by UI/BLoC.

## 4. Repository Ownership Mapping (mandatory)
Create `tool/migration/repo_ownership_map.yaml` before moving code. Rules:
- If `modules.yml` assigns a feature, that feature owns it.
- If primarily used by one feature’s BLoCs/screens, that feature owns it.
- If it is a platform adapter (auth/session/cache/logging/http), move to `core/**`.
- If truly shared domain capability, use `core/domain/ports/**` + `core/data/**`.
- If ambiguous, mark BLOCKED and resolve before migration continues.

## 5. Dependency Direction (hard)
Within a feature:
- UI/BLoC may import feature barrel + approved `core/**`.
- Domain may import `core/domain/**` only (no SDKs/data).
- Data may import SDKs, its own feature domain, approved `core/**`; data must not be imported by UI/BLoC.

Cross-feature:
- Allowed: `import 'package:kinly/features/<f>/<f>.dart';`
- Forbidden: deep imports into `features/<f>/data/**` or internals.

Global bans after migration:
- No imports from `lib/data/repositories/**`.
- No imports into `core/**` from `features/*/data/**`.

## 6. Execution Plan
Phase A — Preparation
- Create `tool/migration/repo_ownership_map.yaml`.
- Ensure `modules.yml` lists all features and barrel paths.

Phase B — Per-repository migration (repeatable):
1) Move interface to `lib/features/<feature>/domain/ports/<name>_repository.dart` (no SDK imports).
2) Move concrete to `lib/features/<feature>/data/supabase/<name>_repository_supabase.dart` (`<Name>RepositorySupabase implements <Name>Repository`).
3) Update feature barrel to export the port (not the concrete).
4) Update callers: replace `lib/data/repositories/...` with feature barrel; use interface type.
5) Move DI registration to `lib/features/<feature>/<feature>_di.dart`.
6) Wire installers in `compose.dart` (or equivalent).
7) Remove legacy file (temporary re-exports discouraged; must be removed before Phase C).

Phase C — Kill shared folder
- Delete `lib/data/repositories/**`.
- CI must fail if the folder exists or is imported.

## 7. Handling “Shared” Repos
- Preferred: shared domain service → `core/domain/ports/**` + `core/data/**`; features depend on the port only.
- Acceptable: one owning feature provides capability; others import only the feature barrel.
- Forbidden: new “shared data” folder.

## 8. DI & Composition
- Each feature owns its installer (`<feature>_di.dart`).
- App composition root wires installers only.
- Composition root must not import feature `data/**` directly.

## 9. Import Graph Checker Updates (required)
- Ban imports containing `data/repositories/`.
- Error if a file outside `features/<X>/` imports `features/<X>/data/**`.
- Cross-feature imports must use `features/<X>/<X>.dart`; error on deeper paths.
- `core/**` may import feature barrels only; never feature data.

## 10. Definition of Done
- `lib/data/repositories/**` removed and forbidden by CI.
- UI/BLoC depend only on feature barrels + ports.
- All concrete repos live in `features/<feature>/data/**`.
- DI registrations live in feature installers; composition root wires them.
- Import checker rules added and passing.
- `repo_ownership_map.yaml` committed and complete.

## 11. Success Criteria
- Repository ownership obvious from path.
- No feature can reach into another feature’s data layer.
- Swapping Supabase impls does not affect UI/BLoC imports.
- Import graph violations fail CI deterministically.
- Codex agents can migrate features independently without collisions.