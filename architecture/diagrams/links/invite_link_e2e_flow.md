---
Domain: Links
Capability: Invite link end-to-end flow
Scope: shared
Artifact-Type: architecture
Stability: evolving
Status: active
Version: v1.1
---

# Kinly Links — End-to-End Invite Flow Diagram (Store-First)

This diagram illustrates the complete invite link flow from web share to app join resolution using the **store-first model** (v1.3):
- Region gating happens first
- Supported regions redirect directly to the app store (no intermediate landing page)
- Android: Install Referrer preserves invite code across install
- iOS: No referrer; manual code entry post-install (accepted tradeoff)
- Deep link path for already-installed apps
- Authentication-aware routing and fallback

## Governing Contracts

| Contract | Scope |
|----------|-------|
| [links_share_links_v1_3.md](../../../contracts/product/kinly/web/links/links_share_links_v1_3.md) | Share links & canonical URLs (store-first) |
| [links_region_gate_v1_2.md](../../../contracts/product/kinly/web/links/links_region_gate_v1_2.md) | Region gating & interest capture |
| [links_deep_links_v1_1.md](../../../contracts/product/kinly/web/links/links_deep_links_v1_1.md) | Deep link mapping & app handoff |
| [uri_association_v1.md](../../../contracts/product/kinly/web/links/uri_association_v1.md) | URI association (AASA/assetlinks) |
| [links_invite_intake_v1_0.md](../../../contracts/product/kinly/mobile/links/links_invite_intake_v1_0.md) | Deep link handling (cold/warm) |
| [links_invite_deferred_install_v1_0.md](../../../contracts/product/kinly/shared/links/links_invite_deferred_install_v1_0.md) | Deferred install-boundary intent |
| [links_fallback_v1_1.md](../../../contracts/product/kinly/web/links/links_fallback_v1_1.md) | Fallback routing & failure handling |

---

## End-to-End Flow

```mermaid
flowchart TD
  %% --- Web: region gate (no landing page for supported regions) ---
  A[Share link opened<br/>https://go.makinglifeeasie.com/kinly/join/:inviteCode] --> B{Region supported?<br/>NZ or SG}

  B -- No --> C[Redirect to /get<br/>interest capture<br/>preview only]
  C --> D[/fallback on errors/]

  %% --- Store-first redirect (v1.3) ---
  B -- Yes --> E{Platform detection}

  E -- Android --> F[Redirect to Play Store<br/>with Install Referrer:<br/>kinly_invite_code=inviteCode]
  E -- iOS --> G[Redirect to App Store<br/>no referrer available]
  E -- Desktop --> H[Render landing page<br/>show store badges]

  %% --- App already installed: deep link intercept ---
  A -.-> |App installed<br/>OS intercepts link| I[Deep link / verified link fires<br/>URI: kinly://join?invite_code=...]
  I --> J[kinly-app: Deep link intake<br/>validate + normalize to invite_code]
  J --> K[Persist Pending Join Intent<br/>invite_code, received_at, source]
  K --> L{Auth known & authenticated?}

  L -- No --> M[Route to Welcome<br/>Defer join resolution]
  M -.-> |After login| L

  L -- Yes --> N{Already has home membership?}
  N -- Yes --> O[Clear Pending Join Intent<br/>Navigate to Today<br/>skip RPC]

  N -- No --> P[Call homes_join RPC<br/>public.homes_join p_code => invite_code<br/>server uses auth.uid]
  P --> Q{RPC Result?}

  Q -- success: joined --> R[Clear Pending Join Intent<br/>Navigate to Today]
  Q -- success: already_member --> R
  Q -- blocked: member_cap --> S[Clear Pending Join Intent<br/>Route to Start<br/>show blocked message]
  Q -- error --> T[Clear Pending Join Intent<br/>Auth-aware fallback]

  %% --- Auth-aware fallback detail ---
  T --> U{Auth state?}
  U -- Unauthenticated --> V[Welcome]
  U -- Authenticated, no home --> W[Start]
  U -- Authenticated, has home --> X[Today]

  %% --- Android: Install + referrer recovery ---
  F --> Y[User installs from Play Store]
  Y --> Z[First app open]
  Z --> AA[Android Install Referrer intake<br/>read once; parse kinly_invite_code]
  AA --> AB[Create Pending Join Intent<br/>source=android_install_referrer]
  AB --> K

  %% --- iOS: Install + manual entry (accepted tradeoff) ---
  G --> AC[User installs from App Store]
  AC --> AD[First app open]
  AD --> AE[Start/Welcome surface shows:<br/>'Have an invite link?']
  AE --> AF[User pastes URL or code]
  AF --> AG[Parse to invite_code<br/>source=ios_manual_confirm]
  AG --> K

  %% --- Invalid payload handling ---
  J -. invalid payload .-> T

  %% --- Web failure handling ---
  H -. web failure .-> D
```

---

## Key Invariants

1. **Store redirect does NOT auto-open the app** — only navigates to store; install and launch are user actions
2. **Region gating happens before any redirect** — unsupported regions go to `/get`
3. **Android preserves invite via Install Referrer** — recovered on first launch
4. **iOS requires manual code entry** — accepted tradeoff, no referrer mechanism
5. **Deep links still work for installed apps** — OS intercepts before web redirect
6. **Pending Join Intent persisted before navigation** — survives restarts
7. **Join resolution only after authentication is confirmed**
8. **Existing home membership takes precedence** — skip RPC, route to Today
9. **All failures apply auth-aware fallback** — Welcome / Start / Today based on state
10. **Intent is single-flight** — cleared after any terminal outcome (success, blocked, error)
11. **Invite codes never logged** — app or backend

---

## iOS Tradeoff

iOS does not provide an Install Referrer API. This means:
- Invite codes cannot be automatically recovered after install
- Users must manually enter or paste the invite code in the app
- The app provides a "Have an invite link?" entry point on Start/Welcome

This is an **accepted limitation** in favor of reduced funnel friction for the majority path (Android + already-installed).
