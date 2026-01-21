---
Domain: Kinly
Capability: Components
Scope: shared
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
---

> This document defines behavioral contracts, not implementation.
> Platforms may differ visually only where explicitly stated.

# Kinly Component Specifications

This document defines the **behavioral contract** for UI components that must
be implemented on both Flutter and Web platforms. It does NOT contain code—
only specifications.

## Buttons

### Filled Button (Primary CTA)

| Property          | Value                          |
|-------------------|--------------------------------|
| Min height        | 48px                           |
| Border radius     | `radius.md` (12px)             |
| Background        | `color.semantic.primary`       |
| Foreground        | `color.on-primary` (white)     |
| Typography        | `typography.label-medium`      |
| Disabled opacity  | `opacity.muted` (0.40)         |

**States:**
- `default`: Normal appearance
- `hover/focus`: Slight elevation increase (web: box-shadow, Flutter: Material InkWell)
- `pressed`: Darker shade (10% black mix)
- `disabled`: Reduced opacity, no pointer events

### Outlined Button (Secondary)

| Property          | Value                          |
|-------------------|--------------------------------|
| Min height        | 44px                           |
| Border radius     | `radius.md` (12px)             |
| Border            | 1px `color.semantic.primary`   |
| Background        | transparent                    |
| Foreground        | `color.semantic.primary`       |
| Typography        | `typography.label-medium`      |

**Dark mode adjustment:** Border and foreground use `outline` color instead.

### Text Button

| Property          | Value                          |
|-------------------|--------------------------------|
| Padding           | `spacing.m` horizontal         |
| Background        | transparent                    |
| Foreground        | `color.semantic.primary`       |
| Typography        | `typography.label-medium`      |

---

## Cards

### Action Card

| Property          | Value                          |
|-------------------|--------------------------------|
| Border radius     | `radius.md` (12px)             |
| Elevation         | `elevation.level1`             |
| Padding           | `spacing.l` (16px)             |
| Background        | `surface-container-low`        |

**Tap behavior:** Ripple effect (Flutter) / subtle scale (web)

### Section Card

| Property          | Value                          |
|-------------------|--------------------------------|
| Border radius     | `radius.lg` (16px)             |
| Elevation         | `elevation.level2`             |
| Padding           | `spacing.xl` (24px)            |
| Background        | Per-section color from palette |

---

## Inputs

### Text Field

| Property          | Value                          |
|-------------------|--------------------------------|
| Height            | 56px (with label), 48px (dense)|
| Border radius     | `radius.sm` (8px)              |
| Border            | 1px `outline`                  |
| Focus border      | 2px `color.semantic.primary`   |
| Error border      | 2px `color.semantic.error`     |
| Typography        | `typography.body-medium`       |
| Label             | `typography.body-small`        |

---

## Lists

### List Tile

| Property          | Value                          |
|-------------------|--------------------------------|
| Min height        | 56px                           |
| Padding           | `spacing.l` horizontal         |
| Leading icon size | `size.icon.md` (24px)          |
| Trailing icon     | `size.icon.sm` (16px)          |
| Title             | `typography.body-large`        |
| Subtitle          | `typography.body-small`        |

---

## Navigation

### App Bar

| Property          | Value                          |
|-------------------|--------------------------------|
| Height            | `size.toolbar` (56px)          |
| Background        | `surface`                      |
| Elevation         | 0 (flat)                       |
| Title             | `typography.title-large`       |

### Bottom Navigation

| Property          | Value                          |
|-------------------|--------------------------------|
| Height            | `size.bottom-nav` (64px)       |
| Icon size         | `size.icon.md` (24px)          |
| Label             | `typography.label-small`       |
| Active color      | `color.semantic.primary`       |
| Inactive color    | `on-surface` @ 60% opacity     |

---

## Accessibility Requirements

All components MUST:

1. **Touch targets**: Minimum 48x48px interactive area
2. **Color contrast**: 4.5:1 for text, 3:1 for large text
3. **Focus indicators**: Visible focus ring using `opacity.halo`
4. **Motion**: Respect `prefers-reduced-motion` (skip animations)
5. **Screen readers**: Proper semantic labels

---

## Animation Patterns

| Animation Type    | Duration              | Easing                |
|-------------------|-----------------------|-----------------------|
| Button press      | `motion.fast` (120ms) | `motion.standard`     |
| Page transition   | `motion.medium` (200ms)| `motion.decelerate`  |
| Modal entrance    | `motion.slow` (300ms) | `motion.emotional`    |
| Micro-interaction | `motion.snappy` (160ms)| `motion.standard`    |