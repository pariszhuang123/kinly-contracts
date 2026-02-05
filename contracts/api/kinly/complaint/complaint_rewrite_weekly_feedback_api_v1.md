---
Domain: Product
Capability: complaint_rewrite
Scope: backend
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
Audience: internal
Last updated: 2026-02-04
---

# Weekly Feedback Rewrite API (complaint_rewrite_weekly_feedback_api_v1)

## 1) Purpose
Expose a backend entrypoint for weekly feedback messages that need calm rewrites before delivery. This surface reuses the complaint rewrite pipeline and introduces `surface = weekly_feedback` as the canonical value (alias: `weekly_harmony` for backward compatibility).

## 2) Entrypoint (RPC)
`weekly_feedback_rewrite_create_v1`

### 2.1 Request payload (authoritative)
```json
{
  "home_id": "uuid",
  "sender_user_id": "uuid",
  "recipient_user_id": "uuid",
  "feedback_cycle_start": "date (ISO 8601, week start)", 
  "sender_message": "string",
  "emotion_context": "optional enum",
  "surface": "weekly_feedback"
}
```

Rules:
- `surface` MUST be `weekly_feedback`; the backend MAY accept `weekly_harmony` and normalize to `weekly_feedback`.
- Frontend MUST NOT send AI provider/model names, prompts, classifier hints, or recipient preferences.
- `feedback_cycle_start` pins cadence to an ISO week (Monday 00:00 UTC). If omitted, backend derives from `now()` at UTC and stores iso_week + iso_week_year.

### 2.2 Response (minimum)
```json
{
  "rewrite_request_id": "uuid",
  "job_id": "uuid",
  "status": "queued | failed"
}
```
- `status = queued` means the request was persisted and enqueued; fulfillment is asynchronous.
- `status = failed` means hard gating failed; no AI work was created.

## 3) Gating and eligibility
- Home and recipient must be in the same `home_id`.
- Recipient must have completed personal preferences; otherwise fall back to default context pack rules (see `complaint_rewrite_backend_context_pack_v1`).
- Cadence: max one `full_reframe` rewrite per sender per ISO week per home. Requests past the limit fail closed.
- Message length: backend MUST enforce a sane limit (e.g., 1,500 chars) to keep cost bounded.
- Abuse: blocklisted senders or recipients MUST be rejected before enqueue.

## 4) Server workflow (delegated)
1. Persist request and snapshots (recipient + preferences).
2. Call classifier (`complaint_rewrite_ai_classifier_v1`) with `surface = weekly_feedback`.
3. Build context pack (`complaint_rewrite_backend_context_pack_v1`).
4. Derive policy/locales and assemble `RewriteRequestV1`.
5. Route (`complaint_rewrite_ai_routing_providers_v1`) and enqueue job (`complaint_rewrite_async_jobs_v1`).
6. Downstream processing, batching, safety checks, and delivery follow existing rewrite contracts unchanged.

## 5) Observability (minimum)
- Events: `weekly_feedback_rewrite_received`, `weekly_feedback_rewrite_enqueued`, `weekly_feedback_rewrite_completed`, `weekly_feedback_rewrite_failed`, `weekly_feedback_rewrite_revealed_to_sender`.
- Event payloads MUST use opaque IDs; no raw or rewritten text.
- Metrics: rate by surface, iso_week, rewrite_strength, provider/model, failure reason.

## 6) Backward compatibility
- `weekly_harmony` requests MUST continue to work but SHOULD be normalized to `weekly_feedback` in storage and routing keys.
- No changes to prompt_version or policy_version are implied; routing config may map `weekly_feedback` to existing `weekly_harmony` rows during migration.

## 7) MUST NOT
- No multi-recipient fan-out; one recipient per request.
- No synchronous completions or progress polling endpoints.
- No exposure of classifier output, routing decisions, or context packs to the client.
- No inline retries from the client; retry requires a new submission.

## 8) Versioning
- Adding required fields or changing cadence semantics -> MAJOR.
- Adding optional metadata (e.g., `feedback_cycle_id`) -> MINOR.
- Renaming the surface after normalization -> MAJOR.
