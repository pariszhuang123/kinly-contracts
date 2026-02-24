---
Domain: Links
Capability: Share links
Scope: frontend
Artifact-Type: contract
Stability: evolving
Status: active
Version: v1.4
---

# Contract - Share Links & Canonical URLs v1.4

Domain: Links  
Capability: Share Links  
Status: Active  
Registry: `contracts/contracts_registry.md`

---

## Purpose

This contract defines:
- canonical public URLs for Kinly Web
- how shared links behave across platforms
- how intent is inferred from URLs
- what share links MUST and MUST NOT do

The goal is to ensure that:
- shared links are reliable across Android, iOS, and desktop
- users are never misled about availability
- links never dead-end or auto-trigger unsafe behavior

---

## Core Principles

1. **Links are platform-neutral**
2. **Links never auto-open the app** (store redirect is allowed; app launch is not)
3. **Links never imply capability without confirmation**
4. **Join routes in supported regions MAY redirect directly to the app store**
5. **Preview routes must always resolve to a readable web page**
6. **Capability (install / join) is decided after region check**

---

## Canonical Host

All Kinly share links MUST use a canonical host:  
https://go.makinglifeeasie.com

(Future aliases may exist, but must redirect to the canonical host.)

---

## Canonical Routes

### Preview Routes (Read-only)

| Route | Purpose |
|----|--------|
| `/` | Generic Kinly landing |
| `/kinly/norms/:homePublicId` | Public house norms (if published) |
| `/fallback` | Safe fallback for invalid links |

Preview routes:
- are readable globally
- MUST NOT imply app availability
- MUST NOT initiate install or join
- MUST always resolve to a readable web page
- For norms routes, `homePublicId` is a stable public identifier; republish of
  norms content does not rotate the URL.
- House norms share/copy UX MUST use the canonical route
  `/kinly/norms/:homePublicId` as the public identity link.

---

### Join Routes (Invite-based)

| Route | Purpose |
|----|--------|
| `/kinly/join/:inviteCode` | Join a specific home |

Join routes:
- imply **intent to join**, not guaranteed success
- are capability-gated by region
- require a valid invite code

#### Join Route Behavior by Region

| Region | Behavior |
|--------|----------|
| Supported (NZ, SG, MY) | MAY redirect directly to app store (see Store-First Redirect) |
| Unsupported | MUST redirect to `/kinly/get` for interest capture |

#### Invite code format
- Exactly 6 characters
- Allowed: A–H, J–N, P–Z, 2–9
- Case-insensitive; normalized to uppercase
- Any other format MUST be treated as invalid

---

## Store-First Redirect (v1.4)

For join routes in **supported regions**, the web layer MAY redirect directly to the platform app store instead of rendering a landing page.

### Android

- Redirect to Play Store with Install Referrer:
  ```
  https://play.google.com/store/apps/details?id=com.makinglifeeasie.kinly&referrer=kinly_invite_code%3D<inviteCode>
  ```
- The referrer MUST be percent-encoded once
- The app recovers `invite_code` via Android Install Referrer API on first launch
- See `links_invite_deferred_install_v1_0.md` for app-side handling

### iOS

- Redirect to App Store:
  ```
  https://apps.apple.com/app/kinly/id<APP_ID>
  ```
- iOS does NOT support install referrers
- The invite code is NOT preserved across install
- The app MUST provide a manual entry surface ("Have an invite link?") post-install
- This is an **accepted tradeoff** documented in this contract

### What This Does NOT Do

- **Does NOT auto-open the app** — only navigates to the store
- **Does NOT bypass region gating** — redirect only happens after region check passes
- **Does NOT apply to preview routes** — those always render a readable page

---

## Share Context & Intent Inference

Intent is inferred from the route:

| Route Type | Inferred Intent |
|----------|----------------|
| Preview routes | `preview` |
| `/kinly/join/:inviteCode` | `join` |

Intent inference:
- is advisory
- MUST NOT override region gating
- MAY be used for copy or interest capture context

---

## Query Parameters

### Allowed Parameters

| Parameter | Purpose |
|---------|--------|
| `src` | Share source identifier (e.g. android, ios, web) |
| `v` | Contract or content version (optional) |
| `next` | Internal continuation path (sanitized) |

---

### Parameter Rules

- `next` MUST:
  - be an internal path only
  - be sanitized server-side
  - never allow open redirects
- Unknown parameters MUST be ignored
- Parameters MUST NOT change gating behavior

---

## Cross-Platform Share Behavior (v1.4)

### Android (Supported Region)
- Link triggers region check
- If supported: redirect to Play Store with referrer
- Does NOT auto-open app

### iOS (Supported Region)
- Link triggers region check
- If supported: redirect to App Store (no referrer)
- Invite code entered manually post-install
- Does NOT auto-open app

### Unsupported Region
- Redirect to `/kinly/get` for interest capture
- No store links shown

### Desktop
- Link opens web landing or redirects to `/kinly/get`
- Store links may be shown but desktop cannot install

---

## Deep Link Interaction

- Deep links MAY be offered via explicit user action (if landing page is rendered)
- Deep links MUST NOT be triggered automatically
- Store-first redirect does NOT trigger deep links
- Deep link mapping is governed by `links_deep_links_v1_1.md`

---

## Region Gating Interaction

This contract defers region logic to:
- links_region_gate_v1_3.md

Share links MUST:
- check region before any redirect
- never bypass region gating
- never imply install or join capability when unavailable

---

## OG Preview Requirements

All shareable routes MUST:
- provide Open Graph metadata (even if redirect follows)
- use absolute URLs for images
- avoid embedding private data
- avoid region-specific promises

OG previews MUST be:
- neutral
- informational
- non-misleading

Note: OG metadata is read by crawlers before any redirect, so redirecting routes still need valid OG tags.

---

## Failure Handling

If:
- route is unknown
- invite code is malformed
- required data is missing
- region check fails

Then:
- route to `/fallback` or `/kinly/get` as appropriate
- provide readable explanation
- never surface raw errors

---

## Security Constraints

Share links MUST NOT:
- expose internal IDs unintentionally
- embed authentication tokens
- leak private home or member data
- enable join or install without explicit user action (store redirect is explicit)
- auto-open the app

---

## Non-Goals

This contract does NOT define:
- deep link URI schemes
- mobile app routing behavior
- analytics attribution models
- SEO optimization strategies

---

## iOS Tradeoff Acknowledgment

iOS does not provide an Install Referrer mechanism. As a result:
- Invite codes cannot be automatically recovered after install
- Users must manually enter or paste the invite code
- This is an **accepted limitation** of the store-first flow
- The app provides a "Have an invite link?" entry point to mitigate friction

This tradeoff is accepted in favor of reduced funnel friction for the majority of users.

---

## Version History

| Version | Change |
|------|--------|
| v1.4 | Expanded supported-region examples to include MY and aligned region-gating reference to v1.3 |
| v1.3 | Allow store-first redirect for join routes in supported regions; document iOS referrer tradeoff; Move public norms canonical route to /kinly/norms/:homePublicId |
| v1.2 | Defined invite code format (6-char typeable set, uppercase normalization) |
| v1.1 | Deduplicated canonical host section; clarified references; cleaned encoding |
| v1.0 | Initial share links and canonical URL contract |

---

## Final Assertion

A Kinly share link must:
- always be safe to open
- always be truthful
- never pressure commitment beyond store visit
- never bypass capability checks
- never auto-open the app

If a link does anything else, it violates this contract.

