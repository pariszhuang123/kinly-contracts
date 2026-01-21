---
Domain: Coordination
Capability: Integration Plan
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Integration Plan

Phase Dependencies
- Auth before Homes join flow
- Invites RPCs before deep link mapping

Critical Integration Points
- UI → BLoC → Repository → Supabase RPCs
- Deep link `/join/:code` → OAuth → `homes.join(code)` → Today

Risk Mitigation
- Forward-only DB migrations; expand/contract for breaking changes
- RLS tests for member allowed, non-member denied, inactive home denied

Success Metrics
- CI green (format, analyze, tests, build)
- RLS/RPC tests pass in Dev before Prod push