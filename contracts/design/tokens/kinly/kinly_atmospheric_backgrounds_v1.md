---
Domain: Kinly
Capability: Atmospheric Backgrounds
Scope: shared
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
---

## Kinly Atmospheric Backgrounds Contract v1

- Status: Draft
- Owner: Planner (policy), Release (CI enforcement), all agents (compliance)
- Scope: Flutter app (`lib/**`), design system tokens, theme helpers
- Non-breaking: Yes (additive presentation layer)

### Dependencies and precedence

Depends on:

- [kinly_foundation_colors_v1.md](kinly_foundation_colors_v1.md)
- [kinly_derived_color_engine_v1.md](kinly_derived_color_engine_v1.md)
- [kinly_control_color_tokens_v1.md](kinly_control_color_tokens_v1.md)
- [kinly_foundation_surfaces_amendment_v1.md](kinly_foundation_surfaces_amendment_v1.md)
- [kinly_dark_mode_refinement_amendment_v1.md](kinly_dark_mode_refinement_amendment_v1.md)
- [kinly_design_system_v1.md](kinly_design_system_v1.md)

Precedence:

1. Foundation color constraints remain immutable. No new hex literals.
2. Derived engine composition rules remain the baseline for all UI colors.
   Scrims, surfaces, and all other visible colors MUST come through the
   derived engine, not from foundation colors directly
   (Derived Color Engine §1, §2, §11).
3. Foundation surfaces amendment governs ownership of top-level destinations.
4. This contract adds an **optional presentation layer** for atmospheric
   backgrounds. It does NOT replace typography, spacing, color semantics,
   button hierarchy, card structure, navigation patterns, or interaction states.

---

## 1) Purpose

Implement atmospheric backgrounds as a supporting visual layer that:

- strengthens Kinly's "home feeling"
- remains secondary to usability
- preserves readability and accessibility
- reuses a small approved token set
- never becomes page-by-page decoration

---

## 2) Visual stack (required)

Every atmospheric screen MUST use this stack:

```
background image → scrim → surface / card → content
```

Text, icons, inputs, and controls MUST NOT sit directly on the raw image.

---

## 3) Appearance mode

Kinly MUST respect the user's selected appearance mode.

- Follow system light / dark mode.
- Do NOT introduce a separate Kinly scheduling system.
- Do NOT override system appearance automatically.
- Appearance MUST be resolved via the Kinly theme / token layer, not via
  widget-side `Brightness` checks (per Derived Color Engine §2).

Atmospheric variation happens **within** light or dark mode, not instead of it.

---

## 4) Accessibility

Minimum contrast requirements (per Derived Color Engine §9):

| Element                             | Ratio |
|-------------------------------------|-------|
| Normal text                         | 4.5:1 |
| Large text                          | 3:1   |
| Meaningful UI components and states | 3:1   |

If readability is at risk, apply mitigations in this order:

1. Increase scrim opacity
2. Strengthen surface
3. Reduce atmospheric strength
4. Remove atmosphere entirely

---

## 5) Real UI text only

All labels, buttons, headings, statuses, and messages MUST remain real UI text.
Essential UI copy MUST NOT be placed inside image assets.

---

## 6) Approved background tokens

Only the following tokens are approved. Codex MUST NOT generate or add one-off
backgrounds per feature or page.

**Dark**

| Token             |
|-------------------|
| `bg_dark_calm`    |
| `bg_dark_warm`    |
| `bg_dark_neutral` |

**Light**

| Token              |
|--------------------|
| `bg_light_warm`    |
| `bg_light_neutral` |
| `bg_light_glow`    |

Asset bindings for these tokens MUST be defined in a single central file
(recommended: `lib/core/theme/atmosphere/kinly_atmosphere_assets.dart`).
No other file may introduce background asset references.

---

## 7) Page classification model

Every screen MUST be classified into one of four categories before atmosphere
is applied.

### Emotional

Used where mood is part of the value.

| Mode  | Token           |
|-------|-----------------|
| Dark  | `bg_dark_warm`  |
| Light | `bg_light_glow` |

### Action

Used where users coordinate or complete lightweight work.

| Mode  | Token            |
|-------|------------------|
| Dark  | `bg_dark_calm`   |
| Light | `bg_light_warm`  |

### Structured

Used where scanning and clarity matter more than mood.

| Mode  | Token               |
|-------|---------------------|
| Dark  | `bg_dark_neutral`   |
| Light | `bg_light_neutral`  |

### Utility

Used where users edit, configure, or enter precise information.

- No atmospheric image.
- Use solid theme background only (derived surface tokens).

---

## 8) Scrim rules

### Dark mode defaults

| Category   | Opacity range |
|------------|---------------|
| Emotional  | 0.38 – 0.45  |
| Action     | 0.50 – 0.55  |
| Structured | 0.58 – 0.65  |
| Utility    | no image      |

### Light mode defaults

| Category   | Opacity range |
|------------|---------------|
| Emotional  | 0.60 – 0.65  |
| Action     | 0.72 – 0.75  |
| Structured | 0.80 – 0.85  |
| Utility    | no image      |

### Scrim color derivation

Scrim base color MUST be resolved from the **derived** surface token family,
not from foundation colors directly.

- Dark scrim base: `scheme.surface` (the dark-mode derived surface)
- Light scrim base: `scheme.surface` (the light-mode derived surface)

Scrim composition MUST happen inside the theme / token layer. Widgets MUST NOT
apply scrim colors or opacity directly.

This ensures compliance with:

- Foundation Colors §4: no hex literals outside the foundation file
- Derived Color Engine §2: foundation colors never appear directly in UI
- Derived Color Engine §11: no per-feature color logic outside the engine

### Tuning rules

- Increase scrim before changing the image.
- Do NOT reduce scrim just because the image looks nicer.
- Per-screen scrim values within the category range are tunable at
  implementation time; the contract governs the range, not exact values.

---

## 9) Surface rules

Atmosphere MUST NEVER be the main reading surface.

Content above the scrim MUST use existing derived surface tokens:

- Reading surfaces: `surfaceContainer`, `surfaceContainerHigh`,
  `surfaceContainerHighest` (per Derived Color Engine §6)
- Borders: `outline` / `outlineVariant` (per Derived Color Engine §6)
- Control colors: unchanged, per Control Color Tokens contract

### Dark mode

- Content sits inside protected cards / containers using derived
  `surfaceContainer*` tokens.
- Optional `outlineVariant` border for separation.

### Light mode

- Content sits inside cards using derived `surfaceContainer*` or
  `surfaceBright` tokens.
- Optional `outlineVariant` border or standard elevation.

### Hard rules

- If a screen has multiple text blocks, each block MUST sit on a surface.
- List rows SHOULD have their own surface or grouped surface treatment.
- Blur and frosted-glass effects are NOT approved in v1. If needed, they
  require a separate renderer contract amendment.

---

## 10) Ownership

### Who sets atmosphere

Only the **route-level surface root** (foundation surface or route screen) MAY
set page atmosphere. This aligns with the Foundation Surfaces Amendment §2:
surfaces own layout, features own content.

- Feature contribution widgets MUST NOT set or override page-level atmosphere.
- Feature widgets register into surface slots; they do not control the
  background behind them.

### New / unmapped screens

Any screen not listed in the screen registry (§11) resolves to **utility**
(no atmosphere) by default. Atmosphere is opt-in via explicit registration.

CI does NOT fail for unregistered screens. CI fails only if a screen attempts
to render atmosphere without a registered entry.

### Dialogs, bottom sheets, and overlays

- Dialogs and bottom sheets use Kinly derived surface tokens
  (`surfaceContainerHigh` or equivalent).
- They do NOT render their own atmospheric background.
- They sit above the scrim in the visual stack.

---

## 11) Screen registry

The registry maps `AppRouteNames.*` values to atmosphere categories. Registry
IDs MUST exactly match route name constants defined in
`lib/app/router/app_route_names.dart` (per Foundation Surfaces Amendment §7.1).

Codex MUST use these defaults unless a human updates this contract.

| Route name (`AppRouteNames.*`) | Category   |
|--------------------------------|------------|
| `today`                        | emotional  |
| `shoppingList`                 | action     |
| `tasksList`                    | action     |
| `addTask`                      | utility    |
| `bills`                        | structured |
| `manage`                       | structured |
| `hub`                          | structured |
| `sharedHouseDetails`           | structured |
| `preferences`                  | structured |
| `houseNorms`                   | structured |
| `houseShoutouts`               | emotional  |
| `profile`                      | utility    |
| `editProfile`                  | utility    |
| `settings`                     | utility    |
| `paymentDetails`               | utility    |
| `weeklyHousePulse`             | emotional  |
| `onboardingWelcome`            | emotional  |
| `onboardingAvatar`             | emotional  |
| `onboardingComplete`           | emotional  |

Onboarding screens that contain forms or precision input (e.g. preference
entry, profile setup) MUST be classified as **utility**, not emotional.

**Rules:**

- The category determines the token pair and scrim range (§7, §8).
  There is no per-screen token override; if a screen needs a different token
  pair, its category must change.
- Adding a new atmospheric screen requires updating this contract.
- Unregistered screens resolve to utility / no atmosphere by default.

---

## 12) Never-do list

Codex MUST NOT:

- Place body text directly on a busy image
- Use atmosphere on dense forms or precision-heavy screens
- Create new background assets per page or feature
- Use atmosphere to communicate urgency, state, or meaning
- Replace proper UI hierarchy with image contrast
- Remove the scrim for aesthetics
- Bake real UI text into an image
- Introduce new raw hex color literals for scrim or base colors
- Apply blur or frosted-glass effects (not approved in v1)
- Use foundation colors directly for scrim (must use derived tokens)

---

## 13) Acceptance criteria

### CI-enforceable (machine-checked)

1. Only approved background token IDs are used (see manifest §17)
2. No atmosphere rendered on screens without a registry entry
3. No raw color literals introduced for atmosphere (scrim, base)
4. Atmosphere configuration comes from the central theme helper, not
   feature-local constants
5. No background asset references outside the central asset file
6. Scrim colors resolve from derived surface tokens, not foundation colors

### Reviewer-verified (human judgment)

7. Text is instantly readable
8. Controls are clearly distinguishable
9. The background does not slow scanning
10. The screen still works with increased text size
11. The screen still feels like Kinly if the atmosphere is removed
12. Light and dark modes both respect system appearance behavior

If any criterion fails, Codex MUST reduce or remove atmosphere.

---

## 14) Fallback rule

If there is uncertainty, choose the clearer option.

Priority order:

1. Readability
2. Usability
3. Consistency
4. Atmosphere

Additional fallbacks:

- If route classification is uncertain → utility / no atmosphere
- If asset load fails or binding is missing → utility / no atmosphere
- If contrast cannot be confidently verified → increase scrim, then remove
- Backgrounds are **decorative only**: no semantics, no focus, no hit-testing

**Clarity wins.**

---

## 15) Implementation guidance (non-normative)

This section is advisory. Implementation details MAY evolve without updating
this contract, as long as the normative rules above are satisfied.

### Recommended pieces

- Category enum
- Atmosphere spec model
- Centralized background token → asset map
- Reusable atmosphere wrapper at the renderer level
- Shared scrim helper in the theme layer
- Per-screen mapping table keyed by `AppRouteNames.*`

### Suggested enum

```dart
enum AtmosphereCategory {
  emotional,
  action,
  structured,
  utility;

  bool get hasAtmosphere => this != utility;
}
```

### Suggested model

```dart
class AtmosphereSpec {
  final AtmosphereCategory category;
  final double? darkScrimOverride;
  final double? lightScrimOverride;

  const AtmosphereSpec({
    required this.category,
    this.darkScrimOverride,
    this.lightScrimOverride,
  });

  bool get enabled => category.hasAtmosphere;
}
```

`enabled` is derived from category — no contradictory states possible.
Scrim overrides are optional; defaults come from the category range (§8).

### Layer split

- `lib/core/theme/atmosphere/**` = data, specs, tokens, asset map (no widgets)
- `lib/renderer/**` = widget wrappers, Material integration, scaffold adapters

### Wrapper responsibility

1. Resolve current appearance via Kinly theme / token layer
2. Choose approved asset from the central map
3. Apply scrim using derived surface token as base color
4. Expose transparent scaffold body
5. Keep content on protected surfaces using derived `surfaceContainer*` tokens

---

## 16) Change control

- Exceptions to the screen registry or category mapping MUST be recorded by
  updating this contract, not by ad-hoc approval.
- Adding a new background token requires updating §6 and the manifest (§17).
- Bumping scrim ranges requires updating §8 and the manifest (§17).

---

## 17) Machine-readable manifest

This manifest is the canonical, parseable source for CI enforcement.

```contracts-json
{
  "domain": "design_system",
  "capability": "atmospheric_backgrounds",
  "approved_tokens": {
    "dark": ["bg_dark_calm", "bg_dark_warm", "bg_dark_neutral"],
    "light": ["bg_light_warm", "bg_light_neutral", "bg_light_glow"]
  },
  "categories": {
    "emotional": {
      "dark_token": "bg_dark_warm",
      "light_token": "bg_light_glow",
      "dark_scrim_range": [0.38, 0.45],
      "light_scrim_range": [0.60, 0.65]
    },
    "action": {
      "dark_token": "bg_dark_calm",
      "light_token": "bg_light_warm",
      "dark_scrim_range": [0.50, 0.55],
      "light_scrim_range": [0.72, 0.75]
    },
    "structured": {
      "dark_token": "bg_dark_neutral",
      "light_token": "bg_light_neutral",
      "dark_scrim_range": [0.58, 0.65],
      "light_scrim_range": [0.80, 0.85]
    },
    "utility": {
      "dark_token": null,
      "light_token": null,
      "dark_scrim_range": null,
      "light_scrim_range": null
    }
  },
  "screen_registry": {
    "today": "emotional",
    "shoppingList": "action",
    "tasksList": "action",
    "addTask": "utility",
    "bills": "structured",
    "manage": "structured",
    "hub": "structured",
    "sharedHouseDetails": "structured",
    "preferences": "structured",
    "houseNorms": "structured",
    "houseShoutouts": "emotional",
    "profile": "utility",
    "editProfile": "utility",
    "settings": "utility",
    "paymentDetails": "utility",
    "weeklyHousePulse": "emotional",
    "onboardingWelcome": "emotional",
    "onboardingAvatar": "emotional",
    "onboardingComplete": "emotional"
  },
  "default_unregistered": "utility",
  "central_asset_file": "lib/core/theme/atmosphere/kinly_atmosphere_assets.dart",
  "scrim_color_source": "scheme.surface",
  "blur_frost_approved": false,
  "entities": {},
  "functions": {},
  "rls": []
}
```
