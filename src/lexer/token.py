from dataclasses import dataclass
from enum import StrEnum


class TokenType(StrEnum): ...


class TokenIdentifier(TokenType):
    IDENTIFIER = "IDENTIFIER"


class TokenKeyword(TokenType):
    BYTE = "BYTE"
    INT8 = "INT8"
    INT32 = "INT32"
    INT64 = "INT64"
    FLOAT32 = "FLOAT32"
    FLOAT64 = "FLOAT64"
    COMPLEX = "COMPLEX"
    BOOL = "BOOL"
    STRING = "STRING"
    ELLIPSIS = "ELLIPSIS"
    CALLABLE = "CALLABLE"
    OBJECT = "OBJECT"
    NONE = "NONE"
    CLASS = "CLASS"
    ENUM = "ENUM"
    STRUCT = "STRUCT"
    UNION = "UNION"
    MAIN = "MAIN"
    WITH = "WITH"
    YIELD = "YIELD"
    LAZY = "LAZY"
    AWAIT = "AWAIT"
    ASYNC = "ASYNC"
    IMPORT = "IMPORT"
    FROM = "FROM"
    AS = "AS"
    DELETE = "DELETE"
    FN = "FN"
    FUNCTION = "FUNCTION"
    LAMBDA = "LAMBDA"
    LET = "LET"
    CONST = "CONST"
    MATCH = "MATCH"
    IF = "IF"
    ELSE = "ELSE"
    LOOP = "LOOP"
    FOR = "FOR"
    RETURN = "RETURN"
    DEFER = "DEFER"
    GOTO = "GOTO"
    ASSERT = "ASSERT"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    SELF = "SELF"
    SUPER = "SUPER"
    TRY = "TRY"
    HANDLE = "HANDLE"
    CATCH = "CATCH"
    FINALLY = "FINALLY"
    THROW = "THROW"
    USING = "USING"
    PERFORM = "PERFORM"
    RESUME = "RESUME"
    IN = "IN"
    IS = "IS"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    PUB = "PUB"
    STATIC = "STATIC"
    ABSTRACT = "ABSTRACT"
    EXPORT = "EXPORT"
    GLOBAL = "GLOBAL"
    LOCAL = "LOCAL"
    MACRO = "MACRO"
    MODULE = "MODULE"


class TokenKeywordSpecial(TokenType):
    LAMBDA_SPECIAL = "λ"


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
    BACKSTICK = "`"


class TokenOperator(TokenType):
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIV = "/"
    FLOOR_DIV = "//"
    POWER = "**"
    INCREMENT = "++"
    DECREMENT = "--"
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
    WALRUS = ":="
    PIPE = "|>"
    AMPERSAND = "&"
    BAR = "|"
    AT = "@"
    CARET = "^"
    EXCLAMATION = "!"
    QUESTION = "?"
    TILDE = "~"
    SHIFT_LEFT = "<<"
    SHIFT_RIGHT = ">>"
    FLOOR_DIV_EQUAL = "//="
    POWER_EQUAL = "**="
    MULTIPLY_EQUAL = "*="
    DIV_EQUAL = "/="
    MOD_EQUAL = "%="
    PLUS_EQUAL = "+="
    MINUS_EQUAL = "-="
    AND_EQUAL = "&="
    OR_EQUAL = "|="
    XOR_EQUAL = "^="
    SHIFT_LEFT_EQUAL = "<<="
    SHIFT_RIGHT_EQUAL = ">>="


class TokenLiteral(TokenType):
    BYTE = "BYTE"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    COMPLEX = "COMPLEX"
    BOOLEAN = "BOOLEAN"
    STRING = "STRING"
    NONE = "NONE"
    ELLIPSIS = "ELLIPSIS"
    STRING_TEMPLATE = "STRING_TEMPLATE"


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
