# Зависимости

## Core + LabScript

Основная лаборатория 1.2 и LabScript 0.1 используют только стандартную библиотеку
Python.

Это сознательное решение:

- обычная установка остаётся маленькой;
- LabScript можно запускать на Windows/Linux/macOS без научного HPC-стека;
- Android/Python-host не должен тянуть лишние бинарные пакеты;
- SAT core остаётся легко проверять;
- дополнительные научные engines подключаются явно.

Это не запрет на библиотеки. Тяжёлая зависимость добавляется тогда, когда она
решает конкретную задачу.

## mcp

Установка:

```bash
pip install -e ".[mcp]"
```

Зависимость: mcp>=2,<3.

Нужна только для Model Context Protocol и AI-клиентов.
Без неё SAT, LabScript, CLI, package build и Markdown integration работают.

## reference

Установка:

```bash
pip install -e ".[reference]"
```

Зависимость: python-sat.

Это независимый SAT reference backend для differential verification.
Основные solver-ы от него не зависят.

## jupyter

Установка:

```bash
pip install -e ".[jupyter]"
```

Зависимость: IPython>=8.

Нужна для %lab / %%lab magic.
Сам LabScript runtime IPython не требует.

## dev

Установка:

```bash
pip install -e ".[dev]"
```

Содержит:

- Ruff — статическая проверка;
- Hypothesis — property-based correctness tests.

## release

Установка:

```bash
pip install -e ".[release]"
```

Содержит build и twine для wheel/sdist проверки.

## Будущие engine extras

Планируется не один огромный набор зависимостей, а отдельные extras/плагины.

Примерное разделение:

- symbolic — SymPy-class backend;
- smt — Z3-class backend;
- sat-production — CaDiCaL/PySAT adapters;
- formal — Lean bridge/tooling;
- rigorous — interval/ball arithmetic;
- numerical — NumPy/SciPy-class stack;
- pde — PETSc/FEniCSx-class stack;
- plots — scientific plotting/report stack.

Человек, которому нужен только LabScript или SAT, не должен устанавливать PDE
или theorem prover.

## Правило добавления зависимости

В PR нужно указать:

1. какую проблему она решает;
2. является ли runtime dependency или optional extra;
3. размер/платформенные ограничения;
4. можно ли продолжать работать без неё;
5. independent test/benchmark;
6. как она влияет на воспроизводимость результатов.

Зависимость не добавляется «для солидности».
