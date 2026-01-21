---
Domain: Contracts
Capability: Business Map Contract
Scope: platform
Artifact-Type: architecture
Stability: evolving
Status: draft
Version: v1.0
---

# Business Map Contract (v1)

- **Status**: Active
- **Owner**: Architecture / Product
- **Applies to**: Humans, Codex, Antigravity, CI
- **Last updated**: 2026-01-09

## 1. Purpose

This contract defines how Kinly’s **Business Map** is:

1. Generated from the dependency graph (`di_graph.md`)
2. Kept strictly in sync with automated generation (`generate.py`)
3. Enforced as part of `check_all.dart`
4. Used by Antigravity / Codex as the primary business understanding artifact

The Business Map is **not hand-edited**. It is derived, validated, and enforced.

## 2. Definitions

### 2.1 `di_graph.md` (Source of Truth)

- A Mermaid graph representing compile-time module dependencies.
- Generated automatically from the codebase.
- Canonical truth for "what depends on what".
- **If `di_graph.md` is wrong, everything else is wrong.**

### 2.2 Business Map

- A business-capability–grouped Mermaid diagram.
- Re-groups existing modules by "project intent" (what problem they solve), not
  by folder.
- Generated from:
  - `di_graph.md` (structure)
  - `business_capabilities_map.yml` (classification)

### 2.3 `business_capabilities_map.yml`

- A small, human-maintained classification file mapping:
  - `module` → `business capability bucket`
- This file encodes **intent**, not dependencies.
- **Example buckets**:
  - `IDENTITY`
  - `HOME`
  - `FLOW`
  - `SHARE`
  - `MONETIZATION`
  - `ONBOARDING`
  - `SURFACES`
  - `CORE`
  - `CONTRACTS`

## 3. Source-of-Truth Rules

### Rule 1 — Dependency truth

- `di_graph.md` is the only source of dependency truth.
- Business Map must be generated from it.
- No dependency may appear in the Business Map that does not exist in
  `di_graph.md`.

### Rule 2 — Classification truth

- `business_capabilities_map.yml` is the only place where Business capability
  groupings are defined.
- It must not encode dependencies.
- It must not encode behavior.

### Rule 3 — No manual edits

- `business_map.md` is generated.
- Manual edits are forbidden.
- Any diff must come from:
  1. Code changes
  2. `di_graph` regeneration
  3. YAML classification updates

## 4. Generation Contract

### 4.1 Inputs

The Business Map generator MUST read:

- `di_graph.md` (or the canonical graph data structure)
- `contracts/architecture/business_capabilities_map.yml`

### 4.2 Output

The generator MUST produce:

- `contracts/architecture/business_map.md`

The output MUST:

- Preserve all nodes
- Preserve all edges
- Group nodes into business capability subgraphs
- Emit a header:
  ```
  %% Auto-generated from di_graph.md
  %% Do not edit manually
  %% Edit business_capabilities_map.yml instead
  ```

### 4.3 Drift Detection

If any module node in `di_graph.md` is not mapped in
`business_capabilities_map.yml`, generation MUST:

1. List unmapped nodes in comments/console.
2. Exit with non-zero status. **This is intentional friction.**

## 5. CI / `check_all.dart` Enforcement

### 5.1 Required Steps in `check_all.dart`

`check_all.dart` MUST execute the following in order:

1. Generate `di_graph`
2. Generate Business Map
3. Fail if unmapped nodes exist
4. Fail if generated files differ from committed files

### 5.2 Failure Semantics

CI MUST fail if:

- A new module appears without a business classification.
- The Business Map is out of sync with `di_graph`.
- A developer updates code but forgets to update classification. **This ensures
  business understanding never silently drifts.**

## 6. Antigravity / Codex Guidance Contract

### 6.1 Mandatory Reading Order for Agents

When an agent starts work on Kinly, it MUST:

1. Read `contracts/architecture/business_map.mmd`
2. Identify the business capability bucket involved
3. Read all related `/contracts/*` in that bucket
4. Only then inspect `/features/*` and `/core/*`

### 6.2 Interpretation Rules for Agents

Agents MUST interpret the map as follows:

- **Subgraph** = business capability
- **Contracts** = business meaning
- **Features** = UI + behavior implementing meaning
- **Core** = reusable capabilities
- **App** = composition only
- **Foundation surfaces** = rendering & registry, not policy

Agents MUST NOT:

- Infer business rules from dependencies alone.
- Add business logic to `core` or `foundation`.
- Change business meaning without updating contracts.

### 6.3 Required Agent Output

When asked to “understand” a feature, Antigravity MUST produce: For each
capability:

- What problem it solves (1–2 sentences)
- Primary contracts involved
- Feature entry points
- Cross-cutting concerns (paywall, notifications, time)

This output MUST reference:

- Business Map bucket name
- Contract file paths

## 7. Change Policy

**Allowed changes**:

- Adding a new business capability bucket
- Reclassifying modules as business understanding evolves
- Splitting or merging capabilities

**Disallowed changes**:

- Editing generated Business Map directly
- Encoding behavior in the classification YAML
- Allowing unmapped modules

## 8. Summary

The dependency graph explains **how** the system is wired. The business map
explains **why** the system exists. This contract ensures they never disagree.