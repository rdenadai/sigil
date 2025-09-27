from textwrap import dedent

from src.lexer import Lexer, TokenAnnotationTypes, TokenKeyword
from src.parser import ASTDeclaration, ASTFunctionDeclaration, ASTNode, ASTType, Parser


def test_parser_simple_strings():
    code = dedent(
        """
        fn main() -> none:
            let greeting: string = 'Hello, World!'
        """
    )

    lexer = Lexer(filename="simple_strings.sigil", lines=code.splitlines())
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
                        value=ASTDeclaration(name="greeting", var_type=TokenAnnotationTypes.STRING),
                        children=[
                            ASTNode(type=ASTType.STRING_LITERAL, value="Hello, World!"),
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


def test_parser_empty_string():
    code = dedent(
        """
        fn main() -> string:
            let empty: string = ''
            return empty
        """
    )

    lexer = Lexer(filename="empty_string.sigil", lines=code.splitlines())
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
                    return_type=TokenAnnotationTypes.STRING,
                ),
                children=[
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.INDENT),
                    ASTNode(
                        type=ASTType.VARIABLE_DECLARATION,
                        value=ASTDeclaration(name="empty", var_type=TokenAnnotationTypes.STRING),
                        children=[
                            ASTNode(type=ASTType.STRING_LITERAL, value=""),
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.RETURN_STATEMENT,
                        value=TokenKeyword.RETURN,
                        children=[
                            ASTNode(type=ASTType.IDENTIFIER, value="empty"),
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


def test_parser_return_string_literal():
    code = dedent(
        """
        fn main() -> string:
            return 'Direct return'
        """
    )

    lexer = Lexer(filename="return_literal.sigil", lines=code.splitlines())
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
                    return_type=TokenAnnotationTypes.STRING,
                ),
                children=[
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.INDENT),
                    ASTNode(
                        type=ASTType.RETURN_STATEMENT,
                        value=TokenKeyword.RETURN,
                        children=[
                            ASTNode(type=ASTType.STRING_LITERAL, value="Direct return"),
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


# def test_parser_string_interpolation():
#     code = dedent(
#         """
#         fn main() -> string:
#             let part1: string = 'Hello, '
#             let part2: string = 'World!'
#             let full: string = `{part1} {part2}`
#             return full
#         """
#     )

#     lexer = Lexer(filename="string_concat.sigil", lines=code.splitlines())
#     tokens = lexer.tokenize()

#     parser = Parser(tokens)
#     ast = parser.parse()

#     expected_ast = {
#         "type": ASTType.PROGRAM,
#         "body": [
#             ASTNode(
#                 type=ASTType.MAIN_DECLARATION,
#                 value=ASTFunctionDeclaration(
#                     name=TokenKeyword.MAIN,
#                     params=[],
#                     return_type=TokenAnnotationTypes.STRING,
#                 ),
#                 children=[
#                     ASTNode(
#                         type=ASTType.VARIABLE_DECLARATION,
#                         value=ASTDeclaration(name="part1", var_type=TokenAnnotationTypes.STRING),
#                         children=[
#                             ASTNode(type=ASTType.STRING_LITERAL, value="Hello, "),
#                         ],
#                     ),
#                     ASTNode(type=ASTType.NEWLINE),
#                     ASTNode(
#                         type=ASTType.VARIABLE_DECLARATION,
#                         value=ASTDeclaration(name="part2", var_type=TokenAnnotationTypes.STRING),
#                         children=[
#                             ASTNode(type=ASTType.STRING_LITERAL, value="World!"),
#                         ],
#                     ),
#                     ASTNode(type=ASTType.NEWLINE),
#                     ASTNode(
#                         type=ASTType.VARIABLE_DECLARATION,
#                         value=ASTDeclaration(name="full", var_type=TokenAnnotationTypes.STRING),
#                         children=[
#                             ASTNode(
#                                 type=ASTType.STRING_CONCATENATION,
#                                 children=[
#                                     ASTNode(type=ASTType.IDENTIFIER, value="part1"),
#                                     ASTNode(type=ASTType.STRING_LITERAL, value=" "),
#                                     ASTNode(type=ASTType.IDENTIFIER, value="part2"),
#                                 ],
#                             ),
#                         ],
#                     ),
#                     ASTNode(type=ASTType.NEWLINE),
#                     ASTNode(
#                         type=ASTType.RETURN_STATEMENT,
#                         value=TokenKeyword.RETURN,
#                         children=[
#                             ASTNode(type=ASTType.IDENTIFIER, value="full"),
#                         ],
#                     ),
#                     ASTNode(type=ASTType.NEWLINE),
#                 ],
#             ),
#             ASTNode(type=ASTType.EOF),
#         ],
#     }
#     assert ast == expected_ast
