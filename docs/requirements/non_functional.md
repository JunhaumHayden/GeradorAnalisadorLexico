# Requisitos Não Funcionais

## 1. Introdução

Este documento especifica os requisitos não funcionais do GAL (Gerador de Analisadores Léxicos), estabelecendo características de qualidade, organização e restrições técnicas que deverão orientar seu desenvolvimento.

## 2. Requisitos não funcionais

### RNF01 — Modularidade

O sistema deverá possuir uma arquitetura modular, separando as responsabilidades relacionadas ao domínio, aos algoritmos, à aplicação, à infraestrutura e à apresentação.

### RNF02 — Legibilidade

O código-fonte deverá seguir convenções de estilo e boas práticas de programação Python, favorecendo sua compreensão e manutenção pelos integrantes do grupo.

### RNF03 — Testabilidade

Os componentes do sistema deverão ser desenvolvidos de maneira que permitam a realização de testes unitários, de integração e de aceitação.

### RNF04 — Manutenibilidade

A organização do código deverá facilitar a identificação, correção e evolução de componentes sem exigir alterações desnecessárias em outras partes do sistema.

### RNF05 — Portabilidade do ambiente

O ambiente de desenvolvimento deverá ser padronizado por meio de Docker Dev Containers, permitindo que os integrantes utilizem uma configuração reproduzível.

### RNF06 — Controle de versão

O desenvolvimento deverá utilizar Git para controle de versão e GitHub para hospedagem do repositório e colaboração entre os integrantes.

### RNF07 — Documentação

O projeto deverá possuir documentação suficiente para descrever sua arquitetura, requisitos, configuração do ambiente e instruções de utilização.

### RNF08 — Qualidade do código

O código-fonte deverá ser submetido a verificações automatizadas de qualidade e formatação utilizando Ruff.

### RNF09 — Compatibilidade tecnológica

O sistema deverá ser desenvolvido em Python, utilizando a versão 3.12 ou superior.

## 3. Organização e tecnologias

O projeto deverá utilizar as seguintes tecnologias e ferramentas:

- Python 3.12 ou superior.
- Docker e Docker Compose.
- PyCharm com suporte a Dev Containers.
- pytest para testes automatizados.
- Ruff para análise estática e formatação.
- Git e GitHub para controle de versão e colaboração.

## 4. Considerações

Os requisitos não funcionais estabelecem diretrizes para a organização e qualidade do GAL.

A implementação deverá considerar esses requisitos durante todas as etapas do desenvolvimento, desde a definição das estruturas fundamentais até a integração final do sistema.
