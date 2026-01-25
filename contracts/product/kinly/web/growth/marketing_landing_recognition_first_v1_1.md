---
Domain: product
Capability: marketing_landing
Scope: frontend
Artifact-Type: contract
Stability: evolving
Status: active
Version: v1.1
---

# Contract: Kinly Marketing Landing Page — Recognition Before Action

## Purpose

This contract defines the required structure, ordering, tone, and interaction model for the Kinly marketing landing page at `go.makinglifeeasie.com`.

This version adds an explicit **problem recognition first** requirement before any product promise or CTA.

The page serves two entry cases:
- Desktop visitors following a share link.
- Visitors who have already registered interest and are now learning what Kinly is.

The landing page exists to:
- help visitors emotionally recognise shared living realities
- establish trust before asking for action
- explain what Kinly is *about*, not how it works
- offer a single, calm path to the app stores

This page is not a conversion funnel. It is an invitation.

---

## Core Promise

The landing page MUST clearly and consistently communicate:

> Kinly helps living together feel lighter.

This promise must be *felt* before it is understood.

---

## Definitions

**Above the fold**  
Content visible within the first viewport on a 390×844 mobile device without scrolling.

**Call to Action (CTA)**  
Any interactive element whose primary intent is to prompt download, signup, or immediate action (e.g. store buttons, “get started” links).

**Observational screen**  
A screen that displays reflection, presence, or context without:
- tasks
- assignments
- completion states
- metrics
- prompts to act

---

## Non-Goals

The landing page MUST NOT:

- explain full functionality
- list features
- optimise for speed of conversion
- use urgency or pressure language
- frame shared living as broken or failing
- imply judgement, monitoring, enforcement, or scoring
- position Kinly as a fixer of people or homes
- ask for email or interest capture again

---

## Signals & Gating (Required)

- When the `/get` interest flow succeeds, Web MUST store a client-side marker named `kinly_interest_status` containing:
  - `country_code` (ISO-3166-1 alpha-2)
  - `ui_locale`
  - `captured_at` (ISO timestamp)
- The landing page MUST read this marker to determine whether the visitor previously registered interest.
- Regional availability MUST reference the active region gating contract (`links_region_gate_v1_1.md`). Supported regions are currently **NZ** and **SG**; use that list verbatim.
- If the marker exists **and** the stored `country_code` is not supported, the landing MUST suppress App Store and Play Store buttons and replace Section 9 with a calm status note (see Section 9).
- If no marker exists, the landing MAY infer capability from geo/locale detection, but MUST NOT suppress store buttons without the marker.

---

## Required Page Flow (Strict Order)

Reordering sections violates this contract.

---

### 0. Problem Recognition (Above the Fold)

**Intent**
State the weight of shared living as normal and non-fault-based before any promise or product language.

**Required elements**
- Short recognition statement that acknowledges shared living getting heavy over time
- Explicit removal of blame from individuals
- No product promise, no CTA, no instructions

**Default copy (may be localized)**
```
Shared living gets heavy.
Even when no one is doing anything wrong.
```

**Enforceable signals**
- MUST appear before any product promise or CTA
- MUST NOT imply failure, dysfunction, or fixing people
- MUST NOT use urgency, imperatives, or exclamation

---

### 1. Hero — Emotional Anchor (Above the Fold)

**Intent**  
Allow the visitor to feel safe and recognised before any action is offered.

**Required elements**
- Small Kinly logo (top-left, non-dominant)
- Primary headline expressing lightness or togetherness
- Sub-headline contextualising shared living
- Calm visual reassurance (imagery or app screenshots)

**Enforceable signals**
- MUST NOT contain CTAs
- MUST NOT contain pricing
- MUST NOT contain store buttons
- MUST NOT use imperatives
- MUST NOT use exclamation marks
- MUST NOT make feature claims

---

### 2. App Image Showcase (Above the Fold)

**Intent**  
Screens should feel like a mirror, not a manual.

**Required**
- Exactly three (3) real app screenshots

**Allowed screen sources**
- Today
- Explore
- Hub (observational only)

**Enforceable signals**
Screens MUST NOT show:
- task lists
- assign / complete actions
- numeric counts or scores
- streaks or progress indicators
- onboarding flows
- admin or ownership controls
- calls to action

Additional Today screen constraint:
- Today may be shown only in a calm state with no visible tasks or metrics (e.g., a clear day message or shared presence card).

Screens MUST communicate:
- observation
- shared presence
- calm
- understanding

---

### 3. Recognition Section

**Intent**  
Allow visitors to recognise their lived experience at a glance.

**Required**
- Short, scannable copy describing shared living realities

**Enforceable signals**
- MUST avoid blame or prescriptions
- MUST be readable on mobile without scrolling fatigue
- MUST avoid imperatives and advice framing

---

### 4. Kinly’s Role — Reflection First

**Intent**  
Explain Kinly’s role emotionally, not operationally.

**Required**
This section MUST communicate that Kinly:
- reflects how a home is feeling
- makes care visible
- lowers emotional load

**Enforceable signals**
- MUST NOT describe workflows
- MUST NOT explain mechanics
- MUST NOT show UI
- MUST NOT describe “how to use” the app

---

### 5. Stranger House Moment

**Intent**  
Normalise uncertainty in early or changing shared living situations.

**Required**
- Narrative framing of early, uncertain, or forming homes

**Enforceable signals**
- MUST normalise uncertainty
- MUST frame “forming” as healthy and expected
- MUST NOT give instructions or advice

---

### 6. Audience by Situation

**Intent**  
Describe who Kinly is for without demographics or labels.

**Required**
- Situational descriptions only

**Allowed examples**
- Flatmates who didn’t choose each other
- Homes adjusting to change
- People who care but avoid drama

**Enforceable signals**
- MUST NOT use age, role, or income descriptors
- MUST NOT imply ideal behaviour

---

### 7. Trust Clarification (“Kinly is not…”)

**Intent**  
Disarm fear of judgement, surveillance, or enforcement.

**Required**
- Explicit clarification of what Kinly is not

**Enforceable signals**
- MUST reduce common misinterpretations
- MUST be concise and calm
- MUST NOT introduce new features

---

### 8. Weekly Reflection (Supporting Signal)

**Intent**  
Communicate that Kinly works on human time, not app time.

**Required**
- Short descriptive paragraph

**Enforceable signals**
- MUST appear below the fold
- MUST NOT be a primary visual
- MUST NOT imply obligation, streaks, or compliance

---

### 9. App Store Routing (Below the Fold)

**Intent**  
Offer action only after understanding.

**Required**
- One iOS App Store button
- One Android Play Store button

**Enforceable signals**
- Buttons MUST appear only once
- Buttons MUST appear only below the fold
- Buttons MUST NOT be duplicated elsewhere
- Buttons MUST NOT use urgency language
- MUST NOT offer additional forms or email capture
- If the visitor already registered interest and their region is not released, suppress both store buttons and all “get the app” microcopy; replace this section with a single calm status note (e.g., “We’ll let you in when Kinly opens in your area.”) while leaving all prior sections unchanged.

**Allowed microcopy**
- “Available on iOS and Android”
- “Get the app”

**Disallowed**
- “Download now”
- “Start free”
- “Join today”

---

## Visual Content Rules

- Visuals are supportive, not persuasive
- App screenshots MUST be real
- Illustrations MAY be used sparingly below the fold
- No animated or dynamic visuals above the fold
- Device frames are optional and non-required

---

## Tone and Language Rules

All copy MUST:

- be readable at Grade 6–7 level
- use short sentences
- avoid moral language
- avoid imperatives (“do”, “fix”, “improve”)
- avoid outcome guarantees
- avoid before/after framing
- sound calm, reflective, and invitational

---

## Desktop / Wide Layout Rules

- Section order MUST remain identical to mobile.
- “Below the fold” for desktop (≥1024px width) means CTAs MUST NOT appear within the first viewport height; store buttons stay only in Section 9.
- No sticky headers, floating CTAs, or duplicated header/footer CTAs.
- Multi-column layouts are allowed only within a section and MUST NOT surface CTAs earlier in the flow.
- Hero height MUST be capped so screenshots and recognition copy remain visible without revealing CTAs early.

---

## Success Criteria

This contract is satisfied if a first-time visitor can truthfully say:

- “That feels familiar.”
- “This isn’t judging me.”
- “I don’t have to do anything yet.”

Conversion is secondary to trust.

---

## Codex Enforcement Guidance

Codex MUST:

- enforce section order
- enforce single CTA placement below the fold
- validate screenshot allowlist and constraints

Codex SHOULD:

- lint for forbidden language
- flag imperatives and urgency phrasing

Codex MUST NOT:

- optimise for conversion
- insert growth patterns
- introduce analytics-driven persuasion by default

---

## Known Pressures

If external requirements (SEO, platform review, growth tooling) conflict with this contract, recognition-first ordering takes precedence.

---

## Future Evolution (Non-Binding)

Future versions may allow:

- regional variants
- life-transition-specific landing paths
- optional light product previews

All future changes MUST preserve recognition-before-action ordering.
