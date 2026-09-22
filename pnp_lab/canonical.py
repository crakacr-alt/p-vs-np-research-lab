def canonical_formula(clauses: list[list[int]] | tuple[tuple[int, ...], ...]) -> tuple:
    """Возвращает стабильный ключ для остаточной CNF-формулы.

    Клаузы и литералы сортируются, поэтому одинаковые формулы,
    пришедшие к нам в разном порядке, получают один ключ.

    Важно: переменные НЕ переименовываются. Это простая и безопасная
    канонизация, а не сложная проверка изоморфизма формул.
    """

    normalized = []

    for clause in clauses:
        normalized.append(tuple(sorted(clause)))

    return tuple(sorted(normalized))
