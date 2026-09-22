# Журнал экспериментов

## Формат записи

Для каждого значимого эксперимента фиксировать:

- ID;
- дата;
- commit SHA;
- гипотеза;
- команда запуска;
- hardware/OS при важности времени;
- сырые данные;
- наблюдение;
- интерпретация;
- попытка опровержения;
- следующий шаг.

## E0001

Статус: TEMPLATE

Команда:

```bash
pnp-lab experiment --start 10 --stop 40 --step 5 --repeats 10 --seed 1
```

Результат пока не заполнен. Этот шаблон специально не содержит выдуманных чисел.


## E0002 — Release benchmark 1.0.0

**Дата:** 2026-09-23  
**Commit:** `3868d686bde1998311abbf7dbb3556989adbb2fc`  
**Среда:** GitHub Actions, Ubuntu, Python 3.12  
**Команда:** `pnp-lab benchmark --output /tmp/pnp-release-benchmark`

### Результаты

| Case | Solver | SAT | Decisions | Calls | XOR eq | Switches | Seconds |
|---|---|---:|---:|---:|---:|---:|---:|
| random-3sat-20 | DPLL | True | 9 | 49 | 0 | 0 | 0.000434 |
| random-3sat-20 | Hybrid | True | 9 | 50 | 0 | 0 | 0.001430 |
| random-3sat-20 | Switch | True | 9 | 50 | 0 | 0 | 0.001476 |
| independent-8 | DPLL | True | 16 | 17 | 0 | 0 | 0.000113 |
| independent-8 | Hybrid | True | 8 | 25 | 0 | 0 | 0.000164 |
| independent-8 | Switch | True | 8 | 25 | 0 | 0 | 0.000229 |
| php-4-3 | DPLL | False | 5 | 53 | 0 | 0 | 0.000145 |
| php-4-3 | Hybrid | False | 5 | 49 | 0 | 0 | 0.000313 |
| php-4-3 | Switch | False | 5 | 49 | 0 | 0 | 0.000374 |
| xor-chain-8 | DPLL | True | 4 | 20 | 0 | 0 | 0.000096 |
| xor-chain-8 | Hybrid | True | 4 | 20 | 0 | 0 | 0.000275 |
| xor-chain-8 | Switch | True | 0 | 1 | 8 | 1 | 0.000119 |
| xor-inconsistent-core | DPLL | False | 7 | 39 | 0 | 0 | 0.000082 |
| xor-inconsistent-core | Hybrid | False | 7 | 28 | 0 | 0 | 0.000232 |
| xor-inconsistent-core | Switch | False | 0 | 1 | 4 | 1 | 0.000041 |

### Наблюдение

На двух XOR-family задачах representation switch полностью убрал DPLL decisions:
`4 -> 0` для SAT XOR-chain и `7 -> 0` для UNSAT XOR-core.

На random 3-SAT и Pigeonhole переключение не сработало, потому что подходящей
XOR3-структуры не было. Там Switch ведёт себя близко к Hybrid и имеет небольшой
overhead распознавания.

На independent-components семейство decomposition уменьшило decisions
`16 -> 8`.

### Интерпретация

E0002 подтверждает только узкую гипотезу H0004 на текущих тестах:
точно распознанная XOR-структура действительно может быть решена без
DPLL-ветвления.

Это **не** подтверждает сильную H0003 про polynomial representation switching
для произвольного 3-SAT.

### Попытка опровержения

В release suite специально присутствуют семейства без XOR-структуры. На них
Switch не показывает алгоритмического преимущества и иногда работает немного
медленнее из-за overhead. Это ожидаемое ограничение текущего метода.

### Следующий шаг

Увеличивать XOR benchmark, добавлять mixed CNF+XOR и искать случаи, где стоимость
распознавания/линейной алгебры превышает выигрыш по ветвлениям.
