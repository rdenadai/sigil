import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint

from src.analyzer import SemanticAnalyzer
from src.codegen import CodeGenerator
from src.lexer import Lexer
from src.parser import Parser

BUILD_DIR = Path("build")


def run_command(command: list[str], capture_output=False):
    """Runs a shell command and handles errors."""
    print(f"Running command: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            check=True,
            text=True,
            capture_output=capture_output,
        )
        return result
    except FileNotFoundError:
        print(f"Command not found: {command[0]}", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {' '.join(command)}", file=sys.stderr)
        if capture_output:
            print("Output:", e.stdout, file=sys.stderr)
            print("Error Output:", e.stderr, file=sys.stderr)
        sys.exit(1)


def main():
    """Main function to handle the compilation process."""

    args = ArgumentParser()
    args.add_argument("file", type=Path, help="File to be processed")
    args.add_argument("--run", action="store_true", help="Run the generated executable")
    args.add_argument("--optm", action="store_true", help="Optimize the generated LLVM IR")
    args = args.parse_args()

    input_file: Path = args.file
    if not input_file.is_file():
        print(f"Error: File '{args.file}' not found.")
        return 1

    if input_file.suffix != ".sl":
        print("Error: Input file must have a .sl extension.")
        return 1

    name = input_file.stem
    print(f"Processing file: {input_file.name}\n")

    # Read the file content
    try:
        source_code = input_file.read_text()
    except IOError as e:
        print(f"Error reading file '{input_file}': {e}")
        return 1

    BUILD_DIR.mkdir(exist_ok=True)
    # Clear previous build files
    for file in BUILD_DIR.glob("*.*"):
        file.unlink()

    # Lexical Analysis
    lex = Lexer(filename=input_file.name, lines=source_code.splitlines())
    tokens = lex.tokenize()
    print("Tokens:")
    print("-" * 20)
    pprint(tokens)
    (BUILD_DIR / f"{name}_tokens.txt").write_text("\n".join(map(str, tokens)))

    # Parsing and AST Generation
    parser = Parser(tokens)
    parser.parse()
    ast = parser.ast
    print("\nAST:")
    print("-" * 20)
    pprint(ast)
    (BUILD_DIR / f"{name}_ast.txt").write_text(repr(ast))

    # Semantic Analysis
    analyzer = SemanticAnalyzer(ast)
    symbol_table = analyzer.analyze()
    print("\nSymbol Table:")
    print("-" * 20)
    pprint(symbol_table)

    # Code Generation using llvmlite to generate LLVM IR
    codegen = CodeGenerator(ast)
    llvm_ir = codegen.generate()
    print("\nLLVM IR:")
    print("-" * 20)
    pprint(llvm_ir)

    if not llvm_ir:
        print("Error: LLVM IR generation failed.")
        return 1

    # Save the LLVM IR to a file
    ll_path = BUILD_DIR / f"{name}.ll"
    ll_path.write_text(llvm_ir)
    print(f"\nLLVM IR saved to {name}.ll")

    output_ll = ll_path
    # LLVM IR Optimization
    if args.optm:
        opt_ll_path = BUILD_DIR / f"{name}_opt.ll"
        run_command(["opt", "-O3", str(ll_path), "-o", str(opt_ll_path)])
        output_ll = opt_ll_path
        print(f"Optimized LLVM IR saved to {name}_opt.ll")

    # Compile LLVM IR to object code using llc (part of LLVM)
    obj_path = BUILD_DIR / f"{name}.o"
    run_command(["llc", "-filetype=obj", str(output_ll), "-o", str(obj_path)])
    print(f"LLVM object code saved to {name}.o")

    # Compile object code to executable (Linux)
    exec_path = BUILD_DIR / name
    run_command(["gcc", str(obj_path), "-o", str(exec_path)])
    print(f"Executable saved to {name}")

    if args.run:
        print(f"\nRunning {name}:")
        print("-" * 20)
        run_command([f"./{exec_path.relative_to(Path.cwd().parent)}"])

    return 0


if __name__ == "__main__":
    raise SystemError(main())
