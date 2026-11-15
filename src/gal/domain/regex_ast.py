"""Árvore sintática (imutável) de expressões regulares.

A concatenação e a união são n-árias para manter a árvore rasa: uma palavra
reservada com centenas de letras não estoura o limite de recursão.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Epsilon:
    """Cadeia vazia (`&`)."""


@dataclass(frozen=True)
class Symbols:
    """Um único caractere ou uma classe de caracteres (`[a-z]`)."""

    chars: frozenset[str]


@dataclass(frozen=True)
class Concat:
    parts: tuple[Node, ...]


@dataclass(frozen=True)
class Union:
    options: tuple[Node, ...]


@dataclass(frozen=True)
class Star:
    """Fecho de Kleene (`*`)."""

    child: Node


@dataclass(frozen=True)
class Plus:
    """Fecho positivo (`+`)."""

    child: Node


@dataclass(frozen=True)
class ZeroOrOne:
    """Opcional (`?`)."""

    child: Node


Node = Epsilon | Symbols | Concat | Union | Star | Plus | ZeroOrOne


@dataclass(frozen=True)
class RegularDefinition:
    """Definição regular `nome: ER`.

    Definições cujo nome começa com `_` são auxiliares: podem ser referenciadas
    por `{nome}` em definições seguintes, mas não geram token.
    """

    name: str
    expression: Node
    source: str
    line: int

    @property
    def is_token(self) -> bool:
        return not self.name.startswith("_")
