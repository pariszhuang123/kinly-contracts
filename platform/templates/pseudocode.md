---
Domain: Templates
Capability: Pseudocode
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Pseudocode Template — SPARC (P Phase)

Use this 1‑page template before implementation for each feature/story. Keep it concise and test‑oriented.

## Feature
- Title: <feature name>
- Contract version: v1 (link to docs/contracts/homes_v1.md)

## Preconditions
- Auth state, membership state, invite/home state relevant to the flow.

## Postconditions
- What must be true after success. Include state changes and emitted events.

## Flow (Pseudocode)
```
Given <initial state>
When  <action>
Then  <outcome>

Steps:
1. ...
2. ...
3. ...
```

## Error Cases / Guards
- Case A → Expected error/result
- Case B → Expected error/result

## State Transitions (optional)
- Diagram: link a Mermaid file in `docs/diagrams/`.

## Test Plan Map
- Reference test names or IDs that cover Given/When/Then above.

## Traceability Map (Spec/Pseudocode → Tests)
| Step (Given/When/Then or numbered) | Test name or link |
| --- | --- |
| ... | ... |