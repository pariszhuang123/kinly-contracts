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
- App launched, or web fit-check flow entered.
- No active session or session expired.

## Postconditions
- On success: user authenticated via Google or Apple; `user_profile` exists and is updated.
- On failure: user remains unauthenticated and stays on Welcome (app) or sign-in prompt (web).

## Surfaces

Google/Apple OAuth via Supabase is valid on **both app and web**.

| Surface | Entry Point | Post-Auth Destination |
|---|---|---|
| App | Welcome screen | App home / onboarding |
| Web (Fit Check) | Fit check sign-in prompt | Fit check dashboard / run results |

## Identity Invariant

Backend ownership and linking MUST use the stable authenticated user
identity (`auth.uid()`), not raw email string matching. "Login with the
same email" is user-facing guidance only.

## Flow (Given/When/Then)

### App
Given an unauthenticated user
When they choose Google or Apple and complete OAuth successfully
Then the app creates/refreshes `user_profile` and enters the app

### Web (Fit Check funnel)
Given an unauthenticated user on the fit check web flow
When they complete 4 behavioural scenarios and choose Google or Apple
to save results
Then the web creates/refreshes `user_profile` and saves fit check
ownership to the authenticated user

Auth is prompted **after** scenario answers, not before. The owner
answers first, then signs in to save.

## Steps

### App
1. Show Welcome with Google and Apple options.
2. On selection, start Supabase OAuth provider flow.
3. On return, if success: ensure `user_profile` exists (upsert) and navigate to app.
4. If failure/cancel: remain on Welcome.

### Web (Fit Check)
1. Owner completes 4 behavioural scenario questions (no auth required).
2. Show sign-in prompt with Google and Apple options (save gate).
3. On selection, start Supabase OAuth provider flow (web redirect).
4. On return, if success: ensure `user_profile` exists (upsert), save
   fit check run bound to `auth.uid()`, and show results.
5. If failure/cancel: remain on sign-in prompt; answers are not saved.

## Error Cases
- OAuth canceled or fails: remain on Welcome (app) or sign-in prompt (web).
- Deactivated user attempts to sign in: deny access.

## Test Plan Map
- Successful Google and Apple sign-in create/refresh `user_profile` (app and web).
- Cancelled auth leaves user unauthenticated.
- Deactivated user cannot access app (RLS denied).
- Web auth session persists across page reloads.
- Same user authenticating on web and app shares the same `auth.uid()`.
