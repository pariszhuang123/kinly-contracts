---
Domain: Homes
Capability: House Norms API
Scope: backend
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
---

# House Norms API v1

Status: Proposed (Create Home MVP)

Scope: Member read and owner write RPCs for House Norms generation, publishing,
and edits at home scope.

Audience: Product, design, engineering, AI agents.

Depends on:
- Homes v2 (memberships + roles)
- House Norms v1
- House Norms Scenarios v1
- House Norms Taxonomy v1

1. Purpose

Define server-side contracts for reading and mutating House Norms. House Norms
are descriptive and non-enforceable. APIs in this contract must not create
permissions, automation, or compliance behavior.

2. Access Model

- Read (`house_norms_get_for_home`) is member-only.
- Write (`house_norms_generate_for_home`, `house_norms_publish_for_home`,
  `house_norms_edit_section_text`) is owner-only.
- All RPC callers MUST be authenticated.
- Caller membership MUST be current for `p_home_id`.
- Home MUST be active.

3. Canonical Inputs

3.1 Template and locale
- `p_template_key` identifies the generation template (for example
  `house_norms_v1`).
- `p_locale` accepts base or region forms (for example `en`, `en-NZ`).
- Server SHOULD normalize locale to a base locale and fallback to `en`.

3.2 Scenario input payload (`p_inputs`)
`p_inputs` is a JSON object with required keys and integer values `0..2`.

Required keys:
- `norms_property_context`
- `norms_relationship_model`
- `norms_rhythm_quiet`
- `norms_shared_spaces`
- `norms_guests_social`
- `norms_responsibility_flow`
- `norms_repair_style`
- `norms_home_identity`

Validation:
- Missing keys MUST fail.
- Values outside `0..2` MUST fail.
- Unknown keys SHOULD fail to avoid semantic drift.

4. RPC Contracts

4.1 `house_norms_get_for_home(p_home_id uuid, p_locale text) -> jsonb`

Caller: current member.

Behavior:
- Returns published House Norms for the home when present.
- Returns null payload when no document exists yet.
- If internal status is `out_of_date`, still return latest published content.

Response shape:

```json
{
  "ok": true,
  "home_id": "uuid",
  "locale": "en",
  "house_norms": {
    "template_key": "house_norms_v1",
    "status": "published|out_of_date",
    "published_content": {},
    "published_at": "timestamptz",
    "last_edited_at": "timestamptz|null",
    "last_edited_by": "uuid|null"
  }
}
```

When absent:

```json
{
  "ok": true,
  "home_id": "uuid",
  "locale": "en",
  "house_norms": null
}
```

4.2 `house_norms_generate_for_home(p_home_id uuid, p_template_key text, p_locale text, p_inputs jsonb, p_force boolean) -> jsonb`

Caller: current owner.

Behavior:
- Validates owner role, template, locale, and `p_inputs`.
- Generates `generated_content` from template + taxonomy-backed inputs.
- MVP profile is single-step: generation publishes immediately.
- When `p_force = false`, implementation MAY short-circuit if equivalent inputs
  are already published.
- When `p_force = true`, implementation MAY overwrite prior generated draft
  state before publish.

Response shape:

```json
{
  "ok": true,
  "home_id": "uuid",
  "template_key": "house_norms_v1",
  "locale": "en",
  "status": "published",
  "generated_content": {},
  "published_content": {},
  "generated_at": "timestamptz",
  "published_at": "timestamptz"
}
```

4.3 `house_norms_publish_for_home(p_home_id uuid, p_locale text) -> jsonb` (optional split mode)

Caller: current owner.

Behavior:
- Optional RPC for flows that separate generate from publish.
- Copies `generated_content` to `published_content`.
- Idempotent when no unpublished generated draft exists.

Response shape:

```json
{
  "ok": true,
  "home_id": "uuid",
  "status": "published",
  "published_content": {},
  "published_at": "timestamptz"
}
```

4.4 `house_norms_edit_section_text(p_home_id uuid, p_locale text, p_section_key text, p_new_text text, p_change_summary text default null) -> jsonb`

Caller: current owner.

Behavior:
- Edits only the target section in `published_content`.
- Creates a revision row in `house_norms_revisions`.
- Must reject unsafe language (enforcement, punishment, threat framing).
- Must reject unknown `p_section_key`.

Response shape:

```json
{
  "ok": true,
  "home_id": "uuid",
  "section_key": "norms_shared_spaces",
  "published_content": {},
  "last_edited_at": "timestamptz",
  "last_edited_by": "uuid"
}
```

5. Storage and Security (Proposed)

Tables:
- `house_norms`
- `house_norms_revisions`

Constraints:
- One active House Norms record per `home_id`.
- `status` in `published|out_of_date`.
- Revision rows append-only.

RLS/privileges:
- RPC-only write model.
- Direct client DML on norms tables denied.
- Write RPCs run as `SECURITY DEFINER` and assert membership/owner role.

6. Error Model

Errors follow `{ code, message, details }` envelope semantics used in Homes APIs.

Proposed codes:
- `UNAUTHORIZED`
- `HOMES_NOT_MEMBER`
- `FORBIDDEN_OWNER_ONLY`
- `HOME_INACTIVE`
- `HOUSE_NORMS_NOT_FOUND`
- `HOUSE_NORMS_INVALID_INPUTS`
- `HOUSE_NORMS_INVALID_TEMPLATE`
- `HOUSE_NORMS_INVALID_SECTION`
- `HOUSE_NORMS_UNSAFE_TEXT`

7. Invariants

- House Norms APIs MUST NOT gate unrelated features.
- House Norms text remains descriptive, not enforceable.
- Non-owners can read but cannot mutate.
- Template updates MUST NOT silently overwrite published content.

8. References

- [House Norms v1](../../../product/kinly/shared/house_norms_v1.md)
- [House Norms Scenarios v1](../../../product/kinly/shared/house_norms_scenarios_v1.md)
- [House Norms Taxonomy v1](../../../product/kinly/shared/house_norms_taxonomy_v1.md)
- [Homes v2](./homes_v2.md)

```contracts-json
{
  "domain": "house_norms_api",
  "version": "v1",
  "entities": {
    "HouseNorms": {
      "homeId": "uuid",
      "templateKey": "text",
      "locale": "text",
      "status": "text",
      "inputs": "jsonb",
      "generatedContent": "jsonb",
      "publishedContent": "jsonb",
      "generatedAt": "timestamptz",
      "publishedAt": "timestamptz",
      "lastEditedAt": "timestamptz|null",
      "lastEditedBy": "uuid|null"
    },
    "HouseNormsRevision": {
      "id": "uuid",
      "homeId": "uuid",
      "editorUserId": "uuid",
      "editedAt": "timestamptz",
      "content": "jsonb",
      "changeSummary": "text|null"
    }
  },
  "functions": {
    "houseNorms.getForHome": {
      "type": "rpc",
      "caller": "member",
      "impl": "public.house_norms_get_for_home",
      "args": {
        "p_home_id": "uuid",
        "p_locale": "text"
      },
      "returns": "jsonb"
    },
    "houseNorms.generateForHome": {
      "type": "rpc",
      "caller": "owner-only",
      "impl": "public.house_norms_generate_for_home",
      "args": {
        "p_home_id": "uuid",
        "p_template_key": "text",
        "p_locale": "text",
        "p_inputs": "jsonb",
        "p_force": "boolean"
      },
      "returns": "jsonb"
    },
    "houseNorms.publishForHome": {
      "type": "rpc",
      "caller": "owner-only",
      "status": "optional",
      "impl": "public.house_norms_publish_for_home",
      "args": {
        "p_home_id": "uuid",
        "p_locale": "text"
      },
      "returns": "jsonb"
    },
    "houseNorms.editSectionText": {
      "type": "rpc",
      "caller": "owner-only",
      "impl": "public.house_norms_edit_section_text",
      "args": {
        "p_home_id": "uuid",
        "p_locale": "text",
        "p_section_key": "text",
        "p_new_text": "text",
        "p_change_summary": "text|null"
      },
      "returns": "jsonb"
    }
  },
  "rls": []
}
```
