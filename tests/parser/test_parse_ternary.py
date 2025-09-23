from textwrap import dedent

from src.lexer import Lexer, TokenAnnotationTypes, TokenKeyword, TokenOperator
from src.parser import ASTDeclaration, ASTFunctionDeclaration, ASTNode, ASTType, Parser


def test_parse_simple_ternary():
    code = dedent(
        """
        fn main() -> none:
            let a: int32 = 3
            let total: int32 = a ? a <= 3 : 10
        """
    )

    lexer = Lexer(filename="simple_ternary.sigil", lines=code.splitlines())
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = {
        "type": ASTType.PROGRAM,
        "body": [
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
                        value=ASTDeclaration(name="a", var_type=TokenAnnotationTypes.INT32),
                        children=[ASTNode(type=ASTType.NUMBER_LITERAL, value="3")],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.VARIABLE_DECLARATION,
                        value=ASTDeclaration(name="total", var_type=TokenAnnotationTypes.INT32),
                        children=[
                            ASTNode(
                                type=ASTType.TERNARY_EXPRESSION,
                                children=[
                                    ASTNode(type=ASTType.IDENTIFIER, value="a"),
                                    ASTNode(
                                        type=ASTType.LOGICAL_EXPRESSION,
                                        value=TokenOperator.LESS_EQUAL,
                                        children=[
                                            ASTNode(type=ASTType.IDENTIFIER, value="a"),
                                            ASTNode(type=ASTType.NUMBER_LITERAL, value="3"),
                                        ],
                                    ),
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="10"),
                                    ASTNode(type=ASTType.NEWLINE),
                                    ASTNode(type=ASTType.DEDENT),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            ASTNode(type=ASTType.EOF),
        ],
    }
    assert ast == expected_ast


def test_parse_complex_ternary():
    code = dedent(
        """
        fn main() -> none:
            let a: int32 = 3
            let total: int32 = a ? a <= 3 ? 5 : 10 : 20

            if a <= 3:
                print('a is less than or equal to 3')
        """
    )

    lexer = Lexer(filename="complex_ternary.sigil", lines=code.splitlines())
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = {
        "type": ASTType.PROGRAM,
        "body": [
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
                        value=ASTDeclaration(name="a", var_type=TokenAnnotationTypes.INT32),
                        children=[ASTNode(type=ASTType.NUMBER_LITERAL, value="3")],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.VARIABLE_DECLARATION,
                        value=ASTDeclaration(name="total", var_type=TokenAnnotationTypes.INT32),
                        children=[
                            ASTNode(
                                type=ASTType.TERNARY_EXPRESSION,
                                children=[
                                    ASTNode(type=ASTType.IDENTIFIER, value="a"),
                                    ASTNode(
                                        type=ASTType.TERNARY_EXPRESSION,
                                        children=[
                                            ASTNode(
                                                type=ASTType.LOGICAL_EXPRESSION,
                                                value=TokenOperator.LESS_EQUAL,
                                                children=[
                                                    ASTNode(type=ASTType.IDENTIFIER, value="a"),
                                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="3"),
                                                ],
                                            ),
                                            ASTNode(type=ASTType.NUMBER_LITERAL, value="5"),
                                            ASTNode(type=ASTType.NUMBER_LITERAL, value="10"),
                                        ],
                                    ),
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="20"),
                                    ASTNode(type=ASTType.NEWLINE),
                                    ASTNode(type=ASTType.NEWLINE),
                                ],
                            ),
                        ],
                    ),
                    ASTNode(
                        type=ASTType.IF_STATEMENT,
                        value=ASTNode(
                            type=ASTType.LOGICAL_EXPRESSION,
                            value=TokenOperator.LESS_EQUAL,
                            children=[
                                ASTNode(type=ASTType.IDENTIFIER, value="a"),
                                ASTNode(type=ASTType.NUMBER_LITERAL, value="3"),
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
                                        value="a is less than or equal to 3",
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


def test_parse_multi_line_complex_ternary():
    code = dedent(
        """
        fn main() -> none:
            let a: int32 = 3
            let total: int32 = a ? 
                a <= 3 ? 5 
                    : 10 
                : 20
            if a <= 3:
                print('a is less than or equal to 3')
        """
    )

    lexer = Lexer(filename="complex_ternary.sigil", lines=code.splitlines())
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = {
        "type": ASTType.PROGRAM,
        "body": [
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
                        value=ASTDeclaration(name="a", var_type=TokenAnnotationTypes.INT32),
                        children=[ASTNode(type=ASTType.NUMBER_LITERAL, value="3")],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.VARIABLE_DECLARATION,
                        value=ASTDeclaration(name="total", var_type=TokenAnnotationTypes.INT32),
                        children=[
                            ASTNode(
                                type=ASTType.TERNARY_EXPRESSION,
                                children=[
                                    ASTNode(type=ASTType.IDENTIFIER, value="a"),
                                    ASTNode(type=ASTType.NEWLINE),
                                    ASTNode(type=ASTType.INDENT),
                                    ASTNode(
                                        type=ASTType.TERNARY_EXPRESSION,
                                        children=[
                                            ASTNode(
                                                type=ASTType.LOGICAL_EXPRESSION,
                                                value=TokenOperator.LESS_EQUAL,
                                                children=[
                                                    ASTNode(type=ASTType.IDENTIFIER, value="a"),
                                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="3"),
                                                ],
                                            ),
                                            ASTNode(type=ASTType.NUMBER_LITERAL, value="5"),
                                            ASTNode(type=ASTType.NEWLINE),
                                            ASTNode(type=ASTType.INDENT),
                                            ASTNode(type=ASTType.NUMBER_LITERAL, value="10"),
                                            ASTNode(type=ASTType.NEWLINE),
                                            ASTNode(type=ASTType.DEDENT),
                                        ],
                                    ),
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="20"),
                                    ASTNode(type=ASTType.NEWLINE),
                                    ASTNode(type=ASTType.DEDENT),
                                ],
                            ),
                        ],
                    ),
                    ASTNode(
                        type=ASTType.IF_STATEMENT,
                        value=ASTNode(
                            type=ASTType.LOGICAL_EXPRESSION,
                            value=TokenOperator.LESS_EQUAL,
                            children=[
                                ASTNode(type=ASTType.IDENTIFIER, value="a"),
                                ASTNode(type=ASTType.NUMBER_LITERAL, value="3"),
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
                                        value="a is less than or equal to 3",
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
