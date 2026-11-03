# Conformance vectors

The language-neutral conformance suite of [docs/03-architecture.md §3](../docs/03-architecture.md#3-c-the-conformance-test-suite).

Each vector is written **once**, here, as data. Every binding runs all of them with a small runner of its own, so the bindings stay
*semantically* identical: same values, same structure, same outcomes, same error codes. A binding pins this repository as
`external/wmoop.doc`, so the vectors it runs always belong to the model its code was generated from.

| Path | What it is |
|---|---|
| `<domain>/<name>.case.yaml` | One case, the source. `<domain>` is the last part of the module the case is about (`transport` for `wmoop.transport`). |
| [`error-codes.yaml`](error-codes.yaml) | The error-code registry (§3.5). A case expects only codes listed there. |
| [`case.schema.json`](case.schema.json) | The JSON Schema of a case file. |
| [`suite.json`](suite.json) | **Generated**: every case in one JSON file, sorted by id. Runners read this file, so they need no YAML parser. Never edit it by hand. |

[`../schema/build_conformance.py`](../schema/build_conformance.py) checks every case and writes `suite.json`; CI runs it with
`--check`. It checks:

- the schema;
- that the id is unique and starts with `conf.<domain>.`;
- that every type, role, interface, property, relation end and enumeration value a case names exists in the model;
- that every name a step uses was bound earlier;
- that every error code is in the registry;
- that every `type_chain` a case expects matches the model's `extends` chain.

```bash
python schema/build_conformance.py           # check the cases and rewrite suite.json
python schema/build_conformance.py --check   # check, and fail if suite.json is stale (CI)
```

## A case

```yaml
# conformance/transport/driver_requires_person.case.yaml
id: conf.transport.driver.attach-requires-person
category: role
description: The Driver role can only be played by a Person.
given:
  - construct: { type: wmoop.transport/Moped, with: { wheelCount: 2, engineDisplacement: { value: 49, unit: cm3 } }, bind: moped }
  - attach_role: { role: wmoop.transport/Driver, to: moped, with: { licenceNumber: L1, licenceCategories: [AM] } }
expect: { outcome: error, error_code: WM-ROLE-PLAYER-MISMATCH }
```

| Field | |
|---|---|
| `id` | Stable and unique: `conf.<domain>.<subject>.<rule>`. Never reused for another rule. |
| `category` | The §3.2 category the case proves: `structural`, `constraint`, `default`, `override`, `role`, `relation`, `enum`, `equivalence` or `behaviour`. |
| `description` | One sentence: the rule, as a reader would state it. |
| `status` | `active` (the default) or `pending`, see below. |
| `reason` | Required for a pending case: what is missing. |
| `given` | The steps, run in order. Optional. |
| `expect` | Either an error outcome or a list of assertions, see below. |

The model's names are used throughout: `wheelCount`, not `WheelCount` or `wheel_count`.

## Steps

Each step is a mapping with one key.

| Step | Does |
|---|---|
| `construct: { type, id?, name?, with?, bind? }` | Builds an instance of a concept or a role. `with` gives model properties (a property left out is not passed at all). For an entity, `id` defaults to `conformance/<bind>` and `name` to `<bind>`, or to the type's name when nothing is bound. |
| `attach_role: { to, role, with?, bind? }` | Builds a role of type `role` and attaches it to `to`. |
| `attach_role: { to, ref }` | Attaches the role object bound as `ref`. |
| `link: { subject, relation, to }` | On a to-many end, adds `to`. On a to-one end, sets it to `to`. Either way the opposite end must follow. |
| `unlink: { subject, relation, from }` | On a to-many end, removes `from`. On a to-one end, clears it if it holds `from`. |
| `assert: { <query>: …, equals: … }` | Checks a query in the middle of the steps. |

Every step must succeed, except the last one of a case that expects an error.

## Queries and assertions

An assertion is a mapping with one query and `equals`, the value the query must return.

| Query | Returns |
|---|---|
| `type_chain: { subject }` | The model types of `subject`, its own type first, then up its `extends` chain. |
| `is_a: { subject, type }` | Whether `subject` is a `type`. |
| `get: { subject, property }` | The value of a property or a relation end, by its model name. |
| `call: { subject, operation, args? }` | The result of an operation (a `behaviour` case). |
| `text: { subject, property? }` | The binding's own string form (`str()`, `ToString()`) of `subject`, or of one of its property values. |
| `text: { value }` | The binding's own string form of a value. |
| `roles: { subject }` | The type ids of the roles `subject` plays, in the order they were attached. |
| `has_role: { subject, role }` | Whether `subject` plays a role of that type. |
| `get_role: { subject, role }` | The role of that type that `subject` plays, or `null`. |
| `role_subject: { role }` | The subject the role object is attached to, or `null`. |
| `same_value: [a, b]` | Whether the binding's own value equality holds between `a` and `b`, with equal hash codes. |
| `has_capability: { subject, capability }` | Whether `subject` currently has the capability, an interface such as `wmoop.transport/IDrive`. |
| `canonical_json: { subject }` | The boundary canonicalizer's JSON for `subject` (§3.1). |

`call` and `get` on members that the model does not declare (hand-written behaviour, kept in step across bindings by ADR 0002) are
allowed only in `behaviour` cases.

## Values

Inputs (`with`, `args`, `same_value`) and expected results (`equals`) use one encoding.

| Value | Written as |
|---|---|
| text, boolean, integer, decimal | a JSON scalar; numbers compare by value, so `49` equals `49.0` |
| absent | `null` |
| an enumeration value | its model id: `AM` |
| a list (`n..*`) | an array, compared in order |
| a date | `{ date: "2026-01-01" }` |
| a quantity | `{ value: 49, unit: cm3 }` |
| an identifier | `{ id: "wmoop.x/y" }` |
| an object a step bound | `{ ref: <name> }` |

Every object a query returns must be one a step bound. A query result can only be compared by name.

## Outcomes

- `expect: { outcome: error, error_code: <code> }`: the last step fails with that code, and every step before it succeeds.
  `violated: <member id>` may say which rule fails; it is informative.
- `expect: [ <assertion>, … ]`: every step succeeds and every assertion holds.

## Pending cases

A case the model specifies but no binding implements yet is `status: pending`, with a `reason`. Runners run it and report it, but a
failure does not fail the run. If a pending case passes, the runner reports that too, so someone can make it active. Once a case is
active, every binding must pass it.

## Writing a runner

A binding's runner reads `external/wmoop.doc/conformance/suite.json` and runs each case on a fresh set of names.

- **Types.** A model type id resolves through the generated metadata (`WM_ID` in Python, `WmId` in C#), not through a naming rule.
- **Members.** A model name matches the binding member that is equal to it, ignoring case and underscores: `wheelCount` matches
  `WheelCount` and `wheel_count`.
- **Errors.** A step fails with the code its error carries (`WmoopError.code`, `IWmoopError.Code`). An error without a code is a
  failure of the binding, not a match.
- **Language guarantees.** Where the language itself rejects something before any code runs, the runner reports the model's code
  for that rule from the binding's own declarations. Examples are a C# `required` member or Python keyword-only argument without a
  default (`WM-REQUIRED-MISSING`), and a C# abstract class (`WM-ABSTRACT-INSTANTIATION`).
- **Output and exit code.** It prints `[PASS]`, `[FAIL]` or `[PENDING]` per case with a summary, and exits non-zero when an active
  case fails.

## Adding a case

1. Write `conformance/<domain>/<name>.case.yaml`, one case per file.
2. Run `python schema/build_conformance.py` and commit the case together with the regenerated `suite.json`.
3. After the merge, every binding receives the case with its next regeneration run. An active case that a binding fails stops that
   run at its tests, so no regeneration pull request opens until the binding passes. If a binding needs work first, add the case as
   pending, and make it active once every binding passes.
