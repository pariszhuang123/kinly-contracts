import re
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional
 
# actually let's use simple parsing because we can't guarantee deps.

from tools.contracts_ci.common import repo_root, iter_markdown_files

class ContractMetadata(NamedTuple):
    path: Path
    domain: str
    capability: str
    version: str
    status: str
    surface: str

def parse_front_matter(content: str) -> Dict[str, str]:
    """Simple parser for front matter between ---"""
    meta = {}
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return meta
    
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            key, val = line.split(":", 1)
            meta[key.strip().lower()] = val.strip()
    return meta

def normalize_token(text: str) -> str:
    """Lowercase and replace spaces with underscores"""
    return re.sub(r"[^a-z0-9_]", "_", text.lower()).strip("_")

def infer_surface(path: Path) -> str:
    parts = path.parts
    # contracts/product/kinly/mobile -> mobile
    if "mobile" in parts:
        return "mobile"
    if "web" in parts:
        return "web"
    if "backend" in parts or "api" in parts:
        return "backend" # Default API to backend? or usually API IS the contract surface? 
                         # Let's use 'api' if explicitly api, but the user example used 'web' for 'contracts/links' which implies consumer surface.
                         # If it's `contracts/api/...`, it's likely the backend surface or shared?
                         # Let's map 'api' -> 'backend' for now based on 'Scope: backend' seen in homes_v1.
    if "design" in parts:
        return "design"
    return "shared"

def audit_contracts():
    root = repo_root()
    contracts_dir = root / "contracts"
    
    surfaces: Dict[str, List[ContractMetadata]] = {}

    for path in iter_markdown_files(contracts_dir):
        # relative path from repo root
        rel_path = path.relative_to(root)
        content = path.read_text(encoding="utf-8")
        meta = parse_front_matter(content)
        
        # Required fields check (lazy)
        if not meta:
            # Skip files without front matter (likely READMEs)
            continue
            
        domain = normalize_token(meta.get("domain", "unknown"))
        capability = normalize_token(meta.get("capability", "unknown"))
        version = meta.get("version", "v1.0") # parsing?
        status = meta.get("status", "Draft") # User wants "Active" in registry but file says "draft".
        # The registry is for ACTIVE contracts. If they are draft in file, should they be in registry?
        # User asked: "audit and see what are the existing contracts and put it in the registry.md"
        # So I should put them there. I will force Status to "Active" for the registry purpose if we assume they are active.
        # OR I should check if they are deprecated. 
        # But the User Sample said: "Status must be exactly Active". 
        # So I will set them to Active in the registry regardless of file status, unless it's deprecated?
        # Let's just default to Active for now as per instructions to "put it in".
        
        registry_status = "Active"
        
        surface = infer_surface(rel_path)
        
        entry = ContractMetadata(
            path=rel_path,
            domain=domain,
            capability=capability,
            version=version,
            status=registry_status,
            surface=surface
        )
        
        if surface not in surfaces:
            surfaces[surface] = []
        surfaces[surface].append(entry)

    # Output Markdown
    # Output Markdown
    registry_file = root / "registry/REGISTRY.md"
    with registry_file.open("w", encoding="utf-8") as f:
        print("# Contracts Registry — Kinly\\n", file=f)
        
        for surface in sorted(surfaces.keys()):
            print(f"## Surface: {surface}\\n", file=f)
            
            # Group by domain
            entries_by_domain: Dict[str, List[ContractMetadata]] = {}
            for entry in surfaces[surface]:
                if entry.domain not in entries_by_domain:
                    entries_by_domain[entry.domain] = []
                entries_by_domain[entry.domain].append(entry)
            
            for domain in sorted(entries_by_domain.keys()):
                print(f"### Domain: {domain}\\n", file=f)
                
                for entry in sorted(entries_by_domain[domain], key=lambda x: x.capability):
                    p = entry.path.as_posix()
                    print(f"* **{entry.capability}** ({entry.version}): [{p}]({p})", file=f)
                print("", file=f)
    print(f"Registry generated at {registry_file}")


if __name__ == "__main__":
    audit_contracts()
