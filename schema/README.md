# WML — the machine contract (validation & structure schema)

This directory is the **machine-readable grammar of WML** (the *WMOOP Modeling Language*): the
same language described prose-first in [`../docs/03-architecture.md`](../docs/03-architecture.md),
here pinned down as a schema a machine can enforce. It is the concrete realisation of the
*"JSON Schema meta-schema"* that `docs/03-architecture.md` §1.3 and §2.4 call for, plus its XSD
twin for an XML serialization, plus the validator that runs them against the canonical model in
[`../model/`](../model/).

> **One grammar, two faces.** The structure and constraints of WML are defined **once** and
> expressed in two interchangeable forms:
> - [`wml.schema.json`](wml.schema.json) — **JSON Schema 2020-12** (for the YAML/JSON form), and
> - [`wml.xsd`](wml.xsd) — **W3C XML Schema** (for the XML form).
>
> They encode the *same* rules (identifier shapes, kinds, cardinalities, required slots,
> provenance). Pick whichever matches your toolchain; the YAML under `model/**` stays the single
> source of truth (Invariant 1) and the XML is a *generated projection* of it.

Normative keywords (MUST/SHOULD/MAY) follow RFC 2119.

---

## 1. Files

| File | What it is |
|------|------------|
| [`wml.schema.json`](wml.schema.json) | JSON Schema (Draft 2020-12) meta-schema for a WML module file (YAML → JSON). The context-free grammar. |
| [`wml.xsd`](wml.xsd) | The XSD equivalent, for the WML-in-XML serialization. Same grammar, XML idiom. |
| [`validate_wml.py`](validate_wml.py) | The **oracle**: runs the JSON Schema grammar gate **and** the cross-file semantic gates (S1–S6, referential integrity) that no context-free grammar can express. Optionally validates the XML projections against the XSD. |
| [`yaml_to_xml.py`](yaml_to_xml.py) | Deterministic projector: merges each module's `*.wml.yaml` files into one `<module>` XML document under [`examples/`](examples/). The XML is **generated** — never hand-edited. |
| [`examples/*.wml.xml`](examples/) | The six seeded modules projected to WML-in-XML (exercise the XSD and double as a single-file view of each module). |
| [`requirements.txt`](requirements.txt) | The validator's Python dependencies. |

---

## 2. Quickstart

```bash
# 1. install the validator's deps (PyYAML + jsonschema + xmlschema)
python -m pip install -r schema/requirements.txt

# 2. validate the whole model: grammar (JSON Schema) + semantics + XSD projections
python schema/validate_wml.py

# 3. (re)generate the XML projections after editing any model/*.wml.yaml
python schema/yaml_to_xml.py

# 4. CI diff-guard: fail if the committed XML is stale versus the YAML
python schema/yaml_to_xml.py --check
```

`validate_wml.py` exits `0` when every gate is green and `1` on any error (warnings alone do not
fail unless you pass `--strict`). This is the automated **Definition of Done** (Invariant 6).
Useful flags: `--no-xsd` (skip the XSD check), `--lint-agentive` (warn on `-er`/`-or` concepts that
may really be roles), and a path argument to validate a subtree (`python schema/validate_wml.py
model/transport`).

Validating directly, without the oracle:

```bash
# JSON side — any JSON-Schema tool; here check-jsonschema over the YAML
pipx run check-jsonschema --schemafile schema/wml.schema.json model/transport/*.wml.yaml

# XML side — any XSD processor
xmllint --schema schema/wml.xsd schema/examples/wmoop.transport.wml.xml --noout
```

---

## 3. The WML language

A WML **module file** (`*.wml.yaml`) holds a module's `module:` header and/or one or more of its
declaration sections. A module MAY span several files; exactly **one** of them carries the header
(the others are continuation fragments, e.g. [`model/transport/roles.wml.yaml`](../model/transport/roles.wml.yaml)).
The top-level keys are:

```yaml
module:        { ... }        # the header (in the module's primary file)
datatypes:     [ ... ]        # named primitive refinements
enumerations:  [ ... ]        # closed value sets
interfaces:    [ ... ]        # behaviour contracts (abstract operations)
concepts:      [ ... ]        # L1 classes
roles:         [ ... ]        # composable, cross-cutting facets
individuals:   [ ... ]        # L2 reference instances
```

### 3.1 Identifiers (QNames)

Every element has a stable, immutable, globally unique ID (S6). Three shapes:

| Kind | Shape | Example |
|------|-------|---------|
| Module | `wmoop.<domain>` (lowercase, dotted) | `wmoop.transport` |
| Type (concept, role, datatype, enumeration, interface, individual) | `<module>/<PascalCase>` | `wmoop.transport/Moped` |
| Member (property, relation) | `<module>/<Concept>#<camelCase>` | `wmoop.transport/Vehicle#wheelCount` |

A **value type** (`type:` / `target:` / a param type) is either one of these primitives —
`string`, `boolean`, `integer`, `decimal`, `number`, `date`, `datetime`, `time`, `duration` — or a
type QName. A **cardinality** is `1`, `0..1`, `1..*`, `0..*`, or an explicit range like `2..5`.

### 3.2 `module` — a versioned namespace

```yaml
module:
  id: wmoop.transport            # moduleQName (required)
  version: 0.3.0                 # SemVer (required)
  title: Transport               # (required)
  depends_on:                    # acyclic (S4)
    - { module: wmoop.core,   version: "^1.0.0" }
    - { module: wmoop.nature, version: "^0.5.0" }
```

### 3.3 `datatype` — a validated primitive

```yaml
- id: wmoop.transport/WheelCount
  name: WheelCount
  base: integer                  # a primitive (required)
  definition: A non-negative count of road wheels on a vehicle.   # required
  constraints: { minimum: 0 }    # optional (see §3.10)
  unit: cm3                      # optional
```

### 3.4 `enumeration` — a closed value set

```yaml
- id: wmoop.transport/LicenceCategory
  name: LicenceCategory
  definition: EU driving-licence categories.        # required
  provenance: [ { source: "Directive 2006/126/EC", ref: "Annex, Art. 4", kind: sourced } ]  # required
  values:
    - { id: AM, definition: "Mopeds, light quadricycles (<=45 km/h)" }   # id + definition required
```

### 3.5 `interface` — a behaviour contract

```yaml
- id: wmoop.transport/IDrive
  name: IDrive
  definition: Contract for operating a road vehicle.   # required
  operations:
    - { name: startEngine, returns: boolean }
    - name: driveTo
      params: [ { name: destination, type: wmoop.geography/Place } ]
      returns: void
```

### 3.6 `concept` — an L1 class

```yaml
- id: wmoop.transport/Moped
  name: Moped
  kind: concrete                 # abstract | concrete (required)
  extends: wmoop.transport/Motorcycle   # single, shallow is-a (optional; S1/S2)
  implements: [ wmoop.transport/IDrive ]
  definition: A low-powered motorcycle (EU L1e-B).      # required
  provenance: [ { source: "Regulation (EU) No 168/2013", ref: "Annex I, category L1e-B", kind: sourced } ]  # required
  classified_as:                 # non-inheritance classification (optional; §3.9)
    - { scheme: "NCBI Taxonomy", value: "..." }
  properties:        [ ... ]     # §3.7
  property_overrides:[ ... ]     # §3.8 (LSP-safe narrowing only, S2)
  invariants:        [ ... ]     # boolean constraints over `self`
  relations:         [ ... ]     # §3.11
```

### 3.7 `property` — a typed, defined, sourced attribute

Every property carries its **own** `definition` and `provenance` (S5); a measurable property
carries a `unit` (R5).

```yaml
- id: wmoop.transport/Vehicle#maxSpeed
  name: maxSpeed
  type: wmoop.core/Speed         # a value type (required)
  unit: km/h
  cardinality: "0..1"            # required
  required: false                # optional
  default: true                  # optional
  definition: The maximum design speed on level ground.   # required
  provenance: [ { source: "Original WMOOP definition", kind: definitional } ]  # required
  constraints: { maximum: 400 }  # optional
```

### 3.8 `property_override` — LSP-safe narrowing (S2)

An override MAY only **narrow** an inherited property (tighten a bound, restrict an enum to a
subset). Widening fails validation.

```yaml
property_overrides:
  - property: wmoop.transport/Motorcycle#engineDisplacement
    constraints: { maximum: 50 }        # cm3 — narrows
```

### 3.9 `role` — a composable facet (the cross-domain crux)

A role attaches to a concept by **composition**; it MUST declare `played_by` and MUST NOT appear in
any `extends` (S3 — a role is not a class).

```yaml
- id: wmoop.transport/Driver
  name: Driver
  definition: The role of a licensed person who operates a road vehicle.   # required
  provenance: [ { source: "Directive 2006/126/EC", kind: definitional } ]  # required
  played_by: wmoop.nature/Person         # the concept that can hold the role (required)
  context:   wmoop.transport             # the domain where the role is meaningful
  cardinality_per_player: "0..1"
  capabilities: [ wmoop.transport/IDrive ]   # interfaces unlocked while the role is held
  properties: [ ... ]
  relations:  [ ... ]
```

### 3.10 `individual` — an L2 reference instance

```yaml
- id: wmoop.education/Mathematics
  name: Mathematics
  instance_of: wmoop.education/CurriculumSubject     # required
  definition: The study of quantity, structure, space and change.
  values:                                            # property local-name -> value
    iscedfField: "054 Mathematics and statistics"
  provenance: [ { source: "UNESCO-UIS ISCED-F 2013", ref: "field 054", kind: sourced } ]
```

### 3.11 `relation`, `constraints`, `provenance`, `labels` (shared)

- **`relation`** — a named association: `{ id, name, target, cardinality, rel?, inverse?, definition?, provenance? }`.
  `rel` is `association` (default), `part_of`, `aggregation`, or `composition` — **never**
  `subclass_of` (use `extends`). `inverse` names the other end's member QName.
- **`constraints`** — `minimum`, `maximum`, `exclusiveMinimum`, `exclusiveMaximum`, `multipleOf`,
  `minLength`, `maxLength`, `pattern`, `format`, `enum`.
- **`provenance`** — a non-empty list; each entry needs a `source`, SHOULD set `kind`
  (`sourced` for a fact with a resolvable `ref`, else `definitional`/`convention`), and MAY add
  `note`, `url`, `retrieved`, `doi`, `isbn`, `author`, `title`, `year`, `type`, `locator`.
- **`labels`** — alternate/localized labels grouped by kind, e.g.
  `labels: { alt: [ { lang: ro, value: "diriginte" } ] }`. The canonical `name` stays the stable
  code identifier.

---

## 4. The semantic rules and who enforces them

The grammar (JSON Schema / XSD) checks the **shape** of one file in isolation. The rules below span
files or need resolution, so [`validate_wml.py`](validate_wml.py) enforces them (mirroring the
`wmoopc compile` gates in `docs/03-architecture.md` §2.4):

| Rule | What | Enforced by |
|------|------|-------------|
| Identifier shapes, required slots, kinds, cardinalities, constraint vocab | shape of each node | **grammar** (`wml.schema.json` / `wml.xsd`) |
| **S1** Shallow inheritance | `extends` depth ≤ 6 (warn at 5) | `validate_wml.py` |
| **S2** LSP-safe overrides | an override only narrows; the owner is an ancestor | `validate_wml.py` |
| **S3** Roles are not classes | no role in any `extends`; a role declares `played_by`; agentive-noun lint (opt-in) | grammar (shape) + `validate_wml.py` |
| **S4** Acyclic graphs | `depends_on` and `extends` are DAGs | `validate_wml.py` |
| **S5** Provenance & definitions | present where required; factual nodes sourced (lint) | grammar (presence) + `validate_wml.py` (honesty lint) |
| **S6** Unique, well-formed IDs | no duplicate type/member IDs; a member's QName matches its owner | grammar (shape) + `validate_wml.py` (uniqueness) |
| Referential integrity | every `extends`/`implements`/`type`/`target`/`played_by`/`capability`/`instance_of`/override resolves | `validate_wml.py` |
| Unit presence (R5) | quantity-typed properties carry a unit (lint) | `validate_wml.py` |

References into a module not present in the checkout (e.g. the pending L0 `wmoop.core`, or a domain
not yet authored) are treated as **external/pending** and accepted; only a dangling reference
*within a module that is present* is a hard error.

---

## 5. JSON Schema ↔ XSD mapping

The two schemas are deliberately isomorphic. The XML idiom differs only in naming and nesting:

| WML (YAML/JSON) | WML-in-XML | Notes |
|-----------------|-----------|-------|
| top-level `module:` + sections | one `<module>` document | the projector merges a module's files into one XML |
| `depends_on: [{module, version}]` | `<dependsOn module= version=/>` | repeated |
| `kind: abstract\|concrete` | `kind="abstract"` | attribute |
| `extends`, `type`, `target`, `cardinality` | same-named attributes | QName/cardinality patterns identical |
| `played_by`, `cardinality_per_player`, `instance_of` | `playedBy`, `cardinalityPerPlayer`, `instanceOf` | snake_case → camelCase |
| `implements: [QName]` | `<implements ref=QName/>` | repeated |
| `capabilities: [QName]` | `<capability ref=QName/>` | repeated |
| `classified_as: [{scheme,value}]` | `<classifiedAs scheme= value=/>` | repeated |
| `property_overrides: [{property, constraints}]` | `<propertyOverride property=> <constraints/> </propertyOverride>` | |
| `definition: "..."` | `<definition>...</definition>` | element (multi-line text) |
| `provenance: [ {...} ]` | `<provenance .../>` | repeated; fields are attributes |
| `constraints: { enum: [...] }` | `<constraints><enum>...</enum></constraints>` | numeric bounds are attributes |
| `labels: { alt: [{lang,value}] }` | `<labels><group kind="alt"><label lang="ro">…</label></group></labels>` | |
| individual `values: { prop: v }` | `<value property="prop">v</value>` | repeated |

Target XML namespace: `https://wmoop.org/wml/1`.

---

## 6. Relationship to the rest of the repo

- **`docs/03-architecture.md`** is the prose specification and rationale. This directory is its
  enforceable counterpart: if the two ever disagree, that is a bug to reconcile.
- **`CONTRIBUTING.md` / `AI_CONTRIBUTING.md`** now reference this meta-schema as
  `schema/wml.schema.json`. The *compiled* model export is a separate build artifact published as
  `wm-<ver>.json` (a Release of `wmoop.doc`) — **not** named `wmoop.json`. The single source of truth
  for this and every CI-enforced constant is the **Normative constants** table in `GOVERNANCE.md`.
- **`.claude/skills/wml-contribute`** points authors at the oracle; `validate_wml.py` is a runnable
  stand-in for the `wmoop validate` step until the full `wmoopc` CLI lands in `wmoop.tools`.

> **Drift status.** `CONTRIBUTING.md` §4.1 and its prose now use the canonical grammar and keywords
> (`wmoop.transport/Driver`, `extends`, `played_by:`, list-form `provenance:`), matching the live
> model in `model/**` and this schema. The **one remaining** item is `CONTRIBUTING.md` §7's
> copy-paste templates, which still use the older notation (dot ids, `kindOf`/`appliesTo`,
> `layer:`/`status:`, object-form `provenance`) under an explicit in-section banner; refreshing those
> templates to the live schema is a separate, doc-only follow-up.

---

## 7. Status & stability

The WML grammar is **v0 (experimental)**, in lockstep with the rest of the project — expect
breaking changes. The schema `$id` is `https://wmoop.org/schema/wml.schema.json`; when the grammar
changes in a breaking way, the schema and this document are versioned together and the change is
classified MAJOR/MINOR/PATCH as in `docs/03-architecture.md` §4.3.
