from textwrap import dedent

from src.lexer import Lexer, TokenAnnotationTypes, TokenKeyword, TokenOperator
from src.parser import ASTDeclaration, ASTFunctionDeclaration, ASTNode, ASTType, ASTTypeValue, Parser


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
                value=ASTDeclaration(name="x", var_type=TokenAnnotationTypes.NONE),
                children=[
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
                value=ASTDeclaration(name="x", var_type=TokenAnnotationTypes.NONE),
                children=[
                    ASTNode(type=ASTType.NUMBER_LITERAL, value="10"),
                ],
            ),
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(
                type=ASTType.VARIABLE_DECLARATION,
                value=ASTDeclaration(name="y", var_type=TokenAnnotationTypes.NONE),
                children=[
                    ASTNode(type=ASTType.NUMBER_LITERAL, value="20"),
                ],
            ),
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(
                type=ASTType.VARIABLE_DECLARATION,
                value=ASTDeclaration(name="z", var_type=TokenAnnotationTypes.NONE),
                children=[
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
                value=ASTDeclaration(name="x", var_type=TokenAnnotationTypes.NONE),
                children=[
                    ASTNode(
                        type=ASTType.BINARY_EXPRESSION,
                        children=[
                            ASTNode(
                                type=ASTType.BINARY_EXPRESSION,
                                children=[
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="10"),
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="5"),
                                ],
                                value=TokenOperator.PLUS,
                            ),
                            ASTNode(type=ASTType.NUMBER_LITERAL, value="2"),
                        ],
                        value=TokenOperator.MULTIPLY,
                    ),
                ],
            ),
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(
                type=ASTType.VARIABLE_DECLARATION,
                value=ASTDeclaration(name="y", var_type=TokenAnnotationTypes.NONE),
                children=[
                    ASTNode(
                        type=ASTType.BINARY_EXPRESSION,
                        children=[
                            ASTNode(
                                type=ASTType.BINARY_EXPRESSION,
                                children=[
                                    ASTNode(type=ASTType.IDENTIFIER, value="x"),
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="3"),
                                ],
                                value=TokenOperator.DIVIDE,
                            ),
                            ASTNode(type=ASTType.NUMBER_LITERAL, value="4"),
                        ],
                        value=TokenOperator.MINUS,
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
                value=ASTDeclaration(name="result", var_type=TokenAnnotationTypes.NONE),
                children=[
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
                                        value=TokenOperator.PLUS,
                                    ),
                                    ASTNode(
                                        type=ASTType.BINARY_EXPRESSION,
                                        children=[
                                            ASTNode(type=ASTType.NUMBER_LITERAL, value="10"),
                                            ASTNode(type=ASTType.NUMBER_LITERAL, value="2"),
                                        ],
                                        value=TokenOperator.MINUS,
                                    ),
                                ],
                                value=TokenOperator.MULTIPLY,
                            ),
                            ASTNode(type=ASTType.NUMBER_LITERAL, value="4"),
                        ],
                        value=TokenOperator.DIVIDE,
                    ),
                ],
            ),
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(
                type=ASTType.VARIABLE_DECLARATION,
                value=ASTDeclaration(name="final", var_type=TokenAnnotationTypes.NONE),
                children=[
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
                                        value=TokenOperator.MULTIPLY,
                                    ),
                                ],
                                value=TokenOperator.PLUS,
                            ),
                            ASTNode(type=ASTType.NUMBER_LITERAL, value="1"),
                        ],
                        value=TokenOperator.MINUS,
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
                print('Equal')
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
                value=ASTFunctionDeclaration(name=TokenKeyword.MAIN, params=[], return_type=TokenAnnotationTypes.NONE),
                children=[
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.INDENT),
                    ASTNode(
                        type=ASTType.VARIABLE_DECLARATION,
                        value=ASTDeclaration(name="x", var_type=TokenAnnotationTypes.COMPLEX),
                        children=[
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
                        value=ASTDeclaration(name="y", var_type=TokenAnnotationTypes.COMPLEX),
                        children=[
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
                        value=ASTDeclaration(name="sum", var_type=TokenAnnotationTypes.COMPLEX),
                        children=[
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
                        value=ASTDeclaration(name="total", var_type=TokenAnnotationTypes.NONE),
                        children=[
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
                        value=ASTNode(
                            type=ASTType.LOGICAL_EXPRESSION,
                            children=[
                                ASTNode(type=ASTType.IDENTIFIER, value="sum"),
                                ASTNode(type=ASTType.IDENTIFIER, value="total"),
                            ],
                            value=TokenOperator.EQUAL_EQUAL,
                        ),
                        children=[
                            ASTNode(type=ASTType.INDENT),
                            ASTNode(
                                type=ASTType.CALL_EXPRESSION,
                                children=[
                                    ASTNode(type=ASTType.STRING_LITERAL, value="Equal"),
                                ],
                                value="print",
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


def test_parser_if_with_more_logical_checks():
    code = dedent(
        """\
        fn main() -> none:
            let x: string = 'a'
            let y: int32 = 2
            let z: bool = true
            if x == 'a' and y != 3 or z:
                print('Equal')
        """
    )

    lexer = Lexer(filename="if_with_more_logical_checks.sigil", lines=code.splitlines())
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = {
        "type": ASTType.PROGRAM,
        "body": [
            ASTNode(
                type=ASTType.MAIN_DECLARATION,
                value=ASTFunctionDeclaration(name=TokenKeyword.MAIN, params=[], return_type=TokenAnnotationTypes.NONE),
                children=[
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.INDENT),
                    ASTNode(
                        type=ASTType.VARIABLE_DECLARATION,
                        value=ASTDeclaration(name="x", var_type=TokenAnnotationTypes.STRING),
                        children=[
                            ASTNode(type=ASTType.STRING_LITERAL, value="a"),
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.VARIABLE_DECLARATION,
                        value=ASTDeclaration(name="y", var_type=TokenAnnotationTypes.INT32),
                        children=[
                            ASTNode(type=ASTType.NUMBER_LITERAL, value="2"),
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.VARIABLE_DECLARATION,
                        value=ASTDeclaration(name="z", var_type=TokenAnnotationTypes.BOOL),
                        children=[
                            ASTNode(type=ASTType.BOOLEAN_LITERAL, value="true"),
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.IF_STATEMENT,
                        value=ASTNode(
                            type=ASTType.LOGICAL_EXPRESSION,
                            children=[
                                ASTNode(
                                    type=ASTType.LOGICAL_EXPRESSION,
                                    value=TokenKeyword.AND,
                                    children=[
                                        ASTNode(
                                            type=ASTType.LOGICAL_EXPRESSION,
                                            value=TokenOperator.EQUAL_EQUAL,
                                            children=[
                                                ASTNode(type=ASTType.IDENTIFIER, value="x"),
                                                ASTNode(type=ASTType.STRING_LITERAL, value="a"),
                                            ],
                                        ),
                                        ASTNode(
                                            type=ASTType.LOGICAL_EXPRESSION,
                                            value=TokenOperator.NOT_EQUAL,
                                            children=[
                                                ASTNode(type=ASTType.IDENTIFIER, value="y"),
                                                ASTNode(type=ASTType.NUMBER_LITERAL, value="3"),
                                            ],
                                        ),
                                    ],
                                ),
                                ASTNode(
                                    type=ASTType.IDENTIFIER,
                                    value="z",
                                ),
                            ],
                            value=TokenKeyword.OR,
                        ),
                        children=[
                            ASTNode(type=ASTType.INDENT),
                            ASTNode(
                                type=ASTType.CALL_EXPRESSION,
                                children=[
                                    ASTNode(type=ASTType.STRING_LITERAL, value="Equal"),
                                ],
                                value="print",
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


def test_parser_function_call():
    code = dedent(
        """\
        fn main() -> none:
            let result = add(5, 10)
            print(result)
        """
    )

    lexer = Lexer(filename="function_call.sigil", lines=code.splitlines())
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = {
        "type": ASTType.PROGRAM,
        "body": [
            ASTNode(
                type=ASTType.MAIN_DECLARATION,
                value=ASTFunctionDeclaration(name=TokenKeyword.MAIN, params=[], return_type=TokenAnnotationTypes.NONE),
                children=[
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.INDENT),
                    ASTNode(
                        type=ASTType.VARIABLE_DECLARATION,
                        value=ASTDeclaration(name="result", var_type=TokenAnnotationTypes.NONE),
                        children=[
                            ASTNode(
                                type=ASTType.CALL_EXPRESSION,
                                value="add",
                                children=[
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="5"),
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="10"),
                                ],
                            ),
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.CALL_EXPRESSION,
                        value="print",
                        children=[
                            ASTNode(type=ASTType.IDENTIFIER, value="result"),
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


def test_parser_function_call_no_args():
    code = dedent(
        """\
        fn main() -> none:
            greet()
        """
    )

    lexer = Lexer(filename="function_call_no_args.sigil", lines=code.splitlines())
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = {
        "type": ASTType.PROGRAM,
        "body": [
            ASTNode(
                type=ASTType.MAIN_DECLARATION,
                value=ASTFunctionDeclaration(name=TokenKeyword.MAIN, params=[], return_type=TokenAnnotationTypes.NONE),
                children=[
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.INDENT),
                    ASTNode(
                        type=ASTType.CALL_EXPRESSION,
                        value="greet",
                        children=[],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.DEDENT),
                ],
            ),
            ASTNode(type=ASTType.EOF),
        ],
    }
    assert ast == expected_ast


def test_parser_function_call_nested():
    code = dedent(
        """\
        fn main() -> none:
            let result = multiply(add(2, 3), 4)
            print(result)
        """
    )

    lexer = Lexer(filename="function_call_nested.sigil", lines=code.splitlines())
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = {
        "type": ASTType.PROGRAM,
        "body": [
            ASTNode(
                type=ASTType.MAIN_DECLARATION,
                value=ASTFunctionDeclaration(name=TokenKeyword.MAIN, params=[], return_type=TokenAnnotationTypes.NONE),
                children=[
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.INDENT),
                    ASTNode(
                        type=ASTType.VARIABLE_DECLARATION,
                        value=ASTDeclaration(name="result", var_type=TokenAnnotationTypes.NONE),
                        children=[
                            ASTNode(
                                type=ASTType.CALL_EXPRESSION,
                                value="multiply",
                                children=[
                                    ASTNode(
                                        type=ASTType.CALL_EXPRESSION,
                                        value="add",
                                        children=[
                                            ASTNode(type=ASTType.NUMBER_LITERAL, value="2"),
                                            ASTNode(type=ASTType.NUMBER_LITERAL, value="3"),
                                        ],
                                    ),
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="4"),
                                ],
                            ),
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.CALL_EXPRESSION,
                        value="print",
                        children=[
                            ASTNode(type=ASTType.IDENTIFIER, value="result"),
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


def test_parser_function_call_with_expression_args():
    code = dedent(
        """\
        fn main() -> none:
            let result = add(5 * 2, 10 - 3)
            print(result)
        """
    )

    lexer = Lexer(filename="function_call_with_expression_args.sigil", lines=code.splitlines())
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = {
        "type": ASTType.PROGRAM,
        "body": [
            ASTNode(
                type=ASTType.MAIN_DECLARATION,
                value=ASTFunctionDeclaration(name=TokenKeyword.MAIN, params=[], return_type=TokenAnnotationTypes.NONE),
                children=[
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.INDENT),
                    ASTNode(
                        type=ASTType.VARIABLE_DECLARATION,
                        value=ASTDeclaration(name="result", var_type=TokenAnnotationTypes.NONE),
                        children=[
                            ASTNode(
                                type=ASTType.CALL_EXPRESSION,
                                value="add",
                                children=[
                                    ASTNode(
                                        type=ASTType.BINARY_EXPRESSION,
                                        value="*",
                                        children=[
                                            ASTNode(type=ASTType.NUMBER_LITERAL, value="5"),
                                            ASTNode(type=ASTType.NUMBER_LITERAL, value="2"),
                                        ],
                                    ),
                                    ASTNode(
                                        type=ASTType.BINARY_EXPRESSION,
                                        value="-",
                                        children=[
                                            ASTNode(type=ASTType.NUMBER_LITERAL, value="10"),
                                            ASTNode(type=ASTType.NUMBER_LITERAL, value="3"),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.CALL_EXPRESSION,
                        value="print",
                        children=[
                            ASTNode(type=ASTType.IDENTIFIER, value="result"),
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


def test_parser_create_multiple_functions():
    code = dedent(
        """\
        fn add(a: int32, b: int32) -> int32:
            return a + b
        
        fn main() -> none:
            let result = add(5, 10)
            print(result)
        """
    )

    lexer = Lexer(filename="create_multiple_functions.sigil", lines=code.splitlines())
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = {
        "type": ASTType.PROGRAM,
        "body": [
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
                value=ASTFunctionDeclaration(name=TokenKeyword.MAIN, params=[], return_type=TokenAnnotationTypes.NONE),
                children=[
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.INDENT),
                    ASTNode(
                        type=ASTType.VARIABLE_DECLARATION,
                        value=ASTDeclaration(name="result", var_type=TokenAnnotationTypes.NONE),
                        children=[
                            ASTNode(
                                type=ASTType.CALL_EXPRESSION,
                                value="add",
                                children=[
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="5"),
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="10"),
                                ],
                            ),
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.CALL_EXPRESSION,
                        value="print",
                        children=[
                            ASTNode(type=ASTType.IDENTIFIER, value="result"),
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
