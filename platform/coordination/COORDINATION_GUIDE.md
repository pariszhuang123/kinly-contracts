---
Domain: Coordination
Capability: Coordination Guide
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Coordination Guide

Purpose
- Share discoveries (parameters, solutions) and failures to prevent repetition.
- Maintain lightweight, reviewable coordination across roles without changing ADRs/contracts.

Directory
- memory_bank/: persistent knowledge (parameters, failures, dependencies)
- orchestration/: agent assignments, progress tracker, integration plan
- subtasks/: short-lived task breakdowns per feature/bug

Protocols
- Before work: check `orchestration/agent_assignments.md`, `orchestration/progress_tracker.md`, `orchestration/integration_plan.md`.
- During work: update `progress_tracker.md` on significant steps; log new parameters/failures immediately in memory_bank.
- After work: mark status complete; if knowledge stabilized, promote to ADR/contract changelog.

Persona and Tone
- Read: `docs/agents/paris.md` (full persona)
- Quick reference: `coordination/memory_bank/persona_paris.md`

Progress Entry Format
- [Timestamp] Agent: [ID]
- Task: [brief]
- Status: [🟢/🟡/🔴/⚪/🔵]
- Details: [done/discovered]
- Next: [explicit next step]

Ownership
- Planner: orchestration files
- Test: test_failures.md
- Release: calibration_values.md (CI/build)
- DB: memory items for RLS/RPCs
- Docs: guide stewardship

Guardrails
- Do not override ADRs/contracts. Promote stable items via ADR or contracts changelog.
- Atomic updates; small diffs preferred.