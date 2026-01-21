---
Domain: Diagrams
Capability: Home State
Scope: platform
Artifact-Type: architecture
Stability: evolving
Status: draft
Version: v1.0
---

```mermaid
stateDiagram-v2
  [*] --> inactive

  inactive --> active: create_home(owner set)
  active --> inactive: last_owner_leaves [no other members]
  active --> active: transfer_owner [new_owner set]
  active --> active: member_joins / member_leaves

  note right of active
    Invariant: owner_count == 1
    Guard to stay active: owner_id != null
  end note
```

See `docs/diagrams/chores/chore_flow.md` for the chore lifecycle that builds on top of active homes.