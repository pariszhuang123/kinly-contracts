---
Domain: Homes
Capability: Flatmate Fit Check API
Scope: backend
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v2.0
---

# Flatmate Fit Check API v2.0

Status: Proposed

Scope: Backend RPCs and public route contracts for authenticated owner
creation and management on web, public candidate submission by share
token, server-side usage gate, owner web dashboard, app bootstrap with
auto-home creation, and email notifications on candidate submissions.

Audience: Product, design, engineering, AI agents.

Depends on:
- Flatmate Fit Check v2 Product Contract
- Flatmate Fit Check API v1 (legacy)
- Homes v2
- Users v1

## 1. Purpose

Define the server-side contract for Flatmate Fit Check v2. This API must
support:
- authenticated owner creation and management on web
- anonymous candidate submission by share token
- server-side usage gate (3 free web runs, then app-required)
- owner web dashboard access
- app bootstrap with auto-home creation
- email notifications on candidate submissions

These APIs MUST remain briefing-oriented. They MUST NOT produce ranking,
sorting, or auto-rejection behavior.

Language change from v1: public vocabulary uses "run" instead of "draft".
If the DB retains `fit_check_drafts`, that is an implementation detail
and MUST NOT leak into v2 API response shapes.

## 2. Access Model

- **Authenticated owner create/update/read:**
  - `fit_check_create_run` — authenticated
  - `fit_check_update_run` — authenticated, owner of run
  - `fit_check_get_owner_dashboard` — authenticated
  - `fit_check_get_owner_review` — authenticated, owner of run
  - `fit_check_get_owner_briefing` — authenticated, owner of run
  - `fit_check_get_prefill_payload` — authenticated, owner of run
  - `fit_check_rotate_share_token` — authenticated, owner of run
  - `fit_check_revoke_share_token` — authenticated, owner of run
- **Public candidate read/write:**
  - `fit_check_get_public_by_token` — public (unchanged from v1)
  - `fit_check_submit_candidate_by_token` — public (unchanged from v1,
    but now triggers async email notification)
- **App bootstrap:**
  - `fit_check_app_bootstrap` — authenticated, checks if home exists,
    creates if not
- **No claim token RPCs** — claim tokens are v1-only and MUST NOT be
  used in v2 flows.

Access requirements:
- Public RPCs MUST NOT require authentication.
- Authenticated RPCs MUST require a valid session via `auth.uid()`.
- Owner read/write RPCs MUST assert that the caller owns the run.
- Direct client DML on fit-check tables MUST be denied; access is
  RPC-only.

## 3. Canonical Inputs

### 3.1–3.6 Shared with v1

The following input definitions are unchanged from v1 and are referenced
here by section number:

- §3.1 Locale — same as [v1 §3.1](./flatmate_fit_check_api_v1.md#31-locale)
- §3.2 Scenario payload (`answers`) — same as [v1 §3.2](./flatmate_fit_check_api_v1.md#32-scenario-payload-answers)
- §3.3 Candidate identity — same as [v1 §3.3](./flatmate_fit_check_api_v1.md#33-candidate-identity)
- §3.4 Candidate location — same as [v1 §3.4](./flatmate_fit_check_api_v1.md#34-candidate-location)
- §3.5 Watchout direction — same as [v1 §3.5](./flatmate_fit_check_api_v1.md#35-watchout-direction)
- §3.6 Anonymous session identity — same as [v1 §3.6](./flatmate_fit_check_api_v1.md#36-anonymous-session-identity)

### 3.7–3.8 Removed in v2

- §3.7 Draft session token — v1-only. Not used in v2.
- §3.8 Share token and claim token — `share_token` semantics are
  unchanged. `claim_token` is v1-only and removed in v2.

## 4. RPC Contracts

### 4.1 `fit_check_create_run(p_locale text, p_answers jsonb) -> jsonb`

Caller: authenticated.

Behavior:
- Creates a new fit check run bound to `auth.uid()`.
- Checks usage gate: if owner has ≥3 completed runs, returns
  `gate_status: "app_required"` instead of full results.
- Generates owner summary labels and share token.
- Saves to DB immediately (no anonymous draft).
- Returns gate status, run data, summary, and share info.

Response shape (ungated — run 1–3):

```json
{
  "ok": true,
  "run_id": "uuid",
  "gate_status": "web_allowed",
  "completed_run_count": 2,
  "requested_locale_base": "en",
  "resolved_locale_base": "en",
  "owner_answers": {
    "fit_cleanliness": 0,
    "fit_rhythm": 1,
    "fit_chores": 0,
    "fit_conflict": 0
  },
  "summary": {
    "labels": [
      "Cleans straight away",
      "Chill - TV or music",
      "Roster system",
      "Brings it up early"
    ]
  },
  "share": {
    "share_token": "text",
    "share_url": "text",
    "expires_at": "timestamptz"
  }
}
```

Response shape (gated — run 4+):

The gated response MUST still return the owner's own answers, summary,
and share link. The gate restricts access to candidate briefings, not
the owner's own data.

```json
{
  "ok": true,
  "run_id": "uuid",
  "gate_status": "app_required",
  "completed_run_count": 4,
  "requested_locale_base": "en",
  "resolved_locale_base": "en",
  "owner_answers": {
    "fit_cleanliness": 0,
    "fit_rhythm": 1,
    "fit_chores": 0,
    "fit_conflict": 0
  },
  "summary": {
    "labels": [
      "Cleans straight away",
      "Chill - TV or music",
      "Roster system",
      "Brings it up early"
    ]
  },
  "share": {
    "share_token": "text",
    "share_url": "text",
    "expires_at": "timestamptz"
  },
  "app_handoff": {
    "download_url": "text",
    "benefits": [
      "See all reports",
      "Manage your home",
      "Track applicants"
    ],
    "benefits_keys": [
      "fit_check.gate.benefit.reports",
      "fit_check.gate.benefit.manage_home",
      "fit_check.gate.benefit.track_applicants"
    ]
  }
}
```

### 4.2 `fit_check_update_run(p_run_id uuid, p_locale text, p_answers jsonb) -> jsonb`

Caller: authenticated owner of run.

Behavior:
- Updates answers on an existing run.
- Does not increment the usage counter.
- Re-generates owner summary labels from updated answers.
- MUST fail if the caller does not own the run.
- Existing `candidate_fit_briefings` remain frozen with their original
  `owner_answers_snapshot`. Editing the owner's answers does NOT
  regenerate or invalidate briefings already generated for prior
  submissions. New candidate submissions after the edit use the updated
  owner answers for briefing generation.

Response shape:

```json
{
  "ok": true,
  "run_id": "uuid",
  "requested_locale_base": "en",
  "resolved_locale_base": "en",
  "owner_answers": {
    "fit_cleanliness": 1,
    "fit_rhythm": 1,
    "fit_chores": 0,
    "fit_conflict": 2
  },
  "summary": {
    "labels": [
      "Cleans when it bothers me",
      "Chill - TV or music",
      "Roster system",
      "Let it go unless big"
    ]
  }
}
```

### 4.3 `fit_check_get_public_by_token(p_share_token text, p_locale text) -> jsonb`

Same as [v1 §4.2](./flatmate_fit_check_api_v1.md#42-fit_check_get_public_by_tokenp_share_token-text-p_locale-text---jsonb).
No changes.

### 4.4 `fit_check_submit_candidate_by_token(p_share_token text, p_locale text, p_display_name text, p_country_code text, p_city_name text, p_answers jsonb) -> jsonb`

Same as [v1 §4.3](./flatmate_fit_check_api_v1.md#43-fit_check_submit_candidate_by_tokenp_share_token-text-p_locale-text-p_display_name-text-p_country_code-text-p_city_name-text-p_answers-jsonb---jsonb)
with the following addition:
- On successful submission, triggers an async email notification to the
  run owner.
- Email delivery failure MUST NOT fail the candidate submission RPC.

### 4.5 `fit_check_get_owner_dashboard(p_locale text) -> jsonb`

Caller: authenticated.

Behavior:
- Returns all runs for the authenticated owner.
- Each run includes: `run_id`, `created_at`, `submission_count`,
  `gate_status`, and summary preview.
- Returns profile info for top-right display: `display_name`,
  `avatar_url`.
- `submission_count` MUST be returned for all runs including gated runs.
  This is intentional: it acts as a teaser showing the owner how many
  candidates have responded, motivating app download.
- Submission list within each run MUST NOT be ranked by fit score.

Response shape:

```json
{
  "ok": true,
  "requested_locale_base": "en",
  "resolved_locale_base": "en",
  "profile": {
    "display_name": "text",
    "avatar_url": "text|null"
  },
  "runs": [
    {
      "run_id": "uuid",
      "created_at": "timestamptz",
      "submission_count": 3,
      "gate_status": "web_allowed",
      "summary_preview": {
        "labels": [
          "Cleans straight away",
          "Chill - TV or music",
          "Roster system",
          "Brings it up early"
        ]
      }
    }
  ],
  "gate": {
    "completed_run_count": 2,
    "web_runs_remaining": 1
  }
}
```

### 4.6 `fit_check_get_owner_review(p_run_id uuid, p_locale text) -> jsonb`

Caller: authenticated owner of the run.

Behavior:
- Same as [v1 §4.6](./flatmate_fit_check_api_v1.md#46-fit_check_get_owner_reviewp_draft_id-uuid-p_locale-text---jsonb)
  with the following changes:
- Uses `run_id` instead of `draft_id`.
- No `home_id` in response (home attachment is a v1 concept for web).
- Gate behaviour: for gated runs (`gate_status: "app_required"`), the
  endpoint MUST still return the owner's summary, share info, and
  submission count. It MUST omit the `submissions` list detail and
  instead return `submissions_gated: true` with an `app_handoff` hint.
  This avoids blocking the owner from their own data while still
  restricting candidate-level detail to the app.

Response shape (ungated):

```json
{
  "ok": true,
  "run_id": "uuid",
  "gate_status": "web_allowed",
  "requested_locale_base": "en",
  "resolved_locale_base": "en",
  "owner_summary": {
    "labels": [
      "Cleans straight away",
      "Quiet early nights",
      "Roster system",
      "Brings it up early"
    ]
  },
  "share": {
    "share_token_status": "active",
    "share_url": null,
    "link_reveal_requires_rotation": true,
    "expires_at": "timestamptz",
    "submissions_remaining": 17
  },
  "submission_count": 3,
  "submissions": [
    {
      "submission_id": "uuid",
      "display_name": "Alex",
      "country_code": "NZ",
      "city_name": "Auckland",
      "review_label": "Alex · 2026-03-25 14:14",
      "submitted_at": "timestamptz",
      "preview": {
        "top_watchouts": [
          "fit_cleanliness",
          "fit_rhythm"
        ],
        "summary_label": "A few things to discuss"
      }
    }
  ]
}
```

Response shape (gated):

```json
{
  "ok": true,
  "run_id": "uuid",
  "gate_status": "app_required",
  "requested_locale_base": "en",
  "resolved_locale_base": "en",
  "owner_summary": {
    "labels": [
      "Cleans straight away",
      "Quiet early nights",
      "Roster system",
      "Brings it up early"
    ]
  },
  "share": {
    "share_token_status": "active",
    "share_url": null,
    "link_reveal_requires_rotation": true,
    "expires_at": "timestamptz",
    "submissions_remaining": 17
  },
  "submission_count": 3,
  "submissions_gated": true,
  "submissions": null,
  "app_handoff": {
    "download_url": "text",
    "message_key": "fit_check.gate.review_locked"
  }
}
```

### 4.7 `fit_check_get_owner_briefing(p_submission_id uuid, p_locale text) -> jsonb`

Same as [v1 §4.7](./flatmate_fit_check_api_v1.md#47-fit_check_get_owner_briefingp_submission_id-uuid-p_locale-text---jsonb).
No changes.

### 4.8 `fit_check_rotate_share_token(p_run_id uuid) -> jsonb`

Same as [v1 §4.8](./flatmate_fit_check_api_v1.md#48-fit_check_rotate_share_tokenp_draft_id-uuid---jsonb)
but uses `p_run_id` instead of `p_draft_id`.

Caller: authenticated owner of the run.

Response shape:

```json
{
  "ok": true,
  "run_id": "uuid",
  "share_token_status": "active",
  "share_url": "text",
  "expires_at": "timestamptz"
}
```

### 4.9 `fit_check_revoke_share_token(p_run_id uuid) -> jsonb`

Same as [v1 §4.9](./flatmate_fit_check_api_v1.md#49-fit_check_revoke_share_tokenp_draft_id-uuid---jsonb)
but uses `p_run_id` instead of `p_draft_id`.

Caller: authenticated owner of the run.

Response shape:

```json
{
  "ok": true,
  "run_id": "uuid",
  "share_token_status": "revoked"
}
```

### 4.10 `fit_check_discard_run(p_run_id uuid) -> jsonb`

Caller: authenticated owner of the run.

Behavior:
- Permanently deletes a run and all associated data (share tokens,
  submissions, briefings, notification records).
- MUST fail if the caller does not own the run.
- MUST only be allowed if the run has **zero** candidate submissions.
  Once a candidate has submitted, the run cannot be discarded (to
  prevent data loss for candidates who already participated).
- Decrements the owner's completed-run count by 1, freeing a gate slot.

Response shape:

```json
{
  "ok": true,
  "discarded_run_id": "uuid",
  "completed_run_count": 2
}
```

Error:
- `FIT_CHECK_DISCARD_HAS_SUBMISSIONS` — run has ≥1 candidate submission
  and cannot be discarded.

### 4.11 `fit_check_update_notification_preference(p_preference text) -> jsonb`

Caller: authenticated.

Behavior:
- Updates the owner's email notification preference.
- `p_preference` MUST be one of: `every_submission`, `daily_digest`,
  `muted`.
- Applies to all runs owned by this user.

Response shape:

```json
{
  "ok": true,
  "notification_preference": "daily_digest"
}
```

### 4.12 `fit_check_get_prefill_payload(p_run_id uuid) -> jsonb`

Same as [v1 §4.10](./flatmate_fit_check_api_v1.md#410-fit_check_get_prefill_payloadp_draft_id-uuid---jsonb)
but uses `p_run_id` instead of `p_draft_id`.

Caller: authenticated owner of the run.

Response shape:

```json
{
  "ok": true,
  "run_id": "uuid",
  "house_norms_prefill": {
    "norms_shared_spaces": "clear_now",
    "norms_rhythm_quiet": "variable",
    "norms_responsibility_flow": "clear_agreements",
    "norms_repair_style": "talk_soon"
  },
  "onboarding_seed": {
    "house_norms": {
      "initial_responses": {
        "norms_shared_spaces": 0,
        "norms_rhythm_quiet": 1,
        "norms_responsibility_flow": 0,
        "norms_repair_style": 0
      }
    },
    "preferences": {
      "initial_responses": {}
    }
  },
  "preference_flow_hints": {
    "supported": false,
    "answers": {}
  }
}
```

### 4.13 `fit_check_app_bootstrap(p_locale text, p_home_id uuid null) -> jsonb`

Caller: authenticated (in-app).

Precondition: the authenticated user MUST have at least one fit check
run. The app SHOULD check for existing runs before calling this endpoint
(e.g., via the dashboard RPC or a lightweight existence check).

Behavior:
- Checks if the authenticated user has any homes.
- **If no home exists**: creates one automatically.
  - Home name defaults to `"{display_name}'s Home"` (localised via
    template key `fit_check.bootstrap.default_home_name`)
  - The user is assigned `owner` role on the auto-created home
  - All fit check runs are attached to the new home
- **If exactly one home exists and `p_home_id` is null**: attaches all
  unattached fit check runs to that home.
- **If multiple homes exist**: `p_home_id` MUST be provided. If null,
  returns `FIT_CHECK_BOOTSTRAP_HOME_CHOICE_REQUIRED` with a list of
  the user's homes so the app can prompt for selection.
- Returns home state and list of fit check runs for app display.
- This is fit-check-funnel-specific orchestration, not a generic Homes
  API.
- Auto-home creation is idempotent; repeated calls MUST NOT create
  duplicate homes. If a home was already created by a previous bootstrap
  call, subsequent calls attach any new unattached runs to it.

Response shape (success):

```json
{
  "ok": true,
  "home_id": "uuid",
  "home_created": true,
  "owner_role": "owner",
  "attached_run_count": 3,
  "runs": [
    {
      "run_id": "uuid",
      "submission_count": 5,
      "summary_preview": {
        "labels": [
          "Cleans straight away",
          "Chill - TV or music",
          "Roster system",
          "Brings it up early"
        ]
      }
    }
  ]
}
```

Response shape (home choice required):

```json
{
  "ok": false,
  "code": "FIT_CHECK_BOOTSTRAP_HOME_CHOICE_REQUIRED",
  "homes": [
    { "home_id": "uuid", "home_name": "text" },
    { "home_id": "uuid", "home_name": "text" }
  ]
}
```

## 5. Storage and Security

Tables are the same as v1:
- `fit_check_drafts`
- `fit_check_share_tokens`
- `candidate_fit_submissions`
- `candidate_fit_briefings`

v2-specific changes:
- `fit_check_drafts.owner_user_id` is NOT NULL in v2 (always
  authenticated at creation time).
- `draft_session_token_hash` and `claim_token_hash` are v1-only columns.
  These columns remain in the schema as nullable for v1 row
  compatibility. v2 RPCs MUST NOT read or write these columns. Once all
  v1 drafts have expired, these columns MAY be dropped.
- `notification_preference` column on `user_profiles` or a
  fit-check-specific settings table. Values: `every_submission`
  (default), `daily_digest`, `muted`.
- New: email notification tracking via async queue. Email delivery is a
  side effect, not a table contract.

### Schema mapping note

The v2 API uses "run" in its public vocabulary. The underlying DB table
remains `fit_check_drafts`. The mapping is:

| API field | DB column |
|---|---|
| `run_id` | `fit_check_drafts.id` |
| `owner_user_id` | `fit_check_drafts.owner_user_id` |
| `home_id` | `fit_check_drafts.home_id` |

This is an API naming convention, not a schema migration. Engineers
MUST use `run_id` in all v2 API surfaces and `fit_check_drafts.id` in
SQL/backend code.

Security requirements:
- All owner-facing mutations are RPC-only.
- Direct client DML on fit-check tables MUST be denied.
- Authenticated RPCs run as `SECURITY DEFINER` and assert ownership via
  `auth.uid()`.
- Public RPCs return only candidate-safe projections.

## 6. Error Model

Private/public RPC errors follow `{ code, message, details }` envelope
conventions when throwing.

Required codes (inherited from v1):
- `UNAUTHORIZED`
- `FORBIDDEN_OWNER_ONLY`
- `FIT_CHECK_NOT_FOUND`
- `FIT_CHECK_INVALID_INPUTS`
- `FIT_CHECK_INVALID_LOCALE`
- `FIT_CHECK_INVALID_TOKEN`
- `FIT_CHECK_TOKEN_EXPIRED`
- `FIT_CHECK_TOKEN_REVOKED`
- `FIT_CHECK_TOKEN_SUBMISSION_LIMIT_REACHED`
- `FIT_CHECK_DUPLICATE_SUBMISSION`
- `FIT_CHECK_RATE_LIMITED`

New codes in v2:
- `FIT_CHECK_GATE_APP_REQUIRED` — owner has hit the 3-run web limit
- `FIT_CHECK_RUN_NOT_FOUND` — specified run does not exist or caller
  does not own it
- `FIT_CHECK_BOOTSTRAP_FAILED` — app bootstrap auto-home creation or
  attachment failed
- `FIT_CHECK_BOOTSTRAP_HOME_CHOICE_REQUIRED` — user has multiple homes
  and `p_home_id` was not provided; response includes home list
- `FIT_CHECK_BOOTSTRAP_NO_RUNS` — bootstrap called but user has no
  fit check runs

Removed codes (v1-only):
- `FIT_CHECK_INVALID_CLAIM_TOKEN`
- `FIT_CHECK_INVALID_OR_USED_CLAIM_TOKEN`
- `FIT_CHECK_INVALID_DRAFT_SESSION`
- `FIT_CHECK_HOME_ATTACHMENT_CONFLICT`

Public token read behavior:
- `fit_check_get_public_by_token` SHOULD prefer `available=false` for
  invalid/expired/revoked/unavailable token states.

Public submission behavior:
- `fit_check_submit_candidate_by_token` MAY throw structured errors for
  duplicate, limit, rate-limit, or invalid payload failures.
- Invalid country or city selections MUST fail with
  `FIT_CHECK_INVALID_INPUTS`.

## 7. Invariants

Inherited from v1:
- API outputs MUST NOT rank or sort candidates by fit.
- API outputs MUST NOT return a numeric fit score.
- Owner review is one submission at a time plus an unranked list view.
- Candidate responses remain anonymous apart from required
  `display_name`.
- Duplicate `display_name` values are allowed and MUST be disambiguated
  in owner review via `submission_id`, `submitted_at`, or a derived
  review label.
- Share-token rotation/revocation MUST NOT delete existing submissions or
  briefings.
- House Norms and preference downstream artifacts are prefill-only in
  this API; no canonical writes occur here.

New in v2:
- Usage gate is server-enforced; client MUST NOT skip the gate.
- App bootstrap auto-home creation is idempotent.
- Email delivery failure MUST NOT fail candidate submission.
- All runs are authenticated at creation; there is no anonymous draft
  state in v2.
- One owner MAY own multiple runs; each run is independent.

## 8. Contract Test Scenarios

- Authenticated owner creates run 1 and receives `gate_status:
  "web_allowed"`.
- Authenticated owner creates run 2 and receives `gate_status:
  "web_allowed"` with `completed_run_count: 2`.
- Authenticated owner creates run 3 and receives `gate_status:
  "web_allowed"` with `completed_run_count: 3`.
- Authenticated owner creates run 4 and receives `gate_status:
  "app_required"` with `completed_run_count: 4`.
- Gated response includes `owner_answers`, `summary`, `share`, and
  `app_handoff` with `download_url`, `benefits`, and `benefits_keys`.
- Owner updates run answers and receives updated summary without
  incrementing usage counter.
- Public token read returns candidate-safe scenario template keys only
  (unchanged from v1).
- Candidate submission returns confirmation payload (unchanged from v1).
- Candidate submission triggers async email notification to run owner.
- Email delivery failure does not fail candidate submission.
- Dashboard returns all runs with correct `gate_status` for each.
- Dashboard includes `profile` with `display_name` and `avatar_url`.
- Dashboard `gate` object shows correct `completed_run_count` and
  `web_runs_remaining`.
- Owner review for an ungated run returns submissions list with preview
  metadata.
- Owner review for a gated run returns `FIT_CHECK_GATE_APP_REQUIRED`
  error.
- Prior ungated runs remain accessible on web after gate is triggered on
  new runs.
- Owner briefing returns watchout keys using canonical
  `owner_higher|candidate_higher` directions (unchanged from v1).
- Share-token rotation creates a new active token without deleting prior
  submissions.
- Share-token revocation revokes without deleting submissions.
- Prefill payload returns House Norms mappings but performs no downstream
  writes.
- App bootstrap creates home when none exists, assigns owner role, and
  attaches all runs.
- App bootstrap attaches unattached runs to single existing home.
- App bootstrap with multiple homes and no `p_home_id` returns
  `FIT_CHECK_BOOTSTRAP_HOME_CHOICE_REQUIRED` with home list.
- App bootstrap with multiple homes and valid `p_home_id` attaches runs
  to the chosen home.
- App bootstrap with no fit check runs returns
  `FIT_CHECK_BOOTSTRAP_NO_RUNS`.
- App bootstrap is idempotent; repeated calls do not create duplicate
  homes.
- App bootstrap returns `home_created`, `owner_role`,
  `attached_run_count`, and run summaries.

## 9. References

- Flatmate Fit Check v2 Product Contract
- [Flatmate Fit Check API v1 (legacy)](./flatmate_fit_check_api_v1.md)
- [Homes v2](./homes_v2.md)
- [Users v1](../identity/users_v1.md)

```contracts-json
{
  "domain": "flatmate_fit_check_api",
  "version": "v2",
  "note": "API uses 'run' vocabulary; DB table is 'fit_check_drafts'. See §5 schema mapping note.",
  "entities": {
    "FitCheckRun": {
      "note": "DB table: fit_check_drafts",
      "id": "uuid (API: run_id)",
      "ownerUserId": "uuid (NOT NULL in v2)",
      "homeId": "uuid|null",
      "ownerAnswers": "jsonb",
      "requestedLocaleBase": "text",
      "createdAt": "timestamptz",
      "updatedAt": "timestamptz"
    },
    "FitCheckShareToken": {
      "id": "uuid",
      "runId": "uuid (DB: draft_id)",
      "tokenHash": "text",
      "status": "text",
      "expiresAt": "timestamptz",
      "revokedAt": "timestamptz|null"
    },
    "CandidateFitSubmission": {
      "id": "uuid",
      "runId": "uuid (DB: draft_id)",
      "displayName": "text",
      "countryCode": "text",
      "cityName": "text",
      "answers": "jsonb",
      "anonymousSessionHash": "text",
      "submittedAt": "timestamptz"
    },
    "CandidateFitBriefing": {
      "id": "uuid",
      "submissionId": "uuid",
      "runId": "uuid (DB: draft_id)",
      "ownerAnswersSnapshot": "jsonb",
      "briefingPayload": "jsonb",
      "generatedAt": "timestamptz"
    }
  },
  "functions": {
    "fitCheck.createRun": {
      "type": "rpc",
      "caller": "authenticated",
      "impl": "public.fit_check_create_run",
      "args": {
        "p_locale": "text",
        "p_answers": "jsonb"
      },
      "returns": "jsonb"
    },
    "fitCheck.updateRun": {
      "type": "rpc",
      "caller": "authenticated",
      "impl": "public.fit_check_update_run",
      "args": {
        "p_run_id": "uuid",
        "p_locale": "text",
        "p_answers": "jsonb"
      },
      "returns": "jsonb"
    },
    "fitCheck.getPublicByToken": {
      "type": "rpc",
      "caller": "public",
      "impl": "public.fit_check_get_public_by_token",
      "args": {
        "p_share_token": "text",
        "p_locale": "text"
      },
      "returns": "jsonb"
    },
    "fitCheck.submitCandidateByToken": {
      "type": "rpc",
      "caller": "public",
      "impl": "public.fit_check_submit_candidate_by_token",
      "args": {
        "p_share_token": "text",
        "p_locale": "text",
        "p_display_name": "text",
        "p_country_code": "text",
        "p_city_name": "text",
        "p_answers": "jsonb"
      },
      "returns": "jsonb"
    },
    "fitCheck.getOwnerDashboard": {
      "type": "rpc",
      "caller": "authenticated",
      "impl": "public.fit_check_get_owner_dashboard",
      "args": {
        "p_locale": "text"
      },
      "returns": "jsonb"
    },
    "fitCheck.getOwnerReview": {
      "type": "rpc",
      "caller": "owner-only",
      "impl": "public.fit_check_get_owner_review",
      "args": {
        "p_run_id": "uuid",
        "p_locale": "text"
      },
      "returns": "jsonb"
    },
    "fitCheck.getOwnerBriefing": {
      "type": "rpc",
      "caller": "owner-only",
      "impl": "public.fit_check_get_owner_briefing",
      "args": {
        "p_submission_id": "uuid",
        "p_locale": "text"
      },
      "returns": "jsonb"
    },
    "fitCheck.rotateShareToken": {
      "type": "rpc",
      "caller": "owner-only",
      "impl": "public.fit_check_rotate_share_token",
      "args": {
        "p_run_id": "uuid"
      },
      "returns": "jsonb"
    },
    "fitCheck.revokeShareToken": {
      "type": "rpc",
      "caller": "owner-only",
      "impl": "public.fit_check_revoke_share_token",
      "args": {
        "p_run_id": "uuid"
      },
      "returns": "jsonb"
    },
    "fitCheck.getPrefillPayload": {
      "type": "rpc",
      "caller": "owner-only",
      "impl": "public.fit_check_get_prefill_payload",
      "args": {
        "p_run_id": "uuid"
      },
      "returns": "jsonb"
    },
    "fitCheck.appBootstrap": {
      "type": "rpc",
      "caller": "authenticated",
      "impl": "public.fit_check_app_bootstrap",
      "args": {
        "p_locale": "text",
        "p_home_id": "uuid|null"
      },
      "returns": "jsonb"
    }
  },
  "rls": []
}
```
