from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.contracts_ci.common import as_posix, in_scope_markdown_files, repo_root

REQUIRED_KEYS = [
    "Domain",
    "Capability",
    "Scope",
    "Artifact-Type",
    "Stability",
    "Status",
    "Version",
]

SCOPE_ALLOWED = {"backend", "frontend", "shared", "platform"}
ARTIFACT_ALLOWED = {"contract", "guide", "reference", "architecture", "adr", "process"}
STABILITY_ALLOWED = {"stable", "evolving", "ephemeral"}
STATUS_ALLOWED = {"draft", "active", "deprecated"}
VERSION_PATTERN = re.compile(r"^v\d+\.\d+(?:\.\d+)?$")


def parse_front_matter(text: str) -> Tuple[Dict[str, str], List[str]]:
    lines = text.splitlines()
    errors: List[str] = []
    if not lines or lines[0].strip() != "---":
        errors.append("missing front matter delimiter '---' at start of file")
        return {}, errors

    try:
        end_index = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        errors.append("unterminated front matter block (missing closing '---')")
        return {}, errors

    header_lines = lines[1:end_index]
    data: Dict[str, str] = {}
    for raw in header_lines:
        if not raw.strip():
            continue
        if ":" not in raw:
            errors.append(f"invalid header line (no colon): '{raw}'")
            continue
        key, value = raw.split(":", 1)
        data[key.strip()] = value.strip()
    return data, errors


def validate_header(path: Path, header: Dict[str, str]) -> List[str]:
    errors: List[str] = []

    for key in REQUIRED_KEYS:
        if key not in header or not header[key]:
            errors.append(f"missing key: {key}")

    scope = header.get("Scope")
    if scope and scope not in SCOPE_ALLOWED:
        errors.append(f"invalid Scope '{scope}' (allowed: {sorted(SCOPE_ALLOWED)})")

    artifact = header.get("Artifact-Type")
    if artifact and artifact not in ARTIFACT_ALLOWED:
        errors.append(f"invalid Artifact-Type '{artifact}' (allowed: {sorted(ARTIFACT_ALLOWED)})")

    stability = header.get("Stability")
    if stability and stability not in STABILITY_ALLOWED:
        errors.append(f"invalid Stability '{stability}' (allowed: {sorted(STABILITY_ALLOWED)})")

    status = header.get("Status")
    if status and status not in STATUS_ALLOWED:
        errors.append(f"invalid Status '{status}' (allowed: {sorted(STATUS_ALLOWED)})")

    version = header.get("Version")
    if version and not VERSION_PATTERN.match(version):
        errors.append("invalid Version format (expected vMAJOR.MINOR or vMAJOR.MINOR.PATCH)")

    return errors


def run(base: Path | None = None) -> Tuple[bool, int, List[str]]:
    root = base or repo_root()
    errors: List[str] = []
    scoped_files = in_scope_markdown_files(root)

    for path in scoped_files:
        rel = as_posix(path.relative_to(root))
        content = path.read_text(encoding="utf-8")
        header, parse_errors = parse_front_matter(content)
        if parse_errors:
            for err in parse_errors:
                errors.append(f"{rel}: {err}")
            continue

        validation_errors = validate_header(path, header)
        for err in validation_errors:
            errors.append(f"{rel}: {err}")

    ok = not errors
    return ok, len(scoped_files), errors


if __name__ == "__main__":
    success, count, errs = run()
    for err in errs:
        print(err)
    if success:
        print(f"Doc header check passed for {count} files.")
    else:
        print(f"Doc header check failed for {len(errs)} issue(s) across {count} files.")
    raise SystemExit(0 if success else 1)
