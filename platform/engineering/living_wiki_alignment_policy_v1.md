---
Domain: platform
Capability: living wiki alignment policy
Scope: platform
Artifact-Type: process
Stability: evolving
Status: active
Version: v1.0
Canonical-Id: living_wiki_alignment_policy
See-Also: contracts/product/kinly/web/contracts_registry.md
---

# Living Wiki Alignment Policy

## Purpose

Define how the generated living wiki and alignment checks enforce consistency
across the canonical contract set.

## Canonical Rule

Canonical docs live under:

- `contracts/**`
- `architecture/**`
- `decisions/**`
- `platform/**`

Generated wiki outputs live under:

- `wiki/**`

The wiki is derived. It MUST be regenerated from canonical docs and MUST NOT be
edited manually.

## Required Metadata

All in-scope markdown docs MUST keep the existing required header keys.

Docs MAY additionally declare:

- `Canonical-Id`
- `Relates-To`
- `Depends-On`
- `Supersedes`
- `Superseded-By`
- `Implements`
- `Implemented-By`
- `See-Also`

Rules:

- `Canonical-Id` SHOULD be lowercase snake_case.
- Relationship values MUST be lowercase snake_case Canonical-Ids or
  repo-relative markdown paths.
- Docs that intentionally describe the same capability across versions SHOULD
  share a `Canonical-Id`.

## Deterministic Enforcement

The first-pass alignment checks are deterministic and MUST NOT rely on opaque AI
judgment.

The guardrails currently enforce:

- explicit relationship targets resolve to a real doc path or known
  `Canonical-Id`
- active docs MUST NOT depend on deprecated docs
- docs with `Superseded-By` MUST be marked `deprecated`
- multiple active docs sharing one explicit `Canonical-Id` MUST declare
  supersession metadata
- generated wiki coverage MUST include every canonical doc on its domain and
  capability pages

The guardrails SHOULD expand over time to include stronger invariant checks
between API, product, design, architecture, and ADR docs.

## Generated Outputs

The generated wiki MUST include:

- `wiki/home.md`
- `wiki/domains/*.md`
- `wiki/capabilities/*.md`
- `wiki/reports/alignment_report.md`
- `wiki/reports/change_digest.md`

If generation changes any derived file, the working tree is stale and the checks
MUST fail until regenerated outputs are committed.

## Workflow

1. Edit canonical docs.
2. Update relationship metadata where applicable.
3. Run `python tools/contracts_ci/run_checks.py`.
4. Review `wiki/reports/alignment_report.md`.
5. Resolve contradictions in canonical docs, not in the generated wiki.
6. Commit canonical and regenerated files together.
