---
Domain: Product
Capability: complaint_rewrite
Scope: backend
Artifact-Type: contract
Stability: stable
Status: active
Version: v1.0
Audience: internal
Last updated: 2026-01-31
---

# Edge Orchestrator (complaint_rewrite_edge_orchestrator_v1)

## 1) Purpose
Define the deterministic control plane for the complaint rewrite system.

The orchestrator:
- wires together upstream and downstream contracts
- decides what happens next (never how to phrase)
- enforces hard safety and product invariants
- keeps behavior backend-controlled and auditable

## 2) Core Principle
**AI may generate language, but the orchestrator decides behavior.**  
Deterministic: same inputs → same decisions; AI is never asked to infer policy, eligibility, or routing.

## 3) Inputs
### 3.1 Entry from frontend / RPC
Invoked only via stable server entrypoints (e.g., `weekly_harmony_rewrite_create_v1` and future complaint surfaces).

Required input:
```json
{
  "home_id": "uuid",
  "sender_user_id": "uuid",
  "recipient_user_id": "uuid",
  "sender_message": "string",
  "emotion_context": "optional enum",
  "surface": "weekly_harmony | direct_message | other"
}
```
Frontend MUST NOT pass AI provider/model info, preferences, topics, or power roles.

## 4) Orchestrator responsibilities (sequential)
1. **Eligibility & gating**  
   - Same `home_id`.  
   - Surface allowed (Weekly Harmony rules already applied upstream).  
   - Recipient opted in (preferences completed).  
   - Sender cadence: max one negative rewrite per ISO week (iso_week + iso_week_year, week starts Monday 00:00 UTC); fail closed if limit reached.  
   - Recipient cadence: must have completed preferences (already enforced).  
   - On failure: abort; return generic failure; do NOT enqueue AI work.

2. **Message persistence (pre-AI)**  
   - Persist raw sender message.  
   - Assign `rewrite_request_id`; status = queued; original text write-once.  
   - Guarantees durability and auditability.

3. **Invoke AI classifier** (`complaint_rewrite_ai_classifier_v1`)  
   - Inputs: `sender_message`, `sender_user_id`, `surface`.  
   - Receive topics, intent, detected language, rewrite strength, safety flags.  
   - Treat output as advisory; apply conservative defaults if confidence low.

4. **Build recipient context pack** (`complaint_rewrite_backend_context_pack_v1`)  
   - Inputs: `home_id`, `sender_user_id`, `recipient_user_id`, `topics[]`, `target_language` (recipient locale), `sender_language` (from classifier).  
   - MUST NOT add/remove preferences, infer missing preferences, or override context semantics.

4a. **Create snapshots (deterministic, before enqueue)**  
   - `recipient_snapshot_id`: stable recipient set at request time (the mentioned user).  
   - `recipient_preference_snapshot_id`: stable preference snapshot for that recipient.  
   - Purpose: prevent membership/preference drift from altering delivery or tone later.  
   - Store these IDs with the rewrite request; pass into job payloads.

5. **Derive rewrite policy and locales**  
   - Inputs: classifier output, context pack, surface rules, power mode.  
   - Normalize locales: decide `source_locale` (classifier language if confidence medium/high, else sender profile locale if present, else `en`); decide `target_locale` (recipient locale normalized, else `en`).  
   - Compute lane: `same_language` if source = target; else `cross_language`.  
   - Policy: `{ tone: gentle|neutral|calm, directness: soft|balanced, emotional_temperature: cool_down|steady, rewrite_strength: light_touch|full_reframe }`.  
   - Rules: higher sender power → softer tone; low confidence → gentler defaults; emotional intensity → cool_down.

   Pseudocode (informative):
   ```
   detected = normalize(classifier.detected_language)
   profile  = normalize(sender_profile_locale) // may be null
   source   = (classifier.confidence in {medium,high}) ? detected : (profile ?? "en")
   target   = normalize(recipient_locale) ?? "en"
   lane     = (source == target) ? "same_language" : "cross_language"
   ```

6. **Assemble RewriteRequestV1**  
   - Include original message, classification, rewrite policy, context pack, output constraints, metadata.  
    - MUST conform to `RewriteRequestV1`; no extra fields; no provider hints.  
    - Attach normalized `source_locale`, `target_locale`, and `lane`; attach snapshot IDs.

7. **Select AI route** (`complaint_rewrite_ai_routing_providers_v1`)  
   - Inputs: task=complaint_rewrite, rewrite_strength, surface, language_pair (source→target), lane, policy_version.  
   - Receive provider, model, execution mode (sync|async|batch), prompt_version.  
   - Accept routing output as-is; never override locally.

8. **Enqueue rewrite job** (`complaint_rewrite_async_jobs_v1`)  
   - Payload: `rewrite_request_id`, serialized RewriteRequestV1, routing info, retry policy.  
   - Return to frontend immediately; do NOT wait for AI completion.

## 5) Post-rewrite handling
- On completion: validate `RewriteResponseV1`; run lexicon + hard safety checks; store rewritten message; set `rewrite_completed_at`; set `sender_reveal_at` (e.g., +24h).
- On failure: mark status = failed; do NOT retry indefinitely; do NOT expose partial output.
 - Reveal timing rule: `sender_reveal_at = rewrite_completed_at + reveal_delay` (product default 24h unless configured). Orchestrator is authoritative; async layer only persists it.

## 6) Error handling & fallbacks
- Classifier failure → defaults: topics ["other"], intent concern, rewrite_strength full_reframe, confidence low.
- Context pack failure → abort rewrite; mark failed; never call rewriter without context.
- Rewriter failure → mark failed; user may retry only with a new message.

## 7) Audit & observability
Record per rewrite: `rewrite_request_id`, classifier_version, context_pack_version, rewrite_policy, provider, model, prompt_version, lexicon_version, timestamps for each stage.

## 8) MUST NOT
- Orchestrator MUST NOT rewrite text, infer preferences, call AI providers directly, expose internal decisions to frontend, apply house norms/rules, or decide visibility timing (except sender reveal gate).

## 9) Determinism guarantee
Given identical sender message, recipient, preferences, classifier version, and routing config → produce the same rewrite request and routing decision. Non-determinism is a contract violation.

## 10) Versioning rules
- Adding orchestration steps → MINOR bump.
- Changing decision logic → MAJOR bump.
- Provider/model changes → NO version bump.

## 11) Summary
The edge orchestrator is the brain of the rewrite system: it keeps AI on a tight leash, protects user trust, and enables safe evolution of models and prompts. If behavior is unexpected, check the orchestrator first.

## TODO
- Add explicit cross-links to `rewrite_eval_v1` and `complaint_rewrite_lexicon_v1` once finalized to make validation dependencies explicit.
