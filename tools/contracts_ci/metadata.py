from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from tools.contracts_ci.common import as_posix, parse_version_from_stem, repo_root, strip_version_suffix

RELATIONSHIP_KEYS = [
    "Canonical-Id",
    "Relates-To",
    "Depends-On",
    "Supersedes",
    "Superseded-By",
    "Implements",
    "Implemented-By",
    "See-Also",
]

LIST_RELATIONSHIP_KEYS = [
    "Relates-To",
    "Depends-On",
    "Supersedes",
    "Superseded-By",
    "Implements",
    "Implemented-By",
    "See-Also",
]

LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:")
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
TITLE_PATTERN = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def normalize_token(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


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


def parse_list_value(value: str) -> List[str]:
    trimmed = value.strip()
    if not trimmed:
        return []
    if trimmed.startswith("[") and trimmed.endswith("]"):
        trimmed = trimmed[1:-1]
    return [item.strip() for item in trimmed.split(",") if item.strip()]


def normalize_reference(value: str) -> str:
    if value.endswith(".md"):
        return value.replace("\\", "/")
    return normalize_token(value)


def extract_title(text: str, path: Path) -> str:
    match = TITLE_PATTERN.search(text)
    if match:
        return match.group(1).strip()
    return path.stem


def is_external(target: str) -> bool:
    return target.startswith(EXTERNAL_PREFIXES) or "://" in target


def is_image(target: str) -> bool:
    lower = target.lower()
    return any(lower.endswith(ext) for ext in IMAGE_EXTENSIONS)


def extract_internal_links(text: str, source_path: Path, root: Path) -> List[str]:
    links: List[str] = []
    seen: set[str] = set()
    for match in LINK_PATTERN.finditer(text):
        raw_target = match.group(1).strip()
        if not raw_target or raw_target.startswith("#") or is_external(raw_target):
            continue
        target = raw_target.split("#", 1)[0].split("?", 1)[0]
        if not target or is_image(target):
            continue
        candidate = (source_path.parent / Path(target)).resolve()
        try:
            rel = as_posix(candidate.relative_to(root))
        except ValueError:
            continue
        if rel not in seen:
            links.append(rel)
            seen.add(rel)
    return links


@dataclass(frozen=True)
class ContractDocument:
    path: Path
    rel_path: str
    header: Dict[str, str]
    title: str
    domain: str
    capability: str
    scope: str
    artifact_type: str
    stability: str
    status: str
    version: str
    canonical_id: str
    relationships: Dict[str, Tuple[str, ...]]
    links: Tuple[str, ...]
    content: str
    modified_ts: float

    @property
    def filename_family(self) -> str:
        return normalize_token(strip_version_suffix(self.path.stem))

    @property
    def inferred_version(self) -> str:
        return parse_version_from_stem(self.path.stem)


def load_documents(base: Path | None = None) -> List[ContractDocument]:
    root = base or repo_root()
    documents: List[ContractDocument] = []
    for path in sorted(root.rglob("*.md")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if not rel.parts or rel.parts[0] not in {"contracts", "architecture", "decisions", "platform"}:
            continue
        if rel.parts[0] == "_incoming":
            continue

        content = path.read_text(encoding="utf-8")
        header, errors = parse_front_matter(content)
        if errors:
            continue

        relationships: Dict[str, Tuple[str, ...]] = {}
        for key in LIST_RELATIONSHIP_KEYS:
            relationships[key] = tuple(normalize_reference(v) for v in parse_list_value(header.get(key, "")))

        canonical_value = header.get("Canonical-Id", "")
        canonical_id = normalize_reference(canonical_value) if canonical_value else normalize_token(strip_version_suffix(path.stem))

        documents.append(
            ContractDocument(
                path=path,
                rel_path=as_posix(rel),
                header=header,
                title=extract_title(content, path),
                domain=header.get("Domain", ""),
                capability=header.get("Capability", ""),
                scope=header.get("Scope", ""),
                artifact_type=header.get("Artifact-Type", ""),
                stability=header.get("Stability", ""),
                status=header.get("Status", ""),
                version=header.get("Version", ""),
                canonical_id=canonical_id,
                relationships=relationships,
                links=tuple(extract_internal_links(content, path, root)),
                content=content,
                modified_ts=path.stat().st_mtime,
            )
        )
    return documents


def relationship_targets(document: ContractDocument, keys: Sequence[str] | None = None) -> List[str]:
    requested = keys or LIST_RELATIONSHIP_KEYS
    targets: List[str] = []
    seen: set[str] = set()
    for key in requested:
        for value in document.relationships.get(key, ()):
            if value not in seen:
                targets.append(value)
                seen.add(value)
    return targets
