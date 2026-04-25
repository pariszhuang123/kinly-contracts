# Kinly Living Wiki

This wiki is generated from canonical docs in `contracts/**`, `architecture/**`, `decisions/**`, and `platform/**`.

## Snapshot

- Canonical docs: 274
- Domains: 45
- Capability pages: 227
- Active docs: 64
- Draft docs: 210
- Deprecated docs: 0
- Alignment issues: 0

## Read First

- Alignment report: [[reports/alignment_report|Alignment Report]]
- Change digest: [[reports/change_digest|Change Digest]]

## Domains

- [[domains/adr_0001_mvp_home_scope_md|adr_0001_mvp_home_scope_md]] (1 docs, 0 active)
- [[domains/adr_0001_user_auth_and_account_lifecycle_md|adr_0001_user_auth_and_account_lifecycle_md]] (1 docs, 0 active)
- [[domains/adr_0002_invites_permanent_codes_md|adr_0002_invites_permanent_codes_md]] (1 docs, 0 active)
- [[domains/adr_0003_expenses_rpc_only_access_md|adr_0003_expenses_rpc_only_access_md]] (1 docs, 0 active)
- [[domains/agents|agents]] (10 docs, 0 active)
- [[domains/architecture_guardrails_v1_1_md|architecture_guardrails_v1_1_md]] (1 docs, 0 active)
- [[domains/backend|backend]] (1 docs, 1 active)
- [[domains/command|command]] (11 docs, 0 active)
- [[domains/complexity_budget_v1_md|complexity_budget_v1_md]] (1 docs, 0 active)
- [[domains/contracts|contracts]] (2 docs, 0 active)
- [[domains/coordination|coordination]] (10 docs, 0 active)
- [[domains/core_placement_rules_v1_md|core_placement_rules_v1_md]] (1 docs, 0 active)
- [[domains/delivery|delivery]] (1 docs, 0 active)
- [[domains/deployment|deployment]] (1 docs, 0 active)
- [[domains/design|design]] (1 docs, 0 active)
- [[domains/design_system|design_system]] (1 docs, 0 active)
- [[domains/di_graph_md|di_graph_md]] (1 docs, 0 active)
- [[domains/diagrams|diagrams]] (20 docs, 0 active)
- [[domains/engineering|engineering]] (16 docs, 0 active)
- [[domains/flows|flows]] (9 docs, 0 active)
- [[domains/forms|forms]] (1 docs, 0 active)
- [[domains/growth|growth]] (5 docs, 4 active)
- [[domains/homes|homes]] (24 docs, 2 active)
- [[domains/identity|identity]] (5 docs, 0 active)
- [[domains/kinly|kinly]] (16 docs, 0 active)
- [[domains/kinly_web|kinly_web]] (1 docs, 1 active)
- [[domains/links|links]] (18 docs, 17 active)
- [[domains/marketing_ops|marketing_ops]] (1 docs, 0 active)
- [[domains/mobile|mobile]] (5 docs, 0 active)
- [[domains/modules_md|modules_md]] (1 docs, 0 active)
- [[domains/monetization|monetization]] (5 docs, 2 active)
- [[domains/norms|norms]] (1 docs, 0 active)
- [[domains/platform|platform]] (3 docs, 2 active)
- [[domains/product|product]] (37 docs, 32 active)
- [[domains/repo_migration_contract_v1_md|repo_migration_contract_v1_md]] (1 docs, 0 active)
- [[domains/report_md|report_md]] (1 docs, 0 active)
- [[domains/runbooks|runbooks]] (3 docs, 0 active)
- [[domains/share|share]] (3 docs, 0 active)
- [[domains/shared|shared]] (31 docs, 0 active)
- [[domains/templates|templates]] (4 docs, 0 active)
- [[domains/testing|testing]] (6 docs, 0 active)
- [[domains/theme|theme]] (1 docs, 1 active)
- [[domains/web_design_system|web_design_system]] (1 docs, 1 active)
- [[domains/web_ui|web_ui]] (1 docs, 1 active)
- [[domains/withyou|withyou]] (8 docs, 0 active)

## Recently Changed Areas

- 2026-04-25: Shopping List Architecture Contract v1.3 -> [[capabilities/shopping_list_contract|shopping_list_contract]] (architecture/contracts/shopping_list_contract.md)
- 2026-04-25: Kinly Command AI Pipeline Contract v1.0 -> [[capabilities/command_ai_pipeline_v1|command_ai_pipeline_v1]] (contracts/api/kinly/command/command_ai_pipeline_v1.md)
- 2026-04-25: Command AI Quota Contract v1.0 -> [[capabilities/command_ai_quota|command_ai_quota]] (contracts/api/kinly/command/command_ai_quota_v1.md)
- 2026-04-25: Command Entry API v1.0 -> [[capabilities/command_entry_api|command_entry_api]] (contracts/api/kinly/command/command_entry_api_v1.md)
- 2026-04-25: Command Expense Module Contract v1.0 -> [[capabilities/command_expense_module|command_expense_module]] (contracts/api/kinly/command/command_expense_module_v1.md)
- 2026-04-25: Kinly Command Router Contract v1.1 -> [[capabilities/command_router_contract|command_router_contract]] (contracts/api/kinly/command/command_router_contract_v1_1.md)
- 2026-04-25: Command Task Module Contract v1.0 -> [[capabilities/command_task_module|command_task_module]] (contracts/api/kinly/command/command_task_module_v1.md)
- 2026-04-25: Voice Command Capture v1.0 -> [[capabilities/voice_command_capture|voice_command_capture]] (contracts/api/kinly/command/voice_command_capture_v1.md)
- 2026-04-25: Home Units API Contract v1.4 -> [[capabilities/home_units_api|home_units_api]] (contracts/api/kinly/homes/home_units_api_v1.md)
- 2026-04-25: paywall_status_get RPC v1.0 -> [[capabilities/paywall_status_get|paywall_status_get]] (contracts/api/kinly/homes/paywall_status_get_v1.md)
- 2026-04-25: Shopping List API Contract v1.8 -> [[capabilities/shopping_list_api|shopping_list_api]] (contracts/api/kinly/homes/shopping_list_api_v1.md)
- 2026-04-25: Paywall Gate Copy Contract (Client) -> [[capabilities/paywall_gate_copy|paywall_gate_copy]] (contracts/design/copy/kinly/paywall_gate_copy_v1.md)

## Key Architecture And Decision Docs

- [architecture_guardrails_amendment_foundation_surfaces_v1](../architecture/architecture_guardrails_amendment_foundation_surfaces_v1.md)
- [Architecture Guardrails Contract v1.1 (Kinly)](../architecture/architecture_guardrails_v1_1.md)
- [Complexity Budget Contract (v1)](../architecture/complexity_budget_v1.md)
- [Contract Lifecycle](../architecture/CONTRACT_LIFECYCLE.md)
- [business_map](../architecture/contracts/business_map.md)
- [Business Map Contract (v1)](../architecture/contracts/business_map_contract.md)
- [Shopping List Architecture Contract v1.3](../architecture/contracts/shopping_list_contract.md)
- [core_placement_rules_v1](../architecture/core_placement_rules_v1.md)
- [di_graph](../architecture/di_graph.md)
- [chore_flow](../architecture/diagrams/chores/chore_flow.md)
- [expense_lifecycle](../architecture/diagrams/expenses/expense_lifecycle.md)
- [home_state](../architecture/diagrams/home_membership/home_state.md)
- [invite_rotation](../architecture/diagrams/home_membership/invite_rotation.md)
- [join_flow](../architecture/diagrams/home_membership/join_flow.md)
- [kick_member](../architecture/diagrams/home_membership/kick_member.md)
- [leave_home](../architecture/diagrams/home_membership/leave_home.md)
- [ownership_model](../architecture/diagrams/home_membership/ownership_model.md)
- [permissions_flow](../architecture/diagrams/home_membership/permissions_flow.md)
- [🏠 Home Membership Domain — Diagrams](../architecture/diagrams/home_membership/README.md)
- [transfer_owner_flow](../architecture/diagrams/home_membership/transfer_owner_flow.md)
- [transfer_owner_sequence](../architecture/diagrams/home_membership/transfer_owner_sequence.md)
- [Kinly Links — End-to-End Invite Flow Diagram (Store-First)](../architecture/diagrams/links/invite_link_e2e_flow.md)
- [Mood & NPS ER View](../architecture/diagrams/mood_nps/mood_nps_er.md)
- [Mood & NPS Flow](../architecture/diagrams/mood_nps/mood_nps_flow.md)
- [Daily Notifications - Phase 1 (Sequence)](../architecture/diagrams/notifications/daily_notifications_phase1.md)
- [Diagrams — Mermaid Quick Guide](../architecture/diagrams/README.md)
- [account_deletion](../architecture/diagrams/user/account_deletion.md)
- [auth_providers](../architecture/diagrams/user/auth_providers.md)
- [avatar_uniqueness](../architecture/diagrams/user/avatar_uniqueness.md)
- [logout](../architecture/diagrams/user/logout.md)
- [Flow — Invite Rotation (Revoke and Reissue)](../architecture/flows/home_membership/invite_rotation.md)
- [Flow — Join Home (Pseudocode)](../architecture/flows/home_membership/join.md)
- [Flow — Kick Member](../architecture/flows/home_membership/kick_member.md)
- [Flow — Leave Home](../architecture/flows/home_membership/leave_home.md)
- [Flow — Transfer Owner](../architecture/flows/home_membership/transfer_owner.md)
- [Flow — Account Deletion (Admin-Approved)](../architecture/flows/user/account_deletion.md)
- [Flow — User Auth (Google/Apple)](../architecture/flows/user/auth.md)
- [Flow — Per-Home Unique Avatars](../architecture/flows/user/avatars.md)
- [Flow — Logout](../architecture/flows/user/logout.md)
- [modules](../architecture/modules.md)
- [Repo Migration Contract v1](../architecture/repo_migration_contract_v1.md)
- [Architecture Report](../architecture/report.md)
- [withYou System Overview (v1)](../architecture/withyou_system_overview_v1.md)
- [ADR-0001: Home-only MVP Scope and Guardrails](../decisions/ADR-0001-mvp-home-scope.md)
- [ADR-0001: User Auth (OAuth-only) and Account Lifecycle](../decisions/ADR-0001-user-auth-and-account-lifecycle.md)
- [ADR-0002: Permanent Invites (Until Revoked)](../decisions/ADR-0002-invites-permanent-codes.md)
- [ADR-0003: Expenses RPC-Only Access Guardrail](../decisions/ADR-0003-expenses-rpc-only-access.md)
- [ADR-0004: Host Links Service on Vercel](../decisions/ADR-0004-links-service-on-vercel.md)
- [ADR-0005: House Rules v1 Owner Authority (No Member Deny, No App Gating)](../decisions/ADR-0005-house-rules-owner-authority-v1.md)
- [ADR-0006: Flatmate Fit Check — Web Auth + Freemium Gate](../decisions/ADR-0006-flatmate-fit-check-web-auth-freemium-gate.md)
