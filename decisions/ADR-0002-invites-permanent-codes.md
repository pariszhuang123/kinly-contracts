---
Domain: Adr 0002 Invites Permanent Codes.Md
Capability: Adr 0002 Invites Permanent Codes
Scope: platform
Artifact-Type: adr
Stability: evolving
Status: draft
Version: v1.0
---

# ADR-0002: Permanent Invites (Until Revoked)

Status: Accepted
Date: 2025-11-03

## Context
- Early drafts considered short‑lived codes (TTL, max uses).
- MVP prioritizes simplicity, low ceremony for households, and fast join (p95 ≤ 400 ms).

## Decision
- Invites are permanent and single-code per home.
- An invite is valid iff the home is active and the invite is not revoked.
- Owners can rotate by revoking; `invites.getOrCreate` issues a new active code when none exists.

## Consequences
- Simpler UX and fewer edge cases (no TTL/maxUses handling in clients).
- Security relies on: easy rotation, home deactivation on last member leaving, and RLS around join.
- DB: unique `code`, FK to `homeId`, and guard checks in RPCs.

## Alternatives Considered
- TTL + maxUses: more control but adds storage, timers, and client state.
- One-time links: higher friction and more state to track.

## Rollback Plan
- Introduce `invites_v2` with TTL/maxUses and deprecate v1; document in a new ADR.
