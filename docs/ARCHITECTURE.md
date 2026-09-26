# Архитектура проекта 1.2

## Основной принцип

Лаборатория разделена на независимые слои:

1. frontends;
2. programmable runtime;
3. exact/scientific engines;
4. verification;
5. experiments/provenance;
6. AI orchestration.

Верхний слой не имеет права объявлять результат более надёжным, чем позволяет
нижний verifier.

## Frontends

Пользователь может работать через LabScript, Python API, CLI, Jupyter,
Markdown/Obsidian и MCP/AI.

Ни один frontend не является источником истины.

## LabScript layer

Каталог pnp_lab/labscript.

language.py определяет RU/ENG mode и нормализует двуязычные keywords, не меняя
строки и комментарии.

runtime.py содержит собственный interpreter: разрешённый AST subset,
functions/loops/conditions/collections, local scopes, step limit,
source-located errors, local .lab modules и explicit host modules.
Произвольный Python exec не используется.

stdlib.py содержит portable standard library: math, crypto, SAT,
JSON/Base64/hash и базовые collection/string helpers.

package.py реализует .labpkg: dependency-aware source bundle,
deterministic ZIP metadata, language version, SHA-256 каждого файла и safe
extraction.

jupyter.py и markdown.py используют тот же LabRuntime. Отдельной реализации
языка для notebook или Obsidian нет.

## Exact solving

cnf.py хранит CNF, DIMACS и независимую проверку SAT model.

dpll.py — простой baseline exact solver.

hybrid.py использует propagation, pure literals, union-find decomposition,
UNSAT cache и Jeroslow-Wang branching.

switch_solver.py и xor.py реализуют точное representation switching
CNF -> XOR -> GF(2).

## Verification

bruteforce.py — независимый oracle для маленьких формул.

verification.py сравнивает DPLL, Hybrid, RepresentationSwitching, brute force и
optional PySAT. Property tests дополнительно генерируют случайные маленькие CNF.

## Formal computation model

turing_machine.py содержит отдельную deterministic single-tape Turing Machine.
Она не является ускорителем SAT, а служит формальной вычислительной моделью.

## Experiments

benchmarks.py, benchmark_runner.py, experiments.py, complexity.py и
hard_search.py дают reproducible inputs, logical metrics, CSV/JSON/Markdown,
complexity fits и adversarial hard-case search.

Benchmark не превращается автоматически в theorem/proof.

## Research provenance

research_db.py хранит гипотезы. Автоматического статуса PROVED нет.

## MCP

mcp_server.py даёт AI только научные инструменты.
workspace.py ограничивает файловый доступ PNP_LAB_WORKSPACE.

## Extension boundary

LabScript host modules и будущий engine registry — место для подключения:

- production SAT/CDCL;
- SMT;
- symbolic math;
- Lean;
- rigorous numerics;
- ODE/PDE;
- visualization;
- enterprise/private libraries.

Parser/runtime не должны напрямую зависеть от тяжёлых backends.

## Почему слои разделены

Это позволяет отдельно ответить:

- кто сформулировал задачу;
- какой engine её решал;
- как получен результат;
- кто его проверил;
- какой уровень доверия допустим;
- можно ли повторить эксперимент.

Для научного проекта это важнее, чем один большой black-box solver.
