---
Domain: Engineering
Capability: Branching Releases
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Branching & Releases (MVP)

## Branching
- Trunk-based development.
- Short-lived branches: `feature/<slug>`.
- Small PRs (< ~400 LOC), use the PR template.

## Reviews
- At least 1 reviewer; role-based reviewers for DB/infra changes.
- Fill Reflect/Continue sections.

## Versioning & Tags
- App versions tagged `vX.Y.Z`.
- Android: bump `versionCode`; iOS: bump build number.

## Release Checklist
- CI green: format, analyze, test, build.
- Post-deploy smoke: `docs/runbooks/smoke.md`.
- Link ADRs and contract version in release notes.
