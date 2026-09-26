# LabScript 0.1 — English reference

LabScript is a small high-level language embedded in P vs NP Research Lab.
It is designed for normal programs as well as calls into exact scientific engines.

Core principles:

- one program model for Russian and English syntax;
- Python-like indentation and readability;
- Unicode identifiers;
- no implicit access to the full Python runtime;
- local modules plus explicitly supplied host modules;
- reproducible portable .labpkg builds;
- the same source works in CLI, Jupyter and Markdown/Obsidian.

## Language directive

Prefer an explicit first-line directive:

```lab
LangRule="-ENG"
```

Russian mode uses:

```lab
Язык="-РУС"
```

EN/ENG/АНГ and RU/RUS/РУС variants are accepted.

## Minimal program

```lab
LangRule="-ENG"

function square(x):
    return x * x

for i in range(1, 6):
    print(i, square(i))
```

Russian syntax is equivalent:

```lab
Язык="-РУС"

функция квадрат(x):
    вернуть x * x

для i в диапазон(1, 6):
    печать(i, квадрат(i))
```

## Main keywords

| English | Russian | Meaning |
|---|---|---|
| let | пусть | assignment |
| function | функция | function |
| return | вернуть | return |
| if | если | condition |
| elseif | иначе если / иначеесли | additional branch |
| else | иначе | alternate branch |
| while | пока | loop |
| for | для | iteration |
| in | в | membership/iteration |
| break | прервать | leave loop |
| continue | продолжить | next iteration |
| pass | пропустить | no-op |
| true | истина | boolean true |
| false | ложь | boolean false |
| null | пусто | no value |
| and | и | boolean AND |
| or | или | boolean OR |
| not | не | boolean NOT |
| import | импорт | module import |
| from | из | import name |
| as | как | alias |

Strings and comments are never keyword-translated.

## Data types and standard library

0.1 supports integers, floats, bool, strings, lists, tuples, maps/dicts and null.

Portable built-ins include print, len/length, range, sum, min, max, abs, round,
sorted, enumerate, zip, numeric/text conversion, append, string helpers, JSON,
hashing, Base64, assertions and type inspection.

## Built-in modules

math provides common mathematical functions and constants.

crypto provides hashing and Base64.

sat exposes the Research Lab exact SAT solvers:

```lab
LangRule="-ENG"
import sat

let result = sat.solve(
    2,
    [[1, 2], [-1, 2]],
)

print(result["sat"])
```

## Local modules

helper.lab:

```lab
LangRule="-ENG"

function triple(x):
    return x * 3
```

main.lab:

```lab
LangRule="-ENG"

import helper
print(helper.triple(14))
```

Modules are resolved next to the program and through LABSCRIPT_PATH.

## Embedding modules

A Python host can explicitly expose a ModuleNamespace. LabScript only receives
the functions and values placed in that namespace. This is the intended bridge
for future Lean, Z3, SymPy, PDE and company-specific integrations.

## CLI

```bash
labscript new hello.lab --lang ENG
labscript check hello.lab
labscript run hello.lab
labscript debug hello.lab
labscript build hello.lab
labscript verify hello.labpkg
labscript run hello.labpkg
labscript hash hello.lab --file
labscript encode64 "hello"
labscript decode64 "aGVsbG8="
```

The same frontend is available through:

```bash
pnp-lab lang run hello.lab
```

## Debug and build

Debug mode in 0.1 is a deterministic statement trace with line, step, statement
type and local values. Interactive breakpoints/watchpoints are planned next.

Build creates a deterministic portable .labpkg containing only the main source
and imported local LabScript modules. Every file is SHA-256 verified and ZIP
metadata is normalized, so identical sources produce identical package bytes.

It is a portable source package, not yet a native executable or WASM binary.

## 0.1 limits

Not implemented yet: classes, async/await, decorators, arbitrary Python imports,
direct file/network APIs, an interactive debugger, or a native/WASM compiler.

The runtime has a statement step limit, but it is not a complete OS sandbox:
heavy calculations can still consume CPU and memory.
