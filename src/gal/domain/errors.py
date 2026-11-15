"""Exceções do GAL."""

from __future__ import annotations


class GalError(Exception):
    """Erro base de todas as falhas previstas do GAL."""


class RegexSyntaxError(GalError):
    """Expressão regular malformada.

    `position` é o índice (base 0) do caractere problemático dentro da ER.
    """

    def __init__(self, message: str, position: int) -> None:
        super().__init__(f"{message} (coluna {position + 1} da expressão)")
        self.message = message
        self.position = position


class DefinitionError(GalError):
    """Arquivo de definições regulares inválido."""

    def __init__(self, message: str, line: int | None = None) -> None:
        prefix = f"linha {line}: " if line is not None else ""
        super().__init__(prefix + message)
        self.line = line


class TableFormatError(GalError):
    """Arquivo de tabela léxica salvo em formato inválido."""
