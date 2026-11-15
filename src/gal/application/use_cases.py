"""Casos de uso do GAL: projetar um analisador léxico e executá-lo."""

from __future__ import annotations

from dataclasses import dataclass

from gal.algorithms import (
    determinize,
    minimize,
    regex_to_dfa,
    tokenize,
    union_with_epsilon,
)
from gal.application.definitions import parse_definitions
from gal.domain import DefinitionError, Dfa, Nfa, RegularDefinition, Token


@dataclass(frozen=True)
class GenerationResult:
    """Todos os artefatos produzidos ao projetar um analisador léxico."""

    definitions: tuple[RegularDefinition, ...]
    token_names: tuple[str, ...]  # em ordem de prioridade
    afds: dict[str, Dfa]  # AFD de cada ER, direto da conversão
    minimized_afds: dict[str, Dfa]  # os mesmos AFDs, minimizados
    afnd: Nfa  # união dos AFDs minimizados via ε-transições
    table: Dfa  # tabela de análise léxica (AFND determinizado)


def generate_analyzer(definitions_text: str) -> GenerationResult:
    """Projeta o analisador léxico a partir do texto de definições regulares.

    Pipeline: ER → AFD (Aho) → minimização → união com ε → determinização.
    """
    definitions = parse_definitions(definitions_text)
    tokens = [d for d in definitions if d.is_token]
    if not tokens:
        raise DefinitionError(
            "nenhuma definição de token (todas são auxiliares ou o arquivo é vazio)"
        )

    afds = {d.name: regex_to_dfa(d.expression, d.name) for d in tokens}
    minimized = {name: minimize(afd) for name, afd in afds.items()}
    names = tuple(afds)
    afnd = union_with_epsilon([minimized[name] for name in names])
    table = determinize(afnd, priority=names)

    return GenerationResult(
        definitions=tuple(definitions),
        token_names=names,
        afds=afds,
        minimized_afds=minimized,
        afnd=afnd,
        table=table,
    )


def run_analyzer(table: Dfa, source_text: str, *, whole_words: bool = False) -> list[Token]:
    """Executa o analisador (tabela) sobre o texto fonte."""
    return tokenize(table, source_text, whole_words=whole_words)
