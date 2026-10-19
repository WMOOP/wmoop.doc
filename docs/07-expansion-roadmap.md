# The Expansion Roadmap — how WMOOP grows toward covering the world

> **Document role.** The World Domain Map ([`06-domain-taxonomy.md`](06-domain-taxonomy.md)) says
> *what* the domains are. This document says *how the model grows* across them over time: the
> philosophical footing for cutting the world into domains at all, the thesis that the model is never
> "finished", the criteria for choosing what to model next, a sequenced set of **waves**, and a
> reusable **domain brief** so any contributor can pick up a domain and make it tractable.
>
> **Status:** Draft for ratification (v0). It is a *plan*, not a promise: every candidate domain stays
> **opt-in and maintainer-gated** (see [`05-adversarial-review.md`](05-adversarial-review.md),
> *scope explosion*). Nothing here adds a domain to `model/` on its own.

---

## 1. The thesis: a model that never "finishes"

The mission is to describe the world — "all the knowledge discovered by humankind" — in one shared,
object-oriented model. Taken literally that is unbounded, and a naive reading ("model everything")
is exactly the failure mode the [adversarial review](05-adversarial-review.md) warns about. WMOOP's
answer is not to finish the world but to make the model **monotonically extensible**:

- **Growth is addition on an acyclic graph.** A new domain is a new versioned module that *depends
  on* existing ones and **adds** concepts, roles, relations and L2 facts. It never re-opens or forks
  a published base (Open/Closed at the package boundary —
  [`03-architecture.md` §4.5](03-architecture.md#45-package-independence-and-extension-by-addition)).
  So the model can grow forever without the earlier parts rotting.
- **"Done" is per-contribution, not per-world.** The Definition of Done
  ([`CONTRIBUTING.md` §8](../CONTRIBUTING.md)) is machine-checkable for *one concept or a tight
  cluster*. Completeness of the *whole* is never required for progress of a *part*.
- **Depth on demand.** A domain is seeded shallow (the concepts that earn their place now) and
  deepened only when a real use, a source, and a steward exist. `nature.genetics` (cells, DNA) is the
  canonical "later, when needed" branch.

The right picture is not a finish line but a **frontier**: the acyclic dependency graph expands
outward, each new module resting on ones already proven.

---

## 2. Philosophical foundations — abstracting the world

To model the world you must first decide **what kinds of thing there are** and **where to cut**.
That is not a software question; it is the oldest question in philosophy (metaphysics and ontology),
and WMOOP's L0 is a deliberately small, engineering-grade answer to it. Recording this lineage is
itself Invariant 4 (*everything is sourced*) applied to the meta-model.

### 2.1 Carving nature at its joints

The guiding idea, from Plato's *Phaedrus*, is to divide reality "at its natural joints" rather than
by convenience. WMOOP operationalises it with three cuts the meta-model keeps sharp
([`02-meta-model.md`](02-meta-model.md)): **is-a vs part-of vs role**, the **endurant / perdurant /
abstract** modes of being, and **universal vs particular** (Type vs Individual). Most naive "model
the world in OOP" projects collapse these, and that is why they cannot hold a process, a number, or a
multiply-classified thing without lying.

### 2.2 Upper ontologies we triangulate

WMOOP's seven L0 categories are not invented; they are triangulated from the major **upper (foundational)
ontologies** and then constrained to the closed-world, single-inheritance OOP target.

| Upper ontology | Core idea WMOOP borrows | Lands in L0 as |
|---|---|---|
| **Aristotle's *Categories*** | substance vs the accidents said of it (quantity, quality, relation, place, time, …) | the split between a `Kind` (substance) and its qualities/quantities/relations |
| **BFO** (Basic Formal Ontology) | **continuant vs occurrent** (3-D object vs 4-D process); independent vs dependent continuants | `Endurant` vs `Perdurant`; `Quality` as a dependent continuant |
| **DOLCE** | endurant / perdurant / quality / abstract; a cognitive-bias-aware "ontology of particulars" | the A/B/C/D category backbone |
| **UFO** (Unified Foundational Ontology) | **rigidity & sortality**; *kind / subkind / phase / role / category* | WMOOP's authoring **stereotypes** and the roles-over-inheritance rule |
| **SUMO** | a large formal upper ontology, **physical vs abstract** at the top | the Natural ↔ Formal top-level split |
| **Cyc / OpenCyc** | a vast commonsense assertion base; collections vs individuals | the Type/Individual meta-axis; L2 reference individuals |

> **The one-line difference.** Those ontologies classify *reality* (or *documents/facts*). WMOOP
> classifies *things in order to generate typed code in many languages*, so it keeps only what a
> deterministic code generator can honour — and turns "roles over inheritance" from philosophy into a
> CI-checkable property (`02-meta-model.md` §7.3).

### 2.3 Aristotle's categories → L0 (worked mapping)

| Aristotle (*Categories*) | Example | WMOOP L0 |
|---|---|---|
| Substance (οὐσία) | a man, a horse | `Endurant` **Kind** |
| Quantity | two cubits long | `Quantity` (magnitude + unit) |
| Quality | white, literate | `Quality` |
| Relation | double, greater | `Relation` |
| Place / Time | in the Lyceum, yesterday | `Relation` to `geography`/a temporal interval |
| Doing / Being-affected | cutting, being burned | `Perdurant` (process) + its participant relations |

This is why L0 is adequate to the task: it is a modern, engineering-trimmed descendant of a 2,300-year-old
list that already separated a thing from what is *said of* it.

### 2.4 Modeling the abstract itself — the `philosophy` and `math` domains

"Abstracting the world" includes the **abstractions themselves**. Numbers, sets, theorems, concepts,
propositions and arguments are first-class `Abstract` entities (L0 category C) — things that would be
what they are "in a universe with no matter and no time" (`02-meta-model.md` §2.3). WMOOP therefore
treats the life of the mind as modellable domains, not as a special case:

- **`math`** — `Number`, `Set` (a Collection), `Group` (an `AbstractType` whose axioms are
  invariants), `Theorem` (with `provenFrom`/`impliedBy` relations).
- **`philosophy`** — `Concept`, `Proposition`, `Argument` (premises → conclusion as relations),
  `Category`, `PhilosophicalPosition` (with `disputed: true` + sources on each side, never a forced
  winner), and the **branches** themselves (metaphysics, epistemology, ethics, logic, aesthetics) as
  an organising taxonomy. This is the home for "concepts of abstracting the world": the model can
  describe *its own* categories as objects of study.
- **`language`** — `Phoneme`, `Morpheme`, `Grapheme`, `Word`, `GrammaticalCategory`: the abstract
  structures by which knowledge is even expressed.

Modelling these keeps WMOOP honest to its own slogan — a *map of the world* must include the maps,
the languages, and the ideas with which humans abstract that world.

---

## 3. How growth works (mechanics recap)

1. **Add a module, declare its edges.** A new domain declares `depends_on` on existing modules; CI
   keeps the graph acyclic (Invariant 5). Cross-domain facets attach as **roles** to existing
   concepts (the `Student`/`Teacher` roles on `nature/Person` are the template).
2. **Seed shallow, deepen on demand.** Ship the concepts with a real source and a use today; leave
   sub-domains as named-but-empty until someone needs them.
3. **One source of truth, generated views.** Every added concept becomes idiomatic C#/Java/Python/C++
   by generation, and its diagram cell by registry regeneration — never by hand (Invariant 1).
4. **Out-of-tree is first-class.** A domain WMOOP does not model canonically can be published by a
   third party against the public IDs (`03-architecture.md` §4.5), so the "world" can grow faster than
   the core governance can ratify.

---

## 4. Prioritization — what to model next

Candidate domains are scored on five axes (higher = sooner). This is a rubric for stewards, not an
algorithm.

| Axis | Question | Why it matters |
|---|---|---|
| **Dependency-readiness** | Are all `depends_on` modules already seeded? | You cannot reference a `Person` or a `Quantity` that does not resolve (DoD). |
| **Foundational leverage** | How many *other* domains are blocked on it? | `core` and `math` unblock almost everything; do them first. |
| **Source availability** | Is there an authoritative, resolvable standard/dataset? | No source → no model (AI_CONTRIBUTING §5). |
| **Pedagogical value** | Does it teach an L0 distinction cleanly? | WMOOP is also a teaching tool; `music` shows all three categories at once. |
| **Demand / sponsorship** | Is a steward or a consumer actually asking? | Mitigates scope explosion; keeps work reviewed. |

The hard gate underneath the rubric: **`core` must become a real module.** It is referenced
everywhere as `wmoop.core` (`Quantity`, units, `Count`, `Area`, base datatypes) but has no file yet;
until it exists, every other module's quantity/unit validation is unverifiable. It is Wave 0.

---

## 5. The waves (a sequenced plan)

A proposal, mapping the [registry](../model/taxonomy.yaml) candidates onto dependency-ordered waves.
Dates are intentionally omitted; a wave advances when its items meet the DoD, not a calendar.

- **Wave 0 — Foundation (unblocks everything).** `core` (realise L0: quantities, units, dimensions,
  provenance, identity). *Highest leverage; blocks all quantity/unit checks.*
- **Wave 1 — Seeded today (done or in hand).** `nature` (incl. **anatomy**), `geography`, `transport`,
  `org`, `architecture`, **`education`**. *The cross-domain role mechanism is proven here
  (Driver; Student/Teacher/FormTutor).*
- **Wave 2 — Formal & cultural spine.** `math` (number, set, algebra, geometry) → unblocks `music`
  (theory/instruments/performance) and `physics`; `language`; `philosophy` (the abstract-of-the-abstract).
- **Wave 3 — Physical world.** `physics` (mechanics first), `chemistry` (elements → compounds →
  reactions as perdurants), `earth`, `space` (the 8 planets as L2).
- **Wave 4 — Society & health.** `economy`, `law` (the `DrivingAuthorisation` that grounds the Driver
  role; `licences`), `politics`; `medicine` (builds on `nature.anatomy`, never copies it).
- **Wave 5+ — Breadth on demand.** `computing`, `software`, `tools`, `food`, `visualarts`,
  `literature`, `religion`, and whatever stewards bring — each a module on the frontier.

Each wave only ever **adds**; nothing above re-opens a module below it.

> **Near-term L0 addition (ADR 0001).** A first-class `Scheme` construct + enriched, dated, sourced
> `classifiedUnder` claims (on concepts, individuals and roles) is a planned **additive** L0 extension
> that realizes ETHICS §2.5 and resolves the D1 contradiction. Sequencing: the simple concept→class
> generator ships first (reference binding, constraints enforced, conformance green); the
> scheme-aware / depth-flattening projector is never on the v1 critical path. See
> [`../governance/adr/0001-classification-source-of-truth.md`](../governance/adr/0001-classification-source-of-truth.md).

---

## 6. The domain brief (make any domain tractable)

Before authoring a domain, a steward fills this one-page brief in the "new domain" issue
([`.github/ISSUE_TEMPLATE/new-domain.md`](../.github/ISSUE_TEMPLATE/new-domain.md)). It turns an
intimidating subject into a small, reviewable first PR.

```
Domain:            wmoop.<id>              (e.g. wmoop.music)
Cluster:           <foundation|formal|natural|place|society|culture|technology|health>
Depends on:        [core, ...]            (must be seeded; must stay acyclic)
One-sentence scope: what this domain is, and explicitly what it is NOT (its neighbours).
Seed concepts (<= 5 for the first PR), each with:
  - name + L0 stereotype (Kind / Subkind / Role / RelationType / QuantityKind / AbstractType / EventType / Collection / Category)
  - one-line own-words definition
  - the authoritative source (standard+clause / paper+DOI / dataset+URL+retrieved / textbook+ISBN+page)
Cross-domain roles/relations: which existing concepts do we attach to (by ID), and how?
L0 distinction showcased: which modelling point does this domain teach? (is-a vs part-of vs role; endurant/perdurant/abstract)
Known disputes/uncertainty: what is contested? (model both sides; do not pick a winner)
Out of scope / later: the sub-domains deliberately left as "depth on demand".
```

Then follow the [`wml-contribute`](../.claude/skills/wml-contribute/SKILL.md) loop and the
[`model/_template/DOMAIN_TEMPLATE.wml.yaml`](../model/_template/DOMAIN_TEMPLATE.wml.yaml) skeleton.

---

## 7. Honest limits

This roadmap does not repeal the [adversarial review](05-adversarial-review.md). The real risks stay
real: **scope explosion** (mitigated by opt-in, maintainer-gated candidates and the per-wave DoD),
**contested classification** (mitigated by `disputed`/alternative schemes, never a forced tree),
**the upper-ontology bet** (L0 is small and conservatively versioned precisely because getting it
wrong is expensive), and **sustaining stewardship** across many domains (the brief and the
machine-checkable DoD exist to keep review cheap). "Covering all knowledge" is a *direction*, not a
deliverable; the deliverable is always the next small, sourced, green contribution.

---

## 8. Sources

- Plato, *Phaedrus* 265e — "carving nature at its joints".
- Aristotle, *Categories* — the ten categories of being.
- Basic Formal Ontology (BFO 2.0 / ISO/IEC 21838-2): <https://basic-formal-ontology.org/>
- DOLCE (Descriptive Ontology for Linguistic and Cognitive Engineering): <https://www.loa.istc.cnr.it/dolce/overview.html>
- UFO (Unified Foundational Ontology) — Guizzardi, *Ontological Foundations for Structural Conceptual Models*, 2005.
- Suggested Upper Merged Ontology (SUMO): <https://www.ontologyportal.org/>
- Cyc / OpenCyc: <https://en.wikipedia.org/wiki/Cyc>
- WMOOP meta-model and taxonomy: [`02-meta-model.md`](02-meta-model.md), [`06-domain-taxonomy.md`](06-domain-taxonomy.md), [`../model/taxonomy.yaml`](../model/taxonomy.yaml).

*Upper ontologies are used as structural inspiration; WMOOP's cuts follow its own code-generation
rules. Per-concept provenance is recorded on each concept in its WML file (Invariant 4), not here.*
