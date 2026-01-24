from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple, Set

from tools.contracts_ci.common import repo_root, in_scope_markdown_files

REGISTRY_PATH = Path("registry/REGISTRY.md")

def check_registry_file(root: Path) -> Tuple[List[str], Set[str]]:
    """
    Validates the registry/REGISTRY.md file format and contents.
    Returns a tuple of (errors, set_of_registered_paths).
    """
    registry_file = root / REGISTRY_PATH
    registered_paths = set()
    
    if not registry_file.exists():
        return [f"Registry file not found at {REGISTRY_PATH}"], registered_paths

    errors = []
    content = registry_file.read_text(encoding="utf-8").splitlines()

    # 1. Check top-level heading
    found_header = False
    for line in content:
        if line.strip().startswith("# Contracts Registry"):
            found_header = True
            break
            
    if not found_header:
        errors.append("Missing required top-level heading: '# Contracts Registry — Kinly'")

    # Parsing state
    current_surface = None
    current_domain = None
    
    # Regex for list item: * **capability** (version): [path](path)
    # Allows for some whitespace flex
    item_regex = re.compile(r"^\*\s+\*\*(?P<capability>.+?)\*\*\s+\((?P<version>.+?)\):\s+\[(?P<path>.+?)\]\(.+?\)$")

    for i, line in enumerate(content):
        line = line.strip()
        if not line:
            continue

        # Headers
        if line.startswith("## Surface:"):
            current_surface = line.replace("## Surface:", "").strip()
            current_domain = None
            continue
            
        if line.startswith("### Domain:"):
            current_domain = line.replace("### Domain:", "").strip()
            continue

        # List Item
        match = item_regex.match(line)
        if match:
            line_num = i + 1
            capability = match.group("capability")
            version = match.group("version")
            contract_path = match.group("path")
            
            if not current_domain:
                 errors.append(f"Line {line_num}: List item found outside of a Domain section")
                 continue

            # Validate Capability
            if not re.match(r"^[a-z0-9_]+$", capability):
                errors.append(f"Line {line_num}: Invalid Capability '{capability}'. Must be lowercase letters, digits, underscore.")
            
            # Validate Contract Path
            full_contract_path = root / contract_path
            if not full_contract_path.exists():
                 errors.append(f"Line {line_num}: Contract file not found: {contract_path}")
            elif not contract_path.startswith("contracts/"):
                 errors.append(f"Line {line_num}: Contract path must start with 'contracts/': {contract_path}")
            else:
                registered_paths.add(contract_path)

            # Validate Version
            if not re.match(r"^v[0-9]+(\.[0-9]+)*$", version):
                errors.append(f"Line {line_num}: Invalid Version '{version}'.")
        else:
            if line.startswith("*"):
                print(f"DEBUG: Line {i+1} failed to match regex: {line!r}")

    return errors, registered_paths


def check_drift(root: Path, registered_paths: Set[str]) -> List[str]:
    """
    Checks if there are any markdown files in contracts/ that are NOT in the registry.
    """
    errors = []
    # common.in_scope_markdown_files returns absolute paths.
    all_files = in_scope_markdown_files(root)
    
    # Normalize registered paths to absolute lowercase strings for Windows compatibility
    registered_abs = { str((root / p).resolve()).lower() for p in registered_paths }
    print(f"DEBUG: Registered count: {len(registered_abs)}")
    if registered_abs:
        print(f"DEBUG: Sample registered: {list(registered_abs)[0]}")
    
    contracts_dir = root / "contracts"
    
    for path in all_files:
        # Check if it is inside contracts/
        if not path.is_relative_to(contracts_dir):
            continue
        
        path_abs = str(path.resolve()).lower()
        
        if path_abs not in registered_abs:
            rel_path = path.relative_to(root).as_posix()
            errors.append(f"Unregistered contract found: {rel_path}. Please add it to {REGISTRY_PATH}")
            
    return errors


def run(root: Path | None = None) -> Tuple[bool, int, List[str]]:
    if root is None:
        root = repo_root()
    
    errors, registered_paths = check_registry_file(root)
    
    if not errors:
        drift_errors = check_drift(root, registered_paths)
        errors.extend(drift_errors)
        
    count = 1 
    
    return len(errors) == 0, count, errors

if __name__ == "__main__":
    _, _, errs = run()
    for e in errs:
        print(e)
