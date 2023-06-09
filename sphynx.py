import argparse
import pathlib
from rich import print
from time import perf_counter

import compiler.lang.common.error
from compiler import __version__, __author__, __license__  # noqa
from compiler.lang import lexer as _lexer, parser as _parser, compiler as _compiler

argparser = argparse.ArgumentParser(description="Compiler for Sphynx-Language (.spx)")
argparser.add_argument("file", type=str, help="The file to compile")
argparser.add_argument("-dcg", "--disable-code-gen", action="store_true", help="Don't generate code for the output file.")
argparser.add_argument("-n", "--no-compile", action="store_true", help="Don't compile the output file.")
argparser.add_argument("-o", "--output", type=str, help="The output file")
argparser.add_argument("-v", "--verbose", action="store_true", help="Prints extra information during compilation")
args = argparser.parse_args()

file = pathlib.Path(args.file)
if not file.exists():
    raise FileNotFoundError(f"File {file} does not exist")
if not args.output:
    args.output = file.with_suffix(".c")
output = pathlib.Path(args.output)
if not output.cwd().exists():
    raise FileNotFoundError(f"Directory {output.cwd()} does not exist")

print(f"Sphynx Compiler v{__version__} by {__author__} ({__license__})")
print(f"Compiling {file} to {output}")
start = perf_counter()

with open(file, "r") as f:
    source = f.read()

try:
    lexer = _lexer.Lexer(str(file), source)
    tokens = lexer.lex()
    if args.verbose:
        print(f"Lexed in {perf_counter() - start:.4f}s")
        print(tokens)
    parser = _parser.Parser(str(file), tokens)
    ast = parser.parse()
except compiler.lang.common.error.SphynxError as e:
    e.print_error()
    exit(1)
if args.verbose:
    print(f"Parsed in {perf_counter() - start:.4f}s")
    print(ast)

if not args.disable_code_gen:
    try:
        comp = _compiler.Compiler(str(file), ast)
        comp.compile()
    except compiler.lang.common.error.SphynxError as e:
        e.print_error()
        exit(1)
    if args.verbose:
        print(f"Compiled in {perf_counter() - start:.4f}s")
        print(comp.out)
print(f"Finished in {perf_counter() - start:.4f}s")
