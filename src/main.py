import os
from argparse import ArgumentParser
from pprint import pprint

from src.analyzer import SemanticAnalyzer
from src.codegen import CodeGenerator
from src.lexer import Lexer
from src.parser import Parser


def main():
    args = ArgumentParser()
    args.add_argument("file", help="File to be processed")
    args = args.parse_args()

    if not os.path.isfile(args.file):
        print(f"Error: File '{args.file}' not found.")
        return 1

    if not args.file.endswith(".sl"):
        print("Error: Input file must have a .sl extension.")
        return 1

    filename = os.path.basename(args.file)
    name = filename.rsplit(".", 1)[0]
    print(f"Processing file: {filename}\n")

    with open(args.file) as f:
        lines = f.readlines()
    lex = Lexer(filename=filename, lines=lines)
    tokens = lex.tokenize()
    print("Tokens:")
    print("-" * 20)
    pprint(tokens)

    parser = Parser(tokens)
    parser.parse()
    ast = parser.ast
    print("\nAST:")
    print("-" * 20)
    pprint(ast)

    analyzer = SemanticAnalyzer(ast)
    symbol_table = analyzer.analyze()
    print("\nSymbol Table:")
    print("-" * 20)
    pprint(symbol_table)

    codegen = CodeGenerator(ast)
    llvm_ir = codegen.generate()
    print("\nLLVM IR:")
    print("-" * 20)
    pprint(llvm_ir)

    if not llvm_ir:
        print("Error: LLVM IR generation failed.")
        return 1

    with open(f"{name}.ll", "w") as f:
        f.write(llvm_ir)
    print(f"\nLLVM IR saved to {name}.ll")

    os.system(f"llc -filetype=obj {name}.ll -o {name}.o")
    print(f"Object code saved to {name}.o")
    os.system(f"gcc {name}.o -o {name}")
    print(f"Executable saved to {name}")

    return 0


if __name__ == "__main__":
    raise SystemError(main())
