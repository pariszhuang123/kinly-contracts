from __future__ import annotations

import re
from pathlib import Path
from typing import List, Set, Tuple

from tools.contracts_ci.common import in_scope_markdown_files, repo_root

REGISTRY_PATH = Path("registry/REGISTRY.md")
ITEM_PATTERN = re.compile(r"^\*\s+\*\*(?P<capability>.+?)\*\*\s+\((?P<version>.+?)\):\s+\[(?P<path>.+?)\]\(.+?\)$")


def check_registry_file(root: Path) -> Tuple[List[str], Set[str]]:
    registry_file = root / REGISTRY_PATH
    registered_paths: Set[str] = set()

    if not registry_file.exists():
        return [f"Registry file not found at {REGISTRY_PATH}"], registered_paths

    errors: List[str] = []
    content = registry_file.read_text(encoding="utf-8").splitlines()

    if "# Contracts Registry - Kinly" not in {line.strip() for line in content}:
        errors.append("Missing required top-level heading: '# Contracts Registry - Kinly'")

    current_domain = None
    for index, raw_line in enumerate(content, start=1):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("## Surface:"):
            current_domain = None
            continue
        if line.startswith("### Domain:"):
            current_domain = line.replace("### Domain:", "", 1).strip()
            continue
        if not line.startswith("*"):
            continue

        match = ITEM_PATTERN.match(line)
        if not match:
            errors.append(f"Line {index}: Invalid registry entry format: {line}")
            continue
        if not current_domain:
            errors.append(f"Line {index}: List item found outside of a Domain section")
            continue

        capability = match.group("capability")
        version = match.group("version")
        contract_path = match.group("path")

        if not re.fullmatch(r"[a-z0-9_]+", capability):
            errors.append(f"Line {index}: Invalid Capability '{capability}'. Must be lowercase letters, digits, underscore.")

        if not re.fullmatch(r"v[0-9]+(\.[0-9]+)*", version):
            errors.append(f"Line {index}: Invalid Version '{version}'.")

        full_contract_path = root / contract_path
        if not full_contract_path.exists():
            errors.append(f"Line {index}: Contract file not found: {contract_path}")
        elif not contract_path.startswith("contracts/"):
            errors.append(f"Line {index}: Contract path must start with 'contracts/': {contract_path}")
        else:
            registered_paths.add(contract_path)

    return errors, registered_paths


def check_drift(root: Path, registered_paths: Set[str]) -> List[str]:
    errors: List[str] = []
    registered_abs = {str((root / item).resolve()).lower() for item in registered_paths}
    contracts_dir = root / "contracts"

    for path in in_scope_markdown_files(root):
        if not path.is_relative_to(contracts_dir):
            continue
        path_abs = str(path.resolve()).lower()
        if path_abs not in registered_abs:
            rel_path = path.relative_to(root).as_posix()
            errors.append(f"Unregistered contract found: {rel_path}. Please add it to {REGISTRY_PATH}")
    return errors


def run(root: Path | None = None) -> Tuple[bool, int, List[str]]:
    base = root or repo_root()
    errors, registered_paths = check_registry_file(base)
    if not errors:
        errors.extend(check_drift(base, registered_paths))
    return len(errors) == 0, 1, errors


if __name__ == "__main__":
    ok, _count, errs = run()
    for err in errs:
        print(err)
    raise SystemExit(0 if ok else 1)
