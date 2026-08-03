"""Shared types for DebugPro link checking."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LinkIssue:
    source: str
    target: str
    line: int
    message: str

    def to_dict(self) -> dict[str, str | int]:
        return {
            "source": self.source,
            "target": self.target,
            "line": self.line,
            "message": self.message,
        }
