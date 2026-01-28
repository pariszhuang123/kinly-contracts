---
Domain: Links
Capability: Invite link end-to-end flow
Scope: shared
Artifact-Type: architecture
Stability: evolving
Status: active
Version: v1.0
---

# Kinly Links — End-to-End Invite Flow Diagram

This diagram illustrates the complete invite link flow from web share to app join resolution, including:
- Web landing and region gating
- Deep link handoff (installed app path)
- Deferred install-boundary recovery (Android referrer, iOS manual)
- Authentication-aware routing and fallback

## Governing Contracts

| Contract | Scope |
|----------|-------|
| [links_share_links_v1_2.md](../../../contracts/product/kinly/web/links/links_share_links_v1_2.md) | Share links & canonical URLs |
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
  %% --- Web: share and landing ---
  A[Share link opened<br/>https://go.makinglifeeasie.com/kinly/join/:inviteCode] --> B{Region supported?<br/>NZ or SG}

  B -- No --> C[Redirect to /get<br/>interest capture<br/>preview only]
  C --> D[/fallback on errors/]

  B -- Yes --> E[Render /kinly/join/:inviteCode page<br/>User-initiated actions only:<br/>• Copy link/code<br/>• Get the app<br/>• Open in Kinly]

  %% --- Installed app path (deep link mapping + URI association) ---
  E --> F{App installed AND<br/>user taps 'Open in Kinly'?}

  F -- Yes --> G[Deep link / verified link fires<br/>URI: kinly://join?invite_code=...]
  G --> H[kinly-app: Deep link intake<br/>validate + normalize to invite_code]
  H --> I[Persist Pending Join Intent<br/>invite_code, received_at, source]
  I --> J{Auth known & authenticated?}

  J -- No --> K[Route to Welcome<br/>Defer join resolution]
  K -.-> |After login| J

  J -- Yes --> L{Already has home membership?}
  L -- Yes --> M[Clear Pending Join Intent<br/>Navigate to Today<br/>skip RPC]

  L -- No --> N[Call homes_join RPC<br/>public.homes_join p_code => invite_code<br/>server uses auth.uid]
  N --> O{RPC Result?}

  O -- success: joined --> P[Clear Pending Join Intent<br/>Navigate to Today]
  O -- success: already_member --> P
  O -- blocked: member_cap --> Q[Clear Pending Join Intent<br/>Route to Start<br/>show blocked message]
  O -- error --> R[Clear Pending Join Intent<br/>Auth-aware fallback]

  %% --- Auth-aware fallback detail ---
  R --> S{Auth state?}
  S -- Unauthenticated --> T[Welcome]
  S -- Authenticated, no home --> U[Start]
  S -- Authenticated, has home --> V[Today]

  %% --- Not installed path (install boundary recovery) ---
  F -- No --> W{Platform}

  W -- Android --> X[User taps 'Get the app'<br/>Play Store URL includes referrer:<br/>kinly_invite_code=inviteCode]
  X --> Y[Install + first open]
  Y --> Z[Android Install Referrer intake<br/>read once; parse kinly_invite_code]
  Z --> AA[Create Pending Join Intent<br/>source=android_install_referrer]
  AA --> I

  W -- iOS --> AB[User taps 'Get the app'<br/>App Store no referrer]
  AB --> AC[Install + first open]
  AC --> AD[Start surface shows:<br/>'Have an invite link?']
  AD --> AE[User pastes URL or code]
  AE --> AF[Parse to invite_code<br/>source=ios_manual_confirm]
  AF --> I

  %% --- Invalid payload handling ---
  H -. invalid payload .-> R

  %% --- Web failure handling ---
  E -. web failure .-> D
```

---

## Key Invariants

1. **Deep links are always user-initiated** — never auto-triggered on page load
2. **Pending Join Intent persisted before navigation** — survives restarts
3. **Join resolution only after authentication is confirmed**
4. **Existing home membership takes precedence** — skip RPC, route to Today
5. **All failures apply auth-aware fallback** — Welcome / Start / Today based on state
6. **Intent is single-flight** — cleared after any terminal outcome (success, blocked, error)
7. **Invite codes never logged** — app or backend
