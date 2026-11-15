"""Testes de aceitação: usam a interface de linha de comando como o usuário usaria."""

from pathlib import Path

import pytest

from gal.presentation.cli import main

EXAMPLES = Path(__file__).resolve().parents[2] / "examples"
DEFINITIONS = EXAMPLES / "definitions"
SOURCES = EXAMPLES / "source_files"


def design(tmp_path: Path, definitions: str) -> Path:
    table = tmp_path / "tabela.json"
    assert main(["gerar", str(DEFINITIONS / definitions), "-o", str(table)]) == 0
    return table


def test_design_then_run_writes_the_token_file(tmp_path, capsys):
    table = design(tmp_path, "ex1_id_num.txt")
    output = tmp_path / "tokens.txt"
    code = main(["analisar", str(table), str(SOURCES / "ex1_fonte.txt"), "-o", str(output)])
    assert code == 0
    assert output.read_text(encoding="utf-8").splitlines() == [
        "<a1, id>",
        "<0, num>",
        "<teste2, id>",
        "<21, num>",
        "<alpha123, id>",
        "<3444, num>",
        "<a43teste, id>",
    ]
    assert "7 token(s)" in capsys.readouterr().out


def test_run_prints_to_stdout_by_default(tmp_path, capsys):
    table = design(tmp_path, "ex2_prefixo.txt")
    capsys.readouterr()
    assert main(["analisar", str(table), str(SOURCES / "ex2_fonte.txt")]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "<aa, er1>",
        "<bbbba, er2>",
        "<ababab, er1>",
        "<bbbbb, er2>",
    ]


def test_lexical_errors_are_reported_as_tokens_and_on_stderr(tmp_path, capsys):
    table = design(tmp_path, "mini_linguagem.txt")
    capsys.readouterr()
    assert main(["analisar", str(table), str(SOURCES / "mini_programa.txt")]) == 0
    captured = capsys.readouterr()
    assert "<@, erro!>" in captured.out.splitlines()
    assert "1 erro(s) léxico(s)" in captured.err


def test_whole_word_flag(tmp_path, capsys):
    table = design(tmp_path, "ex1_id_num.txt")
    source = tmp_path / "fonte.txt"
    source.write_text("ok 1x\n", encoding="utf-8")
    capsys.readouterr()
    main(["analisar", str(table), str(source), "--palavra-inteira"])
    assert capsys.readouterr().out.splitlines() == ["<ok, id>", "<1x, erro!>"]


def test_generate_summary_and_export(tmp_path, capsys):
    export = tmp_path / "automatos"
    code = main(
        [
            "gerar",
            str(DEFINITIONS / "ex1_id_num.txt"),
            "-o",
            str(tmp_path / "t.json"),
            "--exportar",
            str(export),
            "--mostrar",
        ]
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "2 padrão(ões): id, num" in out
    assert "Tabela de análise léxica" in out
    assert sorted(p.name for p in export.iterdir()) == [
        "afd_id.txt",
        "afd_id_minimizado.txt",
        "afd_num.txt",
        "afd_num_minimizado.txt",
        "afnd_uniao.txt",
        "tabela_lexica.txt",
    ]
    assert "AFD de num" in (export / "afd_num.txt").read_text(encoding="utf-8")


def test_show_table(tmp_path, capsys):
    table = design(tmp_path, "ex1_id_num.txt")
    capsys.readouterr()
    assert main(["mostrar", "tabela", str(table)]) == 0
    out = capsys.readouterr().out
    assert out.startswith("Tabela de análise léxica")
    assert "->q0" in out


def test_show_afds_original_and_minimized(capsys):
    path = str(DEFINITIONS / "ex1_id_num.txt")
    assert main(["mostrar", "afds", path]) == 0
    original = capsys.readouterr().out
    assert "AFD de id" in original
    assert "AFD de num" in original
    assert main(["mostrar", "afds", path, "--minimizados"]) == 0
    assert "AFD minimizado de id" in capsys.readouterr().out


def test_show_afnd(capsys):
    assert main(["mostrar", "afnd", str(DEFINITIONS / "ex1_id_num.txt")]) == 0
    out = capsys.readouterr().out
    assert "AFND (união com &)" in out
    assert "&" in out


def test_invalid_definition_returns_error_code(tmp_path, capsys):
    bad = tmp_path / "ruim.txt"
    bad.write_text("id: [a-z\n", encoding="utf-8")
    assert main(["gerar", str(bad), "-o", str(tmp_path / "t.json")]) == 1
    err = capsys.readouterr().err
    assert "linha 1" in err
    assert "falta ']'" in err


def test_missing_file_returns_error_code(tmp_path, capsys):
    assert main(["gerar", str(tmp_path / "nao_existe.txt"), "-o", str(tmp_path / "t.json")]) == 1
    assert "gal: erro:" in capsys.readouterr().err


def test_corrupt_table_returns_error_code(tmp_path, capsys):
    table = tmp_path / "t.json"
    table.write_text("lixo", encoding="utf-8")
    source = tmp_path / "f.txt"
    source.write_text("a", encoding="utf-8")
    assert main(["analisar", str(table), str(source)]) == 1
    assert "tabela inválido" in capsys.readouterr().err


def test_missing_subcommand_is_a_usage_error():
    with pytest.raises(SystemExit) as info:
        main([])
    assert info.value.code == 2
