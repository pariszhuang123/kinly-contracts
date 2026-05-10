---
Domain: Portfolio
Capability: Contractor negotiation playbook
Scope: frontend
Artifact-Type: contract
Stability: evolving
Status: active
Version: v1.0
---

# Contract - Contractor Negotiation Playbook Prototype - v1.0

Registry: `contracts/contracts_registry.md`

---

## Purpose

This contract defines a private-use portfolio prototype at:

`/portfolio/contractor-negotiation-playbook`

The prototype exists to help a contractor navigate a live commercial discussion
with a CEO or senior decision-maker.

It must support:

- fast retrieval of likely executive questions
- short, speakable answer prompts
- option-based commercial framing
- scope and pricing trade-off guidance
- private-use reminders that protect the contractor from accidental overcommitment

---

## Canonical User

The canonical user is the contractor running the discussion.

The page is optimized for:

- rapid scanning during a live meeting
- professional spoken delivery
- commercial structure guidance under pressure

The page is not optimized for:

- external stakeholder self-service
- detailed technical review
- proposal replacement

---

## Core Outcome

The prototype must help move the conversation from:

- "Can everything be done immediately and cheaply?"

toward:

- "Which structure creates the best value with the right balance of certainty
  and flexibility?"

The prototype must reinforce "yes, with structure" rather than blunt refusal.

---

## Required Route Behavior

The canonical public route is:

`/portfolio/contractor-negotiation-playbook`

The route must:

- render as a single human-readable page
- remain safe to open in any browser context
- support direct section jumping through normal anchor links
- remain usable on desktop and mobile

The route must not:

- require authentication
- depend on backend persistence
- auto-redirect to any other route
- expose hardcoded private numbers such as walk-away thresholds

Because the page is intended for private contractor use, it should be treated as
non-indexable by search engines.

---

## Required Information Architecture

The page must contain the following sections:

### 1. Meeting Control

A high-visibility summary showing:

- preferred structure
- fallback structure
- current CEO concern
- repeatable steering line

### 2. CEO Questions

A section containing likely CEO questions.

Each question card must contain:

- the question
- what the question likely means commercially
- a short answer
- a standard answer
- an optional expanded explanation
- a redirect question

### 3. Structure Options

The page must present exactly three primary structure options:

- Fixed Phase 1 + Scoped Expansion
- Hybrid 3-Month Engagement
- Embedded 3-Month Model

Each option must include:

- when to use it
- why the CEO may like it
- contractor risk
- recommended framing

### 4. Commercial Levers

A section listing acceptable negotiation levers such as:

- narrowing first scope
- reducing first-phase domain count
- lowering drill-through depth
- staging rollout
- changing contract structure

### 5. Private Guardrails

A private-use prompt section listing items the contractor must define before the
meeting.

Examples:

- hourly or day-rate floor
- preferred monthly structure
- workload ceiling
- repricing triggers
- red flags

The page may prompt for these items, but must not ship with hardcoded sensitive
values.

### 6. Close Scripts

A section containing concise closing lines for:

- certainty-led discussions
- flexibility-led discussions
- budget-led discussions

---

## Content Rules

All copy must:

- sound commercially calm and professional
- remain concise enough for spoken delivery
- avoid defensive tone
- avoid blunt refusal framing
- prefer option-based language

All copy must avoid:

- overpromising certainty where maturity is unknown
- long technical explanations on first view
- hourly-rate-first framing as the default negotiation lens

---

## Required CEO Question Set

The prototype must support at least the following questions:

1. Can all of this be done in 3 months?
2. What do phases 2 to 5 cost?
3. Can you work within our current budget?
4. Why are later phases more expensive?
5. Can you own the whole thing?
6. Can we just work it out as we go?
7. What is your rate?
8. Can you sharpen the price?
9. Why not include manufacturing now?
10. What do you recommend?

---

## Response Pattern

Each suggested answer must follow this pattern:

1. acknowledge the goal
2. reframe around structure, depth, or trade-off
3. offer options
4. recommend one where appropriate

---

## Non-Goals

This contract does not include:

- legal contract drafting
- CRM behavior
- persistent user accounts
- automated email generation
- proposal document generation

---

## Status

This contract is active for the portfolio prototype route only.
