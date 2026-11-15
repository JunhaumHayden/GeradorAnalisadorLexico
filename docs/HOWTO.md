# HowTo — GAL, Gerador de Analisadores Léxicos

O GAL tem duas partes que funcionam de forma independente:

1. **Projeto** (`gerar`): lê as definições regulares e produz a tabela de análise léxica.
2. **Execução** (`analisar`): usa a tabela salva para analisar um texto fonte.

Os comandos abaixo valem dentro do Dev Container (diretório `/workspace`). Se o pacote não estiver
instalado, use `PYTHONPATH=src python -m gal ...` no lugar de `gal ...`.

```bash
pip install -e ".[dev]"     # opcional: instala o comando `gal`
```

## 1. Escrever as definições regulares

Um arquivo texto, uma definição por linha: `nome: ER`.

```
id: [a-zA-Z]([a-zA-Z] | [0-9])*
num: [1-9]([0-9])* | 0
```

| Sintaxe        | Significado                                                      |
|----------------|------------------------------------------------------------------|
| `ab`           | concatenação                                                     |
| `a \| b`       | união                                                            |
| `a*` `a+` `a?` | fecho, fecho positivo, zero ou uma vez                           |
| `( )`          | agrupamento                                                      |
| `[a-zA-Z0-9_]` | classe de caracteres (intervalos e caracteres avulsos)           |
| `&`            | cadeia vazia (ε)                                                 |
| `\*`, `\(`, …  | caractere especial literal; também `\n`, `\t`, `\r` e `\ ` (espaço) |
| `{nome}`       | reutiliza uma definição **anterior**                             |

Regras:

- Espaços fora de colchetes são ignorados. Dentro de `[ ]` o espaço é um caractere comum.
- Os caracteres `( ) [ ] { } \| * + ? & \` são especiais; escreva `\` antes para usá-los literalmente.
- Linhas em branco e linhas iniciadas por `#` são ignoradas.
- **Prioridade:** quando mais de um padrão aceita o mesmo lexema, vence o que foi definido
  primeiro. Por isso as palavras reservadas vêm antes de `id`.
- **Definições auxiliares:** nomes iniciados por `_` não geram token; servem apenas para serem
  reutilizados com `{nome}`.

```
_letra: [a-zA-Z_]
_digito: [0-9]
if: if
id: {_letra}({_letra} | {_digito})*
```

Limitações: não há negação de classe (`[^a]`) nem o curinga `.`.

## 2. Gerar o analisador

```bash
gal gerar examples/definitions/ex1_id_num.txt -o build/tabela.json
```

Opções úteis:

- `--mostrar` imprime a tabela de análise léxica.
- `--exportar DIR` grava em `DIR` os AFDs (antes e depois da minimização), o AFND da união e a
  tabela final, todos em forma de tabela de texto.

O pipeline executado é: ER → AFD (algoritmo do Aho, via followpos) → minimização → união por
ε-transições → determinização, que resulta na tabela de análise léxica.

## 3. Visualizar os autômatos

```bash
gal mostrar afds examples/definitions/ex1_id_num.txt                 # AFD de cada ER
gal mostrar afds examples/definitions/ex1_id_num.txt --minimizados   # AFDs minimizados
gal mostrar afnd examples/definitions/ex1_id_num.txt                 # AFND da união (coluna &)
gal mostrar tabela build/tabela.json                                 # tabela léxica final
```

Legenda: `->` estado inicial, `*` estado de aceitação, `-` sem transição, coluna `token` com o
padrão reconhecido. Símbolos com comportamento idêntico aparecem agrupados (`[a-zA-Z]`).

## 4. Analisar um texto fonte

```bash
gal analisar build/tabela.json examples/source_files/ex1_fonte.txt -o build/tokens.txt
```

Sem `-o`, os tokens vão para a saída padrão. Cada linha tem a forma `<lexema, padrão>`;
lexemas inválidos saem como `<lexema, erro!>` e o total de erros é avisado em stderr.

Dois modos de análise:

- **Padrão (maior casamento):** em cada posição consome o maior prefixo aceito. Espaços e
  quebras de linha separam lexemas, e `x=1+2` gera cinco tokens. Caracteres que não iniciam
  nenhum token são agrupados em um único lexema de erro.
- **`--palavra-inteira`:** cada palavra (separada por espaços) precisa casar por inteiro com um
  único padrão; senão a palavra inteira vira `erro!`. Com o Exemplo 1, `12ab` fica
  `<12ab, erro!>` em vez de `<12, num>` e `<ab, id>`.

## 5. Exemplos incluídos

| Definições (`examples/definitions`) | Texto fonte (`examples/source_files`) | O que mostra |
|---|---|---|
| `ex1_id_num.txt`      | `ex1_fonte.txt`    | Exemplo 1 do enunciado (identificadores e números) |
| `ex2_prefixo.txt`     | `ex2_fonte.txt`    | Exemplo 2 com `er1`/`er2` = "começa com a"/"começa com b", que reproduz a saída do enunciado |
| `ex2_literal.txt`     | `ex2_fonte.txt`    | Exemplo 2 exatamente como escrito: as duas ERs se sobrepõem e a primeira vence |
| `mini_linguagem.txt`  | `mini_programa.txt`| Palavras reservadas, auxiliares, operadores, maior casamento e erro léxico |

## 6. Testes e qualidade

```bash
pytest -v
ruff check .
ruff format --check .
```

Os testes validam os AFDs gerados contra o módulo `re` do Python em todas as cadeias de até 6 ou
7 símbolos, e cobrem cada algoritmo separadamente (`tests/unit`), o pipeline sobre os exemplos
(`tests/integration`) e a linha de comando (`tests/acceptance`).

## 7. Mapa do código

| Camada           | Conteúdo                                                                 |
|------------------|--------------------------------------------------------------------------|
| `domain`         | `Dfa`, `Nfa`, AST de ER, `Token`, exceções                               |
| `algorithms`     | `regex_parser`, `regex_to_dfa`, `minimization`, `automata_union`, `determinization`, `scanner` |
| `application`    | leitura das definições e casos de uso `generate_analyzer` / `run_analyzer` |
| `infrastructure` | leitura/escrita de arquivos e persistência da tabela em JSON             |
| `presentation`   | CLI (`gal`) e visualização em tabela                                     |
