"""Minimização de AFD por refinamento de partições (Moore).

Estados de aceitação só são equivalentes se reconhecerem o mesmo padrão;
assim a minimização preserva o rótulo de token. O AFD é tratado como parcial:
transição ausente = estado morto implícito, e estados que não alcançam
aceitação são descartados antes do refinamento.
"""

from __future__ import annotations

from collections import deque

from gal.domain import Dfa


def minimize(dfa: Dfa) -> Dfa:
    """Retorna o AFD mínimo equivalente, com estados renumerados por BFS."""
    trimmed = _trim(dfa)
    states = trimmed.states

    # Partição inicial: um bloco por rótulo de aceitação, mais o bloco dos não aceitantes.
    labels = sorted(set(trimmed.accepting.values()))
    block_of_label: dict[str | None, int] = {None: 0}
    block_of_label.update({label: i + 1 for i, label in enumerate(labels)})
    block = {s: block_of_label[trimmed.accepting.get(s)] for s in states}
    block_count = len(set(block.values()))

    while True:
        signatures = {
            s: (
                block[s],
                tuple((sym, block[t]) for sym, t in sorted(trimmed.transitions.get(s, {}).items())),
            )
            for s in states
        }
        ids: dict[tuple, int] = {}
        block = {s: ids.setdefault(signatures[s], len(ids)) for s in states}
        if len(ids) == block_count:
            break
        block_count = len(ids)

    return _renumber(trimmed, block)


def _trim(dfa: Dfa) -> Dfa:
    """Mantém apenas estados alcançáveis a partir do inicial e que levam a aceitação."""
    reachable = {dfa.start}
    queue = deque([dfa.start])
    while queue:
        state = queue.popleft()
        for target in dfa.transitions.get(state, {}).values():
            if target not in reachable:
                reachable.add(target)
                queue.append(target)

    reverse: dict[int, set[int]] = {}
    for source in reachable:
        for target in dfa.transitions.get(source, {}).values():
            reverse.setdefault(target, set()).add(source)
    productive = {s for s in dfa.accepting if s in reachable}
    queue = deque(productive)
    while queue:
        state = queue.popleft()
        for source in reverse.get(state, ()):
            if source not in productive:
                productive.add(source)
                queue.append(source)

    keep = reachable & productive
    if dfa.start not in keep:  # linguagem vazia: sobra só o estado inicial
        return Dfa(start=dfa.start, transitions={dfa.start: {}}, accepting={})
    return Dfa(
        start=dfa.start,
        transitions={
            s: {sym: t for sym, t in dfa.transitions.get(s, {}).items() if t in keep} for s in keep
        },
        accepting={s: label for s, label in dfa.accepting.items() if s in keep},
    )


def _renumber(dfa: Dfa, block: dict[int, int]) -> Dfa:
    """Colapsa cada bloco em um estado, numerando em BFS (saída determinística)."""
    representative: dict[int, int] = {}
    for state in dfa.states:
        representative.setdefault(block[state], state)

    new_id: dict[int, int] = {block[dfa.start]: 0}
    queue = deque([block[dfa.start]])
    transitions: dict[int, dict[str, int]] = {}
    accepting: dict[int, str] = {}
    while queue:
        current = queue.popleft()
        rep = representative[current]
        row: dict[str, int] = {}
        for symbol, target in sorted(dfa.transitions.get(rep, {}).items()):
            target_block = block[target]
            if target_block not in new_id:
                new_id[target_block] = len(new_id)
                queue.append(target_block)
            row[symbol] = new_id[target_block]
        transitions[new_id[current]] = row
        if rep in dfa.accepting:
            accepting[new_id[current]] = dfa.accepting[rep]
    return Dfa(start=0, transitions=transitions, accepting=accepting)
