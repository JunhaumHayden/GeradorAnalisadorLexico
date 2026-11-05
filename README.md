#vGAL — Gerador de Analisadores Léxicos

Framework para geração de analisadores léxicos a partir de definições de expressões regulares, utilizando algoritmos de construção e manipulação de autômatos finitos.

## Sobre o projeto

O GAL é um projeto acadêmico desenvolvido com o objetivo de construir um framework capaz de gerar analisadores léxicos a partir de definições de expressões regulares.

A proposta envolve a conversão de expressões regulares em autômatos finitos, a manipulação e otimização desses autômatos e a geração de estruturas utilizadas no reconhecimento de lexemas.

## Funcionalidades previstas

- Conversão de expressões regulares em autômatos finitos determinísticos (AFD).

- Minimização de autômatos finitos.

- União de autômatos por meio de transições ε.

- Determinização de autômatos finitos não determinísticos (AFND).

- Geração de tabelas de análise léxica.

- Reconhecimento de lexemas e identificação de erros léxicos.

O projeto encontra-se em desenvolvimento. As funcionalidades serão implementadas e integradas progressivamente.

## Tecnologias

- Python 3.12
- Docker
- PyCharm
- pytest
- Ruff

---

## Ambiente de desenvolvimento

O projeto utiliza Docker Dev Containers para padronizar o ambiente de desenvolvimento.

O código-fonte é mantido no sistema hospedeiro (Ubuntu) e montado no container, no diretório /workspace.


### Configuração do ambiente

Abra o projeto na IDE e utilize a configuração disponível em:

`.devcontainer/devcontainer.json`

Crie ou inicie o Dev Container para acessar o ambiente de desenvolvimento.

As dependências de desenvolvimento são instaladas automaticamente durante a criação do ambiente.

---

## Requisitos

- Docker
- Docker Compose
- PyCharm/VS Code com suporte a Dev Containers

---

## Estrutura do projeto

O código está organizado em camadas:

- `domain`: representação dos conceitos fundamentais do domínio: estados, transições, autômatos, expressões regulares e tokens..
- `algorithms`: implementação dos algoritmos de autômatos: conversão, minimização, união e determinização..
- `application`: coordenação dos casos de uso.
- `infrastructure`: operações de entrada e saída.
- `presentation`: interface de interação com o usuário.

```plain text
 formais/
├── .devcontainer/
├── .github/
│   └── ISSUE_TEMPLATE/
├── docs/
│   ├── requirements/
│   ├── architecture/
│   │   └── decisions/
│   └── diagrams/
├── examples/
│   ├── definitions/
│   └── source_files/
├── src/
│   └── gal/
│       ├── domain/
│       ├── algorithms/
│       ├── application/
│       ├── infrastructure/
│       └── presentation/
└── tests/
    ├── unit/
    ├── integration/
    └── acceptance/
```

### Alguns exemplos de responsabilidades:

> Os nomes são sugestões, mas a separação de responsabilidades é o aspecto fundamental.

```plaintext
domain/
├── models/
│   ├── automaton.py
│   ├── state.py
│   ├── transition.py
│   └── lexical_table.py
│
├── algorithms/
│   ├── regex_to_automaton.py
│   ├── minimization.py
│   ├── union.py
│   └── determinization.py
│
├── application/
│   ├── project/
│   │   └── analyzer_generator.py
│   │
│   ├── execution/
│   │   └── lexical_analyzer.py
│   │
│   └── results/
│       └── operation_result.py
│
├── infrastructure/
│   ├── readers/
│   │   ├── definition_reader.py
│   │   └── source_reader.py
│   │
│   └── writers/
│       └── output_writer.py
│
└── presentation/
    ├── cli/
    └── tables/
```

`domain/` — Modelo do domínio

##### Representa os conceitos fundamentais do projeto:
- Estado de um autômato.
- Transição.
- Autômato finito.
- Expressão regular.
- Token.

`algorithms/` — Algoritmos

##### Conterá os algoritmos exigidos no trabalho:
- Conversão de ER para AFD.
- Minimização de AFD.
- União de autômatos por ε-transição.
- Determinização de AFND.

`application/` — Casos de uso

##### Coordena as operações do sistema. 
Por exemplo, gerar um analisador léxico a partir de várias definições de tokens.

`infrastructure/` — Entrada e saída

##### Responsável por ler arquivos de definição, ler arquivos-fonte e gerar arquivos de resultado.

`presentation/` — Interface

##### Responsável pela interação com o usuário.

---

## Execução dos testes

Para executar os testes automatizados:

```bash
pytest -v
```

## Verificação de qualidade

Para verificar possíveis problemas no código:

```bash
ruff check .
```

ou para verificar apenas os arquivos em `src` e `testes`

```bash
ruff check src tests
```

Para verificar a formatação:

```bash
ruff format --check .
```

Para formatar os arquivos automaticamente:

```bash
ruff format .
```

## Organização dos testes

Os testes estão divididos em três categorias:

- `tests/unit`: testes unitários dos componentes.
- `tests/integration`: testes de integração entre componentes.
- `tests/acceptance`: testes de aceitação das funcionalidades do sistema.

## Objetivo

Desenvolver um framework capaz de gerar analisadores léxicos a partir de definições de expressões regulares, utilizando algoritmos de construção e manipulação de autômatos finitos.

## Desenvolvimento

O projeto será desenvolvido de forma colaborativa, utilizando Git para controle de versão e GitHub para hospedagem do repositório e gerenciamento das atividades.