from compiler.lang.common.location import Location, Span
from compiler.lang.common.token import Token, TokenKind, characters, characters_match, keywords
from compiler.lang.common.error import SpanError


class Lexer:
    def __init__(self, filename: str, text: str) -> None:
        self.filename = filename
        self.text = text
        self.index = 0
        self.line = 1
        self.column = 1
        self.cur = self.text[self.index]
        self.tokens = []

        # State
        self.new_line = True

    @property
    def location(self) -> Location:
        return Location(self.filename, self.line, self.column, self.index)

    def span(self, start: Location) -> Span:
        return Span(start, self.location)

    def advance(self) -> None:
        if self.cur == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.index += 1
        if self.index >= len(self.text):
            self.cur = None
            return
        self.cur = self.text[self.index]

    def advance_many(self, amount: int) -> None:
        for _ in range(amount):
            self.advance()

    def peek(self) -> str | None:
        if self.index + 1 >= len(self.text):
            return None
        return self.text[self.index + 1]

    def peek_slice(self, length: int) -> str | None:
        if self.index + length >= len(self.text):
            return None
        return self.text[self.index:self.index+length]

    def push_simple(self, kind: TokenKind, size: int=1) -> None:
        start = self.location
        self.advance_many(size)
        self.tokens.append(Token(kind, None, self.span(start), self.new_line))
        self.new_line = False

    def push(self, kind: TokenKind, data, start: Location) -> None:
        self.tokens.append(Token(kind, data, self.span(start), self.new_line))
        self.new_line = False

    def lex(self) -> list[Token]:
        while self.cur:
            match self.cur:
                case "\n":
                    self.new_line = True
                    self.advance()
                case char if char.isspace(): self.advance()
                case "/" if self.peek() == "/":  # Single-line comment
                    while self.cur and self.cur != "\n":
                        self.advance()
                case "/" if self.peek() == "*":  # Multi-line comment
                    while self.cur and self.peek_slice(2) != "*/":
                        self.advance()
                    if self.peek_slice(2) != "*/":
                        raise SpanError(self.span(self.location), "Expected '*/'")
                    self.advance_many(2)
                case char if char.isalpha() or char == "_": self.lex_identifier()
                case char if char.isdigit() or char == ".": self.lex_number()
                case char if char in characters_match:  # Symbols and operators
                    for key in characters:
                        if self.peek_slice(len(key)) == key:
                            start = self.location
                            self.advance_many(len(key))
                            self.push(characters[key], None, start)
                            break
                case _:
                    raise SpanError(self.span(self.location), f"Unexpected character '{self.cur}'")
        self.push_simple(TokenKind.EOF)
        return self.tokens

    def lex_identifier(self) -> None:
        start = self.location
        identifier = ""
        while self.cur and (self.cur.isalnum() or self.cur == "_"):
            identifier += self.cur
            self.advance()
        kind = keywords.get(identifier, TokenKind.Identifier)
        self.push(kind, identifier, start)

    def lex_number(self) -> None:
        start = self.location
        number = ""
        number += self.lex_integer()
        if self.cur == ".":
            number += self.cur
            self.advance()
            number += self.lex_integer()
            if self.cur == ".":
                raise SpanError(self.span(start), "Unexpected '.'", "Floats cannot have multiple decimal points.")
            self.push(TokenKind.Float, float(number), start)
        else:
            self.push(TokenKind.Integer, int(number), start)

    def lex_integer(self):
        out = ""
        while self.cur and self.cur.isdigit():
            out += self.cur
            self.advance()
            while self.cur == "_":
                self.advance()
        return out
