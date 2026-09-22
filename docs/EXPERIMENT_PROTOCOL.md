# Протокол экспериментов

## Базовый эксперимент роста

Пример:

\`\`\`bash
pnp-lab experiment \
  --start 10 \
  --stop 60 \
  --step 5 \
  --repeats 20 \
  --ratio 4.2 \
  --seed 100 \
  --solvers dpll,hybrid \
  --output results/run-001
\`\`\`

## Почему \`repeats\` важен

Одна random 3-SAT формула при данном n может случайно оказаться простой или трудной. Серия повторов снижает риск сделать вывод по одному необычному экземпляру.

## Что сохраняется

\`results.csv\` — строка на каждый solver и каждый вход.

\`metadata.json\` — параметры запуска, Python/platform и время создания набора.

## Что сравнивать

Первично:

- decisions;
- calls.

Вторично:

- seconds.

Внутренние механизмы hybrid:

- unit_propagations;
- pure_literal_assignments;
- cache_hits;
- decompositions;
- max_depth.

## Hard-case search

\`\`\`bash
pnp-lab hunt \
  --variables 40 \
  --clauses 168 \
  --iterations 2000 \
  --seed 123 \
  --output results/hard-40.cnf
\`\`\`

Этот режим оптимизирует трудность **для конкретной текущей реализации**. Поэтому найденный экземпляр может быть лёгким для другого solver-а.

## Независимая сверка

\`\`\`bash
pnp-lab verify --variables 12 --clauses 50 --count 200
\`\`\`

Для внешнего reference:

\`\`\`bash
pip install -e ".[reference]"
pnp-lab verify --variables 12 --clauses 50 --count 200 --reference
\`\`\`

Важное правило: отсутствие несовпадений на конечной выборке — хороший инженерный тест, но не доказательство корректности на всех входах.
