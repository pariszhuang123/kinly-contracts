---
Domain: Engineering
Capability: Doc Classification Investigation
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Documentation Classification & Scope Attribution v1.0 — Investigation

---
Domain: Engineering System
Capability: Documentation Governance
Scope: platform
Artifact-Type: process
Stability: evolving
Status: Draft (Investigation)
Version: v0.1
---

## Purpose

Document the investigation results for classifying existing Markdown/YAML docs by scope, artifact type, and stability to prep for a future backend/frontend split without moving files yet.

## Proposed Standard Header

Add this block at the top of each document:

```
---
Domain: <business or engineering domain>
Capability: <capability this doc owns>
Scope: backend|frontend|shared|platform
Artifact-Type: contract|architecture|adr|guide|process|reference
Stability: stable|evolving|ephemeral
Status: Draft|Proposed|Approved|Deprecated
Version: vX.Y
---
```

Examples:

- Backend contract (RPC):  
  ```
  ---
  Domain: HOME
  Capability: House Vibe Compute
  Scope: backend
  Artifact-Type: contract
  Stability: stable
  Status: Approved
  Version: v1.0
  ---
  ```
- Frontend contract (design system):  
  ```
  ---
  Domain: Design System
  Capability: Control Color Tokens
  Scope: frontend
  Artifact-Type: contract
  Stability: stable
  Status: Approved
  Version: v1.0
  ---
  ```
- Platform process (coordination):  
  ```
  ---
  Domain: Engineering System
  Capability: Agent Coordination
  Scope: platform
  Artifact-Type: process
  Stability: evolving
  Status: Draft
  Version: v1.0
  ---
  ```

## Inventory & Classification

Columns: path, current title, scope, artifact-type, stability, confidence, notes.

### contracts/**
| Path | Title | Scope | Artifact-Type | Stability | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| contracts/architecture/business_capabilities_map.yml | Business Capabilities Map | platform | reference | evolving | high | Source for business_map.md |
| contracts/architecture/business_map.md | (mermaid graph) | platform | architecture | evolving | high | Generated diagram |
| contracts/architecture/business_map_contract.md | Business Map Contract (v1) | platform | contract | stable | high | Architecture ownership |
| contracts/architecture/shopping_list_contract.md | Shopping List Contracts v1 | shared | contract | evolving | medium | Cross-surface feature |

### coordination/**
| Path | Title | Scope | Artifact-Type | Stability | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| coordination/COORDINATION_GUIDE.md | Coordination Guide | platform | process | evolving | high | Agent/coordination rules |
| coordination/memory_bank/calibration_values.md | Calibration Values | platform | reference | ephemeral | high | Working memory |
| coordination/memory_bank/dependencies.md | Environment Dependencies | platform | reference | evolving | high | Tooling deps |
| coordination/memory_bank/persona_paris.md | Persona – Paris (Quick Reference) | platform | reference | ephemeral | high | Persona note |
| coordination/memory_bank/test_failures.md | Test Failures Knowledge Base | platform | reference | evolving | high | Historical failures |
| coordination/orchestration/agent_assignments.md | Agent Assignments | platform | process | ephemeral | high | Task routing |
| coordination/orchestration/integration_plan.md | Integration Plan | platform | process | ephemeral | medium | Project-specific |
| coordination/orchestration/progress_tracker.md | Progress Tracker | platform | process | ephemeral | high | Status log |
| coordination/subtasks/README.md | Subtasks | platform | guide | evolving | high | How to break work |

### db/**
| Path | Title | Scope | Artifact-Type | Stability | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| db/README.md | Database Migrations & Workflow | backend | guide | evolving | high | DB process |

### docs/adr/**
| Path | Title | Scope | Artifact-Type | Stability | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| docs/adr/ADR-0001-mvp-home-scope.md | ADR-0001: Home-only MVP Scope and Guardrails | platform | adr | stable | high | Frozen decision |
| docs/adr/ADR-0001-user-auth-and-account-lifecycle.md | ADR-0001: User Auth (OAuth-only) and Account Lifecycle | backend | adr | stable | high | Auth decision |
| docs/adr/ADR-0002-invites-permanent-codes.md | ADR-0002: Permanent Invites (Until Revoked) | backend | adr | stable | high | Invites decision |
| docs/adr/ADR-0003-expenses-rpc-only-access.md | ADR-0003: Expenses RPC-Only Access Guardrail | backend | adr | stable | high | Access guardrail |

### docs/agents/**
| Path | Title | Scope | Artifact-Type | Stability | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| docs/agents/deep_linking.md | Deep Linking Agent | platform | guide | evolving | high | Agent role |
| docs/agents/docs.md | Docs Agent | platform | guide | evolving | high | Agent role |
| docs/agents/flutter_bloc.md | Flutter BLoC Agent | platform | guide | evolving | high | Agent role |
| docs/agents/flutter_ui.md | Flutter UI Agent | platform | guide | evolving | high | Agent role |
| docs/agents/paris.md | Paris – Working Memory | platform | guide | evolving | high | Persona guidance |
| docs/agents/planner.md | Planner Agent | platform | guide | evolving | high | Agent role |
| docs/agents/release.md | Release Agent | platform | guide | evolving | high | Agent role |
| docs/agents/supabase_db.md | Supabase/DB Agent | platform | guide | evolving | high | Agent role |
| docs/agents/test.md | Test Agent | platform | guide | evolving | high | Agent role |

### docs/architecture/**
| Path | Title | Scope | Artifact-Type | Stability | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| docs/architecture/di_graph.md | (mermaid graph) | shared | architecture | evolving | high | Dependency graph |
| docs/architecture/modules.md | graph LR | shared | architecture | evolving | medium | Needs header/titles |
| docs/architecture/report.md | Architecture Report | shared | architecture | evolving | high | Narrative report |

### docs/contracts/**
| Path | Title | Scope | Artifact-Type | Stability | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| docs/contracts/app_v1.md | App Contracts v1 – Versioning and Update Policy | shared | contract | stable | high | App update policy |
| docs/contracts/architecture_guardrails_amendment_foundation_surfaces_v1.md | Architecture Guardrails Amendment – Foundation Surfaces v1 (Kinly) | shared | contract | stable | medium | Amendment to guardrails |
| docs/contracts/CHANGELOG.md | Contracts Changelog | platform | reference | stable | high | Version history |
| docs/contracts/chores_v1.md | Chores Contracts v1 | backend | contract | stable | high | Chores domain |
| docs/contracts/chores_v2.md | Chores Contracts v2 | backend | contract | evolving | high | Newer chores |
| docs/contracts/codex_i18n_hygiene.md | Codex i18n Hygiene (CODEX-L10N-001) | platform | process | evolving | high | i18n rules |
| docs/contracts/copy_taste_v1_1.md | Kinly Copy & Product Taste Contract v1.1 | frontend | contract | stable | high | UX copy |
| docs/contracts/core_placement_rules_v1.md | Status: Proposed | frontend | contract | evolving | medium | Needs header/title |
| docs/contracts/daily_notifications_phase1.md | Daily Notifications – Phase 1 (Kinly) | backend | contract | evolving | medium | Notification RPC/cron |
| docs/contracts/expenses_v1.md | Expenses Contracts v1 | backend | contract | stable | high | Expenses domain |
| docs/contracts/expenses_v2.md | Expenses Contracts v2 | backend | contract | evolving | high | New expenses |
| docs/contracts/form_hydration_v1.md | Kinly Form Hydration Contract v1 | shared | contract | stable | high | Form data contract |
| docs/contracts/gratitude_mentions_v1.md | Weekly Feedback – Gratitude + Mentions v1 | backend | contract | evolving | medium | Social feature |
| docs/contracts/gratitude_wall_v1.md | Kinly Gratitude Wall Contract v1 | backend | contract | evolving | medium | Social feature |
| docs/contracts/home_dynamics_v1.md | Kinly Contract v1 - Home Preferences, Vibe, and Rules | shared | contract | stable | high | Preferences rules |
| docs/contracts/homes_v1.md | Kinly Contracts v1 – Home MVP | backend | contract | stable | high | Home domain |
| docs/contracts/homes_v2.md | Kinly Contracts v2 – Home MVP (membership stints) | backend | contract | evolving | high | New home model |
| docs/contracts/house_vibe_aggregation_contract_v1.md | House Vibe Aggregation Contract v1 | backend | contract | stable | high | Aggregation logic |
| docs/contracts/house_vibe_asset_resolution_v1.md | House Vibe Asset Resolution v1 | frontend | contract | stable | high | Asset mapping |
| docs/contracts/house_vibe_canonical_preference_schema_v1.md | House Vibe Canonical Preference Schema v1 | backend | contract | stable | high | Preference payload |
| docs/contracts/house_vibe_compute_rpc_contract_v1.md | House Vibe Compute RPC Contract v1 | backend | contract | stable | high | RPC contract |
| docs/contracts/house_vibe_label_registry_contract_v1.md | House Vibe Label Registry Contract v1 (Presentation Metadata) | frontend | contract | stable | high | UI metadata |
| docs/contracts/house_vibe_mapping_contract_v1.md | House Vibe Mapping Contract v1 (Axes + Label) | shared | contract | stable | high | Mapping rules |
| docs/contracts/house_vibe_mapping_effects_v1.md | House Vibe Mapping Effects v1 (pref_id + axes) | backend | reference | stable | high | Mapping table |
| docs/contracts/house_vibe_overview_v1.md | House Vibe v1 – Overview Contract | shared | guide | stable | high | Overview |
| docs/contracts/house_vibe_share_contract_v1.md | House Vibe Share Contract v1 (Social Sharing Image) | frontend | contract | stable | high | Share image |
| docs/contracts/hub_personal_preferences_visibility_v1.md | Kinly Hub Personal Preferences Visibility Contract v1 | frontend | contract | stable | medium | Hub display rules |
| docs/contracts/kinly_avatar_identity_v1.md | Kinly Avatar Identity Contract v1 | shared | contract | stable | high | Avatar identity |
| docs/contracts/kinly_composable_system_v1.md | Kinly Foundation Composable System Contract v1 | frontend | contract | stable | high | Design system |
| docs/contracts/kinly_control_color_tokens_v1.md | Kinly Control Color Tokens Contract v1.0 | frontend | contract | stable | high | Color tokens |
| docs/contracts/kinly_derived_color_engine_v1.md | Kinly Derived Color Engine Contract v1.0 | frontend | contract | stable | high | Color derivation |
| docs/contracts/kinly_design_system_v1.md | Kinly Design System Contract v1 | frontend | contract | stable | high | Design system |
| docs/contracts/kinly_foundation_colors_v1.md | Kinly Foundation Colors Contract v1.0 | frontend | contract | stable | high | Color palette |
| docs/contracts/kinly_foundation_surfaces_amendment_v1.md | Status: Proposed | shared | contract | evolving | medium | Needs explicit header |
| docs/contracts/member_cap_paywall_v1.md | Member Cap Paywall (v1) | shared | contract | evolving | medium | Paywall variant |
| docs/contracts/mood_nps.md | Mood & NPS Contracts v1 | backend | contract | stable | high | Mood/NPS |
| docs/contracts/paywall_gate.md | Paywall Gate Contract (Client) | frontend | contract | stable | high | Client gating |
| docs/contracts/paywall_personalized_primary_benefit_v1.md | Context-Aware Paywall v1 (Personalized Primary Benefit) | shared | contract | evolving | medium | Personalization rules |
| docs/contracts/paywall_v1.md | Kinly Premium Paywall – Phase 1 Contract | shared | contract | stable | high | Paywall core |
| docs/contracts/preference_reports_v1.md | Kinly Preference Report Contract v1 | backend | contract | stable | medium | Reporting |
| docs/contracts/preference_scenarios_v1.md | Kinly Preference Interpretation & Scenarios Contract v1 | shared | contract | stable | medium | Interpretation |
| docs/contracts/preference_taxonomy_v1.md | Kinly Contract v1 - Preference Taxonomy | shared | contract | stable | high | Taxonomy |
| docs/contracts/shared_understanding_copy_v1.md | Kinly Shared Understanding Copy Contract v1.0 | frontend | contract | stable | high | Copy set |
| docs/contracts/share_recurring_v1.md | Kinly Share – One-Off & Recurring Expenses (v1.1) | backend | contract | stable | high | Share expenses |
| docs/contracts/testing_v1.md | Testing – Unified Contract (v1) | platform | contract | stable | high | Testing contract |
| docs/contracts/users_deactivation_v1.md | Users Deactivation v1 — Leave + Flag Profile | backend | contract | stable | high | User lifecycle |
| docs/contracts/users_v1.md | Users Contracts v1 – Auth and Lifecycle | backend | contract | stable | high | User lifecycle |
| docs/contracts/weekly_house_pulse_v1.md | Kinly Weekly House Pulse Contract v1 | backend | contract | evolving | medium | Engagement metric |
| docs/contracts/welcome_avatar_personal_profile_v1.md | Welcome Avatar & Personal Profile Access v1 (Adjusted) | frontend | contract | stable | medium | Onboarding UI |

### docs/db/**
| Path | Title | Scope | Artifact-Type | Stability | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| docs/db/chores.md | Chores DB Notes (v1) | backend | reference | evolving | medium | DB notes |
| docs/db/migrations.md | DB Migrations (MVP) | backend | guide | evolving | high | Migration process |

### docs/design-system/**
| Path | Title | Scope | Artifact-Type | Stability | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| docs/design-system/README.md | Kinly Design System | frontend | guide | stable | high | Overview |
| docs/design-system/components.md | Kinly Component Specifications | frontend | reference | stable | high | Component specs |

### docs/diagrams/**
| Path | Title | Scope | Artifact-Type | Stability | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| docs/diagrams/README.md | Diagrams – Mermaid Quick Guide | platform | guide | stable | high | How-to |
| docs/diagrams/chores/chore_flow.md | Chore Flow (MVP, aligned with Chores Contracts v1) | shared | reference | stable | high | Flow diagram |
| docs/diagrams/expenses/expense_lifecycle.md | (mermaid) | backend | reference | stable | medium | Diagram only |
| docs/diagrams/home_membership/*.md | (mermaid diagrams) | backend | reference | stable | high | Home membership diagrams |
| docs/diagrams/mood_nps/mood_nps_er.md | Mood & NPS ER View | backend | reference | stable | high | ER diagram |
| docs/diagrams/mood_nps/mood_nps_flow.md | Mood & NPS Flow | backend | reference | stable | high | Flow |
| docs/diagrams/notifications/daily_notifications_phase1.md | Daily Notifications - Phase 1 (Sequence) | backend | reference | stable | high | Sequence |
| docs/diagrams/user/*.md | (mermaid diagrams) | shared | reference | stable | medium | User flows |

### docs/engineering/**
| Path | Title | Scope | Artifact-Type | Stability | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| docs/engineering/architecture_guardrails_v1_1.md | Architecture Guardrails Contract v1.1 (Kinly) | platform | contract | stable | high | Guardrails |
| docs/engineering/branching_releases.md | Branching & Releases (MVP) | platform | process | stable | high | Release process |
| docs/engineering/complexity_budget_v1.md | Complexity Budget Contract (v1) | platform | contract | stable | high | CC budget |
| docs/engineering/composable_system_audit_v1.md | Composable System Audit v1 | frontend | reference | evolving | medium | Audit notes |
| docs/engineering/conventions.md | Engineering Conventions (MVP) | platform | guide | stable | high | Conventions |
| docs/engineering/module_guardrails.md | Module Guardrails Checklist | platform | guide | stable | high | Checklist |
| docs/engineering/ownership.md | Code Ownership (MVP) | platform | process | stable | high | Ownership |
| docs/engineering/pr_review.md | PR & Review Policy (MVP) | platform | process | stable | high | Review rules |
| docs/engineering/repo_migration_contract_v1.md | Repo Migration Contract v1 | platform | contract | evolving | high | Migration plan |
| docs/engineering/sentry_android_native_symbols.md | Contract: Upload Android native debug symbols to Sentry (Flutter) v1 | platform | process | stable | high | Release ops |

### docs/flows/**
| Path | Title | Scope | Artifact-Type | Stability | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| docs/flows/home_membership/*.md | Flow – Invite/Join/Kick/Leave/Transfer | shared | guide | stable | high | Flow guides |
| docs/flows/user/account_deletion.md | Flow – Account Deletion (Admin-Approved) | shared | guide | stable | medium | Admin flow |
| docs/flows/user/auth.md | Flow – User Auth (Google/Apple) | shared | guide | stable | high | Auth flow |
| docs/flows/user/avatars.md | Flow – Per-Home Unique Avatars | shared | guide | stable | high | Avatar flow |
| docs/flows/user/logout.md | Flow – Logout | shared | guide | stable | high | Logout flow |

### docs/runbooks/**
| Path | Title | Scope | Artifact-Type | Stability | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| docs/runbooks/ci_secrets.md | CI Secrets: What Goes Where | platform | guide | stable | high | Runbook |
| docs/runbooks/smoke.md | Post-Deploy Smoke – Home MVP | platform | guide | stable | high | Runbook |
| docs/runbooks/smoke_addenda.md | Post-Deploy Smoke – Additional Scenarios | platform | guide | stable | high | Runbook |

### docs/templates/**
| Path | Title | Scope | Artifact-Type | Stability | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| docs/templates/planning_skeleton.md | Planning Skeleton – BLoC/Repo (SPARC P Phase) | platform | template | stable | high | Template |
| docs/templates/pseudocode.md | Pseudocode Template – SPARC (P Phase) | platform | template | stable | high | Template |
| docs/templates/reasoning_note.md | Reasoning Note | platform | template | stable | high | Template |
| docs/templates/spec.md | Spec Template – SPARC (S Phase) | platform | template | stable | high | Template |

### docs/testing/**
| Path | Title | Scope | Artifact-Type | Stability | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| docs/testing/chores.md | Chores Test Plan (MVP) | backend | guide | stable | high | Tests |
| docs/testing/conventions.md | Testing Conventions (MVP) | platform | guide | stable | high | Conventions |
| docs/testing/rls.md | RLS Test Plan – Home MVP | backend | guide | stable | high | RLS tests |
| docs/testing/rls_addenda.md | RLS Test Addenda – Owner/Member and Invites | backend | guide | stable | high | Addenda |
| docs/testing/rpc.md | RPC/Edge Test Plan – Home MVP | backend | guide | stable | high | RPC tests |
| docs/testing/rpc_addenda.md | RPC Test Addenda – Rotate, Kick, Leave, Transfer | backend | guide | stable | high | Addenda |

### docs/ui/**
| Path | Title | Scope | Artifact-Type | Stability | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| docs/ui/core_ui_primitives.md | Kinly Core UI Primitives | frontend | contract | stable | high | UI primitives |
| docs/ui/reflective_generation_v1.md | Reflective Generation Contract (v1) | frontend | contract | evolving | medium | UI copy |

### docs/engineering/other and misc
| Path | Title | Scope | Artifact-Type | Stability | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| docs/engineering/composable_system_audit_v1.md | Composable System Audit v1 | frontend | reference | evolving | medium | Audit |

## Header Blocks to Apply (high confidence)

Add the standard header with these values:

- `db/README.md`  
  ```
  ---
  Domain: Engineering System
  Capability: Database Migrations
  Scope: backend
  Artifact-Type: guide
  Stability: evolving
  Status: Approved
  Version: v1.0
  ---
  ```
- `docs/adr/ADR-0001-mvp-home-scope.md`  
  ```
  ---
  Domain: PLATFORM
  Capability: Home MVP Scope
  Scope: platform
  Artifact-Type: adr
  Stability: stable
  Status: Approved
  Version: v1.0
  ---
  ```
- `docs/adr/ADR-0001-user-auth-and-account-lifecycle.md`  
  ```
  ---
  Domain: IDENTITY
  Capability: Auth & Account Lifecycle
  Scope: backend
  Artifact-Type: adr
  Stability: stable
  Status: Approved
  Version: v1.0
  ---
  ```
- `docs/adr/ADR-0002-invites-permanent-codes.md`  
  ```
  ---
  Domain: HOME
  Capability: Invites
  Scope: backend
  Artifact-Type: adr
  Stability: stable
  Status: Approved
  Version: v1.0
  ---
  ```
- `docs/adr/ADR-0003-expenses-rpc-only-access.md`  
  ```
  ---
  Domain: SHARE
  Capability: Expenses Access Control
  Scope: backend
  Artifact-Type: adr
  Stability: stable
  Status: Approved
  Version: v1.0
  ---
  ```
- `docs/contracts/homes_v2.md`  
  ```
  ---
  Domain: HOME
  Capability: Homes & Membership Stints
  Scope: backend
  Artifact-Type: contract
  Stability: evolving
  Status: Draft
  Version: v2.0
  ---
  ```
- `docs/contracts/home_dynamics_v1.md`  
  ```
  ---
  Domain: HOME
  Capability: Home Preferences & Rules
  Scope: shared
  Artifact-Type: contract
  Stability: stable
  Status: Approved
  Version: v1.0
  ---
  ```
- `docs/contracts/house_vibe_canonical_preference_schema_v1.md`  
  ```
  ---
  Domain: HOME
  Capability: House Vibe Preferences Schema
  Scope: backend
  Artifact-Type: contract
  Stability: stable
  Status: Approved
  Version: v1.0
  ---
  ```
- `docs/contracts/house_vibe_compute_rpc_contract_v1.md`  
  ```
  ---
  Domain: HOME
  Capability: House Vibe Compute
  Scope: backend
  Artifact-Type: contract
  Stability: stable
  Status: Approved
  Version: v1.0
  ---
  ```
- `docs/contracts/house_vibe_label_registry_contract_v1.md`  
  ```
  ---
  Domain: Design System
  Capability: House Vibe Label Registry
  Scope: frontend
  Artifact-Type: contract
  Stability: stable
  Status: Approved
  Version: v1.0
  ---
  ```
- `docs/contracts/house_vibe_mapping_contract_v1.md`  
  ```
  ---
  Domain: HOME
  Capability: House Vibe Mapping
  Scope: shared
  Artifact-Type: contract
  Stability: stable
  Status: Approved
  Version: v1.0
  ---
  ```
- `docs/contracts/house_vibe_mapping_effects_v1.md`  
  ```
  ---
  Domain: HOME
  Capability: House Vibe Mapping Effects
  Scope: backend
  Artifact-Type: reference
  Stability: stable
  Status: Approved
  Version: v1.0
  ---
  ```
- `docs/contracts/kinly_control_color_tokens_v1.md`  
  ```
  ---
  Domain: Design System
  Capability: Control Color Tokens
  Scope: frontend
  Artifact-Type: contract
  Stability: stable
  Status: Approved
  Version: v1.0
  ---
  ```
- `docs/contracts/kinly_design_system_v1.md`  
  ```
  ---
  Domain: Design System
  Capability: Design System Foundations
  Scope: frontend
  Artifact-Type: contract
  Stability: stable
  Status: Approved
  Version: v1.0
  ---
  ```
- `docs/contracts/paywall_v1.md`  
  ```
  ---
  Domain: MONETIZATION
  Capability: Premium Paywall
  Scope: shared
  Artifact-Type: contract
  Stability: stable
  Status: Approved
  Version: v1.0
  ---
  ```
- `docs/contracts/share_recurring_v1.md`  
  ```
  ---
  Domain: SHARE
  Capability: Recurring Expenses
  Scope: backend
  Artifact-Type: contract
  Stability: stable
  Status: Approved
  Version: v1.1
  ---
  ```
- `docs/contracts/users_v1.md`  
  ```
  ---
  Domain: IDENTITY
  Capability: Users Auth & Lifecycle
  Scope: backend
  Artifact-Type: contract
  Stability: stable
  Status: Approved
  Version: v1.0
  ---
  ```
- `docs/contracts/testing_v1.md`  
  ```
  ---
  Domain: Engineering System
  Capability: Testing Guardrails
  Scope: platform
  Artifact-Type: contract
  Stability: stable
  Status: Approved
  Version: v1.0
  ---
  ```
- `docs/engineering/architecture_guardrails_v1_1.md`  
  ```
  ---
  Domain: Engineering System
  Capability: Architecture Guardrails
  Scope: platform
  Artifact-Type: contract
  Stability: stable
  Status: Approved
  Version: v1.1
  ---
  ```
- `docs/engineering/complexity_budget_v1.md`  
  ```
  ---
  Domain: Engineering System
  Capability: Complexity Budget
  Scope: platform
  Artifact-Type: contract
  Stability: stable
  Status: Approved
  Version: v1.0
  ---
  ```
- `docs/ui/core_ui_primitives.md`  
  ```
  ---
  Domain: Design System
  Capability: Core UI Primitives
  Scope: frontend
  Artifact-Type: contract
  Stability: stable
  Status: Approved
  Version: v1.0
  ---
  ```

## Future Folder Mapping (no moves yet)

- Backend contracts → `kinly-backend/docs/contracts/<domain>/<topic>.md`
- Backend ADRs/tests/runbooks → `kinly-backend/docs/{adr,testing,runbooks}/...`
- Frontend design system & flows → `kinly-frontend/docs/design-system/...` and `kinly-frontend/docs/flows/...`
- Shared contracts (e.g., preference taxonomy, shared enums) → `kinly-shared/contracts/...`
- Platform/process/agent docs → remain in mono-repo or `kinly-platform/docs/...`
- Diagrams follow their owning scope: backend diagrams to backend repo, frontend diagrams to frontend repo, shared diagrams to shared.

## Open Questions (low confidence areas)

- How to tag mixed-scope docs like `paywall_personalized_primary_benefit_v1` (shared personalization vs frontend presentation)?
- Should coordination/memory_bank entries stay ephemeral (excluded from migration) or move to platform repo?
- Where to place cross-surface UX copy (e.g., `shared_understanding_copy_v1`) in a multi-repo world—frontend or shared?

## Contract Critique

- Good: emphasizes non-destructive classification, clear scopes/types/stability, and header standardization before moving files.  
- Risk: “Codex MUST” scope is large—manual header proposals for all high-confidence files may be heavy; consider batching or scripting.  
- Clarify: whether “template” is an allowed Artifact-Type or should be normalized to “guide/reference”; whether ephemeral coordination docs need headers.  
- Add: explicit success metric for future mapping (e.g., zero cross-scope ambiguity) and guidance on how to version headers when docs change without content moves.