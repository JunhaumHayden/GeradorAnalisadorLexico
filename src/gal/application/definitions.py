"""Leitura do arquivo de definições regulares (Anexo I do enunciado).

Formato, uma definição por linha:

    nome: ER

Linhas em branco e linhas iniciadas por `#` são ignoradas. Nomes começados por
`_` são auxiliares (não geram token) e podem ser usados como `{nome}`.
"""

from __future__ import annotations

import re

from gal.algorithms import parse_regex
from gal.domain import DefinitionError, Node, RegexSyntaxError, RegularDefinition

_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*")


def parse_definitions(text: str) -> list[RegularDefinition]:
    """Converte o conteúdo do arquivo de definições em `RegularDefinition`s."""
    definitions: list[RegularDefinition] = []
    known: dict[str, Node] = {}

    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        name, separator, source = line.partition(":")
        name, source = name.strip(), source.strip()
        if not separator:
            raise DefinitionError("esperado 'nome: expressão'", number)
        if not _NAME.fullmatch(name):
            raise DefinitionError(f"nome de definição inválido: '{name}'", number)
        if name in known:
            raise DefinitionError(f"definição '{name}' repetida", number)
        if not source:
            raise DefinitionError(f"definição '{name}' sem expressão", number)

        try:
            expression = parse_regex(source, known)
        except RegexSyntaxError as error:
            raise DefinitionError(f"em '{name}': {error}", number) from error

        known[name] = expression
        definitions.append(RegularDefinition(name, expression, source, number))

    return definitions
