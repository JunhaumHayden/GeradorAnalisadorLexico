import re

from gal.algorithms import (
    determinize,
    epsilon_closure,
    minimize,
    parse_regex,
    regex_to_dfa,
    union_with_epsilon,
)
from gal.domain import EPSILON, Dfa, Nfa
from support import all_strings


def build(er: str, name: str) -> Dfa:
    return minimize(regex_to_dfa(parse_regex(er), name))


def test_union_adds_new_start_with_epsilon_to_each_automaton():
    first, second = build("a", "x"), build("b", "y")
    nfa = union_with_epsilon([first, second])
    assert nfa.start == 0
    assert set(nfa.transitions[0]) == {EPSILON}
    assert len(nfa.transitions[0][EPSILON]) == 2
    assert len(nfa.states) == 1 + len(first.states) + len(second.states)


def test_union_preserves_labels():
    nfa = union_with_epsilon([build("a", "x"), build("b", "y")])
    assert sorted(nfa.accepting.values()) == ["x", "y"]


def test_union_alphabet_excludes_epsilon():
    nfa = union_with_epsilon([build("a", "x"), build("b", "y")])
    assert nfa.alphabet == ["a", "b"]


def test_epsilon_closure_follows_chains():
    nfa = Nfa(
        start=0,
        transitions={
            0: {EPSILON: frozenset({1})},
            1: {EPSILON: frozenset({2}), "a": frozenset({3})},
            2: {},
            3: {},
        },
    )
    assert epsilon_closure(nfa, [0]) == frozenset({0, 1, 2})
    assert epsilon_closure(nfa, [3]) == frozenset({3})


def test_epsilon_closure_handles_cycles():
    nfa = Nfa(0, {0: {EPSILON: frozenset({1})}, 1: {EPSILON: frozenset({0})}})
    assert epsilon_closure(nfa, [0]) == frozenset({0, 1})


def test_determinize_classic_nfa():
    # (a|b)*abb como AFND com ε.
    nfa = Nfa(
        start=0,
        transitions={
            0: {EPSILON: frozenset({1, 7})},
            1: {EPSILON: frozenset({2, 4})},
            2: {"a": frozenset({3})},
            3: {EPSILON: frozenset({6})},
            4: {"b": frozenset({5})},
            5: {EPSILON: frozenset({6})},
            6: {EPSILON: frozenset({1, 7})},
            7: {"a": frozenset({8})},
            8: {"b": frozenset({9})},
            9: {"b": frozenset({10})},
            10: {},
        },
        accepting={10: "p"},
    )
    dfa = determinize(nfa)
    assert len(dfa.states) == 5  # A, B, C, D, E do exemplo do Aho
    oracle = re.compile("(a|b)*abb")
    for text in all_strings("ab", 7):
        assert (dfa.accepts(text) == "p") == (oracle.fullmatch(text) is not None)


def test_determinize_resolves_conflicts_by_priority():
    nfa = union_with_epsilon([build("a?(a|b)+", "er1"), build("b?(a|b)+", "er2")])
    assert determinize(nfa, priority=["er1", "er2"]).accepts("bbbba") == "er1"
    assert determinize(nfa, priority=["er2", "er1"]).accepts("bbbba") == "er2"


def test_determinize_without_priority_is_alphabetical():
    nfa = union_with_epsilon([build("a", "zeta"), build("a", "alfa")])
    assert determinize(nfa).accepts("a") == "alfa"


def test_union_then_determinize_matches_each_pattern_with_priority():
    patterns = [("kw", "if"), ("id", "[a-z]+"), ("num", "[0-9]+")]
    nfa = union_with_epsilon([build(er, name) for name, er in patterns])
    dfa = determinize(nfa, priority=[name for name, _ in patterns])
    oracles = [(name, re.compile(er)) for name, er in patterns]
    for text in all_strings("if0z", 4):
        expected = next((n for n, rx in oracles if rx.fullmatch(text)), None)
        assert dfa.accepts(text) == expected, text


def test_determinized_table_is_deterministic():
    nfa = union_with_epsilon([build("ab", "x"), build("ac", "y")])
    dfa = determinize(nfa, priority=["x", "y"])
    assert dfa.accepts("ab") == "x"
    assert dfa.accepts("ac") == "y"
    assert dfa.accepts("a") is None
