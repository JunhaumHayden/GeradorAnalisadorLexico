"""União de autômatos via ε-transições."""

from __future__ import annotations

from collections.abc import Sequence

from gal.domain import EPSILON, Dfa, Nfa


def union_with_epsilon(automata: Sequence[Dfa]) -> Nfa:
    """Une os AFDs em um AFND com um novo estado inicial (0).

    O novo inicial tem uma ε-transição para o inicial de cada autômato; os
    demais estados são renumerados em blocos consecutivos, na ordem recebida,
    e os rótulos de aceitação são preservados.
    """
    transitions: dict[int, dict[str, frozenset[int]]] = {}
    accepting: dict[int, str] = {}
    starts: list[int] = []

    next_id = 1
    for automaton in automata:
        mapping = {state: next_id + i for i, state in enumerate(automaton.states)}
        next_id += len(mapping)
        starts.append(mapping[automaton.start])
        for state in automaton.states:
            row = automaton.transitions.get(state, {})
            transitions[mapping[state]] = {sym: frozenset({mapping[t]}) for sym, t in row.items()}
        for state, label in automaton.accepting.items():
            accepting[mapping[state]] = label

    transitions[0] = {EPSILON: frozenset(starts)} if starts else {}
    return Nfa(start=0, transitions=transitions, accepting=accepting)
