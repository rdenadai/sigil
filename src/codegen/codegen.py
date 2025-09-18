from __future__ import annotations

from typing import Any

from llvmlite import binding, ir


class CodegenError(Exception): ...


class CodeGenerator:
    def __init__(self, ast: dict[str, Any]):
        self._ast = ast
        self.module = ir.Module(name="sigil")

        binding.initialize()
        binding.initialize_native_target()
        binding.initialize_native_asmprinter()

        # Set the target triple for the module
        self.module.triple = binding.get_default_triple()

    def generate(self) -> str:
        return str(self.module)
