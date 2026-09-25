# Release 1.1.3 — solver efficiency

Версия 1.1.3 улучшает порядок exact-поиска, не меняя математический ответ.

## Изменения

- Jeroslow–Wang branching в Hybrid и RepresentationSwitching solver;
- сначала проверяется более сильная по score полярность;
- decomposition переписан на union-find;
- добавлена метрика `components_solved`;
- benchmark показывает components и max depth;
- solver IDs оставлены прежними для обратной совместимости.

## Проверка

- unit tests на branching heuristic;
- дополнительные decomposition tests;
- все существующие exact/XOR/brute-force tests;
- сравнение SAT/UNSAT старой и новой реализации на одинаковых random inputs.

На контрольной выборке 60 random 3-SAT:

```text
decisions: 727 -> 548
calls:     8006 -> 5529
```

Это не гарантирует такой же выигрыш на других распределениях задач.
