"""Visualização de autômatos em forma de tabela de transições.

Colunas de símbolos com transições idênticas (por exemplo, as 52 letras de
`[a-zA-Z]`) são agrupadas em uma só coluna, rotulada de forma compacta.

Convenções: `->` marca o estado inicial, `*` os de aceitação; a coluna final
mostra o padrão reconhecido. A ε-transição é escrita `&`.
"""

from __future__ import annotations

from collections.abc import Callable, Hashable

from gal.domain import EPSILON, Dfa, Nfa

_MIN_RANGE = 3


def format_dfa(dfa: Dfa, title: str = "") -> str:
    """Tabela de transições de um AFD (`-` = sem transição)."""
    states = dfa.states

    def cell(state: int, symbol: str) -> str:
        target = dfa.step(state, symbol)
        return "-" if target is None else f"q{target}"

    columns = _group_columns(dfa.alphabet, states, lambda s, c: dfa.step(s, c))
    return _render(
        title,
        states,
        dfa.start,
        dfa.accepting,
        [(label, symbols[0]) for label, symbols in columns],
        cell,
    )


def format_nfa(nfa: Nfa, title: str = "") -> str:
    """Tabela de transições de um AFND (conjuntos entre chaves; `&` = ε)."""
    states = nfa.states

    def targets(state: int, symbol: str) -> frozenset[int]:
        return nfa.transitions.get(state, {}).get(symbol, frozenset())

    def cell(state: int, symbol: str) -> str:
        found = sorted(targets(state, symbol))
        if not found:
            return "-"
        if len(found) == 1:
            return f"q{found[0]}"
        return "{" + ",".join(f"q{t}" for t in found) + "}"

    columns = _group_columns(nfa.alphabet, states, targets)
    headers = [(label, symbols[0]) for label, symbols in columns]
    if any(EPSILON in row for row in nfa.transitions.values()):
        headers.append((EPSILON, EPSILON))
    return _render(title, states, nfa.start, nfa.accepting, headers, cell)


# --- internos ---------------------------------------------------------------


def _group_columns(
    alphabet: list[str],
    states: list[int],
    lookup: Callable[[int, str], Hashable],
) -> list[tuple[str, list[str]]]:
    """Agrupa símbolos cuja coluna de transições é idêntica; devolve (rótulo, símbolos)."""
    groups: dict[tuple, list[str]] = {}
    for symbol in alphabet:
        signature = tuple(lookup(state, symbol) for state in states)
        groups.setdefault(signature, []).append(symbol)
    return [(_group_label(symbols), symbols) for symbols in groups.values()]


def _symbol_label(char: str) -> str:
    return {"\n": "\\n", "\t": "\\t", "\r": "\\r", " ": "␣", EPSILON: "\\&"}.get(char, char)


def _group_label(symbols: list[str]) -> str:
    if len(symbols) == 1:
        return _symbol_label(symbols[0])
    ordered = sorted(symbols)
    parts: list[str] = []
    index = 0
    while index < len(ordered):
        end = index
        while end + 1 < len(ordered) and ord(ordered[end + 1]) == ord(ordered[end]) + 1:
            end += 1
        if end - index + 1 >= _MIN_RANGE:
            parts.append(f"{_symbol_label(ordered[index])}-{_symbol_label(ordered[end])}")
        else:
            parts.extend(_symbol_label(c) for c in ordered[index : end + 1])
        index = end + 1
    return "[" + "".join(parts) + "]"


def _render(
    title: str,
    states: list[int],
    start: int,
    accepting: dict[int, str],
    headers: list[tuple[str, str]],
    cell: Callable[[int, str], str],
) -> str:
    """Monta a tabela; `headers` é uma lista de (rótulo, símbolo representante)."""
    labels = [label for label, _ in headers]
    has_tokens = bool(accepting)
    header_row = ["estado", *labels] + (["token"] if has_tokens else [])

    rows: list[list[str]] = []
    for state in states:
        marker = ("->" if state == start else "") + ("*" if state in accepting else "")
        row = [f"{marker}q{state}"]
        row.extend(cell(state, symbol) for _, symbol in headers)
        if has_tokens:
            row.append(accepting.get(state, ""))
        rows.append(row)

    widths = [max(len(r[i]) for r in [header_row, *rows]) for i in range(len(header_row))]

    def line(values: list[str]) -> str:
        return " | ".join(v.ljust(w) for v, w in zip(values, widths, strict=True)).rstrip()

    separator = "-+-".join("-" * w for w in widths)
    body = [line(header_row), separator, *(line(r) for r in rows)]
    return "\n".join(([title] if title else []) + body) + "\n"
