from textwrap import dedent

import pytest

from src.lexer import Lexer, TokenAnnotationTypes, TokenKeyword, TokenOperator
from src.parser import ASTDeclaration, ASTFunctionDeclaration, ASTNode, ASTType, ASTTypeValue, Parser


def test_parser_simple_inline_function():
    code = dedent(
        """
        fn sum(a: int32, b: int32) -> int32:
            return a + b

        fn main() -> none:
            let total: int32 = sum(3, 3)
        """
    )

    lexer = Lexer(filename="simple_inline_function.sigil", lines=code.splitlines())
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = {
        "type": ASTType.PROGRAM,
        "body": [
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(
                type=ASTType.FUNCTION_DECLARATION,
                value=ASTFunctionDeclaration(
                    name="sum",
                    params=[
                        ASTTypeValue(name="a", value=TokenAnnotationTypes.INT32),
                        ASTTypeValue(name="b", value=TokenAnnotationTypes.INT32),
                    ],
                    return_type=TokenAnnotationTypes.INT32,
                ),
                children=[
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.INDENT),
                    ASTNode(
                        type=ASTType.RETURN_STATEMENT,
                        value=TokenKeyword.RETURN,
                        children=[
                            ASTNode(
                                type=ASTType.BINARY_EXPRESSION,
                                value="+",
                                children=[
                                    ASTNode(type=ASTType.IDENTIFIER, value="a"),
                                    ASTNode(type=ASTType.IDENTIFIER, value="b"),
                                ],
                            ),
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.DEDENT),
                ],
            ),
            ASTNode(
                type=ASTType.MAIN_DECLARATION,
                value=ASTFunctionDeclaration(
                    name=TokenKeyword.MAIN,
                    params=[],
                    return_type=TokenAnnotationTypes.NONE,
                ),
                children=[
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.INDENT),
                    ASTNode(
                        type=ASTType.VARIABLE_DECLARATION,
                        value=ASTDeclaration(name="total", var_type=TokenAnnotationTypes.INT32),
                        children=[
                            ASTNode(
                                type=ASTType.CALL_EXPRESSION,
                                value="sum",
                                children=[
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="3"),
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="3"),
                                ],
                            ),
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.DEDENT),
                ],
            ),
            ASTNode(type=ASTType.EOF),
        ],
    }
    assert ast == expected_ast


def test_parser_inline_function_no_params():
    code = dedent(
        """
        fn get_five() -> int32:
            return 5
        fn main() -> none:
            let value: int32 = get_five()
        """
    )

    lexer = Lexer(filename="inline_function_no_params.sigil", lines=code.splitlines())
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = {
        "type": ASTType.PROGRAM,
        "body": [
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(
                type=ASTType.FUNCTION_DECLARATION,
                value=ASTFunctionDeclaration(
                    name="get_five",
                    params=[],
                    return_type=TokenAnnotationTypes.INT32,
                ),
                children=[
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.INDENT),
                    ASTNode(
                        type=ASTType.RETURN_STATEMENT,
                        value=TokenKeyword.RETURN,
                        children=[
                            ASTNode(type=ASTType.NUMBER_LITERAL, value="5"),
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.DEDENT),
                ],
            ),
            ASTNode(
                type=ASTType.MAIN_DECLARATION,
                value=ASTFunctionDeclaration(
                    name=TokenKeyword.MAIN,
                    params=[],
                    return_type=TokenAnnotationTypes.NONE,
                ),
                children=[
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.INDENT),
                    ASTNode(
                        type=ASTType.VARIABLE_DECLARATION,
                        value=ASTDeclaration(name="value", var_type=TokenAnnotationTypes.INT32),
                        children=[
                            ASTNode(
                                type=ASTType.CALL_EXPRESSION,
                                value="get_five",
                                children=[],
                            ),
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.DEDENT),
                ],
            ),
            ASTNode(type=ASTType.EOF),
        ],
    }
    assert ast == expected_ast


def test_parser_inline_function_complex_types():
    code = dedent(
        """
        fn create_complex(real: float64, imag: float64) -> complex:
            return complex_new(real, imag)

        fn main() -> none:
            let c: complex = create_complex(1.0, 2.0)
            if c.real == 1.0 and c.imag == 2.0:
                print('Complex number created successfully!')
        """
    )

    lexer = Lexer(filename="inline_function_complex_types.sigil", lines=code.splitlines())
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = {
        "type": ASTType.PROGRAM,
        "body": [
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(
                type=ASTType.FUNCTION_DECLARATION,
                value=ASTFunctionDeclaration(
                    name="create_complex",
                    params=[
                        ASTTypeValue(name="real", value=TokenAnnotationTypes.FLOAT64),
                        ASTTypeValue(name="imag", value=TokenAnnotationTypes.FLOAT64),
                    ],
                    return_type=TokenAnnotationTypes.COMPLEX,
                ),
                children=[
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.INDENT),
                    ASTNode(
                        type=ASTType.RETURN_STATEMENT,
                        value=TokenKeyword.RETURN,
                        children=[
                            ASTNode(
                                type=ASTType.CALL_EXPRESSION,
                                value="complex_new",
                                children=[
                                    ASTNode(type=ASTType.IDENTIFIER, value="real"),
                                    ASTNode(type=ASTType.IDENTIFIER, value="imag"),
                                ],
                            ),
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.DEDENT),
                ],
            ),
            ASTNode(
                type=ASTType.MAIN_DECLARATION,
                value=ASTFunctionDeclaration(
                    name=TokenKeyword.MAIN,
                    params=[],
                    return_type=TokenAnnotationTypes.NONE,
                ),
                children=[
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.INDENT),
                    ASTNode(
                        type=ASTType.VARIABLE_DECLARATION,
                        value=ASTDeclaration(name="c", var_type=TokenAnnotationTypes.COMPLEX),
                        children=[
                            ASTNode(
                                type=ASTType.CALL_EXPRESSION,
                                value="create_complex",
                                children=[
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="1.0"),
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="2.0"),
                                ],
                            ),
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.IF_STATEMENT,
                        value=ASTNode(
                            type=ASTType.LOGICAL_EXPRESSION,
                            value=TokenKeyword.AND,
                            children=[
                                ASTNode(
                                    type=ASTType.LOGICAL_EXPRESSION,
                                    value=TokenOperator.EQUAL_EQUAL,
                                    children=[
                                        ASTNode(
                                            type=ASTType.CLASS_MEMBER_ACCESS,
                                            value="c",
                                            children=[
                                                ASTNode(
                                                    type=ASTType.CLASS_MEMBER_ACCESS,
                                                    value="real",
                                                ),
                                            ],
                                        ),
                                        ASTNode(type=ASTType.NUMBER_LITERAL, value="1.0"),
                                    ],
                                ),
                                ASTNode(
                                    type=ASTType.LOGICAL_EXPRESSION,
                                    value=TokenOperator.EQUAL_EQUAL,
                                    children=[
                                        ASTNode(
                                            type=ASTType.CLASS_MEMBER_ACCESS,
                                            value="c",
                                            children=[
                                                ASTNode(
                                                    type=ASTType.CLASS_MEMBER_ACCESS,
                                                    value="imag",
                                                ),
                                            ],
                                        ),
                                        ASTNode(type=ASTType.NUMBER_LITERAL, value="2.0"),
                                    ],
                                ),
                            ],
                        ),
                        children=[
                            ASTNode(type=ASTType.INDENT),
                            ASTNode(
                                type=ASTType.CALL_EXPRESSION,
                                value="print",
                                children=[
                                    ASTNode(
                                        type=ASTType.STRING_LITERAL,
                                        value="Complex number created successfully!",
                                    ),
                                ],
                            ),
                            ASTNode(type=ASTType.NEWLINE),
                            ASTNode(type=ASTType.DEDENT),
                        ],
                    ),
                    ASTNode(type=ASTType.DEDENT),
                ],
            ),
            ASTNode(type=ASTType.EOF),
        ],
    }
    assert ast == expected_ast


@pytest.mark.parametrize("lambda_symbol", ["λ", "lambda"])
def test_parser_simple_lambda_function(lambda_symbol):
    code = dedent(
        f"""
        const sum = {lambda_symbol} x, y => x + y

        fn main() -> none:
            const total = sum(2, 2)
        """
    )

    lexer = Lexer(filename="simple_lambda_function.sigil", lines=code.splitlines())
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = {
        "type": ASTType.PROGRAM,
        "body": [
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(
                type=ASTType.VARIABLE_DECLARATION,
                value=ASTDeclaration(name="sum", var_type=TokenAnnotationTypes.NONE),
                children=[
                    ASTNode(
                        type=ASTType.LAMBDA_EXPRESSION,
                        value=ASTFunctionDeclaration(
                            name="<lambda>",
                            params=[
                                ASTTypeValue(name="x", value=TokenAnnotationTypes.NONE),
                                ASTTypeValue(name="y", value=TokenAnnotationTypes.NONE),
                            ],
                            return_type=TokenAnnotationTypes.NONE,
                        ),
                        children=[
                            ASTNode(
                                type=ASTType.BINARY_EXPRESSION,
                                value="+",
                                children=[
                                    ASTNode(type=ASTType.IDENTIFIER, value="x"),
                                    ASTNode(type=ASTType.IDENTIFIER, value="y"),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(
                type=ASTType.MAIN_DECLARATION,
                value=ASTFunctionDeclaration(
                    name=TokenKeyword.MAIN,
                    params=[],
                    return_type=TokenAnnotationTypes.NONE,
                ),
                children=[
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.INDENT),
                    ASTNode(
                        type=ASTType.VARIABLE_DECLARATION,
                        value=ASTDeclaration(name="total", var_type=TokenAnnotationTypes.NONE),
                        children=[
                            ASTNode(
                                type=ASTType.CALL_EXPRESSION,
                                value="sum",
                                children=[
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="2"),
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="2"),
                                ],
                            ),
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.DEDENT),
                ],
            ),
            ASTNode(type=ASTType.EOF),
        ],
    }
    assert ast == expected_ast


@pytest.mark.parametrize("lambda_symbol", ["λ", "lambda"])
def test_parser_lambda_function(lambda_symbol):
    code = dedent(
        f"""
        const sum = {lambda_symbol} x: int32, y: int32 -> int32 => x + y

        fn main() -> none:
            const total = sum(2, 2)
        """
    )

    lexer = Lexer(filename="lambda_function.sigil", lines=code.splitlines())
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = {
        "type": ASTType.PROGRAM,
        "body": [
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(
                type=ASTType.VARIABLE_DECLARATION,
                value=ASTDeclaration(name="sum", var_type=TokenAnnotationTypes.NONE),
                children=[
                    ASTNode(
                        type=ASTType.LAMBDA_EXPRESSION,
                        value=ASTFunctionDeclaration(
                            name="<lambda>",
                            params=[
                                ASTTypeValue(name="x", value=TokenAnnotationTypes.INT32),
                                ASTTypeValue(name="y", value=TokenAnnotationTypes.INT32),
                            ],
                            return_type=TokenAnnotationTypes.INT32,
                        ),
                        children=[
                            ASTNode(
                                type=ASTType.BINARY_EXPRESSION,
                                value="+",
                                children=[
                                    ASTNode(type=ASTType.IDENTIFIER, value="x"),
                                    ASTNode(type=ASTType.IDENTIFIER, value="y"),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(
                type=ASTType.MAIN_DECLARATION,
                value=ASTFunctionDeclaration(
                    name=TokenKeyword.MAIN,
                    params=[],
                    return_type=TokenAnnotationTypes.NONE,
                ),
                children=[
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.INDENT),
                    ASTNode(
                        type=ASTType.VARIABLE_DECLARATION,
                        value=ASTDeclaration(name="total", var_type=TokenAnnotationTypes.NONE),
                        children=[
                            ASTNode(
                                type=ASTType.CALL_EXPRESSION,
                                value="sum",
                                children=[
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="2"),
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="2"),
                                ],
                            ),
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.DEDENT),
                ],
            ),
            ASTNode(type=ASTType.EOF),
        ],
    }
    assert ast == expected_ast
