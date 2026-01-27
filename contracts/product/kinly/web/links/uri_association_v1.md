---
Domain: Links
Capability: URI Association
Scope: platform
Artifact-Type: contract
Stability: stable
Status: active
Version: v1.0
---

# Contract: URI Association (AASA / assetlinks / manifest registration)

## Purpose

Define the domain-to-app trust relationship required for OS-verified links
across multiple Kinly family apps sharing a common link domain.

This contract ensures that:
- iOS and Android can cryptographically verify Kinly-controlled domains
- each link unambiguously resolves to exactly one app
- link hijacking, impersonation, and OS-level ambiguity are prevented
- the system can scale to future Kinly apps without breaking existing links

This contract is infrastructure only. It does not define routing, invite
semantics, authentication, or UX behavior.

---

## Scope

This contract applies to:
- Shared Kinly link domains (for example `go.makinglifeeasie.com`)
- iOS Universal Links (AASA)
- Android Verified App Links (Digital Asset Links / `assetlinks.json`)
- Path-based app ownership across multiple Kinly apps
- Web manifest metadata (informational only)

---

## Core Principle (Normative)

**A single HTTPS URL must resolve to at most one app.**

Shared domains are allowed. Shared path ownership is not.

All Kinly app associations must be disambiguated by path prefix.

---

## Definitions

- Association File (iOS): `apple-app-site-association` (AASA)
- Association File (Android): `assetlinks.json`
- Verified App Link: an HTTPS URL opened directly by the OS in a specific app
- Canonical Path Prefix: the top-level path segment that uniquely identifies
  the owning app
- Fallback: browser navigation when OS verification conditions are not met

---

## Canonical Path Ownership Model

When a domain is shared by multiple Kinly apps, each app must own a distinct,
non-overlapping canonical path prefix.

### Example (illustrative)

| App           | Canonical Path Prefix |
| ------------- | --------------------- |
| Kinly (core)  | `/kinly/*`            |
| Kinly Dating  | `/dating/*`           |
| Kinly Rent    | `/rent/*`             |

No app may claim another app's prefix. No prefix may be claimed by more than
one app.

---

## Normative Requirements

### R1 — Domains (source of truth)

R1.1 Each Kinly-controlled domain that participates in app opening must be
listed in the environment-scoped domain registry.

R1.2 Each such domain must serve:
- iOS: `https://<domain>/.well-known/apple-app-site-association`
- Android: `https://<domain>/.well-known/assetlinks.json`

R1.3 These endpoints must be:
- publicly reachable
- unauthenticated
- non-redirecting
- non-geoblocked
- served over HTTPS with valid TLS

### R2 — iOS (AASA)

R2.1 The AASA file must:
- be valid JSON
- be served at `/.well-known/apple-app-site-association`
- not require a `.json` extension
- not redirect (3xx disallowed)

R2.2 Each Kinly app entry in the AASA file must:
- explicitly list the iOS app identifier (Team ID + Bundle ID)
- declare only the canonical path prefix(es) owned by that app
- not declare paths owned by another Kinly app

R2.3 When multiple Kinly apps share a domain:
- each app must be scoped to its canonical path prefix
- no overlapping path patterns are permitted

### R3 — Android (assetlinks.json)

R3.1 The assetlinks file must:
- be served at `/.well-known/assetlinks.json`
- be a valid JSON array
- not redirect

R3.2 Each Kinly app declaration must:
- specify the Android package name
- specify the SHA-256 certificate fingerprint(s)

R3.3 Path scoping is **not** supported in `assetlinks.json`. Ownership by path
must be enforced in the Android manifest (see R4).

R3.4 No Android package entry should be included if the app does not own at
least one canonical path prefix on that domain.

### R4 — Android app manifest (path ownership)

R4.1 Each Kinly Android app must declare an intent filter per owned canonical
path prefix with:
- `android:autoVerify="true"`
- scheme `https`
- host matching the Kinly domain
- `android:pathPrefix` set to the canonical path prefix

R4.2 No app may declare a wildcard path (e.g., missing `pathPrefix`) on a
shared Kinly domain.

R4.3 For any given domain + path prefix, exactly one app may register a
matching intent filter to avoid OS app-chooser fallbacks.

### R5 — Web Manifest (PWA metadata)

R5.1 The web manifest is metadata only and must not be relied upon for
OS-verified link trust.

R5.2 Any app identity information in the web manifest must be consistent with:
- the app identifiers declared in AASA
- the package identities declared in assetlinks.json

### R6 — Environment Separation (dev / staging / prod)

R6.1 Production domains must publish production app identities only.

R6.2 Non-production domains may publish non-production identities, but must
not publish production identities unless explicitly documented.

R6.3 Canonical path ownership must remain consistent across environments.

### R7 — Backward Compatibility and Redirects

R7.1 Legacy or deprecated paths may exist at the web layer, but must redirect
to a canonical, app-owned path.

R7.2 Only canonical paths may be declared in association files.

### R8 — Caching and Propagation

R8.1 Implementations must assume OS-level caching.

R8.2 Release procedures must account for propagation delays and cached state
(for example reinstall, cache reset, or wait period).

R8.3 Association endpoints should set intentional cache headers to avoid
accidental permanent caching during rollout.

---

## Verification Requirements (Definition of Done)

A release that depends on verified app links must not ship unless:

**V1 — Public fetch**
- Both association endpoints return HTTP 200 on expected domains

**V2 — Content validity**
- JSON parses successfully
- App IDs, package names, and fingerprints match the environment

**V3 — Path correctness**
- A canonical link under each app's prefix opens the correct app
- No app chooser is shown when conditions match

**V4 — Fallback behavior**
- Non-matching conditions open the link in the browser safely

---

## Security and Abuse Considerations

S1 Association files are security boundaries and must be change-controlled.

S2 Path-based ownership must prevent:
- link hijacking
- cross-app impersonation
- ambiguous OS resolution

S3 Association endpoints must not leak secrets.

---

## Non-Goals

This contract does not define:
- deep-link parsing or in-app navigation
- invite formats or semantics
- authentication or session restoration
- deferred deep linking logic
- region gating or marketing UX

These are defined in downstream product contracts.

---

## Dependencies

None (root platform capability).

---

## Downstream Contracts (Informational)

Typical dependent capabilities include:
- product/deep_linking (per app)
- product/invites
- product/auth_entry
- product/reviewer_access
- product/marketing_landing

---

## Production Registry (Authoritative)

- Domain: `go.makinglifeeasie.com`
- Canonical path ownership:
  - Kinly (core): `/kinly/*`

---

## Production App Identities (Authoritative)

### iOS
- Apple Team ID: `M7SBU9RGY5`
- Bundle ID: `com.makinglifeeasie.kinly`
- App Identifier (Team ID + Bundle ID): `M7SBU9RGY5.com.makinglifeeasie.kinly`
- AASA path scope: `/kinly/*`

### Android
- Package name: `com.makinglifeeasie.kinly`
- SHA-256 signing cert fingerprint (App signing key):  
  `14:9A:0A:E7:EE:26:BF:EE:2E:94:26:AE:4B:EA:57:D2:70:94:32:8F:F9:8E:19:42:C5:5C:02:88:36:4B:EA:4D`
- App Links path scope (intent filter): `/kinly/*`

---

## Required Association Files (Production Examples)

### iOS — `https://go.makinglifeeasie.com/.well-known/apple-app-site-association`

```json
{
  "applinks": {
    "details": [
      {
        "appID": "M7SBU9RGY5.com.makinglifeeasie.kinly",
        "paths": [ "/kinly/*" ]
      }
    ]
  }
}
```

### Android — `https://go.makinglifeeasie.com/.well-known/assetlinks.json`

```json
[
  {
    "relation": [ "delegate_permission/common.handle_all_urls" ],
    "target": {
      "namespace": "android_app",
      "package_name": "com.makinglifeeasie.kinly",
      "sha256_cert_fingerprints": [
        "14:9A:0A:E7:EE:26:BF:EE:2E:94:26:AE:4B:EA:57:D2:70:94:32:8F:F9:8E:19:42:C5:5C:02:88:36:4B:EA:4D"
      ]
    }
  }
]
```

Path ownership for Android must also be enforced in the app manifest intent
filters (scope to `/kinly/*`) to align with this contract.
