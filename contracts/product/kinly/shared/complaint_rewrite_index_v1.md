---
Domain: Product
Capability: complaint_rewrite
Scope: shared
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
Audience: internal
Last updated: 2026-01-31
---

# Complaint Rewrite With Recipient Preferences (Index)

## 1. Purpose
- Provide a deterministic, auditable pipeline that rewrites emotionally difficult messages so they land calmly with the intended recipient.
- Preserve sender intent while softening tone and honoring recipient communication preferences (language, directness, timing).
- Support weekly, non-urgent submission surfaces (for example, "Weekly Harmony") with delayed reveal to the sender.

## 2. Scope & Non-Goals
**Scope**
- Context-aware rewrite pipeline for asynchronous complaints or difficult news.
- Recipient preference interpretation scoped to the topics being discussed.
- Supports @mentioning a house member as the intended recipient.

**Out of scope**
- Moderation or rule enforcement.
- Real-time chat assistance or escalation flows.
- Personality profiling or recipient labeling beyond stated preferences.

## 3. Invariants (MUST)
- Original message is stored before any AI step and remains retrievable for audit.
- Orchestrator decisions are deterministic; AI is only asked to phrase, never to choose the flow.
- Preference context is instructional (how to phrase), not descriptive (who the person is).
- Power awareness affects tone softening only; never grants authority or enforcement language.
- Rewrite is asynchronous; no guarantees of immediate delivery or recipient acknowledgement.
- Cadence: per sender, maximum one negative rewrite submission per ISO week (iso_week + iso_week_year), week boundary = Monday 00:00 UTC; maximum one @mention target per sender per ISO week; no home-level quota.
- Eligibility: a recipient can be @mentioned only if they have completed their personal preference inputs; otherwise the submission is rejected with a clear error surfaced to the sender.
- @mentions are limited to members of the same home and must respect visibility and consent gates defined by the frontend contract.

## 4. High-Level Flow
1) User submits a difficult message via an allowed weekly surface; frontend passes intent, recipient, and consent flags only.
2) Message is stored (no AI yet); submission is logged with cadence guardrails (weekly per user) and recipient eligibility (preference completion).
3) Cheap classifier determines topic, intent, language, and rewrite strength.
4) Backend builds a topic-scoped recipient context pack from stored preferences (tone, directness, language, cool-off versus talk-soon).
5) Edge orchestrator validates eligibility, selects rewrite policy, and routes to the chosen AI provider.
6) Rewrite runs asynchronously; batching is allowed when safe.
7) Outputs are checked against evaluation guardrails; failures route to safe fallback copy or manual review bucket.
8) Recipient receives rewritten message; sender sees the rewritten version after delivery (delayed reveal).

## 5. Interfaces (minimum fields)
**Rewrite Request (orchestrator input)**
- `submission_id`, `sender_id`, `recipient_id`
- `topic`, `intent`, `rewrite_strength`, `sender_language`
- `recipient_context_pack_id` (scoped preferences only)
- `power_mode` (owner/head tenant versus housemate)

**Rewrite Output (orchestrator output)**
- `rewritten_text`, `language`, `model_id`, `provider`
- `lexicon_version`, `policy_version`, `eval_result`
- `delivered_at`, `revealed_to_sender_at`, `fallback_reason` (optional)

## 6. Safety and Evaluation Hooks
- Hard safety: no enforcement or authority language, no unapproved threats, no naming outside the provided recipient, no translation drift on key asks.
- Tone and power safety: soften when power is asymmetric; avoid imperatives unless explicitly requested.
- Intent preservation: request, boundary, or clarification must remain semantically intact.
- Regression: compare against `complaint_rewrite_eval_dataset_v1`; blocked outputs route to fallback.

## 7. Sub-Contracts (binding map)
- `complaint_rewrite_schemas_v1` - shared enums and rewrite strength taxonomy.
- `complaint_rewrite_frontend_*` - allowed submission surfaces, cadence limits, consent, @mention visibility rules.
- `complaint_rewrite_backend_context_pack_v1` - preference interpretation and scoping.
- `complaint_rewrite_ai_classifier_v1` - cheap topic, intent, and language classifier.
- `complaint_rewrite_edge_orchestrator_v1` - deterministic control plane and policy selection.
- `complaint_rewrite_ai_routing_providers_v1` - provider and model mapping, batching rules.
- `complaint_rewrite_async_jobs_v1` - queueing, retries, completion timestamps.
- `rewrite_eval_v1`, `complaint_rewrite_eval_dataset_v1`, `complaint_rewrite_eval_judge_v1`, `complaint_rewrite_lexicon_v1` - safety and regression layer.

## 8. Open Questions and TODOs
- Clarify fallback behaviors for failed evaluation (redaction versus templated apology versus manual review).
- Decide whether sender preview is allowed before delivery or only after recipient receipt.
- Set audit retention window and access controls for stored originals and rewrite logs.
