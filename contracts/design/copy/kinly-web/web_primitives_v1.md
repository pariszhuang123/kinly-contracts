# Contract — Web Primitives v1.0

**Domain:** Web UI  
**Capability:** Primitive-based UI composition  
**Status:** Active  
**Registry:** contracts/contracts_registry.md  
**Applies to:** kinly-web (Next.js App Router)

---

## Purpose

This contract defines the mandatory primitive layer for Kinly Web.

Its goals are to:

- ensure all UI is composed from a small, stable set of primitives
- guarantee visual and behavioral consistency across pages
- prevent styling and markup drift
- allow global UI changes by editing tokens or primitives only

This contract is a consumer of:

- **Contract — Web Tokens Build & Delivery v1.0**

---

## Core Principles

1. **No raw UI in pages** — Primitives are the only place styling lives
2. **Tokens, not values** — All visual values come from CSS variables
3. **Composition over configuration** — Build complex UI from simple primitives
4. **No className escape hatch** — Primitives do not accept className props
5. **Web ≠ Flutter, but decisions align**

---

## Definitions

**Primitive**  
A lowest-level UI component that:
- renders semantic HTML
- applies design tokens
- exposes a limited, documented API
- contains styling logic
- does NOT accept className

**Composite Component**  
A reusable component built from primitives (e.g. Hero, InstallButtons).

**Feature UI**  
Screens and flows that compose primitives and composites. Feature UI MUST NOT introduce new styling systems.

---

## Directory Contract

The following structure is REQUIRED:

```
app/                     # Next routes (thin composition only)
components/
  primitives/            # THIS CONTRACT APPLIES HERE
    button/
    text/
    heading/
    card/
    input/
    stack/
    shell/
    ...
  composites/            # built from primitives
  index.ts               # public surface
styles/
  generated/tokens.css   # auto-generated (read-only)
```

Note: `features/` directory is NOT required for kinly-web v1 (no authenticated sessions).

---

## Styling Rules

### Where styling is allowed

- `components/primitives/**`
- `components/composites/**`
- `styles/**`

### Where styling is forbidden

- `app/**`

### Styling source

All visual values MUST come from CSS variables generated from tokens.

Hardcoded values are forbidden unless required for accessibility/behavior and no token exists yet.

---

## Required Primitive Set (v1)

The following primitives MUST exist before expanding feature UI.

### Layout

#### KinlyShell

**Purpose:**
- enforce max content width
- apply horizontal gutters
- center content consistently

**Uses:**
- `size.max-content-width`
- `spacing.l` | `xl`

#### KinlyStack

**Purpose:**
- vertical / horizontal layout
- consistent spacing via tokens

**Required props:**
- `direction`: `"vertical"` | `"horizontal"`
- `gap`: `"xxs"` | `"xs"` | `"s"` | `"m"` | `"l"` | `"xl"`
- `align?`
- `justify?`
- `wrap?`

---

### Typography

#### KinlyText

**Purpose:**
- all body text, labels, helper text

**Required props:**
- `variant`: `bodyLarge` | `bodyMedium` | `bodySmall` | `labelMedium` | `labelSmall`
- `tone`: `default` | `muted` | `danger` | `success` | `warning` | `info`
- `as?`: `p` | `span` | `div`

#### KinlyHeading

**Purpose:**
- all headings

**Required props:**
- `level`: `1` | `2` | `3`
- `as?`: `h1` | `h2` | `h3` (defaults map to level)

---

### Actions & Navigation

#### KinlyButton

**Purpose:**
- all interactive buttons and CTA links

**Required props:**
- `variant`: `filled` | `outlined` | `ghost`
- `size`: `sm` | `md` | `lg`
- `disabled?`
- `isLoading?`
- `href?` (renders as link-button)

**Rules:**
- MUST meet `size.touch-target.min`
- MUST implement focus-visible styling using `--k-web-focus-ring`
- MUST animate using motion tokens

#### KinlyLink

**Purpose:**
- inline links within text

**Rules:**
- MUST use semantic `<a>`
- MUST use link color tokens
- MUST expose focus-visible styling

---

### Surfaces

#### KinlyCard

**Purpose:**
- surface containers (lists, panels, info blocks)

**Required props:**
- `variant`: `surface` | `surfaceContainer` | `surfaceContainerHigh`

**Uses:**
- surface tokens
- radius tokens
- elevation → `--k-web-shadow-color`

#### KinlyDivider

**Purpose:**
- visual separation

**Uses:**
- outline / opacity tokens

---

### Forms

#### KinlyField

**Purpose:**
- label + hint + error layout

**Slots:**
- label
- control
- hint
- error

#### KinlyInput

**Purpose:**
- text / email / password inputs

**Rules:**
- MUST be wrapped by KinlyField
- MUST implement focus ring using `--k-web-focus-ring`
- MUST surface error + disabled states via tokens

---

## Raw Element Restrictions

Outside `components/primitives/**`, the following elements are FORBIDDEN:

| Raw Element | Use Instead |
|-------------|-------------|
| `<button>` | KinlyButton |
| `<a>` | KinlyLink or KinlyButton href |
| `<p>` | KinlyText |
| `<h1>`–`<h6>` | KinlyHeading |
| `<input>` | KinlyInput |

**Allowed raw elements** (when semantically required):
- `main`, `section`, `header`, `footer`, `nav`, `ul`, `ol`, `li`

---

## Accessibility Requirements

All primitives MUST:

- respect `size.touch-target.min`
- support keyboard navigation
- expose visible focus states via `--k-web-focus-ring`
- preserve semantic HTML roles

---

## Lint & Enforcement

This contract MUST be enforced via ESLint:

**Required rules:**
- `react/forbid-elements` for restricted tags
- `no-restricted-imports` to prevent deep/internal imports

CI MUST fail on violations.

---

## Change Management

### Versioning

- Breaking changes to primitive APIs require a major version bump
- Token-derived variable names used by primitives are part of public API

### Exceptions

Allowed only when:
- native element is required for platform constraints
- documented inline with: `// CONTRACT_EXCEPTION(web_primitives_v1): reason`

---

## Non-Goals

This contract does NOT:

- define page layouts
- define copy tone
- require pixel parity with Flutter
- define composites or features

---

## Success Criteria

This contract is successful when:

- pages contain almost no className
- UI changes can be made by editing tokens or primitives only
- adding a new page feels like assembling Lego, not inventing CSS

---

## Change Log

| Date | Change | Approved By |
|------|--------|-------------|
| 2025-01-20 | Initial contract created | Planner |
