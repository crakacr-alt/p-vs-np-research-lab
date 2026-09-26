# Как вносить изменения

## Новая идея

1. Записать проверяемую гипотезу.
2. Указать baseline.
3. Реализовать изменение отдельно и понятно.
4. Добавить correctness test.
5. Добавить benchmark, где эффект должен проявляться.
6. Запустить differential verification.
7. Попытаться найти hard case.
8. Обновить CHANGELOG.

## Новое representation

Нужно обязательно показать:

- точное условие распознавания;
- почему преобразование сохраняет множество решений;
- тест эквивалентности;
- fallback, если условие распознавания не выполнено;
- метрику, по которой оценивается польза switch.

## Новая зависимость

Обновить `docs/DEPENDENCIES.md`:

- что библиотека делает;
- зачем нужна;
- где используется;
- можно ли работать без неё.

## Сильное научное утверждение

Экспериментальные данные нельзя называть доказательством.

Допустимые формулировки:

- observed;
- measured;
- survived tested instances;
- proof candidate.

## Перед pull request

```bash
python -m unittest discover -s tests -v
pnp-lab doctor
pnp-lab benchmark --output results/pre-pr
ruff check pnp_lab tests
```


## Изменения LabScript

Язык — публичный интерфейс. Изменение parser/runtime нельзя делать только ради
одного красивого примера.

Для нового синтаксиса или builtin:

1. показать одинаковое поведение RU/EN, если конструкция языковая;
2. добавить unit test;
3. проверить строки/комментарии, чтобы translator их не менял;
4. не открывать arbitrary Python import/attribute access;
5. не ломать старые .lab examples;
6. обновить LABSCRIPT_RU.md и LABSCRIPT_EN.md;
7. заметное изменение записать в CHANGELOG.

Для package format дополнительно нужны reproducibility и malformed-package tests.

Для host-модуля нужно явно описать, какие capabilities он открывает программе.

## Новая научная engine-интеграция

Lean/SMT/symbolic/PDE backend должен подключаться через явную engine/host-module
границу, а не импортироваться из parser/runtime.

Нужно указать:

- тип задач;
- формат входа/выхода;
- уровень доверия результата;
- independent verifier/certificate, если он существует;
- optional dependency;
- reproducible test/benchmark.
