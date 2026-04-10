---
Domain: Command
Capability: Voice and Text Command Router
Scope: backend
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.1
Relates-To: contracts/api/kinly/homes/shopping_list_api_v1.md, contracts/api/kinly/share/expenses_v2.md, contracts/api/kinly/chores/chore_wheel_api_v1.md, contracts/api/kinly/homes/house_norms_api_v1.md
See-Also: contracts/product/kinly/shared/shopping_list_contract_v1.md, contracts/product/kinly/mobile/chores_v2.md
---

# Kinly Command Router Contract v1.1

## Purpose

This contract defines the **structured output** produced after a user says or types something into Kinly. It is the **decision-ready draft** that the app and backend act on — not the execution itself.

It answers:

1. What did the user mean? → `intent`
2. Do we have enough info? → `status` / `missing_fields`
3. Is this about creating something new or updating something existing? → `resolution.mode`
4. If it matches an existing thing, how confident are we? → `resolution.match_confidence_band` / `top_candidate_score`
5. What should Kinly do next? → `ui_hint` / `policy`

---

## Architecture Overview

```
User input (voice / text)
        │
        ▼
┌──────────────┐
│  LLM Router  │  → intent + arguments + status
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Resolver    │  → resolution (match existing entities, score candidates)
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  Deterministic Rules │  → ui_hint + policy (execute / inline / confirm / route)
└──────────────────────┘
       │
       ▼
   Command Contract JSON  →  app / backend acts on it
```

The LLM's job is narrow: understand intent and extract arguments. The resolver scores candidates against existing data. The deterministic rules decide the UX outcome. This separation means thresholds can be tuned without re-prompting.

---

## 1. Contract Shape

```json
{
  "contract_version": "1.1",
  "source": { ... },
  "intent": "...",
  "arguments": { ... },
  "status": "...",
  "missing_fields": [],
  "ambiguities": [],
  "risk_level": "...",
  "resolution": { ... },
  "ui_hint": { ... },
  "summary": "...",
  "policy": { ... },
  "audit": { ... }
}
```

---

## 2. `source`

Where the command came from.

| Field              | Type     | Description                              |
|--------------------|----------|------------------------------------------|
| `input_mode`       | string   | `"text"` or `"voice"`                    |
| `raw_text`         | string   | Original typed text (empty for voice)    |
| `transcript_text`  | string?  | Speech-to-text output (null for text)    |
| `user_id`          | string   | `"current_user"`                         |
| `home_id`          | string   | `"current_home"`                         |
| `timezone`         | string   | IANA timezone, e.g. `"Pacific/Auckland"` |
| `client_timestamp` | string   | ISO 8601 with offset                     |

### Allowed `input_mode` values

```json
["text", "voice"]
```

---

## 3. `intent`

The normalized action Kinly thinks the user wants.

### Recommended v1 intents

```json
[
  "add_grocery_item",
  "create_task",
  "mark_task_done",
  "create_reminder",
  "create_expense",
  "open_house_norms",
  "view_due_items",
  "view_service"
]
```

---

## 4. `arguments`

Structured values for the action. Missing values MUST be `null`, never guessed.

### Canonical argument shape

```json
{
  "task_id": null,
  "task_title": null,
  "assigned_to": null,
  "due_at": null,
  "amount": null,
  "currency": null,
  "category": null,
  "participants": null,
  "paid_by": null,
  "target_service": null,
  "note": null,
  "item": null
}
```

Not every field is used every time.

---

## 5. `status`

Whether Kinly has enough information.

| Value            | Meaning                                                 |
|------------------|---------------------------------------------------------|
| `complete`       | Enough info to act                                      |
| `missing_fields` | Intent is clear, but something important is missing     |
| `ambiguous`      | More than one valid interpretation or target exists      |

---

## 6. `missing_fields`

Fields still needed before safe execution.

```json
["assigned_to"]
```

---

## 7. `ambiguities`

Explicit uncertainty markers.

### Allowed values

```json
[
  "intent_unclear",
  "multiple_possible_tasks",
  "split_group_unclear",
  "service_target_unclear",
  "no_existing_task_match"
]
```

---

## 8. `risk_level`

How risky it would be to act wrongly.

| Value    | Examples                                       |
|----------|------------------------------------------------|
| `low`    | Add grocery item, mark task done, open page    |
| `medium` | Reminder creation, lightweight assignment      |
| `high`   | Expenses, splits, service/payment changes      |

---

## 9. `resolution`

The key layer for matching user input to existing entities (tasks, expenses, services).

### Shape

```json
{
  "mode": "matched_existing",
  "entity_type": "task",
  "entity_id": "task_123",
  "match_confidence_band": "high",
  "top_candidate_score": 94,
  "top_candidate_reasons": [
    "assigned_to_current_user",
    "due_today",
    "strong_title_match",
    "recently_active"
  ],
  "candidate_count": 3,
  "requires_user_selection": false,
  "selection_thresholds": {
    "auto_execute_min": 80,
    "confirm_min": 50
  }
}
```

### Allowed `mode`

| Value                 | Meaning                                         |
|-----------------------|-------------------------------------------------|
| `not_applicable`      | No matching needed (e.g. add grocery item)      |
| `matched_existing`    | Found the likely existing item                  |
| `needs_selection`     | User should choose from a few matches           |
| `no_match_create_new` | Nothing matched, offer create-new flow          |
| `route_for_resolution`| Too complex, open the page                      |

### Allowed `entity_type`

```json
["task", "expense", "service", "reminder", "none"]
```

### Allowed `match_confidence_band`

```json
["high", "medium", "low", "none"]
```

### `top_candidate_score` interpretation

| Range  | Meaning          |
|--------|------------------|
| 90+    | Very likely      |
| 50–79  | Maybe, confirm   |
| < 50   | Ask/select/route |

### Allowed `top_candidate_reasons`

```json
[
  "assigned_to_current_user",
  "due_today",
  "due_recently",
  "strong_title_match",
  "weak_title_match",
  "recently_active",
  "recurring_task",
  "last_referenced_entity"
]
```

These reasons support debugging, analytics, trust, and explainability.

---

## 10. `ui_hint`

Tells the app what UI pattern to use next.

### Shape

```json
{
  "type": "inline",
  "component": "assign",
  "target": null,
  "prefill": {
    "task_title": "Wash the clothes"
  },
  "options": [
    { "id": "me", "label": "Me" },
    { "id": "alex", "label": "Alex" }
  ]
}
```

### Allowed `type`

| Value     | Meaning                                              |
|-----------|------------------------------------------------------|
| `execute` | Safe to perform now                                  |
| `inline`  | Show quick buttons/chips/picker                      |
| `confirm` | Show summary and confirm button                      |
| `route`   | Deep link into a page with prefilled draft state     |

### Allowed `component`

```json
[
  null,
  "assign",
  "assign_payer",
  "split",
  "pick_date",
  "disambiguate",
  "select_task",
  "select_service"
]
```

### `target`

Only used when `type = "route"`. Example: `"/expenses/create"`

### `prefill`

Draft values carried into the page or confirmation sheet.

### `options`

Used for inline actions. Example:

```json
[
  { "id": "me", "label": "Me" },
  { "id": "alex", "label": "Alex" },
  { "id": "sam", "label": "Sam" }
]
```

---

## 11. `summary`

Human-readable action summary.

```json
"Split $84 groceries across everyone"
```

---

## 12. `policy`

Suggested outcome from router/resolver. Final decision stays deterministic in app/backend logic.

```json
{
  "suggested_outcome": "confirm",
  "requires_confirmation": true,
  "is_executable_now": true,
  "executor": "expense_create_rpc"
}
```

### Allowed `suggested_outcome`

```json
["execute", "inline", "confirm", "route"]
```

---

## 13. `audit`

Optional metadata for versioning.

```json
{
  "router_version": "voice-command-router-v1",
  "schema_version": "1.1"
}
```

---

## 14. Deterministic Decision Rules

These rules MUST execute outside the LLM, in app/backend logic.

```
IF status == complete
   AND risk_level == low
   AND resolution.match_confidence_band IN [high, none]:
   → execute

IF status == complete
   AND risk_level IN [medium, high]:
   → confirm

IF status == missing_fields
   AND missing_fields.count <= 2:
   → inline

IF status == missing_fields
   AND missing_fields.count > 2:
   → route

IF status == ambiguous
   AND resolution.mode == needs_selection
   AND candidate_count <= 3:
   → inline

IF status == ambiguous
   AND resolution.mode == route_for_resolution:
   → route

IF resolution.mode == no_match_create_new:
   → confirm (create-new or create-and-complete)

IF resolution.mode == matched_existing
   AND top_candidate_score >= auto_execute_min:
   → execute

IF resolution.mode == matched_existing
   AND top_candidate_score >= confirm_min
   AND top_candidate_score < auto_execute_min:
   → confirm

IF resolution.mode == matched_existing
   AND top_candidate_score < confirm_min:
   → inline selection or route
```

---

## 15. Candidate Scoring Logic

This powers the `resolution` block. The contract only exposes the final score and reasons — not the full calculation.

### Suggested weights

| Factor                     | Score |
|----------------------------|-------|
| Assigned to current user   | +40   |
| Due today                  | +30   |
| Due recently               | +20   |
| Strong title match         | +30   |
| Weak title match           | +15   |
| Recently active            | +25   |
| Recurring task             | +10   |
| Last referenced entity     | +20   |

---

## 16. Examples

### A. Simple execute — "milk"

```json
{
  "contract_version": "1.1",
  "source": {
    "input_mode": "text",
    "raw_text": "milk",
    "transcript_text": null,
    "user_id": "current_user",
    "home_id": "current_home",
    "timezone": "Pacific/Auckland",
    "client_timestamp": "2026-04-11T10:15:00+12:00"
  },
  "intent": "add_grocery_item",
  "arguments": {
    "item": "milk",
    "task_id": null,
    "task_title": null,
    "assigned_to": null,
    "due_at": null,
    "amount": null,
    "currency": null,
    "category": null,
    "participants": null,
    "paid_by": null,
    "target_service": null,
    "note": null
  },
  "status": "complete",
  "missing_fields": [],
  "ambiguities": [],
  "risk_level": "low",
  "resolution": {
    "mode": "not_applicable",
    "entity_type": "none",
    "entity_id": null,
    "match_confidence_band": "none",
    "top_candidate_score": null,
    "top_candidate_reasons": [],
    "candidate_count": 0,
    "requires_user_selection": false,
    "selection_thresholds": {
      "auto_execute_min": 80,
      "confirm_min": 50
    }
  },
  "ui_hint": {
    "type": "execute",
    "component": null,
    "target": null,
    "prefill": null,
    "options": []
  },
  "summary": "Add milk to grocery list",
  "policy": {
    "suggested_outcome": "execute",
    "requires_confirmation": false,
    "is_executable_now": true,
    "executor": "shopping_list_add_item_rpc"
  },
  "audit": {
    "router_version": "voice-command-router-v1",
    "schema_version": "1.1"
  }
}
```

### B. Inline assign — "wash the clothes"

```json
{
  "contract_version": "1.1",
  "source": {
    "input_mode": "text",
    "raw_text": "wash the clothes",
    "transcript_text": null,
    "user_id": "current_user",
    "home_id": "current_home",
    "timezone": "Pacific/Auckland",
    "client_timestamp": "2026-04-11T10:15:00+12:00"
  },
  "intent": "create_task",
  "arguments": {
    "task_id": null,
    "task_title": "Wash the clothes",
    "assigned_to": null,
    "due_at": null,
    "amount": null,
    "currency": null,
    "category": null,
    "participants": null,
    "paid_by": null,
    "target_service": null,
    "note": null,
    "item": null
  },
  "status": "missing_fields",
  "missing_fields": ["assigned_to"],
  "ambiguities": [],
  "risk_level": "low",
  "resolution": {
    "mode": "not_applicable",
    "entity_type": "none",
    "entity_id": null,
    "match_confidence_band": "none",
    "top_candidate_score": null,
    "top_candidate_reasons": [],
    "candidate_count": 0,
    "requires_user_selection": false,
    "selection_thresholds": {
      "auto_execute_min": 80,
      "confirm_min": 50
    }
  },
  "ui_hint": {
    "type": "inline",
    "component": "assign",
    "target": null,
    "prefill": {
      "task_title": "Wash the clothes"
    },
    "options": [
      { "id": "me", "label": "Me" },
      { "id": "alex", "label": "Alex" },
      { "id": "sam", "label": "Sam" }
    ]
  },
  "summary": "Create task: Wash the clothes",
  "policy": {
    "suggested_outcome": "inline",
    "requires_confirmation": false,
    "is_executable_now": false,
    "executor": "task_create_rpc"
  },
  "audit": {
    "router_version": "voice-command-router-v1",
    "schema_version": "1.1"
  }
}
```

### C. High-risk confirm — "groceries 84 split all"

```json
{
  "contract_version": "1.1",
  "source": {
    "input_mode": "voice",
    "raw_text": "",
    "transcript_text": "groceries 84 split all",
    "user_id": "current_user",
    "home_id": "current_home",
    "timezone": "Pacific/Auckland",
    "client_timestamp": "2026-04-11T10:15:00+12:00"
  },
  "intent": "create_expense",
  "arguments": {
    "task_id": null,
    "task_title": null,
    "assigned_to": null,
    "due_at": null,
    "amount": 84,
    "currency": "NZD",
    "category": "groceries",
    "participants": ["everyone"],
    "paid_by": "current_user",
    "target_service": null,
    "note": null,
    "item": null
  },
  "status": "complete",
  "missing_fields": [],
  "ambiguities": [],
  "risk_level": "high",
  "resolution": {
    "mode": "not_applicable",
    "entity_type": "none",
    "entity_id": null,
    "match_confidence_band": "none",
    "top_candidate_score": null,
    "top_candidate_reasons": [],
    "candidate_count": 0,
    "requires_user_selection": false,
    "selection_thresholds": {
      "auto_execute_min": 80,
      "confirm_min": 50
    }
  },
  "ui_hint": {
    "type": "confirm",
    "component": null,
    "target": null,
    "prefill": {
      "amount": 84,
      "currency": "NZD",
      "category": "groceries",
      "participants": ["everyone"],
      "paid_by": "current_user"
    },
    "options": []
  },
  "summary": "Split $84 groceries across everyone",
  "policy": {
    "suggested_outcome": "confirm",
    "requires_confirmation": true,
    "is_executable_now": true,
    "executor": "expense_create_rpc"
  },
  "audit": {
    "router_version": "voice-command-router-v1",
    "schema_version": "1.1"
  }
}
```

### D. Direct route — "house norms"

```json
{
  "contract_version": "1.1",
  "source": {
    "input_mode": "text",
    "raw_text": "house norms",
    "transcript_text": null,
    "user_id": "current_user",
    "home_id": "current_home",
    "timezone": "Pacific/Auckland",
    "client_timestamp": "2026-04-11T10:15:00+12:00"
  },
  "intent": "open_house_norms",
  "arguments": {
    "task_id": null,
    "task_title": null,
    "assigned_to": null,
    "due_at": null,
    "amount": null,
    "currency": null,
    "category": null,
    "participants": null,
    "paid_by": null,
    "target_service": null,
    "note": null,
    "item": null
  },
  "status": "complete",
  "missing_fields": [],
  "ambiguities": [],
  "risk_level": "low",
  "resolution": {
    "mode": "not_applicable",
    "entity_type": "none",
    "entity_id": null,
    "match_confidence_band": "none",
    "top_candidate_score": null,
    "top_candidate_reasons": [],
    "candidate_count": 0,
    "requires_user_selection": false,
    "selection_thresholds": {
      "auto_execute_min": 80,
      "confirm_min": 50
    }
  },
  "ui_hint": {
    "type": "route",
    "component": null,
    "target": "/house-norms",
    "prefill": null,
    "options": []
  },
  "summary": "Open house norms",
  "policy": {
    "suggested_outcome": "route",
    "requires_confirmation": false,
    "is_executable_now": false,
    "executor": "none"
  },
  "audit": {
    "router_version": "voice-command-router-v1",
    "schema_version": "1.1"
  }
}
```

### E. Matched existing (high confidence) — "washing completed"

```json
{
  "contract_version": "1.1",
  "source": {
    "input_mode": "voice",
    "raw_text": "",
    "transcript_text": "washing completed",
    "user_id": "current_user",
    "home_id": "current_home",
    "timezone": "Pacific/Auckland",
    "client_timestamp": "2026-04-11T10:15:00+12:00"
  },
  "intent": "mark_task_done",
  "arguments": {
    "task_id": "task_123",
    "task_title": "Wash clothes",
    "assigned_to": "current_user",
    "due_at": "2026-04-11T18:00:00+12:00",
    "amount": null,
    "currency": null,
    "category": null,
    "participants": null,
    "paid_by": null,
    "target_service": null,
    "note": null,
    "item": null
  },
  "status": "complete",
  "missing_fields": [],
  "ambiguities": [],
  "risk_level": "low",
  "resolution": {
    "mode": "matched_existing",
    "entity_type": "task",
    "entity_id": "task_123",
    "match_confidence_band": "high",
    "top_candidate_score": 94,
    "top_candidate_reasons": [
      "assigned_to_current_user",
      "due_today",
      "strong_title_match",
      "recently_active"
    ],
    "candidate_count": 3,
    "requires_user_selection": false,
    "selection_thresholds": {
      "auto_execute_min": 80,
      "confirm_min": 50
    }
  },
  "ui_hint": {
    "type": "execute",
    "component": null,
    "target": null,
    "prefill": null,
    "options": []
  },
  "summary": "Mark task 'Wash clothes' as completed",
  "policy": {
    "suggested_outcome": "execute",
    "requires_confirmation": false,
    "is_executable_now": true,
    "executor": "task_completion_rpc"
  },
  "audit": {
    "router_version": "voice-command-router-v1",
    "schema_version": "1.1"
  }
}
```

### F. Medium-confidence match — confirm

```json
{
  "contract_version": "1.1",
  "source": {
    "input_mode": "voice",
    "raw_text": "",
    "transcript_text": "washing completed",
    "user_id": "current_user",
    "home_id": "current_home",
    "timezone": "Pacific/Auckland",
    "client_timestamp": "2026-04-11T10:15:00+12:00"
  },
  "intent": "mark_task_done",
  "arguments": {
    "task_id": "task_456",
    "task_title": "Wash towels",
    "assigned_to": "current_user",
    "due_at": "2026-04-10T18:00:00+12:00",
    "amount": null,
    "currency": null,
    "category": null,
    "participants": null,
    "paid_by": null,
    "target_service": null,
    "note": null,
    "item": null
  },
  "status": "ambiguous",
  "missing_fields": [],
  "ambiguities": ["multiple_possible_tasks"],
  "risk_level": "low",
  "resolution": {
    "mode": "matched_existing",
    "entity_type": "task",
    "entity_id": "task_456",
    "match_confidence_band": "medium",
    "top_candidate_score": 64,
    "top_candidate_reasons": [
      "assigned_to_current_user",
      "due_recently",
      "weak_title_match"
    ],
    "candidate_count": 2,
    "requires_user_selection": false,
    "selection_thresholds": {
      "auto_execute_min": 80,
      "confirm_min": 50
    }
  },
  "ui_hint": {
    "type": "confirm",
    "component": null,
    "target": null,
    "prefill": {
      "task_id": "task_456"
    },
    "options": []
  },
  "summary": "Mark task 'Wash towels' as completed?",
  "policy": {
    "suggested_outcome": "confirm",
    "requires_confirmation": true,
    "is_executable_now": true,
    "executor": "task_completion_rpc"
  },
  "audit": {
    "router_version": "voice-command-router-v1",
    "schema_version": "1.1"
  }
}
```

### G. Low-confidence match — inline selection

```json
{
  "contract_version": "1.1",
  "source": {
    "input_mode": "voice",
    "raw_text": "",
    "transcript_text": "washing completed",
    "user_id": "current_user",
    "home_id": "current_home",
    "timezone": "Pacific/Auckland",
    "client_timestamp": "2026-04-11T10:15:00+12:00"
  },
  "intent": "mark_task_done",
  "arguments": {
    "task_id": null,
    "task_title": "washing",
    "assigned_to": null,
    "due_at": null,
    "amount": null,
    "currency": null,
    "category": null,
    "participants": null,
    "paid_by": null,
    "target_service": null,
    "note": null,
    "item": null
  },
  "status": "ambiguous",
  "missing_fields": ["task_id"],
  "ambiguities": ["multiple_possible_tasks"],
  "risk_level": "low",
  "resolution": {
    "mode": "needs_selection",
    "entity_type": "task",
    "entity_id": null,
    "match_confidence_band": "low",
    "top_candidate_score": 42,
    "top_candidate_reasons": [
      "multiple_weak_matches"
    ],
    "candidate_count": 3,
    "requires_user_selection": true,
    "selection_thresholds": {
      "auto_execute_min": 80,
      "confirm_min": 50
    }
  },
  "ui_hint": {
    "type": "inline",
    "component": "select_task",
    "target": null,
    "prefill": null,
    "options": [
      { "id": "task_123", "label": "Wash clothes" },
      { "id": "task_456", "label": "Wash towels" },
      { "id": "task_789", "label": "Wash sheets" }
    ]
  },
  "summary": "Which task did you complete?",
  "policy": {
    "suggested_outcome": "inline",
    "requires_confirmation": false,
    "is_executable_now": false,
    "executor": "task_completion_rpc"
  },
  "audit": {
    "router_version": "voice-command-router-v1",
    "schema_version": "1.1"
  }
}
```

### H. No match — confirm create-and-complete

```json
{
  "contract_version": "1.1",
  "source": {
    "input_mode": "voice",
    "raw_text": "",
    "transcript_text": "washing completed",
    "user_id": "current_user",
    "home_id": "current_home",
    "timezone": "Pacific/Auckland",
    "client_timestamp": "2026-04-11T10:15:00+12:00"
  },
  "intent": "mark_task_done",
  "arguments": {
    "task_id": null,
    "task_title": "Washing",
    "assigned_to": null,
    "due_at": null,
    "amount": null,
    "currency": null,
    "category": null,
    "participants": null,
    "paid_by": null,
    "target_service": null,
    "note": null,
    "item": null
  },
  "status": "ambiguous",
  "missing_fields": ["task_id"],
  "ambiguities": ["no_existing_task_match"],
  "risk_level": "low",
  "resolution": {
    "mode": "no_match_create_new",
    "entity_type": "task",
    "entity_id": null,
    "match_confidence_band": "none",
    "top_candidate_score": 0,
    "top_candidate_reasons": [],
    "candidate_count": 0,
    "requires_user_selection": false,
    "selection_thresholds": {
      "auto_execute_min": 80,
      "confirm_min": 50
    }
  },
  "ui_hint": {
    "type": "confirm",
    "component": null,
    "target": null,
    "prefill": {
      "task_title": "Washing",
      "mark_completed": true
    },
    "options": []
  },
  "summary": "No matching task found. Create 'Washing' and mark it completed?",
  "policy": {
    "suggested_outcome": "confirm",
    "requires_confirmation": true,
    "is_executable_now": false,
    "executor": "task_create_and_complete_rpc"
  },
  "audit": {
    "router_version": "voice-command-router-v1",
    "schema_version": "1.1"
  }
}
```

---

## 17. Design Principles

1. **The contract is not execution** — it is the decision-ready draft that the app/backend acts on.
2. **LLM scope is narrow** — understand intent + extract arguments. No matching, no UX decisions.
3. **Resolution is separate** — candidate scoring happens in the resolver, using real data.
4. **Final UX decision is deterministic** — threshold-based rules, tunable without re-prompting.
5. **Missing values are null, never guessed** — the contract is honest about what it doesn't know.
6. **Resolution block is optional** — only included when existing-item matching matters.
