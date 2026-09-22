from dataclasses import dataclass
from math import exp, log


@dataclass
class FitResult:
    model: str
    score_r2: float
    parameter: float
    coefficient: float


def _linear_regression(xs, ys):
    """Простая линейная регрессия y = a + b*x без сторонних библиотек."""

    if len(xs) != len(ys) or len(xs) < 2:
        raise ValueError("Для регрессии нужно минимум две точки")

    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)

    denominator = sum((x - x_mean) ** 2 for x in xs)

    if denominator == 0:
        raise ValueError("Все значения x одинаковы")

    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denominator
    intercept = y_mean - slope * x_mean

    predictions = [intercept + slope * x for x in xs]
    ss_res = sum((y - predicted) ** 2 for y, predicted in zip(ys, predictions))
    ss_tot = sum((y - y_mean) ** 2 for y in ys)
    r2 = 1.0 if ss_tot == 0 else 1.0 - ss_res / ss_tot

    return intercept, slope, r2


def fit_polynomial(ns, costs) -> FitResult:
    """Подгоняет модель cost ~= C * n^k."""

    clean = [(n, cost) for n, cost in zip(ns, costs) if n > 0 and cost > 0]

    if len(clean) < 2:
        raise ValueError("Недостаточно положительных точек для polynomial fit")

    xs = [log(n) for n, _ in clean]
    ys = [log(cost) for _, cost in clean]
    intercept, degree, r2 = _linear_regression(xs, ys)

    return FitResult(
        model="polynomial: C*n^k",
        score_r2=r2,
        parameter=degree,
        coefficient=exp(intercept),
    )


def fit_exponential(ns, costs) -> FitResult:
    """Подгоняет модель cost ~= C * a^n."""

    clean = [(n, cost) for n, cost in zip(ns, costs) if cost > 0]

    if len(clean) < 2:
        raise ValueError("Недостаточно положительных точек для exponential fit")

    xs = [float(n) for n, _ in clean]
    ys = [log(cost) for _, cost in clean]
    intercept, log_base, r2 = _linear_regression(xs, ys)

    return FitResult(
        model="exponential: C*a^n",
        score_r2=r2,
        parameter=exp(log_base),
        coefficient=exp(intercept),
    )
