"""Utilitários compartilhados pelos testes."""

from __future__ import annotations

import itertools
from collections.abc import Iterator


def all_strings(alphabet: str, max_length: int) -> Iterator[str]:
    """Todas as cadeias sobre `alphabet` com até `max_length` símbolos (inclui a vazia)."""
    for length in range(max_length + 1):
        for combo in itertools.product(alphabet, repeat=length):
            yield "".join(combo)
