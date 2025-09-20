from typing import Any, List

from src.lexer.token import Token


class ParserError(Exception): ...


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self._ast: dict[str, Any] = {"type": "Program", "body": []}

    # Public entry
    def parse(self) -> dict[str, Any]:
        return self._ast

    @property
    def ast(self) -> dict[str, Any]:
        return self._ast
