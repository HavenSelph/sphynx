from compiler.lang.common.token import Token, TokenKind
from compiler.lang.common.error import SpanError
import compiler.lang.common.ast as ast


class Parser:
    def __init__(self, filename: str, tokens: list[Token]):
        self.filename = filename
        self.tokens = tokens
        self.index = 0
        self.current = self.tokens[self.index]

    def advance(self) -> None:
        if self.current.kind != TokenKind.EOF:
            self.index += 1
            self.current = self.tokens[self.index]

    def consume(self, kind: TokenKind, msg: str=None) -> Token:
        if self.current.kind == kind:
            out = self.current
            self.advance()
            return out
        else:
            raise SpanError(self.current.span, f"Expected {kind}, got {self.current.kind}", msg)

    def consume_line_end(self, msg: str=None) -> None:
        if self.current.kind != TokenKind.Semicolon \
                and not self.current.new_line_before \
                and self.current.kind != TokenKind.EOF:
            raise SpanError(self.current.span, f"Expected line end, got {self.current.kind}", msg)
        self.advance()

    def parse(self):
        return self.parse_block(TokenKind.EOF)

    def parse_block(self, end: TokenKind=TokenKind.RightBrace):
        start = self.current.span
        statements = []
        while self.current.kind != end:
            statements.append(self.parse_statement())
            self.consume_line_end()
        self.consume(end)
        return ast.Block(start.extend(self.current.span), statements)

    def parse_statement(self):
        return self.parse_expression()

    def parse_expression(self):
        return self.parse_assignment()

    def parse_assignment(self):
        return self.parse_logical_or()

    def parse_logical_or(self):
        return self.parse_logical_and()

    def parse_logical_and(self):
        return self.parse_comparison()

    def parse_comparison(self):
        return self.parse_additive()

    def parse_additive(self):
        left = self.parse_exponential()
        while self.current.kind in [TokenKind.Plus, TokenKind.Minus]:
            if self.current.kind == TokenKind.Plus:
                self.advance()
                left = ast.Add(left.span.extend(self.current.span), left, self.parse_exponential())
            elif self.current.kind == TokenKind.Minus:
                self.advance()
                left = ast.Subtract(left.span.extend(self.current.span), left, self.parse_exponential())
        return left

    def parse_exponential(self):
        left = self.parse_multiplicative()
        while self.current.kind == TokenKind.StarStar:
            self.advance()
            left = ast.Power(left.span.extend(self.current.span), left, self.parse_multiplicative())
        return left

    def parse_multiplicative(self):
        left = self.parse_prefix()
        while self.current.kind in [TokenKind.Star, TokenKind.Slash]:
            if self.current.kind == TokenKind.Star:
                self.advance()
                left = ast.Multiply(left.span.extend(self.current.span), left, self.parse_prefix())
            elif self.current.kind == TokenKind.Slash:
                self.advance()
                left = ast.Divide(left.span.extend(self.current.span), left, self.parse_prefix())
        return left

    def parse_prefix(self):
        match self.current.kind:
            case TokenKind.Plus:
                start = self.current.span
                self.advance()
                out = self.parse_postfix()
                out.span = start.extend(self.current.span)
            case TokenKind.Minus:
                start = self.current.span
                self.advance()
                out = ast.Negate(start.extend(self.current.span), self.parse_postfix())
            case _:
                out = self.parse_postfix()
        return out

    def parse_postfix(self):
        return self.parse_atom()

    def parse_atom(self):
        match self.current.kind:
            case TokenKind.LeftParen:
                start = self.current.span
                self.advance()
                out = self.parse_expression()
                out.span = start.extend(self.consume(TokenKind.RightParen, "Expected closing parenthesis").span)
                return out
            case TokenKind.Integer:
                out = ast.Integer(self.current.span, self.current.data)
            case TokenKind.Float:
                out = ast.Float(self.current.span, self.current.data)
            case TokenKind.String:
                out = ast.String(self.current.span, self.current.data)
            case TokenKind.Identifier:
                out = ast.VariableReference(self.current.span, self.current.data)
            case _:
                raise SpanError(self.current.span, f"Unexpected token {self.current.kind}")
        self.advance()
        return out
