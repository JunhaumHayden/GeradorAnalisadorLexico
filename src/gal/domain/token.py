"""Token produzido pelo analisador léxico."""

from __future__ import annotations

from dataclasses import dataclass

ERROR_PATTERN = "erro!"
"""Padrão associado a lexemas que não casam com nenhuma definição regular."""


@dataclass(frozen=True)
class Token:
    lexeme: str
    pattern: str
    line: int = 1
    column: int = 1

    @property
    def is_error(self) -> bool:
        return self.pattern == ERROR_PATTERN

    def __str__(self) -> str:
        return f"<{self.lexeme}, {self.pattern}>"
