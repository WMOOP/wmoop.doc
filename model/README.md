# `model/` — the canonical World Model (WML)

This directory is the **single source of truth** (Invariant 1). Everything here is written in
**WML**, the language-neutral DSL specified in [`../docs/03-architecture.md`](../docs/03-architecture.md).
Per-language repositories (`wmoop.net`, and later `wmoop.java`, `wmoop.py`, `wmoop.cpp`) are
**generated from and conformance-tested against** these files — never hand-maintained in parallel.

## Layout

```
model/
├── nature/      wmoop.nature     — biology branch (Animal → Human → Person)
├── transport/   wmoop.transport  — Vehicle hierarchy + the Driver/Owner roles
└── geography/   wmoop.geography  — administrative areas (Composite / part_of)
```

Each top-level folder is a **module** (an L1 domain). A module declares its `id`, `version`, and
its `depends_on` edges — which must stay **acyclic** (Invariant 5). A module may span several
`*.wml.yaml` files.

## What each file may contain

- `module:` header — id, semantic version, dependencies.
- `datatypes:` / `enumerations:` — value types and closed value sets.
- `interfaces:` — behavioural contracts (capabilities).
- `concepts:` — L1 classes, with `extends` (shallow, Liskov-clean `subclass_of` only),
  `properties` (each typed, with `unit` when measurable), `invariants`, and `provenance`.
- `roles:` — cross-cutting / cross-domain facets attached by composition (`has_role`), e.g.
  `Driver` *played_by* `Person`. **Never** modelled as `Driver : Person`.
- `relations:` — associations such as `part_of` (mereology) and domain links, with inverses.

## The three worked domains

| Module | Shows |
|--------|-------|
| `transport` | A genuine shallow **is-a** hierarchy `Vehicle → RoadVehicle → Motorcycle → Moped`, plus the **Driver** role (the cross-domain crux). |
| `nature` | A deliberately shallow biological lineage; intermediate ranks are carried as `classified_as` facts, not inheritance levels. |
| `geography` | **`part_of` composition**: `Country ⊃ County ⊃ City`. The areas *are* kinds of `AdministrativeArea` (inheritance), but their **containment** is a `part_of` relation — the exact distinction WMOOP insists on. |

Every one of these is mirrored by compiling, runnable C# in
[`wmoop.net`](https://github.com/WMOOP/wmoop.net) (`Wmoop.Transport`, `Wmoop.Nature`,
`Wmoop.Geography`), so you can read the model and the generated-shape side by side.

> Reference C# bindings may implement a **subset** of a module (e.g. collapsing documented
> intermediate biological ranks) for clarity; the WML here remains authoritative.
