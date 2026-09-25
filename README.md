# P vs NP Research Lab

[![tests](https://github.com/crakacr-alt/p-vs-np-research-lab/actions/workflows/tests.yml/badge.svg)](https://github.com/crakacr-alt/p-vs-np-research-lab/actions/workflows/tests.yml)
[![CodeQL](https://github.com/crakacr-alt/p-vs-np-research-lab/actions/workflows/codeql.yml/badge.svg)](https://github.com/crakacr-alt/p-vs-np-research-lab/actions/workflows/codeql.yml)


**P vs NP Research Lab** — открытая научно-исследовательская лаборатория для
воспроизводимых экспериментов с SAT, точными алгоритмами, трудными экземплярами
и переключением математических представлений.

> **Релиз:** 1.1.3  
> **Научный статус:** проект не является доказательством `P = NP` или `P != NP`.

## Что эта схема даёт на практике уже сейчас

Главная идея проекта — не просто «перебирать быстрее», а проверять, может ли одна
и та же задача становиться проще после **точного перехода в другое представление**.

В 1.0 это уже не только идея. Реализован первый настоящий switch:

```text
3-CNF
  |
  | точное распознавание XOR-кодировки
  v
XOR equations
  |
  | Gaussian elimination над GF(2)
  v
SAT / UNSAT
```

Если формула содержит структуру, которая в CNF выглядит как несколько клауз, но
на самом деле является системой XOR-уравнений, solver может перестать ветвиться
по этим клаузам и решить линейную часть алгебраически.

Это **не решает P vs NP**, но даёт работающий экспериментальный ответ на важный
вопрос: «может ли смена представления реально убрать поисковые ветвления на
конкретном классе задач?» — да, и теперь это можно измерять.

Практически лаборатория уже полезна для шести задач:

1. **Сравнивать точные алгоритмы** на одинаковых входах и одинаковых seed.
2. **Находить слабые места** solver-а автоматическим hard-case search.
3. **Проверять новые идеи**, не доверяя только времени выполнения.
4. **Подключать AI через MCP**, чтобы модель сама запускала эксперименты и вела
   журнал гипотез.
5. **Собирать воспроизводимые данные** в CSV/JSON/Markdown вместо рассуждений
   «кажется, стало быстрее».
6. **Запускать формальную машину Тьюринга** и считать её шаги, состояние ленты
   и траекторию вычисления.

Подробнее: [Практическое применение](docs/PRACTICAL_USE.md).

## Что входит в 1.1

### Exact solvers

- `DPLLSolver` — простой baseline;
- `HybridSolver` — DPLL + propagation + union-find decomposition + memoization + Jeroslow–Wang branching;
- `RepresentationSwitchingSolver` — Hybrid-подход с точным переходом
  `CNF -> XOR -> GF(2)` и тем же взвешенным branching для оставшейся CNF.

### Проверка корректности

- независимая проверка SAT-модели;
- brute-force oracle для маленьких задач;
- differential tests между DPLL, Hybrid и Switching solver;
- optional проверка через внешний `python-sat`;
- структурные SAT/UNSAT benchmark-семейства.

### Научная инфраструктура

- random 3-SAT;
- planted 3-SAT;
- Pigeonhole Principle;
- независимые CNF-компоненты;
- XOR-chain;
- линейно противоречивый XOR-core;
- repeated experiments;
- CSV/JSON;
- Markdown benchmark report;
- polynomial/exponential empirical fit;
- SQLite-журнал гипотез;
- hard-case search;
- CI на нескольких версиях Python.

### Формальная модель вычисления

- рабочая детерминированная одно-ленточная машина Тьюринга;
- JSON-описание переходов;
- accept/reject;
- step limit;
- trace;
- CLI и MCP-запуск.

Пример:

```bash
pnp-lab tm examples/turing_even_ones.json 1010 --trace
```

Подробнее: [Машина Тьюринга](docs/TURING_MACHINE.md).

### MCP

AI-модель получает инструменты для:

- проверки состояния проекта;
- решения CNF;
- запуска growth experiment;
- запуска структурного benchmark;
- поиска трудного экземпляра;
- запуска машины Тьюринга;
- добавления и просмотра гипотез;
- изменения статусов гипотез.

Файловые MCP-операции ограничены `PNP_LAB_WORKSPACE`.

## Установка

### Linux / Ubuntu

```bash
git clone https://github.com/crakacr-alt/p-vs-np-research-lab.git
cd p-vs-np-research-lab

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
```

### Windows PowerShell

```powershell
git clone https://github.com/crakacr-alt/p-vs-np-research-lab.git
cd p-vs-np-research-lab

py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -e .
```

Проверка установки:

```bash
pnp-lab doctor
```

## Быстрый старт

Решить CNF:

```bash
pnp-lab solve examples/simple_sat.cnf
```

Явно выбрать solver:

```bash
pnp-lab solve examples/simple_sat.cnf --solver switch
```

Запустить структурный benchmark:

```bash
pnp-lab benchmark --output results/release
```

На выходе:

```text
results/release/benchmark.csv
results/release/benchmark.json
results/release/REPORT.md
```

Growth experiment:

```bash
pnp-lab experiment \
  --start 10 \
  --stop 50 \
  --step 5 \
  --repeats 10 \
  --solvers dpll,hybrid,switch \
  --output results/growth-001
```

Искать трудный случай:

```bash
pnp-lab hunt \
  --variables 30 \
  --clauses 126 \
  --iterations 1000 \
  --output results/hard-30.cnf
```

Differential verification:

```bash
pnp-lab verify \
  --variables 8 \
  --clauses 30 \
  --count 100 \
  --bruteforce
```

С внешним PySAT:

```bash
pip install -e ".[reference]"

pnp-lab verify \
  --variables 10 \
  --clauses 42 \
  --count 100 \
  --reference
```

## Эффективность поиска в 1.1.3

Внутренний порядок поиска улучшен без изменения точности:

- decomposition использует union-find вместо повторного обхода списков соседей;
- branching использует Jeroslow–Wang: литералы коротких клауз имеют больший вес;
- solver сначала пробует полярность с большим score;
- публичные solver IDs сохранены, чтобы не ломать benchmark/скрипты;
- benchmark теперь пишет `components_solved`, `max_depth`, unit/pure counters;
- property-based CI автоматически сверяет exact solver-ы с brute-force.

Контрольный прогон на 60 фиксированных random 3-SAT
(`28 variables / 118 clauses`) дал для Hybrid/Switch:

- decisions: `727 -> 548`;
- recursive calls: `8006 -> 5529`;
- по decisions: 45 случаев лучше, 9 хуже, 6 без изменения.

Это измерение конкретного набора, **не универсальная гарантия ускорения**.

Подробнее: [эвристика поиска](docs/SOLVER_HEURISTICS.md).

## Подключение к Vanya AI / другой модели через MCP

Установить MCP-дополнение:

```bash
pip install -e ".[mcp]"
```

Рекомендуется зафиксировать workspace:

```bash
export PNP_LAB_WORKSPACE=/полный/путь/к/p-vs-np-research-lab
```

Windows PowerShell:

```powershell
$env:PNP_LAB_WORKSPACE="C:\полный\путь\p-vs-np-research-lab"
```

Пример конфигурации MCP-клиента:

```json
{
  "mcpServers": {
    "pnp-lab": {
      "command": "/полный/путь/.venv/bin/python",
      "args": ["-m", "pnp_lab.mcp_server"],
      "env": {
        "PNP_LAB_WORKSPACE": "/полный/путь/к/p-vs-np-research-lab"
      }
    }
  }
}
```

Для Windows в `command` указывается:

```text
C:\...\p-vs-np-research-lab\.venv\Scripts\python.exe
```

Подробно: [MCP](docs/MCP.md).

## Архитектура 1.1

```text
                       DIMACS CNF
                           |
                +----------+----------+
                |                     |
              DPLL                 Hybrid
                |                     |
                +----------+----------+
                           |
                 Representation Switch
                           |
            +--------------+--------------+
            |                             |
        remaining CNF                detected XOR
            |                             |
       exact search                GF(2) elimination
            |                             |
            +--------------+--------------+
                           |
                     exact result
                           |
          +----------------+----------------+
          |                |                |
      verifier         metrics        benchmark/report
                                            |
                                      hypothesis log
                                            |
                                      MCP / AI agent
```

## Научная гипотеза

Рабочее направление называется **Polynomial Representation Switching**.

Сильная версия гипотезы требует доказать, что для любой 3-CNF можно эффективно
находить последовательность точных представлений так, чтобы общий размер
состояния и работа оставались polynomial.

Такого доказательства нет.

Релиз 1.0 проверяет более узкую и честную вещь: один конкретный переход
`CNF -> XOR` может быть обнаружен автоматически и использоваться без потери
точности.

## Документы

- [Практическое применение](docs/PRACTICAL_USE.md)
- [Representation Switching](docs/REPRESENTATION_SWITCHING.md)
- [Архитектура](docs/ARCHITECTURE.md)
- [Исследовательская идея](docs/RESEARCH_IDEA.md)
- [Научный метод](docs/SCIENTIFIC_METHOD.md)
- [Протокол экспериментов](docs/EXPERIMENT_PROTOCOL.md)
- [Ограничения](docs/LIMITATIONS.md)
- [Зависимости](docs/DEPENDENCIES.md)
- [MCP](docs/MCP.md)
- [Машина Тьюринга](docs/TURING_MACHINE.md)
- [Гайд по коду](docs/STUDENT_GUIDE.md)
- [Литература](docs/REFERENCES.md)
- [Roadmap](ROADMAP.md)
- [История изменений](CHANGELOG.md)
- [Безопасность](SECURITY.md)
- [Как внести вклад](CONTRIBUTING.md)
- [Лицензия MIT](LICENSE)
- `CITATION.cff` для цитирования конкретной версии проекта
- [Release notes 1.0](docs/RELEASE_1.0.0.md)
- [Release notes 1.1](docs/RELEASE_1.1.0.md)
- [Release notes 1.1.1](docs/RELEASE_1.1.1.md)
- [Release notes 1.1.2](docs/RELEASE_1.1.2.md)
- [Release notes 1.1.3](docs/RELEASE_1.1.3.md)
- [Solver heuristics](docs/SOLVER_HEURISTICS.md)
- [Release process](docs/RELEASE_PROCESS.md)

## Проверка

```bash
python -m unittest discover -s tests -v
pnp-lab doctor
pnp-lab benchmark --output results/release-check
```

Для полной проверки кода, включая property-based tests:

```bash
pip install -e ".[dev]"
python -m unittest discover -s property_tests -v
ruff check pnp_lab tests property_tests
```

## Как трактовать результаты

`0 decisions` на XOR benchmark означает, что конкретная XOR-часть была решена
алгебраически без DPLL-ветвления. Это важный экспериментальный эффект.

Но даже если все текущие benchmark-задачи решаются быстро, это ничего не говорит
о худшем случае для всех NP-полных задач.

**Практический успех solver-а и доказательство P=NP — разные уровни результата.**
