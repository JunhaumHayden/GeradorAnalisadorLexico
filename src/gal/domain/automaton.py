"""Autômatos finitos.

Estados são inteiros. Estados de aceitação carregam o nome do padrão (token)
que reconhecem, o que permite unir vários autômatos e ainda saber, ao final,
qual padrão casou.
"""

from __future__ import annotations

from dataclasses import dataclass, field

EPSILON = "&"
"""Notação de ε usada em sala e na interface do GAL."""


@dataclass
class Dfa:
    """Autômato finito determinístico, possivelmente parcial.

    A ausência de transição equivale a ir para um estado morto implícito.
    """

    start: int
    transitions: dict[int, dict[str, int]] = field(default_factory=dict)
    accepting: dict[int, str] = field(default_factory=dict)

    @property
    def states(self) -> list[int]:
        found = {self.start, *self.accepting}
        for source, row in self.transitions.items():
            found.add(source)
            found.update(row.values())
        return sorted(found)

    @property
    def alphabet(self) -> list[str]:
        return sorted({symbol for row in self.transitions.values() for symbol in row})

    def step(self, state: int, symbol: str) -> int | None:
        return self.transitions.get(state, {}).get(symbol)

    def accepts(self, text: str) -> str | None:
        """Retorna o padrão que aceita `text` por inteiro, ou None."""
        state = self.start
        for symbol in text:
            next_state = self.step(state, symbol)
            if next_state is None:
                return None
            state = next_state
        return self.accepting.get(state)


@dataclass
class Nfa:
    """Autômato finito não determinístico com ε-transições (símbolo `&`)."""

    start: int
    transitions: dict[int, dict[str, frozenset[int]]] = field(default_factory=dict)
    accepting: dict[int, str] = field(default_factory=dict)

    @property
    def states(self) -> list[int]:
        found = {self.start, *self.accepting}
        for source, row in self.transitions.items():
            found.add(source)
            for targets in row.values():
                found.update(targets)
        return sorted(found)

    @property
    def alphabet(self) -> list[str]:
        """Símbolos de entrada, sem o ε."""
        symbols = {s for row in self.transitions.values() for s in row}
        symbols.discard(EPSILON)
        return sorted(symbols)
