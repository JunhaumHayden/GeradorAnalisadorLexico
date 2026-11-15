"""Parser de expressões regulares (descida recursiva).

Gramática (espaços fora de colchetes são ignorados):

    expr   := termo ('|' termo)*
    termo  := fator+
    fator  := atomo ('*' | '+' | '?')*
    atomo  := '(' expr ')' | '[' classe ']' | '{' nome '}' | '&' | '\\' c | c

`&` é a cadeia vazia (ε). `{nome}` insere uma definição regular anterior.
Os caracteres especiais ( ) [ ] { } | * + ? & \\ precisam de `\\` para serem
literais. Dentro de classes valem intervalos (`a-z`) e as escapes `\\n \\t \\r`.
"""

from __future__ import annotations

from collections.abc import Mapping

from gal.domain import (
    Concat,
    Epsilon,
    Node,
    Plus,
    RegexSyntaxError,
    Star,
    Symbols,
    Union,
    ZeroOrOne,
)

_ESCAPES = {"n": "\n", "t": "\t", "r": "\r"}
_POSTFIX = {"*": Star, "+": Plus, "?": ZeroOrOne}


def parse_regex(text: str, references: Mapping[str, Node] | None = None) -> Node:
    """Converte `text` em uma árvore de ER.

    `references` mapeia nomes de definições anteriores para suas árvores,
    permitindo a sintaxe `{nome}`.
    """
    return _Parser(text, references or {}).parse()


class _Parser:
    def __init__(self, text: str, references: Mapping[str, Node]) -> None:
        self._text = text
        self._references = references
        self._pos = 0

    def parse(self) -> Node:
        node = self._expr()
        if self._peek() is not None:  # só pode ser ')' sobrando
            raise RegexSyntaxError("')' sem '(' correspondente", self._pos)
        return node

    # --- gramática ------------------------------------------------------

    def _expr(self) -> Node:
        options = [self._term()]
        while self._peek() == "|":
            self._pos += 1
            options.append(self._term())
        return options[0] if len(options) == 1 else Union(tuple(options))

    def _term(self) -> Node:
        start = self._pos
        parts: list[Node] = []
        while (char := self._peek()) is not None and char not in "|)":
            parts.append(self._factor())
        if not parts:
            raise RegexSyntaxError("expressão vazia (use & para a cadeia vazia)", start)
        return parts[0] if len(parts) == 1 else Concat(tuple(parts))

    def _factor(self) -> Node:
        node = self._atom()
        while (char := self._peek()) in _POSTFIX:
            self._pos += 1
            node = _POSTFIX[char](node)
        return node

    def _atom(self) -> Node:
        char = self._peek()
        assert char is not None  # garantido por _term
        position = self._pos
        self._pos += 1

        if char == "(":
            node = self._expr()
            if self._peek() != ")":
                raise RegexSyntaxError("falta ')' para fechar o '('", position)
            self._pos += 1
            return node
        if char == "[":
            return self._char_class(position)
        if char == "{":
            return self._reference(position)
        if char == "&":
            return Epsilon()
        if char == "\\":
            return Symbols(frozenset(self._escaped(position)))
        if char in _POSTFIX:
            raise RegexSyntaxError(f"operador '{char}' sem operando", position)
        if char in "]}":
            raise RegexSyntaxError(f"'{char}' sem abertura correspondente (use \\{char})", position)
        return Symbols(frozenset(char))

    def _reference(self, opening: int) -> Node:
        end = self._text.find("}", self._pos)
        if end == -1:
            raise RegexSyntaxError("falta '}' para fechar a referência", opening)
        name = self._text[self._pos : end].strip()
        self._pos = end + 1
        if name not in self._references:
            raise RegexSyntaxError(f"definição '{name}' não existe ou é posterior", opening)
        return self._references[name]

    def _char_class(self, opening: int) -> Node:
        if self._text[self._pos : self._pos + 1] == "^":
            raise RegexSyntaxError(
                "negação de classe não é suportada (use \\^ para o caractere '^')", self._pos
            )
        chars: set[str] = set()
        while True:
            if self._pos >= len(self._text):
                raise RegexSyntaxError("falta ']' para fechar a classe", opening)
            if self._text[self._pos] == "]":
                self._pos += 1
                break
            low_pos = self._pos
            low = self._class_char()
            is_range = self._text[self._pos : self._pos + 1] == "-" and self._text[
                self._pos + 1 : self._pos + 2
            ] not in ("", "]")
            if is_range:
                self._pos += 1
                high = self._class_char()
                if low > high:
                    raise RegexSyntaxError(f"intervalo inválido '{low}-{high}'", low_pos)
                chars.update(chr(code) for code in range(ord(low), ord(high) + 1))
            else:
                chars.add(low)
        if not chars:
            raise RegexSyntaxError("classe vazia", opening)
        return Symbols(frozenset(chars))

    def _class_char(self) -> str:
        char = self._text[self._pos]
        position = self._pos
        self._pos += 1
        return self._escaped(position) if char == "\\" else char

    def _escaped(self, backslash: int) -> str:
        """Lê o caractere após uma `\\` (já consumida)."""
        if self._pos >= len(self._text):
            raise RegexSyntaxError("'\\' no fim da expressão", backslash)
        char = self._text[self._pos]
        self._pos += 1
        return _ESCAPES.get(char, char)

    # --- utilidades -----------------------------------------------------

    def _peek(self) -> str | None:
        """Próximo caractere significativo (pula espaços), sem consumi-lo."""
        while self._pos < len(self._text) and self._text[self._pos].isspace():
            self._pos += 1
        return self._text[self._pos] if self._pos < len(self._text) else None
