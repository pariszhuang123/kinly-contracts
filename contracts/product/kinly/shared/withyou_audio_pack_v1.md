---
Domain: withYou
Capability: Audio Pack and Config
Scope: shared
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
---

# withYou Audio Pack and Config Contract v1.0

## Purpose

Define the contract for offline audio packs (ZIP files), version config, and
audio manifest used by the withYou Flutter app.

See also: [withyou_audio_asset_delivery_v1.md](withyou_audio_asset_delivery_v1.md)

## Canonical Scenario Families

Offline packs are keyed by canonical families, not public route slugs:

- `presence`
- `social_pull`
- `exit_pressure`

## Static ZIP Hosting Path

- `/withyou/audio/{language}/core.zip`

Examples:

- `/withyou/audio/en/core.zip`
- `/withyou/audio/zh/core.zip`
- `/withyou/audio/ko/core.zip`

## ZIP Contents

Each ZIP MUST contain:

| Entry | Description |
|---|---|
| `metadata.json` | Pack metadata (version, language, file listing) |
| `presence/` | Presence-family audio |
| `social_pull/` | Social-pull audio |
| `exit_pressure/` | Exit-pressure audio |

Recommended shape:

| Entry | Description |
|---|---|
| `{family}/primary.m4a` | Single-clip family asset |
| `{family}/stage_1.m4a` | Timed-sequence first clip |
| `{family}/stage_2.m4a` | Timed-sequence second clip |
| `{family}/stage_3.m4a` | Timed-sequence third clip |

Rules:

- `presence` MUST expose `primary`
- `social_pull` MUST expose `stage_1`, `stage_2`, `stage_3`
- `exit_pressure` MUST expose `stage_1`, `stage_2`, `stage_3`
- app lookup MUST use canonical family and clip ids, not public route slugs

## Tracked Download Flow

1. App reads `/withyou/config/audio-manifest.json`
2. App requests `/withyou/download/audio/{language}`
3. Vercel logs the durable event and redirects to `/withyou/audio/{language}/core.zip`
4. App downloads and extracts ZIP
5. App caches locally for offline playback

See: [contracts/api/kinly/withyou/pack_download_tracking_v1.md](../../../api/kinly/withyou/pack_download_tracking_v1.md)

## Version Config

Path: `/withyou/config/version.json`

Suggested shape:

```json
{
  "minimum_version": "1.0.0",
  "latest_version": "1.0.0",
  "force_update": false
}
```

## Audio Manifest

Path: `/withyou/config/audio-manifest.json`

The manifest MUST:

- list downloadable pack languages
- map language to tracked download route
- declare pack version
- declare canonical families and clip ids
- declare default preview language
- declare which languages are exposed in public preview UI

Suggested shape:

```json
{
  "packs": [
    {
      "language": "en",
      "pack_version": "1.0.0",
      "download_url": "/withyou/download/audio/en",
      "bundled": false,
      "scenarios": {
        "presence": {
          "mode": "single_clip",
          "clips": ["primary"]
        },
        "social_pull": {
          "mode": "timed_sequence",
          "clips": ["stage_1", "stage_2", "stage_3"]
        },
        "exit_pressure": {
          "mode": "timed_sequence",
          "clips": ["stage_1", "stage_2", "stage_3"]
        }
      }
    }
  ],
  "default_language": "en",
  "preview_languages": ["en", "zh"]
}
```

`ko` MAY appear in `packs` as downloadable-only. It does not need to be exposed
in public web preview controls.

## Preview Audio

Preview audio is a marketing/demo asset, not the full product pack.

Suggested paths:

- `/withyou/assets/audio-preview/{language}/presence/primary.m4a`
- `/withyou/assets/audio-preview/{language}/social_pull/stage_1.m4a`
- `/withyou/assets/audio-preview/{language}/social_pull/stage_2.m4a`
- `/withyou/assets/audio-preview/{language}/social_pull/stage_3.m4a`
- `/withyou/assets/audio-preview/{language}/exit_pressure/stage_1.m4a`
- `/withyou/assets/audio-preview/{language}/exit_pressure/stage_2.m4a`
- `/withyou/assets/audio-preview/{language}/exit_pressure/stage_3.m4a`

Preview audio MUST remain separate from offline packs.

## Flutter App Responsibilities

The app owns:

- reading manifest config
- choosing language pack
- resolving canonical families and clip ids from manifest metadata
- requesting tracked pack download route
- downloading ZIP
- extracting ZIP
- local caching
- offline playback

## Non-Goals

- no streaming audio
- no in-app audio hosting via Supabase
- no requirement that public route slugs appear inside the offline pack
