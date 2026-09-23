# P vs NP Research Lab 1.1.0

Дата: 2026-09-23

## Главное

Добавлена рабочая детерминированная одно-ленточная машина Тьюринга.

Она не заменяет SAT solver и не является способом ускорить NP-полные задачи.
Её роль — дать лаборатории классическую формальную модель вычисления.

## Добавлено

- `pnp_lab/turing_machine.py`;
- разреженная бесконечная лента;
- JSON loader;
- accept/reject;
- step limit;
- trace;
- пример `turing_even_ones.json`;
- команда `pnp-lab tm`;
- MCP tool `run_turing_machine`;
- self-test в `pnp-lab doctor`;
- отдельные unit-тесты;
- документация `docs/TURING_MACHINE.md`.

## Научная роль

Теперь проект разделяет два уровня:

```text
теория вычисления
    -> Turing Machine

экспериментальные exact algorithms
    -> DPLL / Hybrid / Representation Switching
```

Это полезно для исследования вычислительной сложности, но не является
доказательством P=NP или P!=NP.
