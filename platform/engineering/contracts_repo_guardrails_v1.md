---
Domain: Engineering
Capability: Contracts Repo Guardrails
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Contract — Implement kinly-contracts Guardrails Suite v1.0

## Purpose
`kinly-contracts` MUST be self-validating with a minimal, fast `check_all` suite that enforces:
- required front matter headers
- allowed folder/path structure
- internal relative link integrity
- navigation/index integrity

The guardrails MUST run locally and in CI.

## Non-Goals
- No Flutter/Dart toolchain dependencies
- No Supabase CLI, Docker, database, or edge function execution
- No file mutation in CI (checks only; no auto-fix in CI)
- No external network calls required for checks

## Repository Roots In-Scope
Guardrails apply to markdown files under:
- `contracts/**`
- `architecture/**`
- `decisions/**`
- `platform/**`

Exempt:
- `**/_incoming/**` (quarantine: no checks except basic file existence)
- root `README.md` (header optional)
- any `**/*.png|jpg|jpeg|gif|svg|pdf` (not in scope)

## Deliverables
Codex MUST create these files:

### A) Runner + checks
- `tools/contracts_ci/run_checks.py`
- `tools/contracts_ci/check_doc_headers.py`
- `tools/contracts_ci/check_contract_paths.py`
- `tools/contracts_ci/check_links.py`
- `tools/contracts_ci/check_index.py`
- `tools/contracts_ci/README.md`

### B) CI workflow
- `.github/workflows/contracts_ci.yml`

### C) Repo navigation
- `INDEX.md` at repo root (if not already present)

## Check 1 — Doc Header Enforcement (Required)
All markdown docs under in-scope roots MUST start with YAML front matter (`--- ... ---`) containing keys:

Required keys:
- `Domain`
- `Capability`
- `Scope`
- `Artifact-Type`
- `Stability`
- `Status`
- `Version`

Value constraints:

`Scope` ∈ { `backend`, `frontend`, `shared`, `platform` }

`Artifact-Type` ∈ { `contract`, `guide`, `reference`, `architecture`, `adr`, `process` }

`Stability` ∈ { `stable`, `evolving`, `ephemeral` }

`Status` ∈ { `draft`, `active`, `deprecated` }

`Version` format MUST be:
- `vMAJOR.MINOR` or `vMAJOR.MINOR.PATCH`
Examples: `v1.0`, `v1.2.3`

Header checker MUST:
- ignore files under `_incoming/**`
- ignore root `README.md` (no header required)
- produce actionable errors listing:
  - file path
  - missing keys OR invalid values

## Check 2 — Contract Path Integrity (Required)
The following top-level paths are allowed:

- `contracts/api/kinly/**`
- `contracts/product/kinly/shared/**`
- `contracts/product/kinly/mobile/**`
- `contracts/product/kinly/web/**`
- `contracts/design/tokens/kinly/**`
- `contracts/design/copy/kinly/**`
- `contracts/design/reference/kinly/**`
- `architecture/**`
- `decisions/**`
- `platform/**`
- `_incoming/**`

Rules:
- Any markdown file under `contracts/**` outside the allowed contracts subpaths MUST fail.
- Any “mixed scope” doc discovered MUST be placed under `_incoming/` manually (guardrails will fail otherwise).

Checker output MUST list invalid files and the allowed roots.

## Check 3 — Internal Relative Links (Best-effort, Required)
Scan in-scope markdown files and validate relative links:
- Must validate `](../path/to/file.md)` and `](path/to/file.md)`
- Ignore:
  - `http://` and `https://`
  - `mailto:`
  - `#anchor` links
  - image links (extensions: png/jpg/jpeg/gif/svg/webp)
  - links containing query strings or fragments on external URLs

For relative links with fragments: `foo.md#bar`
- Verify `foo.md` exists (do NOT validate anchor existence).

Error format MUST include:
- source file path
- the exact broken target
- line number if feasible

## Check 4 — Index / Navigation Integrity (Required)
A repo root `INDEX.md` MUST exist.

Index policy:
- Every markdown file under in-scope roots (excluding `_incoming/**`) MUST be referenced somewhere in `INDEX.md`
- Reference means the file path appears in a markdown link target, e.g. `(contracts/api/kinly/.../x.md)`

`check_index.py` MUST:
- build the set of eligible markdown files
- parse `INDEX.md` for link targets
- fail on any “orphaned” doc not referenced
- ignore:
  - root `README.md`
  - `_incoming/**`
  - files named `README.md` inside folders (these may be omitted from index)

## Runner Requirements (`run_checks.py`)
Runner MUST:
- run checks in this order:
  1. doc headers
  2. path integrity
  3. internal links
  4. index integrity
- print grouped output with a summary:
  - number of files scanned
  - failures per check
- exit code 1 if any check fails; 0 otherwise

Local usage:
- `python tools/contracts_ci/run_checks.py`

## CI Workflow Requirements
`.github/workflows/contracts_ci.yml` MUST:
- run on `push`/`pull_request` to `main` + `workflow_dispatch`
- use Python 3.12 (or 3.11 if needed)
- run only: `python tools/contracts_ci/run_checks.py`
- no additional toolchains or services

## Acceptance Criteria
- Adding a markdown doc without front matter fails CI with clear error
- Moving a doc to an invalid path fails CI
- Adding a broken relative link fails CI
- Adding a doc that is not linked from `INDEX.md` fails CI
- CI runtime < 1 minute on typical PR

## Implementation Notes
- Python standard library only preferred
- Use `pathlib` and `re`
- If line numbers are not feasible for link errors, omit them; correctness > niceness