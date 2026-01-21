---
Domain: Diagrams
Capability: Readme
Scope: platform
Artifact-Type: architecture
Stability: evolving
Status: draft
Version: v1.0
---

# 🏠 Home Membership Domain — Diagrams

This folder documents the logical and data flows that define how a **user joins, manages, and leaves a home** in the system.

---

## 🧭 Overview

The **Home Membership** domain governs everything related to:
- Creating or joining a home.
- Inviting, accepting, or removing members.
- Transferring ownership between users.
- Handling permission logic for each role (owner vs member).
- Enforcing “one active home per user” through membership rules.

It connects closely to the following database tables:
- `homes`
- `membership`
- `invites`
- `users`

Each Mermaid file in this folder visualizes a different part of that lifecycle.

---

## 📘 Diagram Index

| File | Description |
|------|--------------|
| **home_state.md** | High-level state diagram showing transitions between home states (active, inactive, ownership changes). |
| **invite_rotation.md** | Explains how invite links are rotated or revoked once used or expired. |
| **join_flow.md** | Details the process of a user joining a home via an invite code. |
| **kick_member.md** | Describes how an owner removes a member from a home and what database updates occur. |
| **leave_home.md** | Shows how members voluntarily leave a home and how `is_current` flips to `FALSE` (emulating the legacy `left_at` semantics). |
| **ownership_model.md** | ER diagram summarizing relationships between `homes`, `users`, and `membership`. |
| **permissions_flow.md** | Illustrates the logic that enforces permissions (e.g., who can transfer, kick, or invite). |
| **transfer_owner_flow.md** | Flow of transferring ownership from one user to another (checks, errors, success). |
| **transfer_owner_sequence.md** | Sequence diagram for the detailed steps and RPC calls in an ownership transfer. |

---

## 🧩 Business Rules

- A **user can belong to only one active home** (`membership.is_current = TRUE` ensures uniqueness).
- Every **home has exactly one owner** (`homes.owner_id`).
- The **owner must also have an active membership** in the same home.
- Invitations can be **revoked or rotated** automatically after use or expiry.
- Ownership transfers **deactivate** the old owner and **activate** the new one within the same home.
- Permission flows ensure that only owners can:
  - Kick members.
  - Transfer ownership.
  - Manage invites.

---

## 🔗 Related Code Modules

| Area | Flutter Folder |
|------|----------------|
| **Join flow UI** | `lib/features/home_membership/join/ui/` |
| **Leave / Kick** | `lib/features/home_membership/leave/` and `kick_member/` |
| **Ownership / Transfer** | `lib/features/home_membership/transfer_owner/` |
| **Core logic** | `lib/features/home_membership/core/` (shared BLoCs, services, entities) |

---

## 🗒️ Notes
- These diagrams reflect backend logic, not UI navigation.
- Mermaid syntax is compatible with GitHub preview; each `.md` file can be opened directly for visualization.
- Update this index whenever new diagrams are added.

---

_Last updated: {{9/11/2025}}_