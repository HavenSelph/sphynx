from __future__ import annotations
from abc import ABC, abstractmethod

from compiler.lang.common.location import Span


class Node(ABC):
    def __init__(self, span: Span) -> None:
        self.span = span

    @abstractmethod
    def __repr__(self) -> str:
        ...


class Block(Node):
    def __init__(self, span: Span, statements: list[Node]):
        super().__init__(span)
        self.statements = statements

    def __repr__(self):
        newline = "\n"
        return f"Block({newline if self.statements else ''}{newline.join(map(repr, self.statements))}{newline if self.statements else ''})"


class If(Node):
    def __init__(self, span: Span, condition: Node, body: Node, else_body: Node) -> None:
        super().__init__(span)
        self.condition = condition
        self.body = body
        self.else_body = else_body

    def __repr__(self) -> str:
        return f"If({self.condition}, {self.body}, {self.else_body})"


class VariableReference(Node):
    def __init__(self, span: Span, name: str) -> None:
        super().__init__(span)
        self.name = name

    def __repr__(self) -> str:
        return f"VariableReference({self.name})"


class VariableDeclaration(Node):
    def __init__(self, span: Span, name: str, value: Node) -> None:
        super().__init__(span)
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return f"VariableDeclaration({self.name}, {self.value})"


class Literal(Node, ABC):
    def __init__(self, span: Span, value: str) -> None:
        super().__init__(span)
        self.value = value

    def __repr__(self) -> str:
        ...


class Integer(Literal):
    def __init__(self, span: Span, value: str) -> None:
        super().__init__(span, value)

    def __repr__(self) -> str:
        return f"Number({self.value})"


class Float(Literal):
    def __init__(self, span: Span, value: str) -> None:
        super().__init__(span, value)

    def __repr__(self) -> str:
        return f"Float({self.value})"


class String(Literal):
    def __init__(self, span: Span, value: str) -> None:
        super().__init__(span, value)

    def __repr__(self) -> str:
        return f"String({self.value})"


class UnaryOp(Node, ABC):
    def __init__(self, span: Span, value: Node) -> None:
        super().__init__(span)
        self.value = value

    def __repr__(self) -> str:
        ...


class Negate(UnaryOp):
    def __init__(self, span: Span, value: Node) -> None:
        super().__init__(span, value)

    def __repr__(self) -> str:
        return f"Negate({self.value})"


class Not(UnaryOp):
    def __init__(self, span: Span, value: Node) -> None:
        super().__init__(span, value)

    def __repr__(self) -> str:
        return f"Not({self.value})"


class BinaryOp(Node, ABC):
    def __init__(self, span: Span, left: Node, right: Node) -> None:
        super().__init__(span)
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        ...


class Add(BinaryOp):
    def __init__(self, span: Span, left: Node, right: Node) -> None:
        super().__init__(span, left, right)

    def __repr__(self) -> str:
        return f"Add({self.left}, {self.right})"


class Subtract(BinaryOp):
    def __init__(self, span: Span, left: Node, right: Node) -> None:
        super().__init__(span, left, right)

    def __repr__(self) -> str:
        return f"Subtract({self.left}, {self.right})"


class Power(BinaryOp):
    def __init__(self, span: Span, left: Node, right: Node) -> None:
        super().__init__(span, left, right)

    def __repr__(self) -> str:
        return f"Power({self.left}, {self.right})"


class Multiply(BinaryOp):
    def __init__(self, span: Span, left: Node, right: Node) -> None:
        super().__init__(span, left, right)

    def __repr__(self) -> str:
        return f"Multipy({self.left}, {self.right})"


class Divide(BinaryOp):
    def __init__(self, span: Span, left: Node, right: Node) -> None:
        super().__init__(span, left, right)

    def __repr__(self) -> str:
        return f"Divide({self.left}, {self.right})"


class Modulo(BinaryOp):
    def __init__(self, span: Span, left: Node, right: Node) -> None:
        super().__init__(span, left, right)

    def __repr__(self) -> str:
        return f"Modulo({self.left}, {self.right})"


class LogicalAnd(BinaryOp):
    def __init__(self, span: Span, left: Node, right: Node) -> None:
        super().__init__(span, left, right)

    def __repr__(self) -> str:
        return f"LogicalAnd({self.left}, {self.right})"


class LogicalOr(BinaryOp):
    def __init__(self, span: Span, left: Node, right: Node) -> None:
        super().__init__(span, left, right)

    def __repr__(self) -> str:
        return f"LogicalOr({self.left}, {self.right})"


class EqualEqual(BinaryOp):
    def __init__(self, span: Span, left: Node, right: Node) -> None:
        super().__init__(span, left, right)

    def __repr__(self):
        return f"EqualEqual({self.left}, {self.right})"


class NotEqual(BinaryOp):
    def __init__(self, span: Span, left: Node, right: Node) -> None:
        super().__init__(span, left, right)

    def __repr__(self):
        return f"NotEqual({self.left}, {self.right})"


class LessThan(BinaryOp):
    def __init__(self, span: Span, left: Node, right: Node):
        super().__init__(span, left, right)

    def __repr__(self):
        return f"LessThan({self.left}, {self.right})"


class LessThanOrEqual(BinaryOp):
    def __init__(self, span: Span, left: Node, right: Node):
        super().__init__(span, left, right)

    def __repr__(self):
        return f"LessThanOrEqual({self.left}, {self.right})"


class GreaterThan(BinaryOp):
    def __init__(self, span: Span, left: Node, right: Node):
        super().__init__(span, left, right)

    def __repr__(self):
        return f"GreaterThan({self.left}, {self.right})"


class GreaterThanOrEqual(BinaryOp):
    def __init__(self, span: Span, left: Node, right: Node):
        super().__init__(span, left, right)

    def __repr__(self):
        return f"GreaterThanOrEqual({self.left}, {self.right})"
