from enum import Enum, auto
from compiler.lang.common.location import Span


class TokenKind(Enum):
    # Misc
    EOF = auto()

    # Keywords
    Const = auto()
    If = auto()
    Else = auto()
    While = auto()
    As = auto()

    # Symbols
    LeftParen = auto()
    RightParen = auto()
    LeftBrace = auto()
    RightBrace = auto()
    LeftBracket = auto()
    RightBracket = auto()

    # Delimiters
    Comma = auto()
    Colon = auto()
    Semicolon = auto()

    # Operators
    Equal = auto()
    Plus = auto()
    Minus = auto()
    Star = auto()
    StarStar = auto()
    Slash = auto()
    Percent = auto()

    # Logical
    And = auto()
    Or = auto()
    Not = auto()

    # Comparison
    EqualEqual = auto()
    BangEqual = auto()
    LessThan = auto()
    LessThanEqual = auto()
    GreaterThan = auto()
    GreaterThanEqual = auto()

    # Literals
    Identifier = auto()
    String = auto()
    Integer = auto()
    Float = auto()


characters = {
    # Symbols
    "(": TokenKind.LeftParen,
    ")": TokenKind.RightParen,
    "{": TokenKind.LeftBrace,
    "}": TokenKind.RightBrace,
    "[": TokenKind.LeftBracket,
    "]": TokenKind.RightBracket,

    # Delimiters
    ",": TokenKind.Comma,
    ":": TokenKind.Colon,
    ";": TokenKind.Semicolon,

    # Operators
    "=": TokenKind.Equal,
    "+": TokenKind.Plus,
    "-": TokenKind.Minus,
    "*": TokenKind.Star,
    "**": TokenKind.StarStar,
    "/": TokenKind.Slash,
    "%": TokenKind.Percent,

    # Comparison
    "==": TokenKind.EqualEqual,
    "!=": TokenKind.BangEqual,
    "<": TokenKind.LessThan,
    "<=": TokenKind.LessThanEqual,
    ">": TokenKind.GreaterThan,
    ">=": TokenKind.GreaterThanEqual,
}

sorted_keys = sorted(characters.keys(), key=lambda x: len(x), reverse=True)
characters = {key: characters[key] for key in sorted_keys}
characters_match = [key[0] for key in sorted_keys]

keywords = {
    # Assignment
    "const": TokenKind.Const,
    "if": TokenKind.If,
    "else": TokenKind.Else,
    "while": TokenKind.While,

    # Postfix
    "as": TokenKind.As,

    # Logical
    "and": TokenKind.And,
    "or": TokenKind.Or,
    "not": TokenKind.Not
}


class Token:
    def __init__(self, kind: TokenKind, data: int | float | str | None, span: Span, new_line_before: bool) -> None:
        self.kind = kind
        self.data = data
        self.span = span

        # Metadata
        self.new_line_before = new_line_before

    def __repr__(self) -> str:
        return f"Token({self.kind}, {self.data.__repr__()}, {self.new_line_before=}, {self.span})"
