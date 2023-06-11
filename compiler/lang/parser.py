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
        end = self.consume(end)
        return ast.Block(start.extend(end.span), statements)

    def parse_statement(self):
        match self.current.kind:
            case TokenKind.If: return self.parse_if()
            case TokenKind.While: return self.parse_while()
            case TokenKind.Fn: return self.parse_function()
            case TokenKind.Const: return self.parse_const()
            case TokenKind.Let: return self.parse_let()
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
        return ast.If(start.extend(else_body.span if else_body else body.span), condition, body, else_body)

    def parse_while(self):
        start = self.current.span
        self.advance()
        condition = self.parse_expression()
        body = self.parse_block()
        return ast.While(start.extend(body.span), condition, body)

    def parse_function(self):
        start = self.current.span
        self.advance()
        name = self.consume(TokenKind.Identifier).data
        self.consume(TokenKind.LeftParen)
        parameters = []
        while self.current.kind != TokenKind.RightParen:
            parameters.append(self.consume(TokenKind.Identifier).data)
            if self.current.kind != TokenKind.Comma:
                break
        self.consume(TokenKind.RightParen, "Maybe you forgot a comma?")
        body = self.parse_block()
        return ast.Function(start.extend(body.span), name, parameters, body)

    def parse_const(self):
        start = self.current.span
        self.advance()
        name = self.consume(TokenKind.Identifier).data
        self.consume(TokenKind.Equal)
        value = self.parse_expression()
        return ast.ConstantDeclaration(start.extend(value.span), name, value)

    def parse_let(self):
        start = self.current.span
        self.advance()
        name = self.consume(TokenKind.Identifier).data
        self.consume(TokenKind.Equal)
        value = self.parse_expression()
        return ast.VariableDeclaration(start.extend(value.span), name, value)

    def parse_expression(self):
        return self.parse_assignment()

    def parse_assignment(self):
        left = self.parse_logical_or()
        match self.current.kind:
            case TokenKind.Equal:
                self.advance()
                right = self.parse_assignment()
                return ast.VariableAssignment(left.span.extend(right.span), left.name, right)
            case _: return left

    def parse_logical_or(self):
        left = self.parse_logical_and()
        while self.current.kind == TokenKind.Or:
            self.advance()
            left = ast.LogicalOr(left, self.parse_logical_and())
        return left

    def parse_logical_and(self):
        left = self.parse_comparison()
        while self.current.kind == TokenKind.And:
            self.advance()
            left = ast.LogicalAnd(left, self.parse_comparison())
        return left

    def parse_comparison(self):
        left = self.parse_additive()
        match self.current.kind:
            case TokenKind.EqualEqual:
                self.advance()
                left = ast.EqualEqual(left, self.parse_additive())
            case TokenKind.BangEqual:
                self.advance()
                left = ast.NotEqual(left, self.parse_additive())
            case TokenKind.LessThan:
                self.advance()
                left = ast.LessThan(left, self.parse_additive())
            case TokenKind.LessThanEqual:
                self.advance()
                left = ast.LessThanOrEqual(left, self.parse_additive())
            case TokenKind.GreaterThan:
                self.advance()
                left = ast.GreaterThan(left, self.parse_additive())
            case TokenKind.GreaterThanEqual:
                self.advance()
                left = ast.GreaterThanOrEqual(left, self.parse_additive())
        return left

    def parse_additive(self):
        left = self.parse_exponential()
        while self.current.kind in [TokenKind.Plus, TokenKind.Minus]:
            if self.current.kind == TokenKind.Plus:
                self.advance()
                left = ast.Add(left, self.parse_exponential())
            elif self.current.kind == TokenKind.Minus:
                self.advance()
                left = ast.Subtract(left, self.parse_exponential())
        return left

    def parse_exponential(self):
        left = self.parse_multiplicative()
        while self.current.kind == TokenKind.StarStar:
            self.advance()
            left = ast.Power(left, self.parse_multiplicative())
        return left

    def parse_multiplicative(self):
        left = self.parse_prefix()
        while self.current.kind in [TokenKind.Star, TokenKind.Slash]:
            if self.current.kind == TokenKind.Star:
                self.advance()
                left = ast.Multiply(left, self.parse_prefix())
            elif self.current.kind == TokenKind.Slash:
                self.advance()
                left = ast.Divide(left, self.parse_prefix())
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
        left = self.parse_atom()
        start = left.span
        match self.current.kind:
            case TokenKind.As:
                self.advance()
                left = ast.Cast(left, self.parse_atom())
            case TokenKind.Colon:
                self.advance()
                raise SpanError(start.extend(self.current.span), "Type annotations are not yet supported")
            case TokenKind.LeftParen:
                self.advance()
                arguments = []
                while self.current.kind != TokenKind.RightParen:
                    arguments.append(self.parse_expression())
                    if self.current.kind == TokenKind.Comma:
                        self.advance()
                    else:
                        break
                end = self.consume(TokenKind.RightParen, "Expected closing parenthesis").span
                left = ast.Call(start.extend(end), left, arguments)
        return left

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
