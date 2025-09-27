# Sigil

<p align="center">
    <img src="https://github.com/rdenadai/sigil/blob/main/static/flogo.png?raw=true" alt="Sigil programming language logo" width="200"/>
</p>

<p align="center">
    <em>A modern programming language.</em>
</p>

---

> [!WARNING]
> Sigil is a work in progress and is not yet stable. It is under active development, and breaking changes are expected.

## Requirements

To build and run Sigil, you need the following dependencies installed on your system:

- **Python 3.12+**: Can be installed using [pyenv](https://github.com/pyenv/pyenv) or [asdf](https://github.com/asdf-vm/asdf).
- **[uv](https://docs.astral.sh/uv/)**: A fast Python package installer from Astral.
- **[LLVM](https://releases.llvm.org/)**: The compiler infrastructure.
- **GCC**: The GNU Compiler Collection.

## Architecture

The Sigil compiler is built with a modular architecture, following a classic multi-stage compilation pipeline. The entire frontend is written in Python.

```
+-----------------------------------+
|      Frontend (Python)            |
+-----------------------------------+
|                                   |
|      Source Code (.sl)            |
|           |                       |
|           v                       |
|         Lexer --(Tokens)-->       |
|           |                       |
|           v                       |
|         Parser --(AST)-->         |
|           |                       |
|           v                       |
|   Semantic Analyzer --(Validated AST)--> |
|           |                       |
|           v                       |
|     Code Generator                |
|           | (LLVM IR)             |
|           v                       |
+-----------------------------------+
              |
              v
+-------------------------------------+
|    Backend (LLVM Toolchain)         |
+-------------------------------------+
|                                     |
|       LLVM IR (.ll)                 |
|           |                         |
|     +-----+------+                  |
|     |            |                  |
|     v            v                  |
| opt (Optional)   llc                |
|     |            ^                  |
| (Optimized IR)   |                  |
|     |            |                  |
|     +------>-----+                  |
|                  | (Object File .o) |
|                  v                  |
|                 gcc                 |
|                  | (Executable)     |
|                  v                  |
|             Executable              |
|                                     |
+-------------------------------------+
```

1.  **Lexical Analysis (`Lexer`)**: The source code is first processed by the lexer, which scans the text and converts it into a stream of tokens. This stage handles indentation, comments, and the basic elements of the language like keywords, identifiers, and operators.

2.  **Syntactic Analysis (`Parser`)**: The parser takes the stream of tokens and constructs an Abstract Syntax Tree (AST). This tree represents the hierarchical structure of the code and validates it against the language's grammar.

3.  **Semantic Analysis (`Analyzer`)**: The semantic analyzer traverses the AST to check for semantic correctness. It builds a symbol table to track variables, functions, and types, ensuring that the code is logically sound (e.g., type checking, scope resolution).

4.  **Code Generation (`CodeGenerator`)**: After analysis, the code generator walks the AST and translates it into LLVM Intermediate Representation (IR).

5.  **Backend Compilation**: The generated LLVM IR is then passed to the LLVM toolchain:
    - **`opt`**: An optional step to optimize the LLVM IR.
    - **`llc`**: Compiles the IR into a native object file (`.o`).
    - **`gcc`**: Links the object file to produce a final executable.

## How to Run

To compile a Sigil file (`.sl`), run the `main.py` script. The compilation artifacts, including tokens, AST, LLVM IR, and the final executable, will be placed in the `build/` directory.

**Basic Compilation:**

```sh
uv run python src/main.py examples/hello_world.sl
```

**Compile and Run:**

To compile and immediately execute the resulting program, use the `--run` flag.

```sh
uv run python src/main.py examples/hello_world.sl --run
```

**Compile with Optimizations:**

To enable LLVM optimizations at the `-O3` level, use the `--optm` flag. Currently, only `-O3` is supported; other optimization levels are not available.

```sh
uv run python src/main.py examples/hello_world.sl --optm --run
```
