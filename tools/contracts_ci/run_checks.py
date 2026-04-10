from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable, List, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.contracts_ci import (
    check_alignment,
    check_contract_paths,
    check_doc_headers,
    check_index,
    check_links,
    check_registry,
    check_wiki_coverage,
    generate_registry,
    generate_wiki,
)
from tools.contracts_ci.common import as_posix, in_scope_markdown_files, repo_root

CheckResult = Tuple[str, bool, int, List[str]]


def run_check(
    label: str, func: Callable[[Path | None], Tuple[bool, int, List[str]]], root: Path
) -> CheckResult:
    ok, count, errors = func(root)
    print(f"\\n=== {label} ===")
    if ok:
        print(f"PASS ({count} files scanned)")
    else:
        print(f"FAIL ({len(errors)} issue(s))")
        for err in errors:
            print(f"- {err}")
    return label, ok, count, errors


def main() -> int:
    root = repo_root()
    print(f"Running contracts guardrails from {as_posix(root)}")

    generated_changes: List[str] = []
    print("Regenerating derived artifacts...")
    generated_changes.extend(generate_registry.audit_contracts(root))
    generated_changes.extend(generate_wiki.generate_wiki(root))

    checks: List[Tuple[str, Callable[[Path | None], Tuple[bool, int, List[str]]]]] = [
        ("Doc headers", check_doc_headers.run),
        ("Path integrity", check_contract_paths.run),
        ("Internal links", check_links.run),
        ("Index integrity", check_index.run),
        ("Registry validity", check_registry.run),
        ("Alignment", check_alignment.run),
        ("Wiki coverage", check_wiki_coverage.run),
    ]

    results: List[CheckResult] = []
    for label, func in checks:
        results.append(run_check(label, func, root))

    total_files = len(in_scope_markdown_files(root))
    failures = {label: len(errs) for label, ok, _count, errs in results if not ok}

    if generated_changes:
        failures["Generated artifacts"] = len(generated_changes)

    print("\\n=== Summary ===")
    print(f"In-scope markdown files scanned: {total_files}")
    for label, ok, _count, errs in results:
        status = "ok" if ok else f"{len(errs)} error(s)"
        print(f"- {label}: {status}")
    if generated_changes:
        print(f"- Generated artifacts: {len(generated_changes)} updated")
        for path in generated_changes:
            print(f"  - {path}")
    else:
        print("- Generated artifacts: ok")

    if failures:
        if generated_changes:
            print("\\nGenerated artifacts changed during the run. Commit regenerated files and rerun checks.")
        print("\\nGuardrails failed.")
        return 1

    print("\\nAll guardrails passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
