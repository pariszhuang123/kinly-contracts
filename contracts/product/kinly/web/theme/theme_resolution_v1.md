---
Domain: Theme
Capability: Theme Resolution
Scope: frontend
Artifact-Type: contract
Stability: evolving
Status: active
Version: v1.0
---

# Contract: Theme Resolution - System / Light / Dark

## Purpose

Define a deterministic method to resolve the active UI theme for Kinly Web
so design tokens always map to one explicit theme at runtime.

## Definitions

### Theme Preference (user intent)
A persisted preference value chosen by the user (or defaulted):
- `system`
- `light`
- `dark`

### Resolved Theme (runtime state)
The concrete theme applied to tokens:
- `light`
- `dark`

### Root Theme Attribute
The HTML root attribute that declares the resolved theme:
- `data-theme="light"` or `data-theme="dark"`
Applied to the `<html>` element (`document.documentElement`).

## Invariants (MUST)

1. The UI MUST always resolve to exactly one `Resolved Theme` before the first
   meaningful paint:
   - `light` OR `dark`
   - never “unknown” or “unset” once initial paint occurs.
2. The UI MUST declare the resolved theme by setting:
   - `<html data-theme="light">` OR `<html data-theme="dark">`
3. Design tokens MUST be selected exclusively via `[data-theme]` selectors:
   - `:root[data-theme="light"] { ... }`
   - `:root[data-theme="dark"] { ... }`
4. `prefers-color-scheme` MUST NOT be the only mechanism for applying tokens.
   It MAY be used only as an input when resolving `system`.
5. Theme resolution MUST run before the first meaningful paint on the web to
   prevent flash-of-wrong-theme and token mismatch.
6. If reading persisted preference throws (e.g., storage blocked), resolution
   MUST fall back to `system` instead of erroring or stalling render.
7. The CSS `color-scheme` property on `html` MUST match the resolved theme once
   known, so UA controls (scrollbars, form fields) align with tokens.

## Resolution Rules

### Inputs
- `P` = Theme Preference from persistent storage (`localStorage.getItem("theme")`)
- `S` = System preference, derived from:
  `window.matchMedia("(prefers-color-scheme: dark)").matches`
  - if true → `S = dark`
  - else → `S = light`

### Valid Values
- If `P` is missing, empty, invalid, or unavailable (storage read throws)
  → treat `P = system`.

### Resolution
- If `P = dark`  → resolved theme = `dark`
- If `P = light` → resolved theme = `light`
- If `P = system` → resolved theme = `S`

### Output
- Set `<html data-theme="{resolved}">`
- Set `document.documentElement.style.colorScheme = "{resolved}"` to keep UA
  controls consistent with tokens.

## Storage Contract

- Storage location: `window.localStorage`
- Storage key: `theme`
- Allowed stored values: `system | light | dark`
- Default: `system`
- If storage is unavailable or throws, treat as default without blocking render.

## Web Implementation Requirements

1. Web MUST apply theme using a pre-paint initialization step:
   - inline `<script>` in `<head>` OR equivalent pre-hydration mechanism.
2. Initialization MUST:
   - read `localStorage.theme` in a `try/catch`
   - compute resolution using rules above
   - set `data-theme` on `<html>` before loading blocking CSS or hydration
   - set `style.colorScheme` on `<html>` to the same resolved value
3. After initialization, the DOM MUST satisfy:
   - `document.documentElement.getAttribute("data-theme")` is `"light"` or
     `"dark"`.
4. If the user preference is `system`, the web MAY listen for OS changes and
   update `data-theme` accordingly. If implemented, updates MUST be debounced
   (<= 200ms) and MUST set both `data-theme` and `colorScheme` together.

## Accessibility Requirements

1. Token sets MUST maintain readable contrast for muted/disabled text on both
   themes.
2. The resolved theme MUST not reduce text readability below WCAG AA for body
   text on primary surfaces.

## Observability / Debug Requirements (SHOULD)

1. A developer SHOULD be able to verify the active theme by inspecting:
   - `<html data-theme="...">`
   - `document.documentElement.style.colorScheme`
2. A developer SHOULD be able to verify token selection by checking the
   computed value of a representative token such as:
   - `--color-disabled`

## Non-Goals

- Defining the full token palette (that is a separate token contract).
- Defining user-facing UI for theme switching (toggle UI is separate).
- Enforcing theme persistence across devices (account sync is separate).

## Acceptance Tests

1. Default (no storage):
   - Given no `localStorage.theme`,
   - When system is dark,
   - Then `<html data-theme="dark">` and `colorScheme` is `"dark"`.
2. Forced dark:
   - Given `localStorage.theme = "dark"`,
   - Regardless of system,
   - Then `<html data-theme="dark">` and `colorScheme` is `"dark"`.
3. Forced light:
   - Given `localStorage.theme = "light"`,
   - Regardless of system,
   - Then `<html data-theme="light">` and `colorScheme` is `"light"`.
4. Invalid value:
   - Given `localStorage.theme = "banana"`,
   - Then treat as `system` and resolve via system preference.
5. No flash (web):
   - Theme attribute is set before first meaningful paint
     (no visible token switch on load).
6. Storage blocked:
   - Given `localStorage` throws on `getItem`,
   - Then resolution still completes, treating preference as `system`.
7. System change when preference is `system`:
   - Given `localStorage.theme = "system"`,
   - When `matchMedia("(prefers-color-scheme: dark)")` fires `change` to dark,
   - Then `<html data-theme="dark">` and `colorScheme` update within 200ms.
