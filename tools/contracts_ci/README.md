## Contracts Guardrails

This suite enforces the kinly-contracts repo guardrails locally and in CI.

### Checks
- Doc headers: YAML front matter required for contracts/architecture/decisions/platform markdown; enforces key/value constraints.
- Path integrity: contracts live only under the allowed kinly paths.
- Internal links: validates relative markdown links (excluding external/image/anchor targets).
- Index integrity: every in-scope doc is referenced from `INDEX.md` (excluding `_incoming/**` and any `README.md`).
- Registry validity: generated contract registry format and coverage.
- Alignment: deterministic cross-document relationship validation.
- Wiki coverage: generated wiki pages must cover every canonical doc.

### Generated artifacts
- `registry/REGISTRY.md`
- `wiki/home.md`
- `wiki/domains/*.md`
- `wiki/capabilities/*.md`
- `wiki/reports/alignment_report.md`
- `wiki/reports/change_digest.md`

If generated artifacts change during `run_checks.py`, the run fails so the regenerated files can be reviewed and committed.

### Usage
Run all checks locally:
```
python tools/contracts_ci/run_checks.py
```

Expected exit codes: `0` when all checks pass, `1` when any check fails. Output lists failures per check for quick triage.
