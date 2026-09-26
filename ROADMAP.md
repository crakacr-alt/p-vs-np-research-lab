# Roadmap

## 1.0 — Scientific Core

Готово:

- exact SAT solvers;
- reproducible experiments;
- brute-force / PySAT verification;
- CNF -> XOR representation switching;
- benchmark/report pipeline;
- MCP research interface;
- hypothesis log.

## 1.1 — Solver quality + formal computation model

Готово:

- Jeroslow–Wang branching;
- union-find decomposition;
- property-based equivalence tests;
- expanded solver metrics;
- deterministic one-tape Turing Machine;
- CI / CodeQL / release discipline.

## 1.2 — LabScript + human-facing platform

Готово:

- LabScript 0.1;
- RU/EN syntax;
- Unicode identifiers;
- functions, loops, conditions, collections;
- local modules;
- explicit host-module API;
- math / crypto / SAT modules;
- JSON, Base64, hashing;
- check/run/debug/build/verify CLI;
- deterministic .labpkg;
- package SHA-256 verification;
- Jupyter magic;
- Markdown / Obsidian runner;
- Windows/Linux/macOS language CI.

Следующий patch-track 1.2.x:

- interactive debugger with breakpoints/watch expressions;
- formatter and linter;
- richer diagnostics with machine-readable JSON;
- package signing;
- dependency manifest;
- dedicated Obsidian plugin;
- native Jupyter kernel;
- controlled file/network capability modules;
- Android compatibility test harness.

## 1.3 — Scientific engine layer

План:

- единый Problem / Result API;
- engine registry;
- CaDiCaL/PySAT production SAT backend;
- Z3-class SMT backend;
- SymPy symbolic backend;
- exact transformation certificates;
- arbitrary-length XOR;
- unified CNF + XOR component decomposition;
- graph/problem-structure features;
- automatic solver/representation policy.

## 1.4 — Formal proof + rigorous numerics

План:

- Lean 4 + mathlib bridge;
- proof-obligation generation;
- import/export theorem artifacts;
- DRAT/LRAT proof verification;
- interval/ball arithmetic backend;
- explicit uncertainty/error bounds;
- result confidence levels:
  CONJECTURE -> NUMERICAL -> CROSS_CHECKED -> RIGOROUS -> CERTIFIED -> FORMAL.

AI может предлагать доказательства, но не может самостоятельно повышать статус до FORMAL.

## 1.5 — Numerical science and visualization

План:

- NumPy/SciPy-class local numerical backend;
- ODE workflows;
- PDE plugin interface;
- PETSc/FEniCSx-class scalable backends;
- convergence/residual/energy analysis;
- reproducible scientific plots;
- CSV/JSON/Parquet-style datasets;
- experiment comparison dashboards.

Первый domain module после общей инфраструктуры:

- Navier–Stokes experiments:
  numerical simulation,
  convergence,
  residuals,
  energy checks,
  rigorous bounds where possible,
  proof obligations for Lean.

Численная симуляция сама по себе не считается доказательством глобального
существования/гладкости.

## 1.6 — LabScript tooling and portable runtime

План:

- stable language specification 1.0;
- package registry format;
- signed packages;
- language server protocol;
- autocomplete/hover/diagnostics;
- native Obsidian plugin;
- native Jupyter kernel;
- portable bytecode;
- WASM runtime;
- browser and Android host;
- capability-based file/network/process APIs;
- reproducible build metadata.

Исходный .lab syntax должен остаться совместимым между Python и WASM runtime.

## 1.7 — Autonomous research workflows

План:

- experiment scheduler;
- counterexample hunter as a first-class service;
- adversarial generator against every solver/transform;
- automatic regression corpus;
- distributed experiment workers;
- result provenance;
- reproducibility bundles;
- AI orchestration with verifier-enforced trust boundaries.

## 2.0 — Verifiable Computational Research Lab

Цель:

- один простой frontend для человека, Jupyter, Obsidian и AI;
- несколько независимых computation/proof engines;
- machine-checkable provenance;
- exact + symbolic + numerical + formal methods;
- воспроизводимые отчёты и графики;
- расширяемый LabScript;
- возможность решать практические тяжёлые задачи без заявления неподтверждённых
  математических «прорывов».

## Теоретический трек P vs NP

Он не исчезает за общей платформой.

Для каждого promising результата:

1. сформулировать точное утверждение;
2. построить независимый verifier;
3. искать контрпример;
4. сравнить с известными baseline/lower-bound результатами;
5. получить certificate/proof там, где это возможно;
6. только после этого усиливать формулировку.

Representation switching остаётся отдельным основным исследовательским направлением.
