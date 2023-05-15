import argparse
import pathlib
from time import perf_counter
from compiler import __version__, __author__, __license__
from compiler.lang import lexer as _lexer, parser as _parser

argparser = argparse.ArgumentParser(description="Compiler for Sphynx-Language (.spx)")
argparser.add_argument("file", type=str, help="The file to compile")
argparser.add_argument("-o", "--output", type=str, help="The output file")
args = argparser.parse_args()

file = pathlib.Path(args.file)
if not file.exists():
    print(f"File {file} does not exist")
    exit(1)
if not args.output:
    args.output = file.with_suffix(".c")
output = pathlib.Path(args.output)

print(f"Sphynx Compiler v{__version__} by {__author__} ({__license__})")
print(f"Compiling {file} to {output}")
start = perf_counter()

with open(file, "r") as f:
    source = f.read()

lexer = _lexer.Lexer(str(file), source)
tokens = lexer.lex()
parser = _parser.Parser(str(file), tokens)
ast = parser.parse()

print(f"Finished in {perf_counter() - start:.4f}s")
