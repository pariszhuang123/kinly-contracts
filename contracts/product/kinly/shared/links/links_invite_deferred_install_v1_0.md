---
Domain: Links
Capability: Deferred install-boundary invite intent
Scope: shared
Artifact-Type: contract
Stability: evolving
Status: active
Version: v1.0
---

# Contract — Deferred Invite Intent Across Install Boundary — v1.0

Registry: `contracts/contracts_registry.md`

---

## Purpose

Preserve and recover invite join intent when a user taps the canonical invite URL **before the app is installed** and ensure the intent is delivered into the existing mobile deep-link intake pipeline (`links_invite_intake_v1_0.md`).

This contract covers:
- web handoff to the appropriate app store with an encoded referrer
- app-side recovery of the referrer and normalization to `invite_code`
- manual fallback on iOS where no referrer exists
- persistence, binding, clearing, and idempotency rules shared with the mobile intake contract

---

## Canonical Path & Naming (Normative)

- Canonical invite URL: `https://go.makinglifeeasie.com/join/:inviteCode`
- Accepted legacy alias: `/kinly/join/:inviteCode` (MAY be consumed but MUST normalize to the canonical path and payload).
- Canonical internal name: `invite_code`
- Android referrer key: `kinly_invite_code`
- Optional source tag: `src=web_join` (or other short reason codes). MUST NOT include tokens, user IDs, or home identifiers.

---

## JoinIntent Payload (Authoritative)

Recovered intent MUST be represented as:

```json
{
  "intent_type": "join_invite",
  "invite_code": "string",
  "source": "string",
  "captured_at": "ISO-8601 timestamp"
}
```

This object is the only output of this contract and MUST feed into `links_invite_intake_v1_0.md` for validation and resolution.

---

## Android — Web → Play Store → App (Required)

**Web handoff**
- Construct Play Store URL: `https://play.google.com/store/apps/details?id=<PACKAGE>&referrer=<REFERRER>`
- `<REFERRER>` MUST be percent-encoded once with the form:  
  `kinly_invite_code=<inviteCode>[&src=web_join]`
  - `inviteCode` MUST be URL-encoded (reserved chars escaped, no double-encoding).
  - Entire referrer string MUST remain under Play Store referrer length limits (<= 2000 chars; invite codes are short so this is satisfied).
- MUST NOT include any other parameters, tokens, or PII.
) to prevent repeat processing.
- If missing or invalid:
**App intake**
- On first app open post-install, kinly-app MUST read the install referrer string.
- Parse `kinly_invite_code`; accept `kinly_invite` as an alias but normalize to `invite_code`.
- If present and valid after validation rules in `links_invite_intake_v1_0.md`:
  - Build a `JoinIntent` with `source="android_install_referrer"` and `captured_at` = current timestamp.
  - Persist as a **Pending Join Intent** using the same store and semantics as `links_invite_intake_v1_0.md`.
  - Immediately mark `deferred_invite_checked` (or equivalent
  - Do nothing further; app startup MUST continue without blocking.

**Binding / Clearing / Idempotency (Shared Rules)**
- Pending Join Intent MUST be stored in the same secure, app-scoped store used by `links_invite_intake_v1_0.md`.
- Intent MUST be bound to the authenticated user; clear automatically on sign-out or auth user change.
- Dedupe: if an identical `invite_code` already exists as pending, MUST NOT create a duplicate record.
- Single-flight: only one resolution attempt per pending intent; clear after any terminal outcome (success, blocked, error).
- Precedence: if a higher-precedence source (platform-delivered deep link) begins resolution, lower-precedence intents (install referrer, manual entry) MUST be cleared immediately.

---

## iOS — Manual Confirm Fallback (Required)

Because iOS lacks reliable install referrer:

- Provide a calm, optional entry point on Start (or Welcome if unauthenticated): “Have an invite link?”.
- Accept either full URL or raw invite code; parse to `invite_code` using the same validation rules as `links_invite_intake_v1_0.md`.
- On valid code:
  - Create `JoinIntent` with `source="ios_manual_confirm"` and persist as Pending Join Intent (same store, same binding/clearing/idempotency rules).
- On invalid code:
  - Ignore, record reason `INVALID_INVITE_CODE` (sans code), and route via auth-aware fallback; MUST NOT block navigation or require modal dismissal.
- The manual entry surface MAY reuse the existing invite-entry UI already used in the join/start flow; no new modal is required if the existing component can be invoked from Start/Welcome.

---

## Precedence (Authoritative)

When multiple invite sources are present, resolution precedence MUST be:
1) Platform-delivered deep link (installed open)
2) Android install referrer
3) iOS manual confirm

Once a higher-precedence intent begins resolution, all lower-precedence intents MUST be discarded and cleared.

---

## Logging & Privacy

- MUST NOT log invite codes, raw referrer strings, or full URLs.
- MAY log reason codes (e.g., `INVALID_INVITE_CODE`, `REFERRER_MISSING`) and source (`android_install_referrer`, `ios_manual_confirm`, `web_join`).

---

## Dependencies

- `contracts/product/kinly/mobile/links/links_invite_intake_v1_0.md` (validation, deep link handling, resolution, pending intent store)
- `contracts/product/kinly/web/links/links_deep_links_v1_1.md` (canonical join path)
- `contracts/product/kinly/web/links/uri_association_v1.md` (path ownership)
- `contracts/product/kinly/web/links/links_fallback_v1_1.md` (fallback routing)

---

## Final Assertion

Kinly MUST:
- offer `/join/:inviteCode` as the canonical invite URL (accepting `/kinly/join/:inviteCode` as a legacy alias)
- encode Android Play Store referrers as `kinly_invite_code=<inviteCode>[&src=web_join]` with single percent-encoding and no PII
- recover install referrer on Android, normalize to `invite_code`, and persist as Pending Join Intent
- provide an iOS manual confirm that feeds the same Pending Join Intent pipeline
- bind intents to the authenticated user, dedupe, single-flight resolve, and clear on sign-out or after any terminal outcome
- hand off all recovered intents to `links_invite_intake_v1_0.md` for validation and join resolution
- never log invite codes or referrer strings
