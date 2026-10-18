# WMOOP Academic Program — Instructor & Curriculum Guide

> **Suggested location:** `wmoop.doc/academic/README.md` (course packs under `wmoop.doc/academic/courses/<lang>/`).
> **Status:** v1 draft, ready for review by the WMOOP steward council.
> **Tagline it serves:** *Describe World into OOP. Map all World Objects into Programming Languages.*

This guide lets an instructor use **WMOOP** (World Map Object-Oriented Programming) as graded coursework, especially in an **Object-Oriented Programming** or **Software Engineering** course. Students do not build throwaway toy programs; they contribute real, reviewed, machine-validated entries to a shared, language-neutral model of the world — and in doing so they practise exactly the judgement that distinguishes a good OO designer from a syntax-fluent beginner: *when is something an `is-a`, a `part-of`, or an `acts-as`?*

It is written to hold under scrutiny from both a software architect and a research scientist: concrete examples, decision rules, rubrics, and small worked snippets instead of hand-waving.

---

## 0. How to read this guide

| Section | Deliverable | For whom |
|---|---|---|
| §1 | Why WMOOP works as coursework | Instructors, curriculum committees |
| §2 | **Learning-outcome map** | Instructors, accreditation reviewers |
| §3 | **The three modelling decisions** (`is-a` / `part-of` / `acts-as`) | Instructors + students |
| §4 | **Assignment ladder A0–A6** | Students (briefs), instructors (setup) |
| §5 | **Rubrics** | Graders, TAs, peer reviewers |
| §6 | **Definition of Done & CI gates** | Everyone (the automated bar) |
| §7 | **Adopt a Domain** program | Cohorts, stewards, maintainers |
| §8 | **Instructor onboarding** + sample syllabus + AI policy | Instructors |
| §9 | **Localization** (e.g., Romanian) | Local universities |
| §10 | Appendices: templates, quick-reference card | Everyone |

**Alignment note.** This document assumes the eight *Core Architectural Invariants* and the WM (World Model) schema. Where it shows a file path (e.g. `*.concept.yaml`) or an ID form (e.g. `wmoop.nature.animals/Mammal`), the authoritative definitions live in the **WM Schema Specification** and **Authoring Guide**; this guide defers to them and only illustrates. The WMOOP identifiers and WML keywords shown throughout this guide (e.g. `wmoop.nature.animals/Mammal`, `extends`, `played_by`) illustrate the canonical forms defined in the **Normative Constants** table in GOVERNANCE.md. See §10 cross-references.

---

## 1. Why WMOOP works as coursework

Most OOP courses teach inheritance first and hardest, so students over-use it. The signature mistakes — `Driver : Person`, `Square : Rectangle`, `City : County` — come from treating inheritance as the default tool. WMOOP inverts the incentives:

1. **The hard part is modelling, not syntax.** The canonical model is language-neutral (Invariant 1), so students must decide *what the thing is* before writing any `class`. Judgement is the graded object.
2. **Mistakes are caught automatically.** Every contribution is validated in CI against a schema and conformance suite (Invariant 6). Students get a fast, objective, non-humiliating "not yet" from a machine before a human reviews taste.
3. **The work is real and durable.** A student's `Mountain` or `Moped` concept persists, is cited, and is reused across languages. This is intrinsically motivating and models professional open-source practice.
4. **It scales to any class size and interest.** A geography enthusiast models landforms; a musician models instruments; a biology double-major models cell organelles. The founder's "professor assigns a domain the student is passionate about" vision is the pedagogy.
5. **It teaches the limits of inheritance by construction.** Composition and roles are first-class in the model (Invariant 3), so students physically cannot smuggle a role into a base class without failing a lint rule.

---

## 2. Learning-outcome map (Deliverable a)

Each outcome is written as *"the student can…"* and tied to the WMOOP activity that develops it, the assignment(s) that assess it, and the Bloom level the assignment targets.

| # | Learning outcome (student can…) | What it means in WMOOP | Primary WMOOP activity | Assessed in | Bloom |
|---|---|---|---|---|---|
| LO-1 | **Abstraction** — find the essential, common properties and name the right level of generality | Define an abstract base concept (e.g. `Landform`, `Instrument`, `Vehicle`) carrying only shared, defensible properties | Author an abstract `kind: Class` concept with shared properties + definition | A1, A3, A6 | Analyze / Create |
| LO-2 | **Encapsulation** — expose intent, hide representation; enforce invariants | Model properties with types, units, allowed ranges/enums; keep derived facts derived | Declare typed properties with units + constraints; generated code exposes read-only/invariant-guarded members | A0, A3 | Apply |
| LO-3 | **Inheritance (and its limits)** — use `is-a` only for stable essence; keep it shallow; honour Liskov | Model genuine `extends` where every instance of the child is permanently a kind of the parent and is substitutable | Build a shallow subtype chain; justify each `extends`; add Liskov conformance cases | A1, A2 | Evaluate |
| LO-4 | **Polymorphism** — one interface, many behaviours | Abstract operations (`area()`, `perimeter()`, sound production) realised per subtype | Define polymorphic operations; generated code dispatches per type; tests assert behaviour | A0, A1 | Apply |
| LO-5 | **Interfaces / traits** — model capabilities orthogonal to the type hierarchy | Attach cross-cutting capabilities (`CanFly`, `IsTransposing`, `HasVertebralColumn`) as traits, not base classes | Declare `traits`; implement interfaces in generated code | A1, A2 | Analyze |
| LO-6 | **Composition / part-of** — model `has-a`/whole-part containment instead of inheritance | Model mereological structure (country **contains** counties) via a `partOf` relation | Build a recursive `partOf` structure with cardinalities; **no** inheritance | **A4** | Evaluate |
| LO-7 | **Roles / capabilities** — attach contextual, temporal, multiple facets by composition | A `Person` *acts as* `Driver`/`Student`/`Employee`; roles are attached, bounded, and plural | Author a `kind: Role` with `played_by`; compose onto a party; **never** subclass | **A5, A6** | Create |
| LO-8 | **Generics / parametric polymorphism** | Reusable role-holders, typed collections, `Quantity<Unit>` | Use a generic role registry / typed collections in generated code | A5, A6 | Apply |
| LO-9 | **SOLID** | SRP (one concept = one responsibility), OCP (extend by new subtypes/traits/roles, not edits), LSP (Liskov conformance), ISP (small traits), DIP (code depends on generated abstractions, not concretions) | Reviewed against SOLID checklist; OCP demonstrated by extension PRs | A2, A6 | Evaluate |
| LO-10 | **Ontology / modelling thinking** | Choose the right category, resist a single forced tree, use categories/tags for contested classification | Decide `is-a` vs `part-of` vs `acts-as`; handle multi-classification with categories | A3, A4, A5 | Create |
| LO-11 | **Unit & conformance testing** | Treat the model as code under test; prove Liskov & behaviour | Write/extend conformance cases; all pass in CI | A2, A6 | Apply |
| LO-12 | **Code review** | Give and receive precise, kind, evidence-based review | Review ≥1 peer PR per assignment; respond to review on own PR | A3–A6 | Evaluate |
| LO-13 | **Open-source collaboration** | Issues, branches, PRs, CODEOWNERS, versioning, provenance, steward etiquette | Contribute via PR to a stewarded domain; cite sources (Invariant 4) | A3–A6, §7 | Create |

> **Accreditation tip.** LO-1…LO-13 map cleanly onto ABET/EUR-ACE SE outcomes (design, teamwork, tooling, professional responsibility). The provenance requirement (LO-13 + Invariant 4) additionally satisfies "information literacy" outcomes rarely hit by programming courses.

---

## 3. The three modelling decisions (the spine of the program)

Before any assignment, teach this one decision. Every rubric and every brief refers back to it.

### 3.1 Decision card — `is-a` vs `part-of` vs `acts-as`

| | **Inheritance — `is-a-kind-of`** | **Composition — `part-of` / `has-a`** | **Role — `acts-as` / `plays`** |
|---|---|---|---|
| **Question** | Is *every* X permanently and essentially a kind of Y? | Is X built from / contained in Y as a component? | Can X take on Y in some context, maybe temporarily, maybe several at once? |
| **Substitutable?** (Liskov) | Yes — anywhere Y is expected, X works | No — a part is not the whole | No — a role is not the essence |
| **Can stop being true while the object lives?** | **No** → if it can, it is *not* inheritance | — | **Yes** — roles start and end |
| **Several at once?** | Rarely; avoid multiple inheritance | Many parts, yes | **Yes** — Driver *and* Employee *and* Student |
| **Modelled as** | `extends` (shallow) | `relation: partOf` (+ cardinality) | `kind: Role` + `played_by` (composition) |
| **Worked example** | `Mammal extends Vertebrate` | `City partOf County partOf Country` | `Person acts-as Driver` |

### 3.2 Litmus questions (apply in order)

1. **Would it ever stop being true while the object still exists?** → **Role.** (A person stops being a driver when the licence expires; they do not stop being a person.)
2. **Can one object be several of these simultaneously?** → **Role or trait**, not single inheritance.
3. **Is it a whole/part containment ("made of", "located in", "administered under")?** → **Composition (`partOf`).**
4. **Is it a genuine, permanent *kind-of* that is substitutable everywhere the parent is?** → **Inheritance** — and keep it shallow (aim ≤ 3–4 levels as a teaching heuristic; the CI gate is depth ≤ 6, warn at 5; respect Liskov).
5. **Is the classification contested or multi-axis?** (A fjord is a valley *and* a coastal feature; a piano is percussion *and* keyboard.) → Use **categories/tags / multiple-parent relations**, not a forced single tree.

### 3.3 The canonical anti-patterns (teach by negative example)

```
Driver : Person          ❌  a driver IS NOT a special kind of person (role → compose)
Employee : Person        ❌  same mistake, different domain
City : County            ❌  a city is NOT a kind of county (part-of → compose)
County : Country         ❌  containment, not subtype
Penguin : Bird { Fly() } ❌  not substitutable (flight is a trait, not on Bird)
Square : Rectangle       ❌  mutable-width breaks Liskov (classic; discuss in A0)
```

---

## 4. Assignment ladder (Deliverable b)

Seven rungs, intro → advanced, each anchored on a founder example and **explicitly labelled** with the modelling tool it teaches. Each assignment states: **Brief · Modelling decision · Canonical deliverables · Tests · Learning outcomes · Worked snippet · Common pitfalls · Stretch.**

**Deliverable convention (all assignments).** A complete submission is **one pull request** containing:
- **Canonical model** files in `wmoop.doc/model/<domain>/` (`*.domain.yaml` manifest + one `*.concept.yaml` per concept) — the single source of truth (Invariant 1).
- **Conformance cases** in `wmoop.doc/conformance/<domain>/` (language-neutral expectations).
- **Idiomatic generated code + unit tests** in a target language repo (e.g. `wmoop.net/src/<Domain>/` and `wmoop.net/test/<Domain>/`).
- A filled **DoD checklist** (§6) and the **modelling-decision justification** (which of `is-a`/`part-of`/`acts-as`, and why).
- At least **one peer review** given and own-PR review addressed (from A3 onward).

> Paths/format illustrate the WM Schema Spec; adjust to its final form.

---

### A0 — Warm-up: Geometry shapes · **Inheritance + interfaces + polymorphism**
**Domain:** `Math/Geometry` (seed). **Difficulty:** intro. **Est. effort:** 3–4 h.

**Brief.** Model `Shape` (abstract) and a small set of plane shapes (`Circle`, `Rectangle`, `Square`, `Triangle`). Provide the polymorphic operations `area` and `perimeter`. Capture the classic **`Square : Rectangle` Liskov trap** as a written note in your PR: explain why you did *not* make `Square` inherit from a mutable `Rectangle`.

**Modelling decision.** **Inheritance** for genuine `is-a` (a `Circle` *is a kind of* `Shape`) + **interface/trait** `IHasVertices`, `IConvex` for orthogonal capabilities + **polymorphism** for `area`/`perimeter`. `Square` is modelled as its own `Shape` (or an immutable regular quadrilateral), **not** as a subtype of a mutable `Rectangle`.

**Canonical deliverables.** `model/math/geometry/{geometry.domain.yaml, Shape.concept.yaml, Circle.concept.yaml, Rectangle.concept.yaml, Square.concept.yaml, Triangle.concept.yaml}`; conformance cases asserting `area`/`perimeter` for known inputs and that a `Shape` reference dispatches correctly.

**Learning outcomes.** LO-1, LO-2, LO-3, LO-4, LO-5.

**Worked snippet (generated C#, idiomatic).**
```csharp
public abstract class Shape
{
    public abstract Area Area { get; }         // units carried (Invariant 4)
    public abstract Length Perimeter { get; }
}

public sealed class Circle(Length radius) : Shape
{
    public Length Radius { get; } = radius;
    public override Area   Area      => Area.Of(Math.PI * Radius.Metres * Radius.Metres);
    public override Length Perimeter => Length.Metres(2 * Math.PI * Radius.Metres);
}
```

**Common pitfalls.** Putting `area()` on a concrete base with a stored field; forgetting units; `Square : Rectangle`.
**Stretch.** Add `Polygon` with a generic `IReadOnlyList<Vertex>` and prove `Square`/`Triangle` satisfy a shared conformance case (intro to generics, LO-8).

---

### A1 — Musical instruments · **Inheritance + traits**
**Domain:** `Music/Instruments` (seed). **Difficulty:** intro. **Est. effort:** 5–6 h.

**Brief.** Model `Instrument` (abstract) and a shallow family tree using a recognised classification (Hornbostel–Sachs): `StringInstrument`, `PercussionInstrument`, `WindInstrument` → a few leaves (`Violin`, `Guitar`, `SnareDrum`, `Flute`). Model *how it is played* and *whether it transposes* as **traits**, because they cut across families.

**Modelling decision.** **Inheritance** for the genuine family `is-a` (a `Violin` *is a* `StringInstrument`); **traits/interfaces** `IBowed`, `IPlucked`, `ITransposing`, `IKeyboardControlled` for cross-cutting capabilities. Teaching moment: the **piano** is percussion-by-mechanism *and* keyboard-controlled — resolve with a trait + category, **not** a second base class (connects to §3.5 contested classification).

**Canonical deliverables.** `model/music/instruments/*` with `Instrument`, three families, ≥4 leaves, ≥3 traits; conformance: each leaf reports its family, its playing-technique trait, and `producesSound()` behaviour.

**Learning outcomes.** LO-1, LO-3, LO-4, LO-5, LO-10.

**Worked snippet (canonical YAML).**
```yaml
id: wmoop.music.instruments/Violin
kind: Class
name: { en: Violin, ro: Vioară }
definition: A bowed string instrument with four strings tuned in perfect fifths.
extends: wmoop.music.instruments/StringInstrument   # genuine is-a
traits: [ wmoop.music.instruments/Bowed ]              # capability, not a base class
provenance:
  - source: "Hornbostel–Sachs classification (1914), rev. MIMO 2011"
    cite: "321.322-71"
version: 1.0.0
```

**Common pitfalls.** `KeyboardInstrument` as a base class (it is a control mechanism → trait); over-deep trees (`BowedStringInstrument : StringInstrument` when a trait suffices).
**Stretch.** Add the contested `Piano` and document, in the PR, why it uses `category: [percussion, keyboard]` instead of multiple inheritance.

---

### A2 — Animal taxonomy · **Inheritance *and its limits* (Liskov)**
**Domain:** `Nature/Animals` (seed). **Difficulty:** intro→intermediate. **Est. effort:** 6–8 h.

**Brief.** Model a slice of the Linnaean hierarchy: `Animal` → `Vertebrate` → `Mammal`/`Bird`/`Fish`, down to a few species (`Sparrow`, `Penguin`, `Housefly`). Carry a common property such as `legCount`. **Do not** put `fly()` on `Bird`.

**Modelling decision.** **Inheritance** for taxonomic `is-a` (ranks are stable, substitutable kinds-of) + **traits** for abilities (`ICanFly`, `ICanSwim`, `IsEndothermic`). The **penguin test**: `Penguin extends Bird` but `Penguin` does **not** have `ICanFly`; `Sparrow` does. This proves why abilities belong in traits — otherwise `Penguin` violates Liskov on a `Bird.Fly()` contract.

**Canonical deliverables.** `model/nature/animals/*` with ≥3 ranks deep, ≥3 species, ≥3 traits; conformance cases including an explicit **Liskov case**: "a `Bird` reference never guarantees flight," asserted via the trait, not the base.

**Learning outcomes.** LO-3, LO-5, LO-9 (LSP), LO-10, LO-11.

**Worked snippet (generated C#, the trap avoided).**
```csharp
public abstract class Animal { public abstract int LegCount { get; } }
public abstract class Bird : Animal { public override int LegCount => 2; } // NO Fly() here
public interface ICanFly { Length MaxAltitude { get; } }

public sealed class Sparrow : Bird, ICanFly { public Length MaxAltitude => Length.Metres(3000); }
public sealed class Penguin : Bird { /* deliberately not ICanFly */ }
```

**Common pitfalls.** `Fly()` on `Bird`; modelling `Pet` as a subclass of `Dog` (that is a role — foreshadows A5); deep chains that add no new essence.
**Stretch.** Add `category`/`tags` for ecological role (predator/prey) as a multi-axis classification distinct from taxonomy (LO-10).

---

### A3 — Geography landforms · **Inheritance + categories for contested classes**
**Domain:** `Nature/Geography` (seed). **Difficulty:** intermediate. **Est. effort:** 8–10 h.

**Brief.** Model `Landform` (abstract) with shared, *sourced* properties (`meanElevation` in metres, `formationProcess`) → `Mountain`, `Valley`, `Plateau`, `River`, `Lake`. Every property must have **units** and a **citation** (Invariant 4). Handle at least one multi-axis case (e.g. a **fjord** is a valley *and* a coastal/marine feature).

**Modelling decision.** **Shallow inheritance** for genuine landform `is-a`; **categories/tags** (not a forced single tree) for contested/multi-axis membership. First assignment requiring real provenance and units.

**Canonical deliverables.** `model/nature/geography/*` with ≥5 landforms; each concept fully sourced with units; a `Fjord` concept using `category: [valley, coastal-marine]`; conformance checks for unit presence and citation presence (the model is its own test).

**Learning outcomes.** LO-1, LO-2, LO-10, LO-12 (first peer review required), LO-13 (provenance).

**Worked snippet (canonical YAML).**
```yaml
id: wmoop.nature.geography/Mountain
kind: Class
name: { en: Mountain, ro: Munte }
definition: A landform rising prominently above its surroundings, typically >300 m local relief.
extends: wmoop.nature.geography/Landform
properties:
  - id: "#meanElevation"
    name: { en: mean elevation }
    type: Quantity
    unit: metre            # units are mandatory (Invariant 4)
provenance:
  - source: "Gregory, K.J. The Earth's Land Surface, SAGE, 2010"
    cite: "ch. 4"
version: 1.0.0
```

**Common pitfalls.** Elevation as a bare number without units; forcing `Fjord : Valley` only; uncited "common knowledge" properties.
**Stretch.** Add `River` as a landform *and* note its `partOf` a `DrainageBasin` — a gentle bridge to A4.

---

### A4 — Administrative hierarchy · **PART-OF COMPOSITION (NOT inheritance)**
**Domain:** `Nature/Geography` (new sub-module `geography.admin`). **Difficulty:** intermediate. **Est. effort:** 8–10 h. **This is the composition keystone.**

**Brief.** Model the administrative hierarchy **Country → County → City** as **containment**, plus a little L2 reference data (your own country, one county, one city). A `City` is **not** a kind of `County`; a `County` is **not** a kind of `Country`. They are **parts** of one another.

**Modelling decision.** **Composition / `partOf` (mereology)** — emphatically **not** inheritance. Students must *attempt and reject* an inheritance model in the PR write-up, applying the §3 litmus. Teach **aggregation vs composition lifetime** (a county's existence does not depend on a single city) and **recursive structures** with cardinalities.

**Canonical deliverables.** `model/nature/geography/admin/*` defining `AdministrativeUnit` with a `partOf` relation and an `AdminLevel` enum (`Country`, `County`, `City`, …); L2 instances in `model/.../admin/instances/`; conformance: traversal (city → county → country), cardinality rules, and a **lint assertion that no admin concept uses `extends` across levels**.

**Learning outcomes.** LO-6 (keystone), LO-2, LO-10, LO-12, LO-13.

**Worked snippet — the wrong vs right model.**
```yaml
# ❌ WRONG — containment modelled as inheritance
# id: wmoop.geography.admin/City
# extends: wmoop.geography.admin/County      # a city is NOT a kind of county

# ✅ RIGHT — containment modelled as a part-of relation
id: wmoop.geography.admin/City
kind: Class
name: { en: City, ro: Oraș }
definition: A large permanent human settlement administered within a county.
relations:
  - type: partOf                 # whole/part mereology, not subtype
    target: wmoop.geography.admin/County
    cardinality: "1"             # part of exactly one county (this model)
version: 1.0.0
```
```csharp
// Generated C# — composition, not a base class
public sealed class AdministrativeUnit
{
    public required string      Name  { get; init; }
    public required AdminLevel  Level { get; init; }            // Country | County | City
    public AdministrativeUnit?  PartOf { get; init; }           // containment link
    public IReadOnlyList<AdministrativeUnit> Parts { get; init; } = [];
}
// NOTE: there is deliberately no `class City : County`.
```

**Common pitfalls.** `City : County`; conflating "is located in" with "is a kind of"; forgetting cardinality; modelling capital-city status as a subtype instead of a **role/flag** (foreshadows A5).
**Stretch.** Add a second hierarchy (electoral districts) that *overlaps* the administrative one — proving why a single tree fails and why `partOf` relations beat inheritance for multi-hierarchy containment (LO-10).

---

### A5 — Person as a role: Driver / Student / Employee · **ROLES (NOT inheritance)**
**Domain:** new `Nature/People` (`Person`) + a role module (`transport.licensing`, `academic`, or `org`). **Difficulty:** advanced. **Est. effort:** 10–12 h. **This is the roles keystone and the first cross-domain link.**

**Brief.** Model `Person` (identity + a few stable biological facts) in the Nature domain. Then model **`Driver`**, **`Student`**, and **`Employee`** as **roles** attached to a `Person` — each with its own meta (e.g., driving licence + categories + issuing authority; enrolment + programme; employer + position). One person must be able to hold several roles at once and to lose a role without ceasing to be a person.

**Modelling decision.** **Roles via composition**, declared as a **versioned, acyclic cross-domain dependency** (Invariant 5). Absolutely **never** `Driver : Person`. Roles are **temporal** (bounded) and **plural**. Introduces **generics** (a typed role registry) and **DIP/ISP** (small role interfaces).

**Canonical deliverables.** `model/nature/people/Person.concept.yaml`; `model/transport/licensing/DriverRole.concept.yaml` (+ `DrivingLicence`, licence-category enum); analogous `StudentRole`, `EmployeeRole`; a **declared cross-domain dependency** in each role module's `*.domain.yaml`; conformance: a person holding Driver + Student simultaneously, a role being added and removed, and a **cycle check** on the domain dependency graph.

**Learning outcomes.** LO-7 (keystone), LO-8, LO-9 (DIP/ISP/OCP), LO-10, LO-13.

**Worked snippet (canonical YAML + generated C#).**
```yaml
id: wmoop.transport.licensing/DriverRole
kind: Role
name: { en: Driver, ro: Șofer }
played_by: wmoop.nature.people/Person        # attached to Person — NOT extends
definition: The capability of a Person to legally operate a road vehicle.
dependsOn: [ "wmoop.nature.people@^2" ]       # declared, versioned, acyclic (Invariant 5)
temporal: { bounded: true }                # roles start and end
properties:
  - { id: "#licence",    name: {en: driving licence}, type: wmoop.transport.licensing/DrivingLicence }
  - { id: "#categories", name: {en: categories},      type: "set<LicenceCategory>" }   # AM,A1,A2,A,B,BE,C...
version: 1.0.0
```
```csharp
public sealed class Person { public required PersonId Id { get; init; } /* stable facts */ }

public interface IRole { DateOnly? ValidUntil { get; } }                 // ISP: tiny role contracts
public sealed record DriverRole(DrivingLicence Licence,
                                IReadOnlySet<LicenceCategory> Categories,
                                DateOnly? ValidUntil) : IRole;

public sealed class Party                                                // composition holds roles
{
    private readonly List<IRole> _roles = [];
    public required Person Person { get; init; }
    public void Assign(IRole r) => _roles.Add(r);
    public T?   As<T>() where T : class, IRole => _roles.OfType<T>().FirstOrDefault(); // generics
    public bool Is<T>() where T : IRole        => _roles.OfType<T>().Any();
}
// A person can be .Is<DriverRole>() AND .Is<StudentRole>() at once; neither is `: Person`.
```

**Common pitfalls.** `Driver : Person`; putting `drivingLicence` directly on `Person`; an undeclared cross-domain reference; a dependency cycle (People → Transport → People).
**Stretch.** Add `role validity windows` and query "all drivers whose licence expires this year," demonstrating that roles are data, not types (LO-7, LO-8).

---

### A6 — Capstone: Vehicle + Driver, cross-domain + codegen conformance · **ALL THREE + generics + SOLID**
**Domain:** new `Transport` (`Vehicle` → `AutoVehicle` → `Moped`) composed with A5's `Driver` role. **Difficulty:** advanced/capstone. **Est. effort:** 14–18 h (often pair/trio).

**Brief.** Build the Transport domain the founder described: `Vehicle` (abstract, with `numberOfWheels`) → `AutoVehicle` (engine-powered) → `Moped`. Use **composition** for parts (a `Vehicle` *has an* `Engine`, `Wheel`s), **inheritance** for the genuine vehicle `is-a`, and **roles** to connect a `Person`/`Driver` to operating a `Vehicle`. Then **prove "write once, replicate everywhere"**: generate idiomatic code in a **second language** from the same canonical model and show both pass the same conformance suite (Invariant 1).

**Modelling decision.** **All three, deliberately separated:** inheritance (`Moped` *is a kind of* `AutoVehicle`), composition (`Vehicle` *has* `Engine`/`Wheel`s), role (`Person` *acts as* `Driver`, who *operates* a `Vehicle`). Plus **generics** (`Quantity<Unit>`, typed collections) and a **full SOLID review**.

**Canonical deliverables.** `model/transport/*` (`Vehicle`, `AutoVehicle`, `Moped`, `Engine`, `Wheel`); cross-domain link from a `Trip`/`operates` relation to A5's `DriverRole`; conformance suite covering inheritance depth, composition cardinalities, and role operation; **code generated into two language repos** (e.g. `wmoop.net` + one of `wmoop.java`/`wmoop.py`/`wmoop.cpp`) both green on the same conformance cases.

**Learning outcomes.** LO-1…LO-13 (integrative), with emphasis on LO-6, LO-7, LO-8, LO-9, LO-11.

**Worked snippet (model shape).**
```yaml
# Vehicle: abstract is-a root with a shared property
id: wmoop.transport/Vehicle
kind: Class
name: { en: Vehicle, ro: Vehicul }
definition: A machine that transports people or cargo.
properties: [ { id: "#numberOfWheels", name: {en: number of wheels}, type: integer } ]
relations:
  - { type: hasPart, target: wmoop.transport/Wheel,  cardinality: "0..*" }   # composition
  - { type: hasPart, target: wmoop.transport/Engine, cardinality: "0..1" }
version: 1.0.0
---
id: wmoop.transport/Moped
kind: Class
extends: wmoop.transport/AutoVehicle     # genuine is-a (AutoVehicle is-a Vehicle)
# operation by a Person is a ROLE link, defined on a Trip/operates relation, never `Moped : Driver`
```

**Common pitfalls.** Collapsing composition (engine) into inheritance (`EnginedVehicle`); re-writing the model by hand per language instead of generating; cross-domain cycles; silent conformance drift between languages.
**Stretch.** Add a third language; publish a short "model-to-code" report; open the capstone as a reviewed PR against a real stewarded domain (bridge to §7).

---

### 4.x Ladder at a glance

| ID | Example | Primary tool | Secondary | Keystone for |
|---|---|---|---|---|
| A0 | Geometry shapes | **Inheritance** | interfaces, polymorphism | polymorphism, Liskov intro |
| A1 | Instruments | **Inheritance** | traits | abstraction, traits |
| A2 | Animal taxonomy | **Inheritance (+ limits)** | traits | **Liskov / inheritance limits** |
| A3 | Landforms | **Inheritance** | categories/tags | abstraction, **provenance** |
| A4 | Country→County→City | **Composition (part-of)** | — | **composition** |
| A5 | Person→Driver/Student/Employee | **Roles** | generics, cross-domain | **roles** |
| A6 | Vehicle + Driver | **All three** | generics, SOLID, codegen | **integration / conformance** |

---

## 5. Rubrics (Deliverable c)

All rubrics use one **4-level scale** so grades compose cleanly:

**0 — Incomplete · 1 — Developing · 2 — Proficient · 3 — Exemplary**

### 5.1 Rubric — Model quality (modelling judgement)

| Criterion | 0 Incomplete | 1 Developing | 2 Proficient | 3 Exemplary |
|---|---|---|---|---|
| **Right tool (`is-a`/`part-of`/`acts-as`)** | Wrong tool (e.g., `Driver:Person`, `City:County`) | Mostly right, one misuse, weak justification | Correct choice with a clear justification per §3 | Correct, justified, *and* shows the rejected alternative and why |
| **Abstraction level** | Base concept missing or arbitrary | Base holds some non-shared properties | Base holds exactly the shared, defensible properties | Elegant, minimal, extensible base; clear extension points (OCP) |
| **Inheritance discipline** | Deep (>4) or Liskov-violating | Shallow but one fragile subtype | Shallow, substitutable, Liskov-safe | Shallow + abilities correctly moved to traits |
| **Cohesion / SRP** | One concept conflates many roles | Minor conflation | One concept = one responsibility | Clean separation; contested classes handled by categories |
| **Naming & definition clarity** | Cryptic or undefined | Understandable, uneven | Clear names + crisp definitions | Publication-quality definitions; disambiguated from near-synonyms |

### 5.2 Rubric — Correctness (machine-checkable)

| Criterion | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **Schema validity (CI)** | Fails schema | Validates with warnings | Validates clean | Clean + no lint waivers |
| **Conformance tests** | Missing/failing | Partial coverage | All required cases pass | Adds meaningful new cases (incl. Liskov/negative) |
| **Codegen builds** | Does not generate/compile | Generates, build warnings | Generates & builds in target language | Builds green in **two** languages, identical conformance |
| **Dependency hygiene** | Undeclared/cyclic deps | Declared, unversioned | Declared + versioned + acyclic | Minimal, justified cross-domain surface |

### 5.3 Rubric — Sourcing / provenance (Invariant 4)

| Criterion | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **Stable ID + name + definition** | Missing fields | Present but inconsistent | All concepts complete | Complete + localized `name@lang` |
| **Citations** | None | Some, informal | Every non-trivial fact cited to a credible source | Primary/standard sources (e.g., MIMO, Linnaean authority, national statute) |
| **Units on quantities** | Missing | Inconsistent | All quantities carry units | Units + ranges/constraints, SI-correct |
| **Verifiability** | Unverifiable claims | Hard to check | A reviewer can verify from citations | Reproducible; links to canonical datasets for L2 |

### 5.4 Rubric — Code review (given & received)

| Criterion | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **Review given** | None | Superficial ("LGTM") | Specific, evidence-based, kind, actionable | Catches a real modelling error; suggests the fix with reasoning |
| **Review received** | Ignores feedback | Addresses some | Addresses all with clear replies | Engages substantively; model improves measurably |
| **PR hygiene** | No description/DoD | Partial | DoD complete, scoped, clean history | Exemplary description + modelling-decision rationale |
| **Collaboration etiquette** | Dismissive/absent | Transactional | Respectful, responsive | Mentors peers; strengthens the domain |

### 5.5 Weighting & grade bands (suggested; instructor-tunable)

| Component | Weight |
|---|---|
| Model quality (§5.1) | 30% |
| Correctness / CI (§5.2) | 30% |
| Provenance (§5.3) | 20% |
| Code review (§5.4) | 20% |

**Band:** convert the 0–3 criterion scores to a percentage (points ÷ max). Suggested letter bands: A ≥ 85%, B 70–84%, C 55–69%, D 40–54%, F < 40%. **Gate:** a submission that fails CI (§6) caps Correctness at 1 regardless of effort — the machine bar is non-negotiable and identical for everyone (Invariant 6).

---

## 6. Definition of Done & CI gates (the automated bar)

A contribution (human- or AI-authored) is **Done** when every box is green. CI enforces items 1–6 automatically; items 7–8 are human.

- [ ] **1. Schema-valid.** Every `*.concept.yaml`/`*.domain.yaml` validates against the WM schema.
- [ ] **2. Complete metadata.** Every concept has a stable **ID**, **name**, **definition**, **provenance**, and **units** on all quantities (Invariant 4).
- [ ] **3. Modelling-decision lint.** No role modelled as a subclass; no `partOf` modelled as `extends`; inheritance depth ≤ configured max; Liskov conformance cases present for subtypes.
- [ ] **4. Dependency graph acyclic & versioned.** Cross-domain links declared with semver ranges; no cycles (Invariant 5).
- [ ] **5. Conformance passes.** All required conformance cases green.
- [ ] **6. Codegen builds.** Generated code compiles and passes conformance in the target language(s).
- [ ] **7. Peer review.** ≥ 1 approving review from a classmate/contributor; author has addressed comments.
- [ ] **8. Steward sign-off** (for domain-structural changes) per CODEOWNERS.

> The DoD is the **objective learning contract**: students always know what "done" means, graders are consistent, and AI contributions meet the *same* bar — no lower, no higher.

---

## 7. The "Adopt a Domain" program (Deliverable d)

A cohort (class, lab section, or club) **adopts** a domain or sub-domain and stewards it across a semester — the founder's "students who love geography describe landforms / administrative structure" vision, operationalised.

### 7.1 The Domain Charter (claiming)

A cohort opens a **Domain Charter** PR (template in §10.2) stating:
- **Scope & boundaries** (e.g., "`Nature/Geography/admin` — administrative hierarchies worldwide"), explicitly listing what is *out* of scope.
- **Dependencies** it expects (acyclic; Invariant 5).
- **Steward(s)** (instructor + 1–2 senior students) added to `CODEOWNERS`.
- **Roadmap** for the semester (concepts to land, provenance sources).
- **Definition of Done** inherited from §6.

A maintainer approves the charter; the domain is now **stewarded** by that cohort for the term.

### 7.2 Contributor progression (student → contributor → steward → maintainer)

| Tier | How you get here | GitHub capability | Responsibilities |
|---|---|---|---|
| **Student** | Enrolled in the course | Fork + open PRs; triage own issues | Complete assignments; cite sources; respond to review |
| **Contributor** | ≥ 2 merged PRs meeting DoD + ≥ 2 quality reviews given | Listed in domain `CONTRIBUTORS`; may review peers | Review classmates' PRs; help newcomers; maintain provenance |
| **Steward** | Sustained quality + instructor nomination | In `CODEOWNERS` for the (sub)domain; approves PRs | Guard the model's integrity; approve structural changes; keep the dependency graph clean; curate the roadmap |
| **Maintainer** | Cross-domain trust (usually faculty/alumni/org) | Org-level; approves charters, cross-domain links, releases | Protect invariants org-wide; cut versioned releases; mediate cross-domain disputes |

Advancement is **evidence-based and transparent** (merged PRs, reviews, provenance quality) — this *is* the open-source collaboration outcome (LO-13), assessed by lived behaviour rather than an exam.

### 7.3 Domain lifecycle

```
PROPOSED → CHARTERED → ACTIVE (a cohort stewards it)
   → HANDED-OFF (end of semester) → ACTIVE (next cohort)  … or …
   → DORMANT (no steward) → ARCHIVED (read-only, still generatable)
```
**No orphans rule.** A domain cannot stay `ACTIVE` without a steward. At semester end it is either handed off or marked `DORMANT`; `DORMANT` domains are frozen but remain valid and generatable (the model never rots silently).

### 7.4 Cross-cohort handoff (semester boundary)

Outgoing stewards deliver a **handoff packet**:
- **Steward log** (decisions, rationale, rejected alternatives).
- **Open-issue triage** with labels (`good-first-issue`, `needs-provenance`, `modelling-question`).
- **Domain health snapshot** — the metrics below.
- A 30-minute live handoff to incoming stewards.

**Domain health metrics (dashboard, auto-computed):**

| Metric | Definition | Healthy |
|---|---|---|
| Coverage | concepts modelled ÷ roadmap concepts | ≥ 70% |
| Provenance completeness | concepts with citations ÷ all concepts | 100% |
| Conformance pass rate | green cases ÷ all cases | 100% |
| Review debt | open PRs awaiting review | ≤ small backlog |
| Bus factor | active stewards | ≥ 2 |

---

## 8. Instructor onboarding & sample syllabus (Deliverable e)

### 8.1 Instructor setup checklist (≈ 1–2 hours)

1. **Read** this guide + the WM Schema Spec + Authoring Guide.
2. **Pick a delivery mode:** (a) **Module slot** — drop A1/A2 + A4 + A5 into an existing OOP course (3–4 weeks); or (b) **Studio** — full-semester *Adopt a Domain* (14 weeks, §8.4).
3. **Create a classroom org/fork** (GitHub Classroom recommended) with branch protection and CI enabled; mirror the WMOOP CI DoD (§6).
4. **Choose domains** matching student interests (geography, music, biology, transport…). Pre-open **Domain Charters** or let cohorts propose.
5. **Seat yourself as a steward** in `CODEOWNERS` for the course's domains.
6. **Share** the student quick-reference card (§10.3) and the academic-integrity/AI policy (§8.2).
7. **Set the grading cadence** (§8.3) and wire rubrics (§5) into your gradebook.
8. **Dry-run** one assignment (A0) yourself end-to-end so you have a reference solution and know the CI feedback students will see.

### 8.2 Academic integrity & AI-assisted contribution policy

WMOOP *wants* AI to contribute, so the policy is about **judgement and disclosure**, not prohibition:
- **AI is allowed and encouraged** as a drafting, translation, and boilerplate tool.
- **The student must understand and defend every decision.** A short oral check or PR discussion confirms authorship of judgement. The graded object is the modelling choice (`is-a`/`part-of`/`acts-as`), which is exactly what AI gets wrong by default — so the human's value-add is real.
- **Disclose assistance** in the PR with a trailer, e.g. `Assisted-by: <tool/model>`.
- **Same DoD for everyone** (§6): AI-authored content passes the identical CI + human review; no shortcut, no penalty.
- **Provenance is non-negotiable** (Invariant 4): AI-suggested "facts" must still be cited to a credible human source, which trains source-criticism.

### 8.3 Grading cadence

- **Per assignment:** auto-grade Correctness from CI; grade Model quality + Provenance + Code review from rubrics (§5). Return within one week.
- **Mid-semester model review (studio):** a "design crit" where cohorts defend their domain model against the §3 litmus.
- **End of semester:** steward handoff quality + domain health (§7.4) contributes to a collaboration grade.

### 8.4 Sample syllabus — two shapes

**(A) Module slot — insert into any OOP course (weeks shown relative to the module):**

| Wk | Topic | WMOOP activity |
|---|---|---|
| 1 | Inheritance, interfaces, Liskov | A1 Instruments + A2 Animals (penguin test) |
| 2 | Composition vs inheritance | **A4** Country→County→City (part-of) |
| 3 | Roles & cross-domain design | **A5** Person→Driver/Student/Employee |
| 4 | Review & integration | Peer review sprint; optional A6 intro |

**(B) Full 14-week "Adopt a Domain" studio:**

| Wk | Focus | Deliverable |
|---|---|---|
| 1 | Intro, ontology thinking, tooling, Domain Charter | Charter PR; env + CI working |
| 2 | Abstraction & polymorphism | **A0** Geometry |
| 3 | Inheritance + traits | **A1** Instruments |
| 4 | Inheritance limits / Liskov | **A2** Animals |
| 5 | Abstraction + provenance + categories | **A3** Landforms |
| 6 | **Composition / part-of** | **A4** Admin hierarchy |
| 7 | **Mid-semester model crit** | Defend model vs §3 litmus |
| 8 | Roles I | **A5** Person + first role |
| 9 | Roles II + cross-domain deps | **A5** multi-role + acyclic deps |
| 10 | Capstone kickoff | **A6** Vehicle inheritance + composition |
| 11 | Capstone integration | **A6** compose Driver role + conformance |
| 12 | Codegen to 2nd language | **A6** two-language green |
| 13 | Code-review sprint + steward duties | Review debt → 0; CODEOWNERS |
| 14 | Presentations + handoff | Domain health report + handoff packet |

---

## 9. Localization (Deliverable f)

WMOOP's model is **language-neutral** (Invariant 1), and localization respects that:

- **Keep canonical.** Stable **IDs** and **canonical names** stay in English and never change by locale — IDs are the interlingua that lets `wmoop.net`, `wmoop.java`, `wmoop.py`, `wmoop.cpp` agree.
- **Translate human-facing fields.** Use per-locale variants on `name`/`definition` (e.g. `name: { en: Mountain, ro: Munte }`), so a Romanian student sees *Munte* while the model and generated symbols stay stable.
- **Translate the course pack, not the model.** Briefs, rubrics, and the quick-reference card live under `wmoop.doc/academic/courses/<lang>/` (e.g. `.../courses/ro/`). A university in Romania can teach entirely in Romanian while contributing to the one global model.
- **Worked example (Romanian).** Students may add `ro` labels as a first, low-risk contribution (great onboarding): `Vehicle→Vehicul`, `Driver→Șofer`, `City→Oraș`, `County→Județ`, `Country→Țară`, `Animal→Animal`, `Mammal→Mamifer`. This teaches that *identity ≠ label* — a core ontology insight (LO-10).

---

## 10. Appendices

### 10.1 Glossary (student-facing)
- **Concept** — a modelled thing (class, role, relation) with a stable ID.
- **Is-a / extends** — genuine, permanent, substitutable kind-of (inheritance).
- **Part-of** — whole/part containment (composition); not a subtype.
- **Role** — a contextual, often temporal, pluralizable capability attached to an entity by composition.
- **Trait/interface** — an orthogonal capability (`CanFly`), independent of the type tree.
- **Provenance** — the cited source backing a fact (mandatory).
- **Conformance case** — a language-neutral test the model must satisfy.
- **Steward / CODEOWNER** — the person accountable for a domain's integrity.

### 10.2 Domain Charter template
```markdown
# Domain Charter: <domain path>
- Scope: <what this domain covers>
- Out of scope: <explicit exclusions>
- Dependencies: <other domains + semver> (must be acyclic)
- Stewards: @instructor, @senior-student  (added to CODEOWNERS)
- Roadmap (this term): <concepts to land, with target sources>
- Definition of Done: inherits wmoop.doc §6
- Localization: <locales maintained, e.g. en, ro>
```

### 10.3 PR template (course)
```markdown
## What
<concepts added/changed>

## Modelling decision
- Chose: [ ] is-a (inheritance)  [ ] part-of (composition)  [ ] acts-as (role)
- Why (per §3 litmus):
- Rejected alternative and why:

## DoD (§6)
- [ ] schema-valid  [ ] metadata complete (id/name/def/provenance/units)
- [ ] modelling lint clean  [ ] deps acyclic+versioned
- [ ] conformance green  [ ] codegen builds  [ ] peer review

Assisted-by: <AI tool/model, if any>
```

### 10.4 Quick-reference decision card (print for students)
> **Would it stop being true while the object lives?** → **Role.**
> **Can it be several at once?** → **Role/trait.**
> **Is it "made of / located in"?** → **Composition (part-of).**
> **Permanent, substitutable kind-of?** → **Inheritance (keep shallow).**
> **Contested / multi-axis?** → **Categories/tags.**
> When in doubt, it is **not** inheritance.

### 10.5 Cross-references (authoritative elsewhere)
- **WM Schema Specification** — exact file format, ID grammar, allowed `kind`s, relation types.
- **Authoring Guide** — how to write a concept/domain file + run CI locally.
- **Governance doc** — CODEOWNERS, release/versioning, maintainer council.
- **Core Architectural Invariants** — the eight invariants this program assumes.