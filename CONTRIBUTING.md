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
