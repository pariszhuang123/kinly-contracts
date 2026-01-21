---
Domain: Shared
Capability: Reflective Generation
Scope: shared
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v1.0
---

# Reflective Generation Contract (v1)

**Contract ID:** `reflective_generation_v1`  
**Status:** Stable (pre-implementation)  
**Type:** System UX pattern  
**Owner:** Frontend (copy resolved by mode)  
**Scope:** Artifact creation flows only

## Purpose

- Create a deliberate pause when Kinly forms identity- or expectation-setting artifacts.  
- Signal care and intentionality; frame outputs as reflections/declarations, not system decisions.  
- Encourage slower, thoughtful reading.  
- This is **not** a loading state or AI affordance.

## Invocation

- Required enum: `ReflectiveGenerationMode { personal_preferences, house_rules, generic }`.  
- Mode is mandatory; missing mode must assert/fail at build time.

## Three-phase ritual (locked)

1. **Immediate acknowledgment** (0–100 ms) — “Got it.” Primary action disabled; optional light haptic.  
2. **Reflective pause** (600–1800 ms, ideal 1000–1200 ms) — Soft fade/breathing animation only. Non-skippable for personal_preferences (back/close disabled during the pause to honor the ritual). No spinners/bars/percentages. Copy resolved strictly by mode. One primary line required, optional secondary (can be time-staggered). Timing is frontend-owned.  
3. **Reveal moment** — Subtle transition (fade-up/slide). Title appears first, then content, CTA last. No “success” toasts; the artifact itself is confirmation.

Hard constraints: minimum duration 600 ms, maximum 1800 ms, ideal 1000–1200 ms. One reflective generation per flow; never stacked; skip reflection on backend errors.

## Modes (copy packs)

### personal_preferences
- **Authorship:** Single author = the user. Editable only by the user; shareable for understanding.  
- **Meaning:** Descriptive, first-person, about comfort/experience; never authoritative.  
- **Tone:** Personal, reflective, non-directive.  
- **Primary copy (options):**  
  - “Reflecting what you shared.” *(recommended default)*  
  - “Putting your preferences into words.”  
  - “Shaping this around what feels right to you.”  
- **Secondary copy (options):**  
  - “So others can understand what feels comfortable to you.” *(recommended default)*  
  - “Just your perspective — nothing assumed.”  
  - “This helps others meet you where you are.”  
- **Exclusions:** No rules/agreements/defaults/expectations/standards/settings/enforcement language.

### house_rules
- **Authorship:** Single author = home owner. Read-only for others; no voting/editing by non-owners.  
- **Meaning:** Declared expectations; mirrors real-world rental dynamics.  
- **Tone:** Neutral, declarative, calm, non-enforcing.  
- **Primary copy (options):** “Putting the home’s expectations into words.” *(recommended)* / “Clarifying how this home works.” / “Writing this down so there are no surprises.” / “Stating the home’s boundaries clearly.”  
- **Secondary copy (options):** “So everyone knows what to expect.” *(recommended)* / “Set by the home owner, shared openly.” / “Clear, visible, and easy to refer back to.” / “Not enforced — just stated.”  
- **Exclusions:** No collective language (“we agreed”), enforcement, consequences, penalties, system defaults.

### generic
- **Authorship:** Context-dependent; non-identity-forming.  
- **Meaning/Tone:** Neutral artifact; calm and minimal.  
- **Primary:** “Putting this together with care.” Secondary optional/omitted.

## Exclusion rules

Never use for deterministic/instant actions (saving settings, invites, permissions, payments), retrieval/navigation (opening artifacts, editing drafts), or low-stakes UI (filters, sorting, layout/theme tweaks). If the user expects instant feedback, do not reflect.

## Engineering notes

- Frontend owns timing; backend speed must not alter duration.  
- Skip reflection on errors; surface the error immediately.  
- Copy is mode-resolved; no inline overrides.  
- Add assertions to prevent usage without a mode.  
- Artifact reveal should arrive formed (no loading/progress in the reveal moment).