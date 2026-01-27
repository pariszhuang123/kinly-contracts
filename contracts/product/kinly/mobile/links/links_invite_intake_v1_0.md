---
Domain: Links
Capability: Deep link intake & invite join resolution
Scope: frontend
Artifact-Type: contract
Stability: evolving
Status: active
Version: v1.0
---

# Contract — Deep Link Handling (Cold Start & Warm Start) for `/kinly/join/:inviteCode` — kinly-app

Registry: `registry/REGISTRY.md`

## Purpose

Define how the Kinly mobile app MUST handle invite links whose canonical web form is:

`https://go.makinglifeeasie.com/kinly/join/:inviteCode`

…across cold start and warm start, in a way that is safe, deterministic, and authentication-aware.

This contract governs:
- intake and validation of invite payloads
- persistence of join intent before navigation
- deferred join resolution after authentication is available
- safe fallback routing on any failure
- idempotent, single-flight join attempts

Goals:
- deep links never assume app readiness, install state, authentication, or membership
- join intent is never lost across restarts
- users are never stranded or misrouted
- existing home membership is never blocked
- Today is reachable only after a successful join, already-member success, or an already-existing home

## Scope

Applies only to kinly-app (mobile).

Out of scope:
- web deep link offering or gating (kinly-web)
- URI association / platform configuration (AASA, assetlinks, manifests) — see dependency
- install-boundary deferred deep linking
- attribution and marketing analytics

## Canonical Naming (Normative)

- Canonical internal name: `invite_code` (string).
- The app MAY accept inbound aliases but MUST normalize to `invite_code`.
- Accepted inbound aliases: `inviteCode`, `invite_id`, `code`.
- After normalization:
  - internal storage field MUST be `invite_code`
  - join RPC argument value MUST be `invite_code`
- RPC mapping:
  - Supabase function name: `public.homes_join(p_code text)`.
  - Exposed RPC name (client call): `homes.join`.
  - The app MUST call `supabase.rpc('homes_join', params: { 'p_code': invite_code })` (or equivalent) so the client-visible RPC remains `homes.join` in line with Kinly naming conventions.

## Definitions

**Canonical Invite URL (Web Form)**  
`https://go.makinglifeeasie.com/kinly/join/:inviteCode`

`inviteCode` is an opaque identifier issued by the backend.

**App Deep Link (Platform-Delivered URI)**  
A platform-delivered URI that resolves to invite intent.

Examples (illustrative):
- `kinly://join?invite_code=ABC123`
- `https://go.makinglifeeasie.com/kinly/join/ABC123`

**Cold Start** — Deep link delivered when the app is not running and launches from scratch.  
**Warm Start** — Deep link delivered while the app is running or resumed.  
**Pending Join Intent** — Persisted representation of a join attempt derived from `invite_code`.

Minimum stored fields:
- `invite_code`
- `received_at` (ISO-8601)
- optional `source` (e.g., `web_join`, `android_install_referrer`, `ios_manual_confirm`)

Pending Join Intent MUST survive:
- app restarts
- authentication transitions
- router resets

Storage scope (MUST):
- store the Pending Join Intent in app-scoped secure storage
- bind the stored intent to the currently authenticated user
- clear on sign-out
- never reuse an intent across different authenticated users on the same device

## Core Principles

- Cold start and warm start MUST produce identical outcomes.
- Invite payload MUST be validated before persisting intent.
- Join intent MUST be persisted before any navigation decision.
- Join resolution MUST NOT occur until authentication is confirmed.
- Membership MUST NOT be assumed.
- Existing home membership MUST take precedence over invite intent.
- Failures MUST route safely and never block access.
- Join resolution MUST be idempotent and single-flight.
- Sensitive data (invite codes) MUST NOT be logged (app or backend).
- Pathing MUST align with `uri_association_v1` (Kinly owns `/kinly/*`).

## Authoritative App Entry Surfaces

| Surface | Preconditions |
| --- | --- |
| Welcome | App installed, user unauthenticated |
| Start | User authenticated, no home membership |
| Today | User authenticated AND (home already exists OR join just succeeded OR already_member success) |

The app MUST respect this ordering.

## Invite Code Validation (Normative)

The app MUST validate `invite_code` before persisting intent.

Minimum requirements (MUST):
- non-empty string
- trimmed of whitespace
- normalized to uppercase
- exactly 6 characters
- characters limited to `A-H, J-N, P-Z, 2-9` (excludes `I`, `O`, `0`, `1`); regex form (case-insensitive input): `^[A-HJ-NP-Z2-9]{6}$`

If validation fails:
- ignore the invite intent
- record a non-PII reason code `INVALID_INVITE_CODE`
- clear any Pending Join Intent derived from this payload
- apply Auth-Aware Fallback Routing
- MUST NOT navigate to Today based on the invite

## Deep Link Payload Rules

Allowed:
- `invite_code` (or inbound alias normalized)
- optional `source`

MUST NOT accept:
- authentication tokens
- user identifiers
- private home data
- membership assumptions

## Intake Requirements (Cold + Warm)

When any deep link is received:
1) Parse and validate payload.  
2) If a valid `invite_code` exists: persist it immediately as a Pending Join Intent.  
3) The app MUST NOT attempt join resolution yet, navigate directly to Today, or assume authentication/membership.  
4) If payload is invalid: ignore intent and apply Auth-Aware Fallback Routing.  

Persistence MUST occur before routing decisions.

## Cold Start Handling (Required)

On cold start with a deep link:
- Capture payload during launch.
- Apply Intake Requirements.
- Continue normal initialization (authentication resolution, core app state, router readiness).
- After readiness: run Resolution Eligibility Check, then Join Resolution Logic if eligible.

Cold start MUST NOT bypass initialization.

## Warm Start Handling (Required)

On warm start with a deep link:
- Capture payload immediately.
- Apply Intake Requirements.
- Run Resolution Eligibility Check.
- Run Join Resolution Logic if eligible.

Warm start MUST NOT bypass validation or persistence.

## Resolution Eligibility Check (Authoritative)

The app MAY attempt join resolution only when:
- authentication state is known, and
- the user is authenticated.

Existing-membership short-circuit (required):
- If the authenticated user already has an active home membership (same signal used by the auth/start/Today router), clear any Pending Join Intent and route to Today without calling the join RPC.

If authentication is unknown or unauthenticated:
- defer join resolution
- route to Welcome

## Backend Join RPC (Normative)

RPC: `public.homes_join(p_code text) -> jsonb` (raises on error)

**Return schema (authoritative)**

Success:
- `status`: `"success"`
- `code`: `"joined"` or `"already_member"`
- `message`: string
- `home_id`: uuid

Blocked (non-error):
- `status`: `"blocked"`
- `code`: `"member_cap"`
- `message`: string
- `home_id`: uuid
- `request_id`: uuid

Errors (raised):
The RPC MAY raise an application error code including:
- `INVALID_CODE`
- `INACTIVE_INVITE`
- `ALREADY_IN_OTHER_HOME`
Other error codes MAY be introduced in future versions.

The backend MUST derive identity via `auth.uid()` and MUST NOT accept user identifiers from the client.

## Join Resolution Logic (Authoritative, RPC-aligned)

When eligible and a Pending Join Intent exists:
- Read Pending Join Intent (`invite_code`).
- Call `public.homes_join(p_code => invite_code)`.

Then:

If RPC returns `status = "success"`:
- If `code = "joined"`: clear Pending Join Intent; navigate to Today.
- If `code = "already_member"`: clear Pending Join Intent; navigate to Today.

If RPC returns `status = "blocked"`:
- If `code = "member_cap"`: clear Pending Join Intent; route to Start; show a non-paywall message indicating the home is not accepting new members and the owner was notified (notification emitted by `public._member_cap_enqueue_request` inside `homes_join`).
- The app MAY display/store `request_id` for support or UI confirmation.

If RPC raises an error:
- Clear Pending Join Intent.
- Apply Auth-Aware Fallback Routing.
- The app SHOULD display a safe message keyed by error code.

Join resolution MUST be idempotent and single-flight (no concurrent attempts).

## Auth-Aware Fallback Routing (Required)

| Auth State | Home Membership | Destination |
| --- | --- | --- |
| Unauthenticated | n/a | Welcome |
| Authenticated | No home | Start |
| Authenticated | Home exists | Today |

Rules:
- Existing home membership MUST always take precedence.
- A failed or ignored invite MUST NOT block access to Today.
- Today MUST NOT be reached due to a failed join attempt.
- Blocked (`member_cap`) MUST NOT navigate to Today.

## Idempotency & Duplicate Delivery Guarantees

The app MUST guard against:
- OS re-delivery of the same link
- repeated user taps
- multiple deep link events during resume

Required behaviors:
- dedupe repeated invite codes
- enforce single-flight join attempts
- clear Pending Join Intent after exactly one resolution attempt (success / blocked / error)

## Platform Delivery Notes (Non-Normative)

iOS: cold start via launch context; warm start via continuation callbacks.  
Android: cold start via Activity intent; warm start via `onNewIntent`. Duplicate delivery is common.  
Implementation MUST unify all paths into: validate → persist intent → defer → resolve → fallback.

## Failure Scenarios & Required Outcomes

| Scenario | Required Behavior |
| --- | --- |
| Invalid payload | Ignore intent, reason `INVALID_INVITE_CODE`, fallback |
| Invite not found (`INVALID_CODE`) | Clear intent, fallback |
| Invite expired/invalid (`INACTIVE_INVITE`) | Clear intent, fallback |
| Already in other home (`ALREADY_IN_OTHER_HOME`) | Clear intent, fallback |
| Member cap reached (`status="blocked", code="member_cap"`) | Clear intent, route Start, show blocked message |
| Auth unknown | Defer, route Welcome |
| Join fails (other error) | Clear intent, fallback |
| Routing error | Safe fallback |
| Duplicate delivery | Dedupe, single-flight |

No failure may:
- crash the app
- strand the user
- block access to an existing home

## Logging & Observability

The app MAY log:
- deep link received (sans invite code)
- resolution attempted (reason codes only)
- resolution success/failure/blocked (reason codes only)

The app MUST NOT log:
- invite codes
- raw deep link URLs
- personal identifiers

The backend MUST NOT log invite codes or include raw invite codes in error metadata.

## Test Requirements (Normative)

The app MUST verify:
- Cold start + valid invite + unauthenticated: intent persisted → Welcome → login → join → Today.
- Warm start + valid invite + authenticated: join → Today.
- Invalid invite: ignored with reason `INVALID_INVITE_CODE` → fallback.
- Duplicate delivery: single join attempt.
- Join failure: intent cleared → fallback.
- Authenticated user with existing home: invite failure → Today.
- Member cap blocked: intent cleared → Start with blocked message (and request_id surfaced if desired).

## Dependencies

- `contracts/product/kinly/web/links/uri_association_v1.md` (path ownership `/kinly/*`)
- `contracts/product/kinly/web/links/links_deep_links_v1_1.md`
- `contracts/product/kinly/web/links/links_fallback_v1_1.md`

## Final Assertion

A Kinly app deep link derived from `/kinly/join/:inviteCode` MUST:
- behave identically on cold and warm start
- normalize to canonical `invite_code`
- persist join intent before navigation
- resolve joins only after authentication
- call `public.homes_join(p_code => invite_code)`
- never assume membership
- never block access to an existing home
- reach Today only after a successful join, already-member success, or existing membership
- handle blocked outcomes explicitly and safely
- always fail safely
- remain compatible with URI association path ownership rules
