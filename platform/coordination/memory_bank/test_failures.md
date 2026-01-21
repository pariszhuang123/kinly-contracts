---
Domain: Coordination
Capability: Test Failures
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Test Failures Knowledge Base

How to use
- Add brief entries when a non-trivial failure is diagnosed and fixed.
- Structure: signature → root cause → fix → prevention.

Template
- Area: [Flutter Widget | BLoC | RLS | RPC | CI]
- Signature: [error/stack snippet]
- Root Cause: [concise]
- Fix: [change applied]
- Prevention: [linters/tests/checks]

Entries
- Area: RLS
  - Signature: Non-member allowed/denied mismatch on home access
  - Root Cause: Missing USING predicate for inactive homes
  - Fix: Add policy `USING (home_active AND is_member(auth.uid()))`
  - Prevention: Add RLS test case for inactive homes
