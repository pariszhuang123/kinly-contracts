---
Domain: Agents
Capability: Deep Linking
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Deep Linking Agent

Template: Context → Objectives → Constraints → Contracts → DoD → Risks → Outputs

Responsibilities
- Define universal link/QR schema for join codes.
- Map deep links to navigation and preloaded actions.

Constraints
- Host/prefix TBD (e.g., kinly.app/join/:code) — confirm before release.
- Auth fallback: prompt OAuth before join RPC.

Outputs
- Deep link specs, route handlers, tests, and docs.
