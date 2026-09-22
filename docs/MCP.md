# MCP: подключение лаборатории к AI-модели

MCP — **Model Context Protocol**. Проект использует стабильную ветку Python SDK 2.x.\n
Он позволяет модели вызывать функции лаборатории вместо того, чтобы только
рассуждать о ней текстом.

## Установка

```bash
pip install -e ".[mcp]"\n# устанавливается mcp>=2,<3
```

Проверка Python-части:

```bash
pnp-lab doctor
```

Проверка запуска MCP:

```bash
pnp-lab-mcp
```

## Workspace

Для MCP рекомендуется явно указать рабочий каталог:

Linux:

```bash
export PNP_LAB_WORKSPACE=/home/user/p-vs-np-research-lab
```

Windows PowerShell:

```powershell
$env:PNP_LAB_WORKSPACE="C:\Projects\p-vs-np-research-lab"
```

MCP не разрешает файловые операции за пределами этого каталога.

## Конфигурация клиента

Общий пример:

```json
{
  "mcpServers": {
    "pnp-lab": {
      "command": "/home/user/p-vs-np-research-lab/.venv/bin/python",
      "args": ["-m", "pnp_lab.mcp_server"],
      "env": {
        "PNP_LAB_WORKSPACE": "/home/user/p-vs-np-research-lab"
      }
    }
  }
}
```

Windows command:

```text
C:\Projects\p-vs-np-research-lab\.venv\Scripts\python.exe
```

## Инструменты 1.0

### `project_status`

Версия, основной solver, реализованный switch и научный статус.

### `doctor`

Быстрая самопроверка.

### `solve_cnf_file(path)`

Точное решение DIMACS CNF внутри workspace.

### `growth_experiment(...)`

Repeated random 3-SAT experiment.

### `run_structural_benchmark(...)`

Структурный benchmark с сохранением CSV/JSON/Markdown.

### `hunt_hard_case(...)`

Adversarial search и сохранение найденного CNF.

### `add_hypothesis(...)`

Добавить гипотезу со статусом `IDEA`.

### `list_hypotheses(...)`

Прочитать журнал.

### `set_hypothesis_status(...)`

Изменить статус в разрешённом наборе.

## Для Vanya AI

Если Vanya AI понимает MCP stdio, нужен тот же command/args.

Схема:

```text
Vanya AI
   |
   | MCP stdio
   v
pnp_lab.mcp_server
   |
   +--> exact solve
   +--> experiments
   +--> benchmarks
   +--> hard-case search
   +--> hypothesis memory
```

## Рекомендуемый research loop для модели

```text
1. list_hypotheses
2. выбрать TESTING/IDEA
3. сформулировать проверяемый эксперимент
4. run_structural_benchmark или growth_experiment
5. hunt_hard_case
6. сравнить результаты
7. изменить статус гипотезы
8. предложить следующий эксперимент
```

## Чего MCP не умеет намеренно

Нет инструмента:

```text
prove_p_equals_np()
```

Результат эксперимента не должен автоматически превращаться в математическое
доказательство.
