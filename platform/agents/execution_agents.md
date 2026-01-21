# Execution Agents — Kinly Web

Execution agents are **automated enforcers**.

They do not make product decisions.  
They do not infer intent.  
They do not negotiate.

Their role is to ensure that rules defined by governance agents and contracts
are consistently enforced and that unsafe changes are blocked early.

If an execution agent fails, a **human governance agent must decide what to do next**.

---

## Guiding Principles

- Execution agents enforce **rules**, not intent
- They are deterministic and boring (this is good)
- They must fail loudly and explain why
- They may block merges
- They may never change system behavior autonomously

Execution agents exist to reduce accidental harm, not to speed up delivery.

---

## Agent Overview

| Agent | Purpose | Blocks Merge |
|---|---|---|
| Contract Enforcement Agent | Prevents behavior drift from contracts | Yes |
| Routing Safety Agent | Prevents dead ends and unsafe redirects | Yes |
| Public Data Exposure Agent | Prevents leakage of private data | Yes |
| Environment Hygiene Agent | Prevents secret leakage | Yes |

---

## 1. Contract Enforcement Agent

**Purpose**  
Ensure that all behavioral changes are explicitly governed by versioned contracts.

**Enforces**
- Changes to routing, deep-link behavior, edge functions, or public pages
  must be accompanied by:
  - a contract version update, **or**
  - an explicit exemption marker

**Triggers on changes to**
- `/app/**`
- `/routes/**`
- `/edge/**`
- `/lib/deep_links/**`

**Pass conditions**
- A file under `/contracts/**` changed, **or**
- Commit contains an explicit marker:

NO_CONTRACT_CHANGE: <short justification>


**Failure message**
> Behavioral change detected without contract update or exemption.

**Ownership**
- Planner
- Docs

**Rationale**
Contracts are the source of truth.  
Silent behavior drift is forbidden.

---

## 2. Routing Safety Agent

**Purpose**  
Ensure that no user can be dead-ended, auto-redirected, or routed unsafely.

**Enforces**
- `/fallback` route always exists and renders safely
- No auto-deep-link on page load
- All join flows render store CTAs
- `next` parameters are internal paths only
- No open redirects (`https://`, `//`, etc.)

**Validation methods**
- Route tests
- Redirect logic inspection
- Query parameter sanitization tests

**Failure message**
> Unsafe routing behavior detected (dead-end, auto-redirect, or open redirect).

**Ownership**
- Deep Linking

**Rationale**
Routing errors cause immediate user loss and break trust.

---

## 3. Public Data Exposure Agent

**Purpose**  
Prevent accidental exposure of private or sensitive data on public pages.

**Enforces**
- Public pages (`/norms`, `/home`, etc.) render only allow-listed fields
- No private identifiers (user IDs, emails, roles)
- No member lists or internal state
- RPC responses match public schemas exactly

**Validation methods**
- Snapshot tests of public routes
- Response shape validation
- Schema allow-list assertions

**Failure message**
> Private or non-allow-listed data exposed on a public surface.

**Ownership**
- Supabase / DB

**Rationale**
Public pages are irreversible once indexed or shared.

---

## 4. Environment Hygiene Agent

**Purpose**  
Prevent secrets, internal URLs, or unsafe configuration from being committed
or exposed to the browser.

**Enforces**
- `.env.local` and `.env.*.local` are gitignored
- No secrets in `NEXT_PUBLIC_*`
- No hardcoded keys or credentials in code
- `.env.example` exists and documents required variables

**Validation methods**
- Git checks
- Static scanning
- Pattern matching for secrets

**Failure message**
> Environment hygiene violation (secret exposure risk).

**Ownership**
- Release

**Rationale**
Configuration mistakes are the most common cause of leaks.

---

## Non-Goals (Intentional)

Execution agents do NOT:
- write code
- generate migrations
- refactor logic
- infer contracts
- approve behavior changes

These responsibilities belong to governance agents.

---

## Escalation Rules

When an execution agent fails:
1. The failure reason must be read and understood
2. The owning governance agent decides:
 - update contract
 - add explicit exemption
 - fix implementation
3. Execution agents are never overridden silently

---

## Philosophy

Execution agents exist to:
- protect users you will never meet
- protect contributors from accidental responsibility
- protect system intent over time

They are guardians, not accelerators.

If an execution agent feels “annoying,” it is doing its job.
