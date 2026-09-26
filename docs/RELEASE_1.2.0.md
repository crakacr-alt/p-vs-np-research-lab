# Release 1.2.0 — LabScript foundation

Version 1.2.0 adds a new user-facing programming layer without removing the
existing SAT/Turing/MCP interfaces.

## LabScript 0.1

- English and Russian syntax;
- explicit language directive;
- Unicode identifiers;
- variables, arithmetic, lists/maps, conditions, loops and functions;
- local LabScript modules;
- controlled host modules for embedding;
- math, crypto and SAT built-in modules;
- JSON, Base64 and hashing helpers;
- statement step limit;
- deterministic debug trace.

## Tooling

- standalone labscript CLI;
- pnp-lab lang bridge;
- check/run/debug/build/verify/hash/encode/decode commands;
- deterministic .labpkg format;
- SHA-256 verification for packaged source files;
- dependency-aware packaging;
- safe package extraction;
- Jupyter %%lab magic;
- Markdown/Obsidian fenced-block runner.

## Compatibility

The core language is pure Python and CI checks Windows, Linux and macOS.
Android can currently use the Python runtime through Termux/Pydroid-style
environments; a separate native/WASM runtime remains future work.

## Correctness and safety

- arbitrary Python object attributes are not exposed;
- arbitrary Python imports are not allowed;
- package paths are validated before extraction;
- identical source inputs produce identical .labpkg bytes;
- old SAT/XOR/Turing tests remain part of the same CI.

LabScript is not an OS-level resource sandbox. CPU/RAM isolation belongs to the
host/container layer.

## Why this release matters

The laboratory can now be used as a standalone programmable tool, not only via
Python or an AI/MCP client. The same extension boundary will be used by future
Lean, SMT, symbolic math and PDE engines.
