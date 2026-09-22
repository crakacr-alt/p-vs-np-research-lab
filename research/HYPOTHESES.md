# Реестр стартовых гипотез

Рабочие статусы можно вести в SQLite через `pnp-lab hypothesis ...`.

## H0001 — Independent component decomposition

**Статус:** TESTING

**Утверждение:** на CNF из независимых компонент decomposition уменьшает число
ветвлений относительно baseline DPLL.

## H0002 — UNSAT residual memoization

**Статус:** TESTING

**Утверждение:** memoization уменьшает повторный поиск на формулах с повторно
возникающими остаточными состояниями.

## H0003 — Polynomial Representation Switching

**Статус:** IDEA

**Сильная формулировка:** для любой 3-CNF существует эффективно находимая
последовательность точных представлений, сохраняющая polynomial-size state и
polynomial total work.

Это чрезвычайно сильная гипотеза. Релиз 1.0 её не доказывает.

## H0004 — Exact XOR switching

**Статус:** TESTING

**Утверждение:** на CNF с точно распознаваемыми XOR3-блоками переход в GF(2)
снижает количество DPLL decisions без изменения SAT/UNSAT результата.

**Проверка:**

- XOR-chain;
- inconsistent XOR core;
- exhaustive equivalence test на одном XOR3;
- differential comparison с baseline.

**Что может опровергнуть полезность:** overhead распознавания и elimination может
оказаться больше выигрыша на маленьких или смешанных формулах. Поэтому нужно
смотреть и logical metrics, и wall-clock time.
