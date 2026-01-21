---
Domain: Adr 0001 Mvp Home Scope.Md
Capability: Adr 0001 Mvp Home Scope
Scope: platform
Artifact-Type: adr
Stability: evolving
Status: draft
Version: v1.0
---

# ADR-0001: Home-only MVP Scope and Guardrails

Status: Accepted
Date: 2025-03-11

## Context
Kinly’s first milestone focuses on Home creation/join/transfer/leave with invite codes and OAuth auth. We require fairness, privacy via RLS, and predictable delivery via TDD.

## Decision
- Deliver Home-only MVP with Auth, Homes, Invites, Deep Links, and i18n.
- All writes go through RPCs. No direct table writes from the client.
- Single active home per user for v1.
- RLS isolates data by home and hides inactive homes.
- CI enforces format, lint, tests, build, and migration pairing.

## Consequences
- Clear agent boundaries: UI→BLoC→Repo→Supabase.
- DB team owns migrations and RLS; Planner/Test review.
- Faster review via PR template with Given/When/Then, DoD, artifacts.
- Future extensions (chores/payments/media) will add new agents without breaking the core.
