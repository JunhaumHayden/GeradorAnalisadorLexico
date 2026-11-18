"""Leitura e escrita de arquivos texto."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from gal.domain import Token


def read_text(path: str | Path) -> str:
    # utf-8-sig descarta o BOM que alguns editores do Windows inserem.
    return Path(path).read_text(encoding="utf-8-sig")


def write_text(path: str | Path, content: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def write_tokens(path: str | Path, tokens: Iterable[Token]) -> None:
    """Grava um token por linha, no formato `<lexema, padrão>`."""
    lines = [str(token) for token in tokens]
    write_text(path, "\n".join(lines) + ("\n" if lines else ""))
