# Contract — Web Tokens Build & Delivery v1.0

**Domain:** Web Design System  
**Capability:** Token compilation + theme delivery  
**Status:** Active  
**Registry:** contracts/contracts_registry.md  
**Applies to:** kinly-web (Next.js)

---

## Purpose

This contract defines how Kinly Web:

- compiles `tokens.json` into CSS variables
- delivers theme-aware tokens to the UI
- derives web-only CSS conveniences (shadows/scrims) without polluting the token source
- guarantees deterministic builds in dev + CI

---

## Source of Truth

### Token source

- **File:** `contracts/design-system/tokens.json`
- **Format:** DTCG-compatible token JSON
- **Ownership:** shared across Flutter + Web

### Build tool

- **Tool:** Style Dictionary (`style-dictionary` npm package)

### Output artifacts

- **Generated CSS:** `app/styles/generated/tokens.css`
- **Generated file header:** MUST include a "do not edit" banner

---

## Theme Contract

### Theme selectors

The generated CSS MUST define tokens for:

- `:root` → shared + light as default
- `[data-theme="dark"]` → dark overrides
- `@media (prefers-color-scheme: dark)` → best-effort auto-dark when user has not explicitly chosen `data-theme="light"`

### Theme precedence

1. **Explicit attribute:** `[data-theme="light" | "dark"]` wins
2. **Otherwise:** `prefers-color-scheme` applies

---

## Derived Web-Only Values (Option B)

The token source MUST NOT contain platform-specific computed strings such as:

- `rgba(...)` shadows
- scrim overlays
- any CSS-only computed helpers

Instead, Style Dictionary MUST derive and output stable CSS variables:

### Required derived variables

- `--k-web-shadow-color`
- `--k-web-scrim-color`
- `--k-web-focus-ring`

### Derivation rules

- shadow/scrim base tint MUST be derived from `color.foundation.neutral.ink`
- alpha MUST be derived from:
  - `opacity.shadow-light` and `opacity.shadow-dark`
  - `opacity.scrim-light` and `opacity.scrim-dark`
- focus-ring MUST reference `--color-primary` (theme-aware)

These variables MUST be emitted inside the theme blocks so they switch with theme.

---

## Build & Runtime Integration

### Build scripts

The project MUST provide the following npm scripts:

| Script | Purpose |
|--------|---------|
| `tokens:build` | Builds tokens once into `app/styles/generated/tokens.css` |
| `tokens:watch` | Watches token source and regenerates CSS on change |
| `dev` | MUST run `tokens:build` before `next dev` |
| `build` | MUST run `tokens:build` before `next build` |

### CI requirements

- CI MUST run `npm run tokens:build` (directly or via `npm run build`)
- If token compilation fails, CI MUST fail

### Import requirements

- The Next.js app MUST import `app/styles/generated/tokens.css` globally (via `app/layout.tsx` or `app/globals.css`)
- No component or feature may "manually" load token CSS at runtime

---

## File Ownership & Edit Rules

### Allowed edits

- `contracts/design-system/tokens.json` (human-edited)
- `style-dictionary.config.mjs` (human-edited)
- any scripts calling Style Dictionary (human-edited)

### Forbidden edits

- `app/styles/generated/tokens.css` MUST NOT be edited by hand

### Git policy

**Option B (active):** Generated CSS is NOT committed.

- Pros: clean diffs, tokens always built fresh
- Cons: build pipeline must always run tokens build

The file `app/styles/generated/` MUST be in `.gitignore`.

---

## Validation

### Determinism

For the same `tokens.json`, `tokens.css` MUST be byte-stable (no timestamps other than the static banner).

### Token completeness

If any required token paths are missing:

- `color.foundation.neutral.ink`
- `opacity.shadow-light`, `opacity.shadow-dark`
- `opacity.scrim-light`, `opacity.scrim-dark`

Then token build MUST fail with a readable error.

---

## Change Management

### Versioning

- Token source `$version` MUST increment on breaking changes to names/paths
- Derived CSS var names (`--k-web-shadow-color`, `--k-web-scrim-color`, `--k-web-focus-ring`) are public API and MUST NOT change without a major version bump.

---

## Change Log

| Date | Change | Approved By |
|------|--------|-------------|
| 2025-01-20 | Initial contract created | Planner |
