# P vs NP Research Lab

[Русский README](README.md)

P vs NP Research Lab is an open verifiable computational research laboratory.
It started with exact SAT, representation switching and reproducible complexity
experiments. Version 1.2 adds LabScript, a bilingual user-facing programming
language and a stable extension boundary for future symbolic, SMT, formal and
numerical engines.

> Release: 1.2.0  
> Scientific status: this project is not a proof of P = NP or P != NP.

## What works now

- exact DPLL, Hybrid and RepresentationSwitching SAT solvers;
- CNF -> XOR recognition and GF(2) solving;
- independent model checks and brute-force/reference verification;
- structured benchmarks and machine-readable reports;
- hard-instance search;
- deterministic Turing Machine model;
- hypothesis database;
- MCP integration for AI clients;
- LabScript 0.1 for standalone human use.

## LabScript

English:

```lab
LangRule="-ENG"

function square(x):
    return x * x

for i in range(1, 6):
    print(i, square(i))
```

Russian:

```lab
Язык="-РУС"

функция квадрат(x):
    вернуть x * x

для i в диапазон(1, 6):
    печать(i, квадрат(i))
```

LabScript is not a renamed Python exec wrapper. It has a controlled runtime,
a restricted syntax set and explicit modules.

Current features:

- functions, conditions and loops;
- Unicode variable/function names;
- lists, tuples and maps;
- local .lab modules;
- explicitly embedded host modules;
- math, crypto and SAT modules;
- JSON, Base64 and hashing helpers;
- deterministic debug trace;
- portable deterministic .labpkg builds with SHA-256 verification;
- Jupyter magic;
- Markdown / Obsidian block execution.

## Install

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -e .
```

Self-test:

```bash
pnp-lab doctor
```

## LabScript quick start

```bash
labscript new hello.lab --lang ENG
labscript check hello.lab
labscript run hello.lab
labscript debug hello.lab
labscript build hello.lab
labscript verify hello.labpkg
labscript run hello.labpkg
```

The same frontend is available under the main CLI:

```bash
pnp-lab lang run hello.lab
```

## Exact SAT

```bash
pnp-lab solve examples/simple_sat.cnf --solver switch
```

Verification:

```bash
pnp-lab verify \
  --variables 8 \
  --clauses 30 \
  --count 100 \
  --bruteforce
```

Release benchmark:

```bash
pnp-lab benchmark --output results/release
```

## Jupyter

```bash
pip install -e ".[jupyter]"
```

Then:

```python
%load_ext pnp_lab.labscript.jupyter
```

And in a cell:

```text
%%lab
LangRule="-ENG"
print(40 + 2)
```

## Obsidian / Markdown

Use fenced blocks labelled lab or labscript and run:

```bash
labscript markdown note.md
```

The source note stays unchanged. LabScript creates a separate result note.

## Python / company embedding

A host can expose only approved functions:

```python
from pnp_lab.labscript import LabRuntime, ModuleNamespace

company = ModuleNamespace(
    "company",
    {"tax": lambda price: round(price * 1.2, 2)},
)

runtime = LabRuntime(modules={"company": company})
runtime.execute("""
LangRule="-ENG"
import company
print(company.tax(100))
""")
```

This is the intended integration boundary for future Lean, Z3, SymPy, numerical
PDE engines and private enterprise modules.

## Platform support

LabScript core is pure Python and CI tests Windows, Linux and macOS.

Android currently uses the Python runtime through environments such as Termux or
Pydroid. A native/WASM runtime is on the roadmap; the .lab source format is
intended to remain compatible.

## Scientific direction

The project is growing into a layered research platform:

- SAT / CDCL / proof certificates;
- SMT;
- symbolic mathematics;
- Lean formal proof;
- rigorous interval/ball numerics;
- ODE/PDE and optimization;
- reproducible plots/reports;
- counterexample search;
- AI orchestration that cannot self-declare a theorem as proved.

See [Scientific platform direction](docs/SCIENTIFIC_PLATFORM.md).

## Documentation

- [LabScript English](docs/LABSCRIPT_EN.md)
- [LabScript Russian](docs/LABSCRIPT_RU.md)
- [Jupyter / Obsidian / platforms](docs/INTEGRATIONS.md)
- [Scientific platform direction](docs/SCIENTIFIC_PLATFORM.md)
- [Representation switching](docs/REPRESENTATION_SWITCHING.md)
- [Scientific method](docs/SCIENTIFIC_METHOD.md)
- [Experiment protocol](docs/EXPERIMENT_PROTOCOL.md)
- [MCP](docs/MCP.md)
- [Turing Machine](docs/TURING_MACHINE.md)
- [Security](SECURITY.md)
- [Roadmap](ROADMAP.md)
- [Changelog](CHANGELOG.md)

## Verification

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s property_tests -v
pnp-lab doctor
```

Experimental performance is evidence about tested instances, not a proof of an
asymptotic complexity result.
