# Decisões arquiteturais


| ID | Decisão | Definição |
|---|---|---|
| ADR-001 | Comunicação entre módulos | Objetos Python tipados. |
| ADR-002 | Representação de dados | Classes e `dataclasses`. |
| ADR-003 | Tratamento de falhas | Resultado padronizado com sucesso ou mensagem de erro. |
| ADR-004 | Separação de responsabilidades | Algoritmos independentes de entrada, saída e apresentação. |
| ADR-005 | Fluxo de projeto | ER → AFD → minimização → união → determinização → tabela léxica. |
| ADR-006 | Fluxo de execução | Texto-fonte + tabela léxica → resultado da análise. |
| ADR-007 | Visualização | Componentes separados para autômatos e tabela léxica. |
| ADR-008 | Armazenamento | Dados processados mantidos exclusivamente em memória. |
| ADR-009 | Persistência | Nenhuma persistência dos autômatos ou da tabela léxica. Apenas o arquivo de saída exigido pelo trabalho. |
| ADR-010 | Ciclo de vida | Novo projeto substitui os dados anteriores; encerramento libera os dados em memória. |

### Boas práticas que continuaremos adotando
Simplicidade não significa abandonar boas práticas. Eu manteria:
- Responsabilidade única: cada classe deve ter uma função bem definida.
- Tipagem explícita: parâmetros e retornos com type hints.
- Baixo acoplamento: algoritmos não devem depender da interface.
- Alta coesão: classes relacionadas devem trabalhar sobre o mesmo conceito.
- Tratamento de exceções: apresentar mensagens de erro em vez de deixar exceções inesperadas chegarem ao usuário.
- Testes automatizados: validar os algoritmos individualmente e depois sua integração.
- Código legível: nomes claros, métodos pequenos e documentação objetiva.