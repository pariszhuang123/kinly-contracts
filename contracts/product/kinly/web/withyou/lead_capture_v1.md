---
Domain: withYou
Capability: Lead Capture
Scope: frontend
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
Canonical-Id: withyou_lead_capture
Relates-To: architecture/withyou_system_overview_v1.md, contracts/product/kinly/web/withyou/scenario_landing_v1.md
Depends-On: contracts/api/kinly/withyou/leads_amendment_v1.md, contracts/product/kinly/web/growth/interest_capture_v1_1.md
Implemented-By: contracts/api/kinly/withyou/leads_amendment_v1.md
---

# Contract — withYou Lead Capture v1.0

## Meta

- **Domain**: withYou
- **Capability**: Lead Capture
- **Surface**: withYou Web (`/withyou/get`)
- **Status**: Draft
- **Owners**: Web, DB
- **Last updated**: 2026-04-04

## Purpose

`/withyou/get` is a dedicated lead-capture page for withYou. It collects early-access interest using the same infrastructure as the existing Kinly interest capture.

## Required Fields

- `email`
- `country_code` (ISO 3166-1 alpha-2)
- `ui_locale` (BCP-47)

## Submission Behavior

Submits to the existing Kinly RPC `public.leads_upsert_v1` using:

- `p_source = 'withyou_web_get'`

This reuses the existing leads infrastructure documented in
[interest_capture_v1_1.md](../growth/interest_capture_v1_1.md).

## Source-Based Uniqueness Requirement

The existing `public.leads` table uses `unique(email)` via citext.

For withYou, the table MUST be updated to support source-based uniqueness:

- **Replace**: `unique(email)`
- **With**: unique index on `(email, source)`

### Conflict behavior

- Same email + same source → update existing row
- Same email + different source → allow separate row

## Source Allowlist Update

The `source` check constraint on `public.leads` MUST be updated to include `'withyou_web_get'`.

Updated allowlist:

```
kinly_web_get, kinly_dating_web_get, kinly_rent_web_get, withyou_web_get
```

## Country Note

Country is useful metadata but is NOT part of the public route model.

## UX Behavior

- Same form UX patterns as the existing Kinly interest capture.
- Detection rules (country, locale) MUST follow the same priority order defined in [interest_capture_v1_1.md](../growth/interest_capture_v1_1.md).
- Error handling MUST follow existing patterns from [interest_capture_v1_1.md](../growth/interest_capture_v1_1.md).

## Dependencies

- Requires schema migration on `public.leads` (uniqueness change + source allowlist).
- See: [leads_amendment_v1.md](../../../../api/kinly/withyou/leads_amendment_v1.md)
