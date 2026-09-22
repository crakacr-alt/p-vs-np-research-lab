# Changelog

Все заметные изменения проекта фиксируются здесь.

## 1.0.0 — 2026-09-23

### Научная часть

- реализован первый exact representation switch: 3-CNF XOR -> GF(2);
- добавлен Gaussian elimination для XOR equations;
- добавлены XOR propagation и direct linear solve;
- расширены solver metrics;
- добавлен brute-force oracle для независимой проверки;
- добавлены структурные benchmark-семейства;
- добавлен release benchmark с CSV/JSON/Markdown отчётом;
- усилена differential verification.

### Инструменты

- добавлена команда `pnp-lab doctor`;
- добавлена команда `pnp-lab benchmark`;
- solver `switch` стал стандартным в CLI;
- MCP расширен benchmark/hypothesis инструментами;
- MCP file access ограничен `PNP_LAB_WORKSPACE`;\n- во время release candidate CI обнаружил несовместимость со старым FastMCP import; код мигрирован на стабильный MCP Python SDK 2.x (`MCPServer`).\n
### Проверка качества

- CI расширен на Python 3.10/3.12/3.13;
- добавлен optional PySAT reference job;
- добавлен brute-force differential job;
- добавлен MCP install/build job;
- добавлены тесты XOR-эквивалентности и workspace isolation.

### Документация

- практическое применение;
- подробное описание representation switching;
- release notes;
- roadmap;
- обновлён README.

## 0.2.0 — 2026-09-22

- проект оформлен как воспроизводимая научная лаборатория;
- добавлен точный hybrid solver;
- decomposition, pure literals, UNSAT memoization, canonical keys;
- расширены метрики;
- added repeated experiments и CSV/JSON;
- добавлен empirical complexity fit;
- добавлен hard-case search;
- добавлен SQLite-реестр гипотез;
- добавлен optional PySAT reference;
- добавлен MCP server;
- расширена русская научная документация;
- добавлены тесты и CI matrix.

## 0.1.0 — 2026-09-22

- минимальный DPLL;
- DIMACS;
- генератор random 3-SAT;
- базовые тесты и документация.
