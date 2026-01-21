---
Domain: Diagrams
Capability: Logout
Scope: platform
Artifact-Type: architecture
Stability: evolving
Status: draft
Version: v1.0
---

```mermaid
flowchart TD
  A[User taps Logout] --> B[Supabase auth.signOut]
  B --> C[Clear local session/cache]
  C --> D[Navigate to Welcome]
```
