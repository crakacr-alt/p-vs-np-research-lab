import ast
import io
import operator
import os
from dataclasses import dataclass, field
from pathlib import Path

from .language import translate_source
from .stdlib import BUILTIN_MODULES, ModuleNamespace, default_builtins


class LabScriptError(RuntimeError):
    pass


class LabScriptSyntaxError(LabScriptError):
    pass


class StepLimitError(LabScriptError):
    pass


class _ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class _BreakSignal(Exception):
    pass


class _ContinueSignal(Exception):
    pass


@dataclass
class Environment:
    values: dict = field(default_factory=dict)
    parent: "Environment | None" = None

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise LabScriptError(f"unknown name: {name}")

    def set(self, name, value):
        self.values[name] = value

    def assign(self, name, value):
        # Assignment is local to the current scope. Functions can read outer
        # values, but do not silently overwrite them.
        self.values[name] = value


@dataclass
class UserFunction:
    name: str
    args: list[str]
    body: list[ast.stmt]
    closure: Environment
    runtime: "LabRuntime"

    def __call__(self, *values):
        if len(values) != len(self.args):
            raise LabScriptError(
                f"{self.name} expects {len(self.args)} arguments, got {len(values)}"
            )

        local = Environment(parent=self.closure)
        for name, value in zip(self.args, values):
            local.set(name, value)

        try:
            self.runtime._exec_block(self.body, local)
        except _ReturnSignal as signal:
            return signal.value
        return None


_ALLOWED_AST = (
    ast.Module,
    ast.Expr,
    ast.Assign,
    ast.AugAssign,
    ast.Name,
    ast.Constant,
    ast.BinOp,
    ast.UnaryOp,
    ast.BoolOp,
    ast.Compare,
    ast.If,
    ast.While,
    ast.For,
    ast.FunctionDef,
    ast.Return,
    ast.Break,
    ast.Continue,
    ast.Pass,
    ast.List,
    ast.Tuple,
    ast.Dict,
    ast.Subscript,
    ast.Slice,
    ast.Call,
    ast.Import,
    ast.ImportFrom,
    ast.Attribute,
    ast.keyword,
    ast.alias,
    ast.arguments,
    ast.arg,
    ast.Load,
    ast.Store,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
    ast.BitXor,
    ast.BitAnd,
    ast.BitOr,
    ast.USub,
    ast.UAdd,
    ast.Not,
    ast.And,
    ast.Or,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.In,
    ast.NotIn,
)

_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.BitXor: operator.xor,
    ast.BitAnd: operator.and_,
    ast.BitOr: operator.or_,
}

_COMPARE = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.In: lambda left, right: left in right,
    ast.NotIn: lambda left, right: left not in right,
}


def parse_source(source: str, filename="<labscript>"):
    language, translated = translate_source(source)

    try:
        tree = ast.parse(translated, filename=filename, mode="exec")
    except SyntaxError as error:
        raise LabScriptSyntaxError(
            f"{filename}:{error.lineno}:{error.offset}: {error.msg}"
        ) from error

    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_AST):
            raise LabScriptSyntaxError(
                f"{filename}:{getattr(node, 'lineno', '?')}: "
                f"unsupported syntax: {type(node).__name__}"
            )

        if isinstance(node, ast.FunctionDef):
            if node.decorator_list or node.returns is not None:
                raise LabScriptSyntaxError(
                    f"{filename}:{node.lineno}: decorators/type returns are not supported"
                )
            if node.args.defaults or node.args.kw_defaults:
                raise LabScriptSyntaxError(
                    f"{filename}:{node.lineno}: default arguments are not supported yet"
                )
            if node.args.vararg or node.args.kwarg or node.args.kwonlyargs:
                raise LabScriptSyntaxError(
                    f"{filename}:{node.lineno}: variadic functions are not supported yet"
                )

    return language, translated, tree


class LabRuntime:
    """Small cross-platform interpreter for LabScript."""

    def __init__(
        self,
        *,
        output=None,
        max_steps=1_000_000,
        module_paths=None,
        modules=None,
        trace=None,
    ):
        self.output = output if output is not None else io.StringIO()
        self.max_steps = int(max_steps)
        self.steps = 0
        self.trace = trace
        self.module_paths = [Path(path).resolve() for path in (module_paths or [])]
        self.module_cache = {}
        self.modules = dict(BUILTIN_MODULES)
        if modules:
            self.modules.update(modules)
        self.globals = Environment()
        self.globals.values.update(default_builtins(self.output))
        self.globals.values.update(self.modules)

    def execute(self, source: str, *, filename="<labscript>", env=None):
        _, _, tree = parse_source(source, filename)
        target = env or self.globals
        self._exec_block(tree.body, target)
        return target

    def execute_file(self, path):
        path = Path(path).resolve()
        source = path.read_text(encoding="utf-8")
        old_paths = list(self.module_paths)

        if path.parent not in self.module_paths:
            self.module_paths.insert(0, path.parent)

        try:
            return self.execute(source, filename=str(path))
        finally:
            self.module_paths = old_paths

    def output_text(self):
        getter = getattr(self.output, "getvalue", None)
        return getter() if getter else ""

    def _tick(self, node, env):
        self.steps += 1
        if self.steps > self.max_steps:
            raise StepLimitError(
                f"step limit {self.max_steps} exceeded; possible infinite loop"
            )

        if self.trace is not None:
            snapshot = {
                key: value
                for key, value in env.values.items()
                if not callable(value) and not isinstance(value, ModuleNamespace)
            }
            self.trace(
                {
                    "line": getattr(node, "lineno", None),
                    "node": type(node).__name__,
                    "steps": self.steps,
                    "locals": snapshot,
                }
            )

    def _exec_block(self, statements, env):
        for statement in statements:
            self._exec_statement(statement, env)

    def _exec_statement(self, node, env):
        self._tick(node, env)

        if isinstance(node, ast.Expr):
            value = self._eval(node.value, env)
            env.set("_", value)
            return value

        if isinstance(node, ast.Assign):
            if len(node.targets) != 1:
                raise LabScriptError("multiple assignment targets are not supported")
            value = self._eval(node.value, env)
            self._assign_target(node.targets[0], value, env)
            return None

        if isinstance(node, ast.AugAssign):
            current = self._eval(node.target, env)
            value = self._eval(node.value, env)
            operation = _BINOPS.get(type(node.op))
            if operation is None:
                raise LabScriptError(
                    f"unsupported augmented operator: {type(node.op).__name__}"
                )
            self._assign_target(node.target, operation(current, value), env)
            return None

        if isinstance(node, ast.If):
            branch = node.body if self._truthy(self._eval(node.test, env)) else node.orelse
            self._exec_block(branch, env)
            return None

        if isinstance(node, ast.While):
            while self._truthy(self._eval(node.test, env)):
                try:
                    self._exec_block(node.body, env)
                except _ContinueSignal:
                    continue
                except _BreakSignal:
                    break
            return None

        if isinstance(node, ast.For):
            iterable = self._eval(node.iter, env)
            for item in iterable:
                self._assign_target(node.target, item, env)
                try:
                    self._exec_block(node.body, env)
                except _ContinueSignal:
                    continue
                except _BreakSignal:
                    break
            return None

        if isinstance(node, ast.FunctionDef):
            arguments = [arg.arg for arg in node.args.args]
            env.set(
                node.name,
                UserFunction(
                    name=node.name,
                    args=arguments,
                    body=node.body,
                    closure=env,
                    runtime=self,
                ),
            )
            return None

        if isinstance(node, ast.Return):
            value = self._eval(node.value, env) if node.value is not None else None
            raise _ReturnSignal(value)

        if isinstance(node, ast.Break):
            raise _BreakSignal()

        if isinstance(node, ast.Continue):
            raise _ContinueSignal()

        if isinstance(node, ast.Pass):
            return None

        if isinstance(node, ast.Import):
            for alias in node.names:
                module = self._load_module(alias.name)
                env.set(alias.asname or alias.name, module)
            return None

        if isinstance(node, ast.ImportFrom):
            module = self._load_module(node.module or "")
            for alias in node.names:
                if alias.name == "*":
                    for name, value in module.values.items():
                        if not name.startswith("_"):
                            env.set(name, value)
                    continue
                env.set(alias.asname or alias.name, module.get(alias.name))
            return None

        raise LabScriptError(f"unsupported statement: {type(node).__name__}")

    def _eval(self, node, env):
        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.Name):
            return env.get(node.id)

        if isinstance(node, ast.List):
            return [self._eval(item, env) for item in node.elts]

        if isinstance(node, ast.Tuple):
            return tuple(self._eval(item, env) for item in node.elts)

        if isinstance(node, ast.Dict):
            return {
                self._eval(key, env): self._eval(value, env)
                for key, value in zip(node.keys, node.values)
            }

        if isinstance(node, ast.BinOp):
            operation = _BINOPS.get(type(node.op))
            if operation is None:
                raise LabScriptError(
                    f"unsupported binary operator: {type(node.op).__name__}"
                )
            return operation(self._eval(node.left, env), self._eval(node.right, env))

        if isinstance(node, ast.UnaryOp):
            value = self._eval(node.operand, env)
            if isinstance(node.op, ast.USub):
                return -value
            if isinstance(node.op, ast.UAdd):
                return +value
            if isinstance(node.op, ast.Not):
                return not self._truthy(value)
            raise LabScriptError(
                f"unsupported unary operator: {type(node.op).__name__}"
            )

        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                result = True
                for item in node.values:
                    result = self._eval(item, env)
                    if not self._truthy(result):
                        return result
                return result

            result = False
            for item in node.values:
                result = self._eval(item, env)
                if self._truthy(result):
                    return result
            return result

        if isinstance(node, ast.Compare):
            left = self._eval(node.left, env)
            for operation_node, comparator in zip(node.ops, node.comparators):
                right = self._eval(comparator, env)
                operation = _COMPARE.get(type(operation_node))
                if operation is None:
                    raise LabScriptError(
                        f"unsupported comparison: {type(operation_node).__name__}"
                    )
                if not operation(left, right):
                    return False
                left = right
            return True

        if isinstance(node, ast.Subscript):
            value = self._eval(node.value, env)
            index = self._eval_slice(node.slice, env)
            return value[index]

        if isinstance(node, ast.Attribute):
            owner = self._eval(node.value, env)
            if isinstance(owner, ModuleNamespace):
                return owner.get(node.attr)
            raise LabScriptError(
                "attributes are allowed only on LabScript modules"
            )

        if isinstance(node, ast.Call):
            function = self._eval(node.func, env)
            if not callable(function):
                raise LabScriptError("attempted to call a non-function value")

            args = [self._eval(arg, env) for arg in node.args]
            kwargs = {
                keyword.arg: self._eval(keyword.value, env)
                for keyword in node.keywords
                if keyword.arg is not None
            }
            if len(kwargs) != len(node.keywords):
                raise LabScriptError("**kwargs are not supported")
            return function(*args, **kwargs)

        raise LabScriptError(f"unsupported expression: {type(node).__name__}")

    def _eval_slice(self, node, env):
        if isinstance(node, ast.Slice):
            lower = self._eval(node.lower, env) if node.lower is not None else None
            upper = self._eval(node.upper, env) if node.upper is not None else None
            step = self._eval(node.step, env) if node.step is not None else None
            return slice(lower, upper, step)
        return self._eval(node, env)

    def _assign_target(self, target, value, env):
        if isinstance(target, ast.Name):
            env.assign(target.id, value)
            return

        if isinstance(target, ast.Subscript):
            container = self._eval(target.value, env)
            index = self._eval_slice(target.slice, env)
            container[index] = value
            return

        raise LabScriptError("assignment target must be a variable or index")

    def _load_module(self, name):
        if name in self.modules:
            return self.modules[name]

        if name in self.module_cache:
            return self.module_cache[name]

        if not name or "." in name or "/" in name or "\\" in name:
            raise LabScriptError(f"invalid module name: {name!r}")

        search_paths = list(self.module_paths)
        env_path = os.environ.get("LABSCRIPT_PATH", "")
        for item in env_path.split(os.pathsep):
            if item:
                search_paths.append(Path(item).resolve())

        for directory in search_paths:
            candidate = directory / f"{name}.lab"
            if not candidate.is_file():
                continue

            module_env = Environment()
            module_env.values.update(default_builtins(self.output))
            module_env.values.update(self.modules)

            source = candidate.read_text(encoding="utf-8")
            old_paths = list(self.module_paths)
            if candidate.parent not in self.module_paths:
                self.module_paths.insert(0, candidate.parent)

            try:
                self.execute(source, filename=str(candidate), env=module_env)
            finally:
                self.module_paths = old_paths

            builtin_names = set(default_builtins(self.output)) | set(self.modules)
            public = {
                key: value
                for key, value in module_env.values.items()
                if not key.startswith("_") and key not in builtin_names
            }
            module = ModuleNamespace(name, public)
            self.module_cache[name] = module
            return module

        raise LabScriptError(f"module not found: {name}")

    @staticmethod
    def _truthy(value):
        return bool(value)


def run_source(
    source: str,
    *,
    filename="<labscript>",
    max_steps=1_000_000,
    modules=None,
):
    output = io.StringIO()
    runtime = LabRuntime(output=output, max_steps=max_steps, modules=modules)
    runtime.execute(source, filename=filename)
    return output.getvalue(), runtime.globals.values
