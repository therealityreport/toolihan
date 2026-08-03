from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DuplicationIssue:
    code: str
    path: str
    message: str
