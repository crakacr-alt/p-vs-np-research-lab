import tempfile
import unittest
from pathlib import Path

from pnp_lab.turing_machine import (
    Transition,
    TuringMachine,
    load_turing_machine,
)


EXAMPLE = (
    Path(__file__).resolve().parents[1]
    / "examples"
    / "turing_even_ones.json"
)


class TestTuringMachine(unittest.TestCase):
    def test_example_accepts_even_number_of_ones(self):
        machine = load_turing_machine(EXAMPLE)
        result = machine.run("1010")

        self.assertEqual(result.status, "ACCEPT")
        self.assertTrue(result.accepted)
        self.assertEqual(result.steps, 5)

    def test_example_rejects_odd_number_of_ones(self):
        machine = load_turing_machine(EXAMPLE)
        result = machine.run("1011")

        self.assertEqual(result.status, "REJECT")
        self.assertFalse(result.accepted)

    def test_empty_input_is_even(self):
        machine = load_turing_machine(EXAMPLE)
        result = machine.run("")

        self.assertEqual(result.status, "ACCEPT")

    def test_head_can_move_left_of_zero(self):
        machine = TuringMachine(
            name="left-test",
            states={"q0", "q1", "qa"},
            input_alphabet={"1"},
            tape_alphabet={"1", "X", "_"},
            blank="_",
            start_state="q0",
            accept_states={"qa"},
            reject_states=set(),
            transitions={
                ("q0", "1"): Transition("1", "L", "q1"),
                ("q1", "_"): Transition("X", "S", "qa"),
            },
        )

        result = machine.run("1")

        self.assertEqual(result.status, "ACCEPT")
        self.assertEqual(result.head, -1)
        self.assertEqual(result.tape_start, -1)
        self.assertEqual(result.tape, "X1")

    def test_step_limit_stops_infinite_loop(self):
        machine = TuringMachine(
            name="loop",
            states={"q"},
            input_alphabet=set(),
            tape_alphabet={"_"},
            blank="_",
            start_state="q",
            accept_states=set(),
            reject_states=set(),
            transitions={
                ("q", "_"): Transition("_", "S", "q"),
            },
        )

        result = machine.run("", max_steps=7)

        self.assertEqual(result.status, "STEP_LIMIT")
        self.assertFalse(result.halted)
        self.assertEqual(result.steps, 7)

    def test_trace_contains_snapshots(self):
        machine = load_turing_machine(EXAMPLE)
        result = machine.run("11", trace=True)

        self.assertGreaterEqual(len(result.trace), 1)
        self.assertEqual(result.trace[0].step, 0)
        self.assertEqual(result.trace[0].state, "q_even")

    def test_invalid_input_symbol_is_rejected_before_run(self):
        machine = load_turing_machine(EXAMPLE)

        with self.assertRaises(ValueError):
            machine.run("102")

    def test_duplicate_transition_in_json_is_invalid(self):
        payload = """{
          "name": "bad",
          "states": ["q0", "qa"],
          "input_alphabet": ["1"],
          "tape_alphabet": ["1", "_"],
          "blank": "_",
          "start_state": "q0",
          "accept_states": ["qa"],
          "reject_states": [],
          "transitions": [
            {"state": "q0", "read": "1", "write": "1", "move": "R", "next": "qa"},
            {"state": "q0", "read": "1", "write": "1", "move": "S", "next": "qa"}
          ]
        }"""

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text(payload, encoding="utf-8")

            with self.assertRaises(ValueError):
                load_turing_machine(path)


if __name__ == "__main__":
    unittest.main()
