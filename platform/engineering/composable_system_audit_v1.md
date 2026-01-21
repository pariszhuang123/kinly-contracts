---
Domain: Engineering
Capability: Composable System Audit
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

## Composable System Audit v1

- Scope: `lib/features/**/ui/*_screen.dart` and `lib/features/**/ui/*_surface.dart`
- Goal: Identify cross-feature surface imports and direct feature references that violate the Composable System Contract v1.

### Summary
- Hub surface now uses registry + slot contracts (see `lib/features/hub/ui/hub_surface_*`).
- Today surface now uses registry + slot contracts (see `lib/features/today/ui/today_surface_*`).
- Explore surface now uses registry + slot contracts (see `lib/features/explore/ui/explore_surface_*`).
- Flow surface now uses registry + slot contracts (see `lib/features/flow/ui/flow_surface_*`).
- Share surfaces now use registry + slot contracts (see `lib/features/share/ui/*_surface_*`).
- Paywall surface now uses registry + slot contracts (see `lib/features/paywall/ui/paywall_surface_*`).
- Welcome surface now uses registry + slot contracts (see `lib/features/welcome/ui/welcome_surface_*`).
- Home membership surfaces now use registry + slot contracts (see `lib/features/home_membership/**/ui/*_surface_*`).
- Several surfaces import other feature internals directly.
- Most violations are in aggregator or cross-feature flows (Today, Share, Paywall, Welcome, Home Membership).

### Cross-feature surface imports (current)
- None detected after contract cleanups; shared contracts now live outside feature internals.

### Next migration targets
1) Migrate shared contracts from `lib/core/**` into the new `lib/contracts/**` layer.
2) Convert remaining cross-feature references to contract types or registries.
3) Flip `tool/check_composable_system.dart --strict` once the above are migrated.