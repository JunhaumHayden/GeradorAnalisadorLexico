# GAL — Gerador de Analisadores Léxicos

Framework para geração de analisadores léxicos a partir de definições de expressões regulares.

## Tecnologias

- Python 3.12
- Docker
- PyCharm
- pytest
- Ruff

## Ambiente de desenvolvimento

O projeto utiliza Docker Dev Containers para padronizar o ambiente de desenvolvimento.

O código-fonte é mantido no sistema hospedeiro (Ubuntu) e montado no container.

## Estrutura do projeto

O código está organizado em camadas:

- `domain`: representação dos conceitos fundamentais do domínio.
- `algorithms`: implementação dos algoritmos de autômatos.
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
## Requisitos

- Docker
- Docker Compose
- PyCharm com suporte a Dev Containers

## Configuração do ambiente

Abra o projeto no PyCharm e utilize a configuração disponível em:

`.devcontainer/devcontainer.json`

Crie ou inicie o Dev Container para acessar o ambiente de desenvolvimento.

As dependências de desenvolvimento são instaladas automaticamente durante a criação do ambiente.

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