from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.contracts_ci.common import as_posix, in_scope_markdown_files, repo_root
from tools.contracts_ci.metadata import LIST_RELATIONSHIP_KEYS, RELATIONSHIP_KEYS, normalize_reference, parse_front_matter

REQUIRED_KEYS = [
    "Domain",
    "Capability",
    "Scope",
    "Artifact-Type",
    "Stability",
    "Status",
    "Version",
]

OPTIONAL_KEYS = set(RELATIONSHIP_KEYS)
SCOPE_ALLOWED = {"backend", "frontend", "shared", "platform"}
ARTIFACT_ALLOWED = {"contract", "guide", "reference", "architecture", "adr", "process"}
STABILITY_ALLOWED = {"stable", "evolving", "ephemeral"}
STATUS_ALLOWED = {"draft", "active", "deprecated"}
CANONICAL_ID_PATTERN = re.compile(r"^[a-z0-9_]+$")
VERSION_PATTERN = re.compile(r"^v\d+\.\d+(?:\.\d+)?$")


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

    canonical_id = header.get("Canonical-Id")
    if canonical_id and not CANONICAL_ID_PATTERN.match(canonical_id):
        errors.append("invalid Canonical-Id format (expected lowercase letters, digits, underscores)")

    for key in LIST_RELATIONSHIP_KEYS:
        raw_value = header.get(key)
        if not raw_value:
            continue
        values = [item for item in raw_value.strip("[]").split(",") if item.strip()]
        if not values:
            errors.append(f"{key} is present but empty")
            continue
        normalized_values = [normalize_reference(item.strip()) for item in values]
        if any(not value for value in normalized_values):
            errors.append(f"{key} contains an empty relationship target")

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
