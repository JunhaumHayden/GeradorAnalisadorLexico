"""Persistência da tabela de análise léxica em JSON.

Separa o projeto do analisador (que gera a tabela) da sua execução (que só
precisa da tabela), permitindo testar cada parte de forma independente.
"""

from __future__ import annotations

import json
from pathlib import Path

from gal.domain import Dfa, TableFormatError

_VERSION = 1


def save_table(table: Dfa, path: str | Path) -> None:
    data = {
        "versao": _VERSION,
        "inicial": table.start,
        "transicoes": {
            str(state): {symbol: target for symbol, target in sorted(row.items())}
            for state, row in sorted(table.transitions.items())
        },
        "aceitacao": {str(state): label for state, label in sorted(table.accepting.items())},
    }
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def load_table(path: str | Path) -> Dfa:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("versao") != _VERSION:
            raise TableFormatError(f"versão de tabela não suportada: {data.get('versao')!r}")
        return Dfa(
            start=int(data["inicial"]),
            transitions={
                int(state): {symbol: int(target) for symbol, target in row.items()}
                for state, row in data["transicoes"].items()
            },
            accepting={int(state): str(label) for state, label in data["aceitacao"].items()},
        )
    except (json.JSONDecodeError, KeyError, TypeError, ValueError, AttributeError) as error:
        raise TableFormatError(f"arquivo de tabela inválido: {path} ({error})") from error
