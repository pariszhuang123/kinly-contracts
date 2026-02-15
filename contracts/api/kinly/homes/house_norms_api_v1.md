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
- Server normalizes locale to lowercase base locale (`locale_base`) and falls
  back to `en`.

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
- Unknown keys MUST fail to avoid semantic drift.
- Payload size above guardrails (2KB) MUST fail.

4. RPC Contracts

4.1 `house_norms_get_for_home(p_home_id uuid, p_locale text) -> jsonb`

Caller: current member.

Behavior:
- Returns draft + published House Norms metadata when present.
- Returns null payload when no document exists yet.
- Returns both requested locale base and stored document locale base.

Response shape:

```json
{
  "ok": true,
  "home_id": "uuid",
  "requested_locale_base": "en",
  "doc_locale_base": "en",
  "house_norms": {
    "template_key": "house_norms_v1",
    "status": "published|out_of_date",
    "inputs": {},
    "draft_content": {},
    "draft_updated_at": "timestamptz",
    "published_content": {},
    "published_at": "timestamptz|null",
    "is_published": true,
    "has_unpublished_changes": false,
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
  "requested_locale_base": "en",
  "house_norms": null
}
```

4.2 `house_norms_generate_for_home(p_home_id uuid, p_template_key text, p_locale text, p_inputs jsonb, p_force boolean) -> jsonb`

Caller: current owner.

Behavior:
- Validates owner role, template, locale, and `p_inputs`.
- Generates draft content (`generated_content`) from template + taxonomy-backed
  inputs.
- Does not update `published_content`.
- When `p_force = false`, implementation MAY short-circuit if equivalent inputs
  are already in the existing document.
- When `p_force = true`, implementation overwrites draft state.

Response shape:

```json
{
  "ok": true,
  "home_id": "uuid",
  "template_key": "house_norms_v1",
  "locale_base": "en",
  "status": "published|out_of_date",
  "draft_content": {},
  "draft_updated_at": "timestamptz",
  "published_content": {},
  "published_at": "timestamptz|null",
  "short_circuited": false
}
```

4.3 `house_norms_publish_for_home(p_home_id uuid, p_locale text) -> jsonb`

Caller: current owner.

Behavior:
- Explicit publish RPC for web/share snapshot updates.
- Copies `generated_content` to `published_content`.
- Marks status as `published`.

Response shape:

```json
{
  "ok": true,
  "home_id": "uuid",
  "requested_locale_base": "en",
  "doc_locale_base": "en",
  "status": "published",
  "published_content": {},
  "published_at": "timestamptz",
  "has_unpublished_changes": false
}
```

4.4 `house_norms_edit_section_text(p_home_id uuid, p_locale text, p_section_key text, p_new_text text, p_change_summary text default null) -> jsonb`

Caller: current owner.

Behavior:
- Edits only the target editable field in `generated_content` (draft).
- Creates a revision row in `house_norms_revisions`.
- Must reject unsafe language (enforcement, punishment, threat framing).
- Must reject unknown `p_section_key`.

Allowed `p_section_key` values:
- `summary_framing`
- `norms_rhythm_quiet`
- `norms_shared_spaces`
- `norms_guests_social`
- `norms_responsibility_flow`
- `norms_repair_style`
- `norms_home_identity`

Field mapping:
- `summary_framing` maps to `generated_content.summary.framing`.
- Norms section keys map to `generated_content.sections.<section_key>.text`.

Validation requirements:
- `p_section_key` outside allowlist MUST fail with `HOUSE_NORMS_INVALID_SECTION`.
- Empty edited text MUST fail with `HOUSE_NORMS_INVALID_INPUTS`.
- Edited text > 2000 chars MUST fail with `HOUSE_NORMS_INVALID_INPUTS`.
- `summary_framing` text > 500 chars MUST fail with
  `HOUSE_NORMS_INVALID_INPUTS`.
- `p_change_summary` > 280 chars MUST fail with `HOUSE_NORMS_INVALID_INPUTS`.
- Unsafe text MUST fail with `HOUSE_NORMS_UNSAFE_TEXT` for English
  (`locale_base='en'`).

Response shape:

```json
{
  "ok": true,
  "home_id": "uuid",
  "requested_locale_base": "en",
  "doc_locale_base": "en",
  "section_key": "norms_shared_spaces",
  "draft_content": {},
  "draft_updated_at": "timestamptz",
  "published_at": "timestamptz|null",
  "status": "published|out_of_date",
  "has_unpublished_changes": true,
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
- `NOT_HOME_MEMBER`
- `INVALID_LOCALE`
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

8. Contract Test Scenarios

- Owner edits `summary_framing` successfully.
- Non-owner edit attempt fails with owner-only authorization error.
- `summary.title` and `summary.subtitle` cannot be edited through
  `house_norms_edit_section_text`.
- Unknown `p_section_key` fails with `HOUSE_NORMS_INVALID_SECTION`.
- Unsafe text fails with `HOUSE_NORMS_UNSAFE_TEXT` for English locale.
- Text > 2000 and summary framing > 500 fail with `HOUSE_NORMS_INVALID_INPUTS`.
- Successful edit creates a row in `house_norms_revisions`.
- Publish copies draft to published and clears unpublished-change flag.

9. References

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
      "localeBase": "text",
      "status": "text",
      "inputs": "jsonb",
      "generatedContent": "jsonb",
      "publishedContent": "jsonb|null",
      "generatedAt": "timestamptz",
      "publishedAt": "timestamptz|null",
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
