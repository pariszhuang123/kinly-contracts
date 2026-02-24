---
Domain: Growth
Capability: outreach_polls
Scope: backend
Artifact-Type: contract
Stability: evolving
Status: active
Version: v1.0
Audience: internal
Last updated: 2026-02-24
---

# Contract - Outreach Polls API v1.0

## Purpose
Define backend schema and RPC contracts for public outreach polls with short-code-backed voting attribution.

## Design Constraints
- Web clients MUST use RPCs; no direct table writes.
- Vote attribution trust boundary is `short_code`.
- One net vote per `session_id + poll_id`.

## Authoritative Tables

### `public.outreach_polls`
- `id` uuid PK
- `app_key` text not null
- `page_key` text not null
- `title` text not null
- `question` text not null
- `description` text null
- `active` boolean default true
- `created_at`, `updated_at`
- unique `(app_key, page_key)`

### `public.outreach_poll_options`
- `id` uuid PK
- `poll_id` uuid FK -> `outreach_polls.id`
- `option_key` text not null
- `label` text not null
- `position` int not null
- `active` boolean default true
- `created_at`, `updated_at`
- unique `(poll_id, option_key)`

### `public.outreach_poll_votes`
- `id` uuid PK
- `poll_id` uuid FK -> `outreach_polls.id`
- `option_id` uuid FK -> `outreach_poll_options.id`
- `session_id` text not null
- `client_vote_id` uuid null
- `short_link_id` uuid null FK -> `outreach_short_links.id`
- attribution snapshot:
  - `page_key`
  - `source_id_resolved`
  - `utm_campaign`
  - `utm_source`
  - `utm_medium`
  - `store`
- `country` text null
- `ui_locale` text null
- `created_at`, `updated_at`

Constraints:
- unique `(poll_id, session_id)` (one net vote per session)
- unique `(client_vote_id)` where not null

## Read Views

### `public.outreach_poll_results_uc_v1`
Provides per-option UC counts for a poll:
- `page_key`
- `option_key`
- `vote_count`
- `total_votes`

Definition requirement:
- filtered to `source_id_resolved = 'uc'`.

### `public.outreach_poll_totals_uc_v1`
Provides UC total votes per poll:
- `page_key`
- `total_votes`
- `last_vote_at`

### `public.outreach_polls_overview_v1`
Provides all poll metadata and aggregated activity:
- title/question metadata
- active flag
- all-source total votes
- UC votes
- last activity timestamp

## RPC Surface

### `public.outreach_poll_get_v1(p_app_key text, p_page_key text) returns jsonb`
Behavior:
- returns active poll and active options ordered by `position`.
- success shape:
  - `{ ok: true, poll: {...}, options: [...] }`
- missing poll:
  - `{ ok: false, error: "poll_not_found" }`

### `public.outreach_poll_vote_submit_v1(...) returns jsonb`
Signature:
- `p_short_code text`
- `p_option_key text`
- `p_session_id text`
- `p_store text default 'unknown'`
- `p_client_vote_id uuid default null`
- `p_country text default null`
- `p_ui_locale text default null`

Behavior:
1. validate session/store/input.
2. resolve `p_short_code` in `outreach_short_links_effective`.
3. resolve poll from short-link `(app_key, page_key)`.
4. resolve option by `option_key` under poll.
5. upsert vote by `(poll_id, session_id)` to enforce one net vote per session.
6. persist attribution snapshot from short-link row.
7. emit `poll_vote` via `public.outreach_log_event`.
8. return `{ ok: true, results: { total_votes, option_counts[] } }` (recommended).

Errors:
- `INVALID_SHORT_CODE`
- `POLL_NOT_FOUND`
- `INVALID_OPTION`
- `INVALID_SESSION`
- `INVALID_STORE`
- `RATE_LIMIT_*` (if applied)

## Security
- RPCs MUST be `SECURITY DEFINER` with `SET search_path = ''`.
- RLS enabled on poll tables.
- `anon`/`authenticated` get EXECUTE on approved RPCs only.
- No direct DML grants to `anon`/`authenticated` on poll tables.

## Event Integration
- Poll vote RPC MUST emit `poll_vote` through `outreach_log_event`.
- Event taxonomy must align with `outreach_tracking_v1_1`.

## Acceptance Criteria
1. Poll fetch returns DB-defined poll by `app_key + page_key`.
2. Vote submit requires valid `short_code` and valid option membership.
3. One session has one net vote per poll.
4. Vote writes attribution snapshot from short-link row.
5. Successful vote emits `poll_vote` event.
