"""Análise léxica com a tabela (AFD) gerada.

Dois modos:

* Padrão — maior casamento (maximal munch): em cada posição consome o maior
  prefixo aceito pela tabela. Espaços e quebras de linha separam lexemes.
  Caracteres que não iniciam nenhum token são agrupados em um lexema de erro.
* Palavra inteira — o texto é dividido por espaços e cada palavra precisa ser
  aceita por completo por um único padrão; caso contrário a palavra toda vira
  erro.
"""

from __future__ import annotations

import re
from bisect import bisect_right

from gal.domain import ERROR_PATTERN, Dfa, Token


def tokenize(table: Dfa, text: str, *, whole_words: bool = False) -> list[Token]:
    """Analisa `text` e devolve a lista de tokens (incluindo os de erro)."""
    locate = _locator(text)
    if whole_words:
        return _tokenize_words(table, text, locate)
    return _tokenize_longest(table, text, locate)


def _longest_match(table: Dfa, text: str, start: int) -> tuple[int, str] | None:
    """Maior prefixo não vazio de `text[start:]` aceito pela tabela: (fim, padrão)."""
    state = table.start
    best: tuple[int, str] | None = None
    index = start
    while index < len(text):
        next_state = table.step(state, text[index])
        if next_state is None:
            break
        state = next_state
        index += 1
        if state in table.accepting:
            best = (index, table.accepting[state])
    return best


def _tokenize_longest(table: Dfa, text: str, locate) -> list[Token]:
    tokens: list[Token] = []
    error_start: int | None = None
    index = 0

    def flush_error(end: int) -> None:
        nonlocal error_start
        if error_start is not None:
            line, column = locate(error_start)
            tokens.append(Token(text[error_start:end], ERROR_PATTERN, line, column))
            error_start = None

    while index < len(text):
        match = _longest_match(table, text, index)
        if match is not None:
            flush_error(index)
            end, pattern = match
            line, column = locate(index)
            tokens.append(Token(text[index:end], pattern, line, column))
            index = end
        elif text[index].isspace():
            flush_error(index)
            index += 1
        else:
            if error_start is None:
                error_start = index
            index += 1
    flush_error(len(text))
    return tokens


def _tokenize_words(table: Dfa, text: str, locate) -> list[Token]:
    tokens: list[Token] = []
    for found in re.finditer(r"\S+", text):
        word = found.group()
        match = _longest_match(table, word, 0)
        pattern = match[1] if match is not None and match[0] == len(word) else ERROR_PATTERN
        line, column = locate(found.start())
        tokens.append(Token(word, pattern, line, column))
    return tokens


def _locator(text: str):
    """Devolve uma função índice -> (linha, coluna), ambas base 1."""
    line_starts = [0] + [m.end() for m in re.finditer(r"\n", text)]

    def locate(index: int) -> tuple[int, int]:
        line = bisect_right(line_starts, index)
        return line, index - line_starts[line - 1] + 1

    return locate
