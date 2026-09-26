# Scientific platform direction

P vs NP Research Lab is moving from a SAT-only laboratory toward a general
verifiable computational research platform.

The project will keep SAT and representation switching as first-class research
areas. The goal is not to hide them behind a generic interface, but to let the
same reproducible workflow use several independent engines.

## Layered design

1. LabScript / Python / Jupyter / MCP frontends.
2. Problem and Result data model.
3. Engine registry.
4. Exact, symbolic, numerical and formal engines.
5. Cross-check and counterexample layer.
6. Reproducible artifacts, plots and reports.
7. Formal verification where feasible.

LabScript host modules added in 1.2 are the extension boundary for these engines.

## Planned engine families

### SAT and discrete exact search

- internal DPLL/Hybrid/RepresentationSwitching;
- modern CDCL backend;
- CaDiCaL/PySAT adapters;
- proof-producing UNSAT backends;
- DRAT/LRAT verification.

### SMT

Z3-class backend for integer/real arithmetic, bit-vectors, arrays and program
constraints.

### Symbolic mathematics

SymPy-class backend for algebra, calculus, equations, symbolic simplification
and exact transformations.

### Formal proof

Lean 4 + mathlib bridge.

The intended workflow is:

conjecture -> computation -> counterexample search -> proof obligations ->
Lean proof -> kernel acceptance.

AI may propose a proof, but only the formal verifier can mark a theorem as
formally verified.

### Rigorous numerics

Interval/ball arithmetic to carry explicit error bounds rather than relying only
on float64 approximations.

### Numerical science

ODE/PDE and optimization backends. Planned integrations include SciPy-class
tools for local work and scalable PETSc/FEniCSx-class tools for larger PDE
experiments.

## Result confidence levels

The platform will distinguish result classes instead of calling everything
"proved":

0. CONJECTURE — unverified statement.
1. NUMERICAL — numerical evidence.
2. CROSS_CHECKED — independent methods agree.
3. RIGOROUS_NUMERICS — certified numeric bounds.
4. CERTIFIED — machine-checkable certificate.
5. FORMAL — proof accepted by a formal proof kernel.

The exact names may evolve before the API is frozen, but the separation itself
is a design requirement.

## Navier–Stokes and other hard problems

A PDE module can help with simulations, convergence studies, residuals, energy
checks, interval bounds, counterexample search and formal proof obligations.

It must not turn a successful numerical run into a claim that an open
mathematical problem has been solved.

The same rule applies to P vs NP, Riemann-type questions and other major open
problems: computation is evidence unless a suitable certificate/formal proof
establishes more.

## Reproducibility

Every future experiment should be able to record:

- source/commit;
- engine and version;
- dataset/input hashes;
- parameters and random seed;
- platform information;
- logical metrics;
- runtime metrics;
- produced certificates;
- plots/data;
- verification status.

This is the main criterion for adding a scientific backend.
