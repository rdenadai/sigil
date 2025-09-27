from textwrap import dedent

from src.lexer import Lexer, TokenAnnotationTypes, TokenKeyword, TokenOperator
from src.parser import ASTDeclaration, ASTFunctionDeclaration, ASTNode, ASTType, ASTTypeValue, Parser


def test_parse_simple_multi_line_ifs():
    code = dedent(
        """
        fn main() -> none:
            let a: int32 = 3
            if a <= 3:
                print('a is less than or equal to 3')
            else:
                if a > 5:
                    print('a is greater than 5')
                else:
                    print('a is between 4 and 5')
            
            let b: int32 = 10
            if b < 5:
                print('b is less than 5')
        """
    )

    lexer = Lexer(filename="simple_multi_line_ifs.sigil", lines=code.splitlines())
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
                                    )
                                ],
                            ),
                            ASTNode(type=ASTType.NEWLINE),
                            ASTNode(type=ASTType.DEDENT),
                            ASTNode(
                                type=ASTType.ELSE_STATEMENT,
                                children=[
                                    ASTNode(type=ASTType.INDENT),
                                    ASTNode(
                                        type=ASTType.IF_STATEMENT,
                                        value=ASTNode(
                                            type=ASTType.LOGICAL_EXPRESSION,
                                            value=TokenOperator.GREATER,
                                            children=[
                                                ASTNode(type=ASTType.IDENTIFIER, value="a"),
                                                ASTNode(type=ASTType.NUMBER_LITERAL, value="5"),
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
                                                        value="a is greater than 5",
                                                    )
                                                ],
                                            ),
                                            ASTNode(type=ASTType.NEWLINE),
                                            ASTNode(type=ASTType.DEDENT),
                                            ASTNode(
                                                type=ASTType.ELSE_STATEMENT,
                                                children=[
                                                    ASTNode(type=ASTType.INDENT),
                                                    ASTNode(
                                                        type=ASTType.CALL_EXPRESSION,
                                                        value="print",
                                                        children=[
                                                            ASTNode(
                                                                type=ASTType.STRING_LITERAL,
                                                                value="a is between 4 and 5",
                                                            )
                                                        ],
                                                    ),
                                                    ASTNode(type=ASTType.NEWLINE),
                                                    ASTNode(type=ASTType.NEWLINE),
                                                    ASTNode(type=ASTType.DEDENT),
                                                ],
                                            ),
                                        ],
                                    ),
                                    ASTNode(type=ASTType.DEDENT),
                                ],
                            ),
                        ],
                    ),
                    ASTNode(
                        type=ASTType.VARIABLE_DECLARATION,
                        value=ASTDeclaration(name="b", var_type=TokenAnnotationTypes.INT32),
                        children=[ASTNode(type=ASTType.NUMBER_LITERAL, value="10")],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.IF_STATEMENT,
                        value=ASTNode(
                            type=ASTType.LOGICAL_EXPRESSION,
                            value=TokenOperator.LESS,
                            children=[
                                ASTNode(type=ASTType.IDENTIFIER, value="b"),
                                ASTNode(type=ASTType.NUMBER_LITERAL, value="5"),
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
                                        value="b is less than 5",
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


def test_parse_simple_multi_line_ifs_with_internal_assignments():
    code = dedent(
        """
        fn main() -> none:
            let a: int32 = 3
            let total: int32 = 0
            if a <= 3:
                total = 10
            else:
                if a > 3:
                    total = 20
                else:
                    total = 30
        """
    )

    lexer = Lexer(filename="simple_multi_line_ifs.sigil", lines=code.splitlines())
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
                        children=[ASTNode(type=ASTType.NUMBER_LITERAL, value="0")],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
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
                                type=ASTType.ASSIGNMENT_EXPRESSION,
                                children=[
                                    ASTNode(type=ASTType.IDENTIFIER, value="total"),
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="10"),
                                ],
                            ),
                            ASTNode(type=ASTType.NEWLINE),
                            ASTNode(type=ASTType.DEDENT),
                            ASTNode(
                                type=ASTType.ELSE_STATEMENT,
                                children=[
                                    ASTNode(type=ASTType.INDENT),
                                    ASTNode(
                                        type=ASTType.IF_STATEMENT,
                                        value=ASTNode(
                                            type=ASTType.LOGICAL_EXPRESSION,
                                            value=TokenOperator.GREATER,
                                            children=[
                                                ASTNode(type=ASTType.IDENTIFIER, value="a"),
                                                ASTNode(type=ASTType.NUMBER_LITERAL, value="3"),
                                            ],
                                        ),
                                        children=[
                                            ASTNode(type=ASTType.INDENT),
                                            ASTNode(
                                                type=ASTType.ASSIGNMENT_EXPRESSION,
                                                children=[
                                                    ASTNode(type=ASTType.IDENTIFIER, value="total"),
                                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="20"),
                                                ],
                                            ),
                                            ASTNode(type=ASTType.NEWLINE),
                                            ASTNode(type=ASTType.DEDENT),
                                            ASTNode(
                                                type=ASTType.ELSE_STATEMENT,
                                                children=[
                                                    ASTNode(type=ASTType.INDENT),
                                                    ASTNode(
                                                        type=ASTType.ASSIGNMENT_EXPRESSION,
                                                        children=[
                                                            ASTNode(type=ASTType.IDENTIFIER, value="total"),
                                                            ASTNode(type=ASTType.NUMBER_LITERAL, value="30"),
                                                        ],
                                                    ),
                                                    ASTNode(type=ASTType.NEWLINE),
                                                    ASTNode(type=ASTType.DEDENT),
                                                ],
                                            ),
                                        ],
                                    ),
                                    ASTNode(type=ASTType.DEDENT),
                                ],
                            ),
                        ],
                    ),
                    ASTNode(type=ASTType.DEDENT),
                ],
            ),
            ASTNode(type=ASTType.EOF),
        ],
    }
    assert ast == expected_ast


def test_parse_simple_multi_line_functions():
    code = dedent(
        """
        fn add(a: int32, b: int32) -> int32:
            return a + b


        fn main() -> none:
            if add(2, 3) == 5:
                print('2 + 3 is 5')
        """
    )

    lexer = Lexer(filename="simple_multi_line_functions.sigil", lines=code.splitlines())
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
                    name="add",
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
                                value=TokenOperator.PLUS,
                                children=[
                                    ASTNode(type=ASTType.IDENTIFIER, value="a"),
                                    ASTNode(type=ASTType.IDENTIFIER, value="b"),
                                ],
                            )
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
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
                        type=ASTType.IF_STATEMENT,
                        value=ASTNode(
                            type=ASTType.LOGICAL_EXPRESSION,
                            value=TokenOperator.EQUAL_EQUAL,
                            children=[
                                ASTNode(
                                    type=ASTType.CALL_EXPRESSION,
                                    value="add",
                                    children=[
                                        ASTNode(type=ASTType.NUMBER_LITERAL, value="2"),
                                        ASTNode(type=ASTType.NUMBER_LITERAL, value="3"),
                                    ],
                                ),
                                ASTNode(type=ASTType.NUMBER_LITERAL, value="5"),
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
                                        value="2 + 3 is 5",
                                    )
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
