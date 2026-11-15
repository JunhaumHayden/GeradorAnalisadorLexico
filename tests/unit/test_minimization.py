import re

import pytest

from gal.algorithms import minimize, parse_regex, regex_to_dfa
from gal.domain import Dfa
from support import all_strings


def build(er: str, name: str = "p") -> Dfa:
    return regex_to_dfa(parse_regex(er), name)


@pytest.mark.parametrize(
    "er",
    ["(a|b)*abb", "a?(a|b)+", "(ab|ba)*", "a(b|c)?d+", "(a|b)*a(a|b)(a|b)", "(a?b?)+"],
)
def test_minimization_preserves_language(er):
    original = build(er)
    minimal = minimize(original)
    alphabet = "".join(original.alphabet)
    for text in all_strings(alphabet, 7):
        assert minimal.accepts(text) == original.accepts(text), f"{er!r} em {text!r}"


@pytest.mark.parametrize(
    ("er", "expected_states"),
    [
        ("(a|b)*abb", 4),
        ("a?(a|b)+", 2),  # equivale a (a|b)+
        ("a|a", 2),
        ("(a|b)*", 1),
        ("ab|ab", 3),
        ("a(b|b)c", 4),
        ("(a|b)(a|b)(a|b)", 4),
    ],
)
def test_minimization_reaches_minimal_state_count(er, expected_states):
    assert len(minimize(build(er)).states) == expected_states


def test_minimization_merges_equivalent_branches():
    # <|>|<=|>=|==|!= : os finais de '<', '>', '=' e '!' + '=' colapsam.
    original = build("<|>|<=|>=|==|!=")
    minimal = minimize(original)
    assert len(minimal.states) < len(original.states)
    for text in ["<", ">", "<=", ">=", "==", "!=", "=", "!", "<<", "=>"]:
        assert minimal.accepts(text) == original.accepts(text)


def test_minimization_never_merges_different_patterns():
    # Estados finais de padrões distintos têm o mesmo comportamento futuro,
    # mas não podem ser fundidos.
    left = Dfa(0, {0: {"a": 1}}, {1: "x"})
    right = Dfa(0, {0: {"b": 1}}, {1: "y"})
    merged = Dfa(
        0,
        {0: {"a": 1, "b": 2}},
        {1: "x", 2: "y"},
    )
    assert minimize(left).accepts("a") == "x"
    assert minimize(right).accepts("b") == "y"
    minimal = minimize(merged)
    assert minimal.accepts("a") == "x"
    assert minimal.accepts("b") == "y"
    assert len(minimal.states) == 3


def test_minimization_removes_unreachable_and_dead_states():
    dfa = Dfa(
        start=0,
        transitions={0: {"a": 1, "b": 2}, 1: {}, 2: {"a": 2}, 3: {"a": 1}},
        accepting={1: "p"},
    )
    minimal = minimize(dfa)  # 2 é morto; 3 é inalcançável
    assert len(minimal.states) == 2
    assert minimal.accepts("a") == "p"
    assert minimal.accepts("b") is None


def test_minimization_is_idempotent_and_deterministic():
    once = minimize(build("(a|b)*abb"))
    twice = minimize(once)
    assert once == twice


def test_minimized_dfa_matches_oracle():
    er = "[a-c]*b+"
    minimal = minimize(build(er))
    oracle = re.compile(er)
    for text in all_strings("abcd", 6):
        assert (minimal.accepts(text) == "p") == (oracle.fullmatch(text) is not None)
