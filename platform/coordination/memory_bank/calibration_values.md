---
Domain: Coordination
Capability: Calibration Values
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Calibration Values

Supabase CLI
- Login (CI/local): `supabase login --token $SUPABASE_ACCESS_TOKEN`
- Dev deploy: `supabase db push --project-ref $SUPABASE_DEV_REF`
- Prod deploy (gated): `supabase db push --project-ref $SUPABASE_PROD_REF`

Flutter CI/Test
- Test reporter: `flutter test --reporter expanded`
- Analyzer: `dart analyze --fatal-infos`
- Format check: `flutter format --set-exit-if-changed .`

Build Budgets
- APK growth: warn if >5% vs main (non-blocking).

Example Configuration (illustrative)
```
{
  "ci": {
    "test_timeout_ms": 30000,
    "retry_attempts": 0
  },
  "supabase": {
    "retry_attempts": 3,
    "retry_backoff_ms": 2000
  },
  "apk_budget": {
    "growth_warn_percent": 5
  }
}
```