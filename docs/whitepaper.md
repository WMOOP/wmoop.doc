# WMOOP: A Schema-First, Language-Neutral Object-Oriented Model of the World

### Position & Architecture Whitepaper

> **Tagline.** *Describe World into OOP; Map all World Objects into Programming Languages.*

| | |
|---|---|
| **Project** | WMOOP — World Map Object-Oriented Programming (`github.com/WMOOP`) |
| **Document** | Position / architecture whitepaper (RFC for community review) |
| **Version** | 0.1 — Draft |
| **Status** | Open for comment; normative once ratified by maintainers |
| **Canonical source** | `wmoop.doc` (this document and the World Model it specifies) |
| **License** | Code: Apache-2.0 (chosen). Documentation & model: CC-BY-4.0 (chosen) |

> **Reading guide.** This paper is the *frame*: it states the vision, the problem, the contributions, the method at a high level, and how we will measure success. It deliberately does **not** reproduce the deep specifications — the meta-model grammar, the domain-authoring guide, the code-generation and conformance machinery, the ethics and governance charter, and the per-domain reference models. Each of those is a self-contained section and is cited here by forward pointer: *(see §M — Meta-model specification)*, *(see §D — Domain authoring guide)*, etc. Where this frame and a detailed section disagree, the invariants in §3.1 are authoritative and both must be reconciled against them.

---

## Abstract

Human knowledge about the physical and conceptual world is vast, highly structured, and overwhelmingly *re-encoded* from scratch in every software project that needs it: a biology app re-invents a taxonomy of organisms, a logistics system re-invents vehicles, a music tool re-invents notes and intervals. The object-oriented paradigm was designed precisely to capture such "is-a-kind-of" and "is-composed-of" structure, yet there exists no shared, language-neutral, rigorously sourced, machine- and human-readable object model of the world from which idiomatic code can be produced across programming languages without duplicating the conceptual model. **WMOOP** proposes exactly this: a single canonical *World Model* (WM) — an ontology-first, declarative description of domains such as nature, mathematics, music, astronomy, geography and transport — organized in three layers (a small fixed meta-model, versioned domain models, and optional reference instances), from which per-language libraries (C#, Java, Python, C++, …) are **generated and conformance-tested**, never hand-ported. The model favors composition, interfaces/traits and *roles* over deep inheritance, treats cross-domain facets (a `Person` acting as a `Driver`) as attached capabilities rather than subclasses, and requires every concept to carry a stable global identifier, a definition, provenance, and units for quantities. Every contribution is validated automatically, giving humans **and** AI systems an unambiguous, machine-checkable Definition of Done. This paper frames WMOOP as both an engineering platform and a scientific instrument — "a metaverse described in programming" — and sets out its problem statement, contributions, three-layer methodology, evaluation plan, phased roadmap, risks, and a shared vocabulary for the community it aims to build.

---

## 1. Introduction

### 1.1 The vision

WMOOP's ambition is to build, in the open, a **shared, machine- and human-readable object-oriented model of the whole world** — and to keep that model in exactly one place while projecting it into every mainstream programming language. The founding intuition is simple and, we argue, under-exploited: the way a biology textbook decomposes *Organism → Animal → Mammal*, the way a physics course decomposes *Body → Vehicle → AutoVehicle → Moped*, and the way OOP decomposes an abstract base class into specializations are *the same intellectual act*. WMOOP makes that act explicit, canonical, cited, and reusable.

The long-horizon image is a **"metaverse described in programming"**: not a rendered 3D world, but a navigable, composable, formally structured description of reality — concepts, their properties, their relationships, the roles they can play, and the individuals that instantiate them — that a human can read, a compiler can turn into a typed library, and an AI can learn the *shape* of the world from. If an encyclopedia tells you *what* things are, WMOOP additionally tells you *how they are structured and composed*, in a form you can execute.

### 1.2 Motivation

Three pressures motivate the project.

- **Endless re-encoding.** The same domain models are rebuilt repeatedly, inconsistently, and without sources. There is no `import World.Nature.Animals` that a team can trust, extend, and cite.
- **Pedagogy needs real substance.** Object-oriented programming is usually taught on toy hierarchies (`Shape → Circle`) that are too small to expose the genuinely hard and interesting modeling decisions — when inheritance is wrong, when a role is right, how to keep a hierarchy Liskov-safe. A *real* world model turns an OOP course into applied knowledge engineering: a professor can assign a passionate student their favorite domain (landforms, countries, musical instruments) and have them contribute documented, tested, citable structure.
- **AI needs structured, sourced knowledge of how concepts compose.** Large models learn statistical associations over text; they benefit enormously from, and can also help build, an explicit, consistent, provenance-bearing scaffold of how the world is organized. WMOOP is designed to be *contributed to by AI and consumed by AI*, under human-ratified, machine-checkable rules.

### 1.3 The gap WMOOP fills

Adjacent efforts exist but none occupies WMOOP's exact position.

| Prior art (families) | What it offers | Why it is not WMOOP |
|---|---|---|
| General knowledge graphs / encyclopedias (e.g. Wikidata/DBpedia-style) | Vast sourced facts about *individuals* | Fact-centric, not an **OOP class/behavior model**; not generated into typed, idiomatic code |
| Upper/formal ontologies (BFO, DOLCE, SUMO families) | Rigorous foundational categories | Philosophically deep but not aimed at **developer-ergonomic, multi-language code generation** or classroom contribution |
| Schema vocabularies (schema.org-style) | Shared web vocabularies | Thin, web-metadata oriented; no composition/role discipline, no cross-language conformance suite |
| Standard libraries & domain SDKs | Idiomatic per-language code | **Duplicated per language and per project**; no single canonical source of truth, no provenance |

WMOOP's distinctive claim is the *conjunction*: an **ontology-first model** that is **developer-first in output**, **source-of-truth-single**, **provenance-bearing**, **role-and-composition-disciplined**, **multi-language by generation**, and **machine-checkable for open contribution by humans and AI**. No existing artifact holds all of these at once.

### 1.4 What this paper is (and is not)

This document is the whitepaper's frame. §2 states the problem and our contributions. §3 gives the methodology at the altitude at which the detailed sections attach. §4–§6 make the project falsifiable and operable: how we measure success, in what order we build, and what can go wrong. §7–§8 give the community a shared vocabulary and quick answers. The normative specifications live in their own sections and are only referenced here.

---

## 2. Problem Statement & Contributions

### 2.1 Problem statement (precise)

> **Can we construct and sustain a single, language-neutral, object-oriented knowledge model of the world — spanning many domains, carrying definitions, provenance and units, and disciplined by composition and roles rather than deep inheritance — from which idiomatic, conformance-tested libraries are *generated* in multiple programming languages with no manual duplication of the conceptual model, and which is safe for both humans and AI to extend under an automated, unambiguous Definition of Done?**

The problem decomposes into a modeling problem, an engineering problem, and a social/governance problem, each with concrete research and engineering questions.

- **RQ1 (Modeling adequacy).** Can a small, fixed meta-model (L0) express the structure of radically different domains — organisms, numbers, musical pitch, planets, administrative geography, vehicles — without forcing each into an unnatural shape?
- **RQ2 (Classification discipline).** Can we keep inheritance shallow and Liskov-safe while handling genuine multiple/contested classification, cross-domain facets, and evolution over time — using roles, interfaces/traits, and categories instead of a single rigid tree?
- **RQ3 (Mechanical parity).** Can "write once, replicate everywhere" be made *mechanical* (code generation + conformance tests) rather than aspirational, across languages with different type systems (e.g. C# vs Python vs C++)?
- **RQ4 (Sourced truth).** Can every concept and quantitative fact be made to carry a stable ID, a definition, a citation, and units, and can that be enforced automatically?
- **RQ5 (Open, AI-ready contribution).** Can the Definition of Done be made machine-checkable enough that a motivated student, a domain expert, or an AI agent can contribute safely, and that low-quality contributions are caught before merge?

### 2.2 Contributions

This whitepaper and the specifications it frames make the following contributions.

- **C1 — A position and architecture** for a schema-first, language-neutral, object-oriented *World Model* as a single source of truth, with per-language repositories positioned strictly as **generated, conformance-tested projections** (not parallel hand-maintained ports).
- **C2 — A three-layer separation** — **L0** meta-model/upper ontology (small, fixed), **L1** domain models (declarative class/property/relation/role definitions), **L2** instances/individuals (optional reference data) — defined precisely enough to be built against *(normative details in §M, §D, §I)*.
- **C3 — A modeling discipline** that privileges **composition, interfaces/traits and roles over deep inheritance**, with explicit decision rules for when `is-a-kind-of` is justified, how to keep hierarchies Liskov-safe, and how cross-domain facets (e.g. `Person`→`Driver`) are modeled as attached roles — *never* as subclasses *(worked out in §C — Classification & roles)*.
- **C4 — A provenance and units contract**: every concept carries a stable global ID, human name, definition, citation/provenance, and (for quantities) units; facts are sourced *(schema in §M; linting rules in §V)*.
- **C5 — A versioned, acyclic domain-dependency model** with declared, versioned cross-domain links, enabling independent evolution of domains without hidden coupling *(§G — Governance & versioning)*.
- **C6 — An automated, machine-checkable Definition of Done** (CI validation, cross-language conformance, provenance linting, consistency and Liskov checks) that makes the model safe to extend by **both humans and AI** *(§V — Validation & CI)*.
- **C7 — This frame itself**: a problem statement, evaluation plan, roadmap, risk register, glossary and FAQ that make WMOOP a falsifiable, operable, and teachable program rather than a slogan.

---

## 3. Methodology & Approach Overview

*This section gives the architecture at a high altitude so the detailed specifications can expand each part. It introduces the invariants, the three layers, and the schema-first pipeline, then maps the deep sections.*

### 3.1 Design principles (the normative invariants)

These eight invariants are **normative**. Every detailed section and every repository MUST conform; the architecture-review process exists to test them.

1. **Schema-first / ontology-first.** A canonical, language-neutral declarative model — the **World Model (WM)** — is the **single source of truth**, kept in `wmoop.doc`. Per-language repos (`wmoop.net`, `wmoop.java`, `wmoop.py`, `wmoop.cpp`) are **generated from** and **conformance-tested against** it. "Write once, replicate everywhere" is **mechanical** (code generation), not manual re-writing.
2. **Three layers.** **L0** meta-model/upper ontology (small, fixed foundational categories); **L1** domain models (declarative class/property/relation/role definitions); **L2** instances/individuals (optional reference data, e.g. the planets).
3. **Composition, interfaces/traits and roles over deep inheritance.** Inheritance models only genuine, stable `is-a-kind-of` essence and stays shallow (respecting Liskov). Cross-cutting or cross-domain facets (Person-as-Driver, Person-as-Employee) are **roles/capabilities attached by composition — never `Driver : Person`**. Contested or multiple classification is handled by categories/tags/multiple-parent relations, not by forcing one inheritance tree.
4. **Sourced, identified, measured concepts.** Every concept carries a **stable global ID**, a **human name**, a **definition**, **provenance/citation**, and (for quantities) **units**. Facts are sourced.
5. **Versioned, acyclic domains.** Domains are versioned modules with an **explicit acyclic dependency graph**; cross-domain links are declared and versioned.
6. **Machine-checkable.** Everything is validated in CI so that humans *and* AI contribute safely against a clear, automated **Definition of Done**.
7. **Ontological completeness.** L0 represents **endurants, perdurants and abstracts** as first-class categories, so abstract domains such as **Math** and **Music** are modellable, not only physical objects.
8. **Identity lifecycle & world-stance.** Every concept has a **stable ID** with a **deprecation / `sameAs` / merge policy**; the model is **open-world for facts** but **closed-world for schema conformance**.

### 3.2 The three-layer architecture

```
            ┌───────────────────────────────────────────────┐
  L0        │  META-MODEL (upper ontology)                   │  small, fixed, rarely changes
  "grammar" │  Concept, Property, Relation, Role, Quantity,  │  — the vocabulary in which
            │  Unit, Category, Individual, Provenance, ...   │     everything else is written
            └───────────────────────────────────────────────┘
                                  ▲ expressed in terms of
            ┌───────────────────────────────────────────────┐
  L1        │  DOMAIN MODELS (declarative)                   │  versioned modules, acyclic deps
  "content" │  Nature(Animals, Plants), Geography,           │  — the classes, properties,
            │  Math(Geometry), Music(Instruments),           │     relations and roles people
            │  Space, Transport(Vehicle→AutoVehicle→Moped)…  │     and AI contribute
            └───────────────────────────────────────────────┘
                                  ▲ instantiated by (optional)
            ┌───────────────────────────────────────────────┐
  L2        │  INSTANCES / INDIVIDUALS (reference data)      │  optional, cited
  "data"    │  the 8 planets, specific landforms, countries… │  — concrete individuals
            └───────────────────────────────────────────────┘
```

- **L0 is the grammar.** It is intentionally **small and stable**: a fixed set of foundational categories and relationships (concept, property, relation, role, quantity, unit, category, individual, provenance). Changing L0 is a rare, heavyweight event because everything is written in it. *(Normative grammar: §M — Meta-model specification.)*
- **L1 is the content.** Each domain is a **versioned module** declaring classes, properties, relations and roles in L0's vocabulary. Domains may depend on other domains, but the dependency graph is **acyclic** and cross-domain links are **declared and versioned** (Invariant 5). The seed taxonomy is tracked in `model/taxonomy.yaml` (the living source of truth) rather than a fixed set — it currently seeds `Math` (with `Geometry`), `Music` (with `Instruments`), `Nature` (with `Animals`, `Plants`), `Geography` as its own top-level domain, `Space`, and the `Transport/Auto` domain (`Vehicle → AutoVehicle → Moped`), all of which live here. *(Authoring rules: §D — Domain authoring guide.)*
- **L2 is the data.** Optional, cited reference *individuals* (e.g. the planets of the Solar System) that instantiate L1 classes. Kept separate so the model is useful even with no instances, and so facts about individuals are versioned and sourced independently of the schema. *(Instance conventions: §I.)*

### 3.3 Schema-first pipeline: one source, many languages

The defining mechanism is that languages are **outputs**, not inputs.

```
   wmoop.doc  ──►  World Model (WM)  ──►  code generator  ──►  wmoop.net  (C#)
 (single source     L0 + L1 + L2         (per-language          wmoop.java (Java)
  of truth)         declarative          emitters +             wmoop.py   (Python)
                    schema)              idiom profiles)         wmoop.cpp  (C++)
                                                │
                                                ▼
                                   conformance test suite
                        (golden cases run identically in every language)
```

- **Generate, don't port.** A contributor who models a domain in the WM — regardless of their "home" language — makes it available to *all* target languages via generation. A C# developer's contribution becomes Java/Python/C++ mechanically (Invariant 1). Hand-writing a class in one language and copy-translating it to others is explicitly **out of pattern**.
- **Idiom profiles.** Each language maps L0 constructs to its own idioms (e.g. roles → interfaces/traits/mixins/protocols as appropriate; units → value types). The *conceptual model is not duplicated*; only the emitter differs. *(Generator design and idiom profiles: §T — Code generation & toolchain.)*
- **Conformance over trust.** A shared, language-neutral suite of **golden cases** is executed against every generated library; parity is a measured number, not a promise (see §4.1, and §V — Validation & CI).

### 3.4 Modeling discipline at a glance (expanded in §C)

A one-line decision rule, stated here so the frame is self-consistent; the full guide, counter-examples and review checklist are in §C.

> **Use inheritance only for a stable, essential `is-a-kind-of` that satisfies Liskov. Use composition for `has-a` / `is-made-of`. Use a *role* for `acts-as` / `plays-the-part-of`, especially across domains. Use categories/tags for contested or multiple classification.**

Worked anchor (full treatment in §C): a `Person` is defined once in **Nature** (biology). When that person drives, they do **not** become a subclass `Driver : Person`; instead a **`Driver` role** from the **Transport** domain is *attached* to the person, carrying its own meta (driving licence, licence category, issue/expiry). The same person can simultaneously hold an `Employee` role from another domain. This keeps the biological hierarchy clean, keeps Transport and Nature **acyclically** linked by a *declared* cross-domain relation, and avoids the combinatorial explosion of `DriverEmployeePatient…` subclasses.

### 3.5 Map of the detailed sections (forward pointers)

This frame attaches to, and must stay consistent with, the following normative sections (authored separately):

| Ref | Section | Scope |
|---|---|---|
| §M | Meta-model specification | L0 grammar: entities, properties, relations, roles, quantities, units, provenance, IDs |
| §D | Domain authoring guide | How to build an L1 domain; templates; naming; the seed taxonomy worked out |
| §C | Classification & roles | Inheritance-vs-composition-vs-role decision rules; Liskov checks; cross-domain roles |
| §I | Instances & reference data | L2 conventions; sourcing individuals |
| §T | Code generation & toolchain | Generator architecture; per-language idiom profiles; packaging |
| §V | Validation & CI | Machine-checkable Definition of Done; conformance suite; linters |
| §G | Governance & versioning | SemVer for domains; acyclic dependency policy; review and ratification |
| §E | Ethics, bias & contribution manual | Contributor ethics; sourcing standards; AI-contribution policy; conduct |

---

## 4. Evaluation Plan

A world model is only credible if its success is **measurable and falsifiable**. We define success metrics, then a validation strategy that enforces them in CI, then a cadence for reporting them.

### 4.1 Success metrics

Metrics are grouped by the question they answer. Targets are initial proposals for ratification (see Roadmap §5 for when each becomes active).

| # | Metric | Definition | Why it matters | Illustrative target (v1) |
|---|---|---|---|---|
| M1 | **Domain coverage** | # ratified domains; # concepts; median & max hierarchy depth per domain | Breadth and healthy shallowness of the model | ≥ 6 domains; ≥ 500 concepts; median depth ≤ 4 |
| M2 | **Cross-language parity %** | share of WM concepts that have a generated **and conformance-passing** implementation in each target language | Proves "generate, don't port" is real (Invariant 1) | ≥ 95% parity on all shipped languages |
| M3 | **Provenance coverage %** | share of concepts and quantitative facts carrying a valid citation; share of quantities carrying units | Enforces sourced, measured truth (Invariant 4) | 100% of merged concepts cited; 100% of quantities carry units |
| M4 | **Model-health / consistency** | CI-measured: 0 dependency cycles; % of hierarchies passing Liskov checks; role-vs-subclass lint violations | Enforces discipline & acyclicity (Invariants 3, 5) | 0 cycles; ≥ 99% Liskov-clean; 0 blocking lint |
| M5 | **Contributor & academic adoption** | # active contributors; # institutions/courses using WMOOP as coursework; # student-authored domains merged | Sustainability and the teaching mission | ≥ 50 contributors; ≥ 5 courses; ≥ 20 student domains |
| M6 | **AI-contribution acceptance rate** | share of AI-authored PRs merged after human review; plus the *revert/defect rate* of merged AI PRs | Shows AI can contribute **safely** (Invariant 6) | acceptance ≥ 40%; AI-PR defect rate ≤ human baseline |
| M7 | **Downstream reuse** | # external projects depending on a WMOOP package; package downloads; # citations of `wmoop.doc` | Real-world and scientific uptake | ≥ 25 dependent projects; first external academic citation |

> **Guardrail on metrics.** Volume metrics (M1, M5) are deliberately *paired* with quality metrics (M3, M4, M6-defect-rate) so that growth cannot be gamed by merging large, unsourced, or malformed contributions. "More concepts" is never a win if provenance or consistency regresses.

### 4.2 Validation strategy

Each metric is backed by an automated check so the **Definition of Done is machine-checkable** (details in §V):

- **Schema validation.** Every L0/L1/L2 artifact validates against the meta-model grammar before merge (supports M1, M3, M4).
- **Cross-language conformance (golden cases).** A single, language-neutral suite is generated into, and executed against, every target library; parity is computed as the pass ratio (M2). A concept is "parity-complete" only when its golden cases pass identically everywhere.
- **Provenance & units linting.** A PR that introduces a concept without a stable ID, definition, and citation — or a quantity without units — fails CI (M3).
- **Consistency & discipline checks.** Dependency-cycle detection, Liskov/substitutability checks on inheritance edges, and a "role-not-subclass" linter that flags cross-domain `is-a` edges for human review (M4).
- **Human-in-the-loop review + ratification.** Automated gates are *necessary, not sufficient*: domain stewards review semantics, sourcing quality and modeling choices before ratification (supports M5, M6). AI PRs follow the **same** gates plus explicit provenance of the AI's sources (§E).
- **Peer review of the model itself.** Domains and the meta-model are periodically reviewed as one would review a scientific artifact: reproducible, sourced, and open to challenge.

### 4.3 Measurement cadence & transparency

- A **public dashboard** (generated in CI) reports M1–M7 per release.
- Metrics are recomputed **on every merge** (gating metrics) and **snapshotted per release** (trend metrics).
- Each release ships a short **model-health report** so regressions in quality are visible, not just growth.

---

## 5. Roadmap

Three phases, each with an explicit exit criterion. The phases are cumulative: later phases keep all earlier guarantees.

### 5.1 v0 — Bootstrap *(prove the pattern on a thin vertical slice)*

**Goal:** prove the schema-first pipeline end-to-end on a *small* but *complete* slice, so every later domain follows a worn path.

Milestones:

- **v0.1 — Meta-model skeleton.** Minimal L0 (concept, property, relation, role, quantity, unit, category, individual, provenance, stable IDs) ratified. *(§M)*
- **v0.2 — Two reference domains.** Model **Transport** (`Vehicle → AutoVehicle → Moped`) and a slice of **Nature** (`Person`), chosen because together they exercise *shallow inheritance*, *composition*, and the flagship **cross-domain role** (`Person` + `Driver`).
- **v0.3 — First generated library + conformance.** Generate `wmoop.net` (C#) from the WM and stand up the golden-case conformance suite. **This proves Invariant 1 concretely.**
- **v0.4 — CI Definition of Done.** Schema validation, provenance/units linting, cycle detection, and a basic role-not-subclass lint all gating merges.

**Exit criterion:** the Person-as-Driver example is modeled once in the WM, generated into C#, passes conformance, and every gate is green — with 100% provenance on the slice.

### 5.2 v1 — Breadth & second language *(prove parity and openness)*

**Goal:** show the model scales across *domains* and *languages*, and is safe for outside contributors.

Milestones:

- **v1.0 — Seed taxonomy filled.** Flesh out `Math(Geometry)`, `Music(Instruments)`, `Nature(Animals, Plants, Geography)`, `Space`, `Transport`. Ship an L2 reference set (e.g. the planets).
- **v1.1 — Second generated language.** Add one of `wmoop.py` / `wmoop.java`, hit **parity ≥ 95%** (M2) — proving generation generalizes beyond C#.
- **v1.2 — Contribution on-ramp.** Contributor guide, domain template, "good first domain" issues, and the **ethics/contribution manual** (§E) published; first **external and student** domains merged (M5).
- **v1.3 — AI-contribution track.** Documented AI-contribution policy and gates live; first AI-authored domain or extension merged under human review (M6).

**Exit criterion:** ≥ 6 domains, ≥ 2 generated languages at ≥ 95% parity, 100% provenance on merged concepts, and at least one externally-authored and one AI-authored contribution merged.

### 5.3 Long-term — toward world coverage *(sustain and deepen)*

**Goal:** steady, governed expansion toward broad coverage, with depth where it earns its keep.

Themes (not strictly ordered):

- **More languages:** add C++ and others, keeping parity a gated metric.
- **Depth on demand:** go deep (e.g. biology toward cells and DNA; astronomy toward galaxies and the universe) *only* where there is a maintainer and sourcing, to avoid scope explosion (§6).
- **Federated domains & stewardship:** domain stewards/working groups, SemVer per domain, declared cross-domain links, and a stable governance process (§G).
- **Academic & research uptake:** course kits for OOP/knowledge-engineering classes; citable releases; collaboration with domain experts; first external academic citations (M7).
- **Ecosystem:** downstream packages, tooling, and visual browsers of the model ("navigate the metaverse-in-programming").

**North star:** WMOOP is cited and reused — by developers as a dependency, by educators as coursework, by researchers as a reference, and by AI systems as structured, sourced knowledge of how the world is composed — while every one of the eight invariants still holds.

---

## 6. Risks & Mitigations

| Risk | Description | Likelihood / Impact | Mitigations |
|---|---|---|---|
| **Scope explosion** | "Model the whole world" is unbounded; effort spreads thin and nothing reaches depth or quality. | High / High | Domains are **opt-in and maintainer-gated**: no domain is added without a steward and sourcing. Depth is pursued only where demanded. Paired quality metrics (§4.1) block shallow bulk growth. Phased roadmap keeps a *complete thin slice* before breadth. |
| **Taxonomy wars** | Contested classifications (how to split organisms; what counts as a vehicle) stall in debate or fork the tree. | High / Medium | Invariant 3: contested/multiple classification uses **categories/tags/multiple-parent relations**, *not* a single forced inheritance tree. A documented **conflict-resolution process** (§G) and sourcing requirement (disputes resolved by citation, not opinion). |
| **Bias & worldview skew** | Domains reflect the cultural, linguistic, and disciplinary biases of early contributors; some perspectives under-represented. | Medium / High | Mandatory **provenance** surfaces whose sources are used; the **ethics manual** (§E) sets sourcing standards and encourages multiple authoritative references and multilingual naming; diverse stewardship; explicit "known-bias / scope" notes per domain. |
| **Bus factor** | Over-reliance on a few maintainers (founder especially) threatens continuity. | Medium / High | Everything is **in the open repo**, declarative, and machine-checkable so a newcomer can self-onboard. Multiple stewards per domain; documented governance (§G); the ethics/contribution manual encodes tribal knowledge as written rules. |
| **Over-engineering** | The meta-model or toolchain becomes so abstract it is unusable or unteachable. | Medium / Medium | Invariant 2 keeps **L0 small and fixed**; changes to L0 are heavyweight and rare. "Good first domain" path and templates (§D). The teaching use-case acts as a usability test: if a student can't model their domain, the model is too complex. |
| **Codegen complexity** | Supporting many languages idiomatically makes the generator brittle; per-language drift creeps in. | Medium / High | Conformance-first: **parity is a gated metric** (M2) and golden cases are the contract. Clear **idiom profiles** (§T) isolate per-language concerns. New languages are added only when they can hit the parity bar. |
| **Low-quality AI contributions** | AI agents submit plausible-but-wrong, unsourced, or subtly duplicated content at scale. | High / High | AI PRs face the **same machine-checkable Definition of Done** as humans, **plus** required provenance of the AI's sources and **mandatory human review** before merge (§E). M6 tracks the *defect rate* of merged AI PRs, not just acceptance, so quality regressions are visible and the policy can tighten. |
| **Model/code drift** | Hand-edits sneak into generated per-language repos, breaking single-source-of-truth. | Medium / High | Generated repos are **treated as build outputs**: CI fails on manual edits outside designated extension points; the WM remains the only place to change meaning (Invariant 1). |
| **IP / licensing contamination** | Contributors paste copyrighted text as "definitions." | Medium / Medium | Sourcing standards in §E: definitions are **written, cited, and substantially original**; provenance links the source rather than copying it; license (Apache-2.0 / CC-BY-4.0 chosen) is enforced on contribution. |

---

## 7. Glossary

- **WMOOP** — *World Map Object-Oriented Programming.* The project and the overall program of modeling the world as a single OOP model.
- **World Model (WM)** — the canonical, language-neutral, declarative model kept in `wmoop.doc`; the **single source of truth** (Invariant 1).
- **Meta-model (L0)** — the small, fixed upper ontology / grammar in which all domains are written (concept, property, relation, role, quantity, unit, category, individual, provenance).
- **Domain model (L1)** — a versioned module declaring the classes, properties, relations and roles of one subject area (e.g. Nature, Transport), written in L0.
- **Instance / Individual (L2)** — a concrete, cited individual that instantiates an L1 class (e.g. Mars instantiates `Planet`).
- **Concept** — a named, identified, defined, sourced entity in the model (a class/type at L1).
- **Role** — a facet or capability a concept can *play*, attached by composition rather than inheritance; the mechanism for cross-domain facets (e.g. the `Driver` role on a `Person`).
- **Composition** — modeling `has-a` / `is-made-of` by containing/referencing other concepts rather than subclassing.
- **Inheritance (`is-a-kind-of`)** — reserved for genuine, stable, Liskov-safe specialization; kept shallow (Invariant 3).
- **Liskov (substitutability)** — the rule that a subtype must be usable anywhere its supertype is expected; a gate on every inheritance edge.
- **Category / tag** — a non-exclusive classification used for contested or multiple membership, instead of forcing one inheritance tree.
- **Provenance** — the citation/source record attached to every concept and quantitative fact (Invariant 4).
- **Stable global ID** — a persistent identifier for a concept that survives renaming and refactoring.
- **Units** — the measurement units required on every quantity.
- **Code generation / generator** — the toolchain that emits per-language libraries from the WM (Invariant 1).
- **Idiom profile** — the per-language mapping from L0 constructs to that language's idioms (interfaces/traits/protocols, value types, etc.).
- **Conformance suite / golden cases** — language-neutral test cases run against every generated library to measure **parity**.
- **Parity** — the share of WM concepts correctly and identically realized across target languages (metric M2).
- **Acyclic dependency graph** — the required shape of inter-domain dependencies; no cycles (Invariant 5).
- **Cross-domain link** — a declared, versioned relationship between concepts in different domains (e.g. Transport's `Driver` role referencing Nature's `Person`).
- **Definition of Done (DoD)** — the machine-checkable set of gates a contribution must pass to merge (Invariant 6).
- **Steward / maintainer** — a person (or working group) responsible for a domain's quality, sourcing and evolution.
- **Per-language repo** — `wmoop.net` (C#), `wmoop.java`, `wmoop.py`, `wmoop.cpp`, … : **generated outputs**, not hand-maintained ports.

---

## 8. FAQ

**Q: Isn't this just another ontology / knowledge graph?**
A: No — it is ontology-first but **developer-first in output**. Unlike fact-centric graphs or purely philosophical upper ontologies, WMOOP's model is designed to be **generated into idiomatic, typed, conformance-tested code** in many languages from one source, with provenance and units, and to be contributable by students and AI under automated gates. See §1.3.

**Q: If I only know C#, is my work wasted for Java/Python/C++?**
A: The opposite. You contribute to the **World Model**, not to C#. Generation projects your domain into every target language automatically (Invariant 1). Modeling once benefits all languages.

**Q: Why not just let everyone subclass freely — isn't that what OOP is for?**
A: Deep, essence-confusing inheritance is the classic failure mode of large OOP systems. WMOOP reserves inheritance for stable, Liskov-safe `is-a-kind-of`, and uses **composition and roles** for everything else — which is exactly why `Driver` is a role on `Person`, not `Driver : Person` (Invariant 3, §3.4, §C).

**Q: Two experts disagree on how to classify something. Who wins?**
A: Neither "wins" by assertion. Contested classification is modeled with **categories/tags/multiple-parent relations**, and disputes are resolved by **citation** under a documented process (§6, §G), not by opinion.

**Q: Can an AI contribute? Won't it flood the repo with plausible nonsense?**
A: AI can contribute, under the **same machine-checkable Definition of Done** as humans **plus** required source provenance and **mandatory human review** (§E). We track not just acceptance but the **defect rate** of merged AI PRs (M6), so quality is monitored and policy can tighten.

**Q: How could a professor use this?**
A: Assign each student a domain they care about (landforms, countries, instruments, animal families). The student models it in the WM, cites sources, and passes CI — learning OOP, knowledge engineering, and sourcing at once, while adding real, reusable structure. See §1.2, roadmap v1.2.

**Q: Do I have to provide instances (L2)?**
A: No. L2 is optional. A domain is useful with classes and roles alone; instances (e.g. the planets) are added separately, and are themselves cited (§3.2, §I).

**Q: What stops the whole thing from ballooning uncontrollably?**
A: Domains are **opt-in and require a maintainer and sources**; depth is pursued only where demanded; quality metrics are paired with growth metrics so shallow bulk cannot score as progress (§4.1, §6).

**Q: What's the license?**
A: Code is **Apache-2.0**. The documentation and model are **CC-BY-4.0** (chosen).

**Q: Where do I start?**
A: Read §M (meta-model) and §D (domain authoring guide), pick a "good first domain," and follow the contribution manual (§E). The v0 bootstrap slice (Person + Vehicle → Driver role) is the worked reference example.

---

## 9. Back matter

**How to cite.** Cite the versioned `wmoop.doc` release (e.g. "WMOOP World Model, v*X.Y*, github.com/WMOOP/wmoop.doc"). Each ratified release is citable.

**How to contribute.** See the contribution and ethics manual (§E) and the domain authoring guide (§D). Every contribution must pass the machine-checkable Definition of Done (§V): stable ID, name, definition, provenance, units for quantities, acyclic dependencies, and Liskov-safe inheritance.

**Document conventions.** The key words MUST, MUST NOT, SHOULD, and MAY in the normative sections are to be read as requirement levels. The eight invariants in §3.1 are normative and take precedence over any conflicting prose.

**References.** *(To be assembled with the detailed sections — prior-art families surveyed in §1.3: general knowledge graphs, formal/upper ontologies, web schema vocabularies, and per-language standard libraries. Full bibliography lives alongside §M.)*