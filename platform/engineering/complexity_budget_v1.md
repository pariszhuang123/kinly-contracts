---
Domain: Engineering
Capability: Complexity Budget
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Complexity Budget Contract (v1)

Scope: Dart sources (Flutter client). Goal: keep logic reviewable, testable, and safe to change by capping cyclomatic complexity (CC) and nudging extraction when branches grow.

## Definitions
- **Cyclomatic Complexity (CC):** increases with `if/else if`, `switch` cases, loops, `catch`, and boolean chains (`&&`, `||`) in conditions.
- **Budget:** CC thresholds per function, BLoC handler, and file. Crossing a target requires extraction or a documented exception; hard caps require refactors.

## Budgets
- **Functions:** target ≤10; soft 11–15 (only if pure + has decision-path tests); hard ≥16 is not allowed.
- **BLoC handlers (`_on<Event>` / `mapEventToState` / inline `on<>()` callbacks):** target ≤12; hard ≥18 is not allowed.
- **Files:** target ≤60; soft 61–90 only if the file is UI composition only (widgets/layout, no domain/BLoC logic); hard ≥91 is not allowed. File CC is the sum of all function/method CCs in the file—reduce by extracting helpers or splitting files.

## Mandatory extraction when over target
When CC > target (10 for functions, 12 for handlers), extract at least one:
- Decision logic → pure helpers such as `*_decideNextState`, `*_computeOutcome`, `*_deriveLimits` (explicit inputs, return value, unit-testable).
- Validation → `validateX()` returning `null` or a typed error/result.
- Side effects → keep RPCs in repositories, analytics in `AnalyticsService`, navigation in UI/Navigator wrappers.
- Stable mappings → replace branching with lookup maps/tables when appropriate.

## Exceptions
- Document with `// CC_BUDGET_EXCEPTION: <reason> (expires: YYYY-MM-DD)`.
- Allowed reasons: interop glue (platform/plugin adapters), generated code shims, UI-only composition.
- Not allowed: “too hard”, “deadline”, “it’s only one function”.
- Expired exceptions must be removed or refactored; hard caps cannot be bypassed.

## Enforcement (CI + local)
- CI fails when: any function CC ≥16; any BLoC handler CC ≥18; any file CC ≥91 (generated code excluded).
- CI warns (non-blocking) when: functions 11–15; BLoC handlers 13–17; files 61–90.
- Exclusions: `**/*.g.dart`, `**/*.freezed.dart`, `**/*.gr.dart`, `**/generated/**`.

## Reporting (retro)
- Track weekly: top 10 functions by CC, top 10 files by CC, and CC delta week-over-week. Hotspot count should trend down even as total CC grows.

## Rule of thumb
- ✅ CC 7 handler that delegates to helpers + repository; CC 12 pure decision helper with tests.
- ❌ CC 22 `_onSubmitPaywall()` that mixes validation, RPC, navigation, and analytics; file-level CC 130 “everything in one file”.