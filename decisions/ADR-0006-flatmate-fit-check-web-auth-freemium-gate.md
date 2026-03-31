---
Domain: Homes
Capability: Flatmate Fit Check
Scope: platform
Artifact-Type: adr
Stability: stable
Status: active
Version: v1.0
---

# ADR-0006: Flatmate Fit Check — Web Auth + Freemium Gate

## Status
Accepted

## Context
The Flatmate Fit Check v1 uses an anonymous-web → app-claim model. The owner completes the fit check anonymously on web, receives a claim token, and must download the app to claim results. This model has several problems:
- High drop-off: owners who never install the app lose their results
- No persistent identity on web means results can't be saved across sessions
- No way to notify owners when candidates submit (no email on file)
- No growth loop: the web experience is a dead end that doesn't convert

The fit check is Kinly's primary acquisition wedge. The current model optimizes for app purity at the cost of conversion.

## Decision
Move to a web-authenticated freemium gate model:

1. **Web authentication required to save** — Owner may answer scenarios anonymously but signs in via Supabase OAuth (Google/Apple) on web before results are saved. Auth is prompted after the owner completes the 4 questions, preserving low-friction entry while ensuring persistent identity for notifications and cross-session access.

2. **3-use freemium gate** — First 3 completed fit check runs are fully accessible on web. On the 4th, the owner is prompted to download the app. Prior runs remain web-accessible.

3. **Auto home bootstrap in app** — When a fit-check-funnel user first logs into the app, a home is automatically created (or existing home joined). This removes friction from the app onboarding path.

4. **Email notifications** — Owner receives an email each time a candidate submits. This keeps the owner engaged even when they haven't opened the app.

5. **v2 contract line** — This is a new major version, not an amendment to v1. The changes are too fundamental to retrofit.

## Consequences

### Positive
- Persistent web identity reduces drop-off
- Email notifications create a re-engagement loop
- Freemium gate provides clear value demonstration before app download
- Auto-home bootstrap reduces app onboarding friction
- Web dashboard gives owners immediate value

### Negative
- Requires web authentication infrastructure (Supabase OAuth on web)
- More complex surface area (web dashboard + app)
- Two contract versions to maintain during transition
- Auto-home creation is a deviation from the normal Homes flow

### Risks
- Identity mismatch if user signs in with different providers on web vs app. Mitigated by: backend uses auth.uid(), not email matching.
- Ambiguous "use" counting. Mitigated by: clearly defined as "newly created owner-completed fit check run."
- Auto-home creation could confuse users with existing homes. Mitigated by: only triggers via fit-check funnel, not platform-wide.
- Email notification failures could block submissions. Mitigated by: async/fire-and-forget, candidate submission never depends on email.

## Alternatives Considered

### Keep v1 anonymous model + improve claim UX
Rejected because the fundamental problem is that anonymous web has no persistent identity — improving the claim UX doesn't solve session loss, email notifications, or web dashboard access.

### Full web app (no app gate)
Rejected because the business goal is app downloads for retention and engagement. The freemium gate strikes a balance between web value and app conversion.

### Magic link auth instead of OAuth
Rejected because Kinly already uses Supabase OAuth (Google/Apple) in the app. Using the same auth system on web ensures identity continuity.

## References
- [Flatmate Fit Check v1](../contracts/product/kinly/shared/flatmate_fit_check_v1.md)
- [Flatmate Fit Check v2](../contracts/product/kinly/shared/flatmate_fit_check_v2.md)
- [Flatmate Fit Check API v1](../contracts/api/kinly/homes/flatmate_fit_check_api_v1.md)
- [Flatmate Fit Check API v2](../contracts/api/kinly/homes/flatmate_fit_check_api_v2.md)
