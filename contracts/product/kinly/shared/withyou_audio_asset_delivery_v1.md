---
Domain: withYou
Capability: Audio Asset Delivery
Scope: shared
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
Canonical-Id: withyou_audio_asset_delivery
Relates-To: contracts/product/kinly/shared/withyou_audio_pack_v1.md, contracts/product/kinly/web/withyou/scenario_landing_v1.md, architecture/withyou_system_overview_v1.md
See-Also: contracts/api/kinly/withyou/pack_download_tracking_v1.md
---

# withYou Audio Asset Delivery Contract v1.0

## Purpose

Define the canonical asset model for withYou audio so the same scenario content
can be published to:

- public web preview assets on Vercel
- offline app ZIP packs for Flutter
- backend-integrated tracked download flows

## Canonical Source Model

Audio content MUST be authored against the following logical identity:

- `language`
- `scenario_family`
- `clip`

Canonical key:

```text
{language}/{scenario_family}/{clip}
```

Examples:

- `en/presence/primary`
- `zh/social_pull/stage_1`
- `zh/exit_pressure/stage_3`

The canonical key MUST stay stable across all delivery surfaces.

## Delivery Surfaces

### Public web preview assets

Public path:

```text
/withyou/assets/audio-preview/{language}/{scenario_family}/{clip}.m4a
```

Examples:

- `/withyou/assets/audio-preview/en/presence/primary.m4a`
- `/withyou/assets/audio-preview/zh/social_pull/stage_2.m4a`
- `/withyou/assets/audio-preview/zh/exit_pressure/stage_1.m4a`

Rules:

- preview assets MUST be individually addressable static files
- preview assets MUST NOT require ZIP extraction
- preview assets MAY expose only the subset needed for marketing/testing

### Offline app pack assets

Download route:

```text
/withyou/download/audio/{language}
```

Resolved ZIP path:

```text
/withyou/audio/{language}/core.zip
```

Recommended extracted layout:

```text
metadata.json
presence/primary.m4a
social_pull/stage_1.m4a
social_pull/stage_2.m4a
social_pull/stage_3.m4a
exit_pressure/stage_1.m4a
exit_pressure/stage_2.m4a
exit_pressure/stage_3.m4a
```

Rules:

- ZIP contents MUST be language-scoped already
- ZIP contents SHOULD NOT repeat the language as an inner folder
- extracted lookup keys MUST remain `{scenario_family}/{clip}`

## Scenario Playback Modes

| Family | Mode | Required clips |
|---|---|---|
| `presence` | `single_clip` | `primary` |
| `social_pull` | `timed_sequence` | `stage_1`, `stage_2`, `stage_3` |
| `exit_pressure` | `timed_sequence` | `stage_1`, `stage_2`, `stage_3` |

UI labels MAY vary by route and by language, but canonical clip ids MUST remain
stable.

## Public Route Mapping

Public route slugs are not canonical asset keys. They map onto families:

- `/withyou/uber` -> `presence`
- `/withyou/walk-home` -> `presence`
- `/withyou/bus-stop` -> `presence`
- `/withyou/party-exit` -> `social_pull`
- `/withyou/date-fading` -> `social_pull`
- `/withyou/new-place` -> `social_pull`
- `/withyou/trapped-conversation` -> `exit_pressure`
- `/withyou/they-wont-let-me-leave` -> `exit_pressure`
- `/withyou/bad-date-exit` -> `exit_pressure`

## Manifest Contract

The audio manifest MUST declare:

- language pack identity
- tracked download route
- canonical family availability
- playback mode
- clip ids

Web preview UI and Flutter playback MUST consume this canonical model instead of
re-deriving file names from route slugs.

## Backend Handoff Contract

Backend consumers need only the tracked download boundary, not public preview
asset hosting.

Backend-facing requirements:

- backend MUST accept tracked download events per `language`
- backend MAY record `pack_version`, `platform`, and `app_version`
- backend MUST NOT need to understand public preview URLs
- backend SHOULD treat family and clip naming as product-owned metadata

## Non-Goals

- no requirement that preview assets equal full app-pack coverage
- no requirement that backend stores public asset URLs
- no requirement that public route slugs appear in the manifest
