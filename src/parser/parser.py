from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from src.lexer.token import (
    Token,
    TokenAnnotationTypes,
    TokenDelimiter,
    TokenIdentifier,
    TokenIndentation,
    TokenKeyword,
    TokenLiteral,
    TokenOperator,
)


class ParserError(Exception): ...


class ASTType(StrEnum):
    PROGRAM = "Program"
    MAIN_DECLARATION = "MainDeclaration"
    VARIABLE_DECLARATION = "VariableDeclaration"
    FUNCTION_DECLARATION = "FunctionDeclaration"
    BINARY_EXPRESSION = "BinaryExpression"
    LOGICAL_EXPRESSION = "LogicalExpression"
    UNARY_EXPRESSION = "UnaryExpression"
    IDENTIFIER = "Identifier"
    NUMBER_LITERAL = "NumberLiteral"
    COMPLEX_LITERAL = "ComplexLiteral"
    STRING_LITERAL = "StringLiteral"
    IF_STATEMENT = "IfStatement"
    MATCH_STATEMENT = "MatchStatement"
    LOOP_STATEMENT = "LoopStatement"
    FOR_STATEMENT = "ForStatement"
    RETURN_STATEMENT = "ReturnStatement"
    NEWLINE = "NewLine"
    EOF = "EOF"
    INDENT = "Indent"
    DEDENT = "Dedent"


@dataclass
class ASTNode:
    type: str
    value: Any = None
    children: list[Any] = field(default_factory=list)


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0
        self._ast: dict[str, Any] = {"type": ASTType.PROGRAM, "body": []}

    @property
    def ast(self) -> dict[str, Any]:
        return self._ast

    def _current_token(self) -> Token | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _previous_token(self) -> Token | None:
        return self.tokens[self.pos - 1] if self.pos - 1 >= 0 else None

    def _next_token(self) -> Token | None:
        return self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None

    def _advance(self):
        self.pos += 1

    def _match(self, expected_types: set[str]) -> Token:
        """Consume token if it matches expected_type, else raise SyntaxError."""
        token = self._current_token()
        if token and token.type in expected_types:
            self._advance()
            return token
        raise ParserError(f"Expected {expected_types} but got {token.type if token else 'EOF'}")

    def _factor(self) -> ASTNode:
        """Parses the highest-precedence expressions (factors)."""
        token = self._current_token()

        if token.type in {TokenLiteral.INTEGER, TokenLiteral.FLOAT}:
            self._advance()
            return ASTNode(type=ASTType.NUMBER_LITERAL, value=token.value)

        if token.type == TokenLiteral.COMPLEX:
            self._advance()
            return ASTNode(type=ASTType.COMPLEX_LITERAL, value=token.value)

        if token.type == TokenIdentifier.IDENTIFIER:
            self._advance()
            return ASTNode(type=ASTType.IDENTIFIER, value=token.value)

        if token.type == TokenDelimiter.LPAREN:
            self._advance()
            node = self._expression()
            self._match({TokenDelimiter.RPAREN})
            return node

        raise ParserError(f"Unexpected token in expression: {token.type}")

    def _term(self) -> ASTNode:
        """Parses multiplication, division, and other higher-precedence operators."""
        node = self._factor()

        while self._current_token() and self._current_token().type in {
            TokenOperator.MULTIPLY,
            TokenOperator.DIVIDE,
            TokenOperator.FLOOR_DIV,
            TokenOperator.POWER,
            TokenOperator.MOD,
        }:
            op_token = self._current_token()
            self._advance()
            right = self._factor()
            node = ASTNode(
                type=ASTType.BINARY_EXPRESSION,
                value=op_token.value,
                children=[node, right],
            )

        return node

    def _expression(self) -> ASTNode:
        """Parses addition, subtraction, and other lowest-precedence operators."""
        node = self._term()

        while self._current_token() and self._current_token().type in {
            TokenOperator.PLUS,
            TokenOperator.MINUS,
        }:
            op_token = self._current_token()
            self._advance()
            right = self._term()
            node = ASTNode(
                type=ASTType.BINARY_EXPRESSION,
                value=op_token.value,
                children=[node, right],
            )

        while self._current_token() and self._current_token().type in {
            TokenOperator.EQUAL_EQUAL,
            TokenOperator.NOT_EQUAL,
            TokenOperator.LESS,
            TokenOperator.LESS_EQUAL,
            TokenOperator.GREATER,
            TokenOperator.GREATER_EQUAL,
        }:
            op_token = self._current_token()
            self._advance()
            right = self._term()
            node = ASTNode(
                type=ASTType.LOGICAL_EXPRESSION,
                value=op_token.value,
                children=[node, right],
            )

        while self._current_token() and self._current_token().type in {
            TokenKeyword.AND,
            TokenKeyword.OR,
        }:
            op_token = self._current_token()
            self._advance()
            right = self._term()
            node = ASTNode(
                type=ASTType.LOGICAL_EXPRESSION,
                value=op_token.value,
                children=[node, right],
            )

        while self._current_token() and self._current_token().type in {
            TokenKeyword.NOT,
        }:
            op_token = self._current_token()
            self._advance()
            right = self._term()
            node = ASTNode(
                type=ASTType.UNARY_EXPRESSION,
                value=op_token.value,
                children=[right],
            )

        return node

    def _assignment(self) -> ASTNode:
        self._match({TokenKeyword.LET, TokenKeyword.CONST})
        identifier_token = self._match({TokenIdentifier.IDENTIFIER})
        if self._current_token() and self._current_token().type == TokenDelimiter.COLON:
            self._match({TokenDelimiter.COLON})
            self._match({kw.name for kw in TokenAnnotationTypes})
        self._match({TokenOperator.EQUAL})
        value_token = self._expression()

        return ASTNode(
            ASTType.VARIABLE_DECLARATION,
            children=[
                ASTNode(type=ASTType.IDENTIFIER, value=identifier_token.value),
                value_token,
            ],
        )

    def _conditional(self) -> ASTNode:
        if self._current_token().type == TokenKeyword.IF:
            self._match({TokenKeyword.IF})
            condition = self._expression()
            self._match({TokenDelimiter.COLON})
            self._match({TokenIndentation.NEWLINE})
            self._match({TokenIndentation.INDENT})

            body = []
            while self._current_token() and self._current_token().type != TokenIndentation.DEDENT:
                stmt = self._statement()
                if stmt:
                    body.append(stmt)

            self._match({TokenIndentation.DEDENT})

            return ASTNode(
                type=ASTType.IF_STATEMENT,
                children=[condition] + body,
            )

        if self._current_token().type == TokenKeyword.MATCH:
            # Placeholder for match statement parsing
            pass

        if self._current_token().type == TokenKeyword.LOOP:
            self._match({TokenKeyword.LOOP})
            self._match({TokenDelimiter.COLON})
            self._match({TokenIndentation.NEWLINE})
            self._match({TokenIndentation.INDENT})
            body = []
            while self._current_token() and self._current_token().type != TokenIndentation.DEDENT:
                stmt = self._statement()
                if stmt:
                    body.append(stmt)
            self._match({TokenIndentation.DEDENT})
            return ASTNode(
                type=ASTType.LOOP_STATEMENT,
                children=body,
            )

        if self._current_token().type == TokenKeyword.FOR:
            self._match({TokenKeyword.FOR})
            iterator = self._match({TokenIdentifier.IDENTIFIER})
            self._match({TokenKeyword.IN})
            iterable = self._expression()
            self._match({TokenDelimiter.COLON})
            self._match({TokenIndentation.NEWLINE})
            self._match({TokenIndentation.INDENT})
            body = []
            while self._current_token() and self._current_token().type != TokenIndentation.DEDENT:
                stmt = self._statement()
                if stmt:
                    body.append(stmt)
            self._match({TokenIndentation.DEDENT})
            return ASTNode(
                type=ASTType.FOR_STATEMENT,
                children=[ASTNode(type=ASTType.IDENTIFIER, value=iterator.value), iterable] + body,
            )

    def _function_declaration(self) -> ASTNode: ...

    def _statement(self) -> ASTNode | None:
        token = self._current_token()
        if not token:
            return None

        if token.type in {TokenKeyword.LET, TokenKeyword.CONST}:
            return self._assignment()
        if token.type == TokenKeyword.FUNCTION:
            return self._function_declaration()
        if token.type in {TokenKeyword.IF, TokenKeyword.MATCH, TokenKeyword.LOOP, TokenKeyword.FOR}:
            return self._conditional()
        if token.type == TokenIndentation.EOF:
            self._advance()
            return ASTNode(type=ASTType.EOF)
        if token.type == TokenIndentation.NEWLINE:
            self._advance()
            return ASTNode(type=ASTType.NEWLINE)
        if token.type == TokenIndentation.INDENT:
            self._advance()
            return ASTNode(type=ASTType.INDENT)
        if token.type == TokenIndentation.DEDENT:
            self._advance()
            return ASTNode(type=ASTType.DEDENT)

        return self._expression()

    def _main_statement(self) -> ASTNode:
        self._match({TokenKeyword.FN, TokenKeyword.FUNCTION})
        self._match({TokenKeyword.MAIN})
        self._match({TokenDelimiter.LPAREN})
        self._match({TokenDelimiter.RPAREN})
        if self._current_token() and self._current_token().type == TokenOperator.ARROW:
            self._match({TokenOperator.ARROW})
            self._match({kw.name for kw in TokenAnnotationTypes})
        self._match({TokenDelimiter.COLON})
        self._match({TokenIndentation.NEWLINE})
        self._match({TokenIndentation.INDENT})

        body = []
        while self._current_token() and self._current_token().type != TokenIndentation.DEDENT:
            stmt = self._statement()
            if stmt:
                body.append(stmt)

        self._match({TokenIndentation.DEDENT})

        return ASTNode(type=ASTType.MAIN_DECLARATION, value=TokenKeyword.MAIN, children=body)

    def parse(self) -> dict[str, Any]:
        """Parse the list of tokens and return the AST."""
        while self._current_token():
            if (
                self._current_token().type in {TokenKeyword.FN, TokenKeyword.FUNCTION}
                and self._next_token().type == TokenKeyword.MAIN
            ):
                self._ast["body"].append(self._main_statement())
                continue
            self._ast["body"].append(self._statement())
        return self._ast
