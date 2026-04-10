from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

from tools.contracts_ci.metadata import ContractDocument, relationship_targets

TRACKED_REL_KEYS = ["Relates-To", "Depends-On", "Supersedes", "Superseded-By", "Implements", "Implemented-By", "See-Also"]


@dataclass(frozen=True)
class AlignmentIssue:
    code: str
    severity: str
    message: str
    paths: Tuple[str, ...]


def _build_indexes(documents: Sequence[ContractDocument]) -> tuple[Dict[str, ContractDocument], Dict[str, List[ContractDocument]]]:
    by_path = {doc.rel_path: doc for doc in documents}
    by_canonical: Dict[str, List[ContractDocument]] = defaultdict(list)
    for doc in documents:
        if "Canonical-Id" in doc.header:
            by_canonical[doc.canonical_id].append(doc)
    return by_path, by_canonical


def _split_path_targets(targets: Iterable[str]) -> Tuple[List[str], List[str]]:
    path_targets: List[str] = []
    canonical_targets: List[str] = []
    for value in targets:
        if value.endswith(".md"):
            path_targets.append(value)
        else:
            canonical_targets.append(value)
    return path_targets, canonical_targets


def analyze_documents(documents: Sequence[ContractDocument]) -> List[AlignmentIssue]:
    issues: List[AlignmentIssue] = []
    by_path, by_canonical = _build_indexes(documents)

    for doc in documents:
        path_targets, canonical_targets = _split_path_targets(relationship_targets(doc, TRACKED_REL_KEYS))

        for target in path_targets:
            if target not in by_path:
                issues.append(
                    AlignmentIssue(
                        code="missing_relationship_target",
                        severity="error",
                        message=f"{doc.rel_path} references missing relationship target '{target}'.",
                        paths=(doc.rel_path,),
                    )
                )

        for canonical_target in canonical_targets:
            if canonical_target not in by_canonical:
                issues.append(
                    AlignmentIssue(
                        code="missing_canonical_target",
                        severity="error",
                        message=f"{doc.rel_path} references unknown Canonical-Id '{canonical_target}'.",
                        paths=(doc.rel_path,),
                    )
                )

        if doc.status == "active":
            for dependency in doc.relationships.get("Depends-On", ()):
                dep_docs = [by_path[dependency]] if dependency.endswith(".md") and dependency in by_path else by_canonical.get(dependency, [])
                for dep_doc in dep_docs:
                    if dep_doc.status == "deprecated":
                        issues.append(
                            AlignmentIssue(
                                code="deprecated_dependency",
                                severity="error",
                                message=f"{doc.rel_path} depends on deprecated document {dep_doc.rel_path}.",
                                paths=(doc.rel_path, dep_doc.rel_path),
                            )
                        )

        if "Canonical-Id" in doc.header and doc.status == "active":
            siblings = [item for item in by_canonical.get(doc.canonical_id, []) if item.status == "active"]
            if len(siblings) > 1:
                sibling_paths = tuple(sorted(item.rel_path for item in siblings))
                missing_supersession = True
                for sibling in siblings:
                    explicit_targets = set(relationship_targets(sibling, ["Supersedes", "Superseded-By"]))
                    related = {item.canonical_id for item in siblings if item is not sibling}
                    if explicit_targets.intersection(related):
                        missing_supersession = False
                        break
                if missing_supersession:
                    issues.append(
                        AlignmentIssue(
                            code="conflicting_active_versions",
                            severity="error",
                            message=f"Canonical-Id '{doc.canonical_id}' has multiple active documents without explicit supersession.",
                            paths=sibling_paths,
                        )
                    )

        if "Canonical-Id" in doc.header and doc.relationships.get("Superseded-By"):
            if doc.status != "deprecated":
                issues.append(
                    AlignmentIssue(
                        code="superseded_status",
                        severity="error",
                        message=f"{doc.rel_path} declares Superseded-By and therefore MUST be deprecated.",
                        paths=(doc.rel_path,),
                    )
                )

    deduped: Dict[tuple[str, tuple[str, ...]], AlignmentIssue] = {}
    for issue in issues:
        deduped[(issue.message, issue.paths)] = issue
    return sorted(deduped.values(), key=lambda item: (item.severity, item.code, item.paths))


def render_alignment_report(documents: Sequence[ContractDocument], issues: Sequence[AlignmentIssue], generated_files: Sequence[str]) -> str:
    active = sum(1 for doc in documents if doc.status == "active")
    draft = sum(1 for doc in documents if doc.status == "draft")
    deprecated = sum(1 for doc in documents if doc.status == "deprecated")

    lines: List[str] = [
        "# Alignment Report",
        "",
        "This report is generated from canonical docs. Edit source docs, then regenerate.",
        "",
        "## Snapshot",
        "",
        f"- Documents scanned: {len(documents)}",
        f"- Active: {active}",
        f"- Draft: {draft}",
        f"- Deprecated: {deprecated}",
        f"- Generated wiki files: {len(generated_files)}",
        "",
        "## Issues",
        "",
    ]

    if not issues:
        lines.append("- No alignment issues detected by deterministic checks.")
    else:
        for issue in issues:
            lines.append(f"- [{issue.severity}] {issue.message}")
            if issue.paths:
                lines.append(f"  Paths: {', '.join(issue.paths)}")

    lines.extend(["", "## Enforcement Rules", ""])
    lines.append("- Explicit relationship targets MUST resolve to a real doc path or Canonical-Id.")
    lines.append("- Active docs MUST NOT depend on deprecated docs.")
    lines.append("- Explicit Canonical-Ids MUST NOT produce multiple active versions without supersession metadata.")
    lines.append("- Docs with `Superseded-By` MUST be marked `deprecated`.")
    lines.append("- Generated wiki coverage is validated separately against canonical docs.")

    return "\n".join(lines).rstrip() + "\n"
