---
Domain: Kinly
Capability: Core Ui Primitives
Scope: shared
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
---

# Kinly Core UI Primitives

Purpose: Shared widgets under `lib/core/ui/**` to keep spacing, colors,
directionality, and i18n consistent.

## Principles

- Design System tokens: spacing (xxs-xxxl), radius (xs-xl), elevation
  (level0-5), motion (easeStandard/Accelerate/Decelerate/Emotional +
  fast/medium/slow/snappy), color tokens, typography tokens.
- Use Kinly primitives only: buttons, snackbars, dialogs, bottom sheets, inputs;
  no raw Material equivalents.
- No hard-coded colors/paddings/text styles; use tokens via Theme extensions
  (Spacing, Corners, Elevations, Motion, KinlyColorTokens, KinlyTypography).
- Directionality safe padding/alignment; use
  EdgeInsetsDirectional/AlignmentDirectional.
- RTL/widget tests for new or changed screens when adding primitives.
- Accessibility baseline (v1):
  - Touch targets: ≥48dp for all tappable primitives.
  - Semantics: provide labels/roles on buttons/tiles/rows/avatar taps.
  - Motion: respect reduce-motion; default durations ≤250ms; use motion tokens.
  - Contrast: use Kinly color tokens only; palette is validated by contrast
    tests.
  - Text: i18n only (`S.of(context)`); ≥14sp styles from typography tokens.
- Avatars: use KinlyCircleAvatar with token sizes (24/40/56 diameters).
- Bottom sheets/dialogs must use KinlyBottomSheet / KinlyAlertDialog (token
  radius/elevation/motion).
- Directionality-safe APIs only; run `dart run tool/check_directionality.dart`.
- No hard-coded strings; use `S.of(context)`.
- Respect theme tokens (`Spacing`, `KinlySections`), light/dark, and
  accessibility.
- No `print`/`debugPrint`; use the logger when needed.

## Buttons

- `KinlyFilledButton` (text/icon, destructive, fullWidth, compact)
- `KinlyOutlinedButton` (text/icon, compact/fullWidth)
- `KinlyFab`, `KinlyAddTileButton`
- When to use: primary CTA = filled; secondary = outlined; tertiary/inline =
  text; destructive variants for irreversible actions.

## Feedback / Loading

- `KinlyLoader` (sizes/patterns).
- `KinlySnackBar` (standard success/error/info/warning snackbars; use instead of
  raw `SnackBar`; supports optional `accentColor` for section flavor while
  keeping semantic backgrounds).
- `house_pulse_strings.dart` (resolves pulse label keys to localized
  title/summary via Kinly l10n).
- `house_pulse_assets.dart` (maps pulse label image keys/states to asset paths
  under `assets/house_pulse_<version>/`; falls back to forming when unknown).

## Avatars & Media

- `KinlyCircleAvatar` (owner badge, fallback handling).
- `personal_profile_sheet.dart` (`PersonalProfileSheet`): avatar-driven personal
  profile access; uses KinlyBottomSheet + KinlyCircleAvatar.
- `enums/personal_profile_entry_source.dart`: enum to label entry provenance for
  personal profile navigation.
- Avatar selection rows reveal display names on selection (identity
  confirmation).
- Photo pickers/previews if shared.

## Inputs & Pickers

- `KinlyTextField` (tokenized text input)
- `KinlyDropdownField` (tokenized dropdown)
- `KinlyChoiceChip` (tokenized choice chip)
- `KinlyFilterChip` (tokenized filter chip)
- `KinlySegmentedControl` (tokenized segmented control)
- `KinlyTabBar` (inline tab bar for active/draft toggles)
- `KinlySearchField` (search variant with clear action)
- `KinlyDatePicker` and other shared pickers.
- `KinlySearchField` (search variant with clear action)

## Feedback / Inline

- `KinlyInfoBanner` (success/info/warning/error inline banner)

## Lists & States

- `KinlyListTile` (tokenized title/subtitle row)
- `KinlyBadge` (single primitive for status badges; uses `Corners.pill` for
  shape; default uses control tokens, use `accentColor` for section flavor,
  `destructive` for error/danger, or `backgroundColor`+`foregroundColor` for
  rare custom variants; `compact` controls padding; `maxLines` supports longer
  labels)
- `KinlyEmptyState` (icon/title/body + optional CTA)
- `kinly_section_card.dart` (`KinlySectionCard`): specialized section container
  with header, title/summary, visual (left/right), tags, footer, and optional
  tap/trailing.
- `enums/kinly_section_card_visual_position.dart`: enum for visual alignment
  (left/right) in `KinlySectionCard`.

## Media

- `KinlyPhotoCapture` (photo pick/preview tile)

## Layout & Spacing

- `Spacing` extension usage; surface/section color guidance from
  `KinlySections`.
- `KinlyScrollFade` (wraps any scrollable to apply top/bottom fade + removes
  overscroll glow; configurable fade fraction and edges).
- Opacity tokens: use `KinlyOpacity`
  (alphaXXS/XS/SM/MD/LG/XL/XXL/Halo/Muted/Scrim/Dim/Faint/FaintStrong/Opaque/OpaqueHigh/Shadow)
  instead of raw `withValues(alpha: ...)`. Match intent: overlays/gradients →
  XL/XXL, badges/tints → MD/LG, halos → Halo, scrims → Scrim, dim states →
  Dim/Faint/FaintStrong, near-opaque surfaces → Opaque/OpaqueHigh, shadows →
  Shadow. Do not use null-aware on required theme extensions (Spacing, Corners,
  KinlyOpacity, KinlyTypography).

## Adding or Changing a Primitive

1. Propose to Planner + Docs (intent, consumers, theme tokens, tests).
2. Build under `lib/core/ui/...`; keep directionality-safe; use `S.of(context)`.
3. Add widget tests (incl. RTL/golden where appropriate). Ensure a11y tests
   cover 48dp + semantics and reduce-motion where relevant.
4. Update this doc with API and examples.
5. Run `check_directionality` and `check_i18n` before landing.
6. `check_core_ui_primitives_doc` guardrail fails if a new `lib/core/ui/**`
   primitive is missing here; add it or create a temporary allowlist entry with
   rationale/expiry in `tool/core_ui_primitives_allowlist.txt`.

## Known Gaps / Backlog

- [List planned primitives or refactors here]