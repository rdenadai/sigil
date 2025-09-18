from dataclasses import dataclass
from enum import StrEnum


class TokenType(StrEnum): ...


class TokenIdentifier(TokenType):
    IDENTIFIER = "IDENTIFIER"


class TokenKeyword(TokenType):
    BYTE = "BYTE"
    INT32 = "INT32"
    INT64 = "INT64"
    FLOAT32 = "FLOAT32"
    FLOAT64 = "FLOAT64"
    COMPLEX = "COMPLEX"
    BOOL = "BOOL"
    STRING = "STRING"
    ELLIPSIS = "ELLIPSIS"
    NONE = "NONE"
    CLASS = "CLASS"
    MAIN = "MAIN"
    YIELD = "YIELD"
    AWAIT = "AWAIT"
    ASYNC = "ASYNC"
    IMPORT = "IMPORT"
    FROM = "FROM"
    AS = "AS"
    FN = "FN"
    FUNCTION = "FUNCTION"
    LAMBDA = "LAMBDA"
    LAMBDA_SPECIAL = "λ"
    LET = "LET"
    CONST = "CONST"
    IF = "IF"
    ELSE = "ELSE"
    LOOP = "LOOP"
    FOR = "FOR"
    RETURN = "RETURN"
    DEFER = "DEFER"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    THIS = "THIS"
    SUPER = "SUPER"
    TRY = "TRY"
    CATCH = "CATCH"
    FINALLY = "FINALLY"
    THROW = "THROW"
    IN = "IN"
    IS = "IS"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    PUB = "PUB"
    STATIC = "STATIC"
    ABSTRACT = "ABSTRACT"
    EXPORT = "EXPORT"


class TokenDelimiter(TokenType):
    COMMA = ","
    SEMICOLON = ";"
    DOT = "."
    COLON = ":"
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"


class TokenOperator(TokenType):
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    DIV = "/"
    FLOOR_DIV = "//"
    POWER = "**"
    MOD = "%"
    EQUAL = "="
    EQUAL_EQUAL = "=="
    NOT_EQUAL = "!="
    LESS = "<"
    LESS_EQUAL = "<="
    GREATER = ">"
    GREATER_EQUAL = ">="
    ARROW = "->"
    DOUBLE_ARROW = "=>"
    PIPE = "|>"
    AMPERSAND = "&"
    CARET = "^"
    SHIFT_LEFT = "<<"
    SHIFT_RIGHT = ">>"


class TokenLiteral(TokenType):
    BYTE = "BYTE"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    COMPLEX = "COMPLEX"
    BOOLEAN = "BOOLEAN"
    STRING = "STRING"
    NONE = "NONE"
    ARRAY = "ARRAY"
    LIST = "LIST"
    TUPLE = "TUPLE"
    MAP = "MAP"
    SET = "SET"
    OBJECT = "OBJECT"
    CALLABLE = "CALLABLE"
    ELLIPSIS = "ELLIPSIS"


class TokenComment(TokenType):
    COMMENT = "COMMENT"


class TokenIndentation(TokenType):
    INDENT = "INDENT"
    DEDENT = "DEDENT"
    NEWLINE = "NEWLINE"
    EOF = "EOF"


@dataclass(frozen=True, slots=True)
class Token:
    filename: str
    line: int
    column: int
    type: TokenType
    value: str
