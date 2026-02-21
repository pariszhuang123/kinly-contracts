---
Domain: product
Capability: qr_short_link_resolution
Scope: frontend
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
Audience: internal
Last updated: 2026-02-21
---

# Contract - QR Generator Short Link Resolution (Web) v1.0

## Purpose
Define `/tools/qr` submit behavior so generated QR assets use a short URL when available, while preserving canonical campaign tracking metadata.

This contract governs frontend flow only.
Backend storage and resolver rules are defined in:
- `contracts/api/kinly/growth/outreach_short_links_v1.md`
- `contracts/api/kinly/growth/outreach_tracking_v1.md`

## Scope
In scope:
- Submit action orchestration for short-link get-or-create.
- URL precedence for preview, copy, and export.
- Failure handling and fallback behavior.
- Environment-aware output host behavior.

Out of scope:
- QR visual styling/token choices.
- Backend schema details and migrations.
- Outreach analytics query definitions.

## Route
- Surface: `https://go.makinglifeeasie.com/tools/qr` (production)
- Surface: `https://staging.makinglifeeasie.com/tools/qr` (staging when available)

## Submit Flow (Normative)
On `Submit & Generate`, client MUST execute:

1. Build canonical destination tuple from form selection:
- `target_path`
- `target_query`
- `utm_campaign`
- `utm_source`
- `utm_medium = "qr"`
- `app_key`
- `page_key`

2. Call backend get-or-create endpoint (`outreach.short_links_get_or_create`).

3. If successful:
- Use returned short URL as the canonical generated URL.
- Render QR from the short URL.
- Populate copy field with the short URL.
- Use short URL for PNG/SVG export payload.

4. If call fails:
- Fallback to full canonical URL (`host + target_path + utm query`).
- Continue rendering/copy/export without blocking.
- Show non-blocking inline warning: short link unavailable, using full URL.

## Idempotency and Reuse Rules
- Frontend MUST treat backend response as source-of-truth for code reuse.
- If canonical destination already exists, frontend MUST reuse existing short URL.
- Frontend MUST NOT generate local/random short codes.

## Environment Rules
- Frontend MUST NOT hardcode short-link host in generated payload.
- Frontend MUST use backend-returned `short_url` for display and QR content.
- If backend returns environment-specific host, frontend MUST preserve it verbatim.

## URL Precedence Rules
- Preferred: backend short URL.
- Fallback: full canonical destination URL.
- The URL used for on-screen display, copy action, and downloadable QR assets MUST be identical within a single generation result.

## UX and Error Handling
- Submit button MUST remain enabled after failure (no dead-end state).
- Generation MUST complete even when short-link API is unavailable.
- Warnings MUST be non-modal and MUST NOT block downloads.
- No technical error codes shown to end users.

## Security and Access
- Frontend MUST call only approved RPC/API surface; no direct table writes.
- Frontend MUST NOT expose service-role credentials.
- Frontend MUST NOT mutate canonical UTM values returned by backend.

## Acceptance Criteria
1. Submit with valid input returns short URL and QR encodes short URL.
2. Repeat submit for same canonical destination returns same short URL.
3. API unavailable still generates valid QR using full URL.
4. Copy button value equals encoded QR URL in both success and fallback paths.
5. Staging and production produce host-appropriate URLs from backend response.

