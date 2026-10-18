<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="brand/logo/wmoop-logo-dark.svg">
    <img alt="WMOOP — World Map Object-Oriented Programming" src="brand/logo/wmoop-logo-light.svg" width="420">
  </picture>
</p>

# WMOOP — World Map Object-Oriented Programming

> **Describe the world in OOP. Map every real-world object into programming languages — once.**

WMOOP is an open-source effort to model the real world — nature and biology, mathematics,
music, astronomy, geography, vehicles, language, and beyond — as **one shared, language-neutral,
object-oriented knowledge model**, from which idiomatic code is generated in many languages
(C#, Java, Python, C++, …) **without duplicating the conceptual model**.

The goal is a kind of *"metaverse described in programming"*: a model that is readable by both
people and machines, that teaches humans and AI how concepts are structured, and that scientists,
educators, students and developers can all extend.

This repository, **`wmoop.doc`**, is the **canonical source of truth**: the meta-model, the
domain models (the *World Model*, written in the **WML** DSL), and all the project documentation.
Per-language repositories such as [`wmoop.net`](https://github.com/WMOOP/wmoop.net) are **generated
from and conformance-tested against** what lives here.

---

## The eight architectural invariants

Everything in WMOOP follows eight non-negotiable rules. They are what keep the model coherent,
scalable, and replicable across languages.

1. **Schema-first.** A canonical, language-neutral model (**WML**) is the single source of truth.
   Per-language bindings are *generated* and conformance-tested — "write once, replicate
   everywhere" is mechanical, never manual copy-paste.
2. **Three layers.** **L0** meta-model (a small, fixed set of foundational categories) · **L1**
   domain models (declarative classes, properties, relations, roles) · **L2** instances (reference
   individuals, e.g. the planets).
3. **Composition and roles over deep inheritance.** Inheritance is reserved for genuine, shallow,
   substitutable *is-a* (Liskov). Cross-cutting or cross-domain facets are **roles** attached by
   composition — a `Person` *acquires* a `Driver` role, it is never a subclass. Contested or
   multiple classification is expressed with categories, not one forced tree.
4. **Everything is sourced.** Every concept carries a stable identifier, a name, a definition, and
   **provenance** (a citation). Measurable properties carry **units** — no bare numbers.
5. **Modular and acyclic.** Domains are versioned modules with an explicit, acyclic dependency
   graph; cross-domain links are declared and versioned.
6. **Machine-checkable.** Validation is automated (CI), so humans *and* AI can contribute against a
   clear, automated Definition of Done.
7. **Ontologically complete.** L0 represents **endurants, perdurants and abstracts** as first-class
   categories, so even domains like **Math** and **Music** are fully modellable.
8. **Identity lifecycle & world-stance.** Every concept keeps a stable identifier with a
   deprecation / `sameAs` / merge policy; facts are treated **open-world**, schema conformance
   **closed-world**.

> These eight are authoritative. Where individual documents cite "Invariant #n", they refer to this
> list.

---

## The canonical cross-domain example

The hardest and most illustrative case — and the one that shows why roles beat inheritance:

- A **`Person`** lives in the **Nature** domain: an intrinsic biological entity (it *is* an animal,
  for life).
- A **`Driver`** is **not** a kind of person. It is a **role** a person *plays* while holding a
  licence — contextual, temporary, non-exclusive. The same person can be a **Driver**, an **Owner**
  and an **Employee** at once.
- So `Driver` lives in the **Transport** domain and is **attached to** a `Person` by composition,
  carrying its own meta (licence number, categories, validity dates).

A runnable implementation of exactly this is in [`wmoop.net`](https://github.com/WMOOP/wmoop.net).

---

## Documentation map

**Start here**
- [Whitepaper](docs/whitepaper.md) — the vision, problem statement, methodology, evaluation plan,
  roadmap, risks, glossary and FAQ.

**The architecture (read in order)**
1. [Foundations & related work](docs/01-foundations.md) — why "is-a" in biology is not OOP
   inheritance; what we borrow from ontologies (BFO, Wikidata, Schema.org, …).
2. [The meta-model (L0)](docs/02-meta-model.md) — the foundational categories and the decision
   rules for inheritance vs. composition vs. role.
3. [Schema format & cross-language generation](docs/03-architecture.md) — the **WML** DSL and the
   pipeline that produces idiomatic C#/Java/Python/C++ with parity.
4. [Academic program](docs/04-academic.md) — how instructors use WMOOP in OOP courses.
5. [Adversarial design review](docs/05-adversarial-review.md) — the project's honest *limitations
   and threats to validity*, from an independent critique.
6. [The World Domain Map](docs/06-domain-taxonomy.md) — the proposed top-level domain categories
   (L1) and their hierarchy, with a living cluster map and dependency diagram generated from
   [`model/taxonomy.yaml`](model/taxonomy.yaml).

**OOP craft**
- [PATTERNS.md](PATTERNS.md) — the OOP best practices and design patterns WMOOP uses and
  recommends (SOLID, GRASP, Role Object, Composite, Visitor, Strategy, Specification, Builder,
  Factory, Registry, …), each tied to the meta-model.

**Design & brand**
- [brand/DESIGN.md](brand/DESIGN.md) — the visual identity & design system: the logo family,
  the palette, and the per-repo logo pattern (the mark encodes the architecture itself).

**Taking part**
- [CONTRIBUTING.md](CONTRIBUTING.md) — how humans contribute.
- [AI_CONTRIBUTING.md](AI_CONTRIBUTING.md) — the protocol for AI/LLM contributors.
- [GOVERNANCE.md](GOVERNANCE.md) · [ETHICS.md](ETHICS.md) · [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SECURITY.md](SECURITY.md) · [SUPPORT.md](SUPPORT.md) · [CHANGELOG.md](CHANGELOG.md)

---

## Repository topology (organisation)

| Repo | Role |
|------|------|
| [`wmoop.doc`](https://github.com/WMOOP/wmoop.doc) | **This repo.** Canonical WML model + all documentation (source of truth). |
| [`wmoop.net`](https://github.com/WMOOP/wmoop.net) | The C#/.NET binding and reference implementation. |
| `wmoop.java`, `wmoop.py`, `wmoop.cpp` | *(planned)* further language bindings, generated from the WML model. |
| `wmoop.tools` | *(planned)* the generator + validators + conformance-test runner. |

The domains WMOOP models are tracked in [`model/taxonomy.yaml`](model/taxonomy.yaml) and mapped in
[the World Domain Map](docs/06-domain-taxonomy.md). Seeded domains (those with a module in `model/`
today) span the Foundation (`core`) and the formal, natural, place, society, culture and technology
clusters — including `math`, `chemistry`, `nature`, `space`, `geography`, `org`, `education`,
`music`, `philosophy`, `transport` and `architecture`. **Geography** is its own domain
(`wmoop.geography`), which **Transport** depends on. The flagship worked example is the Transport
**Driver** role on a Nature **Person**.

---

## Quickstart

- **Just want to understand it?** Read the [whitepaper](docs/whitepaper.md), then the
  [meta-model](docs/02-meta-model.md).
- **Want to see it run?** Clone [`wmoop.net`](https://github.com/WMOOP/wmoop.net) and run the demo:
  ```bash
  dotnet run --project Wmoop.Net/src/Wmoop.Demo
  dotnet run --project Wmoop.Net/src/Wmoop.Patterns.Demo
  ```
- **Want to contribute a concept or a domain?** Read [CONTRIBUTING.md](CONTRIBUTING.md) and open an
  issue with the matching template.
- **Teaching with it?** See the [academic program](docs/04-academic.md).

---

## Status & licensing

**Status: v0 (experimental).** The model, the WML format, and the tooling are under active design;
expect breaking changes. The [adversarial review](docs/05-adversarial-review.md) documents the
known open problems honestly — read it before assuming anything is final.

- **Code** (tooling, generated bindings, examples): **Apache-2.0** — see [`LICENSE`](LICENSE).
- **Model data & documentation** (WML files, prose): **CC-BY-4.0** — see
  [`LICENSE-DATA.md`](LICENSE-DATA.md). Any reuse **must credit the WMOOP project and link back to
  this source repository** (<https://github.com/WMOOP/wmoop.doc>); see the required attribution in
  [`LICENSE-DATA.md`](LICENSE-DATA.md). Attribute third-party sources as required by their licences;
  record provenance on every fact (Invariant 4).
