"""Pipeline completo (definições -> tabela -> tokens) sobre os arquivos de exemplo."""

from pathlib import Path

import pytest

from gal.application import generate_analyzer, run_analyzer
from gal.infrastructure import load_table, read_text, save_table

EXAMPLES = Path(__file__).resolve().parents[2] / "examples"


def tokens_of(definitions: str, source: str, **kwargs) -> list[str]:
    result = generate_analyzer(read_text(EXAMPLES / "definitions" / definitions))
    text = read_text(EXAMPLES / "source_files" / source)
    return [str(t) for t in run_analyzer(result.table, text, **kwargs)]


def test_example_1_from_the_assignment():
    assert tokens_of("ex1_id_num.txt", "ex1_fonte.txt") == [
        "<a1, id>",
        "<0, num>",
        "<teste2, id>",
        "<21, num>",
        "<alpha123, id>",
        "<3444, num>",
        "<a43teste, id>",
    ]


def test_example_2_with_prefix_expressions_matches_the_assignment_output():
    assert tokens_of("ex2_prefixo.txt", "ex2_fonte.txt") == [
        "<aa, er1>",
        "<bbbba, er2>",
        "<ababab, er1>",
        "<bbbbb, er2>",
    ]


def test_example_2_literal_expressions_overlap_and_first_definition_wins():
    # a?(a|b)+ e b?(a|b)+ aceitam as mesmas cadeias: todas caem em er1.
    assert tokens_of("ex2_literal.txt", "ex2_fonte.txt") == [
        "<aa, er1>",
        "<bbbba, er1>",
        "<ababab, er1>",
        "<bbbbb, er1>",
    ]


def test_mini_language_program():
    tokens = tokens_of("mini_linguagem.txt", "mini_programa.txt")
    assert tokens[:8] == [
        "<int, int>",
        "<x1, id>",
        "<=, atrib>",
        "<10, num>",
        "<;, ponto_virgula>",
        "<while, while>",
        "<(, abre_par>",
        "<x1, id>",
    ]
    assert "<>=, op_rel>" in tokens
    assert "<3.14, real>" in tokens
    assert "<!=, op_rel>" in tokens
    assert "<@, erro!>" in tokens
    assert sum(t.endswith("erro!>") for t in tokens) == 1
    assert "<if, if>" in tokens and "<else, else>" in tokens


def test_keywords_beat_identifiers_but_longer_identifiers_win():
    result = generate_analyzer(read_text(EXAMPLES / "definitions" / "mini_linguagem.txt"))
    tokens = [str(t) for t in run_analyzer(result.table, "if iff ifx else elsewhere")]
    assert tokens == ["<if, if>", "<iff, id>", "<ifx, id>", "<else, else>", "<elsewhere, id>"]


def test_whole_word_mode_on_example_1():
    result = generate_analyzer(read_text(EXAMPLES / "definitions" / "ex1_id_num.txt"))
    tokens = [str(t) for t in run_analyzer(result.table, "abc 12ab 007", whole_words=True)]
    assert tokens == ["<abc, id>", "<12ab, erro!>", "<007, erro!>"]


def test_design_and_execution_are_independent_through_the_saved_table(tmp_path):
    result = generate_analyzer(read_text(EXAMPLES / "definitions" / "mini_linguagem.txt"))
    save_table(result.table, tmp_path / "t.json")
    text = read_text(EXAMPLES / "source_files" / "mini_programa.txt")
    assert run_analyzer(load_table(tmp_path / "t.json"), text) == run_analyzer(result.table, text)


def test_generation_exposes_every_intermediate_automaton():
    result = generate_analyzer(read_text(EXAMPLES / "definitions" / "ex1_id_num.txt"))
    assert result.token_names == ("id", "num")
    assert set(result.afds) == set(result.minimized_afds) == {"id", "num"}
    assert result.afnd.start == 0
    for name in result.token_names:
        assert len(result.minimized_afds[name].states) <= len(result.afds[name].states)


@pytest.mark.parametrize(
    ("er_a", "er_b"),
    [("a?(a|b)+", "(a|b)+"), ("(a|b)*", "(a*b*)*"), ("[0-9]+", "[0-9][0-9]*")],
)
def test_equivalent_expressions_produce_identical_tables(er_a, er_b):
    table_a = generate_analyzer(f"p: {er_a}\n").table
    table_b = generate_analyzer(f"p: {er_b}\n").table
    # Mesma linguagem + mesmo rótulo => mesma tabela após minimização do AFD da ER.
    from gal.algorithms import minimize

    assert minimize(table_a) == minimize(table_b)
