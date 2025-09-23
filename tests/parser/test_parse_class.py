from textwrap import dedent

from src.lexer import Lexer, TokenAnnotationTypes, TokenKeyword
from src.parser import (
    ASTClassAttribute,
    ASTClassMethod,
    ASTDeclaration,
    ASTFunctionDeclaration,
    ASTNode,
    ASTType,
    ASTTypeValue,
    Parser,
)


def test_parse_simple_class_example():
    code = dedent(
        """
        class Point:
            pub x: float64
            pub y: float64

            fn new(x: float64, y: float64) -> Point:
                self.x = x
                self.y = y

            fn move(dx: float64, dy: float64) -> none:
                self.x = self.x + dx
                self.y = self.y + dy
        
            fn display() -> none:
                print(`Point({self.x}, {self.y})`)
        
        fn main() -> none:
            let p: Point = Point(3.0, 4.0)
            p.move(1.0, 2.0)
            p.display()
        """
    )

    lexer = Lexer(filename="simple_class_example.sigil", lines=code.splitlines())
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = {
        "type": ASTType.PROGRAM,
        "body": [
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(
                type=ASTType.CLASS_DECLARATION,
                value="Point",
                children=[
                    ASTNode(type=ASTType.INDENT),
                    ASTNode(
                        type=ASTType.CLASS_ATTRIBUTE,
                        value=ASTClassAttribute(
                            name="x",
                            attr_type=TokenAnnotationTypes.FLOAT64,
                            is_static=False,
                            is_pub=True,
                            is_const=False,
                        ),
                        children=[ASTNode(type=ASTType.NONE_LITERAL)],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.CLASS_ATTRIBUTE,
                        value=ASTClassAttribute(
                            name="y",
                            attr_type=TokenAnnotationTypes.FLOAT64,
                            is_static=False,
                            is_pub=True,
                            is_const=False,
                        ),
                        children=[ASTNode(type=ASTType.NONE_LITERAL)],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.CLASS_METHOD,
                        value=ASTClassMethod(
                            fn=ASTFunctionDeclaration(
                                name="new",
                                params=[
                                    ASTTypeValue(name="x", value=TokenAnnotationTypes.FLOAT64),
                                    ASTTypeValue(name="y", value=TokenAnnotationTypes.FLOAT64),
                                ],
                                return_type=TokenAnnotationTypes.OBJECT,
                            ),
                            is_static=False,
                            is_pub=False,
                        ),
                        children=[
                            ASTNode(type=ASTType.NEWLINE),
                            ASTNode(type=ASTType.INDENT),
                            ASTNode(
                                type=ASTType.ASSIGNMENT_EXPRESSION,
                                value=None,
                                children=[
                                    ASTNode(
                                        type=ASTType.CLASS_MEMBER_ACCESS,
                                        value="self",
                                        children=[ASTNode(type=ASTType.CLASS_MEMBER_ACCESS, value="x")],
                                    ),
                                    ASTNode(type=ASTType.IDENTIFIER, value="x"),
                                ],
                            ),
                            ASTNode(type=ASTType.NEWLINE),
                            ASTNode(
                                type=ASTType.ASSIGNMENT_EXPRESSION,
                                value=None,
                                children=[
                                    ASTNode(
                                        type=ASTType.CLASS_MEMBER_ACCESS,
                                        value="self",
                                        children=[ASTNode(type=ASTType.CLASS_MEMBER_ACCESS, value="y")],
                                    ),
                                    ASTNode(type=ASTType.IDENTIFIER, value="y"),
                                ],
                            ),
                            ASTNode(type=ASTType.NEWLINE),
                            ASTNode(type=ASTType.NEWLINE),
                            ASTNode(type=ASTType.DEDENT),
                        ],
                    ),
                    ASTNode(
                        type=ASTType.CLASS_METHOD,
                        value=ASTClassMethod(
                            fn=ASTFunctionDeclaration(
                                name="move",
                                params=[
                                    ASTTypeValue(name="dx", value=TokenAnnotationTypes.FLOAT64),
                                    ASTTypeValue(name="dy", value=TokenAnnotationTypes.FLOAT64),
                                ],
                                return_type=TokenAnnotationTypes.NONE,
                            ),
                            is_static=False,
                            is_pub=False,
                        ),
                        children=[
                            ASTNode(type=ASTType.NEWLINE),
                            ASTNode(type=ASTType.INDENT),
                            ASTNode(
                                type=ASTType.ASSIGNMENT_EXPRESSION,
                                value=None,
                                children=[
                                    ASTNode(
                                        type=ASTType.CLASS_MEMBER_ACCESS,
                                        value="self",
                                        children=[ASTNode(type=ASTType.CLASS_MEMBER_ACCESS, value="x")],
                                    ),
                                    ASTNode(
                                        type=ASTType.BINARY_EXPRESSION,
                                        value="+",
                                        children=[
                                            ASTNode(
                                                type=ASTType.CLASS_MEMBER_ACCESS,
                                                value="self",
                                                children=[ASTNode(type=ASTType.CLASS_MEMBER_ACCESS, value="x")],
                                            ),
                                            ASTNode(type=ASTType.IDENTIFIER, value="dx"),
                                        ],
                                    ),
                                ],
                            ),
                            ASTNode(type=ASTType.NEWLINE),
                            ASTNode(
                                type=ASTType.ASSIGNMENT_EXPRESSION,
                                value=None,
                                children=[
                                    ASTNode(
                                        type=ASTType.CLASS_MEMBER_ACCESS,
                                        value="self",
                                        children=[ASTNode(type=ASTType.CLASS_MEMBER_ACCESS, value="y")],
                                    ),
                                    ASTNode(
                                        type=ASTType.BINARY_EXPRESSION,
                                        value="+",
                                        children=[
                                            ASTNode(
                                                type=ASTType.CLASS_MEMBER_ACCESS,
                                                value="self",
                                                children=[ASTNode(type=ASTType.CLASS_MEMBER_ACCESS, value="y")],
                                            ),
                                            ASTNode(type=ASTType.IDENTIFIER, value="dy"),
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
                        type=ASTType.CLASS_METHOD,
                        value=ASTClassMethod(
                            fn=ASTFunctionDeclaration(
                                name="display",
                                params=[],
                                return_type=TokenAnnotationTypes.NONE,
                            ),
                            is_static=False,
                            is_pub=False,
                        ),
                        children=[
                            ASTNode(type=ASTType.NEWLINE),
                            ASTNode(type=ASTType.INDENT),
                            ASTNode(
                                type=ASTType.CALL_EXPRESSION,
                                value="print",
                                children=[
                                    ASTNode(
                                        type=ASTType.STRING_TEMPLATE,
                                        value=None,
                                        children=[
                                            ASTNode(type=ASTType.STRING_LITERAL, value="Point("),
                                            ASTNode(
                                                type=ASTType.CLASS_MEMBER_ACCESS,
                                                value="self",
                                                children=[ASTNode(type=ASTType.CLASS_MEMBER_ACCESS, value="x")],
                                            ),
                                            ASTNode(type=ASTType.STRING_LITERAL, value=", "),
                                            ASTNode(
                                                type=ASTType.CLASS_MEMBER_ACCESS,
                                                value="self",
                                                children=[ASTNode(type=ASTType.CLASS_MEMBER_ACCESS, value="y")],
                                            ),
                                            ASTNode(type=ASTType.STRING_LITERAL, value=")"),
                                        ],
                                    )
                                ],
                            ),
                            ASTNode(type=ASTType.NEWLINE),
                            ASTNode(type=ASTType.NEWLINE),
                            ASTNode(type=ASTType.DEDENT),
                        ],
                    ),
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
                        value=ASTDeclaration(name="p", var_type=TokenAnnotationTypes.OBJECT),
                        children=[
                            ASTNode(
                                type=ASTType.CALL_EXPRESSION,
                                value="Point",
                                children=[
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="3.0"),
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="4.0"),
                                ],
                            ),
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.CLASS_MEMBER_ACCESS,
                        value="p",
                        children=[
                            ASTNode(
                                type=ASTType.CALL_EXPRESSION,
                                value="move",
                                children=[
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="1.0"),
                                    ASTNode(type=ASTType.NUMBER_LITERAL, value="2.0"),
                                ],
                            )
                        ],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.CLASS_MEMBER_ACCESS,
                        value="p",
                        children=[ASTNode(type=ASTType.CALL_EXPRESSION, value="display", children=[])],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.DEDENT),
                ],
            ),
            ASTNode(type=ASTType.EOF),
        ],
    }
    assert ast == expected_ast


def test_parse_class_with_static_and_const_attributes():
    code = dedent(
        """
        class Config:
            static MAX_CONNECTIONS: int32 = 100
            pub const API_URL: string = 'https://api.example.com'

            fn get_max_connections() -> int32:
                return Config.MAX_CONNECTIONS

            fn get_api_url() -> string:
                return Config.API_URL
        """
    )

    lexer = Lexer(filename="class_with_static_and_const_attributes.sigil", lines=code.splitlines())
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = {
        "type": ASTType.PROGRAM,
        "body": [
            ASTNode(type=ASTType.NEWLINE),
            ASTNode(
                type=ASTType.CLASS_DECLARATION,
                value="Config",
                children=[
                    ASTNode(type=ASTType.INDENT),
                    ASTNode(
                        type=ASTType.CLASS_ATTRIBUTE,
                        value=ASTClassAttribute(
                            name="MAX_CONNECTIONS",
                            attr_type=TokenAnnotationTypes.INT32,
                            is_static=True,
                            is_pub=False,
                            is_const=False,
                        ),
                        children=[ASTNode(type=ASTType.NUMBER_LITERAL, value="100")],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.CLASS_ATTRIBUTE,
                        value=ASTClassAttribute(
                            name="API_URL",
                            attr_type=TokenAnnotationTypes.STRING,
                            is_static=False,
                            is_pub=True,
                            is_const=True,
                        ),
                        children=[ASTNode(type=ASTType.STRING_LITERAL, value="https://api.example.com")],
                    ),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(type=ASTType.NEWLINE),
                    ASTNode(
                        type=ASTType.CLASS_METHOD,
                        value=ASTClassMethod(
                            fn=ASTFunctionDeclaration(
                                name="get_max_connections",
                                params=[],
                                return_type=TokenAnnotationTypes.INT32,
                            ),
                            is_static=False,
                            is_pub=False,
                        ),
                        children=[
                            ASTNode(type=ASTType.NEWLINE),
                            ASTNode(type=ASTType.INDENT),
                            ASTNode(
                                type=ASTType.RETURN_STATEMENT,
                                value=TokenKeyword.RETURN,
                                children=[
                                    ASTNode(
                                        type=ASTType.CLASS_MEMBER_ACCESS,
                                        value="Config",
                                        children=[
                                            ASTNode(
                                                type=ASTType.CLASS_MEMBER_ACCESS, value="MAX_CONNECTIONS", children=[]
                                            )
                                        ],
                                    )
                                ],
                            ),
                            ASTNode(type=ASTType.NEWLINE),
                            ASTNode(type=ASTType.NEWLINE),
                            ASTNode(type=ASTType.DEDENT),
                        ],
                    ),
                    ASTNode(
                        type=ASTType.CLASS_METHOD,
                        value=ASTClassMethod(
                            fn=ASTFunctionDeclaration(
                                name="get_api_url",
                                params=[],
                                return_type=TokenAnnotationTypes.STRING,
                            ),
                            is_static=False,
                            is_pub=False,
                        ),
                        children=[
                            ASTNode(type=ASTType.NEWLINE),
                            ASTNode(type=ASTType.INDENT),
                            ASTNode(
                                type=ASTType.RETURN_STATEMENT,
                                value=TokenKeyword.RETURN,
                                children=[
                                    ASTNode(
                                        type=ASTType.CLASS_MEMBER_ACCESS,
                                        value="Config",
                                        children=[
                                            ASTNode(type=ASTType.CLASS_MEMBER_ACCESS, value="API_URL", children=[])
                                        ],
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
