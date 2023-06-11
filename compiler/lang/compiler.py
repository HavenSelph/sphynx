from __future__ import annotations
from compiler.lang.common.location import Location, Span
from compiler.lang.common.token import Token, TokenKind
from compiler.lang.common.error import SphynxError, SpanError, GenericError
from pathlib import Path
from os import getenv
import compiler.lang.common.ast as ast


class Scope:
    def __init__(self, parent: Scope | None):
        self.parent = parent
        self.symbols = {}


class Compiler:
    def __init__(self, filename: str, program: ast.Block) -> None:
        self.filename = filename
        self.program = program
        self.runtime = None
        self.check_runtime()
        self.out = ""
        self.errors = []
        self.warnings = []

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

    def add(self, line: str):
        self.out += line + "\n"

    def compile(self):
        self.runtime: Path
        for datatype in self.runtime.glob("*.h"):
            self.add(f"#include \"{datatype.name}\"")

    def compile_node(self, node: ast.Node):
        match type(node):
            case ast.Block:
                node: ast.Block
                for statement in node.statements:
                    self.out += self.compile_node(statement)
            case ast.VariableDeclaration:
                node: ast.VariableDeclaration
                self.add(f"Value *{node.name} = {self.compile_node(node.value)};")
            case ast.VariableAssignment:
                node: ast.VariableAssignment
                self.add(f"unref({node.name}); {node.name} = {self.compile_node(node.value)};")
            case ast.VariableReference:
                node: ast.VariableReference
                return f"ref({node.name})"
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
