from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Set, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.contracts_ci.common import as_posix, in_scope_markdown_files, repo_root

LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:")


def is_external(target: str) -> bool:
    return target.startswith(EXTERNAL_PREFIXES) or "://" in target


def is_image(target: str) -> bool:
    lower = target.lower()
    return any(lower.endswith(ext) for ext in IMAGE_EXTENSIONS)


def collect_required_docs(root: Path) -> Set[str]:
    required: Set[str] = set()
    for path in in_scope_markdown_files(root):
        rel = path.relative_to(root)
        if rel.name.lower() == "readme.md":
            continue
        required.add(as_posix(rel))
    return required


def collect_index_targets(index_path: Path, root: Path) -> Set[str]:
    targets: Set[str] = set()
    content = index_path.read_text(encoding="utf-8")
    for match in LINK_PATTERN.finditer(content):
        raw_target = match.group(1).strip()
        if not raw_target or raw_target.startswith("#") or is_external(raw_target):
            continue
        cleaned = raw_target.split("#", 1)[0].split("?", 1)[0]
        if not cleaned or is_image(cleaned):
            continue

        candidate = (index_path.parent / Path(cleaned)).resolve()
        try:
            rel = candidate.relative_to(root)
        except ValueError:
            # Target outside repo root; ignore as external
            continue

        targets.add(as_posix(rel))
    return targets


def run(base: Path | None = None) -> Tuple[bool, int, List[str]]:
    root = base or repo_root()
    errors: List[str] = []
    index_path = root / "INDEX.md"

    if not index_path.exists():
        errors.append("Missing INDEX.md at repo root.")
        return False, 0, errors

    required_docs = collect_required_docs(root)
    indexed_docs = collect_index_targets(index_path, root)

    missing = sorted(required_docs - indexed_docs)
    for doc in missing:
        errors.append(f"{doc} is not referenced in INDEX.md")

    ok = not errors
    return ok, len(required_docs), errors


if __name__ == "__main__":
    success, count, errs = run()
    for err in errs:
        print(err)
    if success:
        print(f"Index check passed for {count} documents.")
    else:
        print(f"Index check failed for {len(errs)} issue(s) across {count} documents.")
    raise SystemExit(0 if success else 1)
