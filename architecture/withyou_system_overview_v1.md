---
Domain: withYou
Capability: System Overview
Scope: platform
Artifact-Type: architecture
Stability: evolving
Status: draft
Version: v1.0
---

# withYou System Overview (v1)

## Purpose

withYou helps users manage uncomfortable situations through believable audio call flows. The system spans two surfaces:

- **Web** (`go.makinglifeeasie.com/withyou`): explains scenarios, provides audio previews, drives app installs, captures leads, and supports QR-based entry.
- **Flutter app**: downloads offline audio packs, caches them locally, and plays them offline.

## Architecture Layers

### 1. Vercel — Public Delivery Layer

Owns all public-facing content and static hosting:

- Public routes under `/withyou`
- Shared landing-page template rendering
- Language switching
- Preview audio assets (static)
- Static app config files (`version.json`, `audio-manifest.json`)
- Static offline ZIP pack hosting
- Tracked download entry routes that redirect to static ZIPs

### 2. Kinly Backend — Narrow Shared Utility

Owns only durable business event persistence:

- Lead persistence (`leads_upsert` RPC → `public.leads`)
- Durable pack-download tracking
- Future QR generation / metadata utilities

The Kinly backend MUST NOT become the main withYou backend. It is reused narrowly for shared utilities only.

### 3. Flutter App — Offline Pack Lifecycle

Owns the full offline audio experience:

- Reading `audio-manifest.json` config
- Choosing language pack
- Requesting tracked pack download route
- Downloading ZIP from redirect target
- Extracting ZIP to local storage
- Local caching
- Offline playback

## Ownership Boundaries

| Owner | Responsibilities |
|---|---|
| Vercel | Public routes, shared landing template, language switching, preview audio, static config, static ZIPs, tracked download routes |
| Kinly backend | Durable lead records, durable pack-download records, future QR utilities |
| Flutter app | Language-pack selection, tracked download request, ZIP download + extraction, local cache, offline playback |

## Key Architectural Rules

1. **Scenario defines the page** — each scenario (e.g. `uber`, `walk-home`, `bus-stop`) MUST have its own landing route.
2. **Scenario and language define the audio experience** — scenario defines the landing route and clip model; language defines which localized pack is downloaded. Language MUST NOT alter the route structure.
3. **Preview audio is separate from offline packs** — preview clips are Vercel static assets; offline packs are downloaded ZIPs. They MUST NOT be conflated.
4. **Static assets stay on Vercel** — audio files, config JSON, and ZIPs MUST be served from Vercel, not Supabase Storage.
5. **Durable business events go to Supabase** — lead captures and pack-download events MUST be persisted via Kinly backend RPCs.
6. **Kinly backend is reused narrowly, not broadly** — only lead persistence, download tracking, and future QR utilities. No withYou-specific business logic SHOULD live in the Kinly backend.

## Non-Goals

- No locale-based route tree (language is a UI toggle, not a route segment)
- No video in v1
- No static audio hosting in Supabase
- No full withYou backend in Kinly

## Public Route Map

| Route | Purpose |
|---|---|
| `/withyou` | Redirect → `/withyou/uber` (default scenario) |
| `/withyou/get` | Lead capture |
| `/withyou/uber` | Scenario landing |
| `/withyou/walk-home` | Scenario landing |
| `/withyou/bus-stop` | Scenario landing |
| `/withyou/download/audio/{language}` | Tracked download -> redirect to `/withyou/audio/{language}/core.zip` |
| `/withyou/config/version.json` | App version config |
| `/withyou/config/audio-manifest.json` | Available packs manifest |

## Data Flow Summary

### Web visitor → preview experience

```
Web visitor → Vercel scenario page → preview audio (Vercel static) → app store links
```

### Web visitor → lead capture

```
Web visitor → /withyou/get → leads_upsert RPC → Supabase public.leads
```

### Flutter app → offline pack download

```
Flutter app
  → /withyou/config/audio-manifest.json
  → language pack selection
  → /withyou/download/audio/{lang}
  → Vercel route handler
  → Supabase event write (pack-download record)
  → redirect to /withyou/audio/{lang}/core.zip (static ZIP)
```
