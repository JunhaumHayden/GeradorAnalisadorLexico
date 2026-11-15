"""Interface de linha de comando do GAL.

    gal gerar DEFINICOES -o TABELA [--exportar DIR] [--mostrar]
    gal analisar TABELA FONTE [-o SAIDA] [--palavra-inteira]
    gal mostrar tabela TABELA
    gal mostrar afds DEFINICOES [--minimizados]
    gal mostrar afnd DEFINICOES

Códigos de saída: 0 sucesso; 1 erro de uso, de arquivo ou de definição.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from gal.application import GenerationResult, generate_analyzer, run_analyzer
from gal.domain import GalError
from gal.infrastructure import load_table, read_text, save_table, write_text, write_tokens
from gal.presentation.table_view import format_dfa, format_nfa


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gal", description="GAL — Gerador de Analisadores Léxicos"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    generate = commands.add_parser("gerar", help="projeta o analisador a partir das definições")
    generate.add_argument("definicoes", type=Path, help="arquivo com as definições regulares")
    generate.add_argument("-o", "--saida", type=Path, required=True, help="tabela léxica (JSON)")
    generate.add_argument(
        "--exportar", type=Path, metavar="DIR", help="grava AFDs, AFND e tabela como texto em DIR"
    )
    generate.add_argument("--mostrar", action="store_true", help="imprime a tabela léxica")
    generate.set_defaults(handler=_cmd_generate)

    analyze = commands.add_parser("analisar", help="executa o analisador sobre um texto fonte")
    analyze.add_argument("tabela", type=Path, help="tabela léxica gerada por 'gerar'")
    analyze.add_argument("fonte", type=Path, help="arquivo com o texto fonte")
    analyze.add_argument("-o", "--saida", type=Path, help="arquivo de tokens (padrão: stdout)")
    analyze.add_argument(
        "--palavra-inteira",
        action="store_true",
        help="cada palavra (separada por espaços) deve casar inteira com um padrão",
    )
    analyze.set_defaults(handler=_cmd_analyze)

    show = commands.add_parser("mostrar", help="visualiza tabelas e autômatos")
    targets = show.add_subparsers(dest="alvo", required=True)

    show_table = targets.add_parser("tabela", help="tabela de análise léxica")
    show_table.add_argument("tabela", type=Path)
    show_table.set_defaults(handler=_cmd_show_table)

    show_afds = targets.add_parser("afds", help="AFD de cada definição regular")
    show_afds.add_argument("definicoes", type=Path)
    show_afds.add_argument("--minimizados", action="store_true", help="mostra os AFDs minimizados")
    show_afds.set_defaults(handler=_cmd_show_afds)

    show_afnd = targets.add_parser("afnd", help="AFND da união dos AFDs (ε-transições)")
    show_afnd.add_argument("definicoes", type=Path)
    show_afnd.set_defaults(handler=_cmd_show_afnd)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except (GalError, OSError) as error:
        print(f"gal: erro: {error}", file=sys.stderr)
        return 1


# --- comandos ----------------------------------------------------------------


def _generate(path: Path) -> GenerationResult:
    return generate_analyzer(read_text(path))


def _cmd_generate(args: argparse.Namespace) -> int:
    result = _generate(args.definicoes)
    save_table(result.table, args.saida)

    print(f"{len(result.token_names)} padrão(ões): {', '.join(result.token_names)}")
    for name in result.token_names:
        before = len(result.afds[name].states)
        after = len(result.minimized_afds[name].states)
        print(f"  {name}: AFD com {before} estado(s), minimizado com {after}")
    print(f"AFND (união): {len(result.afnd.states)} estado(s)")
    print(f"Tabela léxica: {len(result.table.states)} estado(s) -> {args.saida}")

    if args.exportar:
        _export(result, args.exportar)
        print(f"Autômatos exportados em {args.exportar}/")
    if args.mostrar:
        print()
        print(format_dfa(result.table, "Tabela de análise léxica"), end="")
    return 0


def _export(result: GenerationResult, directory: Path) -> None:
    for name in result.token_names:
        write_text(directory / f"afd_{name}.txt", format_dfa(result.afds[name], f"AFD de {name}"))
        write_text(
            directory / f"afd_{name}_minimizado.txt",
            format_dfa(result.minimized_afds[name], f"AFD minimizado de {name}"),
        )
    write_text(directory / "afnd_uniao.txt", format_nfa(result.afnd, "AFND (união com &)"))
    write_text(
        directory / "tabela_lexica.txt", format_dfa(result.table, "Tabela de análise léxica")
    )


def _cmd_analyze(args: argparse.Namespace) -> int:
    table = load_table(args.tabela)
    tokens = run_analyzer(table, read_text(args.fonte), whole_words=args.palavra_inteira)

    if args.saida:
        write_tokens(args.saida, tokens)
        print(f"{len(tokens)} token(s) gravado(s) em {args.saida}")
    else:
        for token in tokens:
            print(token)

    errors = sum(token.is_error for token in tokens)
    if errors:
        print(f"gal: {errors} erro(s) léxico(s)", file=sys.stderr)
    return 0


def _cmd_show_table(args: argparse.Namespace) -> int:
    print(format_dfa(load_table(args.tabela), "Tabela de análise léxica"), end="")
    return 0


def _cmd_show_afds(args: argparse.Namespace) -> int:
    result = _generate(args.definicoes)
    automata = result.minimized_afds if args.minimizados else result.afds
    suffix = " minimizado" if args.minimizados else ""
    print("\n".join(format_dfa(a, f"AFD{suffix} de {n}") for n, a in automata.items()), end="")
    return 0


def _cmd_show_afnd(args: argparse.Namespace) -> int:
    print(format_nfa(_generate(args.definicoes).afnd, "AFND (união com &)"), end="")
    return 0
