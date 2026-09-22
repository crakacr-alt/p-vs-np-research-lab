# MCP: подключение к модели или агенту

MCP — **Model Context Protocol**. Он позволяет модели не только читать текст проекта, но и вызывать разрешённые инструменты как функции.

## 1. Установка

В уже созданном virtual environment:

```bash
pip install -e ".[mcp]"
```

## 2. Ручная проверка

```bash
pnp-lab-mcp
```

Сервер работает через стандартный транспорт MCP, используемый клиентом.

## 3. Конфигурация клиента

Общий пример для MCP-клиента:

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

Если клиент запускается не из активированного virtual environment, лучше указать полный путь к Python из `.venv`.

Linux:

```json
{
  "mcpServers": {
    "pnp-lab": {
      "command": "/path/to/p-vs-np-research-lab/.venv/bin/python",
      "args": ["-m", "pnp_lab.mcp_server"]
    }
  }
}
```

Windows:

```json
{
  "mcpServers": {
    "pnp-lab": {
      "command": "C:\\path\\p-vs-np-research-lab\\.venv\\Scripts\\python.exe",
      "args": ["-m", "pnp_lab.mcp_server"]
    }
  }
}
```

## 4. Что получает модель

### `project_status`

Кратко сообщает версию и научный статус проекта.

### `solve_cnf_file(path)`

Решает локальный DIMACS CNF точным hybrid solver.

### `growth_experiment(...)`

Запускает небольшой эксперимент роста и отдаёт сырые результаты + empirical fit.

### `hunt_hard_case(...)`

Ищет трудный случай для текущего solver-а.

## 5. Для Vanya AI

Если Vanya AI поддерживает стандартный MCP `stdio`, добавь сервер в его список MCP-серверов тем же объектом конфигурации.

Минимальная логика интеграции:

```text
Vanya AI
   |
   | MCP stdio
   v
python -m pnp_lab.mcp_server
   |
   +--> solve_cnf_file
   +--> growth_experiment
   +--> hunt_hard_case
```

Конкретное имя файла конфигурации зависит от версии и оболочки Vanya AI. Важно не путь к конфигу, а две вещи:

- command = Python из окружения проекта;
- args = `-m pnp_lab.mcp_server`.

## 6. Правило безопасности научных выводов

MCP специально не содержит инструмента `prove_p_equals_np`.

Модель может запускать вычислительные эксперименты, но вывод «P = NP доказано» не должен появляться только из результата программы.

Если появится proof candidate, его нужно сохранять как отдельный математический артефакт и проверять независимо.
