---
Domain: Product
Capability: complaint_rewrite
Scope: backend
Artifact-Type: guide
Stability: stable
Status: active
Version: v1.0
Audience: internal
Last updated: 2026-02-01
---

# Complaint Rewrite System Map (Mermaid)

```mermaid
flowchart TD
  FH["Frontend Weekly Harmony<br/>complaint_rewrite_frontend_weekly_harmony_v1"] --> ORCH
  ORCH["Edge Orchestrator<br/>complaint_rewrite_edge_orchestrator_v1"] -->|persist raw msg| REQ["rewrite_requests (storage)"]
  ORCH -->|call| CLF["AI Classifier<br/>complaint_rewrite_ai_classifier_v1"]
  ORCH -->|build| CTX["Recipient Context Pack<br/>complaint_rewrite_backend_context_pack_v1"]
  ORCH -->|locales+lane| LANE["Two-Lane Async<br/>complaint_rewrite_two_lanes_async_v1"]
  ORCH -->|route| ROUTE["AI Routing & Providers<br/>complaint_rewrite_ai_routing_providers_v1"]
  ORCH -->|enqueue| QUEUE["Queue Processing & Backpressure<br/>complaint_rewrite_queue_processing_v1"]

  QUEUE --> JOBS["rewrite_jobs (storage)"]
  QUEUE --> ASYNC["Async Jobs Execution<br/>complaint_rewrite_async_jobs_v1"]
  ASYNC -->|provider call| MODEL[("AI Provider")]
  MODEL -->|response| ASYNC
  ASYNC --> EVAL["Lexicon / Eval<br/>(rewrite_eval_v1, complaint_rewrite_lexicon_v1) TODO link"]
  EVAL --> OUTS
  ASYNC --> OUTS["rewrite_outputs (storage)"]
  OUTS --> RECIP["Recipient delivery"]
  OUTS -->|after sender_reveal_at| SENDER["Sender reveal"]

  subgraph Storage
    REQ
    OUTS
    JOBS
  end

  CTX --> REQ
  ROUTE --> JOBS
  LANE --> JOBS
  CTX -. "snapshot refs" .-> JOBS
```

Notes
- Storage tables reference: `complaint_rewrite_storage_schema_v1`.
- Eval/lexicon contracts are TODO links until finalized.
- Status vocabulary across queue/async/storage: queued -> processing -> completed -> failed -> canceled.
