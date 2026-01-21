---
Domain: Testing
Capability: Rls Addenda
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# RLS Test Addenda — Owner/Member and Invites

Purpose: Complement `docs/testing/rls.md` with concrete predicates and invariants used by policies and RPCs.

Owner vs Member checks
- Owner is derived: `auth.uid() = homes.owner_id`.
- Active member: `EXISTS(SELECT 1 FROM membership m WHERE m.home_id = homes.id AND m.user_id = auth.uid() AND m.is_current = TRUE)`.

Policy expectations (examples)
- homes (SELECT): allowed if home is active AND caller is an active member.
- homes (UPDATE owner_id): no direct updates; only via `homes.transferOwner` RPC (function enforces owner and target active checks).
- membership (SELECT): allowed to active members of that home.
- membership (UPDATE valid_to / is_current): no direct updates; only via `homes.leave` (self) or `members.kick` (owner-only).
- invite (SELECT): allowed to active members; validation of codes requires home active AND `revoked_at IS NULL`.
- invite (INSERT/UPDATE): no direct writes; only via `invites.getOrCreate`, `invites.revoke`, `invites.rotate` (owner-only for revoke/rotate).

Invariants to verify via constraints and tests
- Exactly one active invite per home:
  - Partial unique index on `(home_id)` WHERE `revoked_at IS NULL`.
- One active membership per user across homes (unique partial index on `(user_id)` WHERE `is_current`).
- Owner cannot leave while other active members exist (transfer first).