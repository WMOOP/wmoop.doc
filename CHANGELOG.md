# Changelog

All notable changes to the canonical WMOOP model and documentation are recorded here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
follows [Semantic Versioning](https://semver.org/) for the **model** (see the versioning policy in
[GOVERNANCE.md](GOVERNANCE.md)): a breaking change to the meta-model or to any stable domain bumps
the MAJOR version.

## [Unreleased]

### Added
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
- `model/taxonomy.yaml` updated (registry 0.1.0→0.2.0): `education` added; `architecture`, `org`,
  `nature.anatomy` promoted to **seeded**; the two diagrams in `docs/06-domain-taxonomy.md` regenerated.
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

### Notes
- This is **v0 (experimental)**. The WML format and tooling are not yet stable; see the
  [adversarial review](docs/05-adversarial-review.md) for known open problems.

[Unreleased]: https://github.com/WMOOP/wmoop.doc/commits/main
