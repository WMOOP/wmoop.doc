# `model/` — the canonical World Model (WML)

This directory is the **single source of truth** (Invariant 1). Everything here is written in
**WML**, the language-neutral DSL specified in [`../docs/03-architecture.md`](../docs/03-architecture.md).
Per-language repositories (`wmoop.net`, and later `wmoop.java`, `wmoop.py`, `wmoop.cpp`) are
**generated from and conformance-tested against** these files — never hand-maintained in parallel.

## Layout

```
model/
├── core/          wmoop.core         — L0 kernel: QuantityKinds + SI dimensions, Units, provenance/identity
├── math/          wmoop.math         — abstract objects: Number tower, Set, Polygon, Group (axioms-as-invariants)
├── nature/        wmoop.nature       — biology branch (Animal → Human → Person) + anatomy (Organ part_of Animal)
├── chemistry/     wmoop.chemistry    — Element/Compound (endurants), Atom part_of Molecule, Reaction (perdurant), Catalyst (role)
├── space/         wmoop.space        — CelestialBody → Planet/DwarfPlanet/…; the 8 planets as L2 individuals
├── transport/     wmoop.transport    — Vehicle hierarchy + the Driver/Owner roles
├── geography/     wmoop.geography    — administrative areas (Composite / part_of)
├── architecture/  wmoop.architecture — Building + Room (Room part_of Building)
├── org/           wmoop.org          — Organization + the Employee role
├── education/     wmoop.education    — the "school" example (School is-a Organization; Student/Teacher/FormTutor roles)
├── music/         wmoop.music        — all three L0 categories: theory (Abs), instruments (End), performance (Perd)
├── philosophy/    wmoop.philosophy   — Concept/Proposition/Argument; Aristotle's categories & branches as L2
├── _template/     DOMAIN_TEMPLATE    — copy-paste skeleton for a NEW domain (not a module)
└── taxonomy.yaml  domain registry    — the full domain map (clusters, status, deps)
```

`taxonomy.yaml` is **not** a WML module; it is the catalog of all domains (seeded, planned and
candidate) from which the diagrams in [`../docs/06-domain-taxonomy.md`](../docs/06-domain-taxonomy.md)
are generated. Add or move a domain there, then regenerate the diagrams.

Each top-level folder is a **module** (an L1 domain). A module declares its `id`, `version`, and
its `depends_on` edges — which must stay **acyclic** (Invariant 5). A module may span several
`*.wml.yaml` files.

## What each file may contain

- `module:` header — id, semantic version, dependencies.
- `datatypes:` / `enumerations:` — value types and closed value sets.
- `interfaces:` — behavioural contracts (capabilities).
- `concepts:` — L1 classes, with `extends` (shallow, Liskov-clean `subclass_of` only),
  `properties` (**each typed, defined, and sourced** — every property carries its own
  `definition` and `provenance`, with `unit` when measurable), `invariants`, and `provenance`.
- `roles:` — cross-cutting / cross-domain facets attached by composition (`has_role`), e.g.
  `Driver` *played_by* `Person`. **Never** modelled as `Driver : Person`.
- `relations:` — associations such as `part_of` (mereology) and domain links, with inverses.

## The worked domains

| Module | Shows |
|--------|-------|
| `transport` | A genuine shallow **is-a** hierarchy `Vehicle → RoadVehicle → Motorcycle → Moped`, plus the **Driver** role (the cross-domain crux). |
| `nature` | A deliberately shallow biological lineage; intermediate ranks are carried as `classified_as` facts, not inheritance levels. Plus **anatomy**: `Organ` **`part_of`** `Animal`, `OrganSystem` as a Collection, organs sourced to Uberon/FMA. |
| `geography` | **`part_of` composition**: `Country ⊃ County ⊃ City`. The areas *are* kinds of `AdministrativeArea` (inheritance), but their **containment** is a `part_of` relation — the exact distinction WMOOP insists on. |
| `education` (+ `org`, `architecture`) | The **cross-domain showcase**: a `School` **is-a** `Organization` (NOT a `Building`); `Classroom`/`Laboratory` **is-a** `Room`; `Student`/`Teacher`/`FormTutor` (RO *diriginte*) are **roles** on `Person`, co-held; `CurriculumSubject` is **abstract** with L2 subjects; `Mark` **reifies** a grade. One domain exercising is-a, part-of, roles, abstract types, collections and L2 at once. |
| `math` | **Abstract objects** (L0 category C): the number tower as *siblings* (set-inclusion is not inheritance), `Set` as a Collection, and `Group` as an AbstractType whose axioms are **invariants**. |
| `music` | **All three L0 categories at once**: Abstract (`PitchClass`, `Chord`), Endurant (Hornbostel-Sachs instruments), Perdurant (`MusicalPerformance`, `NoteOccurrence`), plus the `Performer` role. |
| `space` | **L2 reference individuals**: the eight planets (+ Pluto) are instances of `Planet`/`DwarfPlanet`, not subclasses — and `DwarfPlanet` is a *sibling* of `Planet` (IAU B5), not a subkind. |
| `chemistry` | **Endurant vs Perdurant**: `Element`/`Compound` endure, `ChemicalReaction` is an event; `Atom part_of Molecule`; `Catalyst` is a contextual **role**, not a kind. |
| `philosophy` | **Modelling the abstract itself**: concepts, propositions and arguments; contested classification kept honest in prose; Aristotle's ten categories and the five branches as L2. |

`transport`, `nature` and `geography` are mirrored by compiling, runnable C# in
[`wmoop.net`](https://github.com/WMOOP/wmoop.net) (`Wmoop.Transport`, `Wmoop.Nature`,
`Wmoop.Geography`), so you can read the model and the generated-shape side by side; the newer modules
generate the same way once the pipeline runs over them.

## Add a new domain — the 6-step quickstart

1. **Classify first, write second.** Read [`../docs/02-meta-model.md`](../docs/02-meta-model.md) and map
   every noun/attribute to an L0 stereotype (is-a vs part-of vs role vs quality vs category).
2. **Fill the brief.** Complete the one-page *domain brief* in
   [`../docs/07-expansion-roadmap.md`](../docs/07-expansion-roadmap.md) §6 (or the
   [`new-domain` issue template](../.github/ISSUE_TEMPLATE/new-domain.md)).
3. **Copy the skeleton.** Start from [`_template/DOMAIN_TEMPLATE.wml.yaml`](_template/DOMAIN_TEMPLATE.wml.yaml)
   into `model/<id>/<id>.wml.yaml`; keep the first PR to **≤ 5 nodes**.
4. **Source everything.** Every concept, role, enum **and property** gets its own `definition` +
   `provenance`; quantities get a `unit`. Extend existing concepts by **adding** roles, never by editing them.
5. **Register + regenerate.** Add the domain to [`taxonomy.yaml`](taxonomy.yaml) and update the two
   diagrams in [`../docs/06-domain-taxonomy.md`](../docs/06-domain-taxonomy.md).
6. **Self-verify.** Run the [`wml-contribute`](../.claude/skills/wml-contribute/SKILL.md) loop and the
   [`CONTRIBUTING.md` §8](../CONTRIBUTING.md) Definition of Done, then open a small, green, disclosed PR.

> Reference C# bindings may implement a **subset** of a module (e.g. collapsing documented
> intermediate biological ranks) for clarity; the WML here remains authoritative.
