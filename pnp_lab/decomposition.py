def split_into_independent_components(clauses: list[list[int]]) -> list[list[list[int]]]:
    """Делит CNF на независимые компоненты по общим переменным.

    Если две группы клауз не имеют общих переменных, их можно решать отдельно:

        F = F1 И F2

    где переменные F1 и F2 не пересекаются.

    Это точное преобразование: SAT(F) тогда и только тогда,
    когда SAT(F1) и SAT(F2).
    """

    if len(clauses) <= 1:
        return [clauses]

    variable_to_clauses: dict[int, list[int]] = {}

    for clause_index, clause in enumerate(clauses):
        for literal in clause:
            variable = abs(literal)
            variable_to_clauses.setdefault(variable, []).append(clause_index)

    visited = set()
    components = []

    for start in range(len(clauses)):
        if start in visited:
            continue

        stack = [start]
        visited.add(start)
        component_indexes = []

        while stack:
            clause_index = stack.pop()
            component_indexes.append(clause_index)

            for literal in clauses[clause_index]:
                variable = abs(literal)

                for neighbour in variable_to_clauses.get(variable, []):
                    if neighbour not in visited:
                        visited.add(neighbour)
                        stack.append(neighbour)

        components.append([clauses[index] for index in component_indexes])

    return components
