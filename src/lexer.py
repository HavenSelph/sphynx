from src.common.location import Location, Span
from src.common.token import Token, TokenKind


class Lexer:
  def __init__(self, file: str, source: str):
    self.file = file
    self.source = source
    self.cur = None
    self.tokens = []
    self.index = 0
    self.line = 1
    self.column = 1

    self.advance()

  def advance(self, n: int = 1):
    for i in range(n):
      if self.cur == "\n":
        self.line += 1
        self.column = 1
      else:
        self.column += 1
      self.index += 1

      if self.index >= len(self.source):
        return None
      else:
        self.cur = self.source[self.index]
    return self.cur
  
  def peek(self, n: int = 1):
    if self.index + n >= len(self.source):
      return None
    else:
      return self.source[self.index + n]
    
  def peek_range(self, n: int):
    if self.index + n >= len(self.source):
      return None
    else:
      return self.source[self.index:self.index + n]
    
  def location(self):
    return Location(self.line, self.column, self.file)
    
  def lex(self):
    def push_simple(kind: TokenKind, size: int = 1):
      start = self.location()
      self.advance(size)
      self.tokens.append(Token(kind, self.cur, Span(start, self.location())))

    while self.cur:
      start = self.location()
      match self.cur:
        case "\n" | "\t" | "\r" | " ": self.advance()

        case char if char.isdigit():
          

        case "+": push_simple(TokenKind.Plus)
        case "-": push_simple(TokenKind.Minus)
        case "*": push_simple(TokenKind.Star)
        case "/": push_simple(TokenKind.Slash)
        
  def lex_integer(self):
    out = ""
    while self.cur.isdigit():
      out += self.cur
      self.advance()
    return out

  def lex_float(self):
    out = ""
    