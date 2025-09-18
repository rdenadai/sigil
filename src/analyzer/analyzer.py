from __future__ import annotations

from typing import Any


class SemanticError(Exception): ...


class SemanticAnalyzer:
    def __init__(self, ast: dict[str, Any]):
        self._ast = ast

    def analyze(self) -> dict[str, Any]:
        return {}
