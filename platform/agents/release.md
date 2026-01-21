---
Domain: Agents
Capability: Release
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Release Agent

Template: Context → Objectives → Constraints → Contracts → DoD → Risks → Outputs

Responsibilities
- CI/CD workflows, artifact publishing, signing, and environment configs.
- Ensure builds: `flutter build apk/ipa` (Gradle/Xcode under the hood).

Constraints
- Secrets via GitHub OIDC → Supabase; no long‑lived keys.
- Size budget: warn if APK grows >5% vs main.

Outputs
- CI workflows, release notes, and store/upload automation (Fastlane optional later).
