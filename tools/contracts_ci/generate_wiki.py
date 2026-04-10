from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from tools.contracts_ci.alignment import analyze_documents, render_alignment_report
from tools.contracts_ci.metadata import ContractDocument, load_documents, normalize_token, relationship_targets

WIKI_ROOT = Path("wiki")


def wiki_link(label: str, target: str) -> str:
    return f"[[{target}|{label}]]"


def capability_slug(doc: ContractDocument) -> str:
    return doc.canonical_id


def domain_slug(domain: str) -> str:
    return normalize_token(domain or "unknown")


def group_by_domain(documents: Sequence[ContractDocument]) -> Dict[str, List[ContractDocument]]:
    grouped: Dict[str, List[ContractDocument]] = defaultdict(list)
    for doc in documents:
        grouped[domain_slug(doc.domain)].append(doc)
    return grouped


def group_by_capability(documents: Sequence[ContractDocument]) -> Dict[str, List[ContractDocument]]:
    grouped: Dict[str, List[ContractDocument]] = defaultdict(list)
    for doc in documents:
        grouped[capability_slug(doc)].append(doc)
    return grouped


def render_home(documents: Sequence[ContractDocument], issues: Sequence, domain_groups: Dict[str, List[ContractDocument]], capability_groups: Dict[str, List[ContractDocument]]) -> str:
    active_docs = [doc for doc in documents if doc.status == "active"]
    draft_docs = [doc for doc in documents if doc.status == "draft"]
    deprecated_docs = [doc for doc in documents if doc.status == "deprecated"]
    recently_changed = sorted(documents, key=lambda item: item.modified_ts, reverse=True)[:12]

    lines: List[str] = [
        "# Kinly Living Wiki",
        "",
        "This wiki is generated from canonical docs in `contracts/**`, `architecture/**`, `decisions/**`, and `platform/**`.",
        "",
        "## Snapshot",
        "",
        f"- Canonical docs: {len(documents)}",
        f"- Domains: {len(domain_groups)}",
        f"- Capability pages: {len(capability_groups)}",
        f"- Active docs: {len(active_docs)}",
        f"- Draft docs: {len(draft_docs)}",
        f"- Deprecated docs: {len(deprecated_docs)}",
        f"- Alignment issues: {len(issues)}",
        "",
        "## Read First",
        "",
        f"- Alignment report: {wiki_link('Alignment Report', 'reports/alignment_report')}",
        f"- Change digest: {wiki_link('Change Digest', 'reports/change_digest')}",
        "",
        "## Domains",
        "",
    ]

    for slug in sorted(domain_groups):
        docs = domain_groups[slug]
        active_count = sum(1 for doc in docs if doc.status == "active")
        lines.append(f"- {wiki_link(slug, f'domains/{slug}')} ({len(docs)} docs, {active_count} active)")

    lines.extend(["", "## Recently Changed Areas", ""])
    for doc in recently_changed:
        timestamp = datetime.fromtimestamp(doc.modified_ts, tz=timezone.utc).strftime("%Y-%m-%d")
        lines.append(f"- {timestamp}: {doc.title} -> {wiki_link(capability_slug(doc), f'capabilities/{capability_slug(doc)}')} ({doc.rel_path})")

    lines.extend(["", "## Key Architecture And Decision Docs", ""])
    for doc in documents:
        if doc.rel_path.startswith("architecture/") or doc.rel_path.startswith("decisions/"):
            lines.append(f"- [{doc.title}](../{doc.rel_path})")

    return "\n".join(lines).rstrip() + "\n"


def render_domain_page(slug: str, docs: Sequence[ContractDocument]) -> str:
    capability_index: Dict[str, List[ContractDocument]] = defaultdict(list)
    for doc in docs:
        capability_index[capability_slug(doc)].append(doc)

    lines: List[str] = [
        f"# Domain: {slug}",
        "",
        f"- Docs in domain: {len(docs)}",
        f"- Active docs: {sum(1 for doc in docs if doc.status == 'active')}",
        "",
        "## Capabilities",
        "",
    ]

    for cap_slug in sorted(capability_index):
        cap_docs = sorted(capability_index[cap_slug], key=lambda item: (item.version, item.rel_path))
        latest = cap_docs[-1]
        lines.append(f"- {wiki_link(cap_slug, f'../capabilities/{cap_slug}')} -> latest {latest.version} ({latest.status})")

    lines.extend(["", "## Source Docs", ""])
    for doc in sorted(docs, key=lambda item: (item.capability.lower(), item.version, item.rel_path)):
        lines.append(f"- [{doc.title}](../../{doc.rel_path})")

    return "\n".join(lines).rstrip() + "\n"


def render_capability_page(slug: str, docs: Sequence[ContractDocument], by_path: Dict[str, ContractDocument], by_canonical: Dict[str, List[ContractDocument]]) -> str:
    ordered_docs = sorted(docs, key=lambda item: (item.version, item.rel_path))
    latest = ordered_docs[-1]
    related: List[ContractDocument] = []
    seen = {doc.rel_path for doc in ordered_docs}
    for doc in ordered_docs:
        for target in relationship_targets(doc):
            if target.endswith(".md"):
                candidate = by_path.get(target)
                if candidate and candidate.rel_path not in seen:
                    related.append(candidate)
                    seen.add(candidate.rel_path)
            else:
                for candidate in by_canonical.get(target, []):
                    if candidate.rel_path not in seen:
                        related.append(candidate)
                        seen.add(candidate.rel_path)

    lines: List[str] = [
        f"# Capability: {slug}",
        "",
        f"- Canonical-Id: `{slug}`",
        f"- Latest doc: [{latest.title}](../../{latest.rel_path})",
        f"- Domain: {wiki_link(domain_slug(latest.domain), f'../domains/{domain_slug(latest.domain)}')}",
        "",
        "## Versions",
        "",
    ]

    for doc in ordered_docs:
        lines.append(f"- `{doc.version}` `{doc.status}` [{doc.title}](../../{doc.rel_path})")

    lines.extend(["", "## Relationships", ""])
    if related:
        for doc in sorted(related, key=lambda item: item.rel_path):
            lines.append(f"- [{doc.title}](../../{doc.rel_path})")
    else:
        lines.append("- No explicit related docs yet.")

    lines.extend(["", "## Source Docs", ""])
    for doc in ordered_docs:
        lines.append(f"- [{doc.title}](../../{doc.rel_path})")

    return "\n".join(lines).rstrip() + "\n"


def render_change_digest(documents: Sequence[ContractDocument]) -> str:
    recent_docs = sorted(documents, key=lambda item: item.modified_ts, reverse=True)[:20]
    lines: List[str] = [
        "# Change Digest",
        "",
        "This digest is generated from file modification times. Use it as a quick entry point, not as the canonical audit trail.",
        "",
    ]
    for doc in recent_docs:
        changed_at = datetime.fromtimestamp(doc.modified_ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        lines.append(f"- {changed_at}: [{doc.title}](../../{doc.rel_path}) [{doc.status}, {doc.version}]")
    return "\n".join(lines).rstrip() + "\n"


def write_generated_files(root: Path, outputs: Dict[str, str]) -> List[str]:
    changed: List[str] = []
    expected_paths = {root / relative for relative in outputs}

    if root.exists():
        for existing in sorted(root.rglob("*.md")):
            if existing not in expected_paths:
                existing.unlink()
                changed.append(existing.relative_to(root.parent).as_posix())

    for relative, content in outputs.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        previous = path.read_text(encoding="utf-8") if path.exists() else ""
        if previous != content:
            path.write_text(content, encoding="utf-8")
            changed.append(path.relative_to(root.parent).as_posix())

    return sorted(set(changed))


def build_outputs(base: Path | None = None) -> Dict[str, str]:
    root = base or Path(__file__).resolve().parents[2]
    documents = load_documents(root)
    issues = analyze_documents(documents)
    domain_groups = group_by_domain(documents)
    capability_groups = group_by_capability(documents)
    by_path = {doc.rel_path: doc for doc in documents}
    by_canonical = group_by_capability(documents)

    outputs: Dict[str, str] = {}
    outputs["home.md"] = render_home(documents, issues, domain_groups, capability_groups)
    outputs["reports/change_digest.md"] = render_change_digest(documents)

    provisional_generated = list(outputs.keys())
    outputs["reports/alignment_report.md"] = render_alignment_report(documents, issues, provisional_generated)

    for slug, docs in domain_groups.items():
        outputs[f"domains/{slug}.md"] = render_domain_page(slug, docs)

    for slug, docs in capability_groups.items():
        outputs[f"capabilities/{slug}.md"] = render_capability_page(slug, docs, by_path, by_canonical)

    generated_files = sorted(f"{WIKI_ROOT.as_posix()}/{relative}" for relative in outputs)
    outputs["reports/alignment_report.md"] = render_alignment_report(documents, issues, generated_files)
    return outputs


def generate_wiki(base: Path | None = None) -> List[str]:
    root = base or Path(__file__).resolve().parents[2]
    outputs = build_outputs(root)
    return write_generated_files(root / WIKI_ROOT, outputs)


if __name__ == "__main__":
    changed = generate_wiki()
    if changed:
        print("Updated generated files:")
        for path in changed:
            print(f"- {path}")
    else:
        print("Wiki already up to date.")
