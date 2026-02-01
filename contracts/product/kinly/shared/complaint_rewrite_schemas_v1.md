---
Domain: Product
Capability: complaint_rewrite
Scope: shared
Artifact-Type: contract
Stability: stable
Status: active
Version: v1.0
Audience: internal
Last updated: 2026-01-31
---

# Rewrite Request and Response Schema (aka 5.1 Rewrite Schema)

## 1. Purpose
- Define the canonical input and output shapes for the AI rewrite step.
- Keep AI limited to phrasing (not policy decisions) while remaining deterministic, auditable, and provider-agnostic.
- Permit model or provider swaps without changing interfaces or downstream consumers.

## 2. Design Principles
- AI writes words, not policy.
- Context is instructional, not descriptive; preferences guide tone and word choice but never appear in output.
- One rewrite produces exactly one output; rewrite and translation occur in a single step.

## 3. RewriteRequestV1 (input to rewriter)
Constructed only by the backend orchestrator after classification and context building.

```json
{
  "rewrite_request_id": "uuid",
  "sender": {
    "user_id": "uuid",
    "language": "bcp47"
  },
  "recipient": {
    "user_id": "uuid",
    "language": "bcp47",
    "power_mode": "higher_sender | higher_recipient | peer"
  },
  "message": {
    "original_text": "string",
    "detected_language": "bcp47"
  },
  "classification": {
    "topics": ["noise | cleanliness | privacy | guests | schedule | communication | other"],
    "intent": "request | boundary | concern | clarification",
    "rewrite_strength": "light_touch | full_reframe"
  },
  "rewrite_policy": {
    "tone": "gentle | neutral | calm",
    "directness": "soft | balanced",
    "emotional_temperature": "cool_down | steady",
    "avoid": [
      "authority_language",
      "rules_language",
      "enforcement_language"
    ]
  },
  "recipient_context": {
    "communication_style": "gentle | balanced | direct",
    "conflict_repair_preference": "cool_off | talk_soon | check_in",
    "noise_tolerance": "low | medium | high",
    "privacy_preference": "high | medium | low",
    "social_preference": "solo | balanced | together"
  },
  "output_constraints": {
    "target_language": "bcp47",
    "max_length_chars": 600,
    "no_exact_times": true,
    "no_preference_mentions": true,
    "no_rules_or_norms": true
  },
  "metadata": {
    "orchestrator_version": "v1",
    "classifier_version": "v1",
    "lexicon_version": "v1",
    "prompt_version": "v1"
  }
}
```

### Requiredness and validation
- `rewrite_request_id`, `sender.user_id`, `recipient.user_id`, `message.original_text`, `classification.intent`, `output_constraints.target_language` are REQUIRED.
- `classification.topics` MUST be non-empty; if classifier is unsure, include `"other"` explicitly.
- `rewrite_policy` MUST be fully populated by orchestrator; AI must not infer defaults.
- `recipient_context` MUST be topic-scoped: only include keys relevant to detected topics. Example: if `topics` = `["noise"]`, omit `privacy_preference` and `social_preference`.
- `max_length_chars` is a hard ceiling; AI must truncate politely if needed while preserving intent.
- `no_exact_times`: AI must not invent or modify times; it may retain times only if present verbatim in `original_text`.

## 4. Key Clarifications
- Power mode is tone-only: it may soften language but MUST NOT introduce authority, obligation, or ownership references.
- Rewrite policy is explicit: if tone is `gentle` and directness is `soft`, the output must follow even when the original is harsh.
- Preferences never appear in output; they only steer tone, pacing, and directness.

## 5. RewriteResponseV1 (output from rewriter)
This is the only allowed AI output shape.

```json
{
  "rewrite_request_id": "uuid",
  "rewritten_message": {
    "text": "string",
    "language": "bcp47"
  },
  "rewrite_notes": {
    "intent_preserved": true,
    "tone_applied": "gentle | neutral | calm",
    "translation_performed": true
  }
}
```

### Output constraints (non-negotiable)
- Preserve sender intent and requested directness/tone.
- Written in `output_constraints.target_language`.
- No authority, enforcement, or rules language.
- Do not reference recipient preferences, house norms, ownership, AI, or automation.
- Do not invent new complaints, facts, or times; only times present in the original may remain.
- Over-length outputs must be politely shortened without dropping the core ask or boundary.

## 6. Explicit exclusions
- No personality labels, sentiment scores, confidence fields, politeness ratings.
- No model or provider identifiers in the response (those remain in orchestrator logs/metadata).
- No visibility or delivery rules (handled by frontend/backend contracts).

## 7. System usage
- Orchestrator: builds `RewriteRequestV1`.
- AI router: selects model/provider, passes request.
- Rewriter adapter: converts request to prompt/template.
- Eval: validates `RewriteResponseV1`.
- Frontend: never sees these shapes.

## 8. Versioning rules
- Any field addition -> minor version bump.
- Any field removal or semantic change -> major version bump.
- Prompt changes do not affect this schema; model/provider swaps do not affect this schema.

## 9. Mental model
- Classifier decides what the message is about.
- Context pack decides how to speak.
- Rewrite schema tells AI exactly what to write.
- AI is a renderer, not a decider.
