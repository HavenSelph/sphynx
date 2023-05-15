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

    def parse(self):
        return self.parse_block(True)

    def parse_block(self, top: bool=False):
        start = self.current.span
        if not top:
            self.consume(TokenKind.LeftBrace)
            end = TokenKind.RightBrace
        else:
            end = TokenKind.EOF
        statements = []
        while self.current.kind != end:
            statements.append(self.parse_statement())
            self.consume_line_end()
        self.consume(end)
        print(self.current.kind)
        return ast.Block(start.extend(self.current.span), statements)

    def parse_statement(self):
        match self.current.kind:
            case TokenKind.Const: raise NotImplementedError("Const statements not implemented")
            case TokenKind.If: return self.parse_if()
            case _: return self.parse_expression()

    def parse_if(self):
        start = self.current.span
        self.advance()
        condition = self.parse_expression()
        body = self.parse_block()
        else_body = None
        if self.current.kind == TokenKind.Else:
            self.advance()
            else_body = self.parse_statement() if self.current.kind == TokenKind.If else self.parse_block()
        match self.current.kind:
            case TokenKind.Else:
                self.advance()
        return ast.If(start.extend(self.current.span), condition, body, else_body)

    def parse_expression(self):
        return self.parse_assignment()

    def parse_assignment(self):
        return self.parse_logical_or()

    def parse_logical_or(self):
        left = self.parse_logical_and()
        while self.current.kind == TokenKind.Or:
            self.advance()
            left = ast.LogicalOr(left.span.extend(self.current.span), left, self.parse_logical_and())
        return left

    def parse_logical_and(self):
        left = self.parse_comparison()
        while self.current.kind == TokenKind.And:
            self.advance()
            left = ast.LogicalAnd(left.span.extend(self.current.span), left, self.parse_comparison())
        return left

    def parse_comparison(self):
        left = self.parse_additive()
        match self.current.kind:
            case TokenKind.EqualEqual:
                self.advance()
                left = ast.EqualEqual(left.span.extend(self.current.span), left, self.parse_additive())
            case TokenKind.BangEqual:
                self.advance()
                left = ast.NotEqual(left.span.extend(self.current.span), left, self.parse_additive())
            case TokenKind.LessThan:
                self.advance()
                left = ast.LessThan(left.span.extend(self.current.span), left, self.parse_additive())
            case TokenKind.LessThanEqual:
                self.advance()
                left = ast.LessThanOrEqual(left.span.extend(self.current.span), left, self.parse_additive())
            case TokenKind.GreaterThan:
                self.advance()
                left = ast.GreaterThan(left.span.extend(self.current.span), left, self.parse_additive())
            case TokenKind.GreaterThanEqual:
                self.advance()
                left = ast.GreaterThanOrEqual(left.span.extend(self.current.span), left, self.parse_additive())
        return left

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
            case TokenKind.Not:
                start = self.current.span
                self.advance()
                out = ast.Not(start.extend(self.current.span), self.parse_postfix())
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
