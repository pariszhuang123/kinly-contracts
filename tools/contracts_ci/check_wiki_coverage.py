from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

from tools.contracts_ci.generate_wiki import WIKI_ROOT
from tools.contracts_ci.metadata import load_documents, normalize_token


def run(base: Path | None = None) -> Tuple[bool, int, List[str]]:
    root = base or Path(__file__).resolve().parents[2]
    documents = load_documents(root)
    errors: List[str] = []

    home_path = root / WIKI_ROOT / "home.md"
    if not home_path.exists():
        errors.append(f"Missing generated wiki home page: {WIKI_ROOT.as_posix()}/home.md")

    home_content = home_path.read_text(encoding="utf-8") if home_path.exists() else ""
    domain_cache: Dict[str, str] = {}
    capability_cache: Dict[str, str] = {}

    for doc in documents:
        domain_slug = normalize_token(doc.domain or "unknown")
        capability_slug = doc.canonical_id

        domain_path = root / WIKI_ROOT / "domains" / f"{domain_slug}.md"
        capability_path = root / WIKI_ROOT / "capabilities" / f"{capability_slug}.md"

        if not domain_path.exists():
            errors.append(f"Missing wiki domain page for '{domain_slug}': {domain_path.relative_to(root).as_posix()}")
        if not capability_path.exists():
            errors.append(f"Missing wiki capability page for '{capability_slug}': {capability_path.relative_to(root).as_posix()}")

        if domain_path.exists():
            content = domain_cache.setdefault(domain_path.as_posix(), domain_path.read_text(encoding="utf-8"))
            if doc.rel_path not in content:
                errors.append(f"{domain_path.relative_to(root).as_posix()} does not reference {doc.rel_path}")

        if capability_path.exists():
            content = capability_cache.setdefault(capability_path.as_posix(), capability_path.read_text(encoding="utf-8"))
            if doc.rel_path not in content:
                errors.append(f"{capability_path.relative_to(root).as_posix()} does not reference {doc.rel_path}")

        if home_content and f"domains/{domain_slug}" not in home_content:
            errors.append(f"{WIKI_ROOT.as_posix()}/home.md does not link to domain '{domain_slug}'")

    return len(errors) == 0, len(documents), errors


if __name__ == "__main__":
    ok, _count, errs = run()
    for err in errs:
        print(err)
    raise SystemExit(0 if ok else 1)
