---
Domain: Links
Capability: Marketing Surface Namespacing
Scope: frontend
Artifact-Type: contract
Stability: evolving
Status: active
Version: v1.1
---

# Contract - Kinly Marketing Surface Namespacing - v1.1

Registry: `contracts/contracts_registry.md`

---

## Purpose

This contract defines the canonical structure for Kinly-related web entry points
under `go.makinglifeeasie.com`.

It preserves the separation between:

- MakingLifeEasie as the company surface
- Kinly as the product surface
- Kinly discovery pages that support direct indexing of shared-living scenarios

---

## Canonical Ownership

### Root domain

`https://go.makinglifeeasie.com/`

The root path (`/`) MUST represent:

- MakingLifeEasie as a company
- mission, philosophy, and portfolio-level information

The root path (`/`) MUST NOT:

- be treated as a Kinly landing page
- host Kinly-specific onboarding flows
- implicitly redirect to any Kinly surface

### Kinly namespace

All Kinly-related web surfaces MUST live under:

`/kinly/*`

This namespace is exclusively owned by the Kinly product.

---

## Canonical Kinly Entry Points

### Kinly general marketing

`/kinly/general`

This path is the canonical Kinly landing page.

It MUST:

- be human-readable
- explain what Kinly is and why it exists
- remain safe to open in any browser context

It MUST NOT:

- auto-redirect to app stores
- trigger deep links

### Kinly scenario discovery hub

`/kinly/market`

This path is the canonical crawlable index for Kinly scenario landing pages.

It MUST:

- be human-readable
- link directly to all currently public `/kinly/market/:slug` pages
- remain readable without client-side interaction
- support search-engine discovery of scenario-specific public pages

It MUST NOT:

- replace `/kinly/general` as the canonical Kinly landing page
- auto-redirect to app stores
- hide scenario links behind scripts or gated UI

### Kinly scenario pages

`/kinly/market/:slug`

Scenario pages remain public, indexable product pages beneath the Kinly
namespace.

They SHOULD be discoverable from normal HTML links, not only from sitemap
submission.

---

## Explicit Non-Redirect Policy

Because Kinly has not yet been deployed publicly, no legacy redirects are
required.

Therefore:

- the root path (`/`) MUST NOT redirect to `/kinly/general`
- root-level legacy aliases (including `/get`) MUST NOT exist
- `/kinly/general` MUST remain the primary Kinly landing reference
- `/kinly/market` MUST remain a readable discovery hub, not a redirect

### Root-level `/get` prohibition

The root-level path `/get` MUST NOT:

- be implemented as a route
- be used as an alias to any Kinly surface
- redirect to `/kinly/general` or `/kinly/get`

Requests to `/get` SHOULD return `404 Not Found` (or equivalent).

---

## Kinly Acquisition & Install

Install, region gating, and interest-capture flows MAY exist under:

`/kinly/get`

This contract does not redefine acquisition behavior, but enforces that
`/kinly/get` is distinct from both `/kinly/general` and `/kinly/market`.

---

## Non-Goals

This contract does NOT:

- modify mobile deep-link behavior
- redefine invite or join flows
- introduce redirect logic
- impose analytics or attribution requirements

---

## Status

This contract is active and supersedes `links_marketing_surface_namespacing_v1.md`.
