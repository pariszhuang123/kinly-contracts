---
Domain: Product
Capability: complaint_rewrite
Scope: backend
Artifact-Type: guide
Stability: stable
Status: active
Version: v1.0
Audience: internal
Last updated: 2026-02-01
---

# Recipient Context Pack Examples

Use these fixtures as golden cases for adapter and eval tests. They mirror `RecipientContextPackV1` from `complaint_rewrite_backend_context_pack_v1`.

## Files
- `context_pack_noise_owner_to_housemate.json` — noise topic, higher_sender tone multiplier (owner -> housemate).
- `context_pack_privacy_peer.json` — privacy topic, peer power.
- `context_pack_no_preferences_fallback.json` — baseline when no preferences are available.

## How to use in tests
- Adapter tests: load fixture, render prompt/payload, assert required fields and enums are preserved verbatim.
- Eval smoke: feed alongside a sample rewrite request and verify the rewriter honors `instructions`, `avoid`, and `do_not_add`.
- Regression: keep these snapshots stable; if mappings change, update fixture and bump version per contract rules.

## Guardrails when extending
- Do not add model/provider identifiers to fixtures.
- Keep `avoid` and `do_not_add` non-empty.
- Match `topics` and `included_preference_ids` to the topic map in the contract.
