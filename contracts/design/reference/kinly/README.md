---
Domain: Design
Capability: Readme
Scope: shared
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
---

> This design system is a shared contract between Kinly platforms.
> Any change here must be reflected in all consuming platforms
> (Flutter, Web, future surfaces).

# Kinly Design System

This directory contains the **single source of truth** for Kinly's design tokens
across Flutter (kinly_app) and Web (kinly_web) platforms.

## Architecture

```
docs/design-system/
├── tokens.json          # Platform-agnostic design tokens (source of truth)
├── README.md            # This file
└── components.md        # Component behavior specs (TODO)

Platforms consume tokens:
├── lib/renderer/material/theme/  # Flutter implementation
└── kinly_web/                    # Web implementation (TODO)
```

## Token Categories

| Category    | Description                              | Example                  |
|-------------|------------------------------------------|--------------------------|
| `color`     | Foundation colors, semantic colors, brand text | `#366D59` (Kinly Teal)  |
| `typography`| Font families, weights, and text styles  | DM Sans 40px bold        |
| `spacing`   | Layout spacing scale                     | `xxs`=2px → `xxxl`=40px  |
| `radius`    | Corner radius scale                      | `xs`=4px → `pill`=999px  |
| `elevation` | Shadow/depth levels (Material-aligned)   | level0=0 → level5=16     |
| `opacity`   | Alpha values for overlays, states        | `scrim`=0.50             |
| `motion`    | Durations and easing curves              | `fast`=120ms             |
| `size`      | Icon sizes, touch targets, layout        | `min-touch`=48px         |

## Usage

### Flutter (Current)

Flutter reads tokens from `lib/renderer/material/theme/foundation/` and derives
all runtime values in `kinly_palette.dart`. The token JSON here documents the
canonical values.

### Web (Recommended Setup)

**Option A: Manual CSS Variables**
```css
:root {
  /* From tokens.json */
  --color-primary: #366D59;
  --color-secondary: #8BAA91;
  --color-accent: #F6B73C;
  --spacing-s: 8px;
  --spacing-m: 12px;
  --radius-md: 12px;
  /* etc. */
}
```

**Option B: Style Dictionary (Automated)**

Install [Style Dictionary](https://amzn.github.io/style-dictionary/) to
auto-generate CSS/Tailwind/JS from `tokens.json`:

```bash
npm install style-dictionary
npx style-dictionary build --config ./style-dictionary.config.js
```

Example config:
```js
// style-dictionary.config.js
module.exports = {
  source: ['docs/design-system/tokens.json'],
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'kinly_web/src/styles/',
      files: [{
        destination: 'tokens.css',
        format: 'css/variables'
      }]
    },
    tailwind: {
      transformGroup: 'js',
      buildPath: 'kinly_web/',
      files: [{
        destination: 'tailwind.tokens.js',
        format: 'javascript/es6'
      }]
    }
  }
};
```

## Token Format

This file uses the [Design Tokens Community Group](https://design-tokens.github.io/community-group/format/)
JSON format for maximum compatibility with design tools.

## Modularization: What's Shareable?

| Shareable via tokens.json    | Must re-implement per platform |
|-----------------------------|-------------------------------|
| Colors (hex values)         | Widget/component code         |
| Typography scale            | State management (BLoC)       |
| Spacing scale               | Navigation                    |
| Radius scale                | Platform-specific APIs        |
| Elevation values            | Accessibility semantics       |
| Motion durations/easing     | i18n implementation           |
| Icon sizes                  | -                             |

## Updating Tokens

1. Edit `docs/design-system/tokens.json` (source of truth)
2. Update Flutter implementation in `lib/renderer/material/theme/foundation/`
3. Regenerate web tokens (if using Style Dictionary)
4. Update this README if adding new token categories

## Component Specs

See [components.md](components.md) for behavioral specifications of shared
components (buttons, cards, inputs, etc.) that must be re-implemented on each
platform.