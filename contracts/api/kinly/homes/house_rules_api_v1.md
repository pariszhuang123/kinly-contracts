---
Domain: Homes
Capability: House Rules API
Scope: backend
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
---

# House Rules API v1

Status: Proposed (Phase 2 optional)

Scope: Member read and owner write RPCs for concise, owner-authoritative House
Rules at home scope.

Audience: Product, design, engineering, AI agents.

Depends on:
- Homes v2 (memberships + roles)
- House Rules v1

1. Purpose

Define backend contract for reading and publishing House Rules. In v1, rules are
authoritative text and MUST NOT gate unrelated app actions.

2. Access Model

- Read is member-only.
- Write is owner-only.
- Callers MUST be authenticated.
- Caller membership MUST be current for `p_home_id`.
- Home MUST be active.

3. RPCs

3.1 Read (member)
- `house_rules_get_for_home(p_home_id uuid, p_locale text) -> jsonb`
- Returns active rules version or null when absent.

Example response:

```json
{
  "ok": true,
  "home_id": "uuid",
  "locale": "en",
  "house_rules": {
    "version_id": "uuid",
    "version_number": 3,
    "status": "active",
    "rules": [
      "No smoking inside shared indoor areas.",
      "Guests require a same-day heads-up in chat."
    ],
    "published_at": "timestamptz",
    "published_by": "uuid"
  }
}
```

3.2 Upsert draft (owner-only)
- `house_rules_upsert_draft(p_home_id uuid, p_locale text, p_rules text[]) -> jsonb`
- Creates or updates owner draft for current home and locale.

3.3 Publish (owner-only)
- `house_rules_publish_for_home(p_home_id uuid, p_locale text) -> jsonb`
- Activates current draft immediately.
- Supersedes prior active version atomically.

4. Validation Rules

Input `p_rules` MUST satisfy:
- Rule count is 1..7.
- Each rule is <= 140 chars after trim.
- Each rule is single-line (no newline characters).
- Empty/whitespace-only entries are invalid.
- Unsafe/discriminatory content is rejected.

5. Error Envelope

Errors follow `{ code, message, details }` conventions.

Required codes:
- `UNAUTHORIZED`
- `HOMES_NOT_MEMBER`
- `FORBIDDEN_OWNER_ONLY`
- `HOME_INACTIVE`
- `HOUSE_RULES_NOT_FOUND`
- `HOUSE_RULES_INVALID_PAYLOAD`
- `HOUSE_RULES_TOO_MANY_RULES`
- `HOUSE_RULES_RULE_TOO_LONG`
- `HOUSE_RULES_RULE_MULTILINE`
- `HOUSE_RULES_UNSAFE_TEXT`

6. Invariants

- Non-owners cannot mutate House Rules.
- Member read works for active home membership.
- House Rules APIs MUST NOT auto-block unrelated features in v1.
- History of prior published versions MUST remain available for audit.

7. Test Scenarios (Contract Reference)

- Draft with 8 entries -> `HOUSE_RULES_TOO_MANY_RULES`.
- Rule > 140 chars -> `HOUSE_RULES_RULE_TOO_LONG`.
- Rule containing newline -> `HOUSE_RULES_RULE_MULTILINE`.
- Non-owner write call -> `FORBIDDEN_OWNER_ONLY`.
- Member read on active home -> success.
- Unsafe text payload -> `HOUSE_RULES_UNSAFE_TEXT`.

8. References

- [House Rules v1](../../../product/kinly/shared/house_rules_v1.md)
- [House Norms v1](../../../product/kinly/shared/house_norms_v1.md)
- [Homes v2](./homes_v2.md)

```contracts-json
{
  "domain": "house_rules_api",
  "version": "v1",
  "entities": {
    "HouseRulesVersion": {
      "id": "uuid",
      "homeId": "uuid",
      "versionNumber": "int4",
      "locale": "text",
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
      "args": {
        "p_home_id": "uuid",
        "p_locale": "text"
      },
      "returns": "jsonb"
    },
    "houseRules.upsertDraft": {
      "type": "rpc",
      "caller": "owner-only",
      "impl": "public.house_rules_upsert_draft",
      "args": {
        "p_home_id": "uuid",
        "p_locale": "text",
        "p_rules": "text[]"
      },
      "returns": "jsonb"
    },
    "houseRules.publishForHome": {
      "type": "rpc",
      "caller": "owner-only",
      "impl": "public.house_rules_publish_for_home",
      "args": {
        "p_home_id": "uuid",
        "p_locale": "text"
      },
      "returns": "jsonb"
    }
  },
  "rls": []
}
```
