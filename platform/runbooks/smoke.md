---
Domain: Runbooks
Capability: Smoke
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Post‑Deploy Smoke — Home MVP

Scope: Quick verification of critical paths after deploy.

## 1) Join Flow (Happy Path)
- Preconditions: Two test users (U1 owner, U2 joiner); Home H active; active invite code C.
- Steps
  1. U2 opens app (authenticated) and enters code C.
  2. Verify join succeeds within acceptable latency.
  3. Verify U2 appears in active members of H.
- Verify
  - App shows success and navigates to Today/Hub.
  - DB: `member.leftAt IS NULL` for U2 in H.
  - Invite remains active (not revoked), home still active.

## 2) Join Guards
- Revoked code: revoke invite; attempt join → expect Forbidden.
- Inactive home: deactivate by leaving last member; attempt join → expect Forbidden.
- Existing active membership: U2 already in home; attempt join → expect Conflict.

## 3) Ownership Transfer
- Owner transfers to another active member; verify roles updated.

## 4) Performance Note
- Goal: join p95 ≤ 400 ms (end‑to‑end client observable).
- Capture: record timestamps in client logs (start enter code → success), sample 20+ attempts if feasible.
- If exceeded: note in PR “Continue” and create follow‑up issue.

## 5) Links & Evidence
- Attach screenshots/GIFs of happy paths.
- Link CI run and any logs.
