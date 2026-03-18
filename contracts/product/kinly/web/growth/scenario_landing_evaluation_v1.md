---
Domain: product
Capability: scenario_landing_evaluation
Scope: frontend
Artifact-Type: contract
Stability: stable
Status: active
Version: v1.0
---

# Contract: Kinly Scenario Landing Evaluation v1.0

## Purpose

This contract defines the required evaluation method for Kinly's scenario landing
pages before they are approved, rewritten, or scaled.

It exists to make landing-page review repeatable and to prevent drift away from
Kinly's core product truth.

This contract applies to:

- `app/kinly/general/page.tsx` when rendered as the generic landing page
- `app/kinly/general/page.tsx?entry=<scenario>` when rendered as a scenario entry
- `app/kinly/market/*/page.tsx` scenario routes
- scenario copy/config rendered by `app/kinly/market/ScenarioLandingClient.tsx`

This contract is an evaluation gate, not a replacement for implementation or
copy contracts.

Scenario pages MUST still conform to:

- `../../../../design/copy/kinly/web/scenario_landing_copy_contract_v1.md`
- `marketing_landing_recognition_first_v1_2.md` where shared landing principles still apply

---

## Core Truth (Invariant)

Every evaluated page MUST make this meaning clear:

> Kinly reduces repeated conversations in shared living by making expectations visible.

For scenario pages, the review question is:

> Does this page reduce the need to repeat things in shared living?

If the answer is "no" or "not clearly", the page FAILS regardless of score.

---

## In-Scope Evaluation Unit

A single evaluation unit is one published landing experience for one route and one
persona.

Examples:

- `/kinly/general`
- `/kinly/market/flat-agreements`
- `/kinly/market/live-in-landlord`
- `/kinly/general?entry=flat-agreements`

Each unit MUST be evaluated independently, even when multiple routes share the
same rendering shell.

---

## Required Persona Record

Before scoring begins, the evaluator MUST record:

- Persona name
- Route under review
- Top 3 pains
- One awkward moment the page should make recognisable
- One avoidance behaviour the page should make recognisable

If the evaluator cannot fill this in from the page and its scenario definition,
the page fails Persona Fit.

---

## Scored Dimensions (0-100)

Each page MUST be scored across the dimensions below.

### 1. Clarity (25 points)

Within 3 seconds, a new visitor MUST be able to answer:

- Who is this for?
- What problem keeps happening?
- What does Kinly do?

Scoring:

- 25: instantly clear
- 15: partially clear
- 5: vague
- 0: confusing

### 2. Persona Fit (20 points)

The page MUST feel written for one specific scenario, not for "shared living" in
general.

Required signals:

- explicit or strongly implied persona
- examples that match that persona's power dynamics
- wording that sounds native to the scenario

Fail examples:

- generic roommate language reused without adaptation
- audience copy broad enough to fit anyone

### 3. Problem Specificity (15 points)

The pain MUST sound like a real repeated situation.

Required signals:

- first-person or lived-experience phrasing
- concrete examples
- recognisable repeated moments

Pass examples:

- "I keep bringing up the same cleaning issue."
- "I don't want to sound controlling when I mention guests again."

Fail examples:

- "improve shared living harmony"
- "communication breakdown in shared environments"

### 4. Emotional Accuracy (15 points)

The page MUST reflect the emotional cost of repetition.

At least one of these emotions MUST be strongly present:

- frustration
- awkwardness
- avoidance
- resentment
- mental load

Neutral, polished, or over-safe copy that removes the tension fails this
dimension.

### 5. Mechanism Clarity (10 points)

The page MUST make Kinly's mechanism understandable.

The visitor MUST be able to infer all of the following:

- expectations are written down once
- everyone can see the same baseline
- the home can refer back later instead of repeating the conversation

If the page only communicates mood, trust, or tools without this mechanism, it
cannot score above 5 in this category.

### 6. Single-Idea Focus (10 points)

The page MUST stay anchored on one core idea:

- repeated conversations create tension
- visible expectations reduce that tension

Pages lose points when they drift into multiple parallel promises such as:

- chores management
- bills management
- flat operations
- productivity
- generic wellbeing

### 7. Cognitive Load (5 points)

The page MUST be easy to scan on mobile.

Required signals:

- short paragraphs
- clear section hierarchy
- low jargon density
- no dense walls of copy

---

## Hard Fail Conditions

If any hard fail condition is true, the page score is treated as 0 and the page
is not valid.

### 1. Broken Core Truth

The page does not connect repetition to tension, or does not make visible
expectations feel like the relief.

### 2. Abstract-First Messaging

The page leads with abstract product words before lived pain.

Examples:

- platform
- system
- ecosystem
- solution

### 3. Feature-First Structure

The page explains tools, screenshots, or features before the user recognises the
problem.

### 4. Missing Persona

The evaluator cannot tell who the page is for.

### 5. Generic Audience Claim

The page implies it is for everyone, or uses audience language too broad to
shape recognisable entry copy.

---

## Section-Level Evaluation Rules

The evaluator MUST review each major section in order.

### Recognition / Hero

Must establish:

- who the page is for
- the repeated tension
- emotional recognition before product explanation

### What Kinly Is

Must define Kinly clearly as a shared living app and connect that identity to
visible expectations.

### How Kinly Helps in Practice

Must make the mechanism legible without drifting into enforcement or task-system
framing.

### Role / Reflection / Forming-Home Sections

Must reinforce that Kinly reduces repeated reminders and lowers social friction,
not that it controls people.

### Not-List

Must actively remove surveillance, policing, and scorekeeping interpretations.

### Availability / CTA

Must remain secondary to understanding.

This section is not scored for conversion optimization. It is scored only on
whether it preserves the page's calm framing and does not redefine the product.

---

## Scoring Interpretation

- 90-100: excellent, ready to scale
- 80-89: valid, minor improvements allowed
- 60-79: risky, rewrite the weakest section before scaling
- below 60: messaging broken, redesign required

A page is valid only if:

- total score is 80 or higher
- no hard fail condition is triggered

---

## Required Evaluation Process

For every page under review, the evaluator MUST:

1. identify the persona and route
2. record the persona record
3. read the page once without editing
4. apply hard fail checks
5. score each dimension
6. name the weakest dimension
7. rewrite only the weakest section first
8. re-score after changes

Review MUST focus first on recognition, mechanism clarity, and persona fit.

---

## Cross-Page Consistency Rule

Across all scenario landing pages, the following MUST remain constant:

- core problem: repetition creates tension
- core mechanism: expectations are visible and shared
- core value: fewer repeated conversations, less social strain

The following MAY vary by persona:

- examples
- emotional emphasis
- vocabulary
- awkward moments
- avoidance patterns

Scenario pages MUST NOT behave like different products for different audiences.
They are different entry points into the same truth.

---

## Output Format (Required)

Every evaluation record MUST produce:

- route
- persona
- total score
- dimension scores
- hard fail status
- weakest dimension
- recommended rewrite target

Recommended scorecard template:

| Route | Persona | Clarity | Persona Fit | Specificity | Emotional Accuracy | Mechanism Clarity | Focus | Cognitive Load | Total | Hard Fail |
| ----- | ------- | ------- | ----------- | ----------- | ------------------ | ----------------- | ----- | -------------- | ----- | --------- |
| `/kinly/market/example` | Example persona | 0-25 | 0-20 | 0-15 | 0-15 | 0-10 | 0-10 | 0-5 | 0-100 | Yes/No |

---

## Quick Operator Test

Before approving a page, the evaluator SHOULD ask:

1. Do I know who this is for immediately?
2. Do I recognise a repeated conversation?
3. Do I understand how Kinly reduces that repetition?
4. Do I feel relief instead of pressure?

If any answer is "no", the page should not be treated as ready.
