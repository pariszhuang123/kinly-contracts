---
Domain: Adr 0003 Expenses Rpc Only Access.Md
Capability: Adr 0003 Expenses Rpc Only Access
Scope: platform
Artifact-Type: adr
Stability: evolving
Status: draft
Version: v1.0
---

# ADR-0003: Expenses RPC-Only Access Guardrail

Status: Accepted  
Date: 2025-11-21

## Context
- Expenses v1 originally described permissive RLS policies so repositories could query tables directly.
- Chores adopted an RPC-only approach (RLS enabled, no policies) to keep validation, paywall checks, and logging centralized in SECURITY DEFINER functions.
- As Kinly scales, Planner wants a single guardrail that applies to Supabase tables touched by user flows so that:
  - Edge Functions, mobile clients, and admin tooling all share the exact same validation paths.
  - Ownership/membership checks cannot drift between PostgREST filters and stored procedures.
  - Agentic decisions can reference one ADR when deciding whether a new vertical stays RPC-only or exposes table policies.

## Decision
- Expenses tables (`public.expenses`, `public.expense_splits`) keep client access revoked (RLS disabled + `REVOKE ALL` from anon/authenticated). Only trusted service roles can reach the tables directly.
- All reads/writes go through SECURITY DEFINER RPCs (`expenses.create`, `expenses.edit`, `expenses.markSharePaid`, `expenses.cancel`, `expenses.getCurrentOwed`, `expenses.getCreatedByMe`).
- Any automation (Edge Functions, background jobs, migrations) must call these RPCs instead of issuing direct DML unless operating as part of a maintenance window with a documented exception.
- Future domains must explicitly opt out via a new ADR; the default stance is RPC-only access for user-facing data until Planner/Test agree otherwise.

## Consequences
- Centralized validation, logging, and paywall enforcement reduce the risk of inconsistent state.
- RLS tests focus on “no policies installed” instead of duplicating policy permutations.
- Repositories lose the ability to use PostgREST filters for ad-hoc reads; any new data needs an RPC and DTO.
- Service-role code paths (e.g., Edge Functions) are forced to reuse the same guardrails, keeping observability consistent.

## Alternatives Considered
1. **Explicit RLS policies** per table (allowing creator/assignee selects):
   - Pros: PostgREST queries become easier, less RPC work.
   - Cons: Duplicated logic between policies and stored procedures; harder to ensure drafts, debtor-only updates, paywall quotas.
2. **Hybrid** (policies for SELECT, RPCs for writes):
   - Pros: BLoC could read tables directly while still centralizing writes.
   - Cons: Still splits validation logic and increases the testing matrix (policy tests + RPC tests).

## Rollback Plan
- Author `ADR-XXXX-expenses-direct-policies.md`, update the contract, build migrations that add the required `CREATE POLICY` statements, and expand RLS/RPC tests to cover the new selectors.