from dataclasses import asdict, dataclass


@dataclass
class SolverMetrics:
    """Счётчики, которые помогают сравнивать алгоритмы.

    Время само по себе шумное: оно зависит от компьютера и нагрузки.
    Поэтому отдельно считаются логические операции поиска.
    """

    decisions: int = 0
    calls: int = 0
    unit_propagations: int = 0
    pure_literal_assignments: int = 0
    cache_hits: int = 0
    decompositions: int = 0
    max_depth: int = 0
    seconds: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SolveResult:
    sat: bool
    model: dict[int, bool]
    solver: str
    metrics: SolverMetrics

    def to_dict(self) -> dict:
        return {
            "sat": self.sat,
            "model": {str(key): value for key, value in sorted(self.model.items())},
            "solver": self.solver,
            "metrics": self.metrics.to_dict(),
        }
