"""Простой и точный интерпретатор детерминированной машины Тьюринга.

Модуль специально не пытается быть "быстрым эмулятором".
Его задача — дать проекту прозрачную формальную модель вычисления, где можно
считать шаги, положение головки и содержимое ленты.
"""

from dataclasses import asdict, dataclass
import json
from pathlib import Path


MOVE_LEFT = "L"
MOVE_RIGHT = "R"
MOVE_STAY = "S"
ALLOWED_MOVES = {MOVE_LEFT, MOVE_RIGHT, MOVE_STAY}


@dataclass(frozen=True)
class Transition:
    """Один переход машины Тьюринга."""

    write: str
    move: str
    next_state: str


@dataclass(frozen=True)
class TuringSnapshot:
    """Небольшой снимок выполнения для trace."""

    step: int
    state: str
    head: int
    read: str
    window_start: int
    window: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TuringRunResult:
    """Результат одного запуска."""

    machine: str
    status: str
    accepted: bool | None
    halted: bool
    steps: int
    final_state: str
    head: int
    tape_start: int
    tape: str
    trace: list[TuringSnapshot]

    def to_dict(self) -> dict:
        return {
            "machine": self.machine,
            "status": self.status,
            "accepted": self.accepted,
            "halted": self.halted,
            "steps": self.steps,
            "final_state": self.final_state,
            "head": self.head,
            "tape_start": self.tape_start,
            "tape": self.tape,
            "trace": [item.to_dict() for item in self.trace],
        }


@dataclass
class TuringMachine:
    """Детерминированная одно-ленточная машина Тьюринга."""

    name: str
    states: set[str]
    input_alphabet: set[str]
    tape_alphabet: set[str]
    blank: str
    start_state: str
    accept_states: set[str]
    reject_states: set[str]
    transitions: dict[tuple[str, str], Transition]
    description: str = ""

    def validate(self):
        """Проверяет внутреннюю согласованность описания машины."""

        if not self.states:
            raise ValueError("У машины должен быть хотя бы один state")

        if self.start_state not in self.states:
            raise ValueError("start_state отсутствует в states")

        if self.blank not in self.tape_alphabet:
            raise ValueError("blank должен входить в tape_alphabet")

        if self.blank in self.input_alphabet:
            raise ValueError("blank не должен входить в input_alphabet")

        if not self.input_alphabet.issubset(self.tape_alphabet):
            raise ValueError("input_alphabet должен быть подмножеством tape_alphabet")

        if not self.accept_states.issubset(self.states):
            raise ValueError("accept_states должны входить в states")

        if not self.reject_states.issubset(self.states):
            raise ValueError("reject_states должны входить в states")

        if self.accept_states & self.reject_states:
            raise ValueError("accept_states и reject_states не должны пересекаться")

        halting = self.accept_states | self.reject_states

        for (state, read), transition in self.transitions.items():
            if state not in self.states:
                raise ValueError(f"Неизвестное состояние перехода: {state}")

            if state in halting:
                raise ValueError(f"Из halting state {state} переходы не нужны")

            if read not in self.tape_alphabet:
                raise ValueError(f"Неизвестный символ чтения: {read}")

            if transition.write not in self.tape_alphabet:
                raise ValueError(f"Неизвестный символ записи: {transition.write}")

            if transition.move not in ALLOWED_MOVES:
                raise ValueError("move должен быть L, R или S")

            if transition.next_state not in self.states:
                raise ValueError(
                    f"Неизвестное следующее состояние: {transition.next_state}"
                )

    def run(
        self,
        input_text: str,
        max_steps: int = 10_000,
        trace: bool = False,
        trace_radius: int = 8,
    ) -> TuringRunResult:
        """Запускает машину на строке.

        Лента хранится как dict только для непустых ячеек. Поэтому индекс головки
        может уходить и в отрицательную область — это имитирует бесконечную в обе
        стороны ленту без выделения огромного массива.
        """

        self.validate()

        if max_steps < 0:
            raise ValueError("max_steps не может быть отрицательным")

        unknown = set(input_text) - self.input_alphabet

        if unknown:
            raise ValueError(
                "Во входе есть символы вне input_alphabet: "
                + ", ".join(sorted(unknown))
            )

        tape = {
            index: symbol
            for index, symbol in enumerate(input_text)
            if symbol != self.blank
        }

        state = self.start_state
        head = 0
        steps = 0
        history = []

        while True:
            read = tape.get(head, self.blank)

            if trace:
                history.append(
                    self._snapshot(
                        tape=tape,
                        state=state,
                        head=head,
                        step=steps,
                        radius=trace_radius,
                    )
                )

            if state in self.accept_states:
                return self._result(
                    "ACCEPT", True, True, steps, state, head, tape, history
                )

            if state in self.reject_states:
                return self._result(
                    "REJECT", False, True, steps, state, head, tape, history
                )

            if steps >= max_steps:
                return self._result(
                    "STEP_LIMIT", None, False, steps, state, head, tape, history
                )

            transition = self.transitions.get((state, read))

            if transition is None:
                return self._result(
                    "HALT_NO_TRANSITION",
                    None,
                    True,
                    steps,
                    state,
                    head,
                    tape,
                    history,
                )

            if transition.write == self.blank:
                tape.pop(head, None)
            else:
                tape[head] = transition.write

            if transition.move == MOVE_LEFT:
                head -= 1
            elif transition.move == MOVE_RIGHT:
                head += 1

            state = transition.next_state
            steps += 1

    def _snapshot(self, tape, state, head, step, radius):
        start = head - radius
        end = head + radius
        window = "".join(
            tape.get(index, self.blank)
            for index in range(start, end + 1)
        )

        return TuringSnapshot(
            step=step,
            state=state,
            head=head,
            read=tape.get(head, self.blank),
            window_start=start,
            window=window,
        )

    def _result(
        self,
        status,
        accepted,
        halted,
        steps,
        state,
        head,
        tape,
        history,
    ):
        positions = set(tape)
        positions.update({0, head})

        start = min(positions)
        end = max(positions)

        content = "".join(
            tape.get(index, self.blank)
            for index in range(start, end + 1)
        )

        return TuringRunResult(
            machine=self.name,
            status=status,
            accepted=accepted,
            halted=halted,
            steps=steps,
            final_state=state,
            head=head,
            tape_start=start,
            tape=content,
            trace=history,
        )


def machine_from_dict(data: dict) -> TuringMachine:
    """Создаёт машину из обычного Python dict."""

    transitions = {}

    for item in data.get("transitions", []):
        key = (item["state"], item["read"])

        if key in transitions:
            raise ValueError(
                "Детерминированная машина не может иметь два перехода "
                f"для {key}"
            )

        transitions[key] = Transition(
            write=item["write"],
            move=item["move"],
            next_state=item["next"],
        )

    machine = TuringMachine(
        name=data.get("name", "unnamed-machine"),
        description=data.get("description", ""),
        states=set(data["states"]),
        input_alphabet=set(data["input_alphabet"]),
        tape_alphabet=set(data["tape_alphabet"]),
        blank=data["blank"],
        start_state=data["start_state"],
        accept_states=set(data.get("accept_states", [])),
        reject_states=set(data.get("reject_states", [])),
        transitions=transitions,
    )
    machine.validate()
    return machine


def load_turing_machine(path: str | Path) -> TuringMachine:
    """Загружает описание машины из JSON-файла."""

    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return machine_from_dict(data)
