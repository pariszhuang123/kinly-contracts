---
Domain: Coordination
Capability: Dependencies
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Environment Dependencies

Tooling
- Flutter channel: stable (pin via CI)
- Dart: follows Flutter stable
- Supabase CLI: latest (pinned in CI via `supabase/setup-cli@v1`)

Local Notes
- iOS builds require Xcode on macOS
- Android builds require Android SDK/NDK as per Flutter docs
- psql optional for local DB introspection

CI Notes
- `GITHUB_TOKEN` scoped to comment on PRs
- Secrets: `SUPABASE_ACCESS_TOKEN`, `SUPABASE_DEV_REF`, `SUPABASE_PROD_REF`