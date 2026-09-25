# Changelog

Все заметные изменения проекта фиксируются здесь.

## 1.1.2 — 2026-09-25

### Research quality

- добавлен CodeQL для Python;
- добавлен Dependabot для Python dependencies и GitHub Actions;
- добавлены CODEOWNERS, PR template и correctness bug template;
- release checklist сделан универсальным для следующих версий;
- добавлен автоматический GitHub Release workflow для wheel/sdist;
- tag перед публикацией сверяется с package version;
- package CI дополнительно запускает `pip check`;
- CI переведён на актуальные official GitHub Actions;
- исправлен артефакт форматирования в README.

### Научный статус

- solver-алгоритмы в 1.1.2 не менялись;
- версия не заявляет нового результата по P vs NP.

## 1.1.1 — 2026-09-25

### Проверка корректности

- добавлены независимые сертификаты для перехода CNF -> XOR3;
- сертификат проверяется полной таблицей истинности и не использует тот же detector;
- добавлены property-based tests через Hypothesis;
- добавлена exhaustive-проверка всех 256 подмножеств 3-литеральных клауз на трёх переменных;
- дополнительно прогнано 2400 случайных маленьких CNF против полного перебора без расхождений;
- тест версии теперь явно различает установленный пакет и запуск прямо из исходников.

### Инфраструктура

- CI работает с минимальными read-only permissions;
- Ruff проверяет основной код, unit-тесты и property-тесты;
- добавлена MIT License и ссылки на CONTRIBUTING/CITATION в README.

### Научный статус

- эти проверки повышают доверие к реализации, но не являются доказательством P=NP или P!=NP.

## 1.1.0 — 2026-09-23

### Машина Тьюринга

- добавлен рабочий детерминированный одно-ленточный Turing Machine interpreter;
- лента бесконечна в обе стороны и хранится разреженно;
- поддержаны `L/R/S`, accept/reject, step limit и trace;
- добавлена загрузка машин из JSON;
- добавлен пример проверки чётности числа единиц;
- добавлена CLI-команда `pnp-lab tm`;
- добавлен MCP-инструмент `run_turing_machine`;
- машина включена в `pnp-lab doctor`;
- добавлены отдельные unit-тесты и документация.

### Научная роль

- Turing Machine добавлена как формальная эталонная модель вычисления;
- она не используется как искусственный «ускоритель» SAT;
- число шагов можно измерять экспериментально, но конечные измерения не доказывают asymptotic worst-case.

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
- MCP file access ограничен `PNP_LAB_WORKSPACE`;
- во время release candidate CI обнаружил несовместимость со старым FastMCP import; код мигрирован на стабильный MCP Python SDK 2.x (`MCPServer`).

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
