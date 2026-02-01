---
Domain: Marketing Ops
Capability: qr_generator
Scope: frontend
Artifact-Type: contract
Stability: stable
Status: draft
Version: v1.0
Audience: internal
Last updated: 2026-01-31
---

# Contract - QR Generator Hub (Client-only) - v1.0

## 1. Purpose
Define a client-only QR Generator Hub for Kinly marketing operations that:
- Loads a canonical QR catalog (JSON) describing multiple QR variants (UTM-aligned) from a single static asset.
- Supports preloading a specific QR (or filter set) via URL query params.
- Renders a scan-safe QR preview (QR-only by default) with an optional caption card explaining the Kinly value for the selected scenario.
- Exports assets in-browser: PNG (QR-only), PNG with caption card, SVG, and ZIP bulk export (no server/API route).
- Enforces QR safety constraints (scan reliability) and deterministic filenames.

Decisions locked for v1:
- Default preview/export style is a single shared variant; no per-item styling.
- UI is read-only (all labels/URLs/value props come from catalog; no editing in UI).
- Preview may respect dark mode for UI only; QR rendering must remain scan-safe and never invert colors.

Non-goals: no server-side generation, no authenticated storage/upload/persistence, no dynamic tracking calls from this tool.

## 2. Surfaces
### 2.1 Route
`/tools/qr` - intended to be internal/unlisted (no nav link on public marketing pages).

### 2.2 Preload / Deep-link Query Params
Supported params: `id`, `purpose`, `plan`, `pageKey`, `utm_campaign`, `utm_source`.
Rules:
- If `id` is present, it takes precedence over filters.
- Unknown params are dropped on first state write.
- Values MUST be URI-encoded; matching is case-insensitive for filters/UTMs.
- When writing the URL, order params as: `id`, `purpose`, `plan`, `pageKey`, `utm_campaign`, `utm_source`.
- On selection, set `id=<qr_id>` and optionally clear filters.
Examples: `/tools/qr?id=sg_new_place_telegram`, `/tools/qr?purpose=international&plan=market&utm_campaign=singapore_working_holiday&utm_source=telegram`.

## 3. Data Contract: qr_catalog.json
### 3.1 Location
Load one JSON document from `public/qr/qr_catalog.json`.

### 3.2 Catalog Root Schema
```ts
type QrCatalogV1 = {
  version: "v1.0";
  generatedAt: string; // ISO datetime
  items: QrItemV1[];
};
```

### 3.3 Item Schema (QrItemV1)
```ts
type QrItemV1 = {
  // Identity
  qr_id: string; // stable unique key; snake_case; used for deep-linking + filenames

  // Audience grouping (mirrors spreadsheet)
  purpose: string;
  plan: string;
  pageKey: string;

  // UTM fields (explicit for filtering/reporting sanity)
  utm_campaign: string;
  utm_medium: "qr";
  utm_source: string;

  // Fully canonical destination URL (already assembled)
  url: string; // https://... must include utm_* query params

  // Read-only caption metadata (used for optional caption card)
  label: {
    line1: string; // max 40 chars recommended
    line2: string; // max 40 chars recommended
    helper?: string; // optional max 60 chars recommended
  };

  value_prop: string; // short sentence explaining the Kinly value for this scenario

  notes?: string;
};
```

### 3.4 Validation Rules (Client-side)
On load, validate each item; invalid items are excluded and listed in a non-blocking warning UI.
- Catalog `version` MUST equal client-supported `v1.0`; mismatch disables preview/exports and shows an inline error. If `generatedAt` or ETag changes mid-session, revalidate and reload.
- `qr_id` MUST be snake_case, unique case-insensitively, and lowercased for filtering/filenames.
- `url` MUST be https and host MUST be in the allowlist {`go.makinglifeeasie.com`} (extendable); duplicates are invalid.
- `url` MUST contain `utm_campaign`, `utm_medium=qr`, and `utm_source` query params.
- `utm_medium` MUST equal `qr`; `utm_campaign` and `utm_source` SHOULD be lowercased for matching.
- `label.line1` and `label.line2` MUST be non-empty.
- `value_prop` MUST be non-empty text <= 160 characters.

### 3.5 Error States
- Fetch/parse failure: show inline error, disable preview/actions.
- Version/host/validation failure: list invalid items; if all items invalid, show empty state and disable exports.

## 4. Default Design Variant (Single Style)
```
logoAssetPath = "/public/logo-kinly.svg"
foreground = "#0B0B0B"
background = "#FFFFFF"
errorCorrection = "H"
quietZoneModules = 4
logoScale = 0.18 // clamp 0.15-0.20
exportPngSize = 1024

// Caption card
cardWidth = 1024 // px
cardPadding = 72 // px (applied around QR+text container)
cardBackground = "#FFFFFF"
cardTextColor = "#0B0B0B"
cardValuePropMaxChars = 160
cardFontFamily = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
cardFontsEmbed = false // no external fetch
cardLayout = "QR left, text right" on desktop; stack on narrow screens
```
If the logo fails to load: render/export without logo, show inline warning, and set `logoApplied=false` in manifest entries.

## 5. QR Rendering Rules (Scan Safety)
- Use error correction H and at least 4-module quiet zone.
- Dark modules on light background; never invert colors or use transparent backgrounds.
- Center logo sized 15-20% of QR width with solid background knockout to protect modules.
- Contrast: compute WCAG relative luminance ratio of foreground vs background. Block exports if ratio < 5:1; show warning for 5-7:1; no warning >= 7:1.

## 6. Preview vs Export Theme Rules
- UI MAY adapt to system light/dark mode; exported assets MUST NOT vary by theme.
- Preview shows QR inside a light, opaque scan plate (e.g., background `#FFFFFF`) preserving quiet zone; same colors/layout as export.

## 7. UI Behavior (Read-only)
- Filter/selection panel: purpose, plan, pageKey, utm_campaign, utm_source; search by `qr_id` or label text.
- Preview panel: QR preview (square, scan plate) plus read-only metadata (`qr_id`, `url`, label lines, value_prop).
- Caption card preview toggle: default ON for preview; toggle controls whether PNG export includes card; SVG remains QR-only.
- Actions: Copy URL, Download SVG, Download PNG (QR-only), Download PNG with caption card, Bulk export ZIP (filtered set).
- Read-only: no editing of URLs, labels, value_prop, or UTM fields; outputs mirror catalog.
- Accessibility: all controls keyboard reachable with `aria-label`/`aria-describedby`; focus order matches visual order; selection updates announced via `aria-live`.

## 8. Export Contract (Client-only)
### 8.1 Single-Item Exports
- SVG: `<qr_id>.svg`; embeds QR + logo (if available) + opaque background; quiet zone baked in; sRGB profile; explicit width/height/viewBox; no caption card.
- PNG (QR-only): `<qr_id>.png`; 1024x1024; opaque background; quiet zone included; sRGB profile; includes logo if available.
- PNG with caption card: `<qr_id>_card.png`; 1024px width canvas with QR and text laid out per card layout; uses `label.line1`, `label.line2`, optional `helper`, and `value_prop`; sRGB profile; QR rendering identical to QR-only asset.
- Copy URL: copies `item.url` exactly (no mutation).

### 8.2 Bulk Export ZIP (Filtered Set)
- Contents: `manifest.json` + one SVG, one PNG, and one PNG card per item, filenames `<qr_id>.svg`, `<qr_id>.png`, `<qr_id>_card.png`.
- Ordering: manifest and ZIP entries sorted by `qr_id` ascending for determinism.
- Limit: default `MAX_BULK = 250`; block with clear message if filtered count exceeds limit.
- manifest schema:
```ts
type BulkExportManifestV1 = {
  version: "v1.0";
  exportedAt: string; // ISO datetime
  count: number;
  filters: Record<string, string>;
  items: Array<{
    qr_id: string;
    url: string;
    purpose: string;
    plan: string;
    pageKey: string;
    utm_campaign: string;
    utm_medium: "qr";
    utm_source: string;
    label: { line1: string; line2: string; helper?: string };
    value_prop: string;
    designApplied: {
      logoAssetPath: string;
      logoApplied: boolean;
      foreground: string;
      background: string;
      errorCorrection: "H";
      quietZoneModules: number;
      logoScale: number;
      exportPngSize: number;
      colorProfile: "sRGB";
      cardLayout: string;
    };
    files: { svg: string; png: string; png_card: string };
  }>;
};
```
- Implementation: client-only ZIP generation (e.g., JSZip); yield between items to avoid UI freeze.

## 9. Performance & Reliability
- Catalog load SHOULD be browser-cached; validate `version` on every load.
- Rendering is deterministic; only network fetches are catalog and logo asset.
- If logo fails, exports still succeed without logo.

## 10. Security / Access Expectations
- Route public but unlisted; MUST set `meta name="robots" content="noindex,nofollow"` and exclude from sitemap/robots.txt.
- No secrets; catalog only contains public marketing URLs.

## 11. Test Cases (Acceptance)
- Load `/tools/qr` with no params: catalog loads; filters empty; user can select an item.
- Load with valid `id`: item selected; preview renders.
- Load with invalid `id`: loads with no selection; warning shown.
- Load with filters: filters preselected; matching list shown; URL rewritten with ordered params.
- Catalog version mismatch or parse failure: error shown; exports disabled.
- Host allowlist failure: item excluded and reported.
- Validation: missing `utm_medium=qr`, duplicate `qr_id` (case-insensitive), duplicate `url`, missing labels, or missing `value_prop` are excluded and reported.
- Download SVG/PNG/PNG card: filenames match expected; QR-only PNG is 1024x1024; card PNG shows labels + value_prop; quiet zone present; sRGB profile; scans to expected URL.
- Bulk export: ZIP contains manifest + correct set; entries sorted by `qr_id`; limit >250 blocks with message; card PNG present per item.
- Contrast <5:1 blocks export; 5-7:1 warns.
- Logo failure: exports without logo; manifest records `logoApplied=false`; warning visible.
- Zero matches after filters: empty state; exports disabled.
- Accessibility: keyboard-only flow completes actions; screen reader announces selection changes; caption card toggle is reachable and labeled.
