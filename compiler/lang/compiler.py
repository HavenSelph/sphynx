from __future__ import annotations
from compiler.lang.common.location import Location, Span
from compiler.lang.common.token import Token, TokenKind
from compiler.lang.common.error import SphynxError, SpanError, GenericError
from pathlib import Path
from os import getenv
import compiler.lang.common.ast as ast


class Compiler:
    def __init__(self, filename: str, program: ast.Block) -> None:
        self.filename = filename
        self.program = program
        self.runtime = None
        self.check_runtime()
        self.out = ""
        self.errors = []
        self.warnings = []
        self.scopes = []

    def check_runtime(self):
        env = True
        runtime = getenv("SPHYNX_RUNTIME", None)
        if runtime is None:
            env = False
            runtime = Path(__file__).parent.parent.parent / "runtime"
        else:
            runtime = Path(runtime)
        if not runtime.exists():
            if env:
                raise GenericError(f"SPHYNX_RUNTIME environment variable set to {runtime}, but path does not exist")
            raise GenericError(f"Runtime path {runtime} not found")
        self.runtime = runtime

    def warn(self, span, message, flag=""):
        self.warnings.append(SpanError(span, message, flag, color="\u001b[33m"))

    def error(self, span, message, flag=""):
        self.errors.append(SpanError(span, message, flag, color="\u001b[31m"))

    def print_errors(self):
        for error in self.errors:
            error.print_error()

    def print_warnings(self):
        for warning in self.warnings:
            warning.print_error()

    def compile(self):
        self.runtime: Path
        self.out += "#include \"common.h\"\n"
        self.out += "\n".join([f"#include \"{file.name}\"" for file in (self.runtime / "Types").glob("*.h")])
        self.out += "\n".join([f"#include \"{file.name}\"" for file in (self.runtime / "Context").glob("*.h")])
        self.out += "\n\n"
        self.out += self.compile_block(self.program, True)

    def compile_block(self, node: ast.Block, top=False):
        output = ""
        if top:
            output += "int main() "
        output += "{\n"
        self.scopes.append({})
        for statement in node.statements:
            output += self.compile_node(statement)
            output += "\n"
        output += "\n".join([f"unref({name});" for name in self.scopes.pop().keys()])
        output += "\n}"
        return output

    def compile_node(self, node: ast.Node):
        match type(node):
            case ast.Block:
                node: ast.Block
                return self.compile_block(node)

            # Assignment
            case ast.VariableDeclaration:
                node: ast.VariableDeclaration
                self.scopes[-1][node.name] = node
                return f"Value *{node.name} = {self.compile_node(node.value)};"
            case ast.VariableAssignment:
                node: ast.VariableAssignment
                return f"unref({node.name}); {node.name} = {self.compile_node(node.value)};"
            case ast.VariableReference:
                node: ast.VariableReference
                return f"ref({node.name})"

            # Operations
            case ast.Add:
                node: ast.Add
                return f"value_add({self.compile_node(node.left)}, {self.compile_node(node.right)})"
            case ast.Subtract:
                node: ast.Subtract
                return f"value_subtract({self.compile_node(node.left)}, {self.compile_node(node.right)})"
            case ast.Power:
                node: ast.Power
                return f"value_power({self.compile_node(node.left)}, {self.compile_node(node.right)})"
            case ast.Multiply:
                node: ast.Multiply
                return f"value_multiply({self.compile_node(node.left)}, {self.compile_node(node.right)})"
            case ast.Divide:
                node: ast.Divide
                return f"value_divide({self.compile_node(node.left)}, {self.compile_node(node.right)})"
            case ast.Modulo:
                node: ast.Modulo
                return f"value_modulo({self.compile_node(node.left)}, {self.compile_node(node.right)})"

            # Comparisons
            case ast.EqualEqual:
                node: ast.EqualEqual
                return f"value_equals({self.compile_node(node.left)}, {self.compile_node(node.right)})"
            case ast.NotEqual:
                node: ast.NotEqual
                return f"value_not(value_equals({self.compile_node(node.left)}, {self.compile_node(node.right)}))"
            case ast.GreaterThan:
                node: ast.GreaterThan
                return f"value_greater_than({self.compile_node(node.left)}, {self.compile_node(node.right)})"

            # Literals
            case ast.Integer:
                node: ast.Integer
                return f"value_new_int({node.value})"
            case ast.String:
                node: ast.String
                return f"value_new_string({len(node.value)}, \"{node.value}\")"
            case ast.Float:
                node: ast.Float
                return f"value_new_float({node.value})"

            case _:
                raise GenericError(f"Unhandled node type {type(node)}")
