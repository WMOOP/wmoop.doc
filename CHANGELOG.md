# Changelog

All notable changes to the canonical WMOOP model and documentation are recorded here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
follows [Semantic Versioning](https://semver.org/) for the **model** (see the versioning policy in
[GOVERNANCE.md](GOVERNANCE.md)): a breaking change to the meta-model or to any stable domain bumps
the MAJOR version.

## [Unreleased]

### Added
- **Conformance vectors** (`conformance/`, docs/03-architecture.md §3).
  - The suite every binding runs, written once as data: `conformance/<domain>/*.case.yaml`, in the format of
    `conformance/README.md` and `case.schema.json`.
  - 25 active cases: 15 hold the 16 checks that `wmoop.py` and `wmoop.net` used to hand-write twice, and 10 are new.
    They cover identifiers, quantities and their units, the inheritance chains, abstractness, required and `1..*`
    properties, defaults, enumerations, roles and `cardinality_per_player`, relations with their inverse, and the
    hand-written behaviour the bindings keep in step.
  - Three pending cases, the §3.3 examples among them, for rules the model specifies but no binding enforces yet:
    constraints, capabilities and canonical serialization.
  - `schema/build_conformance.py` checks every case against the model and writes `conformance/suite.json`, the
    bundle the runners read, so they need no YAML parser. CI runs its self-test and `--check`.
- **Error-code registry as data**: `conformance/error-codes.yaml`, with three new codes: `WM-ID-INVALID`,
  `WM-UNIT-MISSING` and `WM-ROLE-ALREADY-ATTACHED`.
- **Foundation module** `wmoop.core` (`model/core/core.wml.yaml`, v1.0.0): the L0 kernel referenced by
  every domain — `QuantityKind`s with their SI dimension 7-vector, `Unit`s with `toCanonical`
  conversions, and the provenance/identity base types.
- **Five new seed domains** (authored + adversarially reviewed, each sourced):
  - `wmoop.math` — abstract objects: `Number → {ℕ,ℤ,ℚ,ℝ}` (siblings, not nested inheritance), `Set`
    as a Collection, `GeometricShape → Polygon → Triangle/Quadrilateral`, `Group` as an AbstractType
    whose axioms are invariants. Sourced to ISO 80000-2, Peano, Euclid, Halmos, Dummit & Foote.
  - `wmoop.music` — the showcase of all three L0 categories: Abstract (`PitchClass`, `Interval`,
    `Scale`, `Chord`), Endurant (Hornbostel-Sachs instrument families), Perdurant
    (`MusicalPerformance`, `NoteOccurrence`) + the `Performer` role. Sourced to ISO 16, MIDI 1.0,
    Hornbostel-Sachs.
  - `wmoop.space` — `CelestialBody → {Planet, DwarfPlanet, Star, NaturalSatellite}` (DwarfPlanet a
    sibling of Planet per IAU B5); the 8 planets + Pluto as L2 individuals from the NASA NSSDC
    Planetary Fact Sheet.
  - `wmoop.philosophy` — `Concept`, `Proposition`, `Argument → {Deductive → Syllogism, Inductive}`;
    Aristotle's 10 categories and the 5 branches as L2 individuals; contested classification kept in
    prose. Sourced to Aristotle and the SEP. Models the abstractions with which we abstract the world.
  - `wmoop.chemistry` — `ChemicalSubstance → Element/Compound` (endurants), `Atom part_of Molecule`,
    `ChemicalReaction` (perdurant), `Catalyst` (role); H/C/O/Fe as L2. Sourced to IUPAC.
- **New domains — the "school" worked example**: `wmoop.education` (`model/education/`) with
  `School` (is-a `Organization`, **not** a `Building`), `Classroom`/`Laboratory` (is-a `Room`),
  `CurriculumSubject` (abstract, with L2 subjects Mathematics/Romanian/Biology/Music), `Mark`
  (a reified grade), `StudentClass` (a Collection), and the `Student`/`Teacher`/`FormTutor`
  (RO *diriginte*) **roles** on `Person`. Sourced to ISCED 2011, ISCED-F 2013, ISCO-08.
- **Support domains** it builds on: `wmoop.architecture` (`Building`, `Room` `part_of` `Building`;
  ISO 6707-1) and `wmoop.org` (`Organization` + the `Employee` role; schema.org/ISCO-08).
- **Anatomy branch** in `wmoop.nature` (`model/nature/anatomy.wml.yaml`, module bumped 0.5.0→0.6.0):
  `AnatomicalStructure → Organ` with `Heart/Brain/Lung/Liver/Kidney/Stomach`, `OrganSystem`
  (Collection, with 5 organ systems as L2), and `Organ part_of Animal`. Sourced to Uberon (PMID
  22293552) and the FMA.
- **`docs/07-expansion-roadmap.md`**: how the model grows toward full coverage — philosophical
  footing (BFO/DOLCE/UFO/SUMO; Aristotle's categories), prioritization rubric, sequenced waves, and
  a reusable domain brief.
- **`model/_template/DOMAIN_TEMPLATE.wml.yaml`** + a 6-step "add a domain" quickstart in
  [`model/README.md`](model/README.md) to make contributing a new domain easy.
- `model/taxonomy.yaml` updated (registry → 0.3.0): `education` added; `core`, `architecture`, `org`,
  `nature.anatomy`, `math`, `music`, `space`, `philosophy`, `chemistry` promoted to **seeded**; the two
  diagrams in `docs/06-domain-taxonomy.md` regenerated to match.
- **WML schema & validation (`schema/`)** — the machine contract for WML: `wml.schema.json`
  (JSON Schema 2020-12) and `wml.xsd` (W3C XSD); a validator (`validate_wml.py`: grammar gate +
  the S1–S6 semantic gates + referential integrity + optional XSD check); a deterministic YAML→XML
  projector (`yaml_to_xml.py`) with the six seeded modules projected under `schema/examples/`; the
  language specification (`schema/README.md`); and a CI workflow
  (`.github/workflows/wml-validate.yml`).
- **Canonical schema relocated** to the dedicated repo
  [`WMOOP/wmoop.json`](https://github.com/WMOOP/wmoop.json). `schema/wml.schema.json` and
  `schema/wml.xsd` here are now synced **mirrors**, guarded by a freshness check
  (`schema/check_canonical.py`) — resolving the meta-schema-location inconsistency flagged in
  `docs/05-adversarial-review.md`.
- **Founding documentation set**: whitepaper, foundations & related work, the L0 meta-model,
  the WML schema format & cross-language generation design, the academic program, and an
  independent adversarial design review (`docs/`).
- **`PATTERNS.md`**: OOP best practices and the design-pattern catalogue.
- Governance, ethics, contribution (human and AI), code of conduct, security and support documents.
- Project hygiene: issue/PR templates, `CODEOWNERS`, data license.
- Reference implementation scaffolding in [`wmoop.net`](https://github.com/WMOOP/wmoop.net):
  the `Wmoop.Core` kernel (meta-model), `Wmoop.Nature`, `Wmoop.Transport`, `Wmoop.Geography`
  domains, a `Wmoop.Patterns` library, runnable demos and a dependency-free conformance test
  suite — all building on .NET 8 with the cross-domain `Person`→`Driver` role worked end to end.
- Example WML model files for the Transport, Nature and Geography domains (`model/`).

### Changed
- **The WML grammar is a git submodule, not a mirror.** `wml.schema.json` and `wml.xsd` come from
  `WMOOP/wmoop.json`, pinned at `external/wmoop.json`. The copies in `schema/` and
  `schema/check_canonical.py` are gone, so the two can no longer drift. Clone with
  `--recurse-submodules` (or run `git submodule update --init`); CI checks that the pin is a
  commit on `wmoop.json` main.
- **`schema/validate_wml.py` now enforces the rules the docs describe as machine-checked**, instead
  of passing them silently:
  - **References and dependencies:** a reference into another module needs a declared `depends_on`
    and a satisfied version pin. A reference into a module that does not exist is an error; a
    typo used to pass as "external".
  - **Units:** they resolve to the `wmoop.core` catalogue and match the property's QuantityKind.
  - **Inverses:** each belongs to its relation's target and agrees with a declared other end.
  - **L2 individuals:** checked against their concept (keys, types, cardinality, inherited
    constraints, required values, simple invariants).
  - **Schemes and associations:** registered and checked.
  - **Overrides:** must narrow every inherited constraint.
  - **Layout:** each module lives in one directory.
  - **Robustness:** a malformed file is reported, not a crash.
  - **Cross-module `extends`:** allowed along a declared dependency.
  - **Self-test:** `schema/test_validate_wml.py` has one failing fixture per rule and runs in CI.
- **Model data fixes found by the stricter validator:**
  - **`wmoop.core` 1.0.0 → 1.1.0:** adds the `km` (Kilometre) and `d` (Day) units, which
    `wmoop.space` already used for radii and orbital periods.
  - **`wmoop.nature` 0.6.0 → 0.7.0:** declares the `wmoop.nature/NcbiTaxonomy` scheme. `Human`'s
    classification previously pointed at an undeclared `wmoop.scheme/NcbiTaxonomy`; it now uses
    the new scheme and carries its own provenance.
  - **Re-pinned dependents:** `transport`, `org`, `education` and `music` now require
    `wmoop.nature ^0.7.0`.
- **Docs aligned with the validator:**
  - **Cross-module `extends`:** allowed only along a declared `depends_on`; cross-domain facets
    stay roles. Updated in 02-meta-model, GOVERNANCE (new normative constant), CONTRIBUTING,
    AI_CONTRIBUTING and the whitepaper.
  - **Inheritance depth:** depths 5 and 6 both warn.
  - **Constructs:** `schemes`, `associations` and `completeness` are no longer described as
    "planned", and the architecture spec lists the nine constructs.
  - **Examples:** version-pin examples use `wmoop.nature ^0.7.0`.
  - **Units:** the unit rule names the `wmoop.core` catalogue instead of UCUM.
- **README:**
  - **Repository topology:** the table links all nine WMOOP repositories and has a status column.
    `wmoop.json` (the canonical grammar), `wmoop.js` and `wmoop.db` were missing.
  - **Intro:** it names the bindings `wmoop.tools` generates today and links the conformance vectors
    and the repository topology table.
- **Binding status** (README, CONTRIBUTING, docs/03-architecture.md):
  - `wmoop.net` and `wmoop.py` are generated from the model by `wmoop.tools`, with their behaviour
    hand-written. The docs called them hand-written references.
  - `wmoop.js` is the TypeScript binding, generated the same way. The docs called it planned. Its
    behaviour is added with `extend()` and module augmentation.
  - All three run the shared conformance vectors.
  - The architecture spec has TypeScript in its generation-gap (§2.2), repository (§4.1) and
    naming (§4.2) tables.
- **`wmoop.js` is conformance-gated** (GOVERNANCE.md §1.1): it moves from the planned bindings to
  the conformance-gated bindings (v1), and `wmoop.db` is the only planned one left. The texts that
  restated the old list now name TypeScript or `wmoop.js` with the other four.
- **`CODE_OF_CONDUCT.md` and `SECURITY.md` moved to [`WMOOP/.github`](https://github.com/WMOOP/.github)**,
  the organisation's default community health files, so every WMOOP repository shows the same two
  policies without a copy or a pointer file. Links in this repo now point there.

### Notes
- This is **v0 (experimental)**. The WML format and tooling are not yet stable; see the
  [adversarial review](docs/05-adversarial-review.md) for known open problems.

[Unreleased]: https://github.com/WMOOP/wmoop.doc/commits/main
