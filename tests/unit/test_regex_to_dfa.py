"""ER -> AFD, validado contra o módulo `re` como oráculo."""

import re

import pytest

from gal.algorithms import parse_regex, regex_to_dfa
from support import all_strings

CASES = [
    ("a", "ab"),
    ("ab", "ab"),
    ("a|b", "ab"),
    ("a*", "ab"),
    ("a+", "ab"),
    ("a?", "ab"),
    ("a?(a|b)+", "ab"),
    ("b?(a|b)+", "ab"),
    ("(a|b)*abb", "ab"),
    ("(ab|ba)*", "ab"),
    ("a(b|c)?d+", "abcd"),
    ("[a-c]*b+", "abcd"),
    ("(a*b*)*", "ab"),
    ("(a|b)*a(a|b)(a|b)", "ab"),
    ("(a*)*", "ab"),
    ("(a+)+b?", "ab"),
    ("[1-9][0-9]*|0", "019"),
    ("(a?b?)+", "ab"),
]


@pytest.mark.parametrize(("er", "alphabet"), CASES)
def test_dfa_matches_python_re(er, alphabet):
    dfa = regex_to_dfa(parse_regex(er), "p")
    oracle = re.compile(er)
    for text in all_strings(alphabet, 6):
        expected = oracle.fullmatch(text) is not None
        assert (dfa.accepts(text) == "p") == expected, f"{er!r} em {text!r}"


def test_epsilon_only_accepts_empty_string():
    dfa = regex_to_dfa(parse_regex("&"), "e")
    assert dfa.accepts("") == "e"
    assert dfa.accepts("a") is None


def test_union_with_epsilon_makes_expression_nullable():
    dfa = regex_to_dfa(parse_regex("a|&"), "p")
    assert dfa.accepts("") == "p"
    assert dfa.accepts("a") == "p"
    assert dfa.accepts("aa") is None


def test_dfa_is_deterministic_and_has_no_dead_state():
    dfa = regex_to_dfa(parse_regex("(a|b)*abb"), "p")
    # Todo estado tem caminho até a aceitação (AFD parcial, sem estado morto).
    assert dfa.accepts("abb") == "p"
    assert len(dfa.states) == 4  # número clássico de estados do exemplo do Aho


def test_accepting_states_carry_the_pattern_name():
    dfa = regex_to_dfa(parse_regex("ab"), "meu_token")
    assert set(dfa.accepting.values()) == {"meu_token"}


def test_reused_subtree_gets_independent_positions():
    digit = parse_regex("[0-9]")
    expression = parse_regex("{d}{d}-{d}", {"d": digit})
    dfa = regex_to_dfa(expression, "p")
    assert dfa.accepts("12-3") == "p"
    assert dfa.accepts("1-3") is None
    assert dfa.accepts("12-34") is None
