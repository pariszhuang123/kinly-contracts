---
Domain: Runbooks
Capability: Ci Secrets
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# CI Secrets: What Goes Where

Keep private keys and server-side credentials in GitHub Secrets. The CI workflow materializes them at runtime and never commits them.

## Jobs Overview

- Lint • Test • Coverage: format, analyze, run tests, gate at 95%.
- Supabase Migrations (Dev → Prod): pushes migrations via Supabase CLI.
- Android Dev APK: debug build for flavor `dev` with dart-define JSON.
- Android Prod AAB: release build for flavor `prod`, uploads to Play (internal).
- iOS builds are manual via Xcode (no CI job).

## Secrets (names used in CI)

Supabase
- `SUPABASE_ACCESS_TOKEN` — Personal access token for Supabase CLI.
- `DEV_PROJECT_ID` — Dev project ref (e.g., abcdefg).
- `DEV_DB_PASSWORD` — Dev DB password (if required).
- `PROD_PROJECT_ID` — Prod project ref.
- `PROD_DB_PASSWORD` — Prod DB password (if required).

App defines (compiled into the app through `env/*.json`)
- `SUPABASE_URL` — Project URL.
- `SUPABASE_ANON_KEY` — Public anon key.
- `WEB_CLIENT_ID` — Optional Google OAuth web client ID.
- `IOS_CLIENT_ID` — Optional Google OAuth iOS client ID.
- Deep link host — temporarily hardcoded placeholders in CI (`dev.example.com` / `example.com`) until deep linking is finalized.

Android signing (dev)
- `DEBUG_KEY_ALIAS`
- `DEBUG_KEY_PASSWORD`
- `DEBUG_STORE_PASSWORD`
- `DEBUG_KEYSTORE_BASE64` — Base64 of `android/app/dev_keystore.jks`.

Android signing (prod)
- `PROD_KEY_ALIAS`
- `PROD_KEY_PASSWORD`
- `PROD_STORE_PASSWORD`
- `PROD_KEYSTORE_BASE64` — Base64 of `android/app/prod_keystore.jks`.

Google Play upload
- `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` — Base64 of the service account JSON for Play API.

iOS (optional for future codesign)
- `ASC_API_KEY_B64` — Base64 of `AuthKey_XXXXXX.p8`.
- `ASC_API_KEY_ID` — App Store Connect Key ID.
- `ASC_ISSUER_ID` — App Store Connect Issuer ID.

## Restoring in Workflow (examples)

Create dart-define file
```yaml
- name: Create env/dev.json
  run: |
    mkdir -p env
    cat > env/dev.json <<'JSON'
    {
      "ENV": "dev",
      "SUPABASE_URL": "${{ env.SUPABASE_URL }}",
      "SUPABASE_ANON_KEY": "${{ env.SUPABASE_ANON_KEY }}",
      "DEEPLINK_HOST": "${{ env.DEEPLINK_HOST }}"
    }
    JSON
```

Materialize keystores
```yaml
- name: Setup debug signing (dev)
  run: |
    mkdir -p android/app
    cat > android/app/key.properties <<EOF
    debugKeyAlias=${{ secrets.DEBUG_KEY_ALIAS }}
    debugKeyPassword=${{ secrets.DEBUG_KEY_PASSWORD }}
    debugStorePassword=${{ secrets.DEBUG_STORE_PASSWORD }}
    storeType=JKS
    EOF
    echo "${{ secrets.DEBUG_KEYSTORE_BASE64 }}" | base64 --decode > android/app/dev_keystore.jks
```

Supabase CLI
```yaml
- uses: supabase/setup-cli@v1
  with:
    version: latest
- run: supabase link --project-ref "$SUPABASE_PROJECT_ID"
- run: supabase db push
```

## Notes

- Never commit keystores, Play JSON, App Store keys, or service-role keys.
- Prefer Play App Signing for Android; the upload key lives only in CI and local machines.
- For dev runs, keep real values in `env/dev.json` (gitignored). In CI, synthesize JSON from secrets at runtime.