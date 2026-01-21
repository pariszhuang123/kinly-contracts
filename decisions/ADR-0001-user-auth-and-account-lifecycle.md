---
Domain: Adr 0001 User Auth And Account Lifecycle.Md
Capability: Adr 0001 User Auth And Account Lifecycle
Scope: platform
Artifact-Type: adr
Stability: evolving
Status: draft
Version: v1.0
---

# ADR-0001: User Auth (OAuth-only) and Account Lifecycle

Status: Accepted
Date: 2025-11-08

## Context
- MVP supports Google and Apple sign-in only via Supabase OAuth.
- Users can log out or request account deletion.
- Account deletion must remove personally identifying information (PII) and revoke access, while preserving non-identifying historical integrity.

## Decision
- Authentication providers: Google + Apple only. No password or other providers in MVP.
- Logout: client calls `auth.signOut()` and clears local session/cache; app returns to Welcome.
- Account deletion: self-service Edge Function invoked by the user; runs with service role and orchestrates deletion:
  - Resolves home ownership/memberships automatically before deletion:
    - If the user owns a home and other active members exist, the function auto-transfers ownership to a deterministic active member (earliest membership; tiebreaker lowest userId) and proceeds.
    - If the user owns a home and no other active members exist, the home is deactivated and the owner membership is closed.
    - For non-owned active memberships, the membership is closed.
  - Performs DB changes first (including anonymizing `user_profile` with PII removal and setting `deactivatedAt`).
  - Then deletes the Supabase Auth user.
- RLS: deactivated users are denied for all reads/writes.

## Consequences
- Reduced auth surface (no passwords, no resets) simplifies UX and security.
- Requires admin queue/process and an Edge Function.
- Contracts added in `docs/contracts/users_v1.md`; tests must cover RLS and RPC guards.

## Related
- Diagrams: `docs/diagrams/user/auth_providers.md`, `docs/diagrams/user/logout.md`, `docs/diagrams/user/account_deletion.md`.
- Contracts: `docs/contracts/users_v1.md`, `docs/contracts/homes_v1.md`.