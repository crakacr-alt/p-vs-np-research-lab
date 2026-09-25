def split_into_independent_components(clauses: list[list[int]]) -> list[list[list[int]]]:
    """Делит CNF на независимые компоненты по общим переменным.

    Используется union-find: для каждой переменной достаточно связать текущую
    клаузу с первой клаузой, где эта переменная уже встречалась. Это избегает
    повторных проходов по длинным спискам соседей.

    Преобразование точное:

        F = F1 И F2 И ...

    Если компоненты не делят переменные, их можно решать отдельно.
    """

    if len(clauses) <= 1:
        return [clauses]

    parent = list(range(len(clauses)))
    rank = [0] * len(clauses)

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(first, second):
        root_first = find(first)
        root_second = find(second)

        if root_first == root_second:
            return

        if rank[root_first] < rank[root_second]:
            root_first, root_second = root_second, root_first

        parent[root_second] = root_first

        if rank[root_first] == rank[root_second]:
            rank[root_first] += 1

    first_clause_for_variable: dict[int, int] = {}

    for clause_index, clause in enumerate(clauses):
        for literal in clause:
            variable = abs(literal)

            if variable in first_clause_for_variable:
                union(clause_index, first_clause_for_variable[variable])
            else:
                first_clause_for_variable[variable] = clause_index

    grouped: dict[int, list[list[int]]] = {}

    for clause_index, clause in enumerate(clauses):
        root = find(clause_index)
        grouped.setdefault(root, []).append(clause)

    return list(grouped.values())
