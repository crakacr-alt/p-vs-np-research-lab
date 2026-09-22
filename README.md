# P vs NP Research Lab

**P vs NP Research Lab** — открытый научно-исследовательский проект для воспроизводимых экспериментов с SAT, точными алгоритмами поиска, поиском трудных экземпляров и гипотезой о переключении представлений задачи.

> **Статус:** исследовательская лаборатория, а не доказательство `P = NP` и не доказательство `P != NP`.

## Научная цель

Центральный вопрос проекта:

> можно ли так комбинировать точные представления и преобразования NP-полных задач, чтобы размер промежуточного состояния и число необходимых шагов для любого входа оставались полиномиальными?

Рабочая гипотеза называется **Polynomial Representation Switching** — «полиномиальное переключение представлений».

Для доказательства `P = NP` недостаточно получить быстрые результаты на миллионах тестов. Нужен алгоритм с доказанной полиномиальной верхней границей для **всех** входов. Поэтому проект разделяет:

- инженерное ускорение;
- экспериментальное наблюдение;
- математическую гипотезу;
- доказанный результат.

Эти уровни нельзя смешивать.

## Что реализовано в v0.2

- точный baseline solver DPLL;
- точный hybrid solver;
- unit propagation;
- pure literal elimination;
- разбиение CNF на независимые компоненты;
- memoization доказанных UNSAT-состояний;
- канонический ключ остаточной CNF;
- генератор random 3-SAT;
- генератор planted 3-SAT с известной моделью;
- поиск трудных экземпляров через простой hill climbing;
- воспроизводимые серии экспериментов с несколькими `seed`;
- сохранение сырых данных в CSV и параметров в JSON;
- эмпирическое сравнение polynomial/exponential fit;
- SQLite-журнал исследовательских гипотез;
- независимая проверка SAT-моделей;
- optional reference solver через `python-sat`;
- MCP server для подключения лаборатории к модели/агенту;
- тесты и GitHub Actions.

## Быстрая установка

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

Проверка:

```bash
pnp-lab --help
```

## Примеры

Решить SAT:

```bash
pnp-lab solve examples/simple_sat.cnf
```

Сравнить простой DPLL и hybrid solver:

```bash
pnp-lab experiment --start 10 --stop 40 --step 5 --repeats 5
```

Результаты сохраняются в:

```text
results/latest/results.csv
results/latest/metadata.json
```

Искать трудный экземпляр:

```bash
pnp-lab hunt --variables 30 --clauses 126 --iterations 500
```

Проверить согласованность двух собственных solver-ов:

```bash
pnp-lab verify --variables 12 --clauses 50 --count 200
```

А с независимым PySAT:

```bash
pip install -e ".[reference]"
pnp-lab verify --variables 12 --clauses 50 --count 200 --reference
```

Создать гипотезу:

```bash
pnp-lab hypothesis add \
  --title "H1: decomposition" \
  --statement "Разбиение независимых компонент уменьшает число ветвлений на декомпозируемых формулах"
```

Посмотреть журнал:

```bash
pnp-lab hypothesis list
```

## MCP: подключить к модели за несколько минут

Установить MCP-дополнение:

```bash
pip install -e ".[mcp]"
```

Проверить сервер:

```bash
pnp-lab-mcp
```

В конфигурацию любого MCP-совместимого клиента добавить примерно:

```json
{
  "mcpServers": {
    "pnp-lab": {
      "command": "python",
      "args": ["-m", "pnp_lab.mcp_server"]
    }
  }
}
```

После подключения модель получает инструменты:

- `project_status`;
- `solve_cnf_file`;
- `growth_experiment`;
- `hunt_hard_case`.

Подробно: [docs/MCP.md](docs/MCP.md).

## Архитектура

```text
                 DIMACS CNF
                     |
          +----------+----------+
          |                     |
     DPLL baseline          Hybrid exact
                                |
                +---------------+----------------+
                |               |                |
          propagation      decomposition      memoization
                |               |                |
                +---------------+----------------+
                                |
                         exact SAT/UNSAT
                                |
              +-----------------+------------------+
              |                                    |
       model verification                 research metrics
                                                   |
                        +--------------------------+-----------------+
                        |                          |                 |
                  CSV/JSON runs              hard search      hypotheses DB
```

Подробно: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Сторонние библиотеки

В проекте разрешено использовать любые библиотеки, если они помогают исследованию. Но каждая зависимость должна быть объяснена: **что делает, зачем нужна и можно ли без неё**.

Сейчас core работает без сторонних runtime-зависимостей. Дополнения:

- `mcp` — только для подключения к AI/агентам;
- `python-sat` — только для независимой сверки с промышленным solver;
- `ruff` — только для разработки и CI.

Подробно: [docs/DEPENDENCIES.md](docs/DEPENDENCIES.md).

## Научная дисциплина проекта

Каждый эксперимент должен иметь:

1. точную гипотезу;
2. параметры генерации;
3. seed;
4. версию solver-а;
5. сырые результаты;
6. способ проверки корректности;
7. попытку найти контрпример;
8. явное разделение «наблюдение» и «доказательство».

См. [docs/SCIENTIFIC_METHOD.md](docs/SCIENTIFIC_METHOD.md) и [docs/EXPERIMENT_PROTOCOL.md](docs/EXPERIMENT_PROTOCOL.md).

## Основные документы

- [Исследовательская гипотеза](docs/RESEARCH_IDEA.md)
- [Архитектура](docs/ARCHITECTURE.md)
- [Научный метод](docs/SCIENTIFIC_METHOD.md)
- [Протокол экспериментов](docs/EXPERIMENT_PROTOCOL.md)
- [Ограничения](docs/LIMITATIONS.md)
- [Зависимости](docs/DEPENDENCIES.md)
- [MCP-интеграция](docs/MCP.md)
- [Гайд по коду](docs/STUDENT_GUIDE.md)
- [Литература](docs/REFERENCES.md)
- [Реестр гипотез](research/HYPOTHESES.md)

## Проверка

```bash
python -m unittest discover -s tests -v
```

Для проверки стиля:

```bash
pip install -e ".[dev]"
ruff check pnp_lab tests
```

## Что будет считаться серьёзным результатом

Сильный практический результат: новый точный SAT-метод, который воспроизводимо сокращает поиск на важных семействах задач.

Сильный теоретический результат: доказанная граница для нового класса формул или доказанное свойство переключения представлений.

Решение `P vs NP`: только строгий доказанный общий результат, прошедший независимую математическую проверку.
