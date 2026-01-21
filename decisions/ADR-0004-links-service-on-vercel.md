---
Domain: Links
Capability: Links service hosting
Scope: platform
Artifact-Type: adr
Stability: evolving
Status: draft
Version: v1.0
---

# ADR-0004: Host Links Service on Vercel

Status: Draft  
Date: 2026-01-21

## Context
- Kinly Web links and routing behavior are being standardized.
- We need a canonical decision on where the links service is hosted to keep contracts and enforcement aligned.

## Decision (Draft)
- Provision and run the Kinly links service on Vercel, consistent with the web deployment surface.
- Keep routing safety, region gating, and fallback behavior enforced in this environment.

## Consequences
- Edge functions and contract enforcement must target the Vercel-hosted links service.
- Future changes to hosting must be recorded in a new ADR version.

## Open Questions
- Finalize traffic limits, observability, and rollback procedures for Vercel.
- Confirm data residency implications, if any, for this hosting choice.
