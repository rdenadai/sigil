from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ParserError(Exception):
    message: str
    type: str | None
    value: Any | None
    line: int | None
    column: int | None

    def __init__(
        self,
        message: str,
        type: str | None = None,
        value: Any | None = None,
        line: int | None = None,
        column: int | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __str__(self) -> str:
        location = f" at line {self.line}, column {self.column}" if self.line and self.column else ""
        type_info = f" [Type: {self.type}]" if self.type else ""
        value_info = f" [Value: {self.value}]" if self.value is not None else ""
        return f"ParserError: {self.message}{type_info}{value_info}{location}"


@dataclass(frozen=True, slots=True)
class ASTTypeValue:
    name: str
    value: Any


@dataclass
class ASTFunctionDeclaration:
    name: str
    params: list[ASTTypeValue]
    return_type: str | None


@dataclass
class ASTDeclaration:
    name: str
    var_type: str | None


@dataclass
class ASTClassAttribute:
    name: str
    attr_type: str | None
    is_static: bool
    is_pub: bool
    is_const: bool


@dataclass
class ASTClassMethod:
    fn: ASTFunctionDeclaration
    is_static: bool
    is_pub: bool


class ASTType(StrEnum):
    PROGRAM = "Program"
    BINARY_EXPRESSION = "BinaryExpression"
    LOGICAL_EXPRESSION = "LogicalExpression"
    UNARY_EXPRESSION = "UnaryExpression"
    CALL_EXPRESSION = "CallExpression"
    IDENTIFIER = "Identifier"
    BOOLEAN_LITERAL = "BooleanLiteral"
    NUMBER_LITERAL = "NumberLiteral"
    COMPLEX_LITERAL = "ComplexLiteral"
    STRING_LITERAL = "StringLiteral"
    ELLIPSIS_LITERAL = "EllipsisLiteral"
    NONE_LITERAL = "NoneLiteral"
    STRING_TEMPLATE = "StringTemplate"
    IF_STATEMENT = "IfStatement"
    ELSE_IF_STATEMENT = "ElseIfStatement"
    ELSE_STATEMENT = "ElseStatement"
    TERNARY_EXPRESSION = "TernaryExpression"
    PIPE_EXPRESSION = "PipeExpression"
    ASSIGNMENT_EXPRESSION = "AssignmentExpression"
    MATCH_STATEMENT = "MatchStatement"
    LOOP_STATEMENT = "LoopStatement"
    FOR_STATEMENT = "ForStatement"
    MAIN_DECLARATION = "MainDeclaration"
    VARIABLE_DECLARATION = "VariableDeclaration"
    FUNCTION_DECLARATION = "FunctionDeclaration"
    CLASS_DECLARATION = "ClassDeclaration"
    CLASS_ATTRIBUTE = "ClassAttribute"
    CLASS_METHOD = "ClassMethod"
    CLASS_MEMBER_ACCESS = "ClassMemberAccess"
    LAMBDA_EXPRESSION = "LambdaExpression"
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
