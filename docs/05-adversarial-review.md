# WMOOP Adversarial Design Review


## architecture-skeptic

**Summary:** Adversarial review of WMOOP. The design is unusually literate about prior art, but it has load-bearing contradictions that current docs paper over, and the one piece of real code already violates three of its own invariants. The deepest problem is paradigm choice: everything WMOOP actually needs (multi-parent/contested classification, roles, n-ary + scheme-qualified relations, provenance, reclassification over time, merges) is graph-native and single-inheritance-OOP-hostile, and the docs already smuggle a knowledge graph in under WML while calling OOP the "source of truth." Concretely: (1) BEHAVIOUR — OOP's whole reason to exist — cannot be generated and is hand-ported per language (confirmed in wmoop.net: CanDrive/Describe/Classification are hand-written, and Moped enforces none of its schema constraints), so "write once, replicate everywhere" holds only for the data skeleton, not for methods. (2) The "one rigid identity-giving parent" rule structurally privileges a single tree and directly contradicts the ETHICS "no one true tree / competing schemes" rule (codegen emits Tomato : Berry, baking botany-as-truth). (3) The depth budget (warn >5 / error >7) is broken by real Linnaean taxonomy on the flagship biology domain, and the reference impl already dodges this by demoting ranks to tags — i.e. the headline is-a example is not actually modeled as is-a. (4) Generated closed-world OOP lies under the stated open-world-for-facts invariant: HasRole<Driver>()==false is emitted for "no licence recorded," which is the exact OWA/CWA anti-pattern (A10) the prior-art section warns against — committed by the reference code. Math/abstract objects, dimensional analysis, reclassification (Pluto), recurring/plural roles, and whole-world build/governance throughput are also under-specified or wrong. Recommendation: invert the architecture — author a scheme-aware knowledge graph as the source of truth and make the OOP class hierarchy ONE generated projection (per chosen scheme), exactly as OWL/Protobuf are already treated; keep codegen/idiom-profiles/value-quantities, concede single-inheritance-OOP-as-source.


### Findings


**1. [critical] 4 codegen / Invariant 1 — behaviour**

- Problem: OOP is defined by behaviour (methods), but the WML schema is almost entirely data (properties, relations, constraints). The generation-gap pattern explicitly puts all method bodies in the hand-written half, per language. So every behaviour is re-authored in C#, Java, Python and C++ by hand — the exact duplication the project exists to kill. Confirmed in the reference impl: Wmoop.Transport/DriverRole.cs CanDrive(), Moped.cs Describe()/Classification, and Shape.area() in the academic guide are all hand-written; none is derivable from the schema. Even a universal, language-neutral formula like circle area must be written four times and can silently DRIFT, because the conformance suite only pins structure, constraints and serialization (schema-codegen open question 7.6 admits behaviour is not conformance-tested). 'Write once, replicate everywhere' is therefore true only for the part of OOP that isn't OOP.
- Recommendation: Stop claiming behaviour is covered by Invariant 1. Add a sandboxed, language-neutral expression/behaviour language (CEL-like, resolve schema-codegen OQ7.3 now, not later) for pure, total functions (derived properties, invariants, unit conversions, area/perimeter, canDrive) so they ARE generated and conformance-tested with input/output vectors. Declare everything else (I/O, side-effecting, heuristic behaviour) explicitly OUT of the single-source guarantee and expect it to be written per language. Re-word the whitepaper/abstract: WMOOP generates data structure + declarative constraints + pure derivations; imperative behaviour is per-binding and is a known drift surface with its own behaviour-conformance vectors where it matters.


**2. [critical] 6 paradigm + 1/2 inheritance — OOP vs graph**

- Problem: The meta-model requires every concrete individual to instantiate exactly ONE identity-giving Kind, and Subkind is single-parent. This structurally privileges one classification tree as 'the identity tree' and demotes every rival scheme to tags/categories. That directly contradicts GOVERNANCE/ETHICS §2.5 ('classification schemes are first-class; never one true tree; reviewers reject deleting a rival scheme'). The tomato ruling proves it: §4.4 forces specializes: Berry (botany) as the inheritance edge and makes culinary a second-class tag, and codegen emits Tomato : Berry — baking botany-as-objective-truth into every generated language, exactly the editorializing ETHICS forbids. More broadly, everything WMOOP genuinely needs — multi-parent, contested/dated classification, n-ary and scheme-qualified relations, provenance per edge, sameAs/merge, roles — is graph-native and single-inheritance-hostile. The canonical WML is already a knowledge graph serialized as YAML; OWL/Protobuf/JSON-Schema are already called 'projections.' OOP is simply a poor SOURCE representation.
- Recommendation: Invert the architecture: make a scheme-aware statement/graph model the single source of truth (concepts, typed relations, classifiedUnder:<scheme> edges with provenance/rank, reified n-ary relations). Treat 'the OOP class hierarchy' as ONE GENERATED PROJECTION computed for a chosen primary scheme — same status as the OWL and Protobuf projections already described — not as the authored artifact. This dissolves tomato/Pluto/taxonomy-depth/multi-parent at a stroke and makes the system consistent with 'ontology-first source, developer-first output.' Retain from the current design: idiom-profile codegen, Role/trait mapping, value-object quantities, the DoD/CI. Concede in the docs: single-inheritance OOP is an output view, not the source; retire 'is-a tree = identity' as a structural axiom; change the tagline to 'describe the world as a knowledge graph; project it into OOP.'


**3. [critical] 1 inheritance — depth budget vs real taxonomy**

- Problem: The depth budget is warn >5 / error >7 and the academic guide tells students to keep is-a '≤3–4 levels.' Real Linnaean taxonomy — the project's flagship biology example — is Domain>Kingdom>Phylum>Class>Order>Family>Genus>Species = 8+ rigid, Liskov-clean, identity-sharing sortals (a Dog IS always, necessarily, an Animal). This BREAKS the depth cap on the first serious domain. The reference impl already dodges it: csharp-ref MAPPING NOTES state 'Intermediate biological ranks (Chordate/Mammal/Primate) are classification facts/tags, not extra base classes.' So the headline Animal→Mammal→… 'inheritance' example is NOT modeled as inheritance at all — it is tags — which is an admission the inheritance invariant cannot carry the domain it was sold on.
- Recommendation: Either (a) exempt genuine rigid-sortal scientific rank hierarchies from the depth cap (depth is a code-smell heuristic for ad-hoc modeling, not a law of nature), applying the cap only to non-rank hierarchies; or, preferably under the graph-source inversion, (b) store taxonomy as subclass_of edges in the graph and GENERATE a flattened/opinionated class projection whose runtime inheritance depth is a projection choice, not a modeling constraint. Fix the docs' internal contradiction: the meta-model, the academic '≤3–4 levels' guidance, and the csharp-ref 'ranks are tags' workaround currently describe three different, incompatible treatments of the same example.


**4. [high] 5/6 OWA vs CWA leak — confirmed in reference code**

- Problem: Invariant 8 declares 'open-world for facts' (absence of a fact ≠ its falsehood) but generated OOP is closed-world and emits absence-as-false. Confirmed: RoleContainer.HasRole<Driver>() returns false, and GetRole<T>() returns null, for a Person with no recorded licence — so downstream code reads 'this person cannot/does not drive,' which under the stated OWA is a lie (we may simply not have recorded the licence). This is anti-pattern A10 from the project's own prior-art section, committed by the reference implementation. The DoD also mixes stances (required-properties-populated and no-dangling-refs are closed-world; 'we don't claim all facts' is open-world) with no operational boundary.
- Recommendation: Define a precise CWA↔OWA bridge policy and generate it into code. Distinguish three truth states in generated APIs for facts/roles: Present, Absent-and-known-complete (closed), Unknown (open) — e.g. HasRole<T>() returns a tri-state or throws on 'unknown' unless a completeness assertion exists. Mark each property/relation/role slot with a completeness flag (closed set vs open set); only closed slots may be queried as boolean-false-on-absence. Add a CI check that forbids generating boolean 'does-not-have' accessors over open-world slots. Fix the reference impl to not imply 'cannot drive' from an empty role container.


**5. [high] 3 expressiveness — pure math / abstract objects**

- Problem: The closed property-slot set (Datatype/Enum/Reference/Quantity/Composition) cannot express the actual content of mathematics. A Group is a structure (G, •) with a binary operation satisfying axioms; there is no operation/function type in the slot set, and 'associativity' is only a doc-string invariant because the expression language is deferred to an open question. A Theorem's statement is stored as an opaque String and its proof relations (provenFrom/impliedBy) reference other opaque strings. So the generated Math library is a bibliography, not a model: nothing about a theorem or group is machine-checkable, which silently falsifies the 'everything machine-checkable' DoD for the entire Math domain (one of the four seed domains). The meta-model quietly assumes attribute-bearing objects after claiming it does not.
- Recommendation: Add first-class Operation/Function signatures (domain×…→codomain) and a real, sandboxed logical expression language to L0 BEFORE claiming Math is in scope; without it, descope Math to 'nomenclature only' honestly. Represent abstract structures as parameterized types (carrier + operations + axiom set as checkable formulae), not as property bags. Make the axiom/invariant language part of conformance so 'associativity holds' is a passing test, not a comment. If this is too heavy, state plainly that WMOOP models the TAXONOMY of mathematical objects, not their semantics, and remove the 'helps AI learn how everything is conceived' claim for math.


**6. [high] 1 roles — cardinality, plurality, recurrence, role-role structure**

- Problem: The flagship role is mis-modeled and the mechanism is under-powered. (a) schema-codegen sets Driver cardinality_per_player: 0..1 and a WM-ROLE-DUPLICATE gate — but a person can hold two driving licences (RO + US) and two jobs (two Employee roles) simultaneously; the reference GetRole<T>() returns only the FIRST match, silently hiding the second. (b) Roles carry a single validFrom/validTo interval (DriverRole has one IssueDate/ExpiryDate), so a recurring role — employed 2010–2015 and again 2020–now at the same employer — cannot be expressed as one role with disjoint intervals, and splitting into two roles loses the 'same employment' identity. (c) Relations whose participants are themselves roles, and n-ary role-qualified relations ('Driver drivesFor Employer under Contract X'), have no home: role.relations target entities, and n-ary relation reification is an unresolved open question. (d) 'played_by must already hold role Y' (Team-Captain is-a Player is-a Person) cannot be expressed.
- Recommendation: Change the per-player role cardinality default to 0..* (single-hold is the exception, declared explicitly and justified), and fix GetRole to GetRoles/GetRole(selector). Give roles a validity HISTORY (set of intervals / temporal object), not one interval, and resolve the reified-relation open question in favour of always reifying n-ary and role-participant relations as first-class objects. Allow played_by to reference a role or capability predicate, not only a Kind. Fix the Driver example and conformance vectors to permit multiple simultaneous licences/employments.


**7. [high] 2 shifting classification — Pluto / reclassification over time**

- Problem: Reclassification (Pluto: Planet in 2005, DwarfPlanet in 2006) is NOT 'two schemes disagree' — it is the authoritative scheme changing its verdict over time. But instanceOf is a hard STRUCTURAL edge in the meta-model (and a Kind supplies the principle of identity), while GOVERNANCE/ETHICS model classification as a dated, sourced claim (asOf). These two mechanisms are never reconciled: is 'Pluto instanceOf Planet' structure or a dated claim? If instanceOf changes and Kind gives identity, the immutable-wmid identity story is threatened; if it can't change, the model can't represent the single most famous reclassification in its Space seed domain. The same leak hits part_of (continents partOf Earth is scheme-relative — 4 to 7 continents — but RelationType is a plain unqualified binary edge).
- Recommendation: Make instantiation and classification DATED, SCHEME-QUALIFIED, SOURCED CLAIMS, not structural edges (the graph-source inversion gives this for free). Decouple identity from current classification entirely: wmid identity must survive any reclassification; a Kind supplies a principle-of-identity TEMPLATE, but an individual's current kind is a time-indexed claim, not its identity. Extend scheme/context qualification to RELATIONS too (part_of, borders), not only to subclass/instance edges, so scheme-relative partonomy (continents, oceans) is representable without asserting one count as absolute.


**8. [high] 3 quantities — dimensional analysis is necessary but not sufficient**

- Problem: The 7-vector SI dimension model is treated as THE compatibility check, but dimension equality neither implies nor is implied by quantity-kind compatibility. Torque (N·m) and energy (J=N·m) share the dimension vector (M,L²,T⁻²) yet must never be added/compared — the stated CI rule 'comparisons require equal dimensions' would pass torque+energy. Conversely, radians, steradians and bare counts are all dimensionless (0,…,0), so the model would let you add an angle to a count. Amount-of-substance (mole) is a base dimension yet is really a count, conflicting with the dimensionless Count kind. Currency has no SI dimension and a time-varying conversion; logarithmic 'units' (dB, pH) and ΔT-vs-absolute-T don't fit the factor/offset model cleanly.
- Recommendation: Make QuantityKind the primary compatibility key and DIMENSION a secondary (necessary-not-sufficient) check: two quantities are addable/comparable only if same QuantityKind, not merely same dimension. Model angle/solid-angle/count as distinct dimensionless KINDS that are not mutually compatible. Treat currency and logarithmic quantities as explicit non-SI kinds with their own (possibly time-indexed, non-ratio) conversion semantics, or declare them out of scope. State that dimensional consistency is one gate among several, not the definition of correctness.


**9. [high] 4 codegen — byte-identical serialization vs idiomatic output**

- Problem: The conformance suite's strongest guarantee — byte-identical RFC 8785 canonical JSON across C#/Java/Python/C++ — is in direct tension with the promise of IDIOMATIC per-language code. Languages differ in int/float distinction (Python), native nullability (C++), decimal vs double, set ordering, and record/equality semantics. Forcing byte-identical serialized object graphs pushes generated types toward a lowest-common-denominator representation and bespoke serializers, i.e. AWAY from idiom. You can have byte-identical OR idiomatic; delivering both for every concept across four type systems is a large, permanent maintenance tax that the cost model understates.
- Recommendation: Relax the parity contract from byte-identical serialization to SEMANTIC equivalence against a canonical data model (same values, same structure, same constraint outcomes, same error codes) with a single shared canonicalizer used only at the conformance boundary — not imposed on the idiomatic runtime types. Reserve byte-identical output for an explicit interchange/DTO projection (the Protobuf/JSON projection already exists for this), and keep the idiomatic class libraries free to use native types. Document the per-language idiom tradeoffs as first-class, not as drift to be eliminated.


**10. [high] 5 scalability & governance — whole-world build and review throughput**

- Problem: Two scale walls. (a) The compiled source of truth is a SINGLE content-addressed wm.json (RFC 8785) for the whole world, recompiled and rehashed on every PR and loaded whole by every generator — O(world) per change; conformance is also whole-world. At millions of concepts this is architecturally untenable, and it contradicts the 'domains evolve independently' claim since the binding version tracks the model in lockstep. (b) Governance mandates that a human reviewer independently verify that EACH cited source exists and supports the claim for every AI PR, while also inviting AI contribution 'at scale.' Human citation-verification is the least-scalable possible step; the rate limits (≤10 merged/domain/day) cap throughput so low that 'model the whole world' is throughput-infeasible, and the alternative (skipping verification) voids the anti-hallucination guarantee.
- Recommendation: Make compilation and conformance INCREMENTAL and per-module (content-address each module; a world release is a manifest of module hashes; generators and CI touch only the changed module's dependency cone). Decouple binding versions from the global model so untouched domains don't churn. For governance, replace blanket human citation-verification with tiered trust: automated source-resolvability + source-tier checks + retrieval-augmented claim-support scoring for routine facts, reserving mandatory human verification for sensitive/contested/low-confidence claims. State an explicit, defensible throughput model instead of an uncapped 'whole world' ambition.


**11. [medium] 2/3 mereology — over-specified and partly false**

- Problem: The meta-model asserts blanket 'transitivity, antisymmetry' for part_of. This is false in general: memberOf is NOT transitive (I am a member of a club; the club is a member of a federation; I am not a member of the federation), and part_of transitivity is relation-type-dependent (component/portion/feature/member behave differently — the classic handle/door/house non-transitivity). A CI rule that materializes transitive closure over memberOf or a generic part_of would generate FALSE facts, poisoning the model and any AI that learns from it.
- Recommendation: Adopt the OBO Relation Ontology discipline the prior-art section already cites: define SEPARATE typed part/member relations (properPartOf, componentOf, portionOf, memberOf, …), and declare transitivity/antisymmetry PER RELATION (memberOf: non-transitive; properPartOf: transitive+antisymmetric), not as a blanket property of 'Relation (E).' Remove the blanket algebra claim from §2.3(E).


**12. [medium] 2 crisp classification — ring species, species boundaries, virus-alive**

- Problem: §2.5 explicitly declares 'Classification is crisp; probabilistic/fuzzy membership out of scope.' But the hardest, most famous cases in the flagship biology domain are inherently non-crisp: ring species (A interbreeds with B, B with C, not A with C — one species or two has no crisp answer), fuzzy species boundaries generally, and 'is a virus alive?' (a contested definitional boundary, which the model would mis-handle as an Alive/Dead Phase — a per-individual state — when it is actually contested category membership). Declaring crispness means WMOOP cannot honestly model exactly the examples that make biology interesting, while marketing itself as a tool to teach AI 'how everything is conceived.'
- Recommendation: Keep membership crisp WITHIN a scheme, but make 'is X a Y' a scheme-qualified, sourced claim that can be marked contested/boundary-case with confidence — so ring species and virus-alive are represented as genuinely contested classification across schemes rather than forced to a crisp verdict or excluded. Do NOT model definitional boundary disputes (virus-alive) as Phases. Soften the §2.5 exclusion from 'crisp, full stop' to 'crisp-within-scheme, contested-across-schemes.'


**13. [medium] 5 identity — dedup/splits at scale**

- Problem: Decentralized ULID minting prevents ID collisions but not SEMANTIC duplication, which is the actual risk. Two contributors (or AIs) model Automobile and Car as separate wmids; the only automated guard is a duplicate-detection gate keyed on 'same normalized name/definition' — trivially defeated by paraphrase, which is exactly what LLMs produce. So the gate gives false confidence while duplicates accumulate faster than human stewards merge them. SPLITS are worse: when one concept is later understood as two, sameAs does not help, and re-pointing existing references breaks downstream version pins.
- Recommendation: Replace surface-string dedup with embedding/semantic-similarity duplicate SURFACING (flag likely dup clusters for human adjudication; never auto-merge) and require new concepts to declare 'distinctFrom' nearest neighbours above a similarity threshold. Design split/merge as first-class, versioned operations with migration shims: a split keeps the old wmid as an abstract/umbrella concept with hasNarrower edges and a MAJOR-bump migration note, so pins resolve to the umbrella rather than breaking. Budget stewardship for dedup as an ongoing cost, not a solved CI check.


**14. [medium] 2/4 enums — closed value sets bake in jurisdiction/time variance**

- Problem: LicenceCategory is a closed Enumeration generated to a native enum. But licence categories differ by jurisdiction and change over time (the EU revises them). A closed enum means any jurisdictional addition is a MAJOR, API-breaking bump that cascades to every binding — and it bakes a closed-world assumption into a fact that is open and jurisdiction-relative. Many 'enums' across world domains (blood types are stable; administrative statuses, licence classes, music genres are not) have this property.
- Recommendation: Distinguish stable/closed enumerations (BloodType) from open/evolving controlled vocabularies (LicenceCategory, admin statuses). Generate open vocabularies as references to a concept set / extensible value registry (string-backed with known members), NOT as closed language enums, so adding a member is a MINOR additive change. Add a CI/lint rule that flags jurisdiction- or time-varying sets modeled as closed enums.


**15. [medium] 4 bootstrapping — the toolchain is the project, and does not yet exist**

- Problem: The entire value proposition rests on wmoopc + four generators + three projectors + conformance runner + CI diff-guard. None of that exists yet: the only code on disk (wmoop.net) is HAND-WRITTEN C#, not generated, and it does not even implement the constraints the schema-codegen spec claims are generated — Moped.cs enforces neither engineDisplacement ≤ 50 cc nor maxSpeed ≤ 45 km/h, despite the spec's worked example and the WM-CONSTRAINT-MAX conformance vector asserting exactly those. The side-by-side 'parity proof' (schema → C# + Python) in the spec is therefore illustrative/aspirational, not tool-produced. Readers are being shown a proof of a capability that has not been built, and a reference impl that already contradicts the spec it references.
- Recommendation: Re-label every current 'generated' snippet and the parity proof as HAND-AUTHORED ILLUSTRATIONS until a generator produces them, and make v0.3's exit criterion the generator emitting the reference C# from WML with constraints enforced and conformance green — not a hand-written stand-in. Treat the compiler/toolchain as the critical path and resource it first; the domain content is worthless until mechanical generation exists. As an immediate fix, make the reference Moped enforce its own schema constraints so the showcase stops contradicting the spec.


**16. [medium] 3 events — participant roles and perdurant structure**

- Problem: Perdurants are called 'first-class,' but the supporting machinery is thin and a whole second role system is missing. Event participation uses thematic/semantic roles (agent, patient, instrument — the fuel/oxidizer/products of a Combustion), which are relations between a process and its participants with role labels — categorically different from the social Roles of §3 (Driver/Employee). The meta-model offers no participant-role construct, and §2.5 excludes temporal-parts calculus, so sub-processes, phases of a process, and temporal mereology of events are unsupported. 'First-class' overstates what is actually a bare category label.
- Recommendation: Add an explicit Participation construct (reified: process × participant × participant-role, with cardinality), distinct from social Role, so events can name their participants' parts (agent/patient/instrument). Add minimal temporal mereology (sub-process / temporal-part relations) if processes are to be more than labels, or downgrade the 'first-class perdurant' claim to 'events are typed but structurally shallow in v1' so the docs don't over-promise for biology/astronomy/music processes.


### Proposed additions (architecture-skeptic)

## New / revised subsections the WMOOP docs MUST include

### A. Paradigm correction — the source of truth is a scheme-aware graph; OOP is a projection
Add to the whitepaper (§3) and the schema-codegen spec (§1.3), superseding "WML-the-OOP-DSL is the single source of truth":

> **The canonical World Model is a scheme-aware knowledge graph of concepts, typed relations, and *classification claims*, not a single-inheritance class model.** Classification is expressed as `classifiedUnder(<concept>, <parent>, scheme:<S>, provenance, rank, asOf)` edges, never as a single structural `is-a`. **The OOP class hierarchy is ONE generated projection, computed for a chosen primary scheme**, with exactly the same status as the OWL, Protobuf and JSON-Schema projections. A concept MAY have parents in several schemes; the projector selects one scheme (configurable) to materialize inheritance and emits the rest as tags/annotations. **Nothing in the source privileges one tree.** Rule: *reviewers reject any source edge that asserts an unqualified, scheme-less `subclass_of` or `instance_of`.*

### B. Behaviour policy (fixes the "write once" over-claim)
Add to schema-codegen §2.2 and the whitepaper abstract:

> Invariant 1 ("write once, replicate everywhere") covers **data structure, declarative constraints, and PURE DERIVATIONS only**. Pure, total functions — derived properties, invariants, unit conversions, `area`/`perimeter`, `canDrive` — MUST be authored once in the shared sandboxed expression language (`WMX`, resolving OQ 7.3) and are code-generated AND behaviour-conformance-tested across languages. **All other behaviour (I/O, side-effecting, heuristic) is per-binding, is NOT covered by Invariant 1, and is a declared drift surface.** Any method that cannot be expressed in `WMX` is hand-written in each language and MUST carry input/output conformance vectors wherever cross-language agreement matters.

### C. Open-world / closed-world bridge (normative; fixes A10 in generated code)
Add as meta-model §6.5 and a DoD check:

> Every property, relation and role slot declares a **completeness mode**: `closed` (the model asserts it has all values) or `open` (absence means *unknown*, Invariant 8). **Generated accessors over `open` slots MUST expose three states — Present / Absent-known-complete / Unknown — and MUST NOT emit a boolean "does-not-have" that returns `false` on absence.** `HasRole<T>()` and `GetRole<T>()` over open role slots return a tri-state / may raise `Unknown` unless a completeness assertion exists. **CI gate:** reject any generator that emits absence-as-false over an `open` slot. (The reference `RoleContainer` MUST be updated accordingly — an empty container is "unknown," not "cannot drive.")

### D. Classification, instantiation and relations are DATED, SCHEME-QUALIFIED CLAIMS
Add to meta-model §2 and §6, and to GOVERNANCE:

> `instance_of`, `subclass_of`, and classification-bearing RELATIONS (`part_of`, `borders`, `member_of`) are **time-indexed, scheme-qualified, sourced claims**, not structural edges. **Identity (`wmid`) is invariant under any reclassification** (Pluto keeps its `wmid` when it ceases to be a Planet). A `Kind` supplies a principle-of-identity *template*; an individual's *current* kind is a dated claim. Scheme qualification applies to relations as well as to taxonomy, so scheme-relative partonomy (4–7 continents; virus-alive) is representable without asserting one answer as absolute.

### E. Role mechanism v2 (cardinality, plurality, history, reification)
Replace schema-codegen §1.5 Driver constraints and meta-model §5:

> - Default `cardinality_per_player` is **`0..*`**; single-hold is the declared, justified exception. Accessors return collections (`GetRoles<T>()`), not the first match.
> - Roles carry a **validity HISTORY** (a set of disjoint intervals + status), not a single `validFrom`/`validTo`, so recurring roles (re-employment at the same employer) keep one role identity.
> - **All n-ary and role-participant relations are reified** as first-class objects (resolves OQ meta-model §10.5 and schema-codegen §7.2 in favour of reification): e.g. `Employment(driverRole, organization, contract, interval)`.
> - `played_by` MAY reference a role/capability predicate ("any bearer of the Player role"), not only a `Kind`.
> - The Driver example and its conformance vectors MUST permit multiple simultaneous licences/employments; delete the blanket `WM-ROLE-DUPLICATE` default.

### F. Quantity compatibility (QuantityKind primary, Dimension secondary)
Replace meta-model §6.4 CI rule 3:

> Two quantities are addable/comparable **iff they share the same `QuantityKind`**; equal `Dimension` is necessary but NOT sufficient (torque ≠ energy though both are M·L²·T⁻²). Angle, solid angle, and bare Count are **distinct dimensionless kinds** and are mutually incompatible. Currency and logarithmic quantities (dB, pH) are explicit non-SI kinds with their own (possibly time-indexed, non-ratio) conversion semantics, or are declared out of scope. Temperature distinguishes absolute `T` from difference `ΔT`.

### G. Mereology — typed part relations with per-relation algebra
Replace the blanket "transitivity, antisymmetry" in meta-model §2.3(E):

> There is no single `part_of`. L0 defines typed relations (`properPartOf`, `componentOf`, `portionOf`, `memberOf`, `featureOf`), and **transitivity/antisymmetry are declared per relation** (`properPartOf`: transitive + antisymmetric; `memberOf`: non-transitive). CI MUST NOT materialize transitive closure over non-transitive relations.

### H. Expressiveness gates for Math/abstract and Events (honesty requirement)
Add to meta-model §2.4 and §2.5:

> Until `WMX` (expression/logic language) and first-class `Operation`/`Function` signatures exist in L0, the Math domain is **nomenclature-only**: a `Theorem.statement` and group axioms are opaque strings, NOT machine-checked, and the "everything machine-checkable" DoD does not apply to them. Claims that WMOOP teaches "how mathematics is conceived" are withdrawn until this lands. Events gain an explicit **`Participation`** construct (process × participant × participant-role), distinct from social `Role`; without temporal-parts support, perdurants are documented as "typed but structurally shallow in v1."

### I. Scale, dedup, enums, and bootstrapping — cost-model corrections
Add to GOVERNANCE and the roadmap/risks:

> - **Incremental build:** compilation and conformance are per-module (content-address each module; a world release is a manifest of module hashes; CI touches only a change's dependency cone). Binding versions are decoupled from the global model. A single whole-world `wm.json` is explicitly rejected at scale.
> - **Dedup:** duplicate detection uses semantic/embedding similarity to SURFACE candidate clusters for human adjudication (never auto-merge); new concepts declare `distinctFrom` nearest neighbours. Split/merge are first-class versioned operations with umbrella-concept migration shims so pins never silently break.
> - **Open vocabularies vs closed enums:** jurisdiction- or time-varying sets (LicenceCategory, admin statuses) are generated as references to an extensible value registry, NOT closed language enums; adding a member is MINOR. A lint flags closed enums over evolving sets.
> - **Governance throughput:** mandatory human citation-verification is reserved for sensitive/contested/low-confidence claims; routine facts use automated source-resolvability + tier checks + retrieval-augmented claim-support scoring. The project publishes an explicit throughput model instead of an uncapped "whole world" promise.
> - **Bootstrapping honesty:** all current "generated" snippets and the schema→C#/Python "parity proof" are re-labelled HAND-AUTHORED ILLUSTRATIONS until `wmoopc` produces them; v0.3's exit criterion is the generator emitting the reference binding (with constraints enforced, conformance green), not a hand-written stand-in. Immediately, the reference `Moped` MUST enforce its own `≤50 cc` / `≤45 km/h` constraints so the showcase stops contradicting the spec.


## completeness-critic

**Summary:** WMOOP's deliverables are strong on theory (prior-art, meta-model, governance, ethics, academic) but have gaps that block them from serving as EITHER a credible paper OR real OSS founding docs. The most serious issue: the normative identifier scheme (the heart of Invariant 4) is specified FOUR incompatible ways across core docs, and several other CI-enforced constants (inheritance-depth cap, invariant count, repo topology, target-language set, role keyword, doc license) also conflict; since the whole project rests on machine-checkable write-once determinism, a validator and generator cannot be built against these contradictions. On the project side, the repos on disk are 5-line README stubs: no README/landing, no quickstart, no toolchain-install story, no SECURITY.md, no SUPPORT.md, no delivered issue/PR templates/CODEOWNERS/CHANGELOG, and the advertised single-command C# build targets a .sln listing zero projects. On the paper side there is no Limitations/threats-to-validity section, no references/bibliography convention (literally 'to be assembled'), and no reproducibility/DOI statement. On modelling: no query/search spec despite that being central to the vision; only ONE domain is worked end-to-end schema->code->test though the task requires two; cross-language parity is proven only for structure, not behaviour; and L2-at-scale plus its relationship to wmoop.db are underspecified. On community: no funding/infra-cost model, no defined communication channels, no cold-start plan for the first 10 domains. Drafted ready-to-fold content (canonical ID/keyword spec, reconciliation table, README, QUICKSTART, SECURITY, SUPPORT, Limitations section, references convention, Query/Search spec, and a second end-to-end Geometry domain) is in additions_markdown.


### Findings


**1. [critical] Modelling / Invariant 4 - identifier scheme (CRITICAL cross-document contradiction)**

- Problem: The normative concept/property/role identifier is specified four incompatible ways. meta-model: opaque wmid (ULID) plus QName wm:{domain.path}:{LocalName} with a COLON before the local name (wm:nature.animals:Dog). contribution: CURIE with a DOT and reserved segments prop./rel./role./ind. (wm:nature.animals.Mammal, wm:transport.role.Driver). schema-codegen: wmoop.transport/Moped with a SLASH and #member (wmoop.transport/Vehicle#wheelCount). csharp-ref: wm:transport/Moped. The generator, the ID-immutability gate, referential-integrity checks, cross-domain version pins, and the content-addressed wm.json all key off exactly one ID grammar. With four grammars none of the machine-checkable gates (the project's entire safety claim) can be implemented, and contributors/AI following different docs produce references that never resolve against each other.
- Recommendation: Pick ONE normative ID grammar, define it only in meta-model L0, and have every other doc reference it. Resolve the opaque-ID-vs-QName duality explicitly (recommend immutable wmid ULID as true identity plus one QName syntax as human address; machine refs use wmid, docs/codegen use QName). Add a CI check that the QName regex equals the published grammar. Canonical spec drafted in additions_markdown section A.


**2. [critical] Project - README / landing page (repos are empty stubs)**

- Problem: On disk wmoop.doc/README.md and wmoop.net/README.md are 5-line/2-line stubs; none of the reviewed documents are committed. A developer, student, researcher or AI agent arriving at github.com/WMOOP gets no pitch, no what/why, no map to the real docs. The whitepaper is not a substitute for a landing README. The single highest-traffic entry point is blank, so the carefully designed academic and AI on-ramps are unreachable.
- Recommendation: Add a top-level README to wmoop.doc (org landing) and each binding repo: tagline, one-paragraph pitch, three-layer picture, repo map, 5-line quickstart, links to whitepaper/CONTRIBUTING/GOVERNANCE/academic. Draft in additions_markdown section C.


**3. [high] Modelling discipline - inheritance-depth cap conflict (CI-enforced constant)**

- Problem: Max inheritance depth is a hard CI gate but is given four values: meta-model warn over 5 / error over 7; schema-codegen cap 6, warn at 5; contribution soft cap 5; academic 3-4. A 6-deep chain passes one document's rule and fails another's; the validator can hold only one number.
- Recommendation: Fix one policy (recommend meta-model warn over 5 / error over 7 as the CI rule) and have others cite it; mark academic 3-4 as a pedagogical heuristic, not the gate.


**4. [high] Architecture - number of invariants (6 vs 8) is contradictory**

- Problem: paper-frame, schema-codegen, contribution and governance state SIX normative invariants and quote them verbatim. meta-model section 9 adds Invariant 7 (ontological completeness) and 8 (identity lifecycle) as adopted, and declares itself the authority others must align to. The project thus simultaneously has six invariants and eight. Tooling and docs that reference the invariants cannot tell which set is canonical.
- Recommendation: Decide 6 or 8. If 7/8 are accepted, promote them into paper-frame section 3.1 and governance's invariant table so all docs enumerate the same set; otherwise label them corollaries of I1-I6, not new invariants.


**5. [high] Project - repo topology inconsistency (compiler and compiled-model home)**

- Problem: paper-frame names wmoop.doc plus wmoop.{net,java,py,cpp}. schema-codegen adds wmoop.tools (home of wmoopc and generators) and makes compiled wm.json a Release of wmoop.doc. contribution instead puts the meta-schema AND the compiled JSON/JSON-LD export in a repo named wmoop.json, and adds wmoop.js and wmoop.db. So where is the compiler and where is the compiled artifact have two incompatible answers, and two target repos appear in only one document.
- Recommendation: Publish one authoritative repo-topology table (GOVERNANCE or paper) and reference it everywhere; decide compiler home, compiled-artifact home, and the final binding list (incl. whether JS and a DB binding are v1). Reconciliation table in additions_markdown section B.


**6. [high] Project - target-language scope inconsistency**

- Problem: paper-frame, meta-model and schema-codegen target C#, Java, Python, C++. contribution repeatedly promises C#/Java/Python/C++/JavaScript plus a SQL DB (wmoop.db), and its DoD, metrics and one-edit-becomes-correct-in-six-repos claim depend on the larger set, while the parity metric M2 and conformance runner are scoped to four. Contributors are told one edit yields six outputs, but the conformance contract covers four.
- Recommendation: Reconcile the official binding list in one place; update CONTRIBUTING, M2, and the runner contract. If JS and a relational projection are aspirational, mark them planned, not conformance-gated.


**7. [high] Project - SECURITY.md absent; supply-chain and untrusted-execution surface unaddressed**

- Problem: No SECURITY.md exists, and no doc addresses: (1) wmoopc/generators parse contributor- and AI-authored model files and a CEL-like invariant expression language (a code-execution/resource-exhaustion surface); (2) generated libraries publish to NuGet/Maven/PyPI/vcpkg (supply chain: signing, provenance, typosquatting, who holds publishing creds) with no policy; (3) AI agents open PRs at scale. A malicious model file or compromised release bot could ship arbitrary code to every downstream consumer, and reporters have no private disclosure channel.
- Recommendation: Add SECURITY.md (private reporting, disclosure window, scope) plus a supply-chain section (sandboxed bounded expression eval, signed releases with provenance attestation, protected publishing creds, pinned toolchain). Draft in additions_markdown section E.


**8. [high] Project - quickstart and toolchain installation missing**

- Problem: Every workflow hinges on running wmoop/wmoopc, but no doc says how to obtain or install it (binary? dotnet tool? pip? OSes? tool-vs-model versioning), and there is no clone-to-first-green-PR quickstart. A student or AI agent cannot perform step 3 of the contribution lifecycle; the dense local reward signal AI_CONTRIBUTING sells is unreachable because the oracle has no install path.
- Recommendation: Add a QUICKSTART (install CLI, clone, generate sample slice, run conformance, first trivial PR) and specify CLI distribution and version mapping. Draft in additions_markdown section D.


**9. [high] Modelling - no query/search specification for the knowledge base**

- Problem: The vision (navigable metaverse, AI learning the shape of the world, a reusable research reference) assumes the model can be queried, but no doc specifies how. No query API, no search index, no graph-query story for the primary artifact; OWL/SPARQL is only an optional downstream projection. A consumer cannot answer all mammals with legCount=4, every role a Person can play, which domains depend on nature.people, or find the concept for moped. This undercuts the KB half of the dual value proposition.
- Recommendation: Add a Query and Search section: querying compiled wm.json locally (documented shape plus reference helper per binding), SPARQL via the OWL projection, full-text search over i18n labels/definitions, and how generated libraries expose navigation (role registries, relation inverses, type chains). Outline in additions_markdown section I.


**10. [high] Modelling - only one domain worked end-to-end (task requires two)**

- Problem: The task requires a concrete end-to-end example schema->generated code->test for at least two domains. Only Transport (Vehicle->Moped) plus the Person/Driver role is carried the full distance (WML plus generated C# plus Python plus conformance). Person/Driver is part of that same Transport example, not a second independent domain. Math/Group, Music/Note, Animals, Geography appear only as isolated snippets without generated code or tests. A skeptic cannot confirm the pipeline generalizes to ontologically different shapes (abstract/perdurant) from one physical-object example.
- Recommendation: Add a second full schema->code->conformance walkthrough for a different domain - Geometry (abstract types plus polymorphism plus units) or Music (Abstract PitchClass plus Perdurant NoteOccurrence), which exercise the Abstract/Perdurant categories Transport does not. Geometry sketch in additions_markdown section J.


**11. [high] Paper - no Limitations / threats-to-validity section**

- Problem: For a credible scientific artifact the absence of an explicit Limitations section is serious. The project makes strong falsifiable claims (OntoClean rigidity checkable by non-experts; single-source generation lossless and byte-parity-identical; roles-over-inheritance scales) but never states where they might fail: contributors mis-judging rigidity, silent CWA/OWA mismatch, hand-written behaviour diverging across languages, the empty-commons cold start, Western/English ontological bias in L0, and the untested assumption codegen stays idiomatic at scale. The Risks register is project-ops focused, not scientific threats-to-validity.
- Recommendation: Add a Limitations and Threats to Validity section distinct from the Risks register, honestly enumerating the above and what v0/v1 does NOT yet demonstrate. Draft in additions_markdown section G.


**12. [high] Paper - no references/bibliography convention; bibliography to be assembled**

- Problem: prior-art ends with a prose Indicative references paragraph (surnames only, no year-keys, no DOIs), and paper-frame section 9 says references are to be assembled. There is no citation style, no bibliography file/format, and no rule linking in-text claims to entries. This is distinct from the model's SOURCES.yaml (facts in the model). As a paper it is currently uncitable and unverifiable; as repo docs there is no agreed way to cite sources in prose.
- Recommendation: Adopt a citation convention (references.bib plus a CSL style, or an [Author Year] key scheme) and one bibliography file in wmoop.doc; convert the prose references to real entries with years/DOIs. Convention in additions_markdown section H.


**13. [high] Governance / licensing - doc repo LICENSE contradicts the chosen content license**

- Problem: governance section 10 says documentation and model are CC-BY-4.0 (chosen) and the whole section 10.1 ethos argument rests on it. On disk wmoop.doc/LICENSE is Apache-2.0. So every document ships under a license the governance doc says it must not use, and paper-frame still calls CC-BY proposed (open for ratification) while governance calls it chosen - a third inconsistency on the same question. Downstream reusers get contradictory signals and the attribution guarantee the ethics argument depends on is not in force.
- Recommendation: Decide once (recommend CC-BY-4.0 for docs/model), replace wmoop.doc/LICENSE accordingly (or add LICENSE-DOCS plus per-file SPDX headers), change paper-frame wording from proposed to chosen, and add the SPDX-header CI check governance already promises.


**14. [medium] Normative DSL - role keyword and format-name inconsistency; serialization open vs decided**

- Problem: The role-player keyword is plays/player (meta-model), played_by (schema-codegen/csharp-ref), and appliesTo (contribution/academic) - three spellings of the same normative field. The canonical format is named WML only in schema-codegen. And meta-model Open Question 1 still debates JSON-LD plus SHACL vs OWL profile as unresolved while schema-codegen presents the WML-source-with-projections decision as settled. Generators/contributors keyed to different field names or format assumptions will not interoperate, and is serialization decided has two answers.
- Recommendation: Standardize one keyword (recommend playedBy), formally adopt (or drop) the name WML everywhere, and close meta-model OQ1 by pointing to the schema-codegen decision so it is no longer listed as open.


**15. [medium] Modelling - cross-language behaviour parity not guaranteed (only structure/constraints are)**

- Problem: schema-codegen puts all method bodies/domain behaviour in the hand-written half of the generation gap, and section 3 pins only structure, constraints, defaults, role semantics, relations, enums and serialization - not behaviour (deferred as open question 6). The invariant expression language is also undecided. So two bindings can compute the same operation (a unit conversion, canDrive, a derived property) differently and both pass conformance, undermining the headline semantically-identical claim. The promise one edit, identical meaning everywhere is true only for data shape, not logic.
- Recommendation: Either specify a single sandboxed expression language (CEL-like) so invariants and derived values are generated (not hand-ported) and thus conformance-covered, and/or add a behaviour-conformance vector category with input->output cases; and state plainly that hand-written behaviour is outside the parity guarantee.


**16. [medium] Community / sustainability - no funding or infrastructure-cost model**

- Problem: The risks register covers bus factor but never money. CI on every PR means generating and conformance-testing in 4-6 languages plus hosting a public dashboard and later an online explorer - recurring compute/hosting cost that scales with contribution volume and AI-agent PR traffic (which AI_CONTRIBUTING actively invites). There is no funding plan, no owner of infra cost, and no what-if-the-founder-stops-paying plan. A model-the-whole-world commons with no funding model is a sustainability risk the paper should not omit.
- Recommendation: Add a Funding and Sustainability subsection: cost drivers, candidate routes (academic grants given the pedagogy, a foundation/fiscal host, sponsorship), infra-cost owner, and graceful degradation (the model is plain text in git and self-hostable).


**17. [medium] Community - communication channels and cadence undefined**

- Problem: CONTRIBUTING and FAQ mention Discussions once; otherwise there is no defined place to talk (chat? forum? mailing list?), no community-call cadence, and no triage/office-hours rhythm. governance routes disputes through issues/TSC but day-to-day collaboration and newcomer questions have no home, which matters for bootstrapping contributors and academic cross-cohort handoffs.
- Recommendation: Define official channels in SUPPORT.md and link from READMEs (GitHub Discussions for Q&A, one real-time chat, a periodic public community call, a private security channel). Draft in additions_markdown section F.


**18. [medium] Paper - reproducibility / archival / citable artifact missing**

- Problem: How to cite says cite the versioned wmoop.doc release, but there is no DOI/Zenodo archival, no artifact-availability statement, and no reproducibility recipe for the metrics (M1-M7) or the claimed verified dotnet build, 13 assertions pass. Reviewers expect an archived DOI-bearing artifact and reproducible results; a changing main branch is not a stable citation target.
- Recommendation: Add a reproducibility/artifact statement: mint DOIs for releases (Zenodo-GitHub), pin the toolchain used for any reported numbers, and document exact commands to reproduce the reference build/tests and the dashboard metrics.


**19. [medium] Community - no concrete plan to attract the first 10 domains/contributors (cold start)**

- Problem: The roadmap and academic program describe channels, but the empty-commons cold start is never directly tackled. No go-to-market/launch plan, no named outreach to first candidate stewards, no partnership list, no seed-these-10-domains-ourselves strategy so the commons is non-empty on day one. Metrics target at least 6 domains and at least 50 contributors with no acquisition path.
- Recommendation: Add a Bootstrapping the commons / first 10 domains plan: which domains the founders seed themselves, target academic partners for the studio, a launch sequence, and curated good-first-domains - tied to the paired quality/volume guardrail so the push does not degrade quality.


**20. [medium] Meta-model - foundational-category count internally muddled**

- Problem: meta-model claims 8 foundational categories but the lattice enumerates A,B,C,D,E,F,H (7 letters, skipping G = the Type/Individual axis) under root Entity, and the summary lists Endurant, Perdurant, Abstract, Quality/Quantity, Relation, Role, Collection (7). Whether the count is 7, 8 (counting Entity), and whether Quality and Quantity are one category or two, is ambiguous. Since L0 is sold as closed/fixed, the exact closed set must be unambiguous or the closed-world DoD check cannot be written.
- Recommendation: State the closed set as an explicit numbered list with a stable count, clarify whether Entity (root) and the Type/Individual axis count toward it, and make the A-H lettering match the number (or drop the lettering).


**21. [medium] Modelling - L2 at scale and the L2-to-database relationship underspecified**

- Problem: L2 is handled for small sets (the planets) and bulk imports are gated, but there is no story for large reference datasets (GBIF/periodic-table/ISO-3166 scale) that prior-art section 2.4 cites as proof the approach scales. Are millions of individuals generated into source code? Into wmoop.db? Distributed how? The L2-to-wmoop.db relationship is never defined, and generating hundreds of thousands of instances as compiled classes is infeasible. The scalability claim is not matched by an L2 delivery mechanism.
- Recommendation: Specify an L2 storage/distribution tier separate from code generation (data files plus the wmoop.db relational/graph projection plus a query API), with a size threshold above which instances live as data, and define the L2-to-wmoop.db mapping.


**22. [medium] Project - issue/PR templates, CODEOWNERS, CHANGELOG not delivered as files; SUPPORT absent**

- Problem: Issue templates, the AI PR template, CODEOWNERS and a CHANGELOG are referenced across CONTRIBUTING/AI_CONTRIBUTING/academic/governance but exist only as prose; none exist as files on disk (no .github/ directory), and the changelog format/location is never concretely specified. Contributors and the CI gates that check template fields / CODEOWNERS coverage cannot function without the actual files.
- Recommendation: Deliver the files: .github/ISSUE_TEMPLATE/*.yml, PULL_REQUEST_TEMPLATE.md (with the AI-disclosure section), a root CODEOWNERS wired to MAINTAINERS.yaml, and a CHANGELOG convention (Keep a Changelog plus per-domain sections tied to SemVer). SUPPORT.md drafted in additions_markdown section F.


**23. [medium] Reference implementation - empty .sln contradicts the verified-build claim**

- Problem: csharp-ref says No .sln changes; the human adds the projects and claims the build is verified. On disk wmoop.net/Wmoop.Net/Wmoop.Net.sln references ZERO .csproj files. So dotnet build on the solution builds nothing; the advertised newcomer flow (open solution, build, run demo, 13 assertions pass) fails out of the box. The verified build must have been per-project, not via the solution newcomers open.
- Recommendation: Add the six src projects and the test project to the .sln (dotnet sln add) and verify dotnet build plus dotnet test on the SOLUTION; or state the solution is intentionally empty and give per-project commands. Make the README build instructions match reality.


**24. [low] Modelling - localization flow into generated artifacts, and required-language policy, unresolved**

- Problem: Localized labels (name@lang, prefLabel/altLabel) are well-motivated, but how they reach generated code (resource files? localized XML-doc comments? runtime lookup?) is unspecified, and meta-model OQ6 leaves required-languages-at-submission and non-Latin scripts open. academic section 9 says translate human-facing fields but the schema-codegen generators emit only English identifiers with no label-projection story. i18n is specified at the model layer but dangles at the generation layer.
- Recommendation: Specify the label-projection contract (where localized labels land in each binding), close OQ6 with a minimum-language policy and script handling, and add a conformance vector that a localized label round-trips.


**25. [low] Modelling - n-ary relations / relation attributes left open yet required downstream**

- Problem: meta-model OQ5 leaves unresolved whether n-ary relations and attributed associations (a teaches relation with a semester; who owns operates/operatedBy, also schema-codegen OQ2) are reified as entities or allowed as attributed edges. But relations are first-class in L0, appear in conformance vectors, and must be generated - so codegen and the conformance contract cannot be finalized while this is open. It is a foundational modelling decision presented as a minor open question.
- Recommendation: Resolve it in L0 before v1 (recommend reifying all non-binary and attributed relations as association entities for uniform cross-language generation) and update the relation template, generator mapping, and conformance categories.


### Proposed additions (completeness-critic)

# Ready-to-fold additions

Drafted to drop into `wmoop.doc`. Where a draft resolves a contradiction it picks one option explicitly; adjust the chosen value if maintainers prefer another, but keep it single-valued.

---

## A. Canonical identifier and reserved-keyword specification (resolves the 4-way ID conflict)

> Place in meta-model (L0) as the single normative source. Every other document links here, not restates it.

Identity has two parts.

| Part | Form | Mutability | Used by |
|---|---|---|---|
| Opaque id (`wmid`) | `wmid:` + Crockford-base32 ULID (26 chars) | immutable forever | all machine references, content hashing, cross-domain pins |
| QName (human address) | `wm:<domain.path>:<LocalName>` | stable by policy; rename = new QName + `altQName` + `replacedBy` | docs, code generation, CLI |

QName grammar (the one true grammar, ABNF):

```
qname        = "wm:" domain-path ":" local-name [ "#" member ]
domain-path  = segment *("." segment)          ; lowercase, dotted, singular
segment      = lowercase *(lowercase / DIGIT)
local-name   = ( UPPER *(ALPHA / DIGIT) )      ; PascalCase: Concept/Role/Event/Abstract/Collection/Category/Enum
             / ( LOWER *(ALPHA / DIGIT) )      ; camelCase: Property/Relation
member       = local-name                      ; a property/relation on the owning type
```

Normative examples: `wm:nature.animals:Mammal`, `wm:nature.animals:Mammal#legCount`, `wm:transport.driving:Driver`, `wm:space.planets:Mars` (an L2 individual uses the same grammar; its node `kind` marks it as an individual, do NOT encode kind in the id).

Forbidden forms (reject in CI): slash separators (`wmoop.transport/Moped`), reserved kind-segments in the path (`...role.Driver`, `...prop.legCount`, `...ind.Mars`), and English labels as keys. Kind is a property of the node, never part of the id.

Reserved keyword registry (normative field names; no synonyms):

| Concept | Normative keyword | Rejected synonyms in drafts |
|---|---|---|
| role's allowed player(s) | `playedBy` | `played_by`, `plays`, `appliesTo` |
| rigid specialization | `subClassOf` | `extends`, `kindOf`, `specializes` |
| part-whole | `partOf` | (ok) |
| cross-cutting tag | `category` | `classifiedAs` (keep as the relation, not the tag field) |

A CI check asserts every authored file uses only registered keywords.

---

## B. Reconciliation table for the other conflicting constants

> Place in GOVERNANCE as "Normative constants". One value each; all other docs cite this table.

| Constant | Normative value | Notes |
|---|---|---|
| Inheritance depth | warn at depth over 5, error at depth over 7 | academic "3-4" is a teaching heuristic, not the CI gate |
| Core invariants | I1-I6 normative; I7 (ontological completeness), I8 (identity lifecycle) adopted as I7-I8 | all docs enumerate the same 8; the "six" phrasing is updated |
| Compiler/generator home | `wmoop.tools` | |
| Compiled artifact (`wm-<ver>.json`) home | GitHub Release of `wmoop.doc` | `wmoop.json` holds ONLY the JSON-Schema meta-schema |
| Binding repos, v1-gated | `wmoop.net`, `wmoop.java`, `wmoop.py`, `wmoop.cpp` | `wmoop.js`, `wmoop.db` = planned, not yet conformance-gated; say so in CONTRIBUTING |
| Doc/model license | CC-BY-4.0 | replace `wmoop.doc/LICENSE`; code stays Apache-2.0 |
| Canonical format name | WML (WMOOP Modeling Language) | adopt everywhere; projections to OWL/JSON-Schema/Protobuf |

---

## C. `wmoop.doc/README.md` (org landing)

```markdown
# WMOOP - World Map Object-Oriented Programming
**Describe World into OOP. Map all World Objects into Programming Languages.**

WMOOP is an open, collaborative effort to model the real world - biology, math, music,
astronomy, geography, transport, language - as ONE language-neutral, object-oriented
knowledge model (the World Model), from which idiomatic C#, Java, Python and C++ libraries
are generated and conformance-tested. You model once; every language updates automatically.
Humans and AI contribute against the same automated Definition of Done.

## Why
No shared, sourced, machine- and human-readable OOP model of the world exists today.
WMOOP is ontology-first and developer-first: rigorous enough to cite, concrete enough to compile.

## Architecture in one picture
- L0 meta-model - small, fixed upper ontology (the grammar)
- L1 domain models - versioned, acyclic modules (the content you contribute)
- L2 instances - optional, cited reference data (e.g. the planets)
Composition, interfaces/traits and roles over deep inheritance. A Person who drives is a
Person with a Driver role - never Driver : Person.

## Repo map
| Repo | What |
|---|---|
| wmoop.doc (here) | Source of truth: the World Model + whitepaper + governance/ethics/academic docs |
| wmoop.tools | The wmoopc compiler, generators, projectors, conformance runner |
| wmoop.json | The JSON-Schema meta-schema |
| wmoop.net / .java / .py / .cpp | Generated, conformance-tested language bindings |

## Start here
- New here? Whitepaper + QUICKSTART
- Contribute? CONTRIBUTING (AI agents: AI_CONTRIBUTING)
- Teaching a course? academic/README
- Rules? GOVERNANCE, ETHICS, SECURITY, SUPPORT

## License
Code: Apache-2.0. Model and docs: CC-BY-4.0 (attribution is the point - a provenance-first project).
```

---

## D. `wmoop.doc/QUICKSTART.md`

```markdown
# Quickstart (first green PR in ~15 minutes)

## 1. Install the toolchain
wmoopc is distributed as a self-contained CLI (one binary per OS) from wmoop.tools releases,
and as a dotnet tool:
    dotnet tool install -g wmoop.cli        # or download wmoopc-<os> from wmoop.tools/releases
The CLI version tracks the model it targets: wmoopc --model-version prints the compatible range.

## 2. Clone and build the sample slice
    git clone https://github.com/WMOOP/wmoop.doc && cd wmoop.doc
    wmoopc compile            # validates model/** -> wm.json (+ sha256)
    wmoopc gen --lang csharp  # generates the C# binding into a temp dir
    wmoopc conformance        # runs the golden vectors

## 3. Make your first change
Add one localized label to an existing concept (safest first PR):
    # in model/transport/Moped.wml.yaml, add:  name: { en: Moped, ro: Moped }
    wmoopc validate && wmoopc lint && wmoopc conformance   # all green?
Open a PR. CI runs the SAME checks. A steward reviews meaning; the machine checks shape.

## What NOT to do
Never hand-edit generated binding code (generated/**). Change the model; regenerate.
```

---

## E. `wmoop.doc/SECURITY.md`

```markdown
# Security Policy

## Reporting a vulnerability
Email security@wmoop.org (PGP key in /SECURITY-PGP.asc). Do NOT open a public issue for a
vulnerability. We acknowledge within 72h and aim for coordinated disclosure within 90 days.

## Scope
- The wmoopc compiler/generators and the conformance runner (they parse and evaluate
  contributor- and AI-authored model files and invariant expressions).
- The release/publishing pipeline for generated packages (NuGet/Maven/PyPI/vcpkg).
- CI workflows and the release bot.

## Threat model and controls
- Untrusted model input: wmoopc treats all model files as untrusted data. The invariant
  expression language is a sandboxed, non-Turing-complete subset (no I/O, bounded time/memory).
  Parsing is resource-limited; malformed/oversized files fail closed.
- Supply chain: releases are built on pinned, hash-locked toolchains, published with provenance
  attestation (SLSA) and signed; publishing credentials are org-protected and never exposed to
  PR CI. Package names are reserved to prevent typosquatting.
- AI-authored PRs run with no elevated permissions, under GOVERNANCE section 8 rate limits, and
  cannot trigger a publish.

## Supported versions
Security fixes land on the latest model MAJOR and the previous one.
```

---

## F. `wmoop.doc/SUPPORT.md`

```markdown
# Getting help
- Questions / modelling discussions: GitHub Discussions on wmoop.doc.
- Real-time chat: [community chat link] (#general, #modelling, #tooling, #academic).
- Bugs / feature requests: open an issue with the matching template.
- Security issues: see SECURITY.md (do not use public channels).
- Community call: monthly, open to all; agenda + notes in governance/community-calls/.
- Academic adopters: #academic channel + the Instructor guide (academic/README.md).

Search existing issues/discussions first. Be kind; argue the artifact, not the author.
```

---

## G. Paper section - Limitations and Threats to Validity (new, distinct from the Risks register)

```markdown
## Limitations and Threats to Validity

This is a position/architecture paper; the following are stated plainly rather than hidden.

Construct validity.
- Rigidity is judged by humans. OntoClean meta-properties are checkable given correct
  annotations, but whether a contributor correctly labels a property rigid/anti-rigid is a human
  judgement CI cannot verify. Mislabelling re-admits the errors the gates forbid.
- Behavioural parity is not proven. Conformance pins structure, constraints and serialization,
  not hand-written method behaviour; two bindings may compute the same operation differently.
  "Semantically identical" currently means data-identical, not logic-identical.

Internal validity.
- CWA/OWA bridge. Using OWL reasoning for validation while generating closed-world code risks
  silent mismatch; the bridge policy mitigates but does not eliminate this.
- Losslessness of generation is asserted, not yet empirically measured across all languages.

External validity / generalization.
- Only Transport (+ Person/Driver) is worked end-to-end at submission. Generalization to abstract
  (Math) and perdurant (Music) domains is designed but not yet demonstrated with generated code + tests.
- Ontological bias. L0 draws on BFO/DOLCE/UFO - a Western analytic tradition - and defaults to
  English identifiers; non-Western category systems and non-Latin scripts are under-tested.

Sustainability threats.
- Cold start. A commons has little value until populated; the empty-commons problem is unsolved
  beyond the academic on-ramp.
- Cost. Multi-language codegen + conformance on every PR (amplified by AI PR volume) has recurring
  cost with no funding model yet.

What v0/v1 does NOT yet show: real downstream reuse, a second generated language at parity, an
externally-authored domain surviving review, or any empirical evaluation number.
```

---

## H. References / citation convention (resolves "to be assembled")

```markdown
## Citation convention
- The paper's scholarly references live in wmoop.doc/paper/references.bib (BibTeX), rendered with
  the CSL style in paper/style.csl (default: a numeric IEEE-like style).
- In-text citations use [Author Year] keys (e.g. [Brachman 1983], [Guarino & Welty 2002]), each
  resolving to a .bib entry with DOI/ISBN/URL + accessed date.
- This is SEPARATE from model provenance: facts inside the World Model cite SOURCES.yaml
  (GOVERNANCE section 10.2); the paper cites references.bib.
- Releases are archived with a DOI (Zenodo-GitHub integration). "How to cite" points at the DOI of
  the specific release, not main.
- Action: convert prior-art's prose "Indicative references" into real .bib entries with years/DOIs
  before the first ratified release.
```

---

## I. Query and Search specification (outline to expand into a section)

```markdown
## Querying and searching the World Model

Four supported access paths, in order of weight:

1. Local structured queries over wm.json. The compiled artifact is a documented JSON graph. Each
   binding ships a read-only query helper over the generated types:
   model.conceptsWhere(c => c.Property("legCount") == 4), person.rolesOf<Driver>(),
   model.dependentsOf("wm:nature.people:Person"), model.typeChain("wm:transport:Moped").
   Generated, so identical across languages and conformance-tested.

2. Graph queries via the OWL/RDF projection (SPARQL). For open-ended queries ("every Abstract type
   with no instances", "all roles playable by Person") the OWL projection exposes a SPARQL endpoint.
   The research/semantic-web path.

3. Full-text search over labels/definitions. A generated index keyed by wmid, covering
   prefLabel/altLabel in every language and definition, powers "find the concept for moped" and the
   explorer search box. i18n-aware.

4. L2 reference data at scale. Large instance sets are NOT generated as code; they live as data and
   are queried through the wmoop.db relational/graph projection (see L2 scaling spec).

A conformance vector category "query" asserts the same structured query returns the same result set
in every binding.
```

---

## J. Second end-to-end worked domain - Geometry (schema -> generated code -> test)

> Chosen deliberately to exercise AbstractType + polymorphism + units that the Transport example does not. Pair with the existing Transport example to satisfy the two-domains-end-to-end requirement.

WML (model/math/geometry/*.wml.yaml, module wm:math.geometry):

```yaml
module: { id: wm:math.geometry, version: 0.1.0, dependsOn: [ { module: wm:core, version: "^1" } ] }
abstractTypes:
  - qname: wm:math.geometry:Shape
    kind: abstract
    definition: A plane figure characterized by its boundary.
    operations:
      - { name: area,      returns: { quantityKind: wm:core:Area,   unit: wm:core:m2 } }
      - { name: perimeter, returns: { quantityKind: wm:core:Length, unit: wm:core:m } }
  - qname: wm:math.geometry:Circle
    subClassOf: wm:math.geometry:Shape
    properties: [ { name: radius, quantityKind: wm:core:Length, unit: wm:core:m, cardinality: "1" } ]
  - qname: wm:math.geometry:Rectangle
    subClassOf: wm:math.geometry:Shape
    properties:
      - { name: width,  quantityKind: wm:core:Length, unit: wm:core:m, cardinality: "1" }
      - { name: height, quantityKind: wm:core:Length, unit: wm:core:m, cardinality: "1" }
# Square is NOT subClassOf a mutable Rectangle (Liskov) - it is its own immutable Shape.
```

Generated C# (generated/Math/Geometry/Circle.Gen.cs):

```csharp
public abstract class Shape { public abstract Area Area { get; } public abstract Length Perimeter { get; } }
public sealed partial class Circle(Length radius) : Shape {
    public Length Radius { get; } = radius;
    public override Area   Area      => Area.SquareMetres(Math.PI * Radius.Metres * Radius.Metres);
    public override Length Perimeter => Length.Metres(2 * Math.PI * Radius.Metres);
}
```

Generated Python (generated/math/geometry/circle_gen.py):

```python
class ShapeGen:  # abstract
    def area(self) -> Area: raise NotImplementedError
    def perimeter(self) -> Length: raise NotImplementedError
class CircleGen(ShapeGen):
    def __init__(self, radius: Length) -> None: self.radius = radius
    def area(self) -> Area: return Area.square_metres(math.pi * self.radius.metres ** 2)
    def perimeter(self) -> Length: return Length.metres(2 * math.pi * self.radius.metres)
```

Conformance vector (conformance/math/circle_area.case.yaml):

```yaml
id: conf.math.geometry.circle-area
given: { construct: { type: wm:math.geometry:Circle, with: { radius: { value: 2, unit: m } } } }
expect:
  getProperty: { handle: subject, call: area }
  equals: { value: 12.566370614359172, unit: m2 }   # pi*4, dimension = Area
  dimension_check: pass                               # area has dimension L^2; perimeter L^1
```

This proves the pipeline on an abstract, unit-bearing, polymorphic domain independently of the physical-object Transport domain, and shows the dimensional guarantee (area is Area, not a bare double) reaching generated code in two languages.

