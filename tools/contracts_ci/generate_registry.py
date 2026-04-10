from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from tools.contracts_ci.metadata import ContractDocument, load_documents, normalize_token

REGISTRY_PATH = Path("registry/REGISTRY.md")


def infer_surface(doc: ContractDocument) -> str:
    rel = doc.rel_path
    if "/mobile/" in rel:
        return "mobile"
    if "/web/" in rel:
        return "web"
    if rel.startswith("contracts/api/"):
        return "backend"
    if rel.startswith("contracts/design/"):
        return "design"
    if doc.scope == "platform":
        return "platform"
    return doc.scope or "shared"


def render_registry(documents: List[ContractDocument]) -> str:
    surfaces: Dict[str, Dict[str, List[ContractDocument]]] = defaultdict(lambda: defaultdict(list))

    for doc in documents:
        if not doc.rel_path.startswith("contracts/"):
            continue
        surface = infer_surface(doc)
        domain = normalize_token(doc.domain or "unknown")
        surfaces[surface][domain].append(doc)

    lines: List[str] = ["# Contracts Registry - Kinly", ""]
    for surface in sorted(surfaces):
        lines.append(f"## Surface: {surface}")
        lines.append("")
        for domain in sorted(surfaces[surface]):
            lines.append(f"### Domain: {domain}")
            lines.append("")
            for doc in sorted(surfaces[surface][domain], key=lambda item: (normalize_token(item.capability), item.version, item.rel_path)):
                capability = normalize_token(doc.capability or doc.filename_family or "unknown")
                lines.append(f"* **{capability}** ({doc.version}): [{doc.rel_path}]({doc.rel_path})")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def audit_contracts(root: Path | None = None) -> List[str]:
    base = root or Path(__file__).resolve().parents[2]
    registry_file = base / REGISTRY_PATH
    rendered = render_registry(load_documents(base))
    previous = registry_file.read_text(encoding="utf-8") if registry_file.exists() else ""
    changed: List[str] = []
    if previous != rendered:
        registry_file.parent.mkdir(parents=True, exist_ok=True)
        registry_file.write_text(rendered, encoding="utf-8")
        changed.append(REGISTRY_PATH.as_posix())
    return changed


if __name__ == "__main__":
    changed = audit_contracts()
    if changed:
        print("Updated generated files:")
        for path in changed:
            print(f"- {path}")
    else:
        print("Registry already up to date.")
