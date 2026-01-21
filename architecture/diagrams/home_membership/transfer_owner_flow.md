---
Domain: Diagrams
Capability: Transfer Owner Flow
Scope: platform
Artifact-Type: architecture
Stability: evolving
Status: draft
Version: v1.0
---

```mermaid
flowchart TD
  A["Start: homes.transferOwner(homeId, newOwnerId)"] --> B{Home active?}
  B -- no --> X[Error: Forbidden]
  B -- yes --> C{Caller is current owner?}
  C -- no --> X
  C -- yes --> D{newOwnerId is active member?}
  D -- no --> Y[Error: Invalid/Not Found]
  D -- yes --> E[Set homes.ownerId = newOwnerId]
  E --> Z[Return OK]
```
