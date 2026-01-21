from __future__ import annotations

import re
from pathlib import Path, PurePosixPath
from typing import Iterable, List, Set


IN_SCOPE_DIRS: List[str] = ["contracts", "architecture", "decisions", "platform"]
INCOMING_DIR = Path("_incoming")
ROOT_README = Path("README.md")
MARKDOWN_SUFFIX = ".md"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def as_posix(path: Path) -> str:
    return str(PurePosixPath(path))


def iter_markdown_files(base: Path) -> Iterable[Path]:
    for path in sorted(base.rglob(f"*{MARKDOWN_SUFFIX}")):
        if path.is_file():
            yield path


def in_scope_markdown_files(base: Path) -> List[Path]:
    root = Path(base)
    scoped: List[Path] = []
    for path in iter_markdown_files(root):
        rel = path.relative_to(root)
        if rel.parts and rel.parts[0] in IN_SCOPE_DIRS and not rel.is_relative_to(INCOMING_DIR):
            scoped.append(path)
    return scoped


def strip_version_suffix(stem: str) -> str:
    cleaned = re.sub(r"_v\d+(?:_\d+)*$", "", stem)
    return cleaned


def parse_version_from_stem(stem: str) -> str:
    match = re.search(r"_v(\d+)(?:_(\d+))?(?:_(\d+))?$", stem)
    if not match:
        return "v1.0"
    parts = [int(g) for g in match.groups(default="0")]
    major, minor, patch = parts
    if patch:
        return f"v{major}.{minor}.{patch}"
    return f"v{major}.{minor}"


def find_readme_paths(base: Path) -> Set[Path]:
    return {p for p in iter_markdown_files(base) if p.name.lower() == "readme.md"}
