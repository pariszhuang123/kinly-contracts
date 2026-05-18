---
Domain: Portfolio
Capability: Portfolio index
Scope: frontend
Artifact-Type: contract
Stability: evolving
Status: active
Version: v1.0
---

# Contract - Portfolio Index - v1.0

Registry: `contracts/contracts_registry.md`

---

## Purpose

This contract defines a public portfolio index route at:

`/portfolio`

The route exists to provide a human-readable directory of portfolio case
studies and working prototypes.

---

## Required Route Behavior

The canonical public route is:

`/portfolio`

The route must:

- render as a readable index page
- link directly to currently public portfolio entries
- remain safe to open in any browser context
- remain usable on desktop and mobile

The route must not:

- require authentication
- depend on backend persistence
- auto-redirect to a specific portfolio entry

---

## Required Information Architecture

The page must contain:

- a short framing section explaining that the page is a portfolio directory
- a visible list of portfolio entries
- direct links to each listed entry

The page may group entries by type, but it must preserve direct entry access.

---

## Content Rules

All copy must:

- remain concise
- describe each entry in plain language
- avoid overstating production maturity

---

## Status

This contract is active for the portfolio index route only.
