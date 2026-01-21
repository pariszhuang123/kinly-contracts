from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.contracts_ci.common import as_posix, in_scope_markdown_files, repo_root


LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:")


def is_external(target: str) -> bool:
    return target.startswith(EXTERNAL_PREFIXES) or "://" in target


def is_anchor(target: str) -> bool:
    return target.startswith("#")


def is_image(target: str) -> bool:
    lower = target.lower()
    return any(lower.endswith(ext) for ext in IMAGE_EXTENSIONS)


def run(base: Path | None = None) -> Tuple[bool, int, List[str]]:
    root = base or repo_root()
    scoped_files = in_scope_markdown_files(root)
    errors: List[str] = []

    for path in scoped_files:
        rel_path = as_posix(path.relative_to(root))
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for match in LINK_PATTERN.finditer(line):
                target_raw = match.group(1).strip()

                if is_external(target_raw) or is_anchor(target_raw):
                    continue

                target_no_fragment = target_raw.split("#", 1)[0]
                target_clean = target_no_fragment.split("?", 1)[0]

                if not target_clean:
                    continue

                if is_image(target_clean):
                    continue

                # Skip pure anchor references on the same page (e.g., #heading)
                if target_clean.startswith("#"):
                    continue

                candidate = (path.parent / Path(target_clean)).resolve()
                if not candidate.exists():
                    errors.append(f"{rel_path}:{line_no} -> broken link target '{target_raw}'")

    ok = not errors
    return ok, len(scoped_files), errors


if __name__ == "__main__":
    success, count, errs = run()
    for err in errs:
        print(err)
    if success:
        print(f"Link check passed for {count} files.")
    else:
        print(f"Link check failed for {len(errs)} issue(s) across {count} files.")
    raise SystemExit(0 if success else 1)
