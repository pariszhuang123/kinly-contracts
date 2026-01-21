# agents.md — kinly-contracts

This repository is the canonical home for Kinly contracts, architecture references, decisions (ADRs), and platform process docs.

## Prime Directive
**This repo is source-of-truth for documentation.**  
App repos (kinly-app, kinly-web, future apps) should *consume* these docs but should not re-author them.

## Repo Goals
- Keep contracts discoverable, versioned, and internally consistent
- Enforce stability through lightweight guardrails (headers, paths, links, index)
- Make it easy for humans to find “what is the rule?” quickly

## Where things go (routing rules)

### API Contracts (backend interface)
Path: `contracts/api/kinly/**`
Use for:
- RPC request/response shapes
- auth/permission expectations
- idempotency, error envelopes, invariants

Scope: `backend`  
Artifact-Type: usually `contract`

### Product Rules (behavioral contracts)
Path:
- `contracts/product/kinly/shared/**`
- `contracts/product/kinly/mobile/**`
- `contracts/product/kinly/web/**`

Use for:
- UX behavior rules, gating rules, user flows (non-technical)
- interpretation rules (e.g., “how House Vibe labels are shown”)

Scope:
- shared → `shared`
- mobile/web → `frontend`

### Design System
Path:
- `contracts/design/tokens/kinly/**` (tokens + foundations)
- `contracts/design/copy/kinly/**` (copy standards, voice)
- `contracts/design/reference/kinly/**` (component references)

Scope: usually `shared`

### Architecture
Path: `architecture/**`
Use for:
- module maps, diagrams, system boundaries
- architecture guardrails and invariants (non-API)

Scope: `platform`  
Artifact-Type: `architecture`

### Decisions (ADRs)
Path: `decisions/**`
Use for:
- irreversible/important tradeoffs
- “why we chose X instead of Y”

Scope: `platform`  
Artifact-Type: `adr`

### Platform (process/runbooks)
Path: `platform/**`
Use for:
- CI policies, release policies, doc governance
- agent instructions, checklists

Scope: `platform`  
Artifact-Type: `process` or `guide`

### Quarantine
Path: `_incoming/**`
Use when:
- you cannot classify a file in <10 seconds
- you suspect mixed scope (API + product + copy in one doc)

Files in `_incoming/**` are allowed temporarily but must be moved into a correct bucket before being treated as “canonical”.

## Document format rules (guardrails)
Any markdown doc under:
- `contracts/**`, `architecture/**`, `decisions/**`, `platform/**`
MUST start with YAML front matter:

Required keys:
- Domain
- Capability
- Scope
- Artifact-Type
- Stability
- Status
- Version

Example header:

---
Domain: Homes
Capability: Join Home
Scope: backend
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
---

## Naming rules (keep simple)
- Use lowercase snake_case filenames
- Include version suffix when appropriate, e.g. `homes_v2.md` or `house_vibe_mapping_contract_v1.md`
- Avoid spaces in filenames

## INDEX policy (navigation)
- `INDEX.md` at repo root MUST link to every canonical doc (except `_incoming/**`)
- When adding a doc, you MUST add it to `INDEX.md` in the correct section

## Editing workflow
When making changes:
1) Put the doc in the correct folder
2) Ensure the YAML header is valid
3) Update internal links (relative paths)
4) Add/Update `INDEX.md`
5) Run checks locally:
   - `python tools/contracts_ci/run_checks.py`

## Writing style
- Prefer clear, bounded rules over essays
- Use MUST / MUST NOT / SHOULD / MAY intentionally
- Include examples for request/response shapes and error envelopes where relevant
- Avoid duplicating the same rule in multiple places; link instead

## Versioning guidance
- Use `v1.0` for first stable-ish iteration
- Bump MINOR for additions or clarifications
- Bump MAJOR for breaking semantic changes (meaning changes, not just file moves)
- Deprecate old versions rather than deleting when consumers may still reference them

## When uncertain
If classification is unclear:
- place in `_incoming/kinly/`
- add a short note at top of doc: “needs classification”
- open an issue / TODO to resolve

## Definition of Done for a PR
- CI passes (Contracts CI)
- No orphan docs (INDEX updated)
- No broken internal links
- Header metadata is correct and consistent with folder scope
