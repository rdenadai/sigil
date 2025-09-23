from collections.abc import Iterable
from typing import Any

from src.lexer import (
    Token,
    TokenAnnotationTypes,
    TokenDelimiter,
    TokenIdentifier,
    TokenIndentation,
    TokenKeyword,
    TokenKeywordSpecial,
    TokenLiteral,
    TokenOperator,
)
from src.parser.support import (
    ASTClassAttribute,
    ASTClassMethod,
    ASTDeclaration,
    ASTFunctionDeclaration,
    ASTNode,
    ASTType,
    ASTTypeValue,
    ParserError,
)


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0
        self._ast: dict[str, Any] = {"type": ASTType.PROGRAM, "body": []}

        # Cache commonly used token type sets for performance
        self._ast_type_annotations = {kw.name for kw in TokenAnnotationTypes}
        self._comparison_operators = {
            TokenOperator.EQUAL_EQUAL,
            TokenOperator.NOT_EQUAL,
            TokenOperator.LESS,
            TokenOperator.LESS_EQUAL,
            TokenOperator.GREATER,
            TokenOperator.GREATER_EQUAL,
        }
        self._term_operators = {
            TokenOperator.MULTIPLY,
            TokenOperator.DIVIDE,
            TokenOperator.FLOOR_DIV,
            TokenOperator.POWER,
            TokenOperator.MOD,
        }
        self._token_indentation_types = {TokenIndentation.NEWLINE}

    @property
    def ast(self) -> dict[str, Any]:
        return self._ast

    def _current_token(self) -> Token | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _previous_token(self) -> Token | None:
        return self.tokens[self.pos - 1] if self.pos - 1 >= 0 else None

    def _next_token(self) -> Token | None:
        return self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None

    def _advance(self):
        self.pos += 1

    def _rewind(self):
        self.pos -= 1
        if self.pos < 0:
            self.pos = 0

    def _match(self, expected_types: set[str]) -> Token:
        """Consume token if it matches expected_type, else raise SyntaxError."""
        token = self._current_token()
        if token and token.type in expected_types:
            self._advance()
            return token
        raise ParserError(
            f"Expected one of {expected_types} but got {token.type if token else 'EOF'}",
            token.type if token else None,
            token.value if token else None,
            token.line if token else None,
            token.column if token else None,
        )

    def _accept(self, expected_types: Iterable[Any]) -> Token | None:
        token = self._current_token()
        if token and token.type in expected_types:
            self._advance()
            return token
        return None

    def _factor(self) -> ASTNode:
        """Parses the highest-precedence expressions (factors)."""
        token = self._current_token()
        if not token:
            raise ParserError("Unexpected end of input in expression")

        if token.type in {TokenLiteral.INTEGER, TokenLiteral.FLOAT}:
            self._advance()
            return ASTNode(type=ASTType.NUMBER_LITERAL, value=token.value)

        if token.type == TokenLiteral.COMPLEX:
            self._advance()
            return ASTNode(type=ASTType.COMPLEX_LITERAL, value=token.value)

        if token.type == TokenLiteral.STRING:
            self._advance()
            return ASTNode(type=ASTType.STRING_LITERAL, value=token.value)

        if token.type == TokenLiteral.BOOLEAN:
            self._advance()
            return ASTNode(type=ASTType.BOOLEAN_LITERAL, value=token.value)

        if token.type == TokenLiteral.NONE:
            self._advance()
            return ASTNode(type=ASTType.NONE_LITERAL, value=token.value)

        if token.type == TokenLiteral.ELLIPSIS:
            self._advance()
            return ASTNode(type=ASTType.ELLIPSIS_LITERAL, value=token.value)

        # Function call
        if (
            (token_m := self._current_token())
            and token_m.type in {TokenIdentifier.IDENTIFIER, TokenAnnotationTypes.COMPLEX}
            and self._next_token()
            and getattr(self._next_token(), "type", None) == TokenDelimiter.LPAREN
        ):
            identifier_token = self._match({TokenIdentifier.IDENTIFIER, TokenAnnotationTypes.COMPLEX})
            self._match({TokenDelimiter.LPAREN})
            args = []
            if (token_i := self._current_token()) and token_i.type != TokenDelimiter.RPAREN:
                args.append(self._expression())
                while (token_k := self._current_token()) and token_k.type == TokenDelimiter.COMMA:
                    self._match({TokenDelimiter.COMMA})
                    args.append(self._expression())
            self._match({TokenDelimiter.RPAREN})
            return ASTNode(
                type=ASTType.CALL_EXPRESSION,
                value=identifier_token.value,
                children=args,
            )

        # Parenthesized expression
        if token.type == TokenDelimiter.LPAREN:
            self._advance()
            node = self._expression()
            self._match({TokenDelimiter.RPAREN})
            return node

        # Identifier / member access
        if token.type in {TokenIdentifier.IDENTIFIER, TokenKeyword.SELF}:
            self._advance()
            node = ASTNode(type=ASTType.IDENTIFIER, value=token.value)
            # Chain member access (a.b.c)
            nodes = []
            while dot := self._accept({TokenDelimiter.DOT}):
                member = self._match({TokenIdentifier.IDENTIFIER})
                if (token_n := self._current_token()) and token_n.type == TokenDelimiter.LPAREN:
                    # Function call on member
                    self._match({TokenDelimiter.LPAREN})
                    args = []
                    if (token_i := self._current_token()) and token_i.type != TokenDelimiter.RPAREN:
                        args.append(self._expression())
                        while (token_k := self._current_token()) and token_k.type == TokenDelimiter.COMMA:
                            self._match({TokenDelimiter.COMMA})
                            args.append(self._expression())
                    self._match({TokenDelimiter.RPAREN})
                    nodes.append(
                        ASTNode(
                            type=ASTType.CALL_EXPRESSION,
                            value=member.value,
                            children=args,
                        )
                    )
                else:
                    nodes.append(
                        ASTNode(
                            type=ASTType.CLASS_MEMBER_ACCESS,
                            value=member.value,
                        )
                    )
            # Chain tree building for member access
            if nodes:
                node_tree = node
                for n in nodes:
                    node_tree.children = [n]
                    node_tree = n

                return ASTNode(
                    type=ASTType.CLASS_MEMBER_ACCESS,
                    value=node.value,
                    children=[node_tree],
                )
            return node

        # Lambda expression
        if token.type in {TokenKeyword.LAMBDA, TokenKeywordSpecial.LAMBDA_SPECIAL}:
            self._match({TokenKeyword.LAMBDA, TokenKeywordSpecial.LAMBDA_SPECIAL})
            params = self._get_wrapped_params()
            return_type_token = TokenAnnotationTypes.NONE
            if self._accept({TokenOperator.ARROW}):
                rt = self._match(self._ast_type_annotations)
                return_type_token = TokenAnnotationTypes[rt.value.upper()]
            self._match({TokenOperator.DOUBLE_ARROW})
            body = self._expression()
            return ASTNode(
                type=ASTType.LAMBDA_EXPRESSION,
                value=ASTFunctionDeclaration(
                    name="<lambda>",
                    params=params,
                    return_type=return_type_token,
                ),
                children=[body],
            )

        # String Template
        if token.type == TokenDelimiter.BACKSTICK:
            """
            String template parsing can be added here
            `Hello {user.name}, today is {date.now()}`
            The tokens that we receive are:
            [
                BACKSTICK,
                STRING_TEMPLATE(Hello {user.name}, today is {date.now()}),
                IDENTIFIER(user.name),
                IDENTIFIER(date.now),
                BACKSTICK
            ]
            Output AST:
            StringTemplate
            ├── StringLiteral("Hello ")
            ├── ClassMemberAccess
            │   ├── Identifier("user")
            │   └── Identifier("name")
            ├── StringLiteral(", today is ")
            └── CallExpression
                ├── Identifier("date")
                └── Identifier("now")
            """
            self._advance()
            segments: list[ASTNode] = []
            while (token_s := self._current_token()) and token_s.type != TokenDelimiter.BACKSTICK:
                if token_s.type == TokenLiteral.STRING:
                    self._advance()
                    segments.append(ASTNode(type=ASTType.STRING_LITERAL, value=token_s.value))
                elif token_s.type in {TokenIdentifier.IDENTIFIER, TokenKeyword.SELF}:
                    segments.append(self._expression())
                elif token_s.type == TokenLiteral.STRING_TEMPLATE:
                    # Handle raw string templates without interpolation
                    self._advance()
            # Consume closing backtick
            self._accept({TokenDelimiter.BACKSTICK})
            return ASTNode(type=ASTType.STRING_TEMPLATE, children=segments)

        raise ParserError("Unexpected token in expression", token.type, token.value, token.line, token.column)

    def _unary(self) -> ASTNode:
        """Parses unary operators."""
        if (token := self._current_token()) and token.type in {
            TokenKeyword.NOT,
            TokenOperator.MINUS,
        }:
            self._advance()
            right = self._unary()
            return ASTNode(
                type=ASTType.UNARY_EXPRESSION,
                value=TokenKeyword.NOT if token.type == TokenKeyword.NOT else token.value,
                children=[right],
            )
        return self._factor()

    def _term(self) -> ASTNode:
        """Parses multiplication, division, and other higher-precedence operators."""
        node = self._unary()

        while (token := self._current_token()) and token.type in self._term_operators:
            self._advance()
            right = self._unary()
            node = ASTNode(
                type=ASTType.BINARY_EXPRESSION,
                value=token.value,
                children=[node, right],
            )

        return node

    def _additive_expression(self) -> ASTNode:
        """Parses addition and subtraction."""
        node = self._term()

        while (token := self._current_token()) and token.type in {
            TokenOperator.PLUS,
            TokenOperator.MINUS,
        }:
            self._advance()
            right = self._term()
            node = ASTNode(
                type=ASTType.BINARY_EXPRESSION,
                value=token.value,
                children=[node, right],
            )

        return node

    def _comparison_expression(self) -> ASTNode:
        """Parses comparison operators."""
        node = self._additive_expression()

        while (token := self._current_token()) and token.type in self._comparison_operators:
            self._advance()
            right = self._additive_expression()
            node = ASTNode(
                type=ASTType.LOGICAL_EXPRESSION,
                value=token.type,
                children=[node, right],
            )

        return node

    def _logical_and_expression(self) -> ASTNode:
        """Parses logical AND."""
        node = self._comparison_expression()
        while (token := self._current_token()) and token.type == TokenKeyword.AND:
            self._advance()
            right = self._comparison_expression()
            node = ASTNode(
                type=ASTType.LOGICAL_EXPRESSION,
                value=TokenKeyword.AND,
                children=[node, right],
            )
        return node

    def _logical_or_expression(self) -> ASTNode:
        """Parses logical OR."""
        node = self._logical_and_expression()
        while (token := self._current_token()) and token.type == TokenKeyword.OR:
            self._advance()
            right = self._logical_and_expression()
            node = ASTNode(
                type=ASTType.LOGICAL_EXPRESSION,
                value=TokenKeyword.OR,
                children=[node, right],
            )
        return node

    def _ternary_expression(self) -> ASTNode:
        """Parse ternary expressions: condition ? true_expr : false_expr."""
        node = self._logical_or_expression()

        if self._accept({TokenOperator.QUESTION}):
            body = [node]
            body.extend(self._get_blocks())
            true_expr = self._expression()
            body.append(true_expr)
            body.extend(self._get_blocks())
            self._match({TokenDelimiter.COLON})
            body.extend(self._get_blocks())
            false_expr = self._expression()
            body.append(false_expr)
            node = ASTNode(type=ASTType.TERNARY_EXPRESSION)
            body.extend(self._get_blocks())
            node.children = body
            return node

        return node

    def _pipe_expression(self) -> ASTNode:
        """Parse pipe expressions: expr |> func |> func."""
        node = self._logical_or_expression()

        while self._accept({TokenOperator.PIPE}):
            # Can pipe to identifier or function call
            if (token_m := self._next_token()) and token_m.type == TokenDelimiter.LPAREN:
                # Function call
                func_call = self._expression()  # This will parse the function call
                node = ASTNode(type=ASTType.PIPE_EXPRESSION, children=[node, func_call])
            else:
                # Simple identifier
                func_name = self._match({TokenIdentifier.IDENTIFIER})
                func_node = ASTNode(type=ASTType.IDENTIFIER, value=func_name.value)
                node = ASTNode(type=ASTType.PIPE_EXPRESSION, children=[node, func_node])

        return node

    def _expression(self) -> ASTNode:
        """Parses addition, subtraction, and other lowest-precedence operators."""

        # Try ternary first (lowest precedence)
        node = self._assignment_expression()

        # Then try pipe expressions
        if (token := self._current_token()) and token.type == TokenOperator.PIPE:
            return self._pipe_expression()

        return node

    def _assignment_expression(self) -> ASTNode:
        """Parse assignment expressions."""
        node = self._ternary_expression()

        if self._accept({TokenOperator.EQUAL}):
            value = self._ternary_expression()
            if node.type not in {ASTType.IDENTIFIER, ASTType.CLASS_MEMBER_ACCESS}:
                raise ParserError("Invalid assignment target", node.type, node.value)
            return ASTNode(type=ASTType.ASSIGNMENT_EXPRESSION, children=[node, value])

        return node

    def _assignment(self) -> ASTNode:
        """Parses variable declarations and assignments."""
        self._match({TokenKeyword.LET, TokenKeyword.CONST})
        identifier_token = self._match({TokenIdentifier.IDENTIFIER})

        attr_type = TokenAnnotationTypes.NONE
        if (token := self._current_token()) and token.type == TokenDelimiter.COLON:
            self._match({TokenDelimiter.COLON})
            attr_type = self._define_attribute_type()
        self._match({TokenOperator.EQUAL})

        value = self._expression()

        return ASTNode(
            ASTType.VARIABLE_DECLARATION,
            value=ASTDeclaration(
                name=identifier_token.value,
                var_type=attr_type,
            ),
            children=[value],
        )

    def _get_blocks(self) -> list[ASTNode]:
        """Parses multiple blocks of statements wrapped in indentation."""
        body: list[ASTNode] = []
        while (token := self._current_token()) and token.type in {
            TokenIndentation.NEWLINE,
            TokenIndentation.INDENT,
            TokenIndentation.DEDENT,
        }:
            if token.type == TokenIndentation.NEWLINE:
                body.append(ASTNode(type=ASTType.NEWLINE))
            elif token.type == TokenIndentation.DEDENT:
                body.append(ASTNode(type=ASTType.DEDENT))
            elif token.type == TokenIndentation.INDENT:
                body.append(ASTNode(type=ASTType.INDENT))
            elif token.type == TokenIndentation.EOF:
                body.append(ASTNode(type=ASTType.EOF))
            self._advance()
        return body

    def _get_wrapped_block(self) -> list[ASTNode]:
        """Parses a block of statements wrapped in indentation."""
        self._match({TokenIndentation.INDENT})
        body: list[ASTNode] = [ASTNode(type=ASTType.INDENT)]
        while (token := self._current_token()) and (token.type not in {TokenIndentation.DEDENT, TokenIndentation.EOF}):
            stmt = self._statement()
            if stmt:
                body.append(stmt)
        token = self._match({TokenIndentation.DEDENT, TokenIndentation.EOF})
        if token.type == TokenIndentation.DEDENT:
            body.append(ASTNode(type=ASTType.DEDENT))
        elif token.type == TokenIndentation.EOF:
            self._rewind()  # Keep EOF for outer parsing
        return body

    def _get_wrapped_params(self) -> list[ASTTypeValue]:
        params: list[ASTTypeValue] = []
        while True:
            param_name = self._match({TokenIdentifier.IDENTIFIER})
            attr_type = TokenAnnotationTypes.NONE
            if (token_m := self._current_token()) and token_m.type == TokenDelimiter.COLON:
                self._match({TokenDelimiter.COLON})
                attr_type = self._define_attribute_type()

            params.append(ASTTypeValue(name=param_name.value, value=attr_type))

            if (token_t := self._current_token()) and token_t.type == TokenDelimiter.COMMA:
                self._match({TokenDelimiter.COMMA})
            else:
                break
        return params

    def _conditional_statement(self) -> ASTNode:
        """Parses if, match, loop, and for statements."""
        token = self._current_token()
        if not token:
            raise ParserError("Unexpected end of input in conditional")

        if token.type == TokenKeyword.IF:
            self._match({TokenKeyword.IF})
            condition = self._expression()
            self._match({TokenDelimiter.COLON})
            self._match({TokenIndentation.NEWLINE})
            body = self._get_wrapped_block()
            if_node = ASTNode(type=ASTType.IF_STATEMENT, value=condition, children=body)

            current_node = if_node
            while (token_m := self._current_token()) and token_m.type == TokenKeyword.ELSE:
                self._advance()
                if (token_k := self._current_token()) and token_k.type == TokenKeyword.IF:
                    self._advance()
                    else_if_condition = self._expression()
                    self._match({TokenDelimiter.COLON})
                    self._match({TokenIndentation.NEWLINE})
                    body = self._get_wrapped_block()
                    else_if_node = ASTNode(type=ASTType.ELSE_IF_STATEMENT, value=else_if_condition, children=body)
                    current_node.children.append(else_if_node)
                    current_node = else_if_node
                else:
                    self._match({TokenDelimiter.COLON})
                    self._match({TokenIndentation.NEWLINE})
                    body = self._get_wrapped_block()
                    current_node.children.append(ASTNode(type=ASTType.ELSE_STATEMENT, children=body))
                    break
            return if_node

        if token.type == TokenKeyword.MATCH:
            # Match statement parsing not yet implemented
            raise ParserError(
                "Match statement parsing not yet implemented",
                token.type,
                token.value,
                token.line,
                token.column,
            )

        if token.type == TokenKeyword.LOOP:
            self._match({TokenKeyword.LOOP})
            self._match({TokenDelimiter.COLON})
            self._match({TokenIndentation.NEWLINE})
            body = self._get_wrapped_block()
            return ASTNode(type=ASTType.LOOP_STATEMENT, children=body)

        if token.type == TokenKeyword.FOR:
            self._match({TokenKeyword.FOR})
            iterator = self._match({TokenIdentifier.IDENTIFIER})
            self._match({TokenKeyword.IN})
            iterable = self._expression()
            self._match({TokenDelimiter.COLON})
            self._match({TokenIndentation.NEWLINE})
            body = self._get_wrapped_block()
            return ASTNode(
                type=ASTType.FOR_STATEMENT,
                children=[ASTNode(type=ASTType.IDENTIFIER, value=iterator.value), iterable] + body,
            )

        raise ParserError("Unexpected token in conditional", token.type, token.value, token.line, token.column)

    def _function_statement(self) -> ASTNode:
        """Parses function declarations."""
        self._match({TokenKeyword.FN, TokenKeyword.FUNCTION})

        # Bypass main function here to avoid conflict
        is_main = getattr(self._current_token(), "type", None) == TokenKeyword.MAIN
        if is_main:
            self._match({TokenKeyword.MAIN})
        else:
            # Regular function parsing
            func_name_token = self._match({TokenIdentifier.IDENTIFIER})

        self._match({TokenDelimiter.LPAREN})

        params = []
        if (token := self._current_token()) and token.type != TokenDelimiter.RPAREN:
            params = self._get_wrapped_params()

        self._match({TokenDelimiter.RPAREN})

        attr_type = TokenAnnotationTypes.NONE
        if (token_an := self._current_token()) and token_an.type == TokenOperator.ARROW:
            self._match({TokenOperator.ARROW})
            attr_type = self._define_attribute_type()

        self._match({TokenDelimiter.COLON})
        self._match({TokenIndentation.NEWLINE})
        body: list[ASTNode] = [ASTNode(type=ASTType.NEWLINE)]
        body.extend(self._get_wrapped_block())

        return ASTNode(
            type=ASTType.MAIN_DECLARATION if is_main else ASTType.FUNCTION_DECLARATION,
            value=ASTFunctionDeclaration(
                name=TokenKeyword.MAIN if is_main else func_name_token.value,
                params=params,
                return_type=attr_type,
            ),
            children=body,
        )

    def _return_statement(self) -> ASTNode:
        """Parses return statements."""
        self._match({TokenKeyword.RETURN})
        expr = self._expression()
        return ASTNode(type=ASTType.RETURN_STATEMENT, value=TokenKeyword.RETURN, children=[expr])

    def _define_attribute_type(self) -> TokenAnnotationTypes:
        """Parse optional type annotation for variables and attributes."""
        attr_type = TokenAnnotationTypes.NONE
        type_token = self._accept({TokenIdentifier.IDENTIFIER} | self._ast_type_annotations)
        if type_token:
            if type_token.type == TokenIdentifier.IDENTIFIER:
                attr_type = TokenAnnotationTypes.OBJECT  # Custom types default to OBJECT
            else:
                attr_type = TokenAnnotationTypes[type_token.value.upper()]
        return attr_type

    def _class_attribute_definition(self, is_static: bool, is_pub: bool, is_const: bool) -> ASTNode:
        """Parse class attribute definitions with optional visibility and const modifiers."""
        identifier_token = self._match({TokenIdentifier.IDENTIFIER})

        attr_type = TokenAnnotationTypes.NONE
        if (token := self._current_token()) and token.type == TokenDelimiter.COLON:
            self._match({TokenDelimiter.COLON})
            attr_type = self._define_attribute_type()

        value = ASTNode(type=ASTType.NONE_LITERAL, value=None)
        # Optional initialization
        if (token := self._current_token()) and token.type == TokenOperator.EQUAL:
            self._advance()
            value = self._expression()

        return ASTNode(
            ASTType.CLASS_ATTRIBUTE,
            value=ASTClassAttribute(
                name=identifier_token.value,
                attr_type=attr_type,
                is_static=is_static,
                is_pub=is_pub,
                is_const=is_const,
            ),
            children=[value],
        )

    def _class_statement(self) -> ASTNode:
        """Parse class declarations with inheritance and members."""
        self._match({TokenKeyword.CLASS})
        class_name = self._match({TokenIdentifier.IDENTIFIER})

        # Handle inheritance: class Person(Human, Animal)
        inheritance = []
        if self._accept({TokenDelimiter.LPAREN}):
            inheritance.append(self._match({TokenIdentifier.IDENTIFIER}))
            while self._accept({TokenDelimiter.COMMA}):
                inheritance.append(self._match({TokenIdentifier.IDENTIFIER}))
            self._match({TokenDelimiter.RPAREN})

        self._match({TokenDelimiter.COLON})
        self._match({TokenIndentation.NEWLINE})

        # Parse class body
        self._match({TokenIndentation.INDENT})
        members = [ASTNode(type=ASTType.INDENT)]
        while (token := self._current_token()) and token.type != TokenIndentation.DEDENT:
            if token.type in self._token_indentation_types:
                # Handle newlines and indentation within class body
                if token.type == TokenIndentation.NEWLINE:
                    members.append(ASTNode(type=ASTType.NEWLINE))
                elif token.type == TokenIndentation.INDENT:
                    members.append(ASTNode(type=ASTType.INDENT))
                elif token.type == TokenIndentation.DEDENT:
                    members.append(ASTNode(type=ASTType.DEDENT))
                self._advance()
                continue

            # Parse attributes and methods with visibility modifiers
            is_static = True if self._accept({TokenKeyword.STATIC}) else False
            is_pub = True if self._accept({TokenKeyword.PUB}) else False
            is_const = True if self._accept({TokenKeyword.CONST}) else False

            if (token_n := self._current_token()) and token_n.type in {TokenKeyword.FN, TokenKeyword.FUNCTION}:
                # Method definition
                func = self._function_statement()
                method = ASTNode(
                    type=ASTType.CLASS_METHOD,
                    value=ASTClassMethod(
                        fn=func.value,
                        is_static=is_static,
                        is_pub=is_pub,
                    ),
                    children=func.children,
                )
                members.append(method)
            else:
                # Attribute definition
                attr = self._class_attribute_definition(is_static, is_pub, is_const)
                members.append(attr)

        self._match({TokenIndentation.DEDENT})
        members.append(ASTNode(type=ASTType.DEDENT))
        return ASTNode(type=ASTType.CLASS_DECLARATION, value=class_name.value, children=members)

    def _statement(self) -> ASTNode | None:
        """General statement parser."""
        token = self._current_token()
        if not token:
            return None

        if token.type in {TokenKeyword.LET, TokenKeyword.CONST}:
            return self._assignment()
        if token.type == TokenKeyword.FUNCTION:
            return self._function_statement()
        if token.type in {TokenKeyword.IF, TokenKeyword.MATCH, TokenKeyword.LOOP, TokenKeyword.FOR}:
            return self._conditional_statement()
        if token.type == TokenKeyword.RETURN:
            return self._return_statement()
        if token.type == TokenKeyword.CLASS:
            return self._class_statement()
        if token.type == TokenIndentation.EOF:
            self._advance()
            return ASTNode(type=ASTType.EOF)
        if token.type == TokenIndentation.NEWLINE:
            self._advance()
            return ASTNode(type=ASTType.NEWLINE)
        if token.type == TokenIndentation.INDENT:
            self._advance()
            return ASTNode(type=ASTType.INDENT)
        if token.type == TokenIndentation.DEDENT:
            self._advance()
            return ASTNode(type=ASTType.DEDENT)

        return self._expression()

    def parse(self) -> dict[str, Any]:
        """Parse the list of tokens and return the AST."""
        while self._current_token():
            if stmt := self._statement():
                self._ast["body"].append(stmt)
        return self._ast
