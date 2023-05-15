from enum import Enum, auto
from compiler.lang.common.location import Span


class TokenKind(Enum):
    # Misc
    EOF = auto()

    # Keywords
    Let = auto()

    # Symbols
    LeftParen = auto()
    RightParen = auto()

    # Operators
    Plus = auto()
    Minus = auto()
    Star = auto()
    StarStar = auto()
    Slash = auto()
    Percent = auto()

    # Literals
    Identifier = auto()
    String = auto()
    Integer = auto()
    Float = auto()


characters = {
    # Symbols
    "(": TokenKind.LeftParen,
    ")": TokenKind.RightParen,

    # Operators
    "+": TokenKind.Plus,
    "-": TokenKind.Minus,
    "*": TokenKind.Star,
    "**": TokenKind.StarStar,
    "/": TokenKind.Slash,
    "//": TokenKind.Slash,
    "%": TokenKind.Percent
}

sorted_keys = sorted(characters.keys(), key=lambda x: len(x), reverse=True)
characters = {key: characters[key] for key in sorted_keys}
characters_match = [key[0] for key in sorted_keys]

keywords = {
    # Assignment
    "let": TokenKind.Let,
}


class Token:
    def __init__(self, kind: TokenKind, data: int | float | str | None, span: Span) -> None:
        self.kind = kind
        self.data = data
        self.span = span

        # Metadata
        self.space_after = False

    def __repr__(self) -> str:
        return f"Token({self.kind}, {self.data.__repr__()}, {self.space_after=}, {self.span})"
