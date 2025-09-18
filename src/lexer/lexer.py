from src.lexer.token import (
    Token,
    TokenDelimiter,
    TokenIdentifier,
    TokenIndentation,
    TokenKeyword,
    TokenLiteral,
    TokenOperator,
)

# Map lexemes to TokenOperator/TokenDelimiter (include longest first-safe set)
OP_MAP: dict[str, TokenOperator | TokenDelimiter | TokenLiteral] = {
    "**": TokenOperator.POWER,
    "*": TokenOperator.STAR,
    "/": TokenOperator.DIV,
    "+": TokenOperator.PLUS,
    "-": TokenOperator.MINUS,
    "%": TokenOperator.MOD,
    "==": TokenOperator.EQUAL_EQUAL,
    "!=": TokenOperator.NOT_EQUAL,
    "<=": TokenOperator.LESS_EQUAL,
    ">=": TokenOperator.GREATER_EQUAL,
    "<<": TokenOperator.SHIFT_LEFT,
    ">>": TokenOperator.SHIFT_RIGHT,
    "|>": TokenOperator.PIPE,
    "->": TokenOperator.ARROW,
    "=>": TokenOperator.DOUBLE_ARROW,
    "//": TokenOperator.FLOOR_DIV,
    "=": TokenOperator.EQUAL,
    "<": TokenOperator.LESS,
    ">": TokenOperator.GREATER,
    "&": TokenOperator.AMPERSAND,
    "^": TokenOperator.CARET,
    ",": TokenDelimiter.COMMA,
    ";": TokenDelimiter.SEMICOLON,
    ":": TokenDelimiter.COLON,
    ".": TokenDelimiter.DOT,
    "(": TokenDelimiter.LPAREN,
    ")": TokenDelimiter.RPAREN,
    "{": TokenDelimiter.LBRACE,
    "}": TokenDelimiter.RBRACE,
    "[": TokenDelimiter.LBRACKET,
    "]": TokenDelimiter.RBRACKET,
    "...": TokenLiteral.ELLIPSIS,
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

    def _prepare_operator_tables(self):
        """Pre-sorts operators for maximal munch matching."""
        self._operators = list(OP_MAP.keys())
        self._operators.sort(key=len, reverse=True)
        self._op_first_chars = {op[0] for op in self._operators}

    def _is_ident_start(self, ch: str) -> bool:
        return ch.isalpha() or ch == "_" or ord(ch) > 127

    def _is_ident_part(self, ch: str) -> bool:
        return ch.isalnum() or ch == "_" or ord(ch) > 127

    def _is_operator_start(self, ch: str) -> bool:
        return ch in self._op_first_chars

    def _record_regular_keyword(self, lexeme: str) -> TokenKeyword | TokenIdentifier:
        """Records regular keywords and identifiers."""
        w = lexeme.upper()
        if w in TokenKeyword.__members__:
            return TokenKeyword[w]
        return TokenIdentifier.IDENTIFIER

    def _match_operator(self, line: str, i: int):
        """Finds the longest matching operator at the current position."""
        if not self._is_operator_start(line[i]):
            return None
        for op in self._operators:
            if line.startswith(op, i):
                return op, i + len(op)
        return None

    def _record_special_literal(self, lexeme: str) -> TokenLiteral | None:
        """Records special literals like booleans, None, and ellipsis."""
        if lexeme in {"true", "false"}:
            return TokenLiteral.BOOLEAN
        elif lexeme == "none":
            return TokenLiteral.NONE
        return None

    def _record_integer_literal(self, lexeme: str) -> TokenLiteral | None:
        """Records integer literals, allowing underscores for readability."""
        number = lexeme.replace("_", "")
        if number.isdigit():
            return TokenLiteral.INTEGER
        return None

    def _record_float_literal(self, lexeme: str) -> TokenLiteral | None:
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

    def _record_complex_literal(self, lexeme: str) -> TokenLiteral | None:
        """Records complex literals, which end with 'i'."""
        if lexeme.endswith("i"):
            number = lexeme[:-1]
            if self._record_integer_literal(number) is not None or self._record_float_literal(number) is not None:
                return TokenLiteral.COMPLEX
        return None

    def _record_string_literal(
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

    def _record_numeric_literal(self, i: int, line: str) -> tuple[TokenLiteral, str, int] | None:
        """Records numeric literals (integer, float, complex)."""
        start = i
        L = len(line)
        has_dot, has_e = False, False

        while i < L:
            ch = line[i]
            if ch.isdigit():
                i += 1
            elif ch == "_" and i + 1 < L and line[i + 1].isdigit():
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
        if not lexeme:
            return None

        if (token_type := self._record_integer_literal(lexeme)) is not None:
            return (token_type, lexeme, i)
        if (token_type := self._record_float_literal(lexeme)) is not None:
            return (token_type, lexeme, i)
        if (token_type := self._record_complex_literal(lexeme)) is not None:
            return (token_type, lexeme, i)
        return None

    def _tokenize_line(self, line: str, leading_spaces: int):
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

            # String Literals
            string_literal_result = self._record_string_literal(i, line)
            if string_literal_result is not None:
                lexeme, new_i = string_literal_result
                self._tokens.append(
                    Token(
                        filename=self._filename,
                        line=self._line_number,
                        column=leading_spaces + i,  # opening quote position
                        type=TokenLiteral.STRING,
                        value=lexeme,
                    )
                )
                i = new_i
                continue

            if ch.isdigit() or (ch == "." and i + 1 < L and line[i + 1].isdigit()):
                num_result = self._record_numeric_literal(i, line)
                if num_result:
                    token_type, lexeme, new_i = num_result
                    self._tokens.append(
                        Token(
                            filename=self._filename,
                            line=self._line_number,
                            column=leading_spaces + i,
                            type=token_type,
                            value=lexeme,
                        )
                    )
                    i = new_i
                    continue

            # Identifiers, Keywords, and Literals
            if self._is_ident_part(ch):
                start = i
                while i < L and self._is_ident_part(line[i]):
                    i += 1
                lexeme = line[start:i]

                column = leading_spaces + i - len(lexeme)

                token_type = self._record_special_literal(lexeme)
                if token_type is not None:
                    self._tokens.append(
                        Token(
                            filename=self._filename,
                            line=self._line_number,
                            column=column,
                            type=token_type,
                            value=lexeme,
                        )
                    )
                    continue

                token_type = self._record_regular_keyword(lexeme)
                self._tokens.append(
                    Token(
                        filename=self._filename,
                        line=self._line_number,
                        column=column,
                        type=token_type,
                        value=lexeme,
                    )
                )
                continue

            # Operators and Delimiters
            op_result = self._match_operator(line, i)
            if op_result:
                lexeme, new_i = op_result
                self._tokens.append(
                    Token(
                        filename=self._filename,
                        line=self._line_number,
                        column=leading_spaces + i,
                        type=OP_MAP[lexeme],
                        value=lexeme,
                    )
                )
                i = new_i
                continue

            raise SyntaxError(
                f"Unknown character: '{ch}' at {self._filename}:{self._line_number}:{leading_spaces + i + 1}"
            )

    def tokenize(self):
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
                self._tokens.append(
                    Token(
                        filename=self._filename,
                        line=line_number,
                        column=leading_spaces,
                        type=TokenIndentation.INDENT,
                        value=" " * leading_spaces,
                    )
                )

            while leading_spaces < self._indent_stack[-1]:
                self._indent_stack.pop()
                self._tokens.append(
                    Token(
                        filename=self._filename,
                        line=line_number,
                        column=1,
                        type=TokenIndentation.DEDENT,
                        value="",
                    )
                )

            if leading_spaces != self._indent_stack[-1]:
                raise IndentationError(f"Unindent does not match any outer indentation level. (line {line_number})")

            # Tokenize the actual line content (without leading indentation)
            content = line[leading_spaces:]
            self._tokenize_line(content, leading_spaces=leading_spaces)
            self._tokens.append(
                Token(
                    filename=self._filename,
                    line=line_number,
                    column=len(line) - 1,
                    type=TokenIndentation.NEWLINE,
                    value="\n",
                )
            )

        # Close remaining indentations
        while len(self._indent_stack) > 1:
            self._indent_stack.pop()
            self._tokens.append(
                Token(
                    filename=self._filename,
                    line=len(self._lines),
                    column=1,
                    type=TokenIndentation.DEDENT,
                    value="",
                )
            )

        self._tokens.append(
            Token(
                filename=self._filename,
                line=len(self._lines) + 1,
                column=1,
                type=TokenIndentation.EOF,
                value="",
            )
        )
        return self._tokens
