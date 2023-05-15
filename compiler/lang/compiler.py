from compiler.lang.common.location import Location, Span
from compiler.lang.common.token import Token, TokenKind
from compiler.lang.common.error import SphynxError, SpanError, GenericError
import compiler.lang.common.ast as ast


class Compiler:
    def __init__(self, file: str, program: ast.Block) -> None:
        self.file = file
        self.program = program
        self.errors = []

        # Data
        self.globals = []
        self.functions = []

    def compile(self):
        self.globals_pass()
        if self.errors:
            for error in self.errors:
                error.print_error()
            return

    def globals_pass(self) -> None:
        for statement in self.program.statements:
            match type(statement):
                case ast.ConstantDeclaration():
                    statement: ast.ConstantDeclaration
                    if statement.name in self.globals:
                        self.errors.append(SpanError(statement.span, f"Constant {statement.name} already defined"))
                    else:
                        self.globals.append(statement.name)
                case ast.VariableDeclaration():
                    statement: ast.VariableDeclaration
                    if statement.name in self.globals:
                        self.errors.append(SpanError(statement.span, f"Variable {statement.name} already defined"))
                    else:
                        self.globals.append(statement.name)
                case ast.Function():
                    statement: ast.Function
                    if statement.name in self.globals:
                        self.errors.append(SpanError(statement.span, f"Function {statement.name} already defined"))
                    else:
                        self.globals.append(statement.name)
                case _:
                    self.errors.append(SpanError(statement.span, "Unexpected statement outside of function."))
