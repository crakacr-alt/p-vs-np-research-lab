# P vs NP Research Lab

**P vs NP Research Lab** — открытая научно-исследовательская лаборатория для
воспроизводимых экспериментов с SAT, точными алгоритмами, трудными экземплярами
и переключением математических представлений.

> **Релиз:** 1.0.0  
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

Практически лаборатория уже полезна для пяти задач:

1. **Сравнивать точные алгоритмы** на одинаковых входах и одинаковых seed.
2. **Находить слабые места** solver-а автоматическим hard-case search.
3. **Проверять новые идеи**, не доверяя только времени выполнения.
4. **Подключать AI через MCP**, чтобы модель сама запускала эксперименты и вела
   журнал гипотез.
5. **Собирать воспроизводимые данные** в CSV/JSON/Markdown вместо рассуждений
   «кажется, стало быстрее».

Подробнее: [Практическое применение](docs/PRACTICAL_USE.md).

## Что входит в 1.0

### Exact solvers

- `DPLLSolver` — простой baseline;
- `HybridSolver` — DPLL + propagation + decomposition + memoization;
- `RepresentationSwitchingSolver` — Hybrid-подход с точным переходом
  `CNF -> XOR -> GF(2)`.

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

### MCP

AI-модель получает инструменты для:

- проверки состояния проекта;
- решения CNF;
- запуска growth experiment;
- запуска структурного benchmark;
- поиска трудного экземпляра;
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

## Архитектура 1.0

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
- [Гайд по коду](docs/STUDENT_GUIDE.md)
- [Литература](docs/REFERENCES.md)
- [Roadmap](ROADMAP.md)
- [История изменений](CHANGELOG.md)
- [Release notes 1.0](docs/RELEASE_1.0.0.md)

## Проверка

```bash
python -m unittest discover -s tests -v
pnp-lab doctor
pnp-lab benchmark --output results/release-check
```

Для проверки кода:

```bash
pip install -e ".[dev]"
ruff check pnp_lab tests
```

## Как трактовать результаты

`0 decisions` на XOR benchmark означает, что конкретная XOR-часть была решена
алгебраически без DPLL-ветвления. Это важный экспериментальный эффект.

Но даже если все текущие benchmark-задачи решаются быстро, это ничего не говорит
о худшем случае для всех NP-полных задач.

**Практический успех solver-а и доказательство P=NP — разные уровни результата.**
