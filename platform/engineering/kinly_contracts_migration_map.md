---
Domain: Engineering
Capability: Kinly Contracts Migration Map
Scope: platform
Artifact-Type: process
Stability: evolving
Status: draft
Version: v1.0
---

# Migration Map — kinly → kinly-contracts

Non-destructive classification of kinly docs/contracts into kinly-contracts buckets. No file moves performed.

## Bucket A — API Contracts → contracts/api/kinly/**
- docs/contracts/homes_v2.md → contracts/api/kinly/homes/homes_v2.md (RPC contract: homes.create/join/leave/transfer, membership stints)
- docs/contracts/homes_v1.md → contracts/api/kinly/homes/homes_v1.md (legacy home RPC contract)
- docs/contracts/house_vibe_compute_rpc_contract_v1.md → contracts/api/kinly/homes/house_vibe_compute_rpc_contract_v1.md (RPC request/response + guards)
- docs/contracts/house_vibe_canonical_preference_schema_v1.md → contracts/api/kinly/homes/house_vibe_canonical_preference_schema_v1.md (canonical payload shape)
- docs/contracts/house_vibe_aggregation_contract_v1.md → contracts/api/kinly/homes/house_vibe_aggregation_contract_v1.md (server aggregation contract)
- docs/contracts/house_vibe_asset_resolution_v1.md → contracts/api/kinly/homes/house_vibe_asset_resolution_v1.md (asset resolution inputs/outputs)
- docs/contracts/expenses_v2.md → contracts/api/kinly/share/expenses_v2.md (RPC shapes/guards)
- docs/contracts/expenses_v1.md → contracts/api/kinly/share/expenses_v1.md (legacy)
- docs/contracts/share_recurring_api_v1.md → contracts/api/kinly/share/share_recurring_api_v1.md (recurring expenses API contract)
- docs/contracts/users_v1.md → contracts/api/kinly/identity/users_v1.md (auth/lifecycle contract)
- docs/contracts/users_deactivation_v1.md → contracts/api/kinly/identity/users_deactivation_v1.md (deactivation rules)
- docs/contracts/testing_v1.md → contracts/api/kinly/platform/testing_v1.md (testing contract for API/RPC/RLS expectations)
- docs/contracts/form_hydration_v1.md → contracts/api/kinly/forms/form_hydration_v1.md (form hydration contract)
- docs/contracts/house_vibe_mapping_effects_v1.md → contracts/api/kinly/homes/house_vibe_mapping_effects_v1.md (mapping effects reference)
- docs/contracts/paywall_gate.md → contracts/api/kinly/paywall/paywall_gate.md (legacy combined view; superseded by split files)
- docs/contracts/share_recurring_v1.md → contracts/api/kinly/share/share_recurring_v1.md (legacy combined view; superseded by split files)

## Bucket B — Product Rules → contracts/product/kinly/{shared|mobile|web}/**
- docs/contracts/home_dynamics_v1.md → contracts/product/kinly/shared/home_dynamics_v1.md (preferences/vibe/rules)
- docs/contracts/preference_taxonomy_v1.md → contracts/product/kinly/shared/preference_taxonomy_v1.md (taxonomy rules)
- docs/contracts/preference_scenarios_v1.md → contracts/product/kinly/shared/preference_scenarios_v1.md (interpretation)
- docs/contracts/preference_reports_v1.md → contracts/product/kinly/shared/preference_reports_v1.md (report generation rules)
- docs/contracts/hub_personal_preferences_visibility_v1.md → contracts/product/kinly/mobile/hub_personal_preferences_visibility_v1.md (app display rules)
- docs/contracts/weekly_house_pulse_v1.md → contracts/product/kinly/shared/weekly_house_pulse_v1.md (engagement metric behavior)
- docs/contracts/daily_notifications_phase1.md → contracts/product/kinly/shared/daily_notifications_phase1.md (notification behavior)
- docs/contracts/member_cap_paywall_v1.md → contracts/product/kinly/shared/member_cap_paywall_v1.md (paywall rules)
- docs/contracts/paywall_v1.md → contracts/product/kinly/shared/paywall_v1.md (premium paywall behavior)
- docs/contracts/paywall_gate_product_v1.md → contracts/product/kinly/mobile/paywall_gate_product_v1.md (client gating rules)
- docs/contracts/paywall_personalized_primary_benefit_v1.md → contracts/product/kinly/shared/paywall_personalized_primary_benefit_v1.md (personalization rules)
- docs/contracts/welcome_avatar_personal_profile_v1.md → contracts/product/kinly/mobile/welcome_avatar_personal_profile_v1.md (onboarding UX rules)
- docs/contracts/app_v1.md → contracts/product/kinly/shared/app_v1.md (app versioning/update policy)
- docs/contracts/house_vibe_overview_v1.md → contracts/product/kinly/shared/house_vibe_overview_v1.md (product-facing overview)
- docs/contracts/house_vibe_share_contract_v1.md → contracts/product/kinly/mobile/house_vibe_share_contract_v1.md (share image behavior)
- docs/contracts/house_vibe_mapping_contract_v1.md → contracts/product/kinly/shared/house_vibe_mapping_contract_v1.md (mapping rules)
- docs/contracts/mood_nps.md → contracts/product/kinly/shared/mood_nps.md (NPS product rules)
- docs/contracts/gratitude_wall_v1.md → contracts/product/kinly/shared/gratitude_wall_v1.md
- docs/contracts/gratitude_mentions_v1.md → contracts/product/kinly/shared/gratitude_mentions_v1.md
- docs/contracts/chores_v2.md → contracts/product/kinly/shared/chores_v2.md (product behavior; API split lives under Bucket A if RPC shapes exist)
- docs/contracts/chores_v1.md → contracts/product/kinly/shared/chores_v1.md
- docs/contracts/share_recurring_product_v1.md → contracts/product/kinly/shared/share_recurring_product_v1.md (product rules; paired with API doc)
- docs/ui/reflective_generation_v1.md → contracts/product/kinly/shared/reflective_generation_v1.md (system UX pattern)

## Bucket C — Design System → contracts/design/{tokens|copy}/kinly/**
- docs/contracts/kinly_control_color_tokens_v1.md → contracts/design/tokens/kinly/kinly_control_color_tokens_v1.md (tokens)
- docs/contracts/kinly_foundation_colors_v1.md → contracts/design/tokens/kinly/kinly_foundation_colors_v1.md
- docs/contracts/kinly_derived_color_engine_v1.md → contracts/design/tokens/kinly/kinly_derived_color_engine_v1.md
- docs/contracts/kinly_design_system_v1.md → contracts/design/tokens/kinly/kinly_design_system_v1.md (foundations)
- docs/contracts/kinly_composable_system_v1.md → contracts/design/tokens/kinly/kinly_composable_system_v1.md (layout primitives)
- docs/contracts/kinly_avatar_identity_v1.md → contracts/design/tokens/kinly/kinly_avatar_identity_v1.md
- docs/contracts/kinly_foundation_surfaces_amendment_v1.md → contracts/design/tokens/kinly/kinly_foundation_surfaces_amendment_v1.md
- docs/contracts/kinly_core_ui_primitives.md → contracts/design/tokens/kinly/core_ui_primitives.md
- docs/contracts/paywall_gate_copy_v1.md → contracts/design/copy/kinly/paywall_gate_copy_v1.md
- docs/contracts/copy_taste_v1_1.md → contracts/design/copy/kinly/copy_taste_v1_1.md
- docs/contracts/shared_understanding_copy_v1.md → contracts/design/copy/kinly/shared_understanding_copy_v1.md
- docs/contracts/house_vibe_label_registry_contract_v1.md → contracts/design/copy/kinly/house_vibe_label_registry_contract_v1.md (presentation metadata)
- docs/design-system/README.md → contracts/design/reference/kinly/design_system_readme.md
- docs/design-system/components.md → contracts/design/reference/kinly/components.md

## Bucket D — Architecture → architecture/**
- docs/architecture/di_graph.md → architecture/di_graph.md (dependency graph)
- docs/architecture/modules.md → architecture/modules.md
- docs/architecture/report.md → architecture/report.md
- docs/diagrams/** → architecture/diagrams/** (all Mermaid diagrams by domain)
- docs/flows/** → architecture/flows/** (flow guides; architectural reference)
- docs/engineering/repo_migration_contract_v1.md → architecture/repo_migration_contract_v1.md (repo topology)
- contracts/architecture/** → architecture/contracts/** (business map, shopping list)
- docs/architecture_guardrails_v1_1.md → architecture/architecture_guardrails_v1_1.md
- docs/engineering/complexity_budget_v1.md → architecture/complexity_budget_v1.md (architecture governance reference)
- docs/diagrams/README.md → architecture/diagrams/README.md
- docs/diagrams/chores/chore_flow.md → architecture/diagrams/chores/chore_flow.md
- docs/diagrams/expenses/expense_lifecycle.md → architecture/diagrams/expenses/expense_lifecycle.md
- docs/diagrams/home_membership/README.md → architecture/diagrams/home_membership/README.md
- docs/diagrams/home_membership/home_state.md → architecture/diagrams/home_membership/home_state.md
- docs/diagrams/home_membership/invite_rotation.md → architecture/diagrams/home_membership/invite_rotation.md
- docs/diagrams/home_membership/join_flow.md → architecture/diagrams/home_membership/join_flow.md
- docs/diagrams/home_membership/kick_member.md → architecture/diagrams/home_membership/kick_member.md
- docs/diagrams/home_membership/leave_home.md → architecture/diagrams/home_membership/leave_home.md
- docs/diagrams/home_membership/ownership_model.md → architecture/diagrams/home_membership/ownership_model.md
- docs/diagrams/home_membership/permissions_flow.md → architecture/diagrams/home_membership/permissions_flow.md
- docs/diagrams/home_membership/transfer_owner_flow.md → architecture/diagrams/home_membership/transfer_owner_flow.md
- docs/diagrams/home_membership/transfer_owner_sequence.md → architecture/diagrams/home_membership/transfer_owner_sequence.md
- docs/diagrams/mood_nps/mood_nps_er.md → architecture/diagrams/mood_nps/mood_nps_er.md
- docs/diagrams/mood_nps/mood_nps_flow.md → architecture/diagrams/mood_nps/mood_nps_flow.md
- docs/diagrams/notifications/daily_notifications_phase1.md → architecture/diagrams/notifications/daily_notifications_phase1.md
- docs/diagrams/user/account_deletion.md → architecture/diagrams/user/account_deletion.md
- docs/diagrams/user/auth_providers.md → architecture/diagrams/user/auth_providers.md
- docs/diagrams/user/avatar_uniqueness.md → architecture/diagrams/user/avatar_uniqueness.md
- docs/diagrams/user/logout.md → architecture/diagrams/user/logout.md
- docs/flows/home_membership/invite_rotation.md → architecture/flows/home_membership/invite_rotation.md
- docs/flows/home_membership/join.md → architecture/flows/home_membership/join.md
- docs/flows/home_membership/kick_member.md → architecture/flows/home_membership/kick_member.md
- docs/flows/home_membership/leave_home.md → architecture/flows/home_membership/leave_home.md
- docs/flows/home_membership/transfer_owner.md → architecture/flows/home_membership/transfer_owner.md
- docs/flows/user/account_deletion.md → architecture/flows/user/account_deletion.md
- docs/flows/user/auth.md → architecture/flows/user/auth.md
- docs/flows/user/avatars.md → architecture/flows/user/avatars.md
- docs/flows/user/logout.md → architecture/flows/user/logout.md
- contracts/architecture/business_capabilities_map.yml → architecture/contracts/business_capabilities_map.yml
- contracts/architecture/business_map.md → architecture/contracts/business_map.md
- contracts/architecture/business_map_contract.md → architecture/contracts/business_map_contract.md
- contracts/architecture/shopping_list_contract.md → architecture/contracts/shopping_list_contract.md
- docs/engineering/architecture_guardrails_v1_1.md → architecture/architecture_guardrails_v1_1.md

## Bucket E — Decisions → decisions/**
- docs/adr/ADR-0001-mvp-home-scope.md → decisions/ADR-0001-mvp-home-scope.md
- docs/adr/ADR-0001-user-auth-and-account-lifecycle.md → decisions/ADR-0001-user-auth-and-account-lifecycle.md
- docs/adr/ADR-0002-invites-permanent-codes.md → decisions/ADR-0002-invites-permanent-codes.md
- docs/adr/ADR-0003-expenses-rpc-only-access.md → decisions/ADR-0003-expenses-rpc-only-access.md

## Bucket F — Unclear / Mixed → _incoming/kinly/**
- Currently empty after splitting paywall_gate and share_recurring. Use for any newly discovered mixed-scope files that cannot be cleanly classified in <10 seconds.

## Bucket G — Platform / Process / Guardrails → platform/**
- coordination/COORDINATION_GUIDE.md → platform/coordination/COORDINATION_GUIDE.md
- coordination/orchestration/agent_assignments.md → platform/coordination/orchestration/agent_assignments.md
- coordination/orchestration/integration_plan.md → platform/coordination/orchestration/integration_plan.md
- coordination/orchestration/progress_tracker.md → platform/coordination/orchestration/progress_tracker.md
- coordination/memory_bank/calibration_values.md → platform/coordination/memory_bank/calibration_values.md
- coordination/memory_bank/dependencies.md → platform/coordination/memory_bank/dependencies.md
- coordination/memory_bank/persona_paris.md → platform/coordination/memory_bank/persona_paris.md
- coordination/memory_bank/test_failures.md → platform/coordination/memory_bank/test_failures.md
- coordination/subtasks/README.md → platform/coordination/subtasks/README.md
- docs/agents/deep_linking.md → platform/agents/deep_linking.md
- docs/agents/docs.md → platform/agents/docs.md
- docs/agents/flutter_bloc.md → platform/agents/flutter_bloc.md
- docs/agents/flutter_ui.md → platform/agents/flutter_ui.md
- docs/agents/paris.md → platform/agents/paris.md
- docs/agents/planner.md → platform/agents/planner.md
- docs/agents/release.md → platform/agents/release.md
- docs/agents/supabase_db.md → platform/agents/supabase_db.md
- docs/agents/test.md → platform/agents/test.md
- docs/runbooks/ci_secrets.md → platform/runbooks/ci_secrets.md
- docs/runbooks/smoke.md → platform/runbooks/smoke.md
- docs/runbooks/smoke_addenda.md → platform/runbooks/smoke_addenda.md
- docs/testing/chores.md → platform/testing/chores.md
- docs/testing/conventions.md → platform/testing/conventions.md
- docs/testing/rls.md → platform/testing/rls.md
- docs/testing/rls_addenda.md → platform/testing/rls_addenda.md
- docs/testing/rpc.md → platform/testing/rpc.md
- docs/testing/rpc_addenda.md → platform/testing/rpc_addenda.md
- docs/templates/planning_skeleton.md → platform/templates/planning_skeleton.md
- docs/templates/pseudocode.md → platform/templates/pseudocode.md
- docs/templates/reasoning_note.md → platform/templates/reasoning_note.md
- docs/templates/spec.md → platform/templates/spec.md
- docs/engineering/conventions.md → platform/engineering/conventions.md
- docs/engineering/ownership.md → platform/engineering/ownership.md
- docs/engineering/pr_review.md → platform/engineering/pr_review.md
- docs/engineering/branching_releases.md → platform/engineering/branching_releases.md
- docs/engineering/module_guardrails.md → platform/engineering/module_guardrails.md
- docs/engineering/composable_system_audit_v1.md → platform/engineering/composable_system_audit_v1.md
- docs/contracts/CHANGELOG.md → platform/engineering/contracts_changelog.md (version log; platform reference)
- docs/engineering/doc_classification_investigation_v1.md → platform/engineering/doc_classification_investigation_v1.md
- docs/engineering/sentry_android_native_symbols.md → platform/engineering/sentry_android_native_symbols.md
- docs/ui/core_ui_primitives.md → platform/engineering/core_ui_primitives_doc.md
- docs/db/chores.md → platform/legacy/db/chores.md
- docs/db/migrations.md → platform/legacy/db/migrations.md
- db/README.md → platform/legacy/db/README.md (deprecated; supabase is source of truth)

## Mixed-item split plan
- Completed: paywall_gate split into product (`paywall_gate_product_v1.md`) and copy (`paywall_gate_copy_v1.md`); legacy combined file remains for reference.
- Completed: share_recurring split into API (`share_recurring_api_v1.md`) and product (`share_recurring_product_v1.md`); legacy combined file remains for reference.
- Future: docs/testing/** — separate platform guardrails (checklists) vs product/domain-specific plans; place domain plans with product bucket, keep guardrails in platform/testing.
- Future: coordination/memory_bank/** — archive or summarize into platform/coordination if still needed; otherwise exclude from contracts export.
## Notes
- Mixed items handled: paywall_gate now split into product vs copy; share_recurring split into API vs product. Bucket F is empty until new mixed files appear.
- Testing/runbooks/agents/engineering guardrails are placed in Platform (Bucket G); revisit if a dedicated platform repo is created.
- No files were moved or edited as part of this mapping.