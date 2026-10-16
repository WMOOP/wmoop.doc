# Changelog

All notable changes to the canonical WMOOP model and documentation are recorded here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
follows [Semantic Versioning](https://semver.org/) for the **model** (see the versioning policy in
[GOVERNANCE.md](GOVERNANCE.md)): a breaking change to the meta-model or to any stable domain bumps
the MAJOR version.

## [Unreleased]

### Added
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
