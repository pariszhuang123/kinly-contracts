---
Domain: Links
Capability: Marketing Surface Namespacing
Scope: frontend
Artifact-Type: contract
Stability: evolving
Status: active
Version: v1.0
---

# Contract — Kinly Marketing Surface Namespacing — v1.0

Registry: `contracts/contracts_registry.md`

---

## Purpose

This contract defines the canonical structure for **Kinly-related web entry points** under `go.makinglifeeasie.com`.

It establishes a clear separation between:

* **MakingLifeEasie** (company-level surface)
* **Kinly** (product-level marketing and acquisition surfaces)

The intent is to ensure long-term clarity, avoid redirect debt, and support future multi-product expansion.

---

## Canonical Ownership (Normative)

### Root domain

```
https://go.makinglifeeasie.com/
```

The root path (`/`) MUST represent:

* MakingLifeEasie as a company
* mission, philosophy, and portfolio-level information

The root path (`/`) MUST NOT:

* be treated as a Kinly landing page
* host Kinly-specific marketing or onboarding copy
* implicitly redirect to any Kinly surface

---

### Kinly namespace

All Kinly-related web surfaces MUST live under:

```
/kinly/*
```

This namespace is exclusively owned by the Kinly product.

---

## Canonical Kinly Entry Point (Normative)

### Kinly general marketing

```
/kinly/general
```

This path is the **canonical Kinly landing page**.

All Kinly-related links, CTAs, QR codes, and references that previously pointed to the root path (`/`) MUST now point directly to:

```
/kinly/general
```

This page MUST:

* be human-readable
* explain what Kinly is and why it exists
* be safe to open in any browser context

This page MUST NOT:

* auto-redirect to app stores
* trigger deep links

This page MAY:

* perform **region gating** to determine whether to show App Store / Google Play CTAs (e.g., show store CTAs only for supported regions such as NZ, SG, and MY)

If region gating is applied:

* the page MUST still render meaningful, readable content even when store CTAs are hidden
* hiding store CTAs MUST NOT prevent a user from understanding what Kinly is or what to do next

---

## Explicit Non-Redirect Policy (Normative)

Because Kinly has not yet been deployed publicly, **no legacy redirects are required**.

Therefore:

* The root path (`/`) MUST NOT redirect to `/kinly/general`
* Root-level legacy aliases (including `/get`) MUST NOT exist
* `/kinly/general` MUST be referenced directly by all Kinly entry points
* No 301 or 302 redirects are required to support this contract

### Root-level `/get` prohibition

The root-level path:

```
/get
```

MUST NOT:

* be implemented as a route
* be used as an alias to any Kinly surface
* redirect to `/kinly/general` or `/kinly/get`

Requests to `/get` SHOULD return `404 Not Found` (or an equivalent "no such page" response) to avoid accidental coupling between company root paths and Kinly product surfaces.

This policy intentionally preserves the root domain for future MakingLifeEasie use.

---

## Kinly Acquisition & Install (Informative)

Install, region gating, and interest-capture flows MAY exist under:

```
/kinly/get
```

This contract does not redefine acquisition behavior, but enforces that `/kinly/get` is distinct from `/kinly/general`.

---

## Non-Goals (Explicit)

This contract does NOT:

* modify mobile deep-link behavior
* redefine invite or join flows
* introduce redirect logic
* impose analytics or attribution requirements

---

## Rationale (Non-Normative)

Directly referencing `/kinly/general` avoids permanent redirects, browser caching issues, and future SEO conflicts when the root domain is later promoted to a full company homepage.

This approach favors explicitness over convenience and aligns with contract-first development principles.

---

## Future Compatibility

This structure supports additional products without restructuring the root domain:

```
/kinly-dating/*
/kinly-rent/*
```

---

## Status

This contract is **active** and MUST be implemented before any public-facing Kinly links are distributed.
