def choose_jw_branch(clauses, extra_variable_groups=()):
    """Выбирает переменную по Jeroslow-Wang.

    Короткая клауза сильнее ограничивает поиск, поэтому её литералы получают
    больший вес: 2^(-длина клаузы). Для XOR-групп знак неизвестен, поэтому вес
    делится поровну между True и False.

    Эвристика меняет только порядок поиска. SAT/UNSAT ответ от неё не зависит.
    """

    positive: dict[int, float] = {}
    negative: dict[int, float] = {}

    for clause in clauses:
        if not clause:
            continue

        weight = 2.0 ** (-len(clause))

        for literal in clause:
            variable = abs(literal)

            if literal > 0:
                positive[variable] = positive.get(variable, 0.0) + weight
            else:
                negative[variable] = negative.get(variable, 0.0) + weight

    for group in extra_variable_groups:
        if not group:
            continue

        # XOR не даёт естественной предпочтительной полярности.
        # Добавляем одинаковый вес обеим сторонам.
        weight = (2.0 ** (-len(group))) / 2.0

        for variable in group:
            positive[variable] = positive.get(variable, 0.0) + weight
            negative[variable] = negative.get(variable, 0.0) + weight

    variables = set(positive) | set(negative)

    if not variables:
        raise ValueError("Нельзя выбрать переменную из пустого набора ограничений")

    def score(variable):
        return positive.get(variable, 0.0) + negative.get(variable, 0.0)

    # При равном score выбираем меньший номер. Это делает эксперименты
    # воспроизводимыми между запусками.
    variable = max(variables, key=lambda item: (score(item), -item))
    preferred_value = positive.get(variable, 0.0) >= negative.get(variable, 0.0)

    return variable, preferred_value
