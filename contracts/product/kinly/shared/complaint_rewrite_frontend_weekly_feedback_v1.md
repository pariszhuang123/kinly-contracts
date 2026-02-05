---
Domain: Product
Capability: complaint_rewrite
Scope: frontend
Artifact-Type: contract
Stability: stable
Status: active
Version: v1.1
Audience: internal
Last updated: 2026-02-05
---

# Frontend: Weekly Feedback AI Rewrite Flow

## 1. Purpose
- Define the frontend UX and server interaction for submitting an emotionally difficult message from the Weekly Feedback Review into the complaint rewrite system.
- Ensure users can opt into a calmer rewrite without exposing their original wording to the recipient.
- Keep the experience opt-in, non-real-time, non-enforcing, and strictly one-to-one.

## 2. Conceptual framing
Reflection and translation assist — not a complaint, reporting, moderation, or drafting tool. Frontend submits intent only; AI/provider details stay server-side.

## 3. Entry conditions (hard gating)
The rewrite option MUST render only when all are true:
- Weekly Feedback Review completed.
- Emotion ∈ {rainy, thunderstorm}.
- User selects “Share with one person”.
- Recipient is in the same `home_id` and has completed personal preferences (explicit opt-in).
- Cadence: sender has not submitted a negative rewrite in the current ISO week (iso_week + iso_week_year), where the week boundary is Monday 00:00 UTC.

If the cadence check fails (sender already used their one rewrite this ISO week):
- Do NOT render the rewrite CTA.
- Surface an inline notice: “You already shared one this week. You can send another starting Monday 00:00 UTC.”
- Keep the user on the standard “today”/reflection page; the rewrite entry point reappears automatically when the next ISO week starts.

If any condition fails: do not render rewrite option; user remains in private reflection. No overrides.

## 4. Sender UX flow
1) Sender picks emotion (rainy or thunderstorm).
2) Sender selects exactly one recipient (no multi-select).
3) Sender enters free-form message text.
4) Show fixed helper copy: “This won’t be shared as written.” and “Kinly rewrites this to help it land more calmly.”
5) Sender taps “Rewrite with Kinly”.
6) Show consent confirmation: “I understand this won’t be sent as written.”
7) On confirm: submit; input locks; no edit/undo; original is never shown again.

## 5. Client → server interaction
RPC: `weekly_feedback_rewrite_create_v1`

Payload (frontend controlled):
```json
{
  "home_id": "uuid",
  "sender_user_id": "uuid",
  "recipient_user_id": "uuid",
  "emotion_context": "rainy | thunderstorm",
  "sender_message": "string",
  "mode_preference": "async"
}
```

Client MUST NOT call AI providers, send model/prompt identifiers, pass preferences, guess topic/intent, or estimate rewrite timing.

## 6. Server-controlled lifecycle (informational)
- Message persisted immediately with status `queued`.
- Rewrite runs asynchronously; batching/caching may occur; timing is non-deterministic.
- Frontend must assume minutes-plus latency and eventual delivery only.

## 7. Visibility rules
Recipient:
- Sees only the rewritten message after completion.
- Never sees original text, emotion label, AI involvement, or timing metadata.

Sender:
- Never sees original text again.
- Sees rewritten message only after `sender_reveal_at` (server-defined; default +24h).
- Before reveal: only delivery status is visible.

## 8. UX states (sender)
- Queued: “Kinly is preparing a calmer version.”
- Delivered (hidden): “Your message has been shared.”
- Rewritten (revealed): rewritten message visible.
- Failed: gentle fallback copy.

No countdowns, ETAs, or guarantees.

## 9. Rewrite output assumptions (frontend)
- Intent preserved, tone softened, natural language, recipient locale applied.
- Frontend must not explain wording changes, reference preferences, house rules, or power roles.

## 10. Locale handling
- Default to recipient locale. If sender locale differs, rewrite + translation happen server-side in one pass.
- Frontend must not translate or display bilingual output.

## 11. Error handling
- If rewrite fails, message is not delivered.
- Copy: “Something went wrong. Your message wasn’t shared.”
- Retry requires a new submission; original text remains unrecoverable.

## 12. Telemetry (privacy-safe)
- MAY log: `weekly_review_completed`, `rewrite_submitted`, `rewrite_completed`, `rewrite_revealed_to_sender`, `message_delivered`, `rewrite_failed`.
- MUST NOT log: original text, rewritten text, recipient identifiers, emotion labels.

## 13. Explicit non-goals
- Not an escalation tool, broadcast channel, editable drafting surface, live chat, or house-rules negotiation surface.
- Strictly weekly, emotion-led, one-to-one clarity assist.

## 14. Relationship to other contracts
- `complaint_rewrite_index_v1` — overall scope and invariants.
- `complaint_rewrite_schemas_v1` — backend rewrite request/response shapes.
- `complaint_rewrite_backend_context_pack_v1`, `complaint_rewrite_ai_classifier_v1`, `complaint_rewrite_edge_orchestrator_v1`, `complaint_rewrite_ai_routing_providers_v1`, `complaint_rewrite_async_jobs_v1` — backend only.
- `rewrite_eval_v1`, `complaint_rewrite_eval_dataset_v1`, `complaint_rewrite_eval_judge_v1` — backend QA only.
