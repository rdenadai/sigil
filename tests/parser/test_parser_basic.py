from textwrap import dedent

from src.lexer.lexer import Lexer
from src.lexer.token import TokenKeyword
from src.parser.parser import ASTNode, ASTType, Parser


def test_parser_simple_declaration_expression():
    code = "let x = 42".strip()

    lexer = Lexer(filename="simple_declaration.sigil", lines=[code])
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = {
        "type": ASTType.PROGRAM,
        "body": [
            ASTNode(
                type=ASTType.VARIABLE_DECLARATION,
                children=[
                    ASTNode(type=ASTType.IDENTIFIER, value="x"),
                    ASTNode(type=ASTType.NUMBER_LITERAL, value="42"),
                ],
            ),
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(type=ASTType.EOF),
        ],
    }

    assert ast == expected_ast


def test_parser_multiple_statements():
    code = dedent(
        """\
        let x = 10
        let y = 20
        let z = x + y
        """
    )

    lexer = Lexer(filename="multiple_statements.sigil", lines=code.splitlines())
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = {
        "type": ASTType.PROGRAM,
        "body": [
            ASTNode(
                type=ASTType.VARIABLE_DECLARATION,
                children=[
                    ASTNode(type=ASTType.IDENTIFIER, value="x"),
                    ASTNode(type=ASTType.NUMBER_LITERAL, value="10"),
                ],
            ),
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(
                type=ASTType.VARIABLE_DECLARATION,
                children=[
                    ASTNode(type=ASTType.IDENTIFIER, value="y"),
                    ASTNode(type=ASTType.NUMBER_LITERAL, value="20"),
                ],
            ),
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(
                type=ASTType.VARIABLE_DECLARATION,
                children=[
                    ASTNode(type=ASTType.IDENTIFIER, value="z"),
                    ASTNode(
                        type=ASTType.BINARY_EXPRESSION,
                        children=[
                            ASTNode(type=ASTType.IDENTIFIER, value="x"),
                            ASTNode(type=ASTType.IDENTIFIER, value="y"),
                        ],
                        value="+",
                    ),
                ],
            ),
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(type=ASTType.EOF),
        ],
    }
    assert ast == expected_ast


def test_parser_multiple_statements_with_parentheses():
    code = dedent(
        """\
        let x = (10 + 5) * 2
        let y = x / 3 - 4
        """
    )

    lexer = Lexer(filename="multiple_statements_parentheses.sigil", lines=code.splitlines())
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = {
        "type": ASTType.PROGRAM,
        "body": [
            ASTNode(
                type=ASTType.VARIABLE_DECLARATION,
                children=[
                    ASTNode(type=ASTType.IDENTIFIER, value="x"),
                    ASTNode(
                        type=ASTType.BINARY_EXPRESSION,
                        children=[
                            ASTNode(
                                type=ASTType.BINARY_EXPRESSION,
                                children=[
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="10"),
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="5"),
                                ],
                                value="+",
                            ),
                            ASTNode(type=ASTType.NUMBER_LITERAL, value="2"),
                        ],
                        value="*",
                    ),
                ],
            ),
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(
                type=ASTType.VARIABLE_DECLARATION,
                children=[
                    ASTNode(type=ASTType.IDENTIFIER, value="y"),
                    ASTNode(
                        type=ASTType.BINARY_EXPRESSION,
                        children=[
                            ASTNode(
                                type=ASTType.BINARY_EXPRESSION,
                                children=[
                                    ASTNode(type=ASTType.IDENTIFIER, value="x"),
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="3"),
                                ],
                                value="/",
                            ),
                            ASTNode(type=ASTType.NUMBER_LITERAL, value="4"),
                        ],
                        value="-",
                    ),
                ],
            ),
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(type=ASTType.EOF),
        ],
    }
    assert ast == expected_ast


def test_parser_complex_statements_with_parentheses():
    code = dedent(
        """\
        let result = (5 + 3) * (10 - 2) / 4
        let final = result + (result * 2) - 1
        """
    )

    lexer = Lexer(filename="complex_statements_parentheses.sigil", lines=code.splitlines())
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = {
        "type": ASTType.PROGRAM,
        "body": [
            ASTNode(
                type=ASTType.VARIABLE_DECLARATION,
                children=[
                    ASTNode(type=ASTType.IDENTIFIER, value="result"),
                    ASTNode(
                        type=ASTType.BINARY_EXPRESSION,
                        children=[
                            ASTNode(
                                type=ASTType.BINARY_EXPRESSION,
                                children=[
                                    ASTNode(
                                        type=ASTType.BINARY_EXPRESSION,
                                        children=[
                                            ASTNode(type=ASTType.NUMBER_LITERAL, value="5"),
                                            ASTNode(type=ASTType.NUMBER_LITERAL, value="3"),
                                        ],
                                        value="+",
                                    ),
                                    ASTNode(
                                        type=ASTType.BINARY_EXPRESSION,
                                        children=[
                                            ASTNode(type=ASTType.NUMBER_LITERAL, value="10"),
                                            ASTNode(type=ASTType.NUMBER_LITERAL, value="2"),
                                        ],
                                        value="-",
                                    ),
                                ],
                                value="*",
                            ),
                            ASTNode(type=ASTType.NUMBER_LITERAL, value="4"),
                        ],
                        value="/",
                    ),
                ],
            ),
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(
                type=ASTType.VARIABLE_DECLARATION,
                children=[
                    ASTNode(type=ASTType.IDENTIFIER, value="final"),
                    ASTNode(
                        type=ASTType.BINARY_EXPRESSION,
                        children=[
                            ASTNode(
                                type=ASTType.BINARY_EXPRESSION,
                                children=[
                                    ASTNode(type=ASTType.IDENTIFIER, value="result"),
                                    ASTNode(
                                        type=ASTType.BINARY_EXPRESSION,
                                        children=[
                                            ASTNode(type=ASTType.IDENTIFIER, value="result"),
                                            ASTNode(type=ASTType.NUMBER_LITERAL, value="2"),
                                        ],
                                        value="*",
                                    ),
                                ],
                                value="+",
                            ),
                            ASTNode(type=ASTType.NUMBER_LITERAL, value="1"),
                        ],
                        value="-",
                    ),
                ],
            ),
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(type=ASTType.EOF),
        ],
    }
    assert ast == expected_ast


def test_parser_main_and_complex_numbers():
    code = dedent(
        """\
        fn main() -> none:
            let x: complex = 10 + 2i
            let y: complex = 2 - 5i
            let sum: complex = x + y
            const total = 12 - 3i
            if sum == total:
                2 and 2
        """
    )

    lexer = Lexer(filename="main_and_complex_numbers.sigil", lines=code.splitlines())
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = {
        "type": ASTType.PROGRAM,
        "body": [
            ASTNode(
                type=ASTType.MAIN_DECLARATION,
                value=TokenKeyword.MAIN,
                children=[
                    ASTNode(
                        type=ASTType.VARIABLE_DECLARATION,
                        children=[
                            ASTNode(type=ASTType.IDENTIFIER, value="x"),
                            ASTNode(
                                type=ASTType.BINARY_EXPRESSION,
                                children=[
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="10"),
                                    ASTNode(type=ASTType.COMPLEX_LITERAL, value="2i"),
                                ],
                                value="+",
                            ),
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.VARIABLE_DECLARATION,
                        children=[
                            ASTNode(type=ASTType.IDENTIFIER, value="y"),
                            ASTNode(
                                type=ASTType.BINARY_EXPRESSION,
                                children=[
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="2"),
                                    ASTNode(type=ASTType.COMPLEX_LITERAL, value="5i"),
                                ],
                                value="-",
                            ),
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.VARIABLE_DECLARATION,
                        children=[
                            ASTNode(type=ASTType.IDENTIFIER, value="sum"),
                            ASTNode(
                                type=ASTType.BINARY_EXPRESSION,
                                children=[
                                    ASTNode(type=ASTType.IDENTIFIER, value="x"),
                                    ASTNode(type=ASTType.IDENTIFIER, value="y"),
                                ],
                                value="+",
                            ),
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.VARIABLE_DECLARATION,
                        children=[
                            ASTNode(type=ASTType.IDENTIFIER, value="total"),
                            ASTNode(
                                type=ASTType.BINARY_EXPRESSION,
                                children=[
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="12"),
                                    ASTNode(type=ASTType.COMPLEX_LITERAL, value="3i"),
                                ],
                                value="-",
                            ),
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.IF_STATEMENT,
                        children=[
                            ASTNode(
                                type=ASTType.LOGICAL_EXPRESSION,
                                children=[
                                    ASTNode(type=ASTType.IDENTIFIER, value="sum"),
                                    ASTNode(type=ASTType.IDENTIFIER, value="total"),
                                ],
                                value="==",
                            ),
                            ASTNode(
                                type=ASTType.LOGICAL_EXPRESSION,
                                children=[
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="2"),
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="2"),
                                ],
                                value="and",
                            ),
                            ASTNode(type=ASTType.NEWLINE),
                        ],
                    ),
                ],
            ),
            ASTNode(type=ASTType.EOF),
        ],
    }
    assert ast == expected_ast
