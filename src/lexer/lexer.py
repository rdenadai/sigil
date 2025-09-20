from src.lexer.token import (
    Token,
    TokenDelimiter,
    TokenIdentifier,
    TokenIndentation,
    TokenKeyword,
    TokenKeywordSpecial,
    TokenLiteral,
    TokenOperator,
    TokenType,
)

# Map lexemes to TokenOperator/TokenDelimiter (include longest first-safe set)
OP_MAP: dict[str, TokenOperator | TokenDelimiter | TokenLiteral] = {
    "//=": TokenOperator.FLOOR_DIV_EQUAL,
    "**=": TokenOperator.POWER_EQUAL,
    "<<=": TokenOperator.SHIFT_LEFT_EQUAL,
    ">>=": TokenOperator.SHIFT_RIGHT_EQUAL,
    "++": TokenOperator.INCREMENT,
    "--": TokenOperator.DECREMENT,
    "**": TokenOperator.POWER,
    "//": TokenOperator.FLOOR_DIV,
    "+=": TokenOperator.PLUS_EQUAL,
    "-=": TokenOperator.MINUS_EQUAL,
    "*=": TokenOperator.MULTIPLY_EQUAL,
    "/=": TokenOperator.DIV_EQUAL,
    "%=": TokenOperator.MOD_EQUAL,
    "&=": TokenOperator.AND_EQUAL,
    "|=": TokenOperator.OR_EQUAL,
    "^=": TokenOperator.XOR_EQUAL,
    "==": TokenOperator.EQUAL_EQUAL,
    "!=": TokenOperator.NOT_EQUAL,
    "<=": TokenOperator.LESS_EQUAL,
    ">=": TokenOperator.GREATER_EQUAL,
    "->": TokenOperator.ARROW,
    "=>": TokenOperator.DOUBLE_ARROW,
    "|>": TokenOperator.PIPE,
    "<<": TokenOperator.SHIFT_LEFT,
    ">>": TokenOperator.SHIFT_RIGHT,
    ":=": TokenOperator.WALRUS,
    "+": TokenOperator.PLUS,
    "-": TokenOperator.MINUS,
    "*": TokenOperator.MULTIPLY,
    "/": TokenOperator.DIV,
    "%": TokenOperator.MOD,
    "=": TokenOperator.EQUAL,
    "<": TokenOperator.LESS,
    ">": TokenOperator.GREATER,
    "&": TokenOperator.AMPERSAND,
    "|": TokenOperator.BAR,
    "@": TokenOperator.AT,
    "^": TokenOperator.CARET,
    "!": TokenOperator.EXCLAMATION,
    "?": TokenOperator.QUESTION,
    "~": TokenOperator.TILDE,
    ",": TokenDelimiter.COMMA,
    ";": TokenDelimiter.SEMICOLON,
    ".": TokenDelimiter.DOT,
    ":": TokenDelimiter.COLON,
    "(": TokenDelimiter.LPAREN,
    ")": TokenDelimiter.RPAREN,
    "{": TokenDelimiter.LBRACE,
    "}": TokenDelimiter.RBRACE,
    "[": TokenDelimiter.LBRACKET,
    "]": TokenDelimiter.RBRACKET,
    "`": TokenDelimiter.BACKSTICK,
    "...": TokenLiteral.ELLIPSIS,
}


# Map special keywords (non-ASCII) to TokenKeywordSpecial
KEYWORD_SPECIAL_MAP: dict[str, TokenKeywordSpecial] = {
    "λ": TokenKeywordSpecial.LAMBDA_SPECIAL,
    "Λ": TokenKeywordSpecial.LAMBDA_SPECIAL,
}


class Lexer:
    """A simple lexer for the Sigil programming language."""

    def __init__(self, filename: str, lines: list[str]):
        self._lines = lines
        self._filename = filename
        self._line_number = 0
        self._tokens: list[Token] = []
        self._indent_stack = [0]  # Stack to manage indentation levels
        self._prepare_operator_tables()
        self._prepare_keyword_tables()

    def _prepare_operator_tables(self):
        """Pre-sorts operators for maximal munch matching."""
        self._operators = list(OP_MAP.keys())
        self._operators.sort(key=len, reverse=True)
        self._op_first_chars = {op[0] for op in self._operators}

    def _prepare_keyword_tables(self):
        """Prepares keyword mapping for quick lookup."""
        self._keywords_special = list(KEYWORD_SPECIAL_MAP.keys())
        self._keywords_special.sort(key=len, reverse=True)
        # Create a set for O(1) lookup
        self._regular_keywords = {kw.name for kw in TokenKeyword}

    def _add_token(self, token_type: TokenType, value: str, column: int):
        """Helper to create and append a token."""
        self._tokens.append(
            Token(
                filename=self._filename,
                line=self._line_number,
                column=column,
                type=token_type,
                value=value,
            )
        )

    def _is_ident_start(self, ch: str) -> bool:
        return ch.isalpha() or ch == "_" or ord(ch) > 127

    def _is_ident_part(self, ch: str) -> bool:
        return ch.isalnum() or ch == "_" or ord(ch) > 127

    def _is_operator_start(self, ch: str) -> bool:
        return ch in self._op_first_chars

    def _match_regular_keyword(self, lexeme: str) -> TokenKeyword | TokenKeywordSpecial | TokenIdentifier:
        """Records regular keywords and identifiers."""
        w = lexeme.upper()
        if w in self._regular_keywords:
            return TokenKeyword[w]
        elif lexeme in self._keywords_special:
            return KEYWORD_SPECIAL_MAP[lexeme]
        return TokenIdentifier.IDENTIFIER

    def _match_operator(self, line: str, i: int):
        """Finds the longest matching operator at the current position."""
        if not self._is_operator_start(line[i]):
            return None
        for op in self._operators:
            if line.startswith(op, i):
                return op, i + len(op)
        return None

    def _match_special_literal(self, lexeme: str) -> TokenLiteral | None:
        """Records special literals like booleans, None."""
        if lexeme in {"true", "false"}:
            return TokenLiteral.BOOLEAN
        elif lexeme == "none":
            return TokenLiteral.NONE
        return None

    def _match_integer_literal(self, lexeme: str) -> TokenLiteral | None:
        """Records integer literals, allowing underscores for readability."""
        number = lexeme.replace("_", "")
        if number.isdigit():
            return TokenLiteral.INTEGER
        return None

    def _match_float_literal(self, lexeme: str) -> TokenLiteral | None:
        """Records float literals, allowing underscores for readability."""
        number = "".join(lexeme.split("_"))
        if "." in number:
            parts = number.split(".")
            n_parts = len(parts)
            if n_parts > 2:
                return None
            if all(part.isdigit() for part in parts if part):
                return TokenLiteral.FLOAT
            elif "e" in parts[-1].lower() or "E" in parts[-1].lower():
                e_parts = parts[-1].lower().split("e")
                if len(e_parts) == 2 and all(part.isdigit() or "+" in part or "-" in part for part in e_parts if part):
                    return TokenLiteral.FLOAT
            return None
        elif "e" in number.lower():
            base, _, exponent = number.lower().partition("e")
            if (base == "" or base.replace(".", "", 1).isdigit()) and (
                exponent == "" or exponent.lstrip("+-").isdigit()
            ):
                return TokenLiteral.FLOAT
        return None

    def _match_complex_literal(self, lexeme: str) -> TokenLiteral | None:
        """Records complex literals, which end with 'i'."""
        if lexeme.endswith("i"):
            number = lexeme[:-1]
            if self._match_integer_literal(number) is not None or self._match_float_literal(number) is not None:
                return TokenLiteral.COMPLEX
        return None

    def _match_numeric_literal(self, i: int, line: str) -> tuple[TokenLiteral, str, int] | None:
        """
        Records numeric literals (integer, float, complex) in a single pass.
        The order of checks is important to avoid misclassification.
        Order: Complex -> Float -> Integer
        """
        start = i
        L = len(line)
        has_dot, has_e = False, False

        while i < L:
            ch = line[i]
            if ch.isdigit():
                i += 1
            elif ch == "_":
                i += 1
            elif ch == "." and not has_dot and not has_e:
                # Avoid matching '...' operator
                if line.startswith("...", i):
                    break
                has_dot = True
                i += 1
            elif ch in "eE" and not has_e:
                has_e = True
                i += 1
                if i < L and line[i] in "+-":
                    i += 1
            elif ch == "i" and i > start:
                i += 1
                break
            else:
                break

        lexeme = line[start:i]
        if not lexeme or lexeme == ".":
            return None

        # Check if we have double underscores or leading/trailing underscores
        if "__" in lexeme or lexeme.startswith("_") or lexeme.endswith("_"):
            return None

        # The order of checks is important to avoid misclassification.
        # A complex number like '3i' could be seen as an integer '3'.
        # A float '3.0' could be seen as an integer '3'.
        # Order: Complex -> Float -> Integer
        if (token_type := self._match_complex_literal(lexeme)) is not None:
            return (token_type, lexeme, i)
        if (token_type := self._match_float_literal(lexeme)) is not None:
            return (token_type, lexeme, i)
        if (token_type := self._match_integer_literal(lexeme)) is not None:
            return (token_type, lexeme, i)
        return None

    def _match_string_literal(
        self,
        i: int,
        line: str,
    ) -> tuple[str, int] | None:
        """Records string literals, handling escape sequences."""
        if line[i] == "'":
            start = i + 1  # Skip opening quote
            i += 1
            L = len(line)
            while i < L:
                if line[i] == "\\" and i + 1 < L:
                    i += 2  # Skip escaped character
                elif line[i] == "'":
                    i += 1  # Include closing quote
                    return line[start : i - 1], i
                else:
                    i += 1
            else:
                raise SyntaxError("Unterminated string literal")
        return None

    def _match_string_interpolation(self, i: int, line: str) -> tuple[str, int] | None:
        """Records string interpolation segments."""
        if line[i] == "`" and i + 1 < len(line):
            if line[i + 1] == "`":
                return "", i + 2  # Handle empty interpolation ``
            start = i + 1  # Skip opening `
            i += 2
            L = len(line)
            while i < L:
                if line[i] == "\\" and i + 1 < L:
                    i += 2  # Skip escaped character
                elif line[i] == "`":
                    return line[start:i], i + 1  # Include closing `
                else:
                    i += 1
            else:
                raise SyntaxError("Unterminated string interpolation")
        return None

    def _match_string_interpolation_internals(self, lexeme: str) -> list[tuple[str, int]]:
        # Handle cases like: Hello, {name}! => STRING, COMMA, IDENTIFIER, STRING
        column, i, L = 0, 0, len(lexeme)
        lbrace_start, rbrace_start, open_bracket = 0, 0, False
        identifiers: list[tuple[str, int]] = []
        while i < L:
            if lexeme[i] == "{" and (i == 0 or lexeme[i - 1] != "\\"):
                lbrace_start = i
                open_bracket = True
            elif lexeme[i] == "}" and (i == 0 or lexeme[i - 1] != "\\") and open_bracket:
                rbrace_start = i
                token = lexeme[lbrace_start + 1 : rbrace_start].strip()
                identifiers.append((token, column))
                column = i
                lbrace_start, rbrace_start, open_bracket = 0, 0, False
            i += 1
        return identifiers

    def _tokenize_line(self, line: str, leading_spaces: int):
        """Tokenizes a single line of code."""
        i, L = 0, len(line)
        while i < L:
            ch = line[i]

            # comment start (only when not inside a string)
            if ch == "#":
                break

            # skip inline whitespace
            if ch.isspace():
                i += 1
                continue

            # String Interpolation
            string_interp_result = self._match_string_interpolation(i, line)
            if string_interp_result is not None:
                lexeme, new_i = string_interp_result
                self._add_token(TokenDelimiter.BACKSTICK, "`", leading_spaces + i)
                if lexeme:
                    # Find identifiers inside {}
                    tokens = self._match_string_interpolation_internals(lexeme)
                    if tokens:
                        self._add_token(TokenLiteral.STRING_TEMPLATE, lexeme, leading_spaces + new_i + 1)
                        for token, space in tokens:
                            # We have something like {} in the string
                            if not token:
                                self._add_token(TokenLiteral.STRING, "", leading_spaces + space + 1)
                            else:
                                # We have an identifier or expression inside {}
                                self._add_token(TokenIdentifier.IDENTIFIER, token, leading_spaces + space + 1)
                    # We have a plain string without {}
                    else:
                        self._add_token(TokenLiteral.STRING, lexeme, leading_spaces + new_i + 1)
                # We have an empty interpolation ``
                else:
                    self._add_token(TokenLiteral.STRING, "", leading_spaces + i + 1)
                self._add_token(TokenDelimiter.BACKSTICK, "`", leading_spaces + new_i - 2)
                i = new_i
                continue

            # String Literals
            string_literal_result = self._match_string_literal(i, line)
            if string_literal_result is not None:
                lexeme, new_i = string_literal_result
                self._add_token(TokenLiteral.STRING, lexeme, leading_spaces + i)
                i = new_i
                continue

            # Numeric Literals
            if ch.isdigit() or (ch == "." and i + 1 < L and line[i + 1].isdigit()):
                num_result = self._match_numeric_literal(i, line)
                if num_result:
                    token_type, lexeme, new_i = num_result
                    self._add_token(token_type, lexeme, leading_spaces + i)
                    i = new_i
                    continue

            # Identifiers, Keywords, and Literals
            if self._is_ident_part(ch):
                start = i
                while i < L and self._is_ident_part(line[i]):
                    i += 1
                lexeme = line[start:i]

                column = leading_spaces + i - len(lexeme)

                token_type = self._match_special_literal(lexeme)
                if token_type is not None:
                    self._add_token(token_type, lexeme, column)
                    continue

                if lexeme and lexeme[0].isdigit():
                    raise SyntaxError(
                        f"Invalid identifier starting with a digit: '{lexeme}' at {self._filename}:{self._line_number}:{column + 1}"
                    )
                token_type = self._match_regular_keyword(lexeme)
                self._add_token(token_type, lexeme, column)
                continue

            # Operators and Delimiters
            op_result = self._match_operator(line, i)
            if op_result:
                lexeme, new_i = op_result
                self._add_token(OP_MAP[lexeme], lexeme, leading_spaces + i)
                i = new_i
                continue

            # If we reach here, it's an unknown character
            raise SyntaxError(
                f"Unknown character: '{ch}' at {self._filename}:{self._line_number}:{leading_spaces + i + 1}"
            )

    def tokenize(self):
        """Tokenizes the input lines into a list of tokens."""
        for line_number, raw_line in enumerate(self._lines, 1):
            self._line_number = line_number
            line = raw_line

            # Tabs are not allowed anywhere on the line
            if "\t" in line:
                raise IndentationError(f"Tabs are not allowed. (line {line_number})")

            # Find first non-space character
            i = 0
            while i < len(line) and line[i] == " ":
                i += 1

            # Skip blank lines and comment-only lines
            if i >= len(line) or (i < len(line) and line[i] == "#"):
                continue

            leading_spaces = i

            # Handle INDENT/DEDENT (spaces only)
            if leading_spaces > self._indent_stack[-1]:
                self._indent_stack.append(leading_spaces)
                self._add_token(TokenIndentation.INDENT, " " * leading_spaces, 1)

            while leading_spaces < self._indent_stack[-1]:
                self._indent_stack.pop()
                self._add_token(TokenIndentation.DEDENT, "", 1)

            if leading_spaces != self._indent_stack[-1]:
                raise IndentationError(f"Unindent does not match any outer indentation level. (line {line_number})")

            # Tokenize the actual line content (without leading indentation)
            content = line[leading_spaces:]
            self._tokenize_line(content, leading_spaces=leading_spaces)
            self._add_token(TokenIndentation.NEWLINE, "\n", len(line) - 1)

        # Close remaining indentations
        while len(self._indent_stack) > 1:
            self._indent_stack.pop()
            self._add_token(TokenIndentation.DEDENT, "", 1)

        self._add_token(TokenIndentation.EOF, "", 1)
        return self._tokens
