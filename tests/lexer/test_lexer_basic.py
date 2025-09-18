from typing import Any

import pytest

from src.lexer.lexer import Lexer
from src.lexer.token import (
    TokenDelimiter,
    TokenIdentifier,
    TokenIndentation,
    TokenKeyword,
    TokenKeywordSpecial,
    TokenLiteral,
    TokenOperator,
)


def test_lexer_empty():
    lexer = Lexer(filename="empty.sl", lines=[""])
    tokens = lexer.tokenize()
    assert len(tokens) == 1  # Only EOF
    assert [token.type for token in tokens] == [TokenIndentation.EOF]
    assert tokens[0].value == ""


def test_lexer_whitespace():
    code = """


    """.strip()

    lexer = Lexer(filename="whitespace.sl", lines=[code])
    tokens = lexer.tokenize()
    assert len(tokens) == 1  # Only EOF
    assert [token.type for token in tokens] == [TokenIndentation.EOF]
    assert tokens[0].value == ""


def test_lexer_comment():
    code = """
    # This is a comment
    # Another comment line
    """.strip()

    lexer = Lexer(filename="comment.sl", lines=[code])
    tokens = lexer.tokenize()
    assert len(tokens) == 1  # Only EOF
    assert [token.type for token in tokens] == [TokenIndentation.EOF]
    assert tokens[0].value == ""


def test_lexer_single_line():
    code = "const x: int32 = 42"

    lexer = Lexer(filename="single_line.sl", lines=[code])
    tokens = lexer.tokenize()

    expected_types: list[Any] = [
        TokenKeyword.CONST,
        TokenIdentifier.IDENTIFIER,
        TokenDelimiter.COLON,
        TokenKeyword.INT32,
        TokenOperator.EQUAL,
        TokenLiteral.INTEGER,
        TokenIndentation.NEWLINE,
        TokenIndentation.EOF,
    ]
    assert [token.type for token in tokens] == expected_types
    assert all(isinstance(token.value, str) for token in tokens)


@pytest.mark.parametrize(
    "none_keyword, none_case",
    [
        ("none", "none"),
        ("None", "None"),
        ("NONE", "NONE"),
        ("nOnE", "nOnE"),
        ("NONE", "none"),
        ("none", "None"),
        ("None", "NONE"),
        ("nOnE", "nOnE"),
    ],
)
def test_lexer_none_literal(none_keyword: str, none_case: str):
    code = f"const x: {none_keyword} = {none_case}"

    lexer = Lexer(filename="none_literal.sl", lines=[code])
    tokens = lexer.tokenize()

    expected_types: list[Any] = [
        TokenKeyword.CONST,
        TokenIdentifier.IDENTIFIER,
        TokenDelimiter.COLON,
        TokenKeyword.NONE,
        TokenOperator.EQUAL,
        TokenLiteral.NONE,
        TokenIndentation.NEWLINE,
        TokenIndentation.EOF,
    ]
    assert [token.type for token in tokens] == expected_types
    assert all(isinstance(token.value, str) for token in tokens)


@pytest.mark.parametrize(
    "ellipsis_keyword, ellipsis_case",
    [
        ("ellipsis", "..."),
        ("ELLIPSIS", "..."),
        ("Ellipsis", "..."),
        ("eLlIpSiS", "..."),
        ("ELLIPSIS", "..."),
        ("ellipsis", "..."),
    ],
)
def test_lexer_ellipsis_literal(ellipsis_keyword: str, ellipsis_case: str):
    code = f"const x: {ellipsis_keyword} = {ellipsis_case}"

    lexer = Lexer(filename="ellipsis_literal.sl", lines=[code])
    tokens = lexer.tokenize()

    expected_types: list[Any] = [
        TokenKeyword.CONST,
        TokenIdentifier.IDENTIFIER,
        TokenDelimiter.COLON,
        TokenKeyword.ELLIPSIS,
        TokenOperator.EQUAL,
        TokenLiteral.ELLIPSIS,
        TokenIndentation.NEWLINE,
        TokenIndentation.EOF,
    ]
    assert [token.type for token in tokens] == expected_types
    assert all(isinstance(token.value, str) for token in tokens)


@pytest.mark.parametrize("bool_value", ["true", "false"])
def test_lexer_boolean_literal(bool_value: str):
    code = f"const x: bool = {bool_value}"

    lexer = Lexer(filename="boolean_literal.sl", lines=[code])
    tokens = lexer.tokenize()

    expected_types: list[Any] = [
        TokenKeyword.CONST,
        TokenIdentifier.IDENTIFIER,
        TokenDelimiter.COLON,
        TokenKeyword.BOOL,
        TokenOperator.EQUAL,
        TokenLiteral.BOOLEAN,
        TokenIndentation.NEWLINE,
        TokenIndentation.EOF,
    ]
    assert [token.type for token in tokens] == expected_types
    assert all(isinstance(token.value, str) for token in tokens)


def test_lexer_string_literal():
    code = "let str = '\"Hello, World! \nNew Line Tabbed'"

    lexer = Lexer(filename="string_literal.sl", lines=[code])
    tokens = lexer.tokenize()

    expected_types: list[Any] = [
        TokenKeyword.LET,
        TokenIdentifier.IDENTIFIER,
        TokenOperator.EQUAL,
        TokenLiteral.STRING,
        TokenIndentation.NEWLINE,
        TokenIndentation.EOF,
    ]
    assert [token.type for token in tokens] == expected_types
    assert all(isinstance(token.value, str) for token in tokens)
    assert tokens[3].value == '"Hello, World! \nNew Line Tabbed'


@pytest.mark.parametrize(
    "int_value",
    [
        "0",
        "123",
        "456789",
        "2147483647",
        "9223372036854775807",
        "1_000_000",
    ],
)
def test_lexer_integer_literal(int_value: str):
    code = f"let x = {int_value}"

    lexer = Lexer(filename="integer_literal.sl", lines=[code])
    tokens = lexer.tokenize()

    expected_types: list[Any] = [
        TokenKeyword.LET,
        TokenIdentifier.IDENTIFIER,
        TokenOperator.EQUAL,
        TokenLiteral.INTEGER,
        TokenIndentation.NEWLINE,
        TokenIndentation.EOF,
    ]
    assert [token.type for token in tokens] == expected_types
    assert all(isinstance(token.value, str) for token in tokens)
    assert tokens[3].value == int_value


@pytest.mark.parametrize(
    "negative_int_value",
    [
        "-0",
        "-123",
        "-456789",
        "-2147483648",
        "-9223372036854775808",
        "-1_000_000",
    ],
)
def test_lexer_negative_integer_literal(negative_int_value: str):
    code = f"let x = {negative_int_value}"

    lexer = Lexer(filename="negative_integer_literal.sl", lines=[code])
    tokens = lexer.tokenize()

    expected_types: list[Any] = [
        TokenKeyword.LET,
        TokenIdentifier.IDENTIFIER,
        TokenOperator.EQUAL,
        TokenOperator.MINUS,
        TokenLiteral.INTEGER,
        TokenIndentation.NEWLINE,
        TokenIndentation.EOF,
    ]
    assert [token.type for token in tokens] == expected_types
    assert all(isinstance(token.value, str) for token in tokens)
    assert tokens[4].value == negative_int_value[1:]


@pytest.mark.parametrize(
    "float_value",
    [
        "0.0",
        "3.14",
        "2.71828",
        "1e10",
        "6.022e23",
        "1_000.000_1",
    ],
)
def test_lexer_float_literal(float_value: str):
    code = f"let x = {float_value}"

    lexer = Lexer(filename="float_literal.sl", lines=[code])
    tokens = lexer.tokenize()

    expected_types: list[Any] = [
        TokenKeyword.LET,
        TokenIdentifier.IDENTIFIER,
        TokenOperator.EQUAL,
        TokenLiteral.FLOAT,
        TokenIndentation.NEWLINE,
        TokenIndentation.EOF,
    ]
    assert [token.type for token in tokens] == expected_types
    assert all(isinstance(token.value, str) for token in tokens)
    assert tokens[3].value == float_value


@pytest.mark.parametrize(
    "negative_float_value",
    [
        "-0.0",
        "-3.14",
        "-2.71828",
        "-1e10",
        "-6.022e23",
        "-1_000.000_1",
        "-1.0e-10",
        "-3.5e+20",
        "-2.5e-5",
        "-7.0e+3",
        "-4.2e-2",
        "-9.81e+1",
        "-1_234.56e+7",
    ],
)
def test_lexer_negative_float_literal(negative_float_value: str):
    code = f"let x = {negative_float_value}"

    lexer = Lexer(filename="negative_float_literal.sl", lines=[code])
    tokens = lexer.tokenize()

    expected_types: list[Any] = [
        TokenKeyword.LET,
        TokenIdentifier.IDENTIFIER,
        TokenOperator.EQUAL,
        TokenOperator.MINUS,
        TokenLiteral.FLOAT,
        TokenIndentation.NEWLINE,
        TokenIndentation.EOF,
    ]
    assert [token.type for token in tokens] == expected_types
    assert all(isinstance(token.value, str) for token in tokens)
    assert tokens[4].value == negative_float_value[1:]


@pytest.mark.parametrize(
    "complex_value",
    [
        "2 + 3i",
        "1 + 4i",
        "1 + 1i",
        "100 + 10i",
        "5 + 1_000i",
    ],
)
def test_lexer_complex_literal(complex_value: str):
    code = f"let x = {complex_value}"

    lexer = Lexer(filename="complex_literal.sl", lines=[code])
    tokens = lexer.tokenize()

    expected_types: list[Any] = [
        TokenKeyword.LET,
        TokenIdentifier.IDENTIFIER,
        TokenOperator.EQUAL,
        TokenLiteral.INTEGER,
        TokenOperator.PLUS,
        TokenLiteral.COMPLEX,
        TokenIndentation.NEWLINE,
        TokenIndentation.EOF,
    ]
    assert [token.type for token in tokens] == expected_types
    assert all(isinstance(token.value, str) for token in tokens)
    assert tokens[3].value == complex_value.split(" + ")[0]
    assert tokens[5].value == complex_value.split(" + ")[1]


@pytest.mark.parametrize(
    "complex_value",
    [
        "1 - 1i",
        "3 - 4i",
        "10 - 100i",
        "5 - 1_000i",
    ],
)
def test_lexer_negative_complex_literal(complex_value: str):
    code = f"let x = {complex_value}"

    lexer = Lexer(filename="complex_literal.sl", lines=[code])
    tokens = lexer.tokenize()

    expected_types: list[Any] = [
        TokenKeyword.LET,
        TokenIdentifier.IDENTIFIER,
        TokenOperator.EQUAL,
        TokenLiteral.INTEGER,
        TokenOperator.MINUS,
        TokenLiteral.COMPLEX,
        TokenIndentation.NEWLINE,
        TokenIndentation.EOF,
    ]
    assert [token.type for token in tokens] == expected_types
    assert all(isinstance(token.value, str) for token in tokens)
    assert tokens[3].value == complex_value.split(" - ")[0]
    assert tokens[5].value == complex_value.split(" - ")[1]


@pytest.mark.parametrize("complex_value", ["-5-3i", "-1-3i", "-10-10i"])
def test_lexer_negative_only_complex_literal(complex_value: str):
    code = f"let x = {complex_value}"

    lexer = Lexer(filename="negative_only_complex_literal.sl", lines=[code])
    tokens = lexer.tokenize()

    expected_types: list[Any] = [
        TokenKeyword.LET,
        TokenIdentifier.IDENTIFIER,
        TokenOperator.EQUAL,
        TokenOperator.MINUS,
        TokenLiteral.INTEGER,
        TokenOperator.MINUS,
        TokenLiteral.COMPLEX,
        TokenIndentation.NEWLINE,
        TokenIndentation.EOF,
    ]
    assert [token.type for token in tokens] == expected_types
    assert all(isinstance(token.value, str) for token in tokens)
    assert tokens[4].value == complex_value.split("-")[1]
    assert tokens[6].value == complex_value.split("-")[2]


@pytest.mark.parametrize("constant", ["π", "ε", "τ", "e"])
def test_lexer_math_constants(constant: str):
    code = f"let x = {constant}"

    lexer = Lexer(filename="math_constant.sl", lines=[code])
    tokens = lexer.tokenize()

    expected_types: list[Any] = [
        TokenKeyword.LET,
        TokenIdentifier.IDENTIFIER,
        TokenOperator.EQUAL,
        TokenIdentifier.IDENTIFIER,
        TokenIndentation.NEWLINE,
        TokenIndentation.EOF,
    ]
    assert [token.type for token in tokens] == expected_types
    assert all(isinstance(token.value, str) for token in tokens)
    assert tokens[3].value == constant


@pytest.mark.parametrize("lambda_keyword", ["lambda", "LAMBDA", "λ", "Λ"])
def test_lexer_simple_lambda(lambda_keyword: str):
    code = f"const square = {lambda_keyword} x: x * x"

    lexer = Lexer(filename="simple_lambda.sl", lines=[code])
    tokens = lexer.tokenize()

    expected_types: list[Any] = [
        TokenKeyword.CONST,
        TokenIdentifier.IDENTIFIER,
        TokenOperator.EQUAL,
        TokenKeyword.LAMBDA if lambda_keyword.lower() == "lambda" else TokenKeywordSpecial.LAMBDA_SPECIAL,
        TokenIdentifier.IDENTIFIER,
        TokenDelimiter.COLON,
        TokenIdentifier.IDENTIFIER,
        TokenOperator.MULTIPLY,
        TokenIdentifier.IDENTIFIER,
        TokenIndentation.NEWLINE,
        TokenIndentation.EOF,
    ]
    assert [token.type for token in tokens] == expected_types
    assert all(isinstance(token.value, str) for token in tokens)


def test_lexer_lambda():
    code = "let add: callable = lambda a: int32, b: int32 -> int32: a + b"

    lexer = Lexer(filename="lambda.sl", lines=[code])
    tokens = lexer.tokenize()

    expected_types: list[Any] = [
        TokenKeyword.LET,
        TokenIdentifier.IDENTIFIER,
        TokenDelimiter.COLON,
        TokenKeyword.CALLABLE,
        TokenOperator.EQUAL,
        TokenKeyword.LAMBDA,
        TokenIdentifier.IDENTIFIER,
        TokenDelimiter.COLON,
        TokenKeyword.INT32,
        TokenDelimiter.COMMA,
        TokenIdentifier.IDENTIFIER,
        TokenDelimiter.COLON,
        TokenKeyword.INT32,
        TokenOperator.ARROW,
        TokenKeyword.INT32,
        TokenDelimiter.COLON,
        TokenIdentifier.IDENTIFIER,
        TokenOperator.PLUS,
        TokenIdentifier.IDENTIFIER,
        TokenIndentation.NEWLINE,
        TokenIndentation.EOF,
    ]
    assert [token.type for token in tokens] == expected_types
    assert all(isinstance(token.value, str) for token in tokens)


def test_lexer_basic():
    code = """
    fn main():
        print('Hello, World!')
        const x: int32 = 42
        if x > 10:
            return true
        else:
            return false
    """.strip()

    lexer = Lexer(filename="basic.sl", lines=code.splitlines())  # type: ignore
    tokens = lexer.tokenize()

    expected_types: list[Any] = [
        TokenKeyword.FN,
        TokenKeyword.MAIN,
        TokenDelimiter.LPAREN,
        TokenDelimiter.RPAREN,
        TokenDelimiter.COLON,
        TokenIndentation.NEWLINE,
        TokenIndentation.INDENT,
        TokenIdentifier.IDENTIFIER,
        TokenDelimiter.LPAREN,
        TokenLiteral.STRING,
        TokenDelimiter.RPAREN,
        TokenIndentation.NEWLINE,
        TokenKeyword.CONST,
        TokenIdentifier.IDENTIFIER,
        TokenDelimiter.COLON,
        TokenKeyword.INT32,
        TokenOperator.EQUAL,
        TokenLiteral.INTEGER,
        TokenIndentation.NEWLINE,
        TokenKeyword.IF,
        TokenIdentifier.IDENTIFIER,
        TokenOperator.GREATER,
        TokenLiteral.INTEGER,
        TokenDelimiter.COLON,
        TokenIndentation.NEWLINE,
        TokenIndentation.INDENT,
        TokenKeyword.RETURN,
        TokenLiteral.BOOLEAN,
        TokenIndentation.NEWLINE,
        TokenIndentation.DEDENT,
        TokenKeyword.ELSE,
        TokenDelimiter.COLON,
        TokenIndentation.NEWLINE,
        TokenIndentation.INDENT,
        TokenKeyword.RETURN,
        TokenLiteral.BOOLEAN,
        TokenIndentation.NEWLINE,
        TokenIndentation.DEDENT,
        TokenIndentation.DEDENT,
        TokenIndentation.EOF,
    ]
    assert [token.type for token in tokens] == expected_types
    assert all(isinstance(token.value, str) for token in tokens)
