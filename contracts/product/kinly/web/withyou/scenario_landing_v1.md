---
Domain: withYou
Capability: Scenario Landing
Scope: frontend
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
---

# Contract: withYou Scenario Landing Page Template

## Purpose

All scenario pages under `/withyou/{scenario}` MUST use one shared landing-page template. The template receives scenario-specific config and renders the same structural sections.

This contract defines the routing rules, language model, config shape, and required page sections for v1.

See also: [../../shared/withyou_audio_asset_delivery_v1.md](../../shared/withyou_audio_asset_delivery_v1.md)

---

## Canonical Public Routes

| Route               | Description                           |
|----------------------|---------------------------------------|
| `/withyou`           | Entry point — redirects to default scenario |
| `/withyou/uber`      | Uber scenario landing                 |
| `/withyou/walk-home` | Walk-home scenario landing            |
| `/withyou/bus-stop`  | Bus-stop scenario landing             |

Public routes represent scenario only. Language is handled inside the page as state.

---

## `/withyou` Redirect Behaviour

On visit:

1. Detect preferred language.
2. If Chinese → set default page language to `zh`.
3. Otherwise → set default page language to `en`.
4. Redirect to `/withyou/uber`.

No country-based route structure. No locale-based route structure.

---

## Language Model

Supported web languages: `en`, `zh`.

Resolution order:

1. Query param `?lang=zh`
2. Stored preference
3. Browser language
4. Fallback to `en`

Language switching MUST NOT change the route. It MUST update the page in place.

---

## Scenario Config Shape

Each scenario config MUST define:

| Field               | Type                          | Required | Description                                      |
|---------------------|-------------------------------|----------|--------------------------------------------------|
| `slug`              | `string`                      | yes      | Scenario identifier (e.g. `uber`)                |
| `title`             | `Record<Language, string>`    | yes      | Localized scenario title                         |
| `problem_framing`   | `Record<Language, string>`    | yes      | Localized problem-framing copy                   |
| `preview_experience`| `PreviewExperienceConfig`     | yes      | Per-scenario preview interaction model            |
| `app_links`         | `{ appStore: string; googlePlay: string }` | yes | App Store + Google Play URLs          |
| `qr_metadata`       | `object`                      | no       | Optional QR metadata                             |
| `lead_cta_variant`  | `string`                      | no       | Optional lead CTA variant                        |

---

## Required Page Sections

### Problem Framing

Localized text explaining the discomfort or situation. Rendered from `problem_framing` in the scenario config.

### Audio Preview

The shared landing template MUST support two preview experience types:

- `single_clip`: one immediate preview action for simple scenarios.
- `timed_sequence`: multiple staged clips with explicit controls and optional auto-advance.

`PreviewExperienceConfig` shape:

```ts
type PreviewExperienceConfig =
  | {
      type: 'single_clip';
      clips: {
        primary: Record<Language, string>;
      };
    }
  | {
      type: 'timed_sequence';
      clips: {
        immediate: Record<Language, string>;
        plus_2_min: Record<Language, string>;
        plus_4_min: Record<Language, string>;
      };
      controls: {
        immediate_label: Record<Language, string>;
        plus_2_min_label: Record<Language, string>;
        plus_4_min_label: Record<Language, string>;
        plus_4_min_auto: boolean;
      };
    };
```

Rules:

- Uber-style scenarios SHOULD use `single_clip`.
- Social-pressure exit scenarios MAY use `timed_sequence`.
- Preview clips MUST remain marketing assets, separate from offline app packs.
- Preview clips MUST be statically addressable by scenario, language, and stage.

Suggested asset paths:

- Single clip: `/withyou/assets/audio-preview/{language}/{scenario}/primary.m4a`
- Timed sequence:
  - `/withyou/assets/audio-preview/{language}/{scenario}/immediate.m4a`
  - `/withyou/assets/audio-preview/{language}/{scenario}/plus_2_min.m4a`
  - `/withyou/assets/audio-preview/{language}/{scenario}/plus_4_min.m4a`

Examples:

- Uber:
  - `/withyou/assets/audio-preview/en/uber/primary.m4a`
- Party exit:
  - `/withyou/assets/audio-preview/zh/social_pull/immediate.m4a`
  - `/withyou/assets/audio-preview/zh/social_pull/plus_2_min.m4a`
  - `/withyou/assets/audio-preview/zh/social_pull/plus_4_min.m4a`

### App Links

- App Store link.
- Google Play link.
- Optional waitlist CTA if store links are not live for a market.

### Lead CTA

Either inline form or link to `/withyou/get`.

---

## QR Code Targeting

QR codes MUST point directly to canonical scenario routes:

- `/withyou/uber`
- `/withyou/walk-home`
- `/withyou/bus-stop`

Optional language targeting via query param: `/withyou/uber?lang=zh`.

Static QR creation is acceptable in v1. Future QR utilities MAY be provided by Kinly backend.

---

## Non-Goals (v1)

- No locale-based route tree.
- No video.
- No authenticated sessions.
