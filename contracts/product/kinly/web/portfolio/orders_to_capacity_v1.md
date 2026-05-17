---
Domain: Portfolio
Capability: Orders to capacity manufacturing reporting prototype
Scope: frontend
Artifact-Type: contract
Stability: evolving
Status: active
Version: v1.0
---

# Contract - Orders-to-Capacity Manufacturing Reporting Prototype - v1.0

Registry: `contracts/contracts_registry.md`

---

## Purpose

This contract defines a public portfolio prototype at:

`/portfolio/orders-to-capacity`

The prototype exists to demonstrate how a data analyst in a manufacturing
environment could interpret cross-functional reporting requirements and propose
a practical first-version management reporting model.

The prototype must show how data from Sales, Finance, Inventory, and Production
could be consolidated into a clearer operating view that supports:

- production planning
- inventory visibility
- forecast support
- variance analysis
- reporting consistency
- management recommendation

The prototype is not intended to replicate a full BI implementation. It is
intended to prove:

- understanding of manufacturing reporting requirements
- ability to translate role requirements into reporting structure
- ability to define a small set of decision-useful metrics
- ability to connect analysis to practical management action
- ability to suggest how the same logic could later be implemented in Power BI
  or other reporting tools

All prototype content must use mock data only.

---

## Canonical User

The canonical user is a hiring manager, interviewer, or business stakeholder
reviewing the prototype as evidence of analytical and reporting judgement.

The page is optimized for:

- rapid understanding of the business problem
- clear demonstration of requirement interpretation
- credible first-version reporting design
- practical manufacturing planning reasoning

The page is not optimized for:

- detailed enterprise data engineering review
- production-grade BI delivery
- live operational use
- company-specific process accuracy

---

## Core Outcome

The prototype must help move the conversation from:

- "This candidate can build dashboards"

toward:

- "This candidate understands the reporting requirements of a manufacturing
  planning role and can propose a sensible first reporting model"

The prototype must make clear that the value is not visual polish alone. The
value is the ability to define what should be measured, why it matters, and how
it supports decisions.

---

## Role Alignment

This prototype must visibly align with the following reporting responsibilities
commonly found in manufacturing analyst roles:

- consolidating fragmented data into a central reporting view
- supporting Sales, Finance, and Internal Supply Chain information needs
- enabling production planning and inventory management
- supporting financial forecasting and scenario planning
- surfacing variance against plan, forecast, capacity, and output
- identifying lead time variability, workload spikes, capacity constraints, and
  stock risk
- improving reporting consistency through shared definitions

The prototype must present itself as a first-version response to those
requirements, not as a claim about any real company's systems or performance.

---

## Required Route Behavior

The canonical public route is:

`/portfolio/orders-to-capacity`

The route must:

- render as a human-readable portfolio prototype
- remain safe to open in any browser context
- remain usable on desktop and mobile
- clearly disclose that all data is fictional
- clearly explain why this reporting model was chosen

The route must not:

- require authentication
- depend on backend persistence
- imply access to private company data
- claim operational accuracy for any named employer
- present speculative numbers as real business facts

The route may be indexable, but it must remain explicit that the prototype is
self-initiated and fictional.

---

## Required Information Architecture

The prototype must contain the following sections or equivalent route structure.

### 1. Portfolio Landing / Framing

A first-view section that explains:

- what the prototype is
- why this business problem was chosen
- what the prototype is intended to prove
- what kinds of role requirements it is responding to

This section must position the work as a proposed first-version reporting
model, not a complete solution.

### 2. Executive Summary View

A management-facing summary showing the highest-priority operating signals.

This view must include:

- forecast revenue vs plan
- open order value
- orders at risk
- capacity utilisation
- inventory value
- aged inventory value
- primary bottleneck area
- management recommendation

This view must answer:

- What requires management attention this period?

### 3. Capacity Planning View

A deeper operational view focused on whether expected demand can be met with
available capacity.

This view must include:

- planned hours vs available hours
- weekly capacity gap
- utilisation by work centre
- output vs plan
- late jobs by reason
- lead time variability
- bottleneck work centre

This view must answer:

- Can expected demand be delivered with current capacity, and where are the
  main constraints?

### 4. Why This Prototype

A rationale section explaining why these views and metrics were chosen.

This section must explain:

- why cross-functional reporting matters in manufacturing
- why variance analysis is central
- why reporting consistency matters across departments
- why a narrow first-version design is more useful than a broad dashboard set
- how the same logic could later be implemented in Power BI, Excel, Jet
  Reports, Crystal Reports, or SQL-backed reporting

### 5. Mock Data Model Summary

A concise explanation of the mock data entities and their relationships.

The prototype must show how the reporting model connects at least:

- sales orders
- production jobs
- inventory
- work centres
- finance forecast

This section must reinforce that the prototype is built around shared
definitions rather than isolated departmental reports.

---

## Required KPI Set

The prototype must visibly support a small, consistent KPI set tied to the
role's likely requirements.

At minimum, the prototype must support the following KPI themes:

1. Forecast revenue vs plan variance
2. Production output vs plan variance
3. Weekly capacity gap
4. Capacity utilisation by work centre
5. Orders at risk
6. Lead time variability
7. Inventory ageing
8. Stock position against forecast demand
9. Bottleneck identification
10. Management recommendation

The prototype may include additional measures, but it must not dilute focus
with excessive metric volume.

---

## Required Analytical Framing

The prototype must demonstrate the following analytical behaviours:

- translating fragmented operational data into a shared reporting structure
- comparing actuals, plan, and forecast where relevant
- surfacing exceptions rather than only summarising totals
- identifying where management attention is needed
- turning analysis into practical next-step recommendations

Recommendations must be framed as mock operating suggestions, for example:

- review overload in a constrained work centre
- investigate delayed jobs by common cause
- review slow-moving inventory in a product family
- assess whether planned demand requires overtime, rescheduling, or stock
  review

Recommendations must not be presented as advice based on real company data.

---

## Mock Data Rules

The prototype must use fictional data only.

It may use generic manufacturing entities such as:

- sales orders
- jobs
- inventory items
- work centres
- forecast records

The mock data should be believable enough to support the story, but must avoid:

- real customer identities
- real supplier identities
- real operational performance claims
- private internal naming or process assumptions presented as fact

---

## Content Rules

All copy must:

- sound commercially and analytically credible
- remain concise and easy to scan
- focus on business decisions, not only visuals
- explain assumptions where necessary
- avoid overstating certainty

All copy must avoid:

- pretending to know company-specific internals
- generic dashboard filler language
- excessive BI jargon without business meaning
- claims that the prototype is production-ready

---

## Required Positioning

The prototype must clearly communicate that it is intended to prove:

- understanding of manufacturing planning and reporting needs
- ability to define consistent reporting logic
- ability to structure management-facing analysis
- ability to suggest what a practical first reporting layer could be

The prototype must not frame itself primarily as:

- a full technical solution
- a finished BI system
- a substitute for stakeholder discovery and validated business definitions

---

## Non-Goals

This contract does not include:

- real company analysis
- live ERP integration
- production-grade Power BI delivery
- advanced statistical forecasting models
- optimisation engines
- AI planning automation
- procurement system design
- authenticated workflow tooling

---

## Disclaimer

The prototype must clearly disclose that it is:

- self-initiated
- based on public role requirements only
- built with fictional data
- not commissioned, endorsed, or reviewed by any company referenced in an
  application context

---

## Status

This contract is active for the portfolio prototype route only.
