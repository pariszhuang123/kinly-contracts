---
Domain: Homes
Capability: House rules governance
Scope: platform
Artifact-Type: adr
Stability: evolving
Status: draft
Version: v1.0
---

# ADR-0005: House Rules v1 Owner Authority (No Member Deny, No App Gating)

Status: Draft  
Date: 2026-02-11

## Context
- Kinly introduced House Norms as a non-enforceable, relational layer.
- Customer feedback includes policy-like constraints (smoking, pets, severe
  allergens) that do not fit well in descriptive norms.
- We need a clear governance model that keeps onboarding friction low and avoids
  policy-document bloat.

## Decision
- House Rules v1 is a separate track from House Norms.
- House Rules are owner-authored and owner-published.
- Members have read-only visibility; there is no accept/decline workflow in v1.
- House Rules are concise by contract limits:
  - 1..7 rules per version
  - <=140 chars per rule
  - single-line only
- Rules are authoritative text only in v1:
  - no automatic app gating
  - no reminders/penalties derived from rules
- House Rules are optional:
  - never required for onboarding
  - no setup-pressure UX

## Consequences
- Product keeps fast onboarding while preserving a place for explicit policy
  statements.
- House Norms remains descriptive and non-enforceable.
- Enforcement automation is postponed to later versions if explicitly approved
  via new ADR.

## Alternatives Considered
1. Member signoff required for activation
   - Rejected for v1 due to higher friction and potential deadlock.
2. Immediate app gating from rules
   - Rejected for v1 due to trust and rollout risk.
3. Put all policy constraints into House Norms
   - Rejected because it blurs descriptive vs policy semantics.

## Follow-up
- Add canonical contracts:
  - `contracts/product/kinly/shared/house_rules_v1.md`
  - `contracts/api/kinly/homes/house_rules_api_v1.md`
- Align Home Dynamics and House Norms docs with this split.
