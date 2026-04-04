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

## 1. Purpose

Define the contract for offline audio packs (ZIP files), the version config, and the audio manifest used by the withYou Flutter app.

See also: [withyou_audio_asset_delivery_v1.md](withyou_audio_asset_delivery_v1.md)

## 2. Offline audio pack contract

### 2.1 Static ZIP hosting path

- `/withyou/audio/{language}/core.zip`

Examples:

- `/withyou/audio/en/core.zip`
- `/withyou/audio/zh/core.zip`
- `/withyou/audio/ko/core.zip`

### 2.2 ZIP contents

Each ZIP MUST contain:

| Entry | Description |
|---|---|
| `metadata.json` | Pack metadata (version, language, file listing) |
| `presence/` | Presence scenario audio files |
| `social_pull/` | Social-pull scenario audio files |
| `exit_pressure/` | Exit-pressure scenario audio files |

Scenario directories MAY contain one clip or a staged sequence.

Recommended shape:

| Entry | Description |
|---|---|
| `{scenario}/primary.m4a` | Single-clip scenario asset |
| `{scenario}/stage_1.m4a` | Timed-sequence first clip |
| `{scenario}/stage_2.m4a` | Timed-sequence second clip |
| `{scenario}/stage_3.m4a` | Timed-sequence third clip |

Example:

- `zh/social_pull/stage_1.m4a`
- `zh/social_pull/stage_2.m4a`
- `zh/social_pull/stage_3.m4a`

The app MUST treat the scenario directory as the stable lookup key and MUST NOT assume every scenario has the same number of clips.

### 2.3 Important rule

The app MUST NOT guess file structure from the web route alone. It MUST use the audio manifest plus pack metadata to know which scenarios exist and how many clips each scenario contains.

## 3. Tracked download flow

The app MUST NOT request the static ZIP URL directly if durable counting matters.

Flow:

1. App reads `/withyou/config/audio-manifest.json`
2. App requests tracked route: `/withyou/download/audio/{language}`
3. Vercel logs durable event → redirects to `/withyou/audio/{language}/core.zip`
4. App downloads and extracts ZIP
5. App caches locally for offline playback

See: [contracts/api/kinly/withyou/pack_download_tracking_v1.md](../../../api/kinly/withyou/pack_download_tracking_v1.md)

## 4. Version config

Path: `/withyou/config/version.json`

Purpose:

- App version check
- Force update logic

Suggested shape:

```json
{
  "minimum_version": "1.0.0",
  "latest_version": "1.0.0",
  "force_update": false
}
```

## 5. Audio manifest

Path: `/withyou/config/audio-manifest.json`

Purpose:

- List available pack languages
- Map language to tracked download route
- Declare pack version
- Declare scenario clip configuration
- Define fallback rules

Suggested shape:

```json
{
  "packs": [
    {
      "language": "en",
      "pack_version": "1.0",
      "download_url": "/withyou/download/audio/en",
      "size_bytes": null,
      "checksum": null,
      "bundled": false,
      "scenarios": {
        "uber": {
          "mode": "single_clip",
          "clips": ["primary"]
        },
        "social_pull": {
          "mode": "timed_sequence",
          "clips": ["stage_1", "stage_2", "stage_3"]
        }
      }
    },
    {
      "language": "zh",
      "pack_version": "1.0",
      "download_url": "/withyou/download/audio/zh",
      "size_bytes": null,
      "checksum": null,
      "bundled": false,
      "scenarios": {
        "uber": {
          "mode": "single_clip",
          "clips": ["primary"]
        },
        "social_pull": {
          "mode": "timed_sequence",
          "clips": ["stage_1", "stage_2", "stage_3"]
        }
      }
    },
    {
      "language": "ko",
      "pack_version": "1.0",
      "download_url": "/withyou/download/audio/ko",
      "size_bytes": null,
      "checksum": null,
      "bundled": false,
      "scenarios": {
        "uber": {
          "mode": "single_clip",
          "clips": ["primary"]
        }
      }
    }
  ],
  "default_language": "en"
}
```

`download_url` points to the tracked download route, keeping tracking centralized. `bundled` flag is for future use when packs MAY ship inside the app binary. `scenarios` defines the scenario key, playback mode, and required clip identifiers inside the extracted pack.

## 6. Preview audio (web only)

Preview audio is a marketing/demo asset, NOT the full product pack.

Rule: preview assets MAY be either a single clip or a small staged sequence depending on scenario needs.

Suggested paths:

- `/withyou/assets/audio-preview/{language}/{scenario}/primary.m4a`
- `/withyou/assets/audio-preview/{language}/{scenario}/stage_1.m4a`
- `/withyou/assets/audio-preview/{language}/{scenario}/stage_2.m4a`
- `/withyou/assets/audio-preview/{language}/{scenario}/stage_3.m4a`

Preview audio MUST remain separate from offline packs.

## 7. Flutter app responsibilities

The app owns:

- Reading audio-manifest config
- Choosing language pack
- Resolving scenario clip sets from manifest metadata
- Requesting tracked pack download route
- Downloading ZIP
- Extracting ZIP
- Local caching
- Offline playback

## 8. Non-goals (v1)

- No streaming audio
- No in-app audio hosting via Supabase
- No video
