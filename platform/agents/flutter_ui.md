---
Domain: Agents
Capability: Flutter Ui
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Flutter UI Agent

Template: Context → Objectives → Constraints → Contracts → DoD → Risks → Outputs

Responsibilities
- Implement screens (Welcome, Create, Join, Hub) with i18n.
- Navigation and deep link entry points (consume adapter APIs).
- No direct Supabase; consume BLoC states/events only.

Constraints
- All strings via `S.of(context)`.
- Widget tests ≥1 per screen.

Outputs
- UI code diffs, widget tests, screenshots/GIFs of happy paths.
