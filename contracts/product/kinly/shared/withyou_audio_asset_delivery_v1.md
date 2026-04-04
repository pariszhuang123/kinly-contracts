---
Domain: withYou
Capability: Audio Asset Delivery
Scope: shared
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
---

# withYou Audio Asset Delivery Contract v1.0

## 1. Purpose

Define the canonical asset model for withYou audio so the same scenario content
can be published to:

- public web preview assets on Vercel
- offline app ZIP packs for Flutter
- backend-integrated tracked download flows

This contract exists to keep naming, language coverage, and scenario/stage
mapping stable across web, app, and backend implementations.

## 2. Canonical source model

Audio content MUST be authored against the following logical identity:

- `language`
- `scenario`
- `clip`

Canonical key:

```text
{language}/{scenario}/{clip}
```

Examples:

- `en/uber/primary`
- `zh/social_pull/stage_1`
- `zh/social_pull/stage_2`
- `zh/social_pull/stage_3`

The canonical key MUST stay stable across all delivery surfaces.

## 3. Delivery surfaces

The same logical audio set MAY be published into two different delivery forms.

### 3.1 Public web preview assets

Purpose:

- marketing landing pages
- instant browser playback
- scenario testing before install

Public Vercel path:

```text
/withyou/assets/audio-preview/{language}/{scenario}/{clip}.m4a
```

Examples:

- `/withyou/assets/audio-preview/en/uber/primary.m4a`
- `/withyou/assets/audio-preview/zh/social_pull/stage_1.m4a`
- `/withyou/assets/audio-preview/zh/social_pull/stage_2.m4a`
- `/withyou/assets/audio-preview/zh/social_pull/stage_3.m4a`

Rules:

- Preview assets MUST be individually addressable static files.
- Preview assets MUST NOT require ZIP extraction.
- Preview assets MAY expose only the subset needed for marketing/testing.

### 3.2 Offline app pack assets

Purpose:

- downloadable language pack for Flutter
- offline playback
- consistent clip lookup after extraction

Download route:

```text
/withyou/download/audio/{language}
```

Resolved ZIP path:

```text
/withyou/audio/{language}/core.zip
```

Recommended extracted layout inside each ZIP:

```text
metadata.json
uber/primary.m4a
social_pull/stage_1.m4a
social_pull/stage_2.m4a
social_pull/stage_3.m4a
```

Rules:

- ZIP contents MUST be language-scoped already.
- ZIP contents SHOULD NOT repeat the language as an inner folder.
- The extracted app lookup key MUST remain `{scenario}/{clip}`.

## 4. Scenario playback modes

Each scenario MUST declare one playback mode:

- `single_clip`
- `timed_sequence`

### 4.1 `single_clip`

Used for scenarios like Uber where one believable call clip is enough.

Required clip set:

- `primary`

### 4.2 `timed_sequence`

Used for scenarios like social-pressure exit where staged escalation is needed.

Required clip set:

- `stage_1`
- `stage_2`
- `stage_3`

Suggested interpretation:

- `stage_1` = immediate
- `stage_2` = 2 minutes later
- `stage_3` = 4 minutes later

UI labels MAY vary by language and product surface, but clip keys MUST remain
stable.

## 5. Language rules

Supported languages MUST be declared in the audio manifest.

Rules:

- A language MAY support only a subset of scenarios in early rollout.
- If a scenario is available in a language, all required clips for that
  scenario mode MUST exist.
- Implementations MUST NOT assume all languages have identical scenario
  coverage.

Example:

- `en` may support `uber` and `social_pull`
- `ko` may support only `uber` initially

## 6. Manifest contract

The audio manifest MUST declare:

- language pack identity
- tracked download route
- scenario availability
- playback mode
- clip ids

Suggested shape:

```json
{
  "packs": [
    {
      "language": "zh",
      "pack_version": "1.0",
      "download_url": "/withyou/download/audio/zh",
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
    }
  ],
  "default_language": "en"
}
```

## 7. Web implementation contract

The web scenario page MUST use the manifest/config model, not hardcoded
filename assumptions.

Rules:

- Web preview UI MUST map scenario config to known clip ids.
- `single_clip` pages SHOULD render one primary play action.
- `timed_sequence` pages SHOULD render staged actions such as:
  - play now
  - 2 minutes later
  - 4 minutes later
- Web MAY support auto-play scheduling metadata, but clip identity MUST remain
  based on stable clip ids.

## 8. Backend handoff contract

Backend consumers need only the tracked download boundary, not public preview
asset hosting.

Backend-facing requirements:

- backend MUST accept tracked download events per `language`
- backend MAY record `pack_version`, `platform`, and `app_version`
- backend MUST NOT need to understand public preview URLs
- backend SHOULD treat scenario/clip naming as product-owned metadata, unless a
  future analytics contract explicitly requires per-scenario or per-clip events

## 9. Build and publishing guidance

The preferred pipeline is:

1. Maintain one canonical source set per `{language}/{scenario}/{clip}`
2. Publish web preview assets as public static files
3. Publish app pack assets into per-language ZIP files
4. Generate/update `audio-manifest.json`

This allows shared source content without coupling browser playback to ZIP
delivery.

## 10. Non-goals

- No requirement that preview assets equal full app-pack coverage
- No requirement that backend stores public asset URLs
- No requirement that all languages launch with the same scenario set
