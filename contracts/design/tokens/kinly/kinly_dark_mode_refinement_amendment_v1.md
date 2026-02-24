---
Domain: Kinly
Capability: Dark Mode Refinement
Scope: shared
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
---

# Kinly Dark Mode Refinement Amendment v1.0

## Purpose

This amendment refines Kinly dark mode tokens so the UI remains deep, calm,
warm, and brand-forward while preserving hierarchy and accessibility.

The amendment is additive and does not replace existing foundation, derived, or
control token contracts.

## Scope and Non-Goals

### In scope

- token-level dark mode refinement
- tonal depth and separation rules for dark surfaces
- brand integrity rules for dark primary and accent behavior
- validation criteria for contrast and hierarchy

### Non-goals

- no layout or component structure redesign
- no new component families
- no feature flow changes
- no animation behavior changes
- no new raw color families outside existing foundation constraints

## Dependencies and Precedence

This amendment depends on and must be interpreted with:

- [kinly_foundation_colors_v1.md](kinly_foundation_colors_v1.md)
- [kinly_derived_color_engine_v1.md](kinly_derived_color_engine_v1.md)
- [kinly_control_color_tokens_v1.md](kinly_control_color_tokens_v1.md)
- [kinly_design_system_v1.md](kinly_design_system_v1.md)

Runtime reference:

- `kinly_palette.dart` is the implementation source of truth for runtime
  derivation behavior and token plumbing.

Precedence:

1. Foundation color constraints remain immutable.
2. Derived engine composition rules remain the baseline.
3. This amendment tightens dark-mode quality thresholds and role mapping.
4. If wording conflicts, this amendment governs dark refinement requirements only.

## Definitions

### DeltaL*

`DeltaL*` is the absolute difference in CIE L* lightness between two resolved
tokens in dark mode:

`DeltaL* = abs(L*_a - L*_b)`

L* values must be computed from sRGB using D65/2deg conversion.

### ContrastRatio

`ContrastRatio` uses WCAG relative luminance:

`(L1 + 0.05) / (L2 + 0.05)`, where `L1 >= L2`.

### SaturationDelta

`SaturationDelta` is the dark-minus-light delta in HSL saturation percentage for
the same semantic role:

`SaturationDelta = S_dark - S_light`

### HueDrift

`HueDrift` is the minimum absolute hue-angle distance between light and dark
variants of the same semantic role:

`HueDrift = min(abs(H_dark - H_light), 360 - abs(H_dark - H_light))`

## Normative Rules

1. Dark surface tokens MUST be brand-tinted and MUST NOT form a neutral gray-only ramp.
2. `backgroundPrimary -> backgroundSecondary` MUST maintain `DeltaL* >= 6` (target `6..10`).
3. `backgroundSecondary -> cardPrimary` MUST maintain `DeltaL* >= 6` (target `6..10`).
4. `backgroundPrimary -> cardPrimary` MUST maintain `DeltaL*` in `12..16`.
5. `DeltaL* >= 4` is allowed only for non-primary intermediate tiers.
6. Body text on primary dark surfaces MUST meet `ContrastRatio >= 4.5:1`.
7. Large text and iconography on primary dark surfaces MUST meet `ContrastRatio >= 3.0:1`.
8. Dark `primary` MUST preserve brand identity with `HueDrift <= 8deg` from light `primary`.
9. Dark `primary` saturation MUST satisfy `SaturationDelta in [-10, +10]`.
10. Base dark surfaces MUST NOT rely on stacked overlays for foundational tone construction.
11. Text hierarchy MUST expose explicit semantic roles: `textPrimary`, `textSecondary`, `textMuted`, `textOnPrimary`, `textOnAccent`.
12. Unnamed gray text usage in UI components MUST NOT be introduced.

## Canonical Dark Token Role Matrix

The following mapping is the canonical bridge from conceptual dark-mode roles to
the current token system (`contracts/design/tokens/shared/tokens.json`).

| Conceptual role | Existing semantic token family target | Constraint |
| --- | --- | --- |
| `backgroundPrimary` | `color.dark.surface` | Root background anchor. |
| `backgroundSecondary` | `color.dark.surface-container` | `DeltaL* >= 6` from `backgroundPrimary` (target `6..10`). |
| `surfacePrimary` | `color.dark.surface-container` | Shared section surface; no overlay stacking. |
| `surfaceSecondary` | `color.dark.surface-container-high` | Non-primary intermediate tier; `DeltaL* >= 4` from `surfacePrimary`. |
| `cardPrimary` | `color.dark.surface-container-high` | `DeltaL* >= 6` from `backgroundSecondary` (target `6..10`) and `DeltaL* 12..16` from `backgroundPrimary`. |
| `cardSecondary` | `color.dark.primary-container` | Emphasized card tier; contrast rules still apply. |
| `primary` | `color.dark.primary` | `HueDrift <= 8deg`; `SaturationDelta in [-10, +10]`. |
| `primaryContainer` | `color.dark.primary-container` | Must remain visually distinct from card tiers. |
| `accent` | `color.dark.tertiary` | Accent must remain immediately perceivable on dark surfaces. |
| `accentContainer` | `color.dark.tertiary-container` | Must not collapse with adjacent surfaces. |
| `textPrimary` | `color.dark.on-surface` | `ContrastRatio >= 4.5:1` on primary surfaces. |
| `textSecondary` | `color.dark.secondary` (named semantic alias required) | Must remain readable and distinct from muted text. |
| `textMuted` | `color.dark.disabled` (named semantic alias required) | Must not replace primary content text. |
| `textOnPrimary` | `color.dark.on-primary` | `ContrastRatio >= 4.5:1` on `primary`. |
| `textOnAccent` | `color.dark.on-tertiary` | `ContrastRatio >= 4.5:1` on `accent`. |
| `borderSubtle` | `color.dark.outline-variant` | Subtle separation only; not primary dividers. |
| `borderStrong` | `color.dark.outline` | Primary divider and high-confidence boundaries. |

## Validation and Acceptance Criteria

An implementation of this amendment is accepted only if all checks pass.

1. Contrast verification:
   - all text/surface pairings satisfy WCAG AA thresholds above.
2. Tonal separation verification:
   - `backgroundPrimary -> backgroundSecondary` satisfies `DeltaL* >= 6` (target `6..10`).
   - `backgroundSecondary -> cardPrimary` satisfies `DeltaL* >= 6` (target `6..10`).
   - `backgroundPrimary -> cardPrimary` satisfies `DeltaL* 12..16`.
   - `DeltaL* >= 4` is used only for non-primary intermediate tiers.
3. Brand integrity verification:
   - dark `primary` satisfies `HueDrift <= 8deg`.
   - dark `primary` satisfies `SaturationDelta in [-10, +10]`.
4. Overlay audit:
   - no prohibited stacked overlay construction for base surfaces.
5. Grayscale hierarchy verification:
   - grayscale screenshot review still shows clear depth and content hierarchy.

## Rollout and Risk Mitigation

### Risks

- oversaturation can produce a cartoon-like tone
- low separation can recreate muddy depth
- excessive darkening can make the UI feel heavy
- excessive lifting can produce fake dark mode

### Mitigations

1. Apply changes incrementally and verify each tier against `DeltaL*` thresholds.
2. Run contrast checks before visual sign-off.
3. Validate hue/saturation guardrails before publishing token changes.
4. Gate rollout with paired quantitative checks and screenshot review.

## Informative Appendix: Emotional Benchmark (Non-Normative)

Target mood cues for stakeholder review:

- forest dusk
- warm lamp light
- calm evening
- home at night

Anti-target cues:

- concrete
- developer-tool gray
- asphalt
- generic dashboard

Stakeholder UAT note:

- Qualitative approval (including partner or household stakeholder feedback) is
  recommended but is non-blocking and does not replace normative checks.
