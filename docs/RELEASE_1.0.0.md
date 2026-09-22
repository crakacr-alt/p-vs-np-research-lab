# P vs NP Research Lab 1.0.0

Дата: 2026-09-23

## Тип релиза

Первый устойчивый **scientific core release**.

Это не заявление о решении P vs NP. Релиз означает, что проект теперь имеет
достаточную структуру для воспроизводимых исследований.

## Ключевое изменение

Впервые реализован настоящий exact representation switch:

```text
3-CNF XOR encoding -> XOREquation -> Gaussian elimination over GF(2)
```

То есть идея «если текущее представление неудобно — сменить математический язык»
теперь существует в коде, а не только в документации.

## Добавлено

- `RepresentationSwitchingSolver`;
- точное распознавание XOR3;
- Gaussian elimination over GF(2);
- XOR propagation и direct XOR solve;
- brute-force oracle;
- structured benchmarks;
- Pigeonhole benchmark;
- decomposition benchmark;
- XOR chain benchmark;
- inconsistent XOR core;
- benchmark CSV/JSON/Markdown report;
- `pnp-lab doctor`;
- `pnp-lab benchmark`;
- более строгая differential verification;
- безопасный `PNP_LAB_WORKSPACE` для MCP;
- MCP tools для benchmark и гипотез;
- новые тесты representation switching;
- расширенный CI.

## Проверка релиза

CI проверяет:

- Python 3.10;
- Python 3.12;
- Python 3.13;
- unit tests;
- doctor;
- structural benchmark;
- Ruff;
- optional PySAT reference;
- brute-force differential check;
- установку MCP и создание FastMCP server.

## Ограничение интерпретации

Даже если XOR benchmark решается без DPLL decisions, это только результат для
распознанной линейной структуры.

Никакого общего polynomial bound для 3-SAT из этого не следует.
