---
Domain: Kinly Web
Capability: Contracts registry
Scope: frontend
Artifact-Type: contract
Stability: evolving
Status: active
Version: v1.3
---

# Contracts Registry - Kinly Web

This document is the **single source of truth** for all active contracts
governing the behavior of Kinly Web.

All routing, deep-linking, app availability (region gating), public content
rendering, and interest capture behavior MUST conform to the active contract
versions listed here.

If behavior changes and this registry is not updated, the change is invalid.

---

## Purpose

The Contracts Registry exists to:

- make system behavior explicit
- prevent silent drift
- preserve user trust over time
- provide a stable reference for enforcement and review

This file does **not** define behavior.\
It declares **which contract versions are in force**.

---

## Contract Rules

1. Every behavioral area MUST be governed by a contract.
2. Contracts are immutable once marked active.
3. Behavioral changes require:
   - a new contract version, and
   - an update to this registry.
4. Implementation MUST match the active contract version exactly.
5. Deprecated contracts remain listed for historical reference.

---

## Active Contracts (v1)

### Links & Routing

Note: Region gating governs **app capability** (install / open), not just join
flows. Preview-only routes remain readable globally, but no install or join
capability may be implied outside supported regions.

| Domain | Capability                    | Contract                                          | Status |
| ------ | ----------------------------- | ------------------------------------------------- | ------ |
| Links  | URI Association               | `links/uri_association_v1.md`                     | Active |
| Links  | Share Links                   | `links/links_share_links_v1_3.md`                 | Active |
| Links  | Deep Links                    | `links/links_deep_links_v1_1.md`                  | Active |
| Links  | Deferred Install Invite       | `links/links_invite_deferred_install_v1_0.md`     | Active |
| Links  | Region Gating                 | `links/links_region_gate_v1_2.md`                 | Active |
| Links  | Fallback Behavior             | `links/links_fallback_v1_1.md`                    | Active |
| Links  | Marketing Surface Namespacing | `links/links_marketing_surface_namespacing_v1.md` | Active |

---

### Public Content

| Domain | Capability         | Contract                         | Status |
| ------ | ------------------ | -------------------------------- | ------ |
| Norms  | Public House Norms | `norms/norms_public_norms_v1.md` | Active |

---

### UI Theme

| Domain | Capability       | Contract                       | Status |
| ------ | ---------------- | ------------------------------ | ------ |
| Theme  | Theme Resolution | `theme/theme_resolution_v1.md` | Active |

---

### Growth

| Domain | Capability                | Contract                                             | Status |
| ------ | ------------------------- | ---------------------------------------------------- | ------ |
| Growth | Interest Capture          | `growth/interest_capture_v1.md`                      | Active |
| Growth | Interest Capture Backend  | `growth/interest_capture_v1_backend.md`              | Active |
| Growth | Marketing Landing         | `growth/marketing_landing_recognition_first_v1_1.md` | Active |
| Growth | Outreach Tracking         | `growth/outreach_tracking_v1_1.md`                   | Active |
| Growth | Outreach Tracking Backend | `../../../api/kinly/growth/outreach_tracking_v1_1.md`| Active |
| Growth | Outreach Polls            | `growth/outreach_polls_v1.md`                        | Active |
| Growth | Outreach Polls Backend    | `../../../api/kinly/growth/outreach_polls_v1.md`     | Active |
| Growth | QR Short Link Resolution  | `growth/qr_short_link_resolution_v1.md`              | Active |

---

## Contract Scope Summary

This registry governs:

- canonical public URLs
- app deep-link invocation rules
- region support and gating logic
- interest capture behavior
- outreach tracking (marketing page analytics)
- fallback and error handling
- public visibility of house norms

This registry does **not** govern:

- mobile app internal behavior
- authenticated web sessions
- marketing site content
- behavioral analytics or user profiling

---

## Versioning Policy

- Patch changes (typos, clarifications)\
  -> update contract file without version bump\
  -> registry unchanged

- Behavioral changes (semantics, rules, allowed flows)\
  -> new contract version file\
  -> registry MUST be updated

Version naming convention:
<domain>_<capability>v<major><minor>.md

Examples:

- `links_region_gate_v1_1.md`
- `norms_public_norms_v2.md`

---

## Deprecation Policy

When a contract is superseded:

- it remains listed below as **Deprecated**
- it must not be referenced by active code
- it is kept for auditability and context

---

## Deprecated Contracts

_None (initial release)._

---

## Enforcement

The following mechanisms rely on this registry:

- Contract Enforcement Execution Agent
- DoD Contract Alignment checklist
- Review authority in `AGENTS.md`

Any discrepancy between implementation and this registry must be resolved before
deployment.

---

## Change Log

| Date       | Change                                             | Approved By |
| ---------- | -------------------------------------------------- | ----------- |
| 2026-02-24 | Activated outreach polls and outreach tracking v1.1 | Planner     |
| 2026-02-22 | Activated QR short-link resolution for `/tools/qr` | Planner     |
| 2026-02-17 | Activated norms and links route updates for /kinly/norms | Planner     |
| 2026-01-29 | Added outreach tracking contracts v1               | Planner     |
| 2026-01-26 | Activated links contracts v1.1/v1.2; encoding tidy | Planner     |
| YYYY-MM-DD | Initial contract registry created                  | Planner     |

---

## Final Note

Contracts are not documentation artifacts. They are **behavioral commitments**.

If the registry is unclear, incomplete, or outdated:

- stop
- clarify
- update the registry first

The registry exists so Kinly Web can grow without losing its intent.

