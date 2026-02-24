---
Domain: product
Capability: outreach_polls
Scope: frontend
Artifact-Type: contract
Stability: evolving
Status: active
Version: v1.0
Audience: public
Last updated: 2026-02-24
---

# Contract - Kinly Outreach Polls (Web) v1.0

## Purpose
Define poll UX and tracking behavior for public outreach polls that:
- collect low-friction anonymous votes
- show local social proof ("X UC students voted")
- drive app downloads

## Scope
In scope:
- poll rendering and vote submission
- poll results screen
- short-link handoff behavior (`k_sc`)
- poll analytics events
- app-store bridge CTA behavior

Out of scope:
- authenticated voting
- per-flat segmentation
- unique-person verification

## Route Shape
- Canonical poll route: `/kinly/polls/<slug>`
- Poll pages MUST remain browser-readable and MUST NOT auto-open deep links.

## Poll Identity
- `page_key` is the canonical poll identifier used in tracking and backend APIs.
- Frontend MUST derive deterministic `page_key` from route slug.

## Short-Link Handoff
- Poll vote attribution MUST trust short code, not mutable URL UTMs.
- Resolver route `/<shortCode>` MUST append `k_sc=<shortCode>` for poll destinations.
- Frontend vote submission MUST include `k_sc` as RPC input.

## API Usage (Web)
Frontend MUST call:
- `public.outreach_poll_get_v1` to fetch poll definition/options.
- `public.outreach_poll_vote_submit_v1` to submit votes.

Frontend MAY read:
- `outreach_poll_results_uc_v1` for result visualization.

Frontend MUST NOT write poll tables directly.

## UX Sequence (Normative)
1. Load poll page and fetch poll definition.
2. Emit `poll_page_view` once per `session_id + page_key + tab session`.
3. User selects exactly one option.
4. Submit vote with `k_sc`, `option_key`, and `session_id`.
5. Render results and social-proof count.
6. Emit `poll_results_view` once when results are shown.
7. Store CTA clicks emit `cta_click`.

## Voting Rules
- If `k_sc` is missing/invalid, voting MUST be blocked with safe UI copy.
- Vote success MUST transition to results view.
- Repeated submits from same session SHOULD be idempotent at backend.

## Results Rules
- Results MUST include:
  - option-level counts/percentages
  - total UC vote count
- Display text MUST include local count: `"X UC students voted"` (or locale equivalent).

## Attribution Rules
- `utm_source` should map to school alias (e.g., `uc`) for UC pooling.
- `utm_medium` identifies placement.
- `page_key` identifies poll type.
- `k_sc` remains vote attribution trust anchor.

## Events
Frontend MUST align with outreach tracking v1.1:
- `poll_page_view`
- `poll_results_view`
- `cta_click`

`poll_vote` is expected from backend vote RPC path.

## Privacy and Safety
- No login required.
- No personal identifiers collected in poll flow.
- Failures MUST not dead-end the user.

## Acceptance Criteria
1. Poll route renders from DB-defined poll.
2. Vote requires valid `k_sc`.
3. Results render after vote with UC total.
4. Poll tracking events follow v1.1 event taxonomy.
5. CTA click tracking remains best-effort and non-blocking.
