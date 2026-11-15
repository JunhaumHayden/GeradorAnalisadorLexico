"""Algoritmos de construção e manipulação de autômatos finitos."""

from gal.algorithms.automata_union import union_with_epsilon
from gal.algorithms.determinization import determinize, epsilon_closure
from gal.algorithms.minimization import minimize
from gal.algorithms.regex_parser import parse_regex
from gal.algorithms.regex_to_dfa import regex_to_dfa
from gal.algorithms.scanner import tokenize

__all__ = [
    "determinize",
    "epsilon_closure",
    "minimize",
    "parse_regex",
    "regex_to_dfa",
    "tokenize",
    "union_with_epsilon",
]
