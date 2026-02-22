---
Domain: product
Capability: qr_short_link_resolution
Scope: frontend
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0.2
Audience: internal
Last updated: 2026-02-22
---

# Contract - QR Generator Short Link Resolution (Web) v1.0.2

## Purpose
Define `/tools/qr` submit behavior so generated QR assets use a short URL when available, while preserving canonical campaign tracking metadata.

This contract governs frontend flow only.
Backend storage and resolver rules are defined in:
- `contracts/api/kinly/growth/outreach_short_links_v1.md`
- `contracts/api/kinly/growth/outreach_tracking_v1.md`

## Scope
In scope:
- Submit action orchestration for backend-mediated short-link get-or-create.
- URL precedence for preview, copy, and export.
- Failure handling and fallback behavior.
- Environment-aware output host behavior.
- Public-page safety boundaries for short-link creation.

Out of scope:
- QR visual styling/token choices.
- Backend schema details and migrations.
- Outreach analytics query definitions.

## Route
- Surface: `https://go.makinglifeeasie.com/tools/qr` (production)
- Surface: `https://staging.makinglifeeasie.com/tools/qr` (planned; not yet live as of 2026-02-22)

## Environment Rollout State (Normative)
- As of 2026-02-22, only `go.makinglifeeasie.com` is live for this flow.
- Until `staging.makinglifeeasie.com` is live, non-production environments MAY receive production-host `short_url` values from backend.
- Frontend MUST treat backend-returned `short_url` host as authoritative and MUST NOT rewrite host client-side.
- Once `staging.makinglifeeasie.com` is live, backend SHOULD return staging host in staging, and temporary fallback to production SHOULD be removed.

## Integration Surface (Normative)
- Frontend MUST call a trusted backend route (for example, a Next.js API route), not the DB RPC directly.
- Backend route MUST validate incoming payload before attempting short-link creation.
- Backend route MUST apply rate limiting and abuse controls.
- Backend route MUST call `public.outreach_short_links_get_or_create` using service-role credentials.
- Backend route MUST return the authoritative `short_url` from backend response.
- Public users MAY access `/tools/qr`, but this MUST NOT grant direct public link-creation rights at DB/RPC layer.

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

2. Call trusted backend short-link endpoint (Next.js API route or equivalent).

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
- Frontend MUST call only approved backend API surface for short-link creation.
- Frontend MUST NOT call `public.outreach_short_links_get_or_create` directly.
- Frontend MUST NOT expose service-role credentials.
- Frontend MUST NOT mutate canonical UTM values returned by backend.
- Backend route MUST keep service-role credentials server-side only.
- Backend route MUST enforce abuse controls before service-role RPC execution.

## Acceptance Criteria
1. Submit with valid input returns short URL and QR encodes short URL.
2. Repeat submit for same canonical destination returns same short URL.
3. API unavailable still generates valid QR using full URL.
4. Copy button value equals encoded QR URL in both success and fallback paths.
5. Host behavior follows backend response: production host today, then environment-appropriate host after staging launch.
6. Browser client cannot create short links by calling service-role RPC directly.
