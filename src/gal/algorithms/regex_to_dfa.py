"""Conversão direta de ER para AFD (Aho, Lam, Sethi, Ullman — seção 3.9).

Algoritmo:
  1. Aumenta a ER com o marcador de fim `#`: (r)#.
  2. Numera as folhas (posições) e calcula nullable, firstpos, lastpos e
     followpos sobre a árvore.
  3. Estados do AFD são conjuntos de posições; o inicial é firstpos(raiz).
     Δ(S, a) = união de followpos(p), para cada p em S cujo símbolo é a.
  4. Estados que contêm a posição de `#` são de aceitação.
"""

from __future__ import annotations

from collections import deque
from typing import NamedTuple

from gal.domain import (
    Concat,
    Dfa,
    Epsilon,
    Node,
    Plus,
    Star,
    Symbols,
    Union,
    ZeroOrOne,
)


class _Info(NamedTuple):
    nullable: bool
    first: frozenset[int]
    last: frozenset[int]


class _Analysis:
    """Percorre a árvore numerando posições e acumulando followpos.

    As posições são atribuídas pela ordem de visita, não por identidade de nó:
    uma subárvore reutilizada via `{nome}` ganha posições distintas a cada uso.
    """

    def __init__(self) -> None:
        self.symbols: list[frozenset[str] | None] = []  # None = marcador `#`
        self.follow: list[set[int]] = []

    def new_position(self, chars: frozenset[str] | None) -> int:
        self.symbols.append(chars)
        self.follow.append(set())
        return len(self.symbols) - 1

    def visit(self, node: Node) -> _Info:
        match node:
            case Epsilon():
                return _Info(True, frozenset(), frozenset())
            case Symbols(chars):
                position = frozenset({self.new_position(chars)})
                return _Info(False, position, position)
            case Concat(parts):
                return self._concat([self.visit(part) for part in parts])
            case Union(options):
                infos = [self.visit(option) for option in options]
                return _Info(
                    any(info.nullable for info in infos),
                    frozenset().union(*(info.first for info in infos)),
                    frozenset().union(*(info.last for info in infos)),
                )
            case Star(child):
                info = self.visit(child)
                self._loop(info)
                return _Info(True, info.first, info.last)
            case Plus(child):
                info = self.visit(child)
                self._loop(info)
                return info
            case ZeroOrOne(child):
                info = self.visit(child)
                return _Info(True, info.first, info.last)
        raise TypeError(f"nó de ER desconhecido: {node!r}")

    def _loop(self, info: _Info) -> None:
        for position in info.last:
            self.follow[position] |= info.first

    def _concat(self, infos: list[_Info]) -> _Info:
        # first_from[i] = firstpos da concatenação infos[i:].
        first_from: list[frozenset[int]] = [frozenset()] * (len(infos) + 1)
        for i in range(len(infos) - 1, -1, -1):
            info = infos[i]
            first_from[i] = info.first | first_from[i + 1] if info.nullable else info.first
        for i, info in enumerate(infos[:-1]):
            for position in info.last:
                self.follow[position] |= first_from[i + 1]

        last: frozenset[int] = frozenset()
        for info in reversed(infos):
            last |= info.last
            if not info.nullable:
                break
        return _Info(all(info.nullable for info in infos), first_from[0], last)


def regex_to_dfa(expression: Node, pattern: str) -> Dfa:
    """Constrói o AFD (parcial, sem estado morto) de `expression`.

    Os estados de aceitação ficam rotulados com `pattern`.
    """
    analysis = _Analysis()
    root = analysis.visit(expression)
    end = analysis.new_position(None)
    for position in root.last:
        analysis.follow[position].add(end)
    start_set = root.first | {end} if root.nullable else root.first

    ids: dict[frozenset[int], int] = {start_set: 0}
    queue: deque[frozenset[int]] = deque([start_set])
    transitions: dict[int, dict[str, int]] = {}
    accepting: dict[int, str] = {}

    while queue:
        current = queue.popleft()
        state = ids[current]
        if end in current:
            accepting[state] = pattern

        by_symbol: dict[str, set[int]] = {}
        for position in current:
            chars = analysis.symbols[position]
            if chars is None:
                continue
            for char in chars:
                by_symbol.setdefault(char, set()).update(analysis.follow[position])

        row: dict[str, int] = {}
        for char in sorted(by_symbol):
            target = frozenset(by_symbol[char])
            if not target:
                continue
            if target not in ids:
                ids[target] = len(ids)
                queue.append(target)
            row[char] = ids[target]
        transitions[state] = row

    return Dfa(start=0, transitions=transitions, accepting=accepting)
