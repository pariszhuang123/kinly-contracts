---
Domain: Product
Capability: complaint_rewrite
Scope: backend
Artifact-Type: contract
Stability: stable
Status: active
Version: v1.0
Audience: internal
Last updated: 2026-02-01
---

# Complaint Rewrite Storage Schema (complaint_rewrite_storage_schema_v1)

Purpose: define canonical tables, keys, and constraints for storing complaint rewrite data. Aligns with:
- Edge orchestrator (`complaint_rewrite_edge_orchestrator_v1`)
- Queue processing/backpressure (`complaint_rewrite_queue_processing_v1`)
- Async execution (`complaint_rewrite_async_jobs_v1`, `complaint_rewrite_two_lanes_async_v1`)
- Routing (`complaint_rewrite_ai_routing_providers_v1`)

This schema is authoritative; app services and analytics should consume, not redefine.

## Tables (minimum)

### 1. rewrite_requests
Stores one incoming request (one sender, one mentioned recipient).
- `rewrite_request_id` UUID PK
- `home_id` UUID NOT NULL
- `sender_user_id` UUID NOT NULL
- `recipient_user_id` UUID NOT NULL
- `recipient_snapshot_id` UUID NOT NULL
- `recipient_preference_snapshot_id` UUID NOT NULL
- `surface` TEXT CHECK in ('weekly_harmony','direct_message','other')
- `original_text` TEXT NOT NULL  -- write-once, never updated
- `source_locale` TEXT NOT NULL  -- normalized, never unknown
- `target_locale` TEXT NOT NULL  -- normalized, never unknown
- `lane` TEXT CHECK in ('same_language','cross_language') NOT NULL
- `topics` JSONB NOT NULL        -- from classifier (may be ["other"])
- `intent` TEXT NOT NULL
- `rewrite_strength` TEXT CHECK in ('light_touch','full_reframe') NOT NULL
- `classifier_version` TEXT NOT NULL
- `context_pack_version` TEXT NOT NULL
- `policy_version` TEXT NOT NULL
- `routing_decision_version` TEXT NOT NULL
- `status` TEXT CHECK in ('queued','processing','completed','failed','canceled') NOT NULL DEFAULT 'queued'
- `rewrite_completed_at` TIMESTAMPTZ NULL
- `sender_reveal_at` TIMESTAMPTZ NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()
Indexes:
- PK on `rewrite_request_id`
- Unique on (`rewrite_request_id`,`recipient_user_id`) to align with per-recipient execution unit
- Index on (`home_id`,`status`)
Notes: original_text updates are forbidden; enforce via trigger or application guard.

### 2. rewrite_outputs
Stores finalized rewritten messages (one row per execution unit).
- `rewrite_request_id` UUID NOT NULL REFERENCES rewrite_requests ON DELETE CASCADE
- `recipient_user_id` UUID NOT NULL
- `rewritten_text` TEXT NOT NULL
- `output_language` TEXT NOT NULL  -- must equal target_locale
- `model` TEXT NOT NULL
- `provider` TEXT NOT NULL
- `prompt_version` TEXT NOT NULL
- `policy_version` TEXT NOT NULL
- `lexicon_version` TEXT NOT NULL
- `eval_result` JSONB NOT NULL     -- structured pass/fail + scores
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
Constraints:
- PK on (`rewrite_request_id`,`recipient_user_id`)
- CHECK `output_language = (SELECT target_locale FROM rewrite_requests WHERE rewrite_request_id = rewrite_outputs.rewrite_request_id)`
- No updates after insert (enforce via trigger or app policy).

### 3. rewrite_jobs
Implements queue/backpressure contract.
- `job_id` UUID PK
- `rewrite_request_id` UUID NOT NULL REFERENCES rewrite_requests ON DELETE CASCADE
- `recipient_user_id` UUID NOT NULL
- `recipient_snapshot_id` UUID NOT NULL
- `recipient_preference_snapshot_id` UUID NOT NULL
- `task` TEXT CHECK = 'complaint_rewrite' NOT NULL
- `surface` TEXT NOT NULL
- `rewrite_strength` TEXT NOT NULL
- `language_pair` JSONB NOT NULL   -- {from,to}
- `lane` TEXT NOT NULL
- `routing_decision` JSONB NOT NULL -- RoutingDecisionV1
- `status` TEXT CHECK in ('queued','processing','completed','failed','canceled') NOT NULL DEFAULT 'queued'
- `not_before_at` TIMESTAMPTZ NULL
- `claimed_at` TIMESTAMPTZ NULL
- `claimed_by` TEXT NULL
- `attempt_count` INT NOT NULL DEFAULT 0
- `max_attempts` INT NOT NULL
- `last_error` TEXT NULL
- `last_error_at` TIMESTAMPTZ NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()
Indexes:
- Index on (`status`,`not_before_at`,`created_at`)
- Index on (`rewrite_request_id`,`recipient_user_id`)
Notes: status vocabulary matches async/queue contracts (queued, processing, completed, failed, canceled). No raw text in this table.

### 4. recipient_snapshots
Stores stable target set at request time.
- `recipient_snapshot_id` UUID PK
- `home_id` UUID NOT NULL
- `recipient_user_ids` UUID[] NOT NULL  -- for current flow this will be size 1
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
Note: immutable; referenced by rewrite_requests and rewrite_jobs.

### 5. recipient_preference_snapshots
Stores stable copy/refs of recipient preferences used for rewrite.
- `recipient_preference_snapshot_id` UUID PK
- `recipient_user_id` UUID NOT NULL
- `preference_payload` JSONB NOT NULL  -- minimal data needed by context pack; or pointer to versioned source
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
Note: immutable; referenced by rewrite_requests and rewrite_jobs.

### 6. routing_decisions (optional materialization)
If you materialize routing decisions separately for audit/cost:
- `routing_decision_id` UUID PK
- `rewrite_request_id` UUID NOT NULL
- `decision` JSONB NOT NULL          -- RoutingDecisionV1
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
Otherwise keep inside rewrite_jobs as defined.

## Relationships
- rewrite_jobs.rewrite_request_id → rewrite_requests.rewrite_request_id (CASCADE delete)
- rewrite_outputs.rewrite_request_id → rewrite_requests.rewrite_request_id (CASCADE delete)
- rewrite_requests.recipient_snapshot_id → recipient_snapshots.recipient_snapshot_id
- rewrite_requests.recipient_preference_snapshot_id → recipient_preference_snapshots.recipient_preference_snapshot_id
- rewrite_jobs snapshot fields mirror rewrite_requests to enforce drift-free processing.

## Status alignment
Canonical statuses across rewrite_requests, rewrite_jobs, async/queue: `queued`, `processing`, `completed`, `failed`, `canceled`. Map any legacy `running/succeeded` to `processing/completed`.

## Logging and privacy
- Tables above hold raw and rewritten text only in rewrite_requests.original_text and rewrite_outputs.rewritten_text. All other tables MUST avoid text content.
- Application logs MUST NOT log raw or rewritten text; store opaque IDs only.

## Reveal timing
- `sender_reveal_at` stored on rewrite_requests; set by orchestrator; async layer persists but does not compute it.

## Batching keys (normalization)
- When deriving batch_group_key (per async/routing), use normalized `source_locale`, `target_locale`, `lane`, `provider`, `model`, `prompt_version`, `policy_version`, `execution_mode`. Store batch metadata only in job-level audit logs, not in rewrite_outputs.

## TODO (linkage)
- Add explicit references to `rewrite_eval_v1` and `complaint_rewrite_lexicon_v1` once finalized to document where eval results are stored (`eval_result` column currently JSONB placeholder).
- If provider-level cost/call logs are needed, add a `provider_calls` table keyed by `rewrite_request_id` with opaque request/response IDs (no text bodies).
- See `complaint_rewrite_eval_and_lexicon_v1` for eval result field expectations and linkage.
