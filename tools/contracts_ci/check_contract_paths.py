from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.contracts_ci.common import as_posix, in_scope_markdown_files, repo_root


ALLOWED_CONTRACT_PREFIXES = [
    Path("contracts/api/kinly"),
    Path("contracts/product/kinly/shared"),
    Path("contracts/product/kinly/mobile"),
    Path("contracts/product/kinly/web"),
    Path("contracts/design/tokens/kinly"),
    Path("contracts/design/copy/kinly"),
    Path("contracts/design/reference/kinly"),
]

ALWAYS_ALLOWED_TOP = {"architecture", "decisions", "platform"}


def run(base: Path | None = None) -> Tuple[bool, int, List[str]]:
    root = base or repo_root()
    scoped_files = in_scope_markdown_files(root)
    errors: List[str] = []

    for path in scoped_files:
        rel = path.relative_to(root)
        top = rel.parts[0]

        if top in ALWAYS_ALLOWED_TOP:
            continue

        if top != "contracts":
            continue

        if any(rel.is_relative_to(prefix) for prefix in ALLOWED_CONTRACT_PREFIXES):
            continue

        allowed_paths = [as_posix(p) for p in ALLOWED_CONTRACT_PREFIXES]
        errors.append(
            f"{as_posix(rel)} is outside allowed contract paths. Allowed prefixes: {', '.join(allowed_paths)}"
        )

    ok = not errors
    return ok, len(scoped_files), errors


if __name__ == "__main__":
    success, count, errs = run()
    for err in errs:
        print(err)
    if success:
        print(f"Contract path check passed for {count} files.")
    else:
        print(f"Contract path check failed for {len(errs)} issue(s) across {count} files.")
    raise SystemExit(0 if success else 1)
