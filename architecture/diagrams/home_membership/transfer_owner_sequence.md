---
Domain: Diagrams
Capability: Transfer Owner Sequence
Scope: platform
Artifact-Type: architecture
Stability: evolving
Status: draft
Version: v1.0
---

```mermaid
sequenceDiagram
  actor Owner
  participant App
  participant RPC as homes.transfer_owner
  participant DB

  Owner->>App: Initiate transfer(new_owner_id)
  App->>RPC: transfer_owner(home_id, new_owner_id)
  RPC->>DB: assert caller == homes.owner_id
  RPC->>DB: assert new_owner_id in MEMBERSHIP and is_current
  RPC->>DB: update HOMES.owner_id = new_owner_id
  RPC-->>App: ok
  Note right of RPC: Owner may now leave via homes.leave()
```