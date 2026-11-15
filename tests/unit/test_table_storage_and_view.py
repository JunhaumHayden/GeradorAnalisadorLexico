import json

import pytest

from gal.application import generate_analyzer
from gal.domain import TableFormatError, Token
from gal.infrastructure import load_table, save_table, write_tokens
from gal.presentation.table_view import format_dfa, format_nfa


@pytest.fixture(scope="module")
def result():
    return generate_analyzer("id: [a-zA-Z]([a-zA-Z] | [0-9])*\nnum: [1-9]([0-9])* | 0\n")


def test_table_roundtrip(tmp_path, result):
    path = tmp_path / "sub" / "tabela.json"
    save_table(result.table, path)
    assert load_table(path) == result.table


def test_saved_table_is_plain_json(tmp_path, result):
    path = tmp_path / "t.json"
    save_table(result.table, path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["inicial"] == 0
    assert set(data["aceitacao"].values()) == {"id", "num"}


@pytest.mark.parametrize(
    "content",
    [
        "não é json",
        "[]",
        "{}",
        '{"versao": 99}',
        '{"versao": 1, "inicial": "x", "transicoes": {}, "aceitacao": {}}',
    ],
)
def test_load_rejects_invalid_files(tmp_path, content):
    path = tmp_path / "t.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(TableFormatError):
        load_table(path)


def test_write_tokens_one_per_line(tmp_path):
    path = tmp_path / "out" / "tokens.txt"
    write_tokens(path, [Token("a1", "id"), Token("0", "num")])
    assert path.read_text(encoding="utf-8") == "<a1, id>\n<0, num>\n"


def test_write_tokens_empty(tmp_path):
    path = tmp_path / "tokens.txt"
    write_tokens(path, [])
    assert path.read_text(encoding="utf-8") == ""


def test_dfa_view_groups_equivalent_columns_and_marks_states(result):
    text = format_dfa(result.table, "Tabela")
    lines = text.splitlines()
    assert lines[0] == "Tabela"
    assert "[A-Za-z]" in lines[1]  # 52 letras em uma única coluna
    assert "[1-9]" in lines[1]
    assert any(line.startswith("->q0") for line in lines)
    assert any(line.startswith("*q") and line.rstrip().endswith("id") for line in lines)
    assert any(line.startswith("*q") and line.rstrip().endswith("num") for line in lines)


def test_dfa_view_shows_missing_transitions_as_dash(result):
    assert " - " in format_dfa(result.table)


def test_nfa_view_has_epsilon_column_and_sets(result):
    text = format_nfa(result.afnd, "AFND")
    header = text.splitlines()[1]
    assert header.split(" | ")[-2:] == ["&", "token"] or "&" in header
    assert "{q" in text  # o inicial tem ε para vários estados


def test_view_escapes_whitespace_symbols():
    result = generate_analyzer("ws: [ \\t\\n]+\n")
    header = format_dfa(result.table).splitlines()[0]
    assert "␣" in header
    assert "\\t" in header
    assert "\\n" in header
