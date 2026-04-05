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

All scenario pages under `/withyou/{route_slug}` MUST use one shared landing-page
template. The template receives route-specific config and resolves preview
playback from the canonical scenario family.

See also: [../../shared/withyou_audio_asset_delivery_v1.md](../../shared/withyou_audio_asset_delivery_v1.md)

## Canonical Public Routes

| Route | Canonical family |
|---|---|
| `/withyou/uber` | `presence` |
| `/withyou/walk-home` | `presence` |
| `/withyou/bus-stop` | `presence` |
| `/withyou/party-exit` | `social_pull` |
| `/withyou/date-fading` | `social_pull` |
| `/withyou/new-place` | `social_pull` |
| `/withyou/trapped-conversation` | `exit_pressure` |
| `/withyou/they-wont-let-me-leave` | `exit_pressure` |
| `/withyou/bad-date-exit` | `exit_pressure` |

`/withyou` MUST redirect to `/withyou/uber`.

## Language Model

Supported public preview languages: `en`, `zh`.

Resolution order:

1. query param `?lang=...`
2. stored preference
3. browser language
4. fallback to `en`

Language switching MUST NOT change the route slug.

## Config Model

Each route config MUST define:

| Field | Type | Required | Description |
|---|---|---|---|
| `slug` | `string` | yes | Public route slug |
| `scenario_family` | `presence \| social_pull \| exit_pressure` | yes | Canonical audio family key |
| `title` | `Record<Language, string>` | yes | Localized route title |
| `problem_framing` | `Record<Language, string>` | yes | Localized route framing |
| `what_they_need` | `Record<Language, string>` | yes | Localized need copy |
| `example_outcome` | `Record<Language, string>` | yes | Localized outcome copy |
| `preview_mode` | `single_clip \| timed_sequence` | yes | Derived from scenario family |
| `timed_labels` | localized labels | no | Route-specific labels for staged families |
| `lead_cta` | localized text | yes | CTA to `/withyou/get` |

## Canonical Family Rules

| Family | Preview mode | Clip ids |
|---|---|---|
| `presence` | `single_clip` | `primary` |
| `social_pull` | `timed_sequence` | `stage_1`, `stage_2`, `stage_3` |
| `exit_pressure` | `timed_sequence` | `stage_1`, `stage_2`, `stage_3` |

Route-specific UI labels MAY vary, but canonical clip ids MUST remain stable.

## Required Page Sections

- route title and problem framing
- audio preview
- what the user needs
- example outcome
- app download CTAs
- lead CTA to `/withyou/get`

## Audio Preview Rules

Preview assets MUST be resolved by family, not by route slug:

- `/withyou/assets/audio-preview/{language}/{scenario_family}/primary.m4a`
- `/withyou/assets/audio-preview/{language}/{scenario_family}/stage_1.m4a`
- `/withyou/assets/audio-preview/{language}/{scenario_family}/stage_2.m4a`
- `/withyou/assets/audio-preview/{language}/{scenario_family}/stage_3.m4a`

Rules:

- `presence` pages render one primary play action
- `social_pull` and `exit_pressure` pages render staged controls for
  `stage_1..3`
- preview clips remain marketing/demo assets, separate from offline packs

## QR Code Targeting

QR codes MUST point directly to canonical public routes. Language targeting MAY
use query params, for example `/withyou/uber?lang=zh`.

## Non-Goals

- no locale-based route tree
- no authenticated sessions
- no requirement that public route slugs equal canonical family keys
