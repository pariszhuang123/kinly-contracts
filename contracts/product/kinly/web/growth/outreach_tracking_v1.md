---
Domain: product
Capability: outreach_tracking
Scope: frontend
Artifact-Type: contract
Stability: stable
Status: active
Version: v1.0
Audience: public
Last updated: 2026-01-30
---

# Contract — Kinly Marketing Page Outreach Tracking (Frontend, UTM-aligned)

## 1. Purpose

Define a **minimal, privacy-safe** tracking mechanism for Kinly marketing pages to answer:

1. How many people accessed a marketing page (visit proxy)?
2. Which call-to-action (CTA) did they click (iOS App Store, Google Play, web)?
3. Which campaign and channel/source brought them?

This contract defines **client-side behavior and event semantics only**.

Storage, validation, canonical source resolution (including alias mapping), rate limiting, and security controls are defined in the backend companion contract:

- **Contract — Outreach Event Logging (UTM-aligned, Alias Mapping, RPC-only)**

---

## 2. Canonical Pages (Normative)

**Base URL:** `https://go.makinglifeeasie.com`

**Tracked paths:**

| Path Pattern         | Description                  |
| -------------------- | ---------------------------- |
| `/kinly/general`     | General entry page           |
| `/kinly/marketing/*` | All marketing campaign pages |

All tracked pages MUST:
- render readable content in a browser
- never auto-open the app
- never auto-redirect to an app store
- emit tracking events on a best-effort basis
- never block navigation due to tracking failure

---

## 3. Canonical URL Parameters (Normative)

Tracked pages MUST accept **GA-style UTM parameters**:

| Parameter        | Required | Description |
|------------------|----------|-------------|
| `utm_campaign`   | yes*     | Campaign identifier (e.g., `first_year_2026`) |
| `utm_medium`     | yes*     | Channel type (e.g., `qr`, `poster`, `share`, `interest_page`, `direct`, `email`, `social`) |
| `utm_source`     | yes*     | Raw source identifier from the world (e.g., `fish&chips_ilam`, `uc_ilam`, `instagram_bio`) |

\* “Required” here means the **client MUST send a value** for each parameter. If absent/blank in the URL, the client MUST send `"unknown"`.

Rules:
- If any UTM parameter is missing or blank, the client MUST send the literal string `"unknown"` (not `null`, not empty).
- The client MUST NOT attempt to canonicalize or resolve sources (no registry lookups).
- The client SHOULD lowercase `utm_source` and `utm_medium` before sending (backend also normalizes; this is for consistency).

**Examples:**
- QR flyer:  
  `/kinly/general?utm_campaign=first_year_2026&utm_medium=qr&utm_source=fish&chips_ilam`
- Interest page forward:  
  `/kinly/general?utm_campaign=early_interest_2026&utm_medium=interest_page&utm_source=go_get_page`
- University poster:  
  `/kinly/marketing/students?utm_campaign=uni_launch_2026&utm_medium=poster&utm_source=uc_ilam`

---

## 4. Tracking Model (Normative)

Tracking MUST be implemented as an **append-only event log**:
- each meaningful user action emits one event
- multiple events per session are expected
- events MUST NOT be updated or merged client-side
- tracking failures MUST NOT block page functionality

---

## 5. Backend Ingestion (Normative)

Frontend MUST log events by calling the canonical backend RPC:

- **RPC:** `public.outreach_log_event`

Rules:
- Frontend MUST NOT write directly to any outreach tables.
- Frontend MUST NOT perform canonical source resolution or alias mapping.
- Backend resolves `utm_source` → `source_id_resolved`.

---

## 6. Tracked Events (Normative)

Only the following event types are permitted.

### 6.1 `page_view`

Purpose: visit / scan proxy.

Rules:
- MUST be emitted **at most once** per `session_id` per `page_key` per **tab session**.
- MUST be emitted on initial page load.
- `store` MUST be omitted or `null`.

### 6.2 `cta_click`

Purpose: records install or web intent.

Rules:
- MUST be emitted when a CTA button is clicked.
- MAY emit multiple events per session (e.g., iOS + Android + web).
- `store` MUST be set.

Allowed `store` values:
- `ios_app_store`
- `google_play`
- `web`
- `unknown`

---

## 7. Event Schema (Normative)

Events sent to the RPC MUST conform to the following schema.

### Required fields
- `event`: `page_view` | `cta_click`
- `app_key`: MUST be `kinly-web`
- `page_key`: snake_case identifier (e.g., `kinly_general`, `kinly_marketing_students`)
- `utm_campaign`: string or `"unknown"`
- `utm_medium`: string or `"unknown"`
- `utm_source`: string or `"unknown"`
- `session_id`: required

### Optional fields
- `store` (required for `cta_click`)
- `country` (best-effort)
- `ui_locale` (best-effort)
- `client_event_id` (RECOMMENDED for idempotent `cta_click`; MAY also be used for `page_view`)

Notes:
- Client MUST NOT send `timestamp`. Backend assigns `created_at`.
- Client MUST NOT send any user identifiers.

### Example — `page_view`
```json
{
  "event": "page_view",
  "app_key": "kinly-web",
  "page_key": "kinly_general",
  "utm_campaign": "first_year_2026",
  "utm_medium": "qr",
  "utm_source": "fish&chips_ilam",
  "session_id": "anon_a7Bf3kLm9PqR2xYz",
  "country": "NZ",
  "ui_locale": "en-NZ"
}

Example — cta_click
{
  "event": "cta_click",
  "app_key": "kinly-web",
  "page_key": "kinly_general",
  "utm_campaign": "first_year_2026",
  "utm_medium": "qr",
  "utm_source": "fish&chips_ilam",
  "store": "ios_app_store",
  "session_id": "anon_a7Bf3kLm9PqR2xYz",
  "client_event_id": "3d6c2b57-ff8f-4d52-9c1e-9a28f1bd2e9a",
  "country": "NZ",
  "ui_locale": "en-NZ"
}

8. Client Tracking Algorithm (Normative)

This contract intentionally does not mandate a specific framework implementation.
However, the following client-side algorithm is normative to ensure events are
consistent with backend RPC validation and expected semantics.

8.1 Session Identifier (Normative)

session_id exists solely to:

de-duplicate page_view events

support aggregate analytics and backend rate limiting

Rules:

MUST be generated client-side

MUST be stored in localStorage under a stable key (e.g., kinly.outreach.session_id)

MUST match: ^anon_[A-Za-z0-9_-]{16,32}$

SHOULD rotate after 30 days (best-effort)

MUST NOT be stored in cookies

MUST NOT be linked to authentication or identity

Generation rules:

The token portion (after anon_) MUST be URL-safe characters: [A-Za-z0-9_-]

Length MUST be 16–32 characters (excluding the anon_ prefix)

UUID strings MUST NOT be used directly (may violate length/format rules)

8.2 Tab-Session De-duplication for page_view (Normative)

page_view MUST be emitted at most once per session_id + page_key + tab session.

Implementation guidance:

The client MAY implement a tab-scoped guard using sessionStorage, such as:
kinly.outreach.page_view.sent.<page_key> = "1"

The client MAY use an in-memory guard in addition to sessionStorage.

The client MUST still attempt to emit on initial load (best-effort).

8.3 UTM Read + Normalization (Normative)

On each tracked page load, the client MUST:

read utm_campaign, utm_medium, utm_source from the URL query string

if missing/blank, set each to "unknown"

Rules:

The client MUST NOT attempt to resolve utm_source into a canonical registry id.

The client SHOULD lowercase utm_source and utm_medium before sending.

8.4 CTA Click Logging (Normative)

On CTA click, the client MUST:

emit cta_click

set store to the correct value (ios_app_store | google_play | web | unknown)

proceed with navigation regardless of tracking outcome

Idempotency:

The client SHOULD generate a fresh client_event_id (UUID) for each cta_click.

The client MAY also send client_event_id for page_view if desired.

9. Privacy & Identity Boundary (Hard Rules)

The page MUST NOT:

collect names, emails, or phone numbers via tracking

collect or store IP addresses

fingerprint devices

reference authentication state

attempt identity correlation after app install

store identifiers in cookies

use third-party tracking scripts

10. Failure Handling (Normative)

If tracking fails (network error, validation error, rate limit):

the page MUST still load normally

CTA buttons MUST still function

no user-visible error may be shown

the client MAY log to console for debugging in non-production environments

11. Non-Goals (Explicit)

This contract does NOT support:

install attribution

behavioral analytics or funnels

retargeting or advertising

cross-surface identity tracking

A/B testing infrastructure

12. Success Criteria

This contract is successful if Kinly can reliably answer:

how many people accessed each marketing page

which CTA buttons were clicked

which campaigns and sources are most effective

…without compromising user trust.

13. Guiding Principle

Measure lightly. Respect privacy. Start simple.