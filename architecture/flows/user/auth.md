---
Domain: Flows
Capability: Auth
Scope: platform
Artifact-Type: architecture
Stability: evolving
Status: draft
Version: v1.0
---

# Flow — User Auth (Google/Apple)

Contract: v1 (see `docs/contracts/users_v1.md`)
Diagram: `docs/diagrams/user/auth_providers.md`

## Preconditions
- App launched.
- No active session or session expired.

## Postconditions
- On success: user authenticated via Google or Apple; `user_profile` exists and is updated.
- On failure: user remains unauthenticated and stays on Welcome.

## Flow (Given/When/Then)
Given an unauthenticated user
When they choose Google or Apple and complete OAuth successfully
Then the app creates/refreshes `user_profile` and enters the app

## Steps
1. Show Welcome with Google and Apple options.
2. On selection, start Supabase OAuth provider flow.
3. On return, if success: ensure `user_profile` exists (upsert) and navigate to app.
4. If failure/cancel: remain on Welcome.

## Error Cases
- OAuth canceled or fails: remain on Welcome.
- Deactivated user attempts to sign in: deny access.

## Test Plan Map
- Successful Google and Apple sign-in create/refresh `user_profile`.
- Cancelled auth leaves user unauthenticated.
- Deactivated user cannot access app (RLS denied).
