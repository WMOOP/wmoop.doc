# WMOOP Meta-Model (Layer L0) and Contributor Modeling Rules

> **Document role.** This is the normative specification of WMOOP's upper ontology (layer **L0**) and the rules every contributor — human or AI — follows when authoring a domain model (layer **L1**). L0 is small, fixed, and versioned conservatively. Everything else in WMOOP is built *on top of* and *validated against* it. Where this document and a later section disagree on anything defined here, this document wins; later sections align to it (see **Cross-references**).
>
> **Status:** Draft for ratification. **Normative serialization:** declarative (JSON, JSON-LD-compatible); YAML is shown here for readability. **License context:** Apache-2.0 (code); definitions and facts carry their own provenance.

---

## 0. How to read this document

L0 answers one question: *what are the raw building blocks out of which any corner of the world — a moped, a tomato, a musical note, a mathematical group, a driving licence — can be described once, language-neutrally, so that idiomatic C#/Java/Python/C++ can be generated mechanically and never diverge?*

We separate three things that are routinely (and fatally) conflated in naive OOP modeling:

1. **Foundational categories** (§2): the fixed, closed set of *kinds of thing that can exist*. Think of these as the periodic table. Contributors do not add to this set.
2. **Authoring stereotypes** (§3): the vocabulary contributors actually *write* in L1 (`Kind`, `Role`, `Phase`, …). Each stereotype is a disciplined way of committing to one foundational category with extra rules attached. This is where "roles over inheritance" becomes mechanical rather than a matter of taste.
3. **Mechanics** (§4–§8): decision rules, the cross-domain role mechanism, identity/naming/typing, Liskov discipline, and the CI Definition of Done.

A reader who only wants the rules of thumb should read §4 (decision flowchart) and §7 (shallow is-a). A reader building the validator should read §3, §6, and §8.

---

## 1. What the meta-model must be able to say

A frequent failure mode of "model the world in OOP" projects is to assume the world is **physical objects with attributes**. It is not. WMOOP must, from day one, represent all of the following with equal first-class status:

| Thing | Example domain | Why naive OOP breaks |
|---|---|---|
| A physical persistent object | `Moped` (Transport) | fine — but tempts deep inheritance |
| A process / happening in time | a `Journey`, the *playing* of a note | has temporal parts; is not a "thing with fields" |
| An abstract structure | a `Group`, a `Theorem` (Math) | outside space-time; no causal powers; a *type* more than a *token* |
| A context-dependent facet | `Driver`, `Employee` | relational, anti-rigid, cross-domain; destroys the inheritance tree if modeled as `Driver : Person` |
| A multiply-classified thing | `Tomato` (fruit *and* vegetable) | single inheritance tree cannot hold both honestly |
| A measured quantity | wheel count, mass, tempo | a bare `double` loses units and lets `metres == seconds` |

L0 is the smallest vocabulary that lets us say all six **without lying** (without forcing a process to be an object, an abstract type to be an instance, or a role to be a subclass).

---

## 2. The fixed set of foundational categories

WMOOP commits to **8 foundational categories** arranged under one root, plus **one orthogonal meta-axis** (Type vs Individual) and the **Unit/Dimension apparatus** that supports category D. This set is *closed*: L1 contributors never invent a new foundational category; they specialize within these.

### 2.1 Two independent axes

Every modeled thing is located on **two orthogonal axes**:

- **Axis 1 — Instantiation (meta-axis):** is this a **Type** (a Universal/Class: `Dog`, `Group`, `MajorChord`) or an **Individual** (a Particular/Instance: *this* dog Rex, *this* group ℤ/2ℤ, *this* performance)? This axis is not a category of thing; it cross-cuts all categories. A `Group` is an abstract **Type**; `ℤ/2ℤ` is an abstract **Individual** of it.
- **Axis 2 — Mode of existence:** the 8 categories below.

Keeping these orthogonal is what lets WMOOP treat "the musical note C♯ as a type" and "the C♯ sounded at 00:03 in this recording as an event-individual" as two clearly distinct, linked things rather than a paradox (§2.4).

### 2.2 The category lattice

```
Entity  (root; everything modeled is an Entity)
├── Endurant        (A) continuant; wholly present whenever it exists; persists & can change
│                       e.g. Person, Moped, Planet, Oak Tree
├── Perdurant       (B) occurrent/process/event; unfolds in time; has temporal parts
│                       e.g. Journey, ChemicalReaction, NoteOccurrence, Concert
├── Abstract        (C) outside space-time; no causal powers; often type-like
│                       e.g. Number, Group, Theorem, PitchClass, GeometricShape(as math)
├── Quality         (D) a characteristic that inheres in / is borne by an Entity
│   └── Quantity        a Quality with a measurable Magnitude = Value + Unit + Dimension
│                       e.g. mass, tempo, wheelCount, electricCharge
├── Relation        (E) ties two or more Entities; includes part-whole (mereology)
│                       e.g. partOf, locatedIn, parentOf, memberOf, adjacentTo
├── Role            (F) an anti-rigid, relationally-grounded classification an Entity *plays*
│                       e.g. Driver, Employee, Owner, Student, Capital(city)
└── Collection      (H) a plurality (set/sequence/bag) treated as a single Entity
                        e.g. a Herd, a Chord(as a set of pitches), a Playlist
```

*(Letter labels A–H preserve the task's enumeration; D's `Unit`/`Dimension` and the Type/Individual meta-axis (G) are the supporting apparatus noted above.)*

### 2.3 The categories, defined

Each category below states: **definition**, **litmus question**, **examples**, **why it is in the fixed set**.

**(A) Endurant — "an object"**
- *Def.* A thing that is wholly present at every instant of its existence and persists through change (it can gain/lose parts and qualities and remain the same individual).
- *Litmus.* "Is it still entirely *there* at any single frozen instant?" Yes → Endurant.
- *Examples.* `Person`, `Vehicle`, `Cell`, `Planet`, `Mountain`.
- *In the set because* most of the "objects of the world" are endurants; this is the backbone that inheritance trees specialize.

**(B) Perdurant — "a happening"**
- *Def.* A thing that *occurs* and has temporal parts; at a frozen instant only a slice of it exists.
- *Litmus.* "Does it have a *first half* and a *second half* in time?" Yes → Perdurant.
- *Examples.* `Journey`, `Mitosis`, `MusicalPerformance`, `NoteOccurrence`, `EclipseEvent`, `ChemicalReaction`.
- *In the set because* biology (processes), music (performances), astronomy (orbits, eclipses) and transport (trips) are unmodelable as "objects with fields." Omitting Perdurants forces contributors to fake processes as objects, which corrupts the model.

**(C) Abstract — "a structure or proposition"**
- *Def.* A thing outside space and time, with no causal powers, typically grasped rather than observed.
- *Litmus.* "Would it be exactly what it is in a universe with no matter and no time?" Yes → Abstract.
- *Examples.* `NaturalNumber`, `Group`, `Theorem`, `Set`, `PitchClass`, `Interval`(musical), `Polygon`(as a math object).
- *In the set because* Math and music theory are core WMOOP domains and are *largely abstract*. This is the category most commonly missing from "OOP models of the world," and its absence is why such models cannot host mathematics.

**(D) Quality / Quantity — "a characteristic"**
- *Def.* A feature that cannot exist on its own but *inheres in* a bearer Entity. A **Quantity** is a Quality whose value is a **Magnitude** = a numeric **Value** + a **Unit** of a **QuantityKind** that has a **Dimension**.
- *Litmus.* "Is it *of* something else and unable to float free?" Yes → Quality.
- *Examples.* color, temperament; `mass` (Quantity, kg, dimension M), `tempo` (Quantity, BPM), `wheelCount` (Quantity, dimensionless Count).
- *In the set because* this is how properties are typed *honestly* — a mass is not a `double`; it is a magnitude in a dimension, enabling unit conversion and dimensional checking (§6.4).

**(E) Relation / Association — "a tie"**
- *Def.* An entity that holds between two or more Entities. Includes **mereological** part-whole relations (`properPartOf`, `componentOf`, `memberOf`) with their algebra (transitivity, antisymmetry).
- *Litmus.* "Does it only make sense with ≥2 participants named?" Yes → Relation.
- *Examples.* `orbits(Moon, Planet)`, `partOf(Wheel, Moped)`, `borders(France, Spain)`, `teaches(Professor, Course)`.
- *In the set because* geography (adjacency, containment), biology (organ part-of organism), and astronomy (orbits) are *relational*; and because part-whole is a distinct logic from is-a and must never be confused with it.

**(F) Role — "a hat an entity wears"**
- *Def.* An **anti-rigid**, **relationally-grounded** classification that an Entity plays *in a context* and can start/stop playing without changing what it fundamentally is. Reified as a first-class object (§5).
- *Litmus.* "Can the very same individual stop being this tomorrow yet remain the same individual?" Yes → Role (not a subclass).
- *Examples.* `Driver`, `Owner`, `Employee`, `Student`, `Pet`, `CapitalCity`.
- *In the set because* roles are the mechanism for **cross-domain intersection** (the Person-as-Driver case). Making Role foundational is what keeps the is-a tree clean.

**(H) Collection / Set — "a many-as-one"**
- *Def.* An Entity whose being is constituted by its members (a set, sequence, or bag). May be extensional (defined by members) or intensional (defined by a membership predicate).
- *Litmus.* "Is it essentially *a group of* other entities?" Yes → Collection.
- *Examples.* `Herd`, `Constellation`, `Chord`(as a pitch set), `Playlist`, `Deck`(of cards).
- *In the set because* "set" is foundational to math, and collective entities (herds, fleets, constellations) recur across domains with their own identity and properties.

> **Mnemonic for the ontological square** (two axes at once): *Dog* is a **Type** of **Endurant**; *Rex* is an **Individual Endurant**; *Running* is a **Type** of **Perdurant**; *Rex's run at noon* is an **Individual Perdurant**; *Mass* is a **Quality Type**; *Rex's 12 kg* is a **Quality Individual (a magnitude)**.

### 2.4 Representing abstract and dual type/event things

Two worked resolutions that the fixed set must make clean:

**Mathematics (Group, Theorem).** A `Group` is modeled as an **Abstract Type** whose *definition* is its axioms (closure, associativity, identity, inverses), expressed as **constraints/invariants** over an operation Relation. A specific group such as `ℤ/2ℤ` is an **Abstract Individual** instantiating `Group`. A `Theorem` is an **Abstract** entity of category C, with a `statement`, a `provenance` citation, and relations `provenFrom(axiomsOrTheorems)` and `impliedBy`. No endurant/perdurant machinery is forced on them.

**Music — the "Note is both a type and an event" problem.** This is resolved by Axis 1 + two categories, not by a paradox:

| Concept | Category + Axis | Identity | Example |
|---|---|---|---|
| `PitchClass` (C♯) | **Abstract Type** | by pitch name/frequency class | C♯ |
| `Note` / `ScoredNote` (C♯, quarter, in bar 3) | **Abstract Individual** (a score element) | by its place/spec in a work | the C♯ written in m.3 |
| `NoteOccurrence` | **Perdurant** (an event) | by time interval within a performance | the C♯ *sounded* at 00:03.2 |

They are linked by relations: `ScoredNote instantiates PitchClass`; `NoteOccurrence realizes ScoredNote`. The code generator then emits, e.g., an immutable `PitchClass` value type, a `Note` record, and a `NoteOccurrence` event type — three idiomatic constructs, one coherent model.

### 2.5 Deliberately out of scope for L0 (v1)

To keep L0 minimal and stable, the following are **explicitly excluded** and, where needed, handled at L1 or deferred:

- **Modality and possible worlds** (necessity/possibility as logical operators). We model dispositions pragmatically as capabilities/relations, not with modal logic.
- **Full temporal logic / 4D worm semantics.** Perdurants exist, but L0 commits to a lightweight interval model (`validFrom`/`validTo`, `Instant`, `Duration`), not a general temporal calculus.
- **Deontic logic** (obligations/permissions as formal operators). Licences etc. are modeled as role meta-data, not as deontic statements.
- **Probabilistic/fuzzy membership.** Classification is crisp; uncertainty is carried as `confidence` provenance metadata, not as fuzzy set membership.
- **Belief/epistemic attitudes and provenance of *disputes*** beyond a `contested` flag + alternative-classification links (governance handles the rest).
- **Causation as a primitive.** Expressed as typed relations between perdurants (`causes`), not a logical primitive.

These exclusions are a feature: they keep the fixed set teachable to a first-year OOP student and to an AI contributor, while leaving clean extension points.

---

## 3. Authoring stereotypes — the only vocabulary L1 may use

Contributors do not write "category C" or "an anti-rigid sortal." They pick a **stereotype**. Each stereotype commits to exactly one foundational category and carries extra, machine-checkable rules. This is the operational core of Invariant 3. (Rigidity and sortality below come from UFO; a **sortal** supplies a *principle of identity* — a rule for counting and re-identifying instances; a **rigid** type is one an instance cannot stop being without ceasing to exist.)

| Stereotype | Foundational category | Sortal? | Rigid? | Supplies identity? | Role in the model | Example |
|---|---|---|---|---|---|---|
| `Kind` | Endurant/Abstract | sortal | **rigid** | **yes** | the backbone; every concrete individual instantiates exactly one `Kind` | `Person`, `Vehicle`, `Group` |
| `Subkind` | same as parent | sortal | **rigid** | inherits | a rigid specialization (true `is-a-kind-of`) | `Moped`, `Woman`, `CyclicGroup` |
| `Phase` | same as parent | sortal | **anti-rigid** | inherits | partition by *intrinsic, changeable* state | `Child`/`Adult`, `Alive`/`Dead`, `Solid`/`Liquid` |
| `Role` | Role (F) | sortal | **anti-rigid** | inherits | partition by *relational, context* classification | `Driver`, `Employee`, `CapitalCity` |
| `Category` (Mixin) | cross-cuts | **non-sortal** | rigid-mixin | **no** | multiple classification / tags spanning several `Kind`s | `CulinaryVegetable`, `Furniture`, `RedThing` |
| `RoleMixin` | Role, cross-cutting | non-sortal | anti-rigid | no | a role whose players are several `Kind`s | `Customer` (Person **or** Organization) |
| `RelationType` | Relation (E) | — | — | — | association incl. part-whole; n-ary | `orbits`, `partOf`, `borders` |
| `QualityType` | Quality (D) | — | — | — | a non-numeric attribute | `color`, `bloodType` |
| `QuantityKind` | Quantity (D) | — | — | — | a measurable quality + its Dimension | `Length`, `Mass`, `Tempo`, `Count` |
| `EventType` | Perdurant (B) | sortal | rigid | yes | a kind of process/happening | `Journey`, `Mitosis`, `NoteOccurrence` |
| `AbstractType` | Abstract (C) | sortal | rigid | yes | a kind of abstract structure/proposition | `Theorem`, `Polygon`, `PitchClass` |
| `Collection` | Collection (H) | sortal | rigid | yes | a many-as-one with its own identity | `Herd`, `Constellation`, `Chord` |
| `Enumeration` | — | — | — | — | a closed value set with stable literals | `LicenceCategory`, `BloodType` |
| `Individual` | any | — | — | — | an L2 instance / reference datum | `Earth`, `ℤ/2ℤ`, *this* person |

**The single most important rule in WMOOP falls straight out of this table:**

> Inheritance (`Subkind`) is permitted **only between rigid sortals that share a principle of identity**. `Phase`, `Role`, `Category`, and `RoleMixin` are **never** modeled by subclassing a `Kind`. They are partitions/attachments. This is what makes "roles over inheritance" a *checkable property*, not a style preference.

---

## 4. Decision rules: inheritance vs interface/trait vs composition vs role

### 4.1 The four tests

Apply these in order to any proposed relationship "B relates to A":

1. **Identity test (sortal?).** Does B keep A's way of being counted and re-identified? (One Moped *is* one Motorcycle, counted the same way.) If B counts differently (a `Chord` vs its `Note`s; an `Engine` vs its `Car`), it is **not** is-a — consider part-whole or collection.
2. **Rigidity test.** Could *this very individual* stop being a B tomorrow and still be the same individual? **Yes → anti-rigid → `Phase` or `Role`, never inheritance.** (A person stops being a `Driver`; a thing never stops being a `PhysicalObject`.)
3. **Relational test.** Does B make sense only relative to some *other* entity/context (an authority, an employer, a relationship)? **Yes → `Role`** (attach by composition, §5). If anti-rigid but *intrinsic* (age, state of matter) → **`Phase`**.
4. **Substitutability test (Liskov).** Can every B be used *everywhere* an A is expected, honoring A's contracts, with nothing removed or contradicted? **No → not inheritance** (use interface for the partial capability, or composition). **Yes, and tests 1–3 say rigid sortal → `Subkind` (inheritance).**
5. **Multiplicity test.** Must the thing be classified under **two or more independent dimensions at once** (botanical *and* culinary; shape *and* material)? **Yes → `Category`/tags (multiple classification), not a single inheritance chain.**

### 4.2 Decision flowchart (ordered rules)

Read top to bottom; stop at the first match.

1. Does it exist only as *a feature of* another entity (a measurable or qualitative characteristic)? → **`QualityType`/`QuantityKind`** (a *property*, not a class).
2. Is it fundamentally *a tie between* two or more entities? → **`RelationType`** (incl. part-whole). If it is "A is composed of / has part B," use **composition / mereology**, never inheritance.
3. Is it *a happening* with temporal parts? → **`EventType`** (Perdurant). Relate it to its participants with relations.
4. Is it outside space-time (a structure, number, proposition)? → **`AbstractType`**.
5. Is it a context-dependent, relationally-grounded hat an entity wears (fails the Rigidity + Relational tests)? → **`Role`**, attached by **composition** (§5). Never subclass.
6. Is it an intrinsic, changeable state partition (anti-rigid but *not* relational)? → **`Phase`**.
7. Does it need classification along **two+ independent axes at once**, or does it span **several Kinds**? → **`Category`/tag** (multiple classification), optionally **interfaces/traits** for shared capability.
8. Is it a *shared capability or contract* that several unrelated Kinds can offer (`Playable`, `Measurable`, `Serializable`-of-the-world-kind, `Locatable`)? → **interface / trait** (composition of behavior), not a base class.
9. Is it a genuine, stable, rigid `is-a-kind-of` that passes **all four tests (1–4 in §4.1)**? → **`Subkind` (inheritance)** — and keep it shallow (§7).
10. Otherwise → it is probably a **`Kind`** (a new root of identity) or you have mis-scoped it; ask in review.

### 4.3 Decision table (quick reference)

| If the relationship is… | …then use | …never use |
|---|---|---|
| rigid, same identity, fully substitutable `is-a-kind-of` | **Inheritance** (`Subkind`) | roles, tags |
| "can do / offers contract X" across unrelated kinds | **Interface / trait** | base class |
| "has / is made of / is composed of" | **Composition** (part-whole relation) | inheritance |
| "plays the part of X in a context" (anti-rigid, relational) | **Role** (composition, §5) | `Driver : Person` |
| intrinsic changeable state | **`Phase`** | subclass per state |
| classified on 2+ independent axes / spans kinds | **`Category` / tags** | multi-level inheritance |

### 4.4 Worked examples

**(1) Moped — inheritance, shallow.**
`Moped` → `Motorcycle` → `RoadVehicle` → `Vehicle`. Every link passes all four tests: a Moped *is* rigidly a kind of Motorcycle (never stops being one); it is counted as one vehicle; it is substitutable anywhere a Motorcycle/RoadVehicle/Vehicle is expected; it adds no contradiction (it *narrows*: ≤ 50 cc, ≤ 45 km/h). → **`Subkind` chain, depth 4** (within budget, §7).

```yaml
- stereotype: Kind
  qname: wmoop.transport.vehicles/Vehicle
  abstract: true
  properties: [ { name: wheelCount, quantityKind: wmoop.core/Count, unit: wmoop.core/one, cardinality: "1" } ]
- stereotype: Subkind
  qname: wmoop.transport.vehicles/RoadVehicle
  extends: wmoop.transport.vehicles/Vehicle
- stereotype: Subkind
  qname: wmoop.transport.vehicles/Motorcycle
  extends: wmoop.transport.vehicles/RoadVehicle
  properties: [ { name: wheelCount, const: 2 } ]        # narrows, never contradicts
- stereotype: Subkind
  qname: wmoop.transport.vehicles/Moped
  extends: wmoop.transport.vehicles/Motorcycle
  properties:
    - { name: engineDisplacement, quantityKind: wmoop.core/Volume, unit: wmoop.core/cm3, constraints: { max: 50 } }
    - { name: maxDesignSpeed,     quantityKind: wmoop.core/Speed,  unit: wmoop.core/km_per_h, constraints: { max: 45 } }
```

**(2) Tomato — multiple classification via Category/tag, NOT inheritance.**
A tomato *is* rigidly a kind of fruiting plant/berry (botanical **`Subkind`**). "Vegetable" here is *culinary* — a different, orthogonal axis — so it is a **`Category`** tag, not a parent in the identity tree. Modeling `Tomato : Vegetable : Fruit` would be dishonest (vegetable is not a botanical kind) and would fail the Multiplicity test.

```yaml
- stereotype: Subkind
  qname: wmoop.nature.plants/Tomato
  extends: wmoop.nature.plants/Berry          # botanical is-a (rigid, single identity)
  categories:                                   # orthogonal, multiple classification
    - wmoop.culinary/CulinaryVegetable
    - wmoop.nutrition/RichInLycopene
# Category definitions span many Kinds and carry no identity principle:
- stereotype: Category
  qname: wmoop.culinary/CulinaryVegetable
  appliesTo: { anyOf: [ wmoop.nature.plants/* ] }
  definition: "Plant part used savoury in cooking; a culinary, not botanical, grouping."
  provenance: [ { source: "Nix v. Hedden, 149 U.S. 304 (1893)", kind: stipulative } ]
```

Generated code: `Tomato : Berry` (inheritance) **and** `Tomato` tagged `[CulinaryVegetable, RichInLycopene]` (e.g., C# attributes / Java annotations / Python class vars / C++ type traits). One honest tree, many cross-cutting tags.

**(3) Person-as-Driver — Role via composition (full treatment in §5).**
`Driver` fails the Rigidity test (a person stops driving) and passes the Relational test (depends on a licensing authority). → **`Role`**, a reified object attached to the `Person`, never `Driver : Person`.

---

## 5. Cross-domain intersection: the Role mechanism in full

This is the mechanism by which WMOOP becomes a *connected* world model rather than a pile of disjoint domains.

### 5.1 Requirements the mechanism must satisfy

1. **Identity preservation.** The Person and its Driver-facet are the *same individual*; querying the driver's address returns the person's address. No cloning, no `Driver` copy of `Person` data.
2. **Non-destructive extension.** The Nature domain's `Person` is untouched and unaware of Transport. Transport depends on Nature; **never the reverse** (acyclic dependency, Invariant 5).
3. **Language-neutral.** The canonical form is declarative; each target language renders it idiomatically but equivalently.
4. **Multiplicity.** One entity may play **many roles simultaneously** (Driver *and* Owner *and* Employee), each independent.
5. **Time-bounded & stateful.** Each role may carry `validFrom`/`validTo`, status, and expiry, and be queried "as of" a date.
6. **Carries meta.** The role holds role-specific data (licence number, categories, issuing authority) that would pollute `Person` if pushed up.

### 5.2 Canonical language-neutral representation

**Role *type* definition (L1, in the Transport domain, `wmoop.doc` single source of truth):**

```yaml
stereotype: Role
id: wmid:01JABCXYZ0000000000000000
qname: wmoop.transport.driving/Driver
label: Driver
definition: "A person authorised to, and in the state of being entitled to, operate a road vehicle."
provenance:
  - { source: "Directive 2006/126/EC on driving licences", kind: definitional }
played_by:                                   # allowed players (the 'filler' / base)
  anyOf: [ wmoop.nature.people/Person ]
relationalGround:                        # roles are relationally dependent
  dependsOn: wmoop.transport.driving/DrivingAuthorisation
antiRigid: true
timeBounded: true
properties:
  - { name: licenceNumber,    type: String, cardinality: "1", identifying: true }
  - { name: licenceCategories, type: Enum, enum: wmoop.transport.driving/LicenceCategory, cardinality: "1..*" }
  - { name: issuedOn,         type: Date, cardinality: "1" }
  - { name: expiresOn,        type: Date, cardinality: "0..1" }
  - { name: issuingAuthority, type: Reference, target: wmoop.geography.admin/Jurisdiction, cardinality: "1" }
  - { name: status,           type: Enum, enum: wmoop.transport.driving/LicenceStatus, cardinality: "1", default: VALID }
```

**L2 instance — one Person, three simultaneous, time-bounded roles:**

```yaml
individual:
  instanceOf: wmoop.nature.people/Person          # ONE identity principle, unchanged
  id: wmid:01JADPERSONADA00000000000
  label: "Ada L."
  plays:
    - role: wmoop.transport.driving/Driver
      id: wmid:01JADROLEDRV0000000000000
      licenceNumber: "RO-B-12345678"
      licenceCategories: [ B, A2 ]
      issuedOn: 2019-04-01
      expiresOn: 2029-04-01
      issuingAuthority: wmoop.geography.admin/RO
      validFrom: 2019-04-01
      status: VALID
    - role: wmoop.transport.ownership/VehicleOwner
      id: wmid:01JADROLEOWN0000000000000
      owns: wmid:01JADVEHMOPED00000000000
      validFrom: 2021-06-15
    - role: wmoop.org.employment/Employee
      id: wmid:01JADROLEEMP0000000000000
      employer: wmid:01JADORGACME00000000000
      validFrom: 2020-01-10
      validTo:   2023-12-31                     # time-bounded; now inactive
```

Note what this representation guarantees: the person is `instanceOf Person` **once** (identity preserved); the roles are *attachments* with their own `wmid`s and their own meta; three roles coexist; two different domains (Transport, Org) attached roles to a Nature entity **without the Nature domain depending on them**.

### 5.3 Pseudo-code (language-neutral) and idiomatic C#

**Language-neutral:**

```
interface RolePlayer:
    roles: Set<Role>
    func play(r: Role)
    func rolesOf<T: Role>(at: Instant = now) -> List<T>

abstract Role:
    player:     EntityRef
    validFrom:  Date?
    validTo:    Date?
    func isActive(at: Instant) -> Bool = (validFrom..validTo).contains(at)

class Driver extends Role:                       # extends Role, NOT Person
    licenceNumber:     String
    licenceCategories: Set<LicenceCategory>
    issuedOn:          Date
    expiresOn:         Date?
    func canDrive(cat: LicenceCategory, at: Instant) -> Bool =
        isActive(at) and (expiresOn == null or at <= expiresOn) and cat in licenceCategories
```

**Idiomatic C# (aligning with `wmoop.net`):**

```csharp
public interface IRole {
    Guid PlayerId { get; }
    DateOnly? ValidFrom { get; }
    DateOnly? ValidTo   { get; }
    bool IsActiveOn(DateOnly date) =>
        (ValidFrom is null || date >= ValidFrom) && (ValidTo is null || date <= ValidTo);
}

// Driver extends the Role contract — NOT Person. Composition preserves identity.
public sealed record Driver(
    Guid PlayerId,
    string LicenceNumber,
    IReadOnlySet<LicenceCategory> Categories,
    DateOnly IssuedOn,
    DateOnly? ExpiresOn = null,
    DateOnly? ValidFrom = null,
    DateOnly? ValidTo   = null) : IRole
{
    public bool CanDrive(LicenceCategory cat, DateOnly on) =>
        IsActiveOn(on) && (ExpiresOn is null || on <= ExpiresOn) && Categories.Contains(cat);
}

public interface IRolePlayer { IReadOnlyCollection<IRole> Roles { get; } }

public static class RolePlayerExtensions {
    public static IEnumerable<T> RolesOf<T>(this IRolePlayer p, DateOnly? on = null) where T : IRole =>
        p.Roles.OfType<T>().Where(r => on is null || r.IsActiveOn(on.Value));
}

// Person (Nature domain) implements IRolePlayer; it knows nothing about Driver.
var today = DateOnly.FromDateTime(DateTime.UtcNow);
bool licensedToDriveB = ada.RolesOf<Driver>(today).Any(d => d.CanDrive(LicenceCategory.B, today));
bool alsoOwner        = ada.RolesOf<VehicleOwner>(today).Any();
```

The *same* shape generates mechanically into: **Java** (`interface IRole` default methods + `record Driver implements IRole`), **Python** (`typing.Protocol` + `@dataclass(frozen=True) class Driver`), **C++** (`struct IRole` abstract + value-type `Driver`, `player.rolesOf<Driver>()` via templates). "Write once (the role in `wmoop.doc`), replicate everywhere" is thus code generation, not re-authoring (Invariant 1).

### 5.4 Dependency direction and versioning

- `wmoop.transport.driving` **depends on** `wmoop.nature.people` (it references `Person`). The reverse edge is forbidden; CI rejects a cycle.
- The cross-domain reference is a **typed, versioned link**: `played_by.anyOf: [ wmoop.nature.people/Person@^2 ]`. If Nature publishes `Person@3` with a breaking change, Transport keeps compiling against `^2` until it migrates — crowd-sourced domains evolve independently (Invariant 5).
- A role may allow several player Kinds via `RoleMixin` (e.g., `Customer` plays `Person` **or** `Organization`); the generator emits a marker interface both Kinds implement.

---

## 6. Identity, naming, and property typing

### 6.1 Identity scheme

Every concept and every instance carries **two identifiers** with different jobs, because a crowd-sourced, multi-language ontology must survive renames, translations, merges, and forks. The QName grammar is defined canonically in the **Normative Constants** table in `GOVERNANCE.md`, which is the single source of truth for the ID grammar.

| Identifier | Form | Mutability | Purpose |
|---|---|---|---|
| **Opaque id** (`wmid`) | `wmid:` + Crockford base32 **ULID** (26 chars, time-sortable) | **immutable forever** | opaque stable-identity backing (optional in v0); the QName is the working identifier and all examples use it |
| **QName** (qualified name) | `wmoop.{domain-path}/{LocalName}` e.g. `wmoop.nature.animals/Dog` | stable *by policy*; change only via deprecation + alias | human-readable primary address, used in docs and code generation |
| **Module version** | SemVer on the domain module (`nature.animals@2.3.0`) | per release | lets references pin (`@2.3.0`) or range (`@^2`) |
| **Label(s)** | `prefLabel` + localized `altLabel` (lang-tagged) | freely editable | display names; **never** an identity key |

**Merge & lifecycle policy** (essential for an open community):
- To rename: keep the `wmid`, change the QName, record the old QName in `altQName`, emit a `replacedBy`/`sameAs` so old links resolve.
- To merge duplicates (two contributors modeled `Automobile` and `Car`): keep one `wmid`, mark the other `deprecated: true` with `sameAs: <survivor wmid>`; CI redirects references.
- To deprecate: `status: deprecated`, `deprecatedSince`, optional `supersededBy`. Deprecated concepts are never deleted (would break downstream pins), only tombstoned.
- IDs are **minted decentrally** (ULID needs no central server), so forks and offline contributors never collide — a deliberate match to the open-source, AI-assisted contribution model.

### 6.2 Naming conventions

| Element | Convention | Example |
|---|---|---|
| Domain / module path | lowercase dotted segments, singular | `nature.animals`, `transport.driving` |
| `Kind`/`Subkind`/`Role`/`EventType`/`AbstractType`/`Collection`/`Category` | **PascalCase**, **singular** noun | `Moped`, `Driver`, `Journey`, `Theorem`, `Herd`, `CulinaryVegetable` |
| Property / quality / quantity | **camelCase**, noun | `wheelCount`, `maxDesignSpeed`, `bloodType` |
| `RelationType` | **camelCase verb phrase**, reads source→target | `partOf`, `orbits`, `bordersWith`, `teaches` |
| Role end / participant name | camelCase noun | `driver`, `employer`, `whole`, `part` |
| `Enumeration` literal | **UPPER_SNAKE_CASE** | `LicenceCategory.A2`, `BloodType.O_NEGATIVE` |
| `Unit` symbol id | lowercase as published; symbol field separate | `km_per_h` (id), `"km/h"` (symbol) |
| Boolean property | `is`/`has`/`can` prefix | `isNavigable`, `hasChloroplasts`, `canFly` |

Rules: no abbreviations unless an accepted standard term; names are in English with localized labels alongside; a name expresses *what it is*, never *what it is used for* (that is a Role/Category).

### 6.3 Property typing

A property on a Type is one of these **typed slots**:

| Property form | Declares | Required keys |
|---|---|---|
| **Datatype** | a primitive value | `type` (from the primitive set) |
| **Enum** | a value from a closed `Enumeration` | `enum` (ref), optional `extensible: false` |
| **Reference** | a typed link to another concept/instance | `target` (type ref), optional `inverse` (relation name) |
| **Quantity** | a magnitude | `quantityKind`, `unit`, optional `constraints` |
| **Composition** | an owned part (part-whole) | `partType`, `lifecycle: dependent` |

**Primitive datatype set (closed, v1):** `Boolean`, `Integer`, `Decimal`, `String`, `Text` (long), `LangString` (localized), `Date`, `DateTime`, `Instant`, `Duration`, `URI`, `Identifier`. (Numeric measurements never use `Decimal` directly — they use **Quantity**, §6.4.)

**Every property carries:**
- `cardinality` — one of `0..1`, `1`, `0..*`, `1..*`, or explicit `m..n`. **Required = minimum ≥ 1.**
- optional modifiers: `default`, `immutable` (set once), `identifying` (contributes to natural key), `unique`, `derived: <expression>`, `ordered` (for `*` collections), `constraints` (`min`/`max`/`pattern`/`enumSubset`).
- `definition` **and** `provenance` — **both are mandatory on every property**, not only on
  "non-obvious" ones. A structural or naming choice is still sourced honestly with
  `kind: definitional`/`convention` (rather than left blank); a sourced claim uses
  `kind: sourced` with a resolvable `source`.

**Provenance object** (required on every concept, role, enumeration **and property** definition, and
on L2 facts): `{ source: <citation/URI>, kind: sourced | definitional | convention, retrievedOn?: Date, confidence?: 0..1 }`. This operationalizes Invariant 4 ("facts are sourced") while allowing `definitional` for definitions and `convention` for naming and modelling conventions — so *nothing is unsourced*, but a modelling choice is never dressed up as a `sourced` citation.

### 6.4 Quantities, units, and dimensional checking

This is how WMOOP refuses to let the world be modeled in naked `double`s.

- A **`QuantityKind`** (e.g., `Length`, `Mass`, `Time`, `Speed`, `Count`, `Angle`) has a **`Dimension`**: a 7-vector over the SI base dimensions **(L, M, T, I, Θ, N, J)** = (Length, Mass, Time, ElectricCurrent, Temperature, AmountOfSubstance, LuminousIntensity), plus the dimensionless case `(0,0,0,0,0,0,0)` used by `Count`, `Ratio`, `Angle`.
- A **`Unit`** belongs to one `QuantityKind` and declares a conversion to the kind's canonical (SI) unit: `{ factor, offset }` (offset supports °C↔K). E.g., `km_per_h` → `m_per_s` with `factor: 0.277…`.
- A **derived `QuantityKind`** declares a dimension *formula*: `Speed = Length · Time⁻¹` → dimension `(1,0,-1,0,0,0,0)`.

**CI dimensional checks (machine-enforced):**
1. A `Quantity` property's `unit` must belong to its `quantityKind` (reject `mass` measured in `km/h`).
2. Any `derived` expression combining quantities must be **dimensionally consistent**: the dimensions of the right-hand side must reduce to the declared left-hand dimension. (e.g., `power = force · velocity` ⇒ dimensions add correctly; otherwise CI fails the build.)
3. Comparisons/relations between two quantities require equal dimensions (`wheelCount < maxSpeed` is rejected).
4. The code generator emits **strong value types** (`Length`, `Mass`, `Speed` structs) in each language rather than primitives, so `var d = speed * time;` is a `Length` at compile time, and `length + mass` fails to compile — the dimensional guarantee is carried into generated code, not just the model.

```yaml
- stereotype: QuantityKind
  qname: wmoop.core.quantities/Speed
  dimension: { L: 1, T: -1 }                 # all others 0
  canonicalUnit: wmoop.core.units/m_per_s
- stereotype: Unit
  qname: wmoop.core.units/km_per_h
  of: wmoop.core.quantities/Speed
  symbol: "km/h"
  toCanonical: { factor: 0.2777778, offset: 0 }
```

---

## 7. Keeping is-a hierarchies shallow and honest

Deep, dishonest inheritance is the single biggest risk to a crowd-sourced world model: it is contagious (every contributor copies the pattern) and brittle (fragile base class). L0 enforces discipline.

### 7.1 Rules and budgets

1. **Rigid-sortal-only.** `Subkind` is allowed only between rigid sortals sharing identity (§3). Everything anti-rigid or non-sortal uses `Phase`/`Role`/`Category`/interface. *This alone removes most bad inheritance.*
2. **Liskov is mandatory and checkable.** A `Subkind` may only **weaken preconditions, strengthen postconditions, preserve invariants, and never remove or contradict** an inherited member. A subtype that must throw "not supported" for an inherited operation is **not** a subtype — refactor to an interface or role.
3. **Narrow, don't contradict.** A subkind may restrict a property's range (`Moped.maxDesignSpeed ≤ 45`) but may not redefine its type, unit, or meaning, nor flip a Boolean invariant.
4. **Depth budget.** From a domain root to a concrete leaf, depth 5 triggers a CI *warning* and a required justification, and depth > 6 is a CI *error*. Most real "is-a-kind-of" chains in the world are 3–5 deep; longer usually hides phases, roles, or parts masquerading as subclasses.
5. **Favor composition and capability.** Prefer `has-a` (part-whole), `plays` (role), `can-do` (interface/trait) to `is-a`. When tempted to subclass to add behavior, ask: *is this new behavior an essence of a new kind, or a capability?* Capability → interface/trait.
6. **Thin, stable base types.** A base `Kind` declares only members true of **every** instance for **all time** (the rigid invariants). Optional, role-specific, phase-specific, or rarely-shared members **must not** be pushed up. This is the structural defense against the fragile base class: bases change rarely because they contain only what cannot vary.
7. **Open for extension, closed for mutation.** New variants attach via new `Subkind`s, `Category` tags, roles, or interfaces — not by editing a published base. Published bases evolve only via SemVer-breaking releases.

### 7.2 Anti-pattern catalog (reject on sight)

| Anti-pattern | Why wrong | Correct modeling |
|---|---|---|
| `Driver : Person` | anti-rigid, relational | `Role Driver` by composition (§5) |
| `Square : Rectangle` with mutable sides | breaks Liskov (setWidth violates invariant) | separate immutable `Square`/`Rectangle`, or `Rectangle` with a `isSquare` derived property; shape as `AbstractType` |
| `Penguin : Bird` overriding `fly()` to throw | removes an inherited contract | `canFly` capability / interface `Flying`; `Bird` does not promise flight |
| `Tomato : Vegetable : Fruit` | mixes botanical identity with culinary category | botanical `Subkind` + culinary `Category` tag (§4.4) |
| `Engine : Car` (to "inherit the car's data") | part, not kind | `partOf(Engine, Car)` composition |
| `Adult : Person` as a subclass | anti-rigid intrinsic state | `Phase Adult/Child` |
| 9-level `LivingThing → … → Dog` chain | depth hides phases/roles | collapse to rigid kinds; move variability to tags/phases |
| `GoldCustomer : Customer : Person` | role + tier + identity conflated | `Role Customer` + `tier: Enum` property/`Phase` |

### 7.3 The substitution checklist (CI-enforceable gate for any new `Subkind`)

A proposed `B : A` passes only if **all** hold (CI checks the structural ones; review confirms the semantic ones):

- [ ] B is a **rigid sortal** and A is its (rigid) sortal super (stereotype check).
- [ ] B and A share a **principle of identity** (same `Kind` root).
- [ ] Every required member of A is present and **not weakened** in B (contract check).
- [ ] B **adds or narrows**; it removes/contradicts nothing (no overridden member throws "unsupported," no invariant flipped).
- [ ] The "**always / every / for its whole life**" sentence is true: *"Every B is, for its entire existence, a kind of A."*
- [ ] Resulting depth ≤ budget (§7.1 rule 4).

Failing any item routes the contributor to §4's flowchart to pick Role, Phase, Category, interface, or composition instead.

---

## 8. Machine-checkable Definition of Done (how CI validates L0 conformance)

So that **humans and AI can contribute safely against an automated bar** (Invariant 6), every pull request to a domain module is validated by CI against L0. A contribution is *Done* when all checks pass:

**Structural / schema checks**
1. Every concept has a `wmid` (valid ULID), a `qname` (matching naming conventions §6.2), a `prefLabel`, a `definition`, and `provenance`.
2. Every property has a `cardinality`; every `Quantity` has a valid `quantityKind` + compatible `unit`.
3. Every `wmid`/`qname` reference resolves (no dangling links); versioned references satisfy their pins.
4. The domain dependency graph is **acyclic**; no domain references a not-yet-depended module.

**Stereotype / modeling-discipline checks**
5. Every `Subkind` passes the §7.3 substitution gate (rigid sortal, shared identity, narrows-not-contradicts, depth ≤ budget).
6. No `Role`/`Phase`/`Category` is expressed via `Subkind`; no anti-rigid or non-sortal type appears in an inheritance edge.
7. Every `Role` declares `plays` (allowed players) that resolve, and (if `timeBounded`) a validity model.

**Semantic / quantity checks**
8. All `derived` expressions and quantity comparisons are **dimensionally consistent** (§6.4).
9. Enum references resolve; `required` properties (`min ≥ 1`) are populated on L2 instances.
10. Provenance `kind` is valid; empirical facts carry a resolvable `source`.

**Round-trip / generation checks (Invariant 1)**
11. Code generation succeeds for every target language from this model.
12. **Conformance tests** generated from the WM pass in each per-language repo (`wmoop.net`, `wmoop.java`, `wmoop.py`, `wmoop.cpp`): the generated code's structure matches the model (names, hierarchy depth, role composition, units), proving no manual drift.

An AI contributor is therefore handed an unambiguous, automatable target: *produce a declarative diff that passes checks 1–12.* No subjective taste is required to pass review for the mechanical parts; human review focuses only on definitional correctness and classification judgment.

---

## 9. Refinements to the Core Architectural Invariants

I **endorse all six** invariants and do not deviate from them. I sharpen three and add two, all consistent with the originals:

- **Invariant 1 (schema-first) — sharpened.** Generation must be **conformance-tested round-trip** (DoD checks 11–12), and each language repo must provide **non-clobbered extension points** (C# `partial`/extension methods, Java/Python/C++ equivalents) so hand-written idiomatic helpers coexist with generated code without manual re-authoring of the *model*. "Generated" ≠ "frozen against idiom"; it means the *conceptual model* is never hand-copied.
- **Invariant 3 (composition/roles over inheritance) — made checkable.** Elevated from a principle to a **stereotype system** (`Kind`/`Subkind`/`Phase`/`Role`/`Category`/`RoleMixin`, §3) with **rigidity + sortality** as the discriminators, and a CI substitution gate (§7.3). "Roles over inheritance" is now a property the validator can enforce, not a reviewer's opinion.
- **Invariant 4 (every concept sourced) — refined.** Provenance is **typed** (`sourced | definitional | convention`) with optional `confidence`, so definitions and naming/modelling conventions are not forced to cite an external source, while `sourced` facts must.
- **Added — Invariant 7 (ontological completeness):** L0 must represent **endurants, perdurants, and abstracts** as first-class, not physical-objects-with-properties only. (Without this, Math and Music cannot be modeled; it is implicit in the mission and is now explicit.)
- **Added — Invariant 8 (identity lifecycle & open-world stance):** identity is an **immutable opaque `wmid` + stable QName**, with first-class **deprecation/`sameAs`/`replacedBy`** merge policy; the model is **open-world for facts** (absence of a fact ≠ its falsehood) but **closed-world for schema conformance** (the DoD checks are exhaustive and binding). A crowd-sourced ontology *will* accumulate duplicates and renames; the identity lifecycle must be designed in, not bolted on.

---

## 10. Open questions (for other sections / governance)

1. **Normative serialization & reasoning depth.** Commit to plain JSON + JSON-LD context, or adopt an OWL 2 profile (e.g., OWL 2 QL/EL) + **SHACL** for constraints? JSON-LD+SHACL likely best balances accessibility (students, AI) with checkability; full OWL reasoning may be more than needed and harder for newcomers. *Recommendation leans JSON-LD + SHACL; needs ratification.*
2. **Validator implementation language** and whether it ships as a reusable CLI/GitHub Action (needed for the DoD to be real on day one).
3. **Governance of contested classifications** beyond the `contested` flag + alternative links: who adjudicates, and how `sameAs`/merge decisions are approved.
4. **Temporal granularity for Phases/Roles** in v1 — are `Phase`s in scope for the first release, or deferred behind `Role`s and enum `status` fields?
5. **n-ary relations and relation attributes** (a `teaches` relation that itself has a `semester`): reify all non-binary relations as entities, or allow attributed associations? (Reification is cleaner for cross-language generation.)
6. **Internationalization** of `prefLabel`/`definition`: required languages at submission, and handling of non-Latin scripts in `altLabel`.
7. **Generated-code escape hatches**: the exact per-language extension-point convention (so Invariant 1's "non-clobbering" is concrete for `wmoop.net` first, then mirrored).
8. **ID minting at scale**: ULID is decentralized and sufficient, but do we also want a human-facing short-code registry for teaching (e.g., `WM-NAT-0001`) mapped to `wmid`s?