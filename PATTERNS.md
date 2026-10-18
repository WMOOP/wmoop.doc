# WMOOP — Patterns & Practices

**The definitive guide to the object-oriented principles and design patterns the World Map Object-Oriented Programming project uses and recommends.**

> **Status:** Normative for all contributions. If a contribution in any language departs from this guide, the departure must be justified in review.
>
> **Audience:** Contributors writing or reviewing WMOOP code in C#, Java, Python, or C++ — and anyone extending the canonical **WML** model in `wmoop.doc`.

---

## 0. Orientation — why this document exists

WMOOP models *the world* as a schema-first, language-neutral object model. The canonical model is written **once** as **WML** (the DSL in `wmoop.doc`) — the single source of truth — and idiomatic C#, Java, Python, and C++ data classes are **generated** from it and conformance-tested.

The model is layered:

| Layer | Name | Content |
|-------|------|---------|
| **L0** | Meta-model | Foundational categories: `Entity`, `Role`, `Quantity`, `ConceptId`, the stereotypes below |
| **L1** | Domain models | Declarative classes, properties, relations, roles (`Person`, `Vehicle`, `Country`…) |
| **L2** | Instances | Individuals and the registries that hold them (`ada-lovelace`, `piaggio-ciao`…) |

Every modelling fact is expressed through a small, fixed vocabulary of **meta-model relations / stereotypes**. This vocabulary is the spine of the whole guide — every pattern below is justified by *which stereotype it realizes*:

| Stereotype | Meaning | Rigidity |
|------------|---------|----------|
| `subclass_of` | True, shallow, Liskov-clean **is-a** | Rigid, substitutable |
| `instance_of` | An L2 individual of an L1 class | — |
| `part_of` | Mereology / containment (a whole has parts) | Structural |
| `has_role` | A **contextual facet** a thing gains or loses | Anti-rigid, non-exclusive |
| `has_quality` | A measurable or descriptive **attribute** | — |
| `classified_as` | A **perspectival** category/tag; supports multiple, contested classification | Non-rigid |
| `association` | A relation between entities, possibly n-ary, possibly with its own attributes | — |

### The prime directive

> **Composition + interfaces/traits + Roles over deep inheritance.**
>
> Inheritance is reserved for rigid, substitutable **is-a** and kept **shallow** (depth budget ≈ 4 as the target; the CI gate is depth ≤ 6, warning at depth 5). Cross-domain intersection is expressed with **Role objects**: a `Person` (Nature domain) *acquires* a `Driver` role (Transport domain) — **never** `Driver : Person`.

### The engineering standard

> **Across every WMOOP repository, use the best, most-established methods, concepts and patterns — at the right level of abstraction.**

This is binding for **all** repos (`wmoop.doc`, `wmoop.net`, and every generated binding and tool), not just this one. In practice:

- **Proven over clever.** Reach first for well-understood, named designs — [SOLID](#11-solid), [GRASP](#12-grasp), the GoF patterns catalogued below, and each language's own idioms — not ad-hoc constructions. Reinventing a standard pattern badly is a reviewable defect.
- **Depend on abstractions.** Program to interfaces/traits, roles and specifications, not concrete generated types ([DIP](#11-solid), §1.3); remove cross-language duplication by **generation**, never copy-paste.
- **…but abstract only to the altitude a real use case demands.** Abstraction is a tool, not a goal: **KISS and YAGNI win ties** ([§1.3](#13-supporting-principles)). No speculative layers, no indirection without a second concrete user — **[premature abstraction](#4-anti-patterns) is itself an anti-pattern** and is reviewed like any other. (The whitepaper tracks over-engineering as a project risk.)
- **Idiomatic per language.** One model generates C#, Java, Python and C++; each binding must read as natural code *in that language*, not as a transliteration.
- **Justify departures.** Consistent with this guide's normative status, a deviation from a recommended pattern or abstraction is allowed only when argued in review.

### Invariants every concept obeys

1. A concept is written **once** (in WML); cross-language duplication is removed by **generation**, not copy-paste.
2. Inheritance models a genuine, permanent, substitutable kind-of; everything else is a role, a quality, a classification, or an association.
3. Facets are roles attached by composition and are non-permanent, non-exclusive.
4. Every concept carries a stable **`ConceptId`**, a **name**, a **definition**, and **provenance**; every measurable property carries **units** — no bare numbers.

### The question this guide must answer head-on

> **If the data classes are generated from the schema, where does behaviour (algorithms / operations) live?**

Stated plainly so it is never lost: **behaviour lives in hand-written operations *outside* the generated data model.** The three load-bearing homes for behaviour are **Visitor** (double dispatch), **Strategy** (swappable algorithms), and **Specification** (composable rules), plus designated per-language extension points (partial classes, extension methods, mixins, free functions). The generated data stays **stable and regenerable**; behaviour evolves independently. [§2.3](#23-visitor--double-dispatch--the-home-of-behaviour), [§2.4](#24-strategy), [§2.5](#25-specification), and especially [§3](#3-patterns-and-the-generation-gap) make this concrete.

### The Core API this guide is written against

All C# snippets are **net8.0**, `nullable enable`, file-scoped namespaces, dependency-free (BCL only), and consistent with the shipped `Wmoop.Core` kernel:

```csharp
public readonly struct ConceptId : IEquatable<ConceptId>        // value identity; "wmoop.<domain>/Name"
public readonly struct Quantity  : IEquatable<Quantity>         // (Value, Unit) — never a bare number
public abstract class  Entity                                   // Id : ConceptId, Name : string
public interface       IRole      { ConceptId RoleType; Entity? Subject; }
public abstract class  Role : IRole                             // AttachTo(subject) is internal
public interface       IHasRoles  { AddRole<T>(T); HasRole<T>(); GetRole<T>(); Roles; }
public sealed class    RoleContainer : IHasRoles                // composed, not inherited
```

---

## 1. Principles

### 1.1 SOLID

Each principle below is stated once in general terms, then pinned to a concrete WMOOP application.

| Principle | WMOOP application (one line) |
|-----------|------------------------------|
| **S** — Single Responsibility | A generated data class holds **only state** for one concept; algorithms live in their own visitor/strategy/specification type — one reason to change each. |
| **O** — Open/Closed | New behaviour is added by writing a **new visitor or specification**, never by editing a generated class; new facets by adding a **new `Role`**, not by widening a base. |
| **L** — Liskov Substitution | `subclass_of` is admitted **only** when the subtype honours every base guarantee — `Moped` *is-substitutable-for* `Vehicle`; `Driver` is **not** substitutable for `Person`, so it is a role. |
| **I** — Interface Segregation | Capabilities are small, focused contracts — `IHasRoles`, `IVisitor<T>`, `ISpecification<T>` — so a type implements only what it truly offers. |
| **D** — Dependency Inversion | Nature knows nothing of Transport; `OwnerRole` depends on the `Vehicle` abstraction, and high-level operations depend on `IVisitor`/`ISpecification`, not concrete classes. |

### 1.2 GRASP

| Pattern | WMOOP application |
|---------|-------------------|
| **Information Expert** | The object that owns the data answers the question: `DriverRole.CanDrive(...)` lives on the role that holds the licence dates, not on `Person`. |
| **Creator** | Factories/builders that *aggregate or contain* a part create it — a `CountryBuilder` creates the `County` parts it will hold (`part_of`). |
| **Low Coupling** | Cross-domain links go through roles and interfaces, so Nature ⟂ Transport; generated classes never reference behaviour types. |
| **High Cohesion** | One concept = one class of pure state; one algorithm = one visitor. Nothing mixes "what a thing is" with "what you do to it". |
| **Controller** | A per-domain *registry / service* (L2) coordinates instance creation and lookup, keeping use-case flow out of the data model. |
| **Polymorphism** | Variant behaviour is dispatched by type, not by `switch`-on-tag: the `Vehicle` hierarchy's `Classification`, and visitor double dispatch over the concept tree. |
| **Pure Fabrication** | `RoleContainer`, `ConceptRegistry`, and visitors are invented (not domain concepts) to keep cohesion high and coupling low. |
| **Indirection** | Roles and adapters interpose between domains and between the canonical model and external datasets (Wikidata), decoupling both sides. |
| **Protected Variations** | The WML schema + generated interfaces form a stable seam; regeneration and external-data drift are absorbed behind it. |

### 1.3 Supporting principles

**Composition over inheritance.** The single most important rule. `Person` *has-a* `RoleContainer`; it does not inherit `Driver`. Deep trees are brittle and force a thing into exactly one lineage; the world is not shaped that way (a person is simultaneously a driver, an owner, an employee, a patient). Inheritance depth budget: **≈ 4** as the target (`Vehicle → RoadVehicle → Motorcycle → Moped` is at the limit); the CI gate is depth ≤ 6, warning at depth 5.

**Program to interfaces.** Callers depend on `IHasRoles`, `IRole`, `ISpecification<T>`, `IVisitor<T>` — never on a concrete generated class where an abstraction exists. This is what lets behaviour be swapped and the data be regenerated.

**Immutability & value objects.** `ConceptId` and `Quantity` are `readonly struct`s with value equality and no setters. A `ConceptId` is *identity*; a `Quantity` is *a measured value*. Neither has a lifecycle — two `Quantity(45, "km/h")` are the same value, full stop. Generated state is init-only; change produces a new object, not a mutation of identity.

**Law of Demeter.** Talk to immediate collaborators. Prefer `person.GetRole<DriverRole>()?.CanDrive("B", today)` — one hop to the role, which is the information expert — over reaching through a chain of getters to pull licence fields up into `Person` and compute there (that would be *feature envy*, §4).

**Fail-fast / guard clauses.** Constructors validate at the boundary and throw immediately: `ConceptId` rejects blank values; `Quantity` rejects a missing unit; `DriverRole` rejects an expiry before issue. Illegal objects never come into existence.

**DRY via codegen.** DRY in WMOOP is *not* "don't repeat a line of C#" — it is "**don't repeat a concept across languages**." The concept is defined once in WML and projected into every target. Hand-copying a class from the C# port into the Java port is the forbidden duplication; generation is the cure. (See [§3](#3-patterns-and-the-generation-gap).)

**KISS / YAGNI.** `Quantity` carries a unit *symbol*, not a full dimensional-analysis engine — that is a documented future L0 extension, added when a use case demands it, not speculatively. A dimensionless count (wheels, legs) stays a plain `int`; do not wrap it in `Quantity` just for symmetry.

**Make illegal states unrepresentable.** Push invariants into the type system so bad states cannot be built, not merely detected later:

```csharp
namespace Wmoop.Core;

// A measured property is a Quantity (unit-bearing) BY TYPE — there is no overload
// that accepts a bare double, so "45" with no unit is a compile error, not a bug.
public sealed class EngineSpec
{
    public Quantity Displacement { get; }            // cannot be constructed without a unit
    public EngineSpec(Quantity displacement) => Displacement = displacement;
}
// new EngineSpec(new Quantity(49, "cc"));   OK
// new EngineSpec(49);                        does not compile — illegal state unrepresentable
```

A role that has not been granted has `Subject == null` *by design*, and `AttachTo` is `internal` and single-shot — the kernel is the only thing that can bind a role, and it can never silently re-point one. The illegal state ("a role attached to two subjects") cannot be reached from outside.

---

## 2. Design-pattern catalog

Each entry gives: **Intent**, a concrete **WMOOP use case**, the **meta-model stereotype** it realizes, an **idiomatic C# snippet** (≤ 25 lines, dependency-free), and **When NOT to use**.

### 2.1 Role Object — *the `Person → Driver` crux*

**Intent.** Attach, and later detach, a context-dependent facet to an object without changing its class, so one object can play many independent roles at once.

**WMOOP use case.** A `Person` (Nature) becomes a `Driver` and simultaneously an `Owner` (Transport) — temporary, non-exclusive facets that biology must know nothing about.

**Realizes.** `has_role`.

**WML keyword.** In the model a role is declared with `played_by` (rendered `playedBy` in the XML projection); the `AddRole`/`HasRole`/`GetRole`/`IHasRoles` members below are the **generated** C# runtime accessors, not model keywords.

```csharp
using Wmoop.Core;
namespace Wmoop.Transport;

// The facet is its OWN object with its OWN state (licence), bound to a subject by
// composition. Never "DriverRole : Person".
public sealed class DriverRole : Role
{
    public static readonly ConceptId TypeId = new("wmoop.transport.driving/Driver");
    public override ConceptId RoleType => TypeId;

    public string LicenceNumber { get; }
    public IReadOnlyList<string> Categories { get; }
    public DateOnly IssueDate { get; }
    public DateOnly ExpiryDate { get; }

    public DriverRole(string licence, IEnumerable<string> categories,
                      DateOnly issue, DateOnly expiry)
    {
        if (string.IsNullOrWhiteSpace(licence)) throw new ArgumentException("licence required");
        if (expiry < issue) throw new ArgumentException("expiry precedes issue");
        LicenceNumber = licence; Categories = categories.ToArray();
        IssueDate = issue; ExpiryDate = expiry;
    }
    // Information Expert: the role answers the question about its own data.
    public bool CanDrive(string category, DateOnly on) =>
        on >= IssueDate && on <= ExpiryDate &&
        Categories.Contains(category, StringComparer.OrdinalIgnoreCase);
}

// Granting and querying, through the capability interface (see RoleContainer):
//   ada.AddRole(new DriverRole("RO-AB-123456", new[]{"AM","B"}, issue, expiry));
//   if (ada.GetRole<DriverRole>()?.CanDrive("B", today) == true) { ... }
```

**When NOT to use.** When the facet is **permanent and definitional** (a `Person` *is* always a `Homo sapiens` — that is `subclass_of`, not a role), or when only one facet can ever apply and it never changes. Over-rolifying rigid kinds just adds indirection.

### 2.2 Composite — *`part_of` hierarchies*

**Intent.** Treat an individual object and a composition of objects uniformly through a single interface, so clients walk a whole/part tree without special-casing leaves.

**WMOOP use case.** Geography: `Country` contains `County` contains `City`. Also biological part-of (organism → organ → tissue) and a musical `Score → Movement → Measure`. Same shape, one abstraction.

**Realizes.** `part_of`.

```csharp
using Wmoop.Core;
namespace Wmoop.Geography;

// A place is a part of at most one whole and may contain parts — uniform treatment.
public abstract class Place : Entity
{
    private readonly List<Place> _parts = new();
    protected Place(ConceptId id, string name) : base(id, name) { }

    public IReadOnlyList<Place> Parts => _parts;
    public Place Add(Place part) { _parts.Add(part); return this; }   // Creator + fluent

    // Default recursive aggregation; a leaf contributes itself, a whole its parts.
    public virtual int SettlementCount() =>
        _parts.Count == 0 ? (this is City ? 1 : 0)
                          : _parts.Sum(p => p.SettlementCount());
}

public sealed class Country : Place { public Country(ConceptId id, string n) : base(id, n) { } }
public sealed class County  : Place { public County (ConceptId id, string n) : base(id, n) { } }
public sealed class City    : Place { public City   (ConceptId id, string n) : base(id, n) { } }
//   var ro = new Country("wmoop.geography/RO", "Romania").Add(new County("wmoop.geography/RO-CJ", "Cluj")
//               .Add(new City("wmoop.geography/RO-CJ-cluj", "Cluj-Napoca")));
```

**When NOT to use.** When the "parts" are really **associations** with their own attributes (membership with a start date), or when leaf and composite genuinely need different client-facing contracts — forcing uniformity then leaks "I am a leaf, don't call that" exceptions.

### 2.3 Visitor + double dispatch — *the home of behaviour*

**Intent.** Add new operations over a fixed object structure without modifying the classes in it. The structure exposes an `Accept` hook; each operation is a separate visitor; the right method is chosen by **double dispatch** (first on the element type, then on the visitor).

**WMOOP use case.** **This is the direct answer to "where does behaviour live when data classes are generated?"** The generated concept classes are inert state with a one-line, generated `Accept`. Every algorithm — rendering, validation, export to Wikidata, cost estimation, a geography census — is a hand-written visitor *outside* the generated model. New operations ship without regenerating or editing a single data class (Open/Closed).

**Realizes.** Operates over `subclass_of` / `part_of` structures; the behaviour itself is *not* a stereotype — that is the point.

```csharp
using Wmoop.Core;
namespace Wmoop.Transport;

public interface IVehicleVisitor<out T>     // one method per concrete generated kind
{
    T Visit(Moped m);
    T Visit(Motorcycle m);
}

public partial abstract class Vehicle       // GENERATED partial: the Accept hook only
{
    public abstract T Accept<T>(IVehicleVisitor<T> v);
}
public partial class  Motorcycle { public override T Accept<T>(IVehicleVisitor<T> v) => v.Visit(this); }
public partial sealed class Moped { public override T Accept<T>(IVehicleVisitor<T> v) => v.Visit(this); }

// HAND-WRITTEN behaviour, entirely outside the data model:
public sealed class RoadTaxVisitor : IVehicleVisitor<Quantity>
{
    public Quantity Visit(Moped m)      => new(0, "EUR");                 // mopeds exempt
    public Quantity Visit(Motorcycle m) => new(m.MaxSpeed.Value * 0.5, "EUR");
}
//   Quantity tax = someVehicle.Accept(new RoadTaxVisitor());  // dispatched by real type
```

**When NOT to use.** When the **structure changes often** but operations rarely do — then every new class forces editing every visitor, and a polymorphic virtual method on the class (or Strategy) is better. Also skip it for a single trivial operation; a visitor for one `Describe()` is ceremony. (WMOOP's structure is schema-stable and operations proliferate — exactly Visitor's sweet spot.)

### 2.4 Strategy

**Intent.** Encapsulate a family of interchangeable algorithms behind one interface and select among them at runtime.

**WMOOP use case.** Rendering a `Quantity` for different locales/unit systems; choosing a distance metric between `Place`s (great-circle vs road); a classification-confidence scorer. The *policy* varies while the data stays fixed — a second home for behaviour alongside Visitor.

**Realizes.** Behaviour over `has_quality` values (and others); not a structural stereotype.

```csharp
using Wmoop.Core;
namespace Wmoop.Core.Presentation;

public interface IQuantityFormatter { string Format(Quantity q); }

public sealed class SiFormatter : IQuantityFormatter
{
    public string Format(Quantity q) => $"{q.Value:0.###} {q.Unit}";
}

public sealed class ImperialSpeedFormatter : IQuantityFormatter
{
    public string Format(Quantity q) =>
        q.Unit == "km/h" ? $"{q.Value * 0.621:0.#} mph" : $"{q.Value:0.###} {q.Unit}";
}

public sealed class QuantityLabel                 // depends on the ABSTRACTION (DIP)
{
    private readonly IQuantityFormatter _fmt;
    public QuantityLabel(IQuantityFormatter fmt) => _fmt = fmt;   // inject the policy
    public string Of(Quantity q) => _fmt.Format(q);
}
//   new QuantityLabel(new ImperialSpeedFormatter()).Of(new Quantity(200, "km/h")); // "124.2 mph"
```

**When NOT to use.** When there is exactly one algorithm that will never vary (YAGNI — do not inject a strategy "just in case"), or when the variants differ by *object type* over a stable structure (that is Visitor/polymorphism, not runtime strategy selection).

### 2.5 Specification

**Intent.** Represent a boolean rule as a first-class, composable object so the same rule drives **validation**, **in-memory filtering**, and **query** — combined with `And` / `Or` / `Not`.

**WMOOP use case.** "A `Person` who currently holds a valid category-B licence" is one specification used to validate a data edit *and* to filter an L2 registry *and* (via Adapter) to build an external query. Rules are authored once as objects, not re-expressed per call site.

**Realizes.** `classified_as` (perspectival membership) and `association` filters; a hand-written behaviour family.

```csharp
namespace Wmoop.Core.Rules;

public interface ISpecification<in T>
{
    bool IsSatisfiedBy(T candidate);
}

public static class Spec
{
    public static ISpecification<T> And<T>(this ISpecification<T> a, ISpecification<T> b) => new AndSpec<T>(a, b);
    public static ISpecification<T> Or<T> (this ISpecification<T> a, ISpecification<T> b) => new OrSpec<T>(a, b);
    public static ISpecification<T> Not<T>(this ISpecification<T> a)                      => new NotSpec<T>(a);

    private sealed class AndSpec<T>(ISpecification<T> a, ISpecification<T> b) : ISpecification<T>
    { public bool IsSatisfiedBy(T x) => a.IsSatisfiedBy(x) && b.IsSatisfiedBy(x); }
    private sealed class OrSpec<T>(ISpecification<T> a, ISpecification<T> b) : ISpecification<T>
    { public bool IsSatisfiedBy(T x) => a.IsSatisfiedBy(x) || b.IsSatisfiedBy(x); }
    private sealed class NotSpec<T>(ISpecification<T> a) : ISpecification<T>
    { public bool IsSatisfiedBy(T x) => !a.IsSatisfiedBy(x); }
}
//   var eligible = new HoldsCategory("B").And(new IsAdult());        // compose
//   registry.Where(eligible.IsSatisfiedBy);                          // filter
//   if (!eligible.IsSatisfiedBy(candidate)) throw new ...;           // validate
```

**When NOT to use.** For a single inline predicate used in one place — a lambda is clearer. Reach for Specification when the rule is **named, reused, or composed**, or must be translated to another backend.

### 2.6 Builder + Fluent Interface

**Intent.** Assemble a complex, validated object step by step through a readable, chainable API, keeping the final object immutable.

**WMOOP use case.** Constructing a geography `Country` with nested `County`/`City` parts, or a `DriverRole` with several categories and dates, without a telescoping constructor — and running fail-fast validation once at `Build()`.

**Realizes.** `part_of` assembly and `has_role` construction; GRASP Creator.

```csharp
using Wmoop.Core;
namespace Wmoop.Geography;

public sealed class CountryBuilder
{
    private readonly ConceptId _id;
    private readonly string _name;
    private readonly List<Place> _counties = new();
    public CountryBuilder(ConceptId id, string name) { _id = id; _name = name; }

    public CountryBuilder WithCounty(string id, string name, params (string Id, string Name)[] cities)
    {
        var county = new County(id, name);
        foreach (var c in cities) county.Add(new City(c.Id, c.Name));
        _counties.Add(county);
        return this;                                   // fluent: returns self
    }

    public Country Build()
    {
        if (_counties.Count == 0) throw new InvalidOperationException("country has no counties");
        var country = new Country(_id, _name);
        foreach (var c in _counties) country.Add(c);
        return country;                                // immutable result
    }
}
//   new CountryBuilder("wmoop.geography/RO","Romania")
//       .WithCounty("wmoop.geography/RO-CJ","Cluj", ("wmoop.geography/RO-CJ-cluj","Cluj-Napoca")).Build();
```

**When NOT to use.** When a constructor with a few required parameters is already clear (`new Quantity(49, "cc")` needs no builder). A builder for a two-field value object is pure overhead.

### 2.7 Abstract Factory / Factory Method — *the codegen projection*

**Intent.** Create families of related objects through an abstraction, so the concrete, platform-idiomatic types are chosen behind a stable interface.

**WMOOP use case.** This *is* the codegen projection modelled in the type system: one WML concept is realized by a per-language factory that produces the idiomatic instance (a C# `record`, a Java POJO, a Python `@dataclass`). Within C#, a factory also constructs the right `Vehicle` leaf from a WML `kind` discriminator without the caller knowing the concrete class.

**Realizes.** `instance_of` (the projection of an L1 class to an L2 individual).

```csharp
using Wmoop.Core;
namespace Wmoop.Transport;

public interface IVehicleFactory                       // abstract factory surface
{
    Vehicle Create(ConceptId id, string name, Quantity maxSpeed);
}

public sealed class MopedFactory : IVehicleFactory     // one concrete family member
{
    public Vehicle Create(ConceptId id, string name, Quantity maxSpeed) =>
        new Moped(id, name, maxSpeed, engineDisplacement: new Quantity(49, "cc"));
}

public static class VehicleFactories                   // factory method keyed by WML kind
{
    public static IVehicleFactory For(string wmlKind) => wmlKind switch
    {
        "Moped"      => new MopedFactory(),
        _            => throw new NotSupportedException($"No factory for kind '{wmlKind}'.")
    };
}
//   var v = VehicleFactories.For("Moped").Create("wmoop.transport/x","X", new(45,"km/h"));
```

**When NOT to use.** When there is a single concrete type and no family to vary — a plain constructor or the Builder is simpler. Do not introduce a factory to hide a `new` that has no polymorphic choice behind it.

### 2.8 Registry + Flyweight — *interned `ConceptId`, shared definitions*

**Intent.** **Registry:** a well-known place to find instances by key. **Flyweight:** share one immutable instance for every logically-equal value instead of duplicating it, to cut memory and make identity comparisons cheap.

**WMOOP use case.** Concept *definitions* (name, definition, provenance for `wmoop.transport/Moped`) are identical across millions of L2 individuals — intern them once. An L2 `ConceptRegistry` holds canonical individuals so references resolve to the same object.

**Realizes.** `instance_of` resolution; backs `has_quality` definitions shared across instances.

```csharp
using Wmoop.Core;
namespace Wmoop.Core.Registry;

public sealed record ConceptDefinition(ConceptId Id, string Name, string Definition, string Provenance);

public sealed class ConceptRegistry                     // Registry + Flyweight factory
{
    private readonly Dictionary<ConceptId, ConceptDefinition> _interned = new();

    // Returns the SAME shared instance for a given id (flyweight interning).
    public ConceptDefinition Intern(ConceptDefinition def)
    {
        if (_interned.TryGetValue(def.Id, out var existing)) return existing;
        _interned[def.Id] = def;
        return def;
    }

    public ConceptDefinition? Resolve(ConceptId id) =>
        _interned.TryGetValue(id, out var d) ? d : null;   // Null Object is a cleaner alt — §2.12
    public IReadOnlyCollection<ConceptDefinition> All => _interned.Values;
}
//   Two individuals of wmoop.transport/Moped share one ConceptDefinition — not a copy each.
```

**When NOT to use.** When instances are **mutable** or few — interning mutable objects aliases state and causes spooky action at a distance; a registry of a handful of objects is premature. Flyweight only pays off for high-cardinality immutable values.

### 2.9 Adapter

**Intent.** Make an incompatible interface usable through the interface clients expect, without changing either side.

**WMOOP use case.** Two directions: (a) project the canonical model onto each language's idioms (a WMOOP `Quantity` ↔ a host library's unit type); (b) integrate **external datasets** — wrap a Wikidata entity so it presents as a WMOOP `Entity` with a `ConceptId` and provenance, isolating all of WMOOP from the external schema's quirks.

**Realizes.** `association` / `instance_of` across a boundary (Indirection, DIP).

```csharp
using Wmoop.Core;
namespace Wmoop.Integration.Wikidata;

// The shape of the foreign data (what we DON'T control).
public sealed record WikidataEntity(string QId, string Label, string? FetchedFrom);

// Adapter: presents a foreign record AS a WMOOP Entity, minting a ConceptId + provenance.
public sealed class WikidataPersonAdapter : Entity
{
    private readonly WikidataEntity _source;
    public WikidataPersonAdapter(WikidataEntity source)
        : base(new ConceptId($"wmoop.nature/wd-{source.QId}"), source.Label)
        => _source = source;

    public string Provenance => _source.FetchedFrom ?? $"wikidata:{_source.QId}";
}
//   Entity e = new WikidataPersonAdapter(new WikidataEntity("Q7259","Ada Lovelace","wikidata"));
//   // Rest of WMOOP treats `e` as any other Entity; nothing else imports the Wikidata schema.
```

**When NOT to use.** When you *own* both sides — fix the real interface instead of wrapping it. An adapter that merely renames methods you control is debt. Never let adapted external text flow in as trusted input: it is data, validated at the seam.

### 2.10 Decorator

**Intent.** Add responsibilities to an object dynamically by wrapping it in another object with the same interface, instead of subclassing for every combination.

**WMOOP use case.** Layer **optional capabilities** onto a behaviour: wrap an `IQuantityFormatter` (§2.4) to add caching, a unit-conversion pass, or a localisation suffix — composing features à la carte without a class explosion (`CachingLocalisedImperialFormatter`…).

**Realizes.** Behavioural layering; no structural stereotype (it decorates a Strategy).

```csharp
using Wmoop.Core;
namespace Wmoop.Core.Presentation;

public sealed class CachingFormatter : IQuantityFormatter      // same interface it wraps
{
    private readonly IQuantityFormatter _inner;
    private readonly Dictionary<Quantity, string> _cache = new();
    public CachingFormatter(IQuantityFormatter inner) => _inner = inner;

    public string Format(Quantity q)
    {
        if (_cache.TryGetValue(q, out var hit)) return hit;     // Quantity has value equality
        return _cache[q] = _inner.Format(q);
    }
}
//   IQuantityFormatter f = new CachingFormatter(new ImperialSpeedFormatter());
//   f.Format(new Quantity(200, "km/h"));   // second identical call is served from cache
```

**When NOT to use.** When the layered behaviours are mutually dependent or order-sensitive in ways wrapping hides, or when there is exactly one optional feature — a flag is simpler than a wrapper type. Deep decorator stacks become as hard to reason about as deep inheritance.

### 2.11 Template Method — *use sparingly*

**Intent.** Define an algorithm's skeleton in a base method, deferring specific steps to overridable hooks in subclasses.

**WMOOP use case.** `Vehicle.Describe()` is a small, legitimate template: the base composes the sentence from polymorphic parts (`Classification`, `WheelCount`, `MaxSpeed`) and `Moped` extends it. **Caution:** this couples the varying step to the inheritance tree. WMOOP's prime directive prefers **Strategy** (§2.4) for varying behaviour precisely because Strategy composes without inheritance. Use Template Method only when the skeleton is intrinsic to a genuine `subclass_of` hierarchy that already exists for *data* reasons.

**Realizes.** `subclass_of` (and inherits its risks).

```csharp
using Wmoop.Core;
namespace Wmoop.Transport;

public abstract partial class Vehicle : Entity
{
    public abstract string Classification { get; }                 // the deferred step (hook)

    public virtual string Describe() =>                            // the skeleton
        $"{Name} — a {Classification} with {WheelCount} wheels, top speed {MaxSpeed}.";
}

public sealed partial class Moped
{
    public override string Classification => "moped";
    public override string Describe() => base.Describe() + $" Engine: {EngineDisplacement}.";
}
```

**When NOT to use.** When the varying step is a *policy* rather than part of a rigid is-a kind — use Strategy. Any time you reach for Template Method and the base exists *only* to host the hook, you are using inheritance for code reuse (anti-pattern §4) — stop.

### 2.12 Null Object

**Intent.** Provide a benign, do-nothing implementation of an interface so callers never branch on `null`.

**WMOOP use case.** An unresolved `ConceptDefinition` lookup (§2.8) can return an `UnknownConcept` that answers safely (empty definition, `"unresolved"` provenance) instead of `null`, so rendering and export code has no null checks scattered through it (supports Law of Demeter and fail-safe reads). *Distinct* from a role's `Subject == null`, which is a meaningful "not yet granted" state, not a null-object case.

**Realizes.** `instance_of` fallback.

```csharp
using Wmoop.Core;
namespace Wmoop.Core.Registry;

public sealed class NullConceptDefinition
{
    public static readonly ConceptDefinition Instance =
        new(new ConceptId("wmoop.core/UnknownConcept"), "Unknown", "", "unresolved");
    private NullConceptDefinition() { }
}

public sealed class SafeRegistry
{
    private readonly ConceptRegistry _inner;
    public SafeRegistry(ConceptRegistry inner) => _inner = inner;

    // Never returns null; callers need no null-guard.
    public ConceptDefinition Resolve(ConceptId id) =>
        _inner.Resolve(id) ?? NullConceptDefinition.Instance;
}
```

**When NOT to use.** When "absent" is genuinely different from "empty" and the caller *must* react to it (a missing licence must block driving, not silently pass) — there, surface the absence. A null object that swallows a real error is worse than a `null`.

### 2.13 Observer / event — *optional model-change notifications*

**Intent.** Let interested parties subscribe to an object's changes without the subject knowing who they are.

**WMOOP use case.** An **optional** L2 facility: when a role is granted or a registry gains an individual, notify indexers, caches (§2.10), or audit logs. Kept optional and off the generated data path so the core model has no event coupling.

**Realizes.** `association` (publisher ↔ subscribers), decoupled by Indirection.

```csharp
using Wmoop.Core;
namespace Wmoop.Core.Events;

public sealed record RoleGranted(Entity Subject, ConceptId RoleType);

public sealed class RoleEventHub                         // uses BCL events only
{
    public event Action<RoleGranted>? Granted;
    public void Publish(Entity subject, IRole role) =>
        Granted?.Invoke(new RoleGranted(subject, role.RoleType));
}
//   hub.Granted += e => Console.WriteLine($"{e.Subject.Name} gained {e.RoleType}");
//   hub.Publish(ada, driverRole);
```

**When NOT to use.** When the flow is synchronous and known at the call site — a direct call is clearer and traceable. Observers can create surprising reentrancy and lifetime leaks; keep them out of the generated model and out of hot paths.

### 2.14 Interpreter — *the query / Specification DSL*

**Intent.** Represent sentences of a small language as an object tree and evaluate them by walking it.

**WMOOP use case.** The composable **Specification** rules (§2.5) *are* an interpreter: `And`/`Or`/`Not` nodes plus leaf predicates form an expression tree for a WMOOP query DSL, evaluated in-memory or translated by an Adapter to an external query. It is the executable grammar behind "find individuals matching this rule."

**Realizes.** `classified_as` / `association` querying.

```csharp
namespace Wmoop.Core.Rules;

// Grammar nodes = the Specification tree; evaluation = Interpret over a candidate.
public interface IQueryExpr<in T> { bool Interpret(T candidate); }

public sealed class HoldsCategory : IQueryExpr<Wmoop.Nature.Person>
{
    private readonly string _category;
    private readonly DateOnly _on;
    public HoldsCategory(string category, DateOnly on) { _category = category; _on = on; }

    public bool Interpret(Wmoop.Nature.Person p) =>
        p.GetRole<Wmoop.Transport.DriverRole>()?.CanDrive(_category, _on) == true;
}
//   Compose with the And/Or/Not nodes from §2.5 to build a full query expression tree.
```

**When NOT to use.** When the "language" has one or two fixed forms — hand-write the check. A full interpreter is justified only when rules are numerous, user-authored, or need translation to another engine; otherwise it is premature abstraction (§4).

### 2.15 Prototype / clone — *a caution around value identity*

**Intent.** Create a new object by copying an existing one.

**WMOOP use case / caution.** Mostly a **warning**. A `ConceptId` is *identity*: cloning an `Entity` and keeping its `Id` creates two objects claiming to be the same concept — a corruption of L2. If you clone for a template, you **must** mint a fresh `ConceptId`. Value objects (`Quantity`) are safe to copy precisely because they carry *no identity* — a copy of `Quantity(45,"km/h")` is equal to and interchangeable with the original.

**Realizes.** `instance_of` (and the identity hazard around it).

```csharp
using Wmoop.Core;
namespace Wmoop.Transport;

public static class VehiclePrototype
{
    // A clone MUST receive a new identity; copying the ConceptId would alias identity.
    public static Moped CloneAsNew(Moped template, ConceptId freshId, string name) =>
        new(freshId, name, template.MaxSpeed, template.EngineDisplacement);
}
//   var clone = VehiclePrototype.CloneAsNew(piaggio, "wmoop.transport/piaggio-2", "Piaggio #2");
//   // clone.Id != piaggio.Id — distinct individuals; but a Quantity copied inside is just equal.
```

**When NOT to use.** To duplicate an identity-bearing `Entity` while preserving its `ConceptId` — never. And do not add a `Clone()` to value objects: they are immutable, so a "copy" is just the same value.

---

## 3. Patterns and the generation gap

This section is the operational answer to **"where does behaviour live?"** and to **"how does regeneration stay safe?"**

### 3.1 The two columns

| | **GENERATED from WML** | **HAND-WRITTEN, idiomatic** |
|---|---|---|
| **What** | Data: classes, properties, `has_quality` fields, `part_of` containment, `subclass_of` lineage, `has_role` attach points, `Accept` hooks, `ConceptId`/provenance, the factory surface | Behaviour: Visitors, Strategies, Specifications/Interpreters, Builders, Decorators, Observers, Adapters to the outside world |
| **Patterns** | Composite skeleton, Role attach points, Factory Method projection, Flyweight definitions, the `Accept` half of Visitor | Visitor bodies, Strategy, Specification, Builder, Decorator, Null Object, Observer, Adapter, Template-Method hooks (sparingly) |
| **Changes when** | The *world model* changes (a concept is added/refined in WML) | A *computation* changes (new algorithm, new rule, new rendering) |
| **Owns** | State and structure | Algorithms and policy |

The dividing line is exact: **generated code never contains an algorithm beyond trivial, generated accessors and a one-line `Accept`.** Everything a reviewer would call "logic" is hand-written in a visitor, strategy, or specification. That is *why* the data can be regenerated at will — regeneration cannot clobber behaviour, because behaviour is not in the generated files.

### 3.2 Where behaviour lives — restated for the record

1. **Operations over the structure → Visitor (double dispatch).** Add operations without touching data classes (Open/Closed). The schema-stable concept tree is Visitor's ideal substrate.
2. **Swappable policies → Strategy.** Formatting, scoring, distance metrics — injected, not baked in.
3. **Rules → Specification / Interpreter.** One rule object validates, filters, and queries.
4. **Construction → Builder / Factory.** Idiomatic, validated assembly per language.
5. **Edge behaviour → Decorator, Observer, Adapter.** Optional layers and integrations, off the core path.

No behaviour hides inside a generated setter. If you feel the urge to put logic in a generated class, it belongs in one of the five homes above.

### 3.3 How regeneration stays safe

Three mechanisms, applied per language:

- **Do-not-edit regions.** Every generated file opens with a machine-readable banner (`// <auto-generated>`); editing inside it is a review failure. Regeneration overwrites only these files.
- **Partial classes / extension points (C#, and the per-language equivalent).** Generated types are declared `partial`. Hand-written behaviour — including the `Accept` *bodies* if a project chooses to hand-place them, convenience methods, and `[CallerMemberName]`-style helpers — lives in a *separate, non-generated* `*.Manual.cs` partial that regeneration never touches. Java uses a generated base + hand-written subclass or an interface the generator implements; Python uses a generated module imported by a hand-written one (or mixins); C++ uses a generated header included by a hand-written translation unit.
- **Behaviour is external by construction.** Because Visitors/Strategies/Specifications are their own types in their own files, a full regeneration of the data model leaves them compiling unchanged — the only coupling is to the generated *interfaces*, which are themselves part of the stable WML projection.

The practical contract: **you can delete and regenerate the entire `generated/` tree at any commit and lose nothing but the data classes, which come back identical.** If that is ever untrue, behaviour has leaked into generated code and the fix is to move it out, not to hand-edit the generated file.

---

## 4. Anti-patterns

Each is a direct violation of the prime directive or an invariant. Reviewers reject these on sight.

| Anti-pattern | Why it is wrong in WMOOP | Do this instead |
|---|---|---|
| **Deep inheritance** (depth ≫ 4) | Brittle, forces one lineage, breaks Liskov as it grows | Keep ≈ 4 (CI gate: depth ≤ 6, warn at 5); push variation into Roles/Strategy/classification |
| **God base class** | A fat `Entity` accreting every optional field/method; low cohesion, high coupling | Small `Entity` (Id, Name); capabilities as interfaces (`IHasRoles`), facets as roles |
| **`Driver : Person`** | Models an anti-rigid, non-exclusive facet as a permanent kind; a person can't then be driver *and* owner | `has_role`: `person.AddRole(new DriverRole(...))` (§2.1) |
| **Setter-driven mutable identity** | Mutating a `ConceptId` (or re-pointing a role's `Subject`) destroys L2 referential integrity | Immutable `ConceptId`; `AttachTo` internal + single-shot; new object for change |
| **Primitive obsession** (bare numbers) | `double MaxSpeed` loses the unit; 200 km/h vs 200 mph silently conflate | `Quantity` everywhere a thing is measured; plain `int` only for dimensionless counts |
| **Feature envy** | `Person.CanDrive(...)` reaches into licence fields it doesn't own | Put the method on the information expert: `DriverRole.CanDrive(...)` |
| **Stringly-typed relations** | `"part_of"` / `"Driver"` as raw strings; typos compile, meaning is lost | Typed `ConceptId` constants (`DriverRole.TypeId`), typed role/visitor APIs |
| **Premature abstraction** | An Interpreter/Strategy/factory for one fixed case (violates YAGNI) | Start concrete; extract a pattern when a *second* real variant appears |
| **Inheritance for code reuse** | Subclassing just to inherit helper methods, not because of is-a | Compose a helper (`RoleContainer`), use a Strategy or an extension method |

**Worked contrast — the crux, right and wrong:**

```csharp
// WRONG — anti-rigid facet as a rigid kind; cannot be driver AND owner at once.
public class Driver : Person { public string Licence { get; set; } }   // setter-driven identity too

// RIGHT — facet as a Role, attached by composition; many facets coexist.
ada.AddRole(new DriverRole("RO-AB-123456", new[] { "B" }, issue, expiry));
ada.AddRole(new OwnerRole(moped, ownedSince));
bool ok = ada.GetRole<DriverRole>()?.CanDrive("B", today) == true;      // ask the expert
```

---

## 5. Quick-reference table

| Pattern | WMOOP use | Meta-model stereotype | Generated or hand-written |
|---|---|---|---|
| **Role Object** | `Person` acquires `Driver`/`Owner` facets | `has_role` | Attach points generated; role state generated; role **behaviour** hand-written |
| **Composite** | `Country → County → City`; biological part-of; musical score | `part_of` | Structure generated; traversal **behaviour** hand-written |
| **Visitor + double dispatch** | **Where behaviour lives** — ops over the concept tree (tax, export, census) | operates over `subclass_of`/`part_of` | `Accept` hook generated; **visitor bodies hand-written** |
| **Strategy** | Quantity formatting, distance metric, scoring | behaviour over `has_quality` | Hand-written |
| **Specification** | Eligibility rules: validate + filter + query (`And`/`Or`/`Not`) | `classified_as`, `association` | Hand-written |
| **Builder + Fluent** | Assemble `Country` with nested parts; multi-field `DriverRole` | `part_of`, `has_role` | Hand-written |
| **Abstract Factory / Factory Method** | Per-language idiomatic projection; `Vehicle` leaf from WML kind | `instance_of` | Factory surface generated; selection logic hand-written |
| **Registry + Flyweight** | Interned `ConceptId`/`ConceptDefinition`; L2 individual registry | `instance_of`, shared `has_quality` | Hand-written (infra); definitions sourced from generated model |
| **Adapter** | Project model to host idioms; wrap Wikidata as `Entity` | `association`, `instance_of` across a boundary | Hand-written |
| **Decorator** | Layer caching/localisation onto a formatter | behavioural layering | Hand-written |
| **Template Method** *(sparingly)* | `Vehicle.Describe()` skeleton + `Classification` hook | `subclass_of` | Skeleton may be generated; hooks hand-written — prefer Strategy |
| **Null Object** | `UnknownConcept` for unresolved lookups | `instance_of` fallback | Hand-written |
| **Observer / event** *(optional)* | Notify indexers/caches on role grant / registry add | `association` | Hand-written, off the core path |
| **Interpreter** | The query/Specification DSL (expression tree) | `classified_as`, `association` | Hand-written |
| **Prototype / clone** *(caution)* | Template-copy an `Entity` **with a fresh `ConceptId`** | `instance_of` (identity hazard) | Hand-written; never clone identity |

---

### Closing note

Two sentences hold the whole guide together. **Composition, interfaces, and Roles over deep inheritance** — the model stays shallow, flexible, and true to a world where things wear many hats. And **behaviour lives outside the generated data model, in Visitors, Strategies, and Specifications** — so the one canonical WML model can be regenerated into every language, forever, without ever overwriting a line of logic.
