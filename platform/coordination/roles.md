# Roles — Kinly Web

This document defines **who owns what** in the Kinly Web repository.
Roles exist to make decisions explicit, prevent accidental harm, and keep the system calm.

If a question is unclear, start here.

---

## Planner

**Primary responsibility**
- Product intent, scope, sequencing, and safety posture

**Owns**
- Public vs private boundaries
- Region gating policy
- Join semantics
- Interest capture purpose
- Contract approval

**Must review**
- Any change affecting routing behavior
- Any change affecting onboarding or join flows
- Any change that alters public visibility
- Any new data collection

**Can block**
- Features that introduce social risk
- Features that bypass contracts
- Features that weaken fallback safety

---

## Web UI

**Primary responsibility**
- Next.js routes and pages
- Accessibility and clarity
- OG previews
- Store CTA rendering

**Owns**
- Page composition
- Visual hierarchy
- Error states and empty states

**Must not**
- Implement business logic
- Write to the database
- Bypass region gating rules
- Auto-open the app without user action

**Reviews**
- UI changes for clarity, accessibility, and tone

---

## Deep Linking

**Primary responsibility**
- Mapping between web URLs and app deep links

**Owns**
- Deep link formats
- Query parameter translation
- App fallback semantics

**Must review**
- Any change to `/join`, `/home`, or `/norms` routes
- Any change that affects how the app is opened

**Can block**
- Auto-redirects
- Unsafe deep-link attempts
- Changes that risk dead-ending users

---

## Edge Functions

**Primary responsibility**
- Input validation
- Calling RPCs
- Returning safe, non-leaky responses

**Owns**
- HTTP contract with the web client
- Error code mapping
- Rate limiting (if added)

**Must not**
- Write to tables directly
- Contain business rules (those live in RPCs)
- Return raw database errors

**Reviews**
- Security and validation logic

---

## Supabase / DB

**Primary responsibility**
- Data integrity and safety

**Owns**
- Tables and schemas
- RPCs (SECURITY DEFINER)
- Indexes and migrations

**Must review**
- Any new RPC
- Any schema or contract change
- Any change affecting public data exposure

**Can block**
- Unsafe data access
- Missing RLS protections
- Logic leaking into Edge Functions

---

## Test

**Primary responsibility**
- Confidence and regression protection

**Owns**
- Route tests
- Edge function tests
- Contract coverage
- Fallback path tests

**Must review**
- Any change touching onboarding, join, or public pages

**Can block**
- Changes without sufficient coverage
- Changes that weaken fallback guarantees

---

## Docs

**Primary responsibility**
- Keeping system knowledge accurate and legible

**Owns**
- AGENTS.md
- contracts/*
- docs/*

**Must review**
- Any change that affects behavior or authority

---

## Release

**Primary responsibility**
- Deployment safety

**Owns**
- Vercel configuration
- Environment variables
- Preview vs production parity

**Must review**
- CI/CD changes
- Domain or routing config changes

**Can block**
- Changes that risk production stability

---

## Escalation Rules

- If a change affects **social safety or power dynamics** → Planner decides
- If a change affects **data exposure** → DB decides
- If a change affects **deep links** → Deep Linking decides
- If roles disagree → Planner resolves

---

## Role Philosophy

Roles exist to:
- slow down risky changes
- protect users from harm
- protect contributors from accidental responsibility

No role exists to “ship faster at all costs”.
