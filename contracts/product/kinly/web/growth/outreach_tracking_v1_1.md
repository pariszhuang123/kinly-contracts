---
Domain: product
Capability: outreach_tracking
Scope: frontend
Artifact-Type: contract
Stability: stable
Status: active
Version: v1.1
Audience: public
Last updated: 2026-02-24
---

# Contract - Kinly Outreach Tracking (Frontend, UTM-aligned) v1.1

## Purpose
Define privacy-safe outreach tracking for Kinly web pages and polls using append-only event logs.

This contract governs frontend event semantics only. Backend validation, source resolution, and rate limiting are defined in `contracts/api/kinly/growth/outreach_tracking_v1_1.md`.

## Canonical Ingestion Path
- Frontend MUST log events via `public.outreach_log_event`.
- Frontend MUST NOT write outreach tables directly.
- Frontend MUST NOT canonicalize `utm_source`; backend resolves aliases.

## UTM Rules
- `utm_campaign`, `utm_medium`, `utm_source` MUST be sent on every event.
- Missing or blank values MUST be sent as `"unknown"`.
- Frontend SHOULD lowercase `utm_medium` and `utm_source`.

## Allowed Events
The only allowed event values are:
- `page_view`
- `poll_page_view`
- `poll_vote`
- `poll_results_view`
- `cta_click`

## Event Semantics

### `page_view`
- Purpose: page visit proxy for non-poll pages and short-link resolver logging.
- MUST be emitted at most once per `session_id + page_key + tab session` when emitted client-side.

### `poll_page_view`
- Purpose: poll page load with client session semantics for funnel counts.
- MUST be emitted at most once per `session_id + page_key + tab session`.

### `poll_vote`
- Purpose: successful vote submission.
- SHOULD be emitted server-side by poll vote RPC.
- Frontend MUST NOT emit duplicate `poll_vote` for the same successful submission if backend already emits.

### `poll_results_view`
- Purpose: results render after vote.
- MUST be emitted at most once per `session_id + page_key + tab session`.

### `cta_click`
- Purpose: outbound install intent.
- Allowed `store`: `ios_app_store` | `google_play` | `web` | `unknown`.

## Poll Short-Code Handoff
- Poll vote attribution trust boundary is `short_code`.
- Poll pages reached via short links MUST receive `k_sc=<short_code>` in URL query.
- Frontend vote submission MUST send `k_sc` (as RPC `p_short_code`) rather than trusting mutable URL UTMs.

## Required Event Payload Fields
- `event`
- `app_key` (MUST be `kinly-web`)
- `page_key`
- `utm_campaign`
- `utm_medium`
- `utm_source`
- `session_id`

Optional:
- `store` (required for `cta_click`)
- `country`
- `ui_locale`
- `client_event_id`

## Session Identifier
- MUST match `^anon_[A-Za-z0-9_-]{16,32}$`.
- MUST be stored in `localStorage` key `kinly.outreach.session`.
- SHOULD rotate after 30 days.
- MUST NOT be tied to identity.

## Privacy Rules
Frontend tracking MUST NOT collect:
- names, email, phone
- IP addresses
- auth identifiers
- fingerprinting identifiers
- cross-surface identity joins

## Failure Handling
Tracking failures MUST NOT block user flows:
- pages still render
- vote and CTA actions still work
- no user-facing technical errors for tracking failures

## Non-goals
- install attribution
- retargeting
- per-user profiling
- cross-surface identity correlation

## Version History
| Version | Change |
| --- | --- |
| v1.1 | Added poll event taxonomy (`poll_page_view`, `poll_vote`, `poll_results_view`) and `k_sc` handoff semantics. |
| v1.0 | Initial outreach tracking contract. |
