import pytest

from gal.algorithms import parse_regex
from gal.domain import (
    Concat,
    Epsilon,
    Plus,
    RegexSyntaxError,
    Star,
    Symbols,
    Union,
    ZeroOrOne,
)


def sym(chars: str) -> Symbols:
    return Symbols(frozenset(chars))


def test_single_symbol():
    assert parse_regex("a") == sym("a")


def test_concatenation_is_flat():
    assert parse_regex("abc") == Concat((sym("a"), sym("b"), sym("c")))


def test_union_has_lower_precedence_than_concatenation():
    assert parse_regex("ab|c") == Union((Concat((sym("a"), sym("b"))), sym("c")))


def test_postfix_operators_bind_to_the_last_atom():
    assert parse_regex("ab*") == Concat((sym("a"), Star(sym("b"))))
    assert parse_regex("a+") == Plus(sym("a"))
    assert parse_regex("a?") == ZeroOrOne(sym("a"))
    assert parse_regex("a*+") == Plus(Star(sym("a")))


def test_parentheses_group():
    assert parse_regex("(a|b)*") == Star(Union((sym("a"), sym("b"))))


def test_whitespace_outside_classes_is_ignored():
    assert parse_regex("[a-z] ( [a-z] | [0-9] ) *") == parse_regex("[a-z]([a-z]|[0-9])*")


def test_epsilon_symbol():
    assert parse_regex("a|&") == Union((sym("a"), Epsilon()))


def test_character_class_with_ranges_and_literals():
    assert parse_regex("[a-cX_]") == sym("abcX_")


def test_class_keeps_space_and_literal_dash_at_the_edges():
    assert parse_regex("[ a]") == sym(" a")
    assert parse_regex("[-a]") == sym("-a")
    assert parse_regex("[a-]") == sym("a-")


def test_escapes_make_special_characters_literal():
    assert parse_regex(r"\*\(\&\\") == Concat((sym("*"), sym("("), sym("&"), sym("\\")))
    assert parse_regex(r"\n\t") == Concat((sym("\n"), sym("\t")))
    assert parse_regex(r"\ ") == sym(" ")
    assert parse_regex(r"[\]\-\\]") == sym("]-\\")


def test_references_inline_previous_definitions():
    digit = parse_regex("[0-9]")
    assert parse_regex("{d}+", {"d": digit}) == Plus(digit)


@pytest.mark.parametrize(
    ("text", "fragment"),
    [
        ("", "vazia"),
        ("a|", "vazia"),
        ("|a", "vazia"),
        ("()", "vazia"),
        ("(a", "falta ')'"),
        ("a)", "sem '('"),
        ("*a", "sem operando"),
        ("a|*", "sem operando"),
        ("[a-", "falta ']'"),
        ("[]", "classe vazia"),
        ("[z-a]", "intervalo inválido"),
        ("[^a]", "negação"),
        ("a]", "sem abertura"),
        ("a}", "sem abertura"),
        ("{x", "falta '}'"),
        ("{x}", "não existe"),
        ("a\\", "fim da expressão"),
    ],
)
def test_syntax_errors(text, fragment):
    with pytest.raises(RegexSyntaxError) as info:
        parse_regex(text)
    assert fragment in str(info.value)


def test_error_reports_position():
    with pytest.raises(RegexSyntaxError) as info:
        parse_regex("ab(c")
    assert info.value.position == 2


def test_long_literal_does_not_hit_recursion_limit():
    assert isinstance(parse_regex("a" * 5000), Concat)
