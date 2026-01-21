# Deployment — Kinly Web

This document describes how Kinly Web is deployed and operated.

Kinly Web is a **public, safety-sensitive surface**.  
Deployment must preserve routing safety, region gating, and fallback guarantees.

---

## Hosting

- Platform: Vercel
- Framework: Next.js
- Deployment model:
  - Preview deployments per PR
  - Production deployment from `main`

Primary domain:
- `go.makinglifeeasie.com`

---

## Environments

| Environment | Purpose | Domain |
|---|---|---|
| Local | Developer testing | localhost |
| Preview | PR validation | *.vercel.app |
| Production | Live traffic | go.makinglifeeasie.com |

---

## Environment Variables

### Local development
- Use `.env.local`
- `.env.local` is gitignored
- Copy from `.env.example`

### Vercel
- Environment variables are set in:
  - Project → Settings → Environment Variables
- Variables must be configured for:
  - Preview
  - Production

No secrets are stored in the repository.

---

## Required Variables

See `.env.example` for the authoritative list.

Rules:
- Only non-sensitive values may use `NEXT_PUBLIC_*`
- Secrets live only in:
  - Vercel secrets
  - Supabase Edge Function secrets

---

## Supabase Edge Functions

- Kinly Web does not write to the database directly
- All writes go through Supabase Edge Functions
- Edge Functions call Postgres RPCs (SECURITY DEFINER)

Before deploying web changes that rely on Edge Functions:
- Ensure the function is deployed
- Ensure secrets are configured
- Ensure RPC exists and is tested

---

## Preview Deployments (PRs)

Preview deployments are required for:
- Routing changes
- Join flow changes
- Public norms page changes
- Region gating changes

Checklist:
- [ ] Preview URL opens correctly
- [ ] `/fallback` route works
- [ ] Join flows show store CTAs
- [ ] No auto-redirect to app
- [ ] Unsupported regions gated correctly

---

## Production Deployment

Production deploys occur when:
- Changes are merged to `main`
- CI passes
- Execution agents pass

Before merging:
- Verify preview behavior
- Confirm no contract drift
- Confirm environment variables are present

---

## Rollback Strategy

- Vercel supports instant rollback to previous deployment
- Rollback is preferred over hot-fixing in production
- If rollback occurs:
  - Identify contract impact
  - Document cause if behavioral

---

## Domain & DNS Notes

- Domain is managed outside this repo
- Changes to domain or routing require:
  - Planner approval
  - Release approval

---

## Known Risks & Safeguards

- Misconfigured env vars can break routing
- Missing Edge Function can block interest capture
- Auto-redirects can dead-end users

Safeguards:
- `/fallback` route must always exist
- Store CTAs must always render
- Execution agents must pass

---

## When in Doubt

- Prefer safety over speed
- Prefer fallback over failure
- Prefer rollback over patching

If uncertain, stop and escalate to the Planner.
