from __future__ import annotations

from pathlib import Path

try:
    from .debugpro_duplication_types import DuplicationIssue
except ImportError:
    from debugpro_duplication_types import DuplicationIssue


SHARED_REFERENCES = {
    Path("skills/debugpro/references/debugging-discipline.md"),
    Path("skills/debugpro/references/parallel-debugging-contract.md"),
    Path("skills/debugpro/references/missing-evidence-routing.md"),
    Path("skills/debugpro/references/skill-overlap-inventory.md"),
}

PARALLEL_SKILLS = (
    "debugpro-team",
    "debugpro-arbitration",
)

MISSING_EVIDENCE_SKILLS = (
    "debugpro-intake",
    "debugpro-hypotheses",
    "debugpro-root-cause-tracing",
    "debugpro-instrumentation",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def skill_path(root: Path, name: str) -> Path:
    return root / "skills" / name / "SKILL.md"


def missing_reference_links(root: Path) -> list[DuplicationIssue]:
    issues: list[DuplicationIssue] = []
    issues.extend(
        missing_links(root, PARALLEL_SKILLS, "parallel-debugging-contract.md", "missing_parallel_contract_link")
    )
    issues.extend(
        missing_links(root, MISSING_EVIDENCE_SKILLS, "missing-evidence-routing.md", "missing_evidence_routing_link")
    )
    return issues


def missing_links(root: Path, names: tuple[str, ...], target: str, code: str) -> list[DuplicationIssue]:
    issues: list[DuplicationIssue] = []
    for name in names:
        path = skill_path(root, name)
        if path.exists() and target not in read_text(path):
            issues.append(DuplicationIssue(code, str(path.relative_to(root)), missing_link_message(target)))
    return issues


def missing_link_message(target: str) -> str:
    return f"Skill should link {target}."


def shared_references_missing(root: Path) -> list[DuplicationIssue]:
    issues: list[DuplicationIssue] = []
    for relative in sorted(SHARED_REFERENCES):
        if not (root / relative).exists():
            issues.append(DuplicationIssue("missing_shared_reference", str(relative), "Shared reference is missing."))
    return issues
