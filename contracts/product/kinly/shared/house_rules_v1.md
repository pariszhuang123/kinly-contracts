---
Domain: Shared
Capability: House Rules
Scope: shared
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
---

# Kinly House Rules Contract v1

Status: Proposed (Phase 2 optional)

Scope: Owner-authored, concise home policy statements that are read-only for
members and do not gate app actions in v1.

Audience: Product, design, engineering, AI agents.

Depends on:
- Homes v2 (memberships + roles)
- Home Dynamics Contract v1
- Kinly product philosophy (care, not control)

1. Purpose

House Rules capture explicit, high-importance home policies in a short,
discoverable format.

House Rules are:
- Owner-authored.
- Non-negotiable in v1 policy terms.
- Versioned.
- Read-only for members.

House Rules are not:
- A discussion thread.
- A voting flow.
- An app gating system in v1.

2. Rollout Guardrail

- House Rules are optional and MUST NOT be required for onboarding.
- The app MUST NOT block core usage when no rules exist.
- UX MUST avoid setup-pressure language for House Rules in v1.

3. Ownership and Permissions

3.1 Owner authority
- Only the current home owner MAY create, edit, and publish House Rules.
- Owner publish activates a new rules version immediately.

3.2 Member permissions
- All current home members MAY view active House Rules.
- Members MUST NOT accept, reject, vote, comment, or dispute rules in-product
  in v1.

4. Rule Format and Brevity Limits

- Each published rules version MUST contain 1..7 rules.
- Each rule MUST be a single line (no newlines).
- Each rule MUST be <= 140 characters after trim.
- Long rationale text MUST NOT be embedded in rule lines.

5. Lifecycle and Versioning

States:
- `draft`
- `active`
- `superseded`

Rules lifecycle:
- Owner edits a draft.
- Owner publish creates an active version immediately.
- Prior active version becomes superseded.

Versioning requirements:
- Latest active version is canonical.
- Prior versions MUST remain stored for audit/history.
- Version upgrades are additive/clarifying unless explicitly marked breaking.

6. Safety Guardrails

Rule content MUST NOT:
- Include discriminatory or protected-class exclusion language.
- Name or target specific individuals.
- Contain threats, punishments, or coercive framing.
- Introduce illegal instructions.

7. Enforcement Model (v1)

- House Rules are authoritative text, not app-enforced controls.
- No Kinly feature may be auto-blocked based on House Rules in v1.
- No reminders, penalties, or automation triggers are derived from rules in v1.

8. Examples and Routing

Common rule topics:
- Smoking policy
- Pets policy
- Severe allergen policy
- Property care boundaries

Topic routing:
- Soft relational defaults -> House Norms.
- Explicit policy constraints -> House Rules.

9. Non-Goals (v1)

- Member approvals or denials
- Majority voting
- Comment threads
- Automated gating or compliance scoring

10. Invariants

- Owner has final authority over House Rules in v1.
- Members have read-only visibility.
- Rules remain concise by hard limits.
- House Rules and House Norms remain separate canonical tracks.

```contracts-json
{
  "domain": "house_rules",
  "version": "v1",
  "entities": {
    "HouseRulesVersion": {
      "id": "uuid",
      "homeId": "uuid",
      "version": "int4",
      "status": "text",
      "rules": "text[]",
      "publishedAt": "timestamptz",
      "publishedBy": "uuid"
    }
  },
  "functions": {
    "houseRules.getForHome": {
      "type": "rpc",
      "caller": "member",
      "impl": "public.house_rules_get_for_home",
      "returns": "jsonb"
    },
    "houseRules.upsertDraft": {
      "type": "rpc",
      "caller": "owner-only",
      "impl": "public.house_rules_upsert_draft",
      "returns": "jsonb"
    },
    "houseRules.publishForHome": {
      "type": "rpc",
      "caller": "owner-only",
      "impl": "public.house_rules_publish_for_home",
      "returns": "jsonb"
    }
  },
  "rls": []
}
```
