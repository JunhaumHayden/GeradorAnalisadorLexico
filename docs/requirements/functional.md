# Requisitos Funcionais

## 1. Introdução

Este documento especifica os requisitos funcionais do GAL (Gerador de Analisadores Léxicos), descrevendo as funcionalidades que o sistema deverá disponibilizar.

O GAL deverá permitir a geração de analisadores léxicos a partir de definições de expressões regulares, utilizando algoritmos de construção e manipulação de autômatos finitos.

## 2. Requisitos funcionais

### RF01 — Leitura das definições de expressões regulares

O sistema deverá permitir a leitura de definições de expressões regulares fornecidas por meio de um arquivo de entrada.

As definições deverão respeitar o formato estabelecido pelo projeto:

`def-reg: ER`

### RF02 — Interpretação de expressões regulares

O sistema deverá interpretar expressões regulares utilizando a notação estabelecida pelo trabalho.

Deverá reconhecer:

- Operador de fechamento de Kleene (`*`).
- Operador de fechamento positivo (`+`).
- Operador opcional (`?`).
- Operador de alternância (`|`).
- Agrupamentos de caracteres, incluindo `[a-zA-Z]` e `[0-9]`.
- Representação de transição vazia por `&`.

### RF03 — Conversão de expressões regulares em AFD

O sistema deverá converter cada expressão regular válida em um autômato finito determinístico (AFD), utilizando o algoritmo de conversão especificado no trabalho.

### RF04 — Minimização de autômatos

O sistema deverá permitir a minimização dos autômatos finitos determinísticos gerados, preservando a linguagem reconhecida por cada autômato.

### RF05 — União de autômatos

O sistema deverá permitir a união de autômatos por meio da utilização de transições vazias (ε).

### RF06 — Determinização de autômatos

O sistema deverá permitir a conversão de autômatos finitos não determinísticos (AFND) em autômatos finitos determinísticos (AFD).

### RF07 — Geração da tabela de análise léxica

O sistema deverá gerar uma representação tabular que permita realizar a análise léxica a partir dos autômatos construídos e determinizados.

### RF08 — Visualização de autômatos

O sistema deverá permitir a visualização dos autômatos gerados, seja por meio de representação tabular ou de arquivo de saída.

### RF09 — Visualização da tabela de análise léxica

O sistema deverá permitir a visualização da tabela utilizada pelo analisador léxico.

### RF10 — Leitura do código-fonte

O sistema deverá permitir a leitura de um arquivo contendo o texto-fonte que será submetido à análise léxica.

### RF11 — Reconhecimento de lexemas

O sistema deverá analisar o texto-fonte utilizando a tabela de análise léxica gerada, identificando os lexemas reconhecidos e seus respectivos padrões.

### RF12 — Identificação de erros léxicos

O sistema deverá identificar trechos do texto-fonte que não sejam reconhecidos pelos padrões definidos.

### RF13 — Geração do resultado da análise léxica

O sistema deverá gerar um arquivo de saída contendo os resultados da análise, utilizando as seguintes representações:

- `<lexema, padrão>` para lexemas reconhecidos.
- `<lexema, erro!>` para trechos não reconhecidos.

## 3. Restrições de entrada

As expressões regulares deverão respeitar a notação e os operadores definidos pelo trabalho.

A representação de transições vazias deverá utilizar o símbolo `&`.

As definições deverão respeitar o formato de entrada especificado para o projeto.

## 4. Questões pendentes de especificação

Os seguintes aspectos precisam ser definidos pelo grupo antes da implementação:

- Qual será a interface de interação com o usuário?
- Como serão tratados padrões que reconhecem o mesmo lexema?
- Qual será a regra de prioridade entre padrões de tokens?
- Como será definido o comportamento diante de lexemas que possam ser reconhecidos por diferentes quantidades de caracteres?
- Como serão tratados espaços em branco e quebras de linha?
- Será permitido utilizar definições de expressões regulares dentro de outras definições?
- Qual será o formato detalhado dos arquivos de visualização dos autômatos e da tabela?

## 5. Considerações

Os requisitos apresentados descrevem as funcionalidades previstas para o GAL com base no escopo do trabalho acadêmico.

As questões pendentes deverão ser discutidas e documentadas antes da implementação das funcionalidades relacionadas.
