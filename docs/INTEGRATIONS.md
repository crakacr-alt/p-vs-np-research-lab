# LabScript integrations

LabScript is deliberately usable without AI. MCP remains one interface, not the
main runtime.

## Jupyter / IPython

Install the optional integration:

```bash
pip install -e ".[jupyter]"
```

Load the extension once:

```python
%load_ext pnp_lab.labscript.jupyter
```

Then a cell can contain a complete program:

```text
%%lab
Язык="-РУС"

функция куб(x):
    вернуть x ** 3

для i в диапазон(1, 5):
    печать(i, куб(i))
```

Runtime state is kept between LabScript cells in the same IPython session.

## Obsidian and ordinary Markdown

Put LabScript in a fenced block with language lab or labscript.

Example note:

```markdown
# Experiment

~~~lab
Язык="-РУС"
пусть x = 40
~~~

~~~lab
Язык="-РУС"
печать(x + 2)
~~~
```

Run:

```bash
labscript markdown note.md
```

The original note is not edited. A sibling note named
note.lab-results.md is created with outputs from each block. Blocks share one
runtime, so later blocks can use variables/functions from earlier blocks.

This works for a normal Markdown folder and for an Obsidian vault.

A dedicated Obsidian plugin and live execution bridge are planned after the
language core is stable. The current format will remain compatible with that
plugin.

## Python embedding

```python
from pnp_lab.labscript import LabRuntime, ModuleNamespace

company = ModuleNamespace(
    "company",
    {
        "price_with_tax": lambda x: round(x * 1.2, 2),
    },
)

runtime = LabRuntime(modules={"company": company})
runtime.execute("""
LangRule="-ENG"
import company
print(company.price_with_tax(100))
""")
```

The host decides exactly which functions become visible.

## Windows / Linux / macOS

The core runtime is pure Python and is continuously tested on all three desktop
OS families in GitHub Actions.

Python 3.10+ is required.

## Android

The current Python runtime can be used through environments such as Termux or
Pydroid where Python 3.10+ and the package can run.

Android is not yet a separately certified native runtime. The long-term target
is a WASM/portable runtime so the same .lab and .labpkg files can run in mobile,
browser and desktop hosts without changing the language.

## Portable packages

Use:

```bash
labscript build program.lab
labscript verify program.labpkg
labscript run program.labpkg
```

Portable build includes only imported local LabScript modules. It does not
download dependencies from the network.

## MCP / AI

Existing MCP tools continue to work. A future LabScript MCP module will let an
agent generate and execute LabScript while the exact/verifier layers remain
responsible for scientific claims.
