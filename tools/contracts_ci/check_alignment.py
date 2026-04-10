from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from tools.contracts_ci.alignment import analyze_documents
from tools.contracts_ci.metadata import load_documents


def run(base: Path | None = None) -> Tuple[bool, int, List[str]]:
    root = base or Path(__file__).resolve().parents[2]
    documents = load_documents(root)
    issues = analyze_documents(documents)
    errors = [issue.message for issue in issues if issue.severity == "error"]
    return len(errors) == 0, len(documents), errors


if __name__ == "__main__":
    ok, _count, errs = run()
    for err in errs:
        print(err)
    raise SystemExit(0 if ok else 1)
