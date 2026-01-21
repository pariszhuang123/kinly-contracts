---
Domain: Engineering
Capability: Sentry Android Native Symbols
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Contract: Upload Android native debug symbols to Sentry (Flutter) v1

## Goal
When CI builds an Android release (AAB), CI uploads native debug symbols so SIGABRT/native crashes are symbolicated in Sentry.

## Approach
- Use `sentry_dart_plugin` after the Android release build (symbols exist only after the build).
- Generate full native debug symbols via Gradle (`ndk.debugSymbolLevel = "FULL"`).

## Repo changes
1) `pubspec.yaml`
   - Add dev dependency: `sentry_dart_plugin: ^3.0.0`
   - Add `sentry:` config:
     ```yaml
     sentry:
       upload_debug_symbols: true
       upload_source_maps: false
       upload_sources: false
       ignore_missing: true
       log_level: error
     ```
   - Notes: the plugin reads config from `pubspec.yaml`, env vars, or `sentry.properties`.

2) Android Gradle (Kotlin DSL)
   - In `android/app/build.gradle.kts`, ensure release build type emits full symbols:
     ```kotlin
     buildTypes {
       release {
         ndk { debugSymbolLevel = "FULL" }
       }
     }
     ```
   - This creates `build/app/outputs/native-debug-symbols/<flavor>Release/out.zip` that the plugin uploads.

3) GitHub Actions secrets
   - Required: `SENTRY_AUTH_TOKEN` (scope: project:releases or project:write), `SENTRY_ORG`, `SENTRY_PROJECT`
   - Optional: `SENTRY_URL` (self-hosted only)

4) CI workflow (`.github/workflows/ci.yml`)
   - After building the prod AAB, run the plugin:
     ```yaml
     - name: Upload Sentry Android native symbols (prod)
       env:
         SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
         SENTRY_ORG: ${{ secrets.SENTRY_ORG }}
         SENTRY_PROJECT: ${{ secrets.SENTRY_PROJECT }}
         SENTRY_URL: ${{ secrets.SENTRY_URL }}
       run: dart run sentry_dart_plugin
     ```
   - Ordering: must run **after** `flutter build appbundle --release --flavor prod ...` and **before** build outputs are cleaned.

## Acceptance criteria
- CI logs show `dart run sentry_dart_plugin` succeeded (no auth/org/project errors).
- In Sentry → Releases, the built release contains uploaded native debug files.
- A native crash that previously showed only `abort()` frames now resolves to library and function names.

## Notes and future options
- If Dart obfuscation is later enabled, pass `--obfuscate --split-debug-info` during build and set `dart_symbol_map_path` for the plugin.
- Release association: the plugin uses build outputs to derive the correct release; no manual `SENTRY_RELEASE` is needed unless customized.