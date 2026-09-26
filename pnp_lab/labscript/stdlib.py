import base64
import hashlib
import json
import math
from dataclasses import dataclass

from ..cnf import CNFProblem
from ..dpll import DPLLSolver
from ..hybrid import HybridSolver
from ..switch_solver import RepresentationSwitchingSolver


@dataclass(frozen=True)
class ModuleNamespace:
    name: str
    values: dict

    def get(self, name):
        if name.startswith("_") or name not in self.values:
            raise AttributeError(f"module {self.name!r} has no public name {name!r}")
        return self.values[name]


def _stable_text(value) -> str:
    if isinstance(value, (dict, list, tuple, bool, int, float)) or value is None:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return str(value)


def hash_value(value, algorithm="sha256"):
    data = _stable_text(value).encode("utf-8")
    try:
        digest = hashlib.new(str(algorithm).lower())
    except ValueError as error:
        raise ValueError(f"unknown hash algorithm: {algorithm}") from error
    digest.update(data)
    return digest.hexdigest()


def encode64(value):
    return base64.b64encode(_stable_text(value).encode("utf-8")).decode("ascii")


def decode64(value):
    try:
        return base64.b64decode(str(value), validate=True).decode("utf-8")
    except Exception as error:
        raise ValueError("invalid base64 input") from error


def solve_sat(variables, clauses, solver="switch"):
    problem = CNFProblem(
        variables=int(variables),
        clauses=tuple(tuple(int(literal) for literal in clause) for clause in clauses),
    )
    problem.validate()

    solvers = {
        "dpll": DPLLSolver,
        "hybrid": HybridSolver,
        "switch": RepresentationSwitchingSolver,
    }
    if solver not in solvers:
        raise ValueError("solver must be dpll, hybrid, or switch")

    result = solvers[solver]().solve(problem)
    return result.to_dict()


def assert_true(value, message="assertion failed"):
    if not value:
        raise AssertionError(str(message))
    return True


def append(value, item):
    value.append(item)
    return value


def upper(value):
    return str(value).upper()


def lower(value):
    return str(value).lower()


def split(value, separator=None):
    return str(value).split(separator)


def join(separator, values):
    return str(separator).join(str(item) for item in values)


def json_encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def json_decode(value):
    return json.loads(str(value))


def type_name(value):
    names = {
        bool: "bool",
        int: "int",
        float: "float",
        str: "text",
        list: "list",
        tuple: "tuple",
        dict: "map",
        type(None): "null",
    }
    return names.get(type(value), type(value).__name__)


MATH_MODULE = ModuleNamespace(
    "math",
    {
        "pi": math.pi,
        "e": math.e,
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "floor": math.floor,
        "ceil": math.ceil,
        "factorial": math.factorial,
        "gcd": math.gcd,
    },
)

CRYPTO_MODULE = ModuleNamespace(
    "crypto",
    {
        "hash": hash_value,
        "encode64": encode64,
        "decode64": decode64,
    },
)

SAT_MODULE = ModuleNamespace(
    "sat",
    {
        "solve": solve_sat,
    },
)


def default_builtins(output):
    def lab_print(*values, sep=" ", end="\n"):
        output.write(sep.join(str(value) for value in values) + end)
        return None

    return {
        "print": lab_print,
        "length": len,
        "len": len,
        "range": range,
        "sum": sum,
        "min": min,
        "max": max,
        "abs": abs,
        "round": round,
        "sorted": sorted,
        "enumerate": enumerate,
        "zip": zip,
        "int": int,
        "float": float,
        "text": str,
        "str": str,
        "bool": bool,
        "list": list,
        "tuple": tuple,
        "map": dict,
        "dict": dict,
        "hash": hash_value,
        "encode64": encode64,
        "decode64": decode64,
        "solve_sat": solve_sat,
        "assert_true": assert_true,
        "type_name": type_name,
        "append": append,
        "upper": upper,
        "lower": lower,
        "split": split,
        "join": join,
        "json_encode": json_encode,
        "json_decode": json_decode,
    }


BUILTIN_MODULES = {
    "math": MATH_MODULE,
    "crypto": CRYPTO_MODULE,
    "sat": SAT_MODULE,
}
