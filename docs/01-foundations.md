# 2. Foundations and Related Work

> **Purpose.** WMOOP is not the first attempt to describe the world formally. Biologists, chemists, geographers, musicologists, lexicographers, philosophers and software engineers have each built large, maintained, machine-readable models of their slice of reality. This section surveys that prior art across five families, compares the approaches critically, and distils each into an explicit **Lesson for WMOOP**. The lessons are then consolidated into the design principles we adopt and the anti-patterns we forbid. Throughout, we tie findings back to the project's **Core Architectural Invariants** (referenced as *Invariant 1–6*).
>
> The single most consequential finding, which organises everything that follows, is this: **the "is-a" of ordinary thought and of biology is not the "is-a" of an OOP class hierarchy.** Decades of ontology engineering exist largely because that confusion is expensive. WMOOP must get it right once, in the canonical World Model (WM), so that it never has to be re-litigated in five target languages.

---

## 2.1 Taxonomy vs. Ontology vs. OOP Class Model

Three artifacts are routinely conflated because they all draw boxes connected by arrows. They are not the same thing, and WMOOP needs all three *as distinct layers*.

| Dimension | **Taxonomy** | **Ontology** | **OOP class model** |
|---|---|---|---|
| Primary purpose | Classify / browse | Specify meaning for machines & people | Organise executable code & state |
| Core primitive | Category in a tree | Concept + typed relations + axioms | Class with fields + methods |
| Meaning of "is-a" | Subsumption (kind-of) | Subsumption, *axiomatised* | Subtyping (behavioural substitutability) + implementation reuse |
| Multiple parents | Common (polyhierarchy) | Common and principled | Rare, dangerous (diamond, state) |
| Instances | Usually out of scope | First-class (A-Box) | Objects at runtime |
| Behaviour | None | Optional (rules) | Central (dispatch, mutation) |
| Governing discipline | Editorial | Logic / model theory | Type system / LSP |
| Formal check | Tree well-formedness | Consistency, satisfiability (reasoner) | Compilation, tests |

**Why "is-a" overloading is the root problem.** Brachman's classic *"What IS-A Is and Isn't"* (1983) showed that a single network link labelled "is-a" is routinely used for at least four incompatible relations:

1. **Subsumption** — *Moped* is a kind of *AutoVehicle*. (concept → concept)
2. **Instantiation** — *Earth* is an instance of *Planet*. (individual → concept)
3. **Subtyping / substitutability** — any *Square* can stand in for a *Rectangle* **only if every operation valid on a Rectangle is valid on a Square** (Liskov Substitution Principle, 1987/1994). This is a *behavioural* claim, not a classificatory one.
4. **Part-of / role-of / attribute-of** — a *wheel* is-a part of a *vehicle*; a *driver* is-a role a person plays. These are *not* subsumption at all.

A software `extends` keyword silently asserts **all four at once** (subsumption + a subtype obligation + state/behaviour inheritance). The world's taxonomies assert only #1 and #2 — and frequently violate #3.

**The single-inheritance limitation and the multiple-classification problem.** Mainstream OOP languages (C#, Java) allow exactly one superclass. The world does not cooperate:

- A **tomato** is a *fruit* (botany) and a *vegetable* (cuisine). The classification depends on the *perspective*, not the object.
- A **penguin** is-a *Bird* but cannot *Fly*; a **whale** is-a *Mammal* but lives in water and has no legs — so `Bird.Fly()` and `Mammal.legCount = 4` as inherited defaults are *false for subtypes*, i.e. LSP violations waiting to happen.
- A **person** is simultaneously an *Employee*, a *Driver*, a *Patient*, a *Taxpayer* — each a different perspective requiring different data, none essential to being a person.

Forcing these into a single inheritance tree produces exactly the pathologies this project exists to avoid: `Driver : Person`, `TomatoFruit` vs `TomatoVegetable` duplicate classes, or God base classes stuffed with every possible attribute.

> **Lesson 2.1 for WMOOP.** Keep the three artifacts *separate and layered* (this is Invariant 2: L0 meta-model / L1 domain model / L2 instances). In the WM, **never express a single undifferentiated `is-a`.** Provide distinct, named relation types — `subclass_of`, `instance_of`, `part_of`, `has_role`, `has_quality`, `classified_as` (perspectival tag) — so that generation can map each to the *correct* target-language construct (inheritance, object instantiation, composition field, trait, enum/attribute). Reserve true inheritance for rigid subsumption that also satisfies LSP, and model everything else by composition and relations (Invariant 3).

---

## 2.2 Upper Ontologies: the foundational categories

Upper (or *foundational*) ontologies define the small set of top-level categories under which every domain concept must fall. They are the field's answer to the question *"what kinds of thing are there, before we talk about any particular subject?"* — precisely what WMOOP's L0 meta-model must answer.

**BFO (Basic Formal Ontology; Smith, Grenon, Arp).** Small, realist, deliberately austere; the reference upper ontology for the OBO Foundry (§2.4) and an ISO/IEC standard (21838-2). Its master split is **continuant vs. occurrent**:

- **Continuant** — persists through time, wholly present at each moment. Subdivided into:
  - *Independent continuant* — **object** (a car, a cell), object aggregate, fiat object part (e.g., the northern hemisphere).
  - *Specifically dependent continuant* — a **quality** (mass, colour), or a **realizable entity**: **role**, **disposition**, **function**. A *role* is externally grounded and **optional** — a person has the *driver* role only in a context, and can lose it. This is BFO's formalisation of exactly the Person-as-Driver case.
  - *Generically dependent continuant* — **information artifacts** (a design, a model, a musical score) that can be copied across bearers.
- **Occurrent** — unfolds in time (a **process**, a process boundary, temporal and spatiotemporal regions).

**DOLCE (Descriptive Ontology for Linguistic and Cognitive Engineering; Gangemi, Guarino, Masolo, Oltramari, Borgo).** *Descriptive* (tracks human cognition and language) rather than realist. Master split **endurant vs. perdurant** (its 3D analogue of continuant/occurrent), plus a rich treatment of **qualities** and **quality spaces**: a quality (e.g., *the mass of this car*) takes a value (a *quale*) in a *quality region* (e.g., a point on the mass scale, **with a unit**). This is directly the machinery WMOOP needs for Invariant 4 (quantities carry units).

**SUMO (Suggested Upper Merged Ontology; Niles & Pease).** Large, pragmatic, written in SUO-KIF, mapped comprehensively to WordNet, and shipped with mid-level and domain ontologies. Demonstrates an upper→mid→domain layering and the value of linking the formal model to natural-language lexemes.

**GFO (General Formal Ontology; Herre et al., Leipzig).** Explicitly *multi-layered* and supports **both 3D and 4D** perspectives. Notably distinguishes **universals, concepts, and symbols** (the thing, the mental category, and the name for it) — a three-way separation WMOOP should echo (concept vs. label vs. identifier).

**Cyc (Lenat et al.).** The largest hand-built common-sense KB. Its enduring contribution for us is **microtheories**: assertions are true *within a context*, and contradictory assertions can coexist in different contexts. Cyc is also a cautionary tale: decades of manual curation at enormous cost and limited openness. The lesson is to adopt *contextualisation* without inheriting *manual-only* curation.

**What to borrow — a concrete L0 proposal.** WMOOP does not need to pick one upper ontology wholesale (over-committing philosophically is itself an anti-pattern — keep L0 *small and fixed*, Invariant 2). It should adopt a **minimal, fixed set of foundational categories**, informed primarily by BFO, with DOLCE's quality-space treatment of quantities:

| WMOOP L0 category (proposed) | Borrowed from | Role in the model |
|---|---|---|
| `Object` (independent continuant) | BFO independent continuant | The default home of "things": Vehicle, Animal, Planet, Instrument |
| `Quality` (+ value in a quality space w/ unit) | BFO quality / DOLCE quale | Measurable/observable attributes: mass, wheelCount, tempo |
| `Role` (realizable, external, anti-rigid) | BFO role / OntoClean | Driver, Employee, Patient — attached, never inherited |
| `Disposition` / `Capability` | BFO disposition/function | CanFly, IsSoluble — a capability a thing may bear |
| `Process` (occurrent) | BFO occurrent / DOLCE perdurant | Combustion, Photosynthesis, Performance (optional in v1) |
| `InformationArtifact` (generically dependent) | BFO GDC | A score, a schema, a definition — copyable across bearers |

**OntoClean — the single most useful tool in this subsection.** Guarino & Welty's **OntoClean** methodology supplies *meta-properties* that make inheritance discipline *mechanical and checkable* (Invariant 6), rather than a matter of taste:

- **Rigidity (±R):** a property is **rigid (+R)** if it holds *necessarily* for every instance that has it (if *x* is a *Person*, *x* is *always* a Person); **anti-rigid (~R)** if any instance could lose it while continuing to exist (*Student*, *Driver*, *Caterpillar-vs-Butterfly stage*).
- **Identity (±I):** does the property carry a criterion for telling two instances apart / tracking one over time?
- **Unity (±U):** are instances wholes under a defining relation?
- **Dependence:** do instances depend on another entity to exist?

The key **constraint**: an **anti-rigid property cannot subsume a rigid one.** Therefore `Person : Student` and — critically for this project — `Person : Driver` are *formally* invalid, because *Driver* is anti-rigid and externally dependent while *Person* is rigid. This is the rigorous justification for Invariant 3.

> **Lesson 2.2 for WMOOP.** Adopt a **small fixed L0** of foundational categories (table above) rather than a sprawling philosophy. Treat **Role, Disposition/Capability, and Quality as first-class, non-inheritance constructs**. Encode **OntoClean meta-properties (rigidity, identity, unity) as required metadata on every L1 concept**, and have CI enforce the rule *"anti-rigid may not be a superclass of rigid"* — this turns "roles over inheritance" from advice into an automated gate. Use Cyc-style **microtheories/contexts** for contested classification (the tomato), implemented as perspectival tags rather than parallel classes.

---

## 2.3 Large Practical Knowledge Bases

These are the web-scale proofs that structured world-modelling *works operationally*. Their data-modelling choices are battle-tested.

**Wikidata (Vrandečić & Krötzsch).** The reference implementation of almost everything WMOOP wants:
- **Opaque, stable, global IDs**: items are `Q…` (Earth = `Q2`), properties are `P…`. IDs are *language-independent integers*; labels, descriptions and aliases exist per-language on top. Identity is decoupled from name.
- **Properties are first-class, versioned, documented entities** — not strings. A relation like *instance of* (`P31`) or *subclass of* (`P279`) is itself a curated item.
- **Statements, not triples**: each statement is *property → value* plus **qualifiers** (temporal/contextual scope), **references** (provenance), and a **rank** (preferred / normal / deprecated). Contradictory sourced claims can coexist, ranked.
- **Lexemes** handle lexicographic data separately from concepts.

**DBpedia.** Extracts structured data from Wikipedia infoboxes into the **DBpedia Ontology** via community **mappings**. Lesson: a curated *mapping layer* can harvest existing, messy, human-authored knowledge into a clean model — relevant to WMOOP's "import from Wikidata/authoritative sources" strategy.

**Schema.org (Google/Bing/Yahoo/Yandex).** Deliberately *lightweight and pragmatic*. Two features matter:
- **Multi-typing**: an entity can have several types at once (a *LocalBusiness* that is also a *Restaurant*) — multiple classification without multiple inheritance of state.
- **Soft typing**: `domainIncludes` / `rangeIncludes` express *expectations*, not hard constraints. This "good enough, extensible" stance is why Schema.org achieved mass adoption where heavier ontologies did not.

**WordNet (Miller, Fellbaum).** A *lexical* database whose unit is the **synset** — a set of synonymous words denoting *one concept*. Relations: **hypernym/hyponym** (is-a), **meronym/holonym** (part-of), **antonym**, **troponym** (verbs). Crucial structural lesson: **a concept (synset) is distinct from the words that name it.** The concept is identified by an offset/ID; many words in many languages point to it. This is precisely GFO's universal-vs-symbol split and the pattern WMOOP's IDs must follow.

**ConceptNet (Speer et al.).** A multilingual semantic network of *common-sense* relations drawn from many sources: `IsA`, `PartOf`, `UsedFor`, `CapableOf`, `HasProperty`, `AtLocation`, etc. Edges carry **weights** (confidence) and **sources**. Lesson: the world needs **many typed relations beyond is-a**, each edge carrying confidence and provenance.

> **Lesson 2.3 for WMOOP.** (1) Use **opaque, stable, global IDs** (e.g., `WM:Q…`/`WM:C…` for concepts, `WM:P…` for properties) that are **decoupled from human names and from any language** — labels are multilingual annotations (Invariant 4's "human name" is metadata, not identity). (2) Make **properties/relations first-class, documented, versioned WM entities**, not bare strings. (3) Model every fact as a **statement with provenance (references) and context (qualifiers)**, and adopt a **rank/deprecation** mechanism so contradictory sourced claims and corrections are first-class — this operationalises Invariant 4. (4) Allow **multiple classification via multi-typing/tags** (Schema.org) rather than multiple inheritance. (5) Keep the *default* typing stance pragmatic and extensible; reserve hard constraints for where they earn their cost.

---

## 2.4 Domain Datasets That Prove the Approach Scales

The skeptic's fair question — *"does declarative, language-neutral, composition-first world-modelling actually scale to millions of real concepts?"* — is answered by existing production datasets.

**Gene Ontology (GO; Ashburner et al.) and the OBO Foundry.** GO models gene function in **three orthogonal sub-ontologies** (molecular function, biological process, cellular component), in the OBO format, using a **shared relation set** (`is_a`, `part_of`, `regulates`, `has_part`) defined once in the **Relation Ontology (RO)**. It scales to tens of thousands of terms and millions of annotations, each annotation tagged with an **evidence code** (provenance of the assertion). Logical **cross-products** define GO terms by composition with *other* ontologies (e.g., a process acting on a ChEBI chemical) — reuse instead of duplication. Governing it, the **OBO Foundry principles** are effectively a ready-made constitution for WMOOP:
- **Orthogonality** — each entity is defined in exactly **one** ontology; others reuse it (single source of truth, Invariant 1).
- **Shared relations** (RO) — a common relation vocabulary across domains (Invariant 3/5).
- **Common format, open licence, versioning, documented, reviewed** — governance (Invariant 6).

**NCBI Taxonomy / GBIF / Darwin Core / Wikispecies (biology classification).** Instructive precisely because biological classification is *contested and revised*:
- **NCBI Taxonomy** is an openly *pragmatic*, operational classification (ranks as scaffolding) — explicitly *not* a claim of phylogenetic truth.
- **GBIF Backbone Taxonomy** *reconciles many conflicting source checklists* into one backbone, handling **synonyms** and alternative classifications rather than forcing one tree.
- **Darwin Core (TDWG)** is a *shared vocabulary of standard terms* for biodiversity records — a common schema everyone maps to.
- **Wikispecies** is the wiki-curated, community directory.

**ChEBI (Chemical Entities of Biological Interest).** The textbook demonstration of **structure vs. role separation**: ChEBI maintains a **structural** classification (`is_a` by chemistry) *and a separate* **role** classification (`has_role`: *solvent*, *antioxidant*, *drug*). The *same* molecule is a subclass (by structure) and bears several roles (by use). This is Invariant 3 proven in production chemistry.

**Periodic-table datasets (PubChem, Wikidata, open CSV/JSON sets).** Elements keyed by **atomic number as a stable ID**, with sourced quantitative properties (mass, electronegativity) **carrying units**, plus isotopes. A clean model of **L2 reference instances** with sourced, unit-bearing quantities.

**QUDT and UCUM (units).** **QUDT** models *quantity kinds*, *units*, and *dimension vectors* with conversion factors; **UCUM** is a machine-parseable grammar of unit codes (`kg`, `m/s2`, `Cel`). Together they enforce that *a number is never stored bare*. Dimensional consistency becomes a checkable property.

**FOAF (Friend of a Friend).** A tiny, hugely reused vocabulary for **people** and their relationships (`Person`, `name`, `knows`, `mbox`). Demonstrates that **Person is a cross-cutting entity reused across domains** — exactly WMOOP's Person-in-Nature reused as a Driver facet in Transport.

**GeoNames / ISO 3166 / OpenStreetMap (geography).** A spectrum of governance:
- **ISO 3166** — the gold standard for **stable, governed, versioned identifiers** of real-world entities (country codes with a documented change process, reserved and transitional codes). Ideal model for L2 reference-data IDs.
- **GeoNames** — stable `geonameId`s, feature codes, hierarchy.
- **OpenStreetMap** — a **free-tagging folksonomy** (`key=value`), maximally open, community tag-wiki governed. Its cautionary lesson: without curation, tags fragment and duplicate.

**MusicBrainz / Music Ontology (music).** **MBIDs** are stable UUIDs for artists, works, recordings and releases; the community edits with **voting/review**. The **Music Ontology** adopts FRBR-style layering (abstract **Work** → **Expression** → concrete **Manifestation**), which maps naturally onto WMOOP's L1-concept-vs-L2-instance distinction and models events/performances as processes.

| Dataset (domain) | Scale evidence | Stable IDs | Provenance | Units | Multiple / role classification | Governance | Primary pattern WMOOP steals |
|---|---|---|---|---|---|---|---|
| **GO / OBO Foundry** (biology) | 10⁴ terms, 10⁶+ annotations | Yes (`GO:…`) | Evidence codes | n/a | `has_part`, cross-products | Orthogonality + shared RO + review | **Orthogonal single-source domains; shared relation vocabulary** |
| **GBIF / Darwin Core** (biology) | Global species backbone | Yes | Source checklists | n/a | Synonyms, reconciled trees | Backbone reconciliation | **Reconcile many source taxonomies; synonyms, not duplicate classes** |
| **ChEBI** (chemistry) | 10⁵ entities | Yes (`CHEBI:…`) | Curated refs | n/a | **Structure vs. role split** | OBO | **Role classification separate from structural is-a** |
| **Periodic table** | 118 + isotopes | Atomic number | Sourced | **Yes** | n/a | Authoritative | **L2 reference instances with unit-bearing quantities** |
| **QUDT / UCUM** (units) | All SI + derived | Yes | Standards | **The point** | n/a | Standards body | **Value = magnitude + unit + quantity kind; dimensional checks** |
| **FOAF** (people) | Web-scale reuse | IRIs | — | — | People reused everywhere | W3C-adjacent | **Shared cross-domain Person vocabulary** |
| **ISO 3166** (geo) | ~250 countries | **Governed codes** | Official | — | — | **Documented change process** | **Stable, versioned, governed identifiers** |
| **OpenStreetMap** (geo) | Planet-scale | `node/way` ids | Changesets | partial | Free tags | Folksonomy + tag wiki | **Openness — with the cautionary need for curation** |
| **MusicBrainz / Music Ontology** | 10⁷ entities | **MBID (UUID)** | Edit history | — | FRBR layering | **Community voting/review** | **UUID IDs + community review + Work/Manifestation layering** |

> **Lesson 2.4 for WMOOP.** Scale is a *governance* problem, and the solution is already proven: adopt **OBO-Foundry-style orthogonality** (each concept defined once; others reuse) with a **shared relation vocabulary** and an **explicit acyclic domain-dependency graph** (Invariant 5). Separate **structural is-a from role classification** everywhere (ChEBI), reconcile competing classifications with **synonyms and backbone reconciliation** rather than duplicate classes (GBIF), attach **units via QUDT/UCUM to every quantity** (Invariant 4), use **governed stable IDs with a documented change process** for L2 reference data (ISO 3166 / MBID), and pair **openness with curation/review** (MusicBrainz, not raw OSM). Treat **Person/Place/Organisation as shared cross-domain concepts** (FOAF), realising the Person↔Driver cross-domain link as a declared, versioned relation (Invariant 5).

---

## 2.5 Software-Side Prior Art

The world model is only valuable if it generates *idiomatic* code in each language. Software engineering supplies both the generation machinery and the composition patterns.

**Entity-Component-System (ECS).** Games and simulations abandoned deep inheritance for ECS: an **Entity** is a bare ID; **Components** are plain data attached to it; **Systems** are behaviour that operates over entities having given components. Capabilities are *added by attaching components*, not by subclassing. ECS is the purest industrial expression of **composition over inheritance** and maps almost one-to-one onto WMOOP's Role/Capability model: *Driver* is a component you attach to a *Person* entity.

**Domain-Driven Design (DDD; Evans).** Supplies the vocabulary for Invariant 5:
- **Bounded Context** — an explicit boundary within which a model (and a term) has one precise meaning. *The same word means different things in different contexts* (a "Book" in a sales context vs. a shipping context). This is WMOOP's **domain module**, and the formal basis for the tomato/microtheory problem.
- **Ubiquitous Language** — one agreed vocabulary per context.
- **Entities / Value Objects / Aggregates** — identity-bearing things vs. immutable value types (WMOOP quantities are value objects).
- **Context Mapping** (shared kernel, published language, anticorruption layer) — the *declared, versioned* way two contexts relate. The Person↔Driver link is a **shared kernel / context map**, not an inheritance edge.

**Mixins / Traits / Interfaces with defaults.** Rust **traits**, Scala **traits**, Ruby **mixins**, C++ **concepts**/CRTP, Java/C# **interfaces with default methods**. These provide *horizontal* composition of contract-and-behaviour independent of the inheritance axis. They are the **generation target for WMOOP Roles and Capabilities**: a WM `Role` becomes a trait/interface in each language, keeping output idiomatic rather than forcing a base class.

**Protobuf / IDL + code generation.** Protocol Buffers, Thrift, Cap'n Proto, FlatBuffers, ASN.1, Avro and OpenAPI are the **existence proof of Invariant 1**: a *single declarative schema* generates correct, idiomatic code in many languages, with *no hand-maintained parallel copies*. They also contribute hard-won **schema-evolution discipline** WMOOP must copy: **stable field numbers/identifiers**, **reserved** (never-reuse) tags, explicit **backward/forward-compatibility rules**, and (Avro/schema registries) **compatibility checking in CI**. "Write once, replicate everywhere" is *mechanical*, and these tools show exactly how to keep it safe over time.

**JSON Schema.** Declarative validation with `$ref`/`$defs` reuse, stable `$id`, and composition keywords — `allOf` / `anyOf` / `oneOf` / `not` and `if`/`then`/`else`. The composition keywords are a natural encoding of **multi-classification and role attachment** ("an entity that is `allOf` [Object] and bears `anyOf` [these roles]"), and give WMOOP a **machine-checkable Definition of Done** for the WM (Invariant 6).

**OWL / RDF / SHACL.** The W3C semantic-web stack: **RDF** triples over **IRIs**, **RDFS/OWL** class and property axioms, **Description Logic** reasoners (automatic classification, consistency checking, satisfiability), and **SHACL** for shape/constraint validation. WMOOP should borrow the **formal relation semantics and optional reasoning** for *validating the model*. But there is a **critical semantic caveat**: OWL assumes the **Open-World Assumption (OWA)** and **no Unique Name Assumption** (absence of a fact ≠ its falsehood; two IDs may denote the same thing unless stated otherwise). OOP code assumes the **Closed-World Assumption** and unique names. Mixing them silently produces subtle bugs (e.g., a reasoner "completing" a class you expected to be exhaustive).

> **Lesson 2.5 for WMOOP.** (1) Model the WM as a **declarative schema and generate** per-language code; adopt Protobuf/Avro-grade **schema-evolution rules** — stable identifiers, reserved IDs, CI compatibility gates (Invariant 1). (2) Generate **concepts → classes**, **rigid is-a → (shallow) inheritance**, and **Roles/Capabilities → traits/interfaces/components** so output is idiomatic in each language (Invariant 3). (3) Use **ECS-style composition** as the mental model for attaching roles and facets. (4) Treat **domains as DDD bounded contexts** with **explicit, versioned context maps** for cross-domain links (Invariants 5, 3); the Person-as-Driver case is a context map, not a subclass. (5) Validate the WM with **JSON Schema/SHACL (closed-world) as the generation contract and automated DoD** (Invariant 6), and use **OWL reasoning optionally for consistency** — but **declare an explicit CWA↔OWA bridge policy** so model-level reasoning and generated-code semantics never silently disagree.

---

## 2.6 Synthesis — Principles to Adopt and Anti-Patterns to Avoid

### Design principles WMOOP adopts

| # | Principle | Evidence | Invariant |
|---|---|---|---|
| P1 | **Three separated layers**: concept/ID ≠ schema/model ≠ instances. | WordNet, Wikidata, DDD | 2 |
| P2 | **Opaque, stable, global, language-neutral IDs**; names are multilingual metadata. | Wikidata QIDs, MBID, ISO 3166, WordNet synsets | 4 |
| P3 | **Properties and relations are first-class, documented, versioned entities** with a **shared relation vocabulary**. | Wikidata P-IDs, OBO RO | 3, 5 |
| P4 | **Every fact is sourced; every quantity carries a unit and quantity kind.** Statements support qualifiers, references, and deprecation/rank. | GO evidence codes, Wikidata refs, QUDT/UCUM | 4 |
| P5 | **Roles, Capabilities and Qualities are composition constructs**, externally grounded and anti-rigid — never inheritance. | BFO roles, OntoClean, ChEBI `has_role`, ECS, traits | 3 |
| P6 | **Inheritance is shallow and reserved for rigid is-a that satisfies LSP**, validated by OntoClean meta-properties in CI. | OntoClean, Liskov | 3, 6 |
| P7 | **Multiple / contested classification via tags, multi-typing and reconciliation**, not multiple inheritance. | Schema.org multi-type, GBIF, Cyc microtheories | 3 |
| P8 | **Orthogonal, single-source domains** with an **explicit acyclic dependency graph** and declared, versioned cross-domain links. | OBO Foundry, DDD context maps | 1, 5 |
| P9 | **Schema-first + codegen** with Protobuf/Avro-grade evolution rules (stable IDs, reserved, CI compat). | Protobuf, Avro, Thrift | 1 |
| P10 | **Everything machine-checkable**: JSON Schema/SHACL as the generation contract + optional OWL reasoning, giving an automated Definition of Done. | JSON Schema, SHACL, OWL reasoners | 6 |
| P11 | **Contextualisation** for perspective-dependent truth (bounded contexts / microtheories). | Cyc, DDD | 3, 5 |
| P12 | **Open, versioned, review-based governance** pairing openness with curation. | Wikidata, MusicBrainz, OBO Foundry | 6 |

### Anti-patterns WMOOP forbids

| # | Anti-pattern | Why it fails | Prevented by |
|---|---|---|---|
| A1 | Treating one undifferentiated `is-a` as subsumption + subtyping + reuse at once. | Conflates four distinct relations (Brachman). | P1, P3 |
| A2 | **`Driver : Person`, `Student : Person`, `Employee : Person`** — roles as subclasses. | Anti-rigid cannot subsume rigid (OntoClean); breaks LSP. | P5, P6 |
| A3 | Deep inheritance trees and **God base classes** stuffed with every attribute to force reuse. | Fragile, non-idiomatic, LSP violations (penguin/whale). | P5, P6 |
| A4 | **Multiple inheritance of state** to encode multi-classification (tomato as fruit *and* vegetable). | Diamond problem; perspective is not structure. | P7, P11 |
| A5 | Baking the **English label into identity** (names/keys as IDs). | Breaks multilinguality, renames, merges. | P2 |
| A6 | **Bare numbers** without unit, dimension, or quantity kind. | Undetectable unit errors; no dimensional checks. | P4 |
| A7 | **Unsourced assertions** with no provenance or correction mechanism. | Not scientific; cannot adjudicate conflicts. | P4, P12 |
| A8 | One **monolithic ontology** and/or **cyclic domain dependencies**. | Unscalable, unversionable, un-reviewable. | P8 |
| A9 | **Hand-maintaining parallel per-language copies** of the model. | Drift, duplication — the exact problem WMOOP exists to kill. | P9 |
| A10 | Importing **OWL/OWA facts into CWA code** (or vice versa) with no explicit bridge. | Silent semantic mismatch, false completeness. | P10 |
| A11 | **Uncurated folksonomy** (raw OSM-style free tags) as the vocabulary. | Tag explosion, duplicates, no interoperability. | P3, P12 |
| A12 | **Over-engineering L0** — committing to a large, contested upper ontology up front. | Paralysis; philosophy over delivery. | Keep L0 small/fixed (Invariant 2) |

---

## 2.7 How this positions WMOOP

No existing system does *all* of what WMOOP proposes: upper ontologies formalise categories but do not generate idiomatic OOP in five languages; IDLs generate code beautifully but model only data structures, with no ontological discipline, roles, or provenance; knowledge bases capture world facts richly but target reasoning, not clean generated class libraries; domain datasets prove scale but each within one subject. **WMOOP's contribution is the synthesis**: an ontology-first canonical World Model (borrowing BFO's categories, OntoClean's rigor, Wikidata's ID/provenance model, OBO's orthogonal governance, QUDT/UCUM's units) that is *also* a code-generation source (borrowing Protobuf's codegen and evolution discipline, DDD's bounded contexts, and ECS/traits' composition), yielding idiomatic, conformance-tested OOP libraries across languages with zero duplication of the conceptual model — explicitly so that humans *and* AI can contribute against an automated Definition of Done.

*Indicative references: Gruber (1993) on ontologies; Brachman (1983) on IS-A; Liskov & Wing (1994) on substitutability; Guarino & Welty (OntoClean); Arp, Smith & Spear (BFO); Masolo, Borgo, Gangemi, Guarino, Oltramari (DOLCE); Niles & Pease (SUMO); Herre (GFO); Lenat (Cyc); Vrandečić & Krötzsch (Wikidata); Miller/Fellbaum (WordNet); Speer et al. (ConceptNet); Ashburner et al. (Gene Ontology) and the OBO Foundry principles; Hastings et al. (ChEBI); the QUDT and UCUM specifications; Brickley & Miller (FOAF); the ISO 3166 standard; Raimond et al. (Music Ontology); Evans (Domain-Driven Design); the Protocol Buffers, JSON Schema, OWL 2 and SHACL specifications.*