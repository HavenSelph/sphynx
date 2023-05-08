from dataclasses import dataclass
from location import Location, Span
from enum import Enum, auto


class TokenKind(Enum):
  # Literals
  IntegerLiteral = auto()
  FloatLiteral = auto()

  # Operators
  Plus = auto()
  Minus = auto()
  Star = auto()
  Slash = auto()


@dataclass
class Token:
  kind: TokenKind
  value: str
  span: Span

  def __str__(self):
    return f"{self.kind.name} {self.value} {self.span}"