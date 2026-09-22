# Roadmap

## 1.0 — Scientific Core Release

Готовая база:

- exact solvers;
- reproducible experiments;
- structured benchmarks;
- brute-force / PySAT differential verification;
- CNF -> XOR representation switch;
- MCP research interface;
- hypothesis log.

## 1.1 — SAT research quality

План:

- подключение современного CDCL solver как полноценного benchmark backend;
- DRAT/LRAT proof certificates для UNSAT там, где backend их поддерживает;
- больше benchmark-семейств;
- автоматический regression benchmark между commit-ами;
- статистика распределения сложности, а не только среднее.

## 1.2 — Rich representation switching

План:

- XOR произвольной длины;
- unified component decomposition для CNF + XOR;
- graph representation;
- структурные признаки задачи;
- policy выбора следующего точного преобразования.

## 1.3 — Proof-complexity experiments

План:

- Tseitin formulas;
- pigeonhole scaling;
- crafted resolution-hard families;
- отдельные метрики размера доказательства;
- хранение контрпримеров как версионируемых артефактов.

## 2.0 — Multi-representation research engine

Цель:

- подключаемые exact representations;
- общий verifier переходов;
- автоматический поиск sequences of representation switches;
- adversarial generator против всей системы;
- AI orchestration через MCP без права самостоятельно объявлять доказательство.

## Отдельный теоретический трек

Для каждого promising результата:

1. сформулировать точное утверждение;
2. попытаться построить контрпример;
3. доказать более слабую версию;
4. сравнить с известными lower bounds;
5. только после этого усиливать формулировку.
