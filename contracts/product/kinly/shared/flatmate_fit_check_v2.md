---
Domain: Homes
Capability: Flatmate Fit Check
Scope: shared
Artifact-Type: contract
Stability: evolving
Status: draft
Version: v2.0
---

# Kinly Flatmate Fit Check Contract v2.0

Status: Draft

Scope: Owner-first pre-interview screening tool. Captures a home's living
style via behavioural scenario questions, collects anonymous candidate
responses, and generates a briefing for the head tenant on what to be
aware of and what to ask before the interview. v2 replaces the v1
"anonymous web + app-only claim" model with a **web-authenticated
freemium gate** model.

Audience: Product, design, engineering, AI agents.

Platform: Web (must be web-accessible). Must be i18n-ready from day one.

Depends on:
- Flatmate Fit Check v1 (`contracts/product/kinly/shared/flatmate_fit_check_v1.md`)
- House Norms Taxonomy v1 (`contracts/product/kinly/shared/house_norms_taxonomy_v1.md`)
- House Norms Scenarios v1 (`contracts/product/kinly/shared/house_norms_scenarios_v1.md`)
- Users v1 — Supabase auth (`contracts/api/kinly/identity/users_v1.md`)
- Homes v2 (`contracts/api/kinly/homes/homes_v2.md`)

---

## 1. Purpose

The Flatmate Fit Check gives a head tenant (or lived-in landlord) a
structured way to screen applicants before an interview.

This helps surface issues that are usually invisible during interviews
but often become ongoing friction after move-in.

The system:
1. Captures the home's living style via behavioural scenario questions
2. Collects the same scenarios from the candidate (anonymous)
3. Generates a **pre-interview briefing** for the owner: what to be aware
   of + what questions to ask to confirm
4. May show a candidate-specific **Alignment Preview** to help the owner
   understand where living-style expectations already line up
5. Provides the owner a **web dashboard** for all candidate submissions
   tied to their fit-check runs (for unlocked runs)
6. After app download, stores the owner's answers so they can later
   prefill House Norms and personal preference flows (but does not
   auto-write to those systems)
7. Uses a **freemium gate** to convert web-only owners into app users
   after they have experienced enough value

## 2. Core Product Principle

This is an **owner-first screening tool**.

Value flows to the head tenant / lived-in landlord. The candidate
participates, but the product does not promise the candidate independent
value.

The system focuses on identifying where day-to-day friction is most
likely to occur, rather than evaluating whether someone is a "good" or
"bad" fit.

v2 adds: the product is **web-first for acquisition** (low-friction entry,
immediate value) and **app for retention** (persistent dashboard,
notifications, home management). The freemium gate bridges the two.

It is NOT:
- A mutual compatibility tool
- A scoring, ranking, or gatekeeping system
- A replacement for conversation or interviews

## 3. Problem Definition

Head tenants and lived-in landlords:
- Receive multiple applicants
- Rely on gut feel and repeated conversations
- Often discover lifestyle mismatches after move-in

This system gives the owner a structured briefing on what to explore
before committing, based on how the applicant answered the same living
scenarios.

v2 additionally addresses:
- The v1 anonymous-web/app-claim model loses owners who never complete
  the app claim step, creating a drop-off gap between web value and
  retained engagement
- Requiring an app download before the owner can re-access briefings
  reduces repeat usage and sharing
- Web authentication removes the fragile claim-token handoff and lets
  the owner see results immediately on web

## 4. Scope

### Included
- Behavioural scenario-based question capture (3 options per question)
- Web-authenticated owner flow (Supabase OAuth — Google or Apple)
- Owner web dashboard for runs and candidate briefings
- Freemium usage gate (first 3 runs free on web, 4th+ gated to app)
- Anonymous candidate response flow
- Owner pre-interview briefing (alignments, watchouts, suggested
  questions, and temporary candidate-specific alignment preview)
- Email notifications to owner on candidate submission
- App handoff with auto home bootstrap for gated owners
- Persistent storage of owner answers for later prefill into House Norms

### Excluded
- Financial verification (bond, job checks)
- Legal tenancy processes
- Personality matching or scoring
- Ranked applicant lists or sorting by fit
- Candidate-facing compatibility or comparison results
- Direct writes to `house_norms` or `preference_responses` (see §15)
- v1 anonymous-web/app-claim token flow for new users (deprecated for
  new entrants; see §21)

## 5. Questions: Behavioural Scenario Capture

Unchanged from v1; see `flatmate_fit_check_v1.md` §5.

The same 4 behavioural scenarios, same taxonomy, same i18n rules apply.

## 6. Owner Identity Model

### 6.1 Authentication Required

The owner MUST authenticate via **Supabase OAuth** (Google or Apple) on
web before results are saved.

Authentication is NOT required to begin answering scenarios. The owner
MAY answer all 4 behavioural questions anonymously. Authentication is
prompted **after** the owner completes the scenarios, at the point of
saving results. This preserves the low-friction entry of v1 while
ensuring persistent identity before data is committed.

Ownership of a fit-check run is bound to the authenticated user on web,
not via app claim tokens. The v1 anonymous-web/app-claim model is
superseded for new users.

### 6.2 Identity Linking

Backend linking MUST use the stable authenticated user/account identity
(`auth.uid()`) returned by Supabase, not raw email string matching.

"Login with the same email" is user-facing guidance only — it helps
owners understand they should use the same provider when moving from web
to app. The system MUST NOT rely on email comparison to resolve identity;
`auth.uid()` is the canonical identifier.

### 6.3 Session Persistence

After authentication, the owner's web session MUST persist across
browser tabs and page reloads until explicit sign-out or session expiry.
The owner MUST NOT be required to re-authenticate for each run.

## 7. Freemium Usage Gate

### 7.1 Definition of "Use"

A single "use" is defined as: **one newly created owner-completed
fit-check run** — that is, the owner answers all 4 behavioural scenarios
and the run is saved to the database.

The following do NOT count as a use:
- Reopening or viewing an existing run
- Editing answers on a previously completed run
- Viewing candidate submissions or briefings for any run

### 7.2 Free Tier (Runs 1–3)

For the first 3 completed runs, the owner receives **full web access**
to:
- All results and home vibe summaries
- All candidate briefings (alignments, watchouts, suggested questions,
  alignment preview)
- Summary reports and dashboards

### 7.3 Gated Tier (Run 4+)

Starting from the 4th completed run:
- The owner is gated after answering scenarios
- Web shows a **gate screen** explaining what they get in the app:
  - All fit check reports in one place
  - Home management features
  - Push notifications for new candidate submissions
- The gate screen MUST include a prominent app download link / CTA
- Prior unlocked runs (1–3) remain fully web-accessible — the gate
  applies only to newly created runs beyond the free tier

#### 7.3.1 Gated Run Visibility

On a gated run, the web MUST still show the owner:
- Their own scenario answers and home vibe summary for that run
- The share link (so they can still send it to candidates)

The gate restricts access to **candidate briefings, watchouts, and
suggested questions** for that run — not the owner's own answers.

This ensures the owner sees immediate value from their effort (their
summary + share link) and understands what they'll unlock in the app.

### 7.4 Usage Counter

- The usage counter is **server-side**, keyed by the authenticated
  owner's user id (`auth.uid()`)
- The counter MUST be accurate and tamper-resistant (not derived from
  client state)
- The counter increments when a run is saved (4 scenarios completed +
  persisted), not on run creation or partial progress

### 7.5 Gate Timing

The gate check happens when the owner tries to **create and complete a
new run**, not when viewing existing runs, submissions, or briefings.

If the owner is at their gate threshold (3 completed runs):
- They MAY begin a new run and answer scenarios
- After answering all 4 scenarios on their 4th+ run, the gate screen is
  shown instead of the full results
- The run is still saved to the database (answers are not discarded)
- The owner can access the full results for that run via the app

## 8. Functional Flow — Owner (Web, Authenticated)

### 8.1 Step 1 — Entry

Owner lands on the fit check web page.

Owner sees scenario framing:
> Template key: `fit_check.owner.entry_prompt`
> (en: "Quick check to spot potential issues before inviting someone to
> view")

### 8.2 Step 2 — Answer 4 Behavioural Scenarios

Owner answers 4 behavioural questions. Each answer stores a
`scenario_id` + `option_index` (0, 1, or 2).

Same questions as v1 §5.

This step does NOT require authentication. The owner answers scenarios
in an anonymous browser session to keep entry friction low.

### 8.3 Step 3 — Authentication (Save Gate)

After answering all 4 scenarios, the owner is prompted to sign in via
Google or Apple (Supabase OAuth) before results are saved.

If the owner is already signed in (active session), this step is
skipped automatically.

Authentication MUST happen before answers are persisted to the database.
The owner MAY NOT skip authentication and still receive saved results.

If the owner abandons authentication at this step, answers are not
persisted. The owner can restart the flow.

### 8.4 Step 4 — Output

System generates a home vibe summary from captured values and saves the
run to the database, bound to the owner's `auth.uid()`.

Output uses template keys per dimension, resolved by locale and
option_index. Example (en):

> "Cleans straight away · Quiet early nights · Roster system · Raises
> things early"

For runs 1–3: full results displayed on web.

For runs 4+: gate screen displayed (see §7.3).

### 8.5 Step 5 — Share Link

System creates a `fit_check_share_token` and displays a shareable URL.

The owner can copy and send this link to applicants.

### 8.6 Step 6 — Dashboard Access

Owner can return anytime (web) and see their dashboard of runs and
candidate submissions (see §10).

For runs 1–3: full web access to all briefings and reports.

For runs 4+: gated — gate screen shown with app benefits + download CTA.

## 9. Functional Flow — Candidate (Anonymous, Web)

Unchanged from v1; see `flatmate_fit_check_v1.md` §6.2.

The candidate flow remains anonymous, web-based, and unchanged:
- Open shared link → identify self (`display_name`) → answer same 4
  scenarios → location capture → confirmation → personalized result
  page → optional app CTA
- Candidate MUST NOT see owner answers before submitting
- Candidate does not receive compatibility results or owner briefing
  output

## 10. Owner Web Dashboard

### 10.1 Profile Display

The owner's profile name and avatar/icon MUST be displayed at the
top-right corner of the dashboard.

The dashboard URL MUST use an opaque identifier (e.g.,
`/fit-check/dashboard`) and MUST NOT include the owner's profile name,
email, or other personally identifiable information in the URL path or
query parameters. The owner's identity is resolved from the
authenticated session, not from the URL.

This preserves the asymmetric visibility model: candidates who receive a
share link MUST NOT be able to infer the owner's identity from any URL
structure.

### 10.2 What Is a "Run"

A "run" represents one screening session for one listing, room, or
batch of applicants. The owner creates a new run each time they want to
screen candidates for a different situation.

Examples:
- Screening applicants for a spare room → one run
- Re-screening after a flatmate leaves 6 months later → a new run
- Screening for a second property → a new run

The dashboard SHOULD frame runs with creation dates and summary labels
so the owner can distinguish them. The system does NOT enforce what a
run is "for" — this is the owner's organisational choice.

### 10.3 Runs List

The dashboard MUST show a list of all the owner's completed runs with:
- Run identifier or home vibe summary label
- Creation timestamp
- Number of candidate submissions received per run
- Visual indicator of locked vs unlocked status

### 10.4 Run Detail

Clicking into a run shows:
- Full home vibe summary for that run
- List of candidate submissions with `display_name`, `submitted_at`,
  location, and a preview of the top watchout
- Ability to open the full briefing per candidate (see §11)

### 10.5 Access Rules

- For runs 1–3: full web access to all details, briefings, and reports
- For runs 4+: owner's own summary and share link are visible; candidate
  briefings are gated with app download prompt (see §7.3.1)

## 11. Owner Briefing

Same structure as v1 §6.3: context, alignments, watchouts, suggested
questions, alignment preview, limitation disclaimer.

See `flatmate_fit_check_v1.md` §6.3 for full specification.

In v2, the briefing is rendered on web for unlocked runs (runs 1–3). For
gated runs (4+), the briefing is accessible only via the app.

## 12. Recipient Tracking + Email Notifications

### 12.1 Submission Tracking

The system MUST track how many recipients (candidates) have filled in
each run's questionnaire.

The submission count MUST be visible to the owner on the web dashboard
(§10.2) and in the app.

### 12.2 Email Notification on Submission

The system MUST send an email notification to the owner every time a
candidate submits a completed questionnaire.

### 12.3 Email Content

Each notification email MUST include:
- Candidate `display_name`
- Submission timestamp
- Link to view the briefing:
  - For runs 1–3: link routes to the web summary report / briefing view
  - For runs 4+: link routes to an app download/open page

The email SHOULD include a brief summary of the top watchout or
alignment status to entice the owner to review.

### 12.4 Notification Preferences

The owner MUST be able to control email notification frequency:

| Setting | Behaviour |
|---|---|
| `every_submission` (default) | One email per candidate submission |
| `daily_digest` | One daily summary email with all new submissions |
| `muted` | No email notifications; owner checks dashboard manually |

Notification preference is per-owner (applies to all runs), not
per-run. The preference is set from the web dashboard or app settings.

The system MUST include an **unsubscribe link** in every notification
email that sets the preference to `muted`.

### 12.5 Delivery Model

Candidate submission success MUST NOT depend on synchronous email
delivery. Email is **async / fire-and-forget**.

Rules:
- The candidate's submission is committed to the database before any
  email dispatch is attempted
- Email delivery failure MUST NOT cause the submission to fail or roll
  back
- The system SHOULD retry transient email failures but MUST NOT block
  the submission pipeline on retries

## 13. App Handoff + Auto Home Bootstrap

### 13.1 Trigger

After the 4th completed run, the owner is prompted to download the app
via the gate screen (§7.3).

### 13.2 CTA Framing

The gate screen CTA MUST explain app benefits clearly:
> Template key: `fit_check.gate.app_cta`
> (en: "See all your fit check reports, manage your home, track
> applicants — download Kinly")

### 13.3 App Entry Detection

The app MUST know whether the user arrived via the fit-check funnel.

The recommended mechanism is a **server-side flag**: the backend tracks
whether the authenticated user has any fit check runs
(`fit_check_drafts WHERE owner_user_id = auth.uid()`). On first app
login, the app calls `fit_check_app_bootstrap` which checks this flag
and triggers the appropriate flow.

The app MUST call `fit_check_app_bootstrap` on first login when the
user has existing fit check runs. The app MUST NOT call this endpoint
for users who have no fit check history.

### 13.4 App Login Behaviour

When the owner logs into the app (with the same authenticated account,
matched by `auth.uid()`) and bootstrap is triggered:

- **If no home exists**: a home is automatically created for them.
  - Home name: defaults to `"{owner_display_name}'s Home"` (localised
    via template key `fit_check.bootstrap.default_home_name`)
  - The owner is assigned the `owner` role on the auto-created home
  - The owner MAY be prompted to rename the home or complete home
    details later, but this is optional and non-blocking
  - This bypasses the normal create-home flow
- **If exactly one home exists**: fit check runs are attached to that
  home. No duplicate home is created.
- **If multiple homes exist**: the app MUST prompt the owner to choose
  which home to attach fit check runs to. The system MUST NOT guess.

### 13.5 Fit Check Prominence in App

In the app, the fit check report MUST be the **top / first item** on the
home screen or dashboard after the owner's initial app login from the
fit-check funnel.

All prior web runs and candidate submissions MUST be immediately visible
in the app.

### 13.6 Scope of Auto-Home Creation

Auto-home creation is **fit-check-funnel-specific**, not a
platform-wide behaviour change.

Rules:
- Auto-home creation MUST only trigger via `fit_check_app_bootstrap`
  when the owner has fit check runs and no existing home
- Other app entry points (direct download, invite link, etc.) MUST NOT
  trigger auto-home creation
- The auto-created home follows standard Homes v2 data model and
  lifecycle rules after creation
- The auto-created home uses the same `homes` table and RLS rules as
  any other home — it is not a special entity

## 14. Visibility Model

Same as v1 §9 with one extension:

| Data | Owner (Web, unlocked) | Owner (Web, gated) | Owner (App) | Candidate |
|---|---|---|---|---|
| Owner's scenario answers | ✅ | ✅ | ✅ | ❌ |
| Home vibe summary | ✅ | ✅ | ✅ | ❌ |
| Share link | ✅ | ✅ | ✅ | N/A |
| Candidate's scenario answers | ✅ (briefing context) | ❌ (app only) | ✅ | ✅ (own result page only) |
| Pre-interview briefing | ✅ | ❌ (app only) | ✅ | ❌ |
| Suggested questions | ✅ | ❌ (app only) | ✅ | ❌ |
| Candidate `country_code` / `city_name` | ✅ | ❌ (app only) | ✅ | ✅ (own values) |
| Other candidates' data | N/A (one at a time) | N/A | N/A | ❌ |
| Candidate `display_name` | ✅ | ❌ (app only) | ✅ | ✅ (own value) |

The candidate sees: question flow → location capture → submission
confirmation → personalized result page → optional app CTA.

### 14.1 Answer Leakage

With a 3-point ordinal scale and directional watchout copy, the owner can
often infer the candidate's approximate position from the briefing. This
is acceptable and intentional — the briefing is meant to inform the
owner's interview preparation.

## 15. Downstream Data: Prefill, Not Auto-Write

Unchanged from v1; see `flatmate_fit_check_v1.md` §7.

The Fit Check does NOT directly write to `house_norms` or
`preference_responses`. Owner answers are stored in fit-check tables and
made available as prefill data for downstream flows.

## 16. Data Model

### Required Tables

| Table | Purpose |
|---|---|
| `fit_check_drafts` | Owner scenario answers. In v2, `owner_user_id` is always set (NOT NULL) since authentication is required before saving. |
| `fit_check_share_tokens` | Public tokens for candidate access; FK to `fit_check_drafts` |
| `candidate_fit_submissions` | Candidate `display_name`, `country_code`, `city_name`, and scenario answers; FK to `fit_check_drafts` |
| `candidate_fit_briefings` | Generated briefing per submission; FK to `candidate_fit_submissions`; includes frozen owner answers snapshot |
| `email_notification_queue` | Tracks email notifications dispatched to owners on candidate submission (delivery status, retry state) |

### Relationships

```
fit_check_drafts (1)
  ├── fit_check_share_tokens (1:many, typically 1 active)
  ├── candidate_fit_submissions (1:many)
  │     ├── candidate_fit_briefings (1:1)
  │     └── email_notification_queue (1:1)
  └── homes (0:1, FK after home creation/attachment)
```

### v2-Specific Design Notes

- `fit_check_drafts.owner_user_id` is NOT NULL in the v2 flow. All
  drafts are created by authenticated owners.
- **Usage counter**: the owner's completed-run count MAY be derived from
  a count query on `fit_check_drafts WHERE owner_user_id = ?` or MAY
  use a separate `owner_usage_counter` table/column for performance.
  The implementation MUST be server-side and consistent.
- `email_notification_queue` tracks per-submission email dispatch:
  notification type, recipient, dispatch status, retry count, timestamps.
- Each answer is stored as `scenario_id` + `option_index` (0–2).
- `candidate_fit_briefings` stores a frozen snapshot of the owner's
  answers at comparison time, so briefings remain valid if the owner
  later changes answers.

## 17. Privacy and Lifecycle

### 17.1 Token Expiry
- `fit_check_share_tokens`: configurable TTL (default: 30 days)
- Expired tokens MUST return a clear localised "link expired" message

### 17.2 Token Revocation
- Authenticated owner MUST be able to revoke and regenerate the share
  token from the web dashboard or app
- Revoking MUST NOT delete existing submissions or briefings

### 17.3 Submission Limits
- Max submissions per share token: configurable (default: 20)
- One submission per anonymous session per token (duplicate rejection)
- Rate limiting MUST be applied to the submission endpoint

Backend-enforced anti-abuse requirements:
- Anonymous session identity MUST be server-issued (for example, an
  opaque cookie-backed session identifier)
- Duplicate detection MUST be defined against `(share_token,
  anonymous_session_id)`
- Duplicate submissions from the same anonymous session for the same
  token MUST be rejected with a structured duplicate error
- Rate limiting SHOULD consider token and short-window network abuse
  signals
- Expired, revoked, invalid, duplicate, rate-limited, and submission-cap
  failures MUST be distinguishable in backend error handling

The product MUST NOT rely on browser session state alone as the sole
anti-abuse control.

### 17.4 Data Retention
- In v2, there are no unclaimed drafts — all drafts are created by
  authenticated owners and linked to `auth.uid()` at creation time
- Drafts follow standard home data retention
- Candidate submissions linked to a deleted draft are cascade-deleted

### 17.5 Candidate Privacy
- No open-text answers (structured option_index only)
- Candidate location is limited to bounded fields: `country_code` and
  `city_name`
- Candidate submissions MUST NOT store device fingerprints or IP addresses
  beyond rate-limit window
- Rate-limiting metadata MUST NOT be persisted

### 17.6 Deletion
- Home deletion MUST cascade to all fit check data (drafts, tokens,
  submissions, briefings, email notification records)
- Account deletion MUST cascade to all fit check data owned by that user
- Candidates cannot self-delete in v2 (no identity to authenticate
  against). Deletion is via cascade or retention purge.

## 18. Anti-Discrimination

Unchanged from v1; see `flatmate_fit_check_v1.md` §13.

Scenario prompts, watchout copy, and suggested questions MUST stay
focused on household logistics and MUST NOT reference or proxy for
protected characteristics.

## 19. Non-Goals

Unchanged from v1; see `flatmate_fit_check_v1.md` §14.

The system MUST NOT verify truthfulness of responses, enforce decisions,
replace in-person interviews, guarantee compatibility, produce ranked
applicant lists, or write directly to `house_norms` or
`preference_responses`.

## 20. Success Criteria

### Product Metrics
- ≥ 80% completion rate (4 scenarios)
- ≥ 50% owners share link to at least one candidate
- ≥ 40% of gated owners (4th+ use) download the app
- Measurable reduction in drop-off vs v1 anonymous claim model
- Email open rate for candidate submission notifications

### Behavioural Indicators
- Owners use suggested questions in real interviews
- Owners report better clarity before committing
- Reduced post-move-in friction reports

## 21. Migration / Coexistence with v1

### 21.1 Existing v1 Users

v1 anonymous drafts with claim tokens continue to work for existing
users who created fit checks under the v1 model. These drafts retain
their existing claim and session token mechanics.

### 21.2 New Users

New users entering the fit check web flow receive the v2 experience
(web-authenticated, freemium gate). The v1 anonymous-web/app-claim flow
is not offered to new entrants.

### 21.3 API Coexistence

During the transition period, the backend MUST serve both v1 and v2 API
surfaces simultaneously:
- v1 RPCs (`fit_check_upsert_draft`, `fit_check_claim_draft`, etc.)
  remain live for existing v1 drafts
- v2 RPCs (`fit_check_create_run`, `fit_check_get_owner_dashboard`,
  etc.) serve new users
- Both API versions share the same underlying `fit_check_drafts` table
- v1 rows have nullable `owner_user_id` (anonymous until claimed);
  v2 rows have non-null `owner_user_id` (authenticated at creation)
- The web entry point determines which flow is used; there is no
  per-request version negotiation

### 21.4 Deprecation

v1 is deprecated for new entrants once v2 is stable and rolled out.

Existing v1 drafts are not retroactively migrated. They remain accessible
via the v1 claim flow until they expire per v1 retention rules (§12.4 of
v1). After all v1 drafts have expired or been claimed, v1 RPCs MAY be
decommissioned.

## 22. Invariant

The Flatmate Fit Check is an owner's pre-interview preparation tool.
It surfaces what to be aware of and what to ask — it does not score,
rank, or gatekeep. It MUST NOT become a mechanism for sorting or
filtering people.
