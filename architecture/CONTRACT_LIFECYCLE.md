---
Domain: platform
Capability: contracts
Scope: platform
Artifact-Type: process
Stability: stable
Status: active
Version: v1.0
---

# Contract Lifecycle

This document formalises how **contracts** are authored, validated, promoted, and consumed across the Kinly ecosystem.

It exists to prevent accidental coupling, unclear ownership, and CI automation overreach.

---

## Core Principle

> **Backend is the authority of truth.**
> **kinly-contracts is the authority of record.**

* The backend *proves* what exists and what runs.
* The contracts repository *declares* what is agreed, stable, and consumable.

These two roles must remain distinct.

---

## Two Types of Contracts (Critical Distinction)

Kinly uses the word *contract* for two very different artifacts. They must never be treated the same.

### 1. Human‑Authored Contracts (Design & Intent)

**What they are**

* Markdown documents describing product behaviour, API intent, rules, invariants, and expectations
* Versioned intentionally (e.g. `homes_v1.md`, `chores_v2.md`)

**Examples**

* Product flows
* Domain rules
* API semantics
* Behavioural guarantees

**Properties**

* Written and reviewed by humans
* Carry meaning, rationale, and constraints
* Not always immediately implementable

These are **specifications**, not build artifacts.

---

### 2. Machine‑Generated Contracts (Execution Snapshots)

**What they are**

* Generated outputs derived from the backend reality

**Examples**

* `openapi.json`
* `types.generated.ts`
* `schema.sql`
* `rls_policies.sql`
* `edge_functions.json`
* `registry.json`
* `registry.schema.json`

**Properties**

* Fully regenerable
* Deterministic
* Source of truth for execution and integration

These are **snapshots**, not specifications.

---

## Authoritative Ownership

| Artifact Type                                   | Primary Owner | Publication Mode    |
| ----------------------------------------------- | ------------- | ------------------- |
| Human contracts (`*.md`)                        | Humans        | Manual, intentional |
| Generated snapshots (`*.json`, `*.sql`, `*.ts`) | CI            | Automatic, enforced |

---

## Human‑Authored Contract Lifecycle

### Step 1 — Authoring (Backend‑First)

Human contracts are **written first in `kinly-backend`**:

```
kinly-backend/docs/contracts/
```

**Why backend‑first?**

* Keeps intent close to feasibility
* Allows rapid iteration with real constraints
* Avoids speculative contracts detached from implementation

---

### Step 2 — Review & Approval

* Contracts are reviewed via PR in `kinly-backend`
* Discussion focuses on:

  * semantics
  * breaking change impact
  * versioning correctness

No automation publishes these contracts.

---

### Step 3 — Promotion to kinly‑contracts (Manual)

Once approved, the contract is **manually promoted** to:

```
kinly-contracts/contracts/api/kinly/<domain>/
```

**Rules**

* Preserve filename and version
* Promotion is an explicit decision
* This is a publication act, not a sync

Optional staging may be done via:

```
kinly-contracts/_incoming/kinly/
```

---

## Machine‑Generated Contract Lifecycle

### Step 1 — Generation (Backend Only)

Generated exclusively in `kinly-backend` via:

```
./tool/contracts_regen.sh
```

These artifacts must never be hand‑edited.

---

### Step 2 — Validation (CI Gate)

Backend CI enforces:

* registry structural validity
* snapshot completeness
* no uncommitted drift

Failures block the pipeline.

---

### Step 3 — Publication (Automatic)

On successful CI run, snapshots are **automatically published** to:

```
kinly-contracts/contracts/api/kinly_backend/
```

This step is fully automated and deterministic.

---

## Folder Responsibility Map

```
kinly-contracts/
├─ contracts/
│  ├─ api/
│  │  ├─ kinly/           # Human‑authored contracts (manual)
│  │  └─ kinly_backend/   # Generated snapshots (CI‑only)
```

**Hard rule**

* CI may only write to `kinly_backend/`
* Humans may only write to `kinly/`

---

## Explicit Anti‑Patterns (Do Not Do These)

❌ Auto‑sync Markdown contracts via CI
❌ Allow CI to modify `contracts/api/kinly/`
❌ Treat human contracts as build outputs
❌ Edit generated snapshots by hand

These break trust, intent, and version discipline.

---

## Why This Matters

This lifecycle ensures:

* clear ownership boundaries
* stable frontend consumption
* backend‑led truth
* intentional API evolution
* auditable change history

Most importantly, it prevents accidental coupling between **design intent** and **implementation state**.

---

## Summary Rule (Memorise This)

> **Humans publish meaning.**
> **CI publishes reality.**

When in doubt, choose the slower, explicit path.
