import pytest

from gal.application import generate_analyzer
from gal.domain import ERROR_PATTERN, Token

DEFINITIONS = """
if: if
id: [a-z]+
num: [0-9]+
real: [0-9]+\\.[0-9]+
le: <=
lt: <
eq: =
"""


@pytest.fixture(scope="module")
def table():
    return generate_analyzer(DEFINITIONS).table


def run(table, text, **kwargs):
    from gal.algorithms import tokenize

    return [(t.lexeme, t.pattern) for t in tokenize(table, text, **kwargs)]


def test_priority_goes_to_the_first_definition(table):
    assert run(table, "if iff") == [("if", "if"), ("iff", "id")]


def test_maximal_munch(table):
    assert run(table, "<= < 3.14 3") == [
        ("<=", "le"),
        ("<", "lt"),
        ("3.14", "real"),
        ("3", "num"),
    ]


def test_tokens_without_separating_spaces(table):
    assert run(table, "ab=12<=x") == [
        ("ab", "id"),
        ("=", "eq"),
        ("12", "num"),
        ("<=", "le"),
        ("x", "id"),
    ]


def test_backtracks_to_last_accepting_prefix(table):
    # "3." entra no ramo de `real` mas só "3" é aceito; o "." vira erro.
    assert run(table, "3.x") == [("3", "num"), (".", ERROR_PATTERN), ("x", "id")]


def test_consecutive_invalid_characters_form_one_error_lexeme(table):
    assert run(table, "a@#$b") == [("a", "id"), ("@#$", ERROR_PATTERN), ("b", "id")]


def test_error_at_start_and_end(table):
    assert run(table, "@a@") == [("@", ERROR_PATTERN), ("a", "id"), ("@", ERROR_PATTERN)]


def test_uppercase_is_not_in_the_alphabet(table):
    assert run(table, "aBc") == [("a", "id"), ("B", ERROR_PATTERN), ("c", "id")]


def test_whitespace_separates_and_is_never_reported(table):
    assert run(table, "  a \t\n b\r\n") == [("a", "id"), ("b", "id")]


def test_empty_text_yields_no_tokens(table):
    assert run(table, "") == []
    assert run(table, " \n ") == []


def test_positions_are_one_based(table):
    from gal.algorithms import tokenize

    tokens = tokenize(table, "ab 12\n  x @")
    assert tokens == [
        Token("ab", "id", 1, 1),
        Token("12", "num", 1, 4),
        Token("x", "id", 2, 3),
        Token("@", ERROR_PATTERN, 2, 5),
    ]


def test_whole_word_mode_accepts_complete_words(table):
    assert run(table, "if abc 42", whole_words=True) == [
        ("if", "if"),
        ("abc", "id"),
        ("42", "num"),
    ]


def test_whole_word_mode_rejects_partially_valid_words(table):
    assert run(table, "12abc ok", whole_words=True) == [
        ("12abc", ERROR_PATTERN),
        ("ok", "id"),
    ]


def test_whole_word_mode_does_not_accept_shorter_prefix(table):
    assert run(table, "3.", whole_words=True) == [("3.", ERROR_PATTERN)]


def test_pattern_may_define_whitespace_tokens():
    table = generate_analyzer("ws: [ \\t]+\nid: [a-z]+\n").table
    assert run(table, "a  b") == [("a", "id"), ("  ", "ws"), ("b", "id")]


def test_token_string_format():
    assert str(Token("a1", "id")) == "<a1, id>"
    assert str(Token("@", ERROR_PATTERN)) == "<@, erro!>"
    assert Token("@", ERROR_PATTERN).is_error
    assert not Token("a", "id").is_error
