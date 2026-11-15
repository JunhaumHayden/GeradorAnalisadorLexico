"""Determinização de AFND com ε-transições (construção de subconjuntos)."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable, Sequence

from gal.domain import EPSILON, Dfa, Nfa


def epsilon_closure(nfa: Nfa, states: Iterable[int]) -> frozenset[int]:
    """Estados alcançáveis a partir de `states` usando apenas ε-transições."""
    closure = set(states)
    stack = list(closure)
    while stack:
        state = stack.pop()
        for target in nfa.transitions.get(state, {}).get(EPSILON, ()):
            if target not in closure:
                closure.add(target)
                stack.append(target)
    return frozenset(closure)


def determinize(nfa: Nfa, priority: Sequence[str] = ()) -> Dfa:
    """Converte `nfa` em AFD.

    Quando um subconjunto contém estados de aceitação de padrões diferentes, o
    rótulo escolhido é o do padrão que aparece primeiro em `priority`
    (ordem de definição); padrões fora da lista perdem para os da lista e
    empatam por ordem alfabética.
    """
    rank = {name: i for i, name in enumerate(priority)}

    def best(labels: Iterable[str]) -> str:
        return min(labels, key=lambda label: (rank.get(label, len(rank)), label))

    start_set = epsilon_closure(nfa, [nfa.start])
    ids: dict[frozenset[int], int] = {start_set: 0}
    queue: deque[frozenset[int]] = deque([start_set])
    transitions: dict[int, dict[str, int]] = {}
    accepting: dict[int, str] = {}

    while queue:
        current = queue.popleft()
        state = ids[current]
        labels = [nfa.accepting[s] for s in current if s in nfa.accepting]
        if labels:
            accepting[state] = best(labels)

        by_symbol: dict[str, set[int]] = {}
        for nfa_state in current:
            for symbol, targets in nfa.transitions.get(nfa_state, {}).items():
                if symbol != EPSILON:
                    by_symbol.setdefault(symbol, set()).update(targets)

        row: dict[str, int] = {}
        for symbol in sorted(by_symbol):
            target = epsilon_closure(nfa, by_symbol[symbol])
            if target not in ids:
                ids[target] = len(ids)
                queue.append(target)
            row[symbol] = ids[target]
        transitions[state] = row

    return Dfa(start=0, transitions=transitions, accepting=accepting)
