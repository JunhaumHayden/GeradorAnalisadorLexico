import pytest

from gal.application import generate_analyzer, parse_definitions
from gal.domain import DefinitionError


def test_parses_names_expressions_and_lines():
    definitions = parse_definitions("id: [a-z]+\n\nnum: [0-9]+\n")
    assert [(d.name, d.source, d.line) for d in definitions] == [
        ("id", "[a-z]+", 1),
        ("num", "[0-9]+", 3),
    ]


def test_hyphen_in_names_and_colon_in_expression():
    definitions = parse_definitions("def-reg1: a:b\n")
    assert definitions[0].name == "def-reg1"
    assert definitions[0].source == "a:b"


def test_comments_blank_lines_and_crlf_are_ignored():
    definitions = parse_definitions("# comentário\r\n\r\nid: a\r\n")
    assert [d.name for d in definitions] == ["id"]


def test_auxiliary_definitions_are_not_tokens():
    definitions = parse_definitions("_d: [0-9]\nnum: {_d}+\n")
    assert [d.is_token for d in definitions] == [False, True]


@pytest.mark.parametrize(
    ("text", "fragment"),
    [
        ("sem dois pontos", "esperado"),
        (": a", "nome de definição inválido"),
        ("1x: a", "nome de definição inválido"),
        ("a b: a", "nome de definição inválido"),
        ("id:", "sem expressão"),
        ("id: a\nid: b", "repetida"),
        ("id: (a", "falta ')'"),
        ("id: {x}", "não existe"),
        ("a: b\nid: {c}", "não existe"),
    ],
)
def test_definition_errors(text, fragment):
    with pytest.raises(DefinitionError) as info:
        parse_definitions(text)
    assert fragment in str(info.value)


def test_error_reports_the_line_number():
    with pytest.raises(DefinitionError, match="linha 3"):
        parse_definitions("a: a\n\nb: (b\n")


def test_forward_reference_is_rejected():
    with pytest.raises(DefinitionError, match="linha 1"):
        parse_definitions("a: {b}\nb: x\n")


def test_generation_requires_at_least_one_token():
    with pytest.raises(DefinitionError, match="nenhuma definição de token"):
        generate_analyzer("_aux: a\n")
    with pytest.raises(DefinitionError):
        generate_analyzer("\n# só comentário\n")
