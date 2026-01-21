---
Domain: Agents
Capability: Flutter Bloc
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Flutter BLoC Agent

Template: Context → Objectives → Constraints → Contracts → DoD → Risks → Outputs

Responsibilities
- Implement feature BLoCs for Auth and Home flows.
- Consume repositories only; expose states/events to UI.

Constraints
- No direct HTTP/Supabase.
- Unit tests for happy/error paths.

Outputs
- BLoC code diffs, unit tests, contract notes if repository interfaces change.
