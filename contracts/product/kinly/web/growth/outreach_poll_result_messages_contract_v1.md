---
Domain: product
Capability: outreach_poll_result_messages
Scope: frontend
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
Audience: internal
Last updated: 2026-03-03
---

# Contract - Outreach Poll Result Messages (Web) v1.0

## Purpose
Define post-vote explanation text and CTA label resolution for outreach polls so users see option-specific guidance that acknowledges their context and improves CTA click-through.

This contract governs frontend behavior only.
Backend schema, constraints, and access rules are defined in `../../../../api/kinly/growth/outreach_poll_result_messages_v1.md`.

## Goals and Non-goals
Goals:
- tailor explanation text and CTA label by selected poll option
- support optional source/campaign overrides
- keep CTA destination stable while preserving attribution on navigation
- improve conversion by using outcome-oriented CTA language

Non-goals:
- store platform detection logic
- redirect engine implementation
- full onboarding redesign
- long-form educational content

## Definitions
- Poll: active poll context from poll contracts
- Option: selected option in poll context
- Explanation text: short post-vote interpretation copy shown under results chart
- CTA label: primary action button text shown below explanation text
- Resolution tier: `EXACT | SOURCE_ONLY | GLOBAL_DEFAULT | FALLBACK`

## Message Resolution Algorithm (MUST)
Given:
- `poll_id`
- `selected_option_id`
- request context: `source_id_resolved`, `utm_campaign`

The frontend MUST resolve one active row using ordered fallback:

1. `EXACT`
   - `poll_id = ?`
   - `option_id = ?`
   - `source_id_resolved = ?`
   - `utm_campaign = ?`
   - `active = true`
2. `SOURCE_ONLY`
   - `poll_id = ?`
   - `option_id = ?`
   - `source_id_resolved = ?`
   - `utm_campaign IS NULL`
   - `active = true`
3. `GLOBAL_DEFAULT`
   - `poll_id = ?`
   - `option_id = ?`
   - `source_id_resolved IS NULL`
   - `utm_campaign IS NULL`
   - `active = true`

If none resolves, UI MUST use `FALLBACK` explanation text and CTA label.

## Copy Rules
Explanation text MUST be:
- concise and scannable
- kind and non-judgmental
- framed as reducing admin burden and creating clarity

Explanation text MUST NOT:
- shame users
- escalate conflict
- include hardcoded URLs

CTA label MUST be:
- short and action-oriented
- outcome-first over generic install wording
- free of hardcoded URLs

Preferred CTA patterns:
- `Remove follow-ups`
- `Stop being the spreadsheet`
- `Lock your system in`
- `Admin relief in 5 minutes`

Discouraged CTA patterns:
- `Download Kinly`
- `Install now`

## UI Contract
Results page MUST render:
- poll question
- total votes line
- chart (pie/donut)
- option list with percentage + count
- resolved explanation text (`primary_message`)
- primary CTA from resolved `cta_label`

Fallback values:
- `fallback_primary_message`: `Every flat has its own "how things get done." Kinly helps make it clearer and calmer.`
- `fallback_cta_label`: `Set your flat up in 5 minutes`

## CTA Navigation Contract
Frontend CTA click MUST route to:
- `https://go.makinglifeeasie.com/kinly`

Store routing (iOS/Android/Web) is handled by that destination page and is out of scope for this contract.

Frontend MAY append query params for attribution:
- `src=poll`
- `poll=<page_key>`
- `opt=<option_key>`
- `k_sc=<short_code>`
- `utm_campaign`
- `utm_source`
- `utm_medium`
- `ui_locale`
- `country`
- `session_id` (if available)

Precedence:
- existing params SHOULD be preserved
- `poll` and `opt` MUST reflect current vote context

## Telemetry
Events MUST align with `outreach_tracking_v1_1.md` taxonomy and ingestion rules.

Frontend MUST emit:
- `poll_results_view` (once per `session_id + page_key + tab session`)
- `cta_click` on CTA tap/click

`poll_vote` is expected from backend vote RPC path.

Frontend MUST send events via:
- `public.outreach_log_event`

Frontend MUST NOT write outreach event tables directly.

Required fields for these events:
- `event`
- `app_key` (`kinly-web`)
- `page_key`
- `utm_campaign`
- `utm_source`
- `utm_medium`
- `session_id`

Recommended fields for results/CTA events:
- `poll_id`
- `option_id`
- `option_key`
- `k_sc`
- `resolved_message_id`
- `resolution_tier`

## Dependencies
- Poll frontend behavior: `outreach_polls_v1.md`
- Poll backend API: `../../../../api/kinly/growth/outreach_polls_v1.md`
- Result-message backend schema/security: `../../../../api/kinly/growth/outreach_poll_result_messages_v1.md`
- Tracking taxonomy: `outreach_tracking_v1_1.md`

## Acceptance Criteria
For a poll with three options:
1. one `GLOBAL_DEFAULT` row exists per option
2. selecting option A renders option A explanation text and CTA label
3. source and campaign override is preferred when both match
4. results render emits `poll_results_view` with `resolution_tier`
5. clicking CTA emits `cta_click`
6. CTA navigation target is `https://go.makinglifeeasie.com/kinly`

## Deferred Extensions
- A/B variants via `variant_key` with weighted selection
- locale-specific message table
- secondary CTA support
- micro-insight tooltips
- invite flow extensions
