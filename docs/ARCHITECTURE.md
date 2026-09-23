# Архитектура проекта 1.1

## Основной принцип

Проект разделён на четыре слоя:

1. exact solving;
2. representation switching;
3. scientific experiments;
4. AI/MCP orchestration.

Ни один верхний слой не должен подменять корректность нижнего.

## Exact solving

### `cnf.py`

- структура CNF;
- DIMACS import/export;
- независимая проверка SAT model.

### `dpll.py`

Простой baseline.

### `hybrid.py`

Точный solver с:

- unit propagation;
- pure literal elimination;
- independent component decomposition;
- UNSAT memoization;
- DPLL branching.

### `bruteforce.py`

Медленный независимый oracle для маленьких задач.

## Representation layer

### `xor.py`

- распознаёт точную XOR3-кодировку в CNF;
- хранит `XOREquation`;
- выполняет Gaussian elimination над GF(2);
- выводит XOR unit assignments;
- строит одно решение линейной системы.

### `switch_solver.py`

Связывает CNF и XOR.

```text
original CNF
    |
detect XOR3
    |
    +--> remaining CNF ----+
    |                      |
    +--> XOR equations ----+
                           |
                      shared model
                           |
                SAT / UNSAT + metrics
```

Это первый working representation switch проекта.

## Computational model layer

### `turing_machine.py`

Отдельная формальная модель вычисления:

- deterministic single-tape Turing Machine;
- разреженная лента с отрицательными и положительными индексами;
- JSON transition table;
- accept/reject;
- step limit;
- trace.

Этот слой не является частью SAT solver-а. Он нужен для связи экспериментов с
классической теорией вычислимости и сложности.

## Benchmark layer

### `benchmarks.py`

Структурные семейства:

- random 3-SAT;
- Pigeonhole Principle;
- independent components;
- XOR chains;
- inconsistent XOR core.

### `benchmark_runner.py`

Одинаковые задачи прогоняются через несколько solver-ов.

Сохраняются:

- CSV;
- JSON;
- Markdown report.

### `experiments.py`

Growth experiment по размеру random 3-SAT.

### `complexity.py`

Empirical fit:

- `C*n^k`;
- `C*a^n`.

Fit не считается доказательством асимптотики.

### `hard_search.py`

Adversarial search против текущего solver-а.

## Verification layer

### `verification.py`

Сравнивает:

- DPLL;
- Hybrid;
- RepresentationSwitchingSolver;
- brute force, если включён;
- PySAT, если установлен.

## Research layer

### `research_db.py`

SQLite-журнал гипотез.

Нет автоматического статуса `PROVED`.

## MCP layer

### `mcp_server.py`

AI получает ограниченный набор научных инструментов.

### `workspace.py`

Файлы MCP разрешены только внутри `PNP_LAB_WORKSPACE`.

Это важно, потому что исследовательскому агенту не нужен произвольный доступ к
остальной файловой системе.

## Почему не всё сделано одним solver-ом

Для исследования важно видеть, какое улучшение что меняет.

Если сразу использовать огромный black-box solver, трудно понять причину
ускорения.

Поэтому baseline, hybrid и switch существуют отдельно.
