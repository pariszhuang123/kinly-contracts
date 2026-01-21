# Definition of Done (DoD) — Kinly Web

A change is considered **done** only when all applicable items below are satisfied.

DoD exists to prevent incomplete, unsafe, or undocumented behavior from shipping.

---

## 1. Contract Alignment

- [ ] Relevant contract identified
- [ ] Contract updated if behavior changed
- [ ] Contract version bumped if semantics changed
- [ ] `contracts/contracts_registry.md` updated
- [ ] If no contract change: explicit confirmation recorded

---

## 2. Implementation

- [ ] Route / component implemented as specified
- [ ] Edge Function implemented (if required)
- [ ] RPC exists and matches expected schema
- [ ] No direct database writes
- [ ] No business logic in Web UI or Edge Function

---

## 3. Safety & Privacy

- [ ] Public pages expose allow-listed fields only
- [ ] No private identifiers rendered
- [ ] No auto-deep-linking on page load
- [ ] Safe fallback exists for all failure cases
- [ ] Data minimization respected

---

## 4. Routing & Fallback

- [ ] `/fallback` path works
- [ ] Invalid routes do not dead-end
- [ ] `next` params sanitized (internal paths only)
- [ ] Store CTAs visible where appropriate
- [ ] Unsupported regions gated correctly

---

## 5. Tests

- [ ] Route tests updated or added
- [ ] Edge Function tests updated or added (if applicable)
- [ ] Public page snapshot tests updated
- [ ] Fallback paths covered
- [ ] Execution agents passing

---

## 6. Observability

- [ ] Error states return reason codes
- [ ] No sensitive data in logs
- [ ] Logs are actionable and readable

---

## 7. Environment & Deployment

- [ ] `.env.example` updated if variables changed
- [ ] No secrets committed
- [ ] Vercel preview tested
- [ ] Production behavior verified (or explicitly deferred)

---

## 8. Documentation

- [ ] README.md updated if user-facing behavior changed
- [ ] Docs updated if operational behavior changed
- [ ] ADR added if architectural decision was made

---

## Final Check

- [ ] I can explain this change in one sentence
- [ ] I know who owns the behavior
- [ ] I know how this fails safely

If any box is unchecked, the change is **not done**.
