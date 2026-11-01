#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_validate_wml.py - self-test of the WML oracle (validate_wml.py).

A small, valid base model is written to a temporary directory together with one case's
extra files, and the oracle runs over it as a whole model (``--complete``). The base alone
must pass with no warnings; every negative case adds one violation and must fail with the
expected message. A rule the docs call machine-enforced has a case here that proves it
fires - that is what keeps a green run meaningful.

Usage:
    python schema/test_validate_wml.py        # exit 0 = every case behaved as expected
"""
from __future__ import annotations

import contextlib
import io
import shutil
import sys
import tempfile
from pathlib import Path
from textwrap import dedent, indent

sys.dont_write_bytecode = True  # keep schema/ free of __pycache__
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import validate_wml  # noqa: E402

PROV = '[ { source: "Test fixture", kind: definitional } ]'


def concept(cid: str, *, kind: str = "concrete", extends: str | None = None, body: str = "") -> str:
    """One `concepts:` item; ``body`` is YAML nested under it."""
    lines = [f"  - id: {cid}", f"    name: {cid.rsplit('/', 1)[1]}", f"    kind: {kind}"]
    if extends:
        lines.append(f"    extends: {extends}")
    lines += ["    definition: A test concept.", "    provenance: @P@"]
    return "\n".join(lines) + "\n" + (indent(dedent(body).strip("\n"), "    ") + "\n" if body else "")


def header(mid: str, version: str, deps: str) -> str:
    return f"module:\n  id: {mid}\n  version: {version}\n  title: Test\n  depends_on:\n{deps}"


def dep(mid: str, rng: str) -> str:
    return f'    - {{ module: {mid}, version: "{rng}" }}\n'


DEP_CORE = dep("wmoop.core", "^1.0.0")
DEP_ZOO = dep("wmoop.zoo", "^0.2.0")

BASE = {
    "core/core.wml.yaml": "module: { id: wmoop.core, version: 1.0.0, title: Core }\nconcepts:\n"
    + concept("wmoop.core/QuantityKind", body="""
        properties:
          - { id: wmoop.core/QuantityKind#canonicalUnit, name: canonicalUnit, type: string, cardinality: "1", definition: Its canonical unit., provenance: @P@ }
        """)
    + concept("wmoop.core/Unit", body="""
        properties:
          - { id: wmoop.core/Unit#symbol, name: symbol, type: string, cardinality: "1", definition: Its symbol., provenance: @P@ }
          - { id: wmoop.core/Unit#quantityKind, name: quantityKind, type: string, cardinality: "1", definition: What it measures., provenance: @P@ }
        """)
    + dedent("""\
        individuals:
          - { id: wmoop.core/Length, name: Length, instance_of: wmoop.core/QuantityKind, values: { canonicalUnit: wmoop.core/Metre } }
          - { id: wmoop.core/Mass, name: Mass, instance_of: wmoop.core/QuantityKind, values: { canonicalUnit: wmoop.core/Kilogram } }
          - { id: wmoop.core/Speed, name: Speed, instance_of: wmoop.core/QuantityKind, values: { canonicalUnit: wmoop.core/MetrePerSecond } }
          - { id: wmoop.core/Metre, name: m, instance_of: wmoop.core/Unit, values: { symbol: m, quantityKind: wmoop.core/Length } }
          - { id: wmoop.core/Kilogram, name: kg, instance_of: wmoop.core/Unit, values: { symbol: kg, quantityKind: wmoop.core/Mass } }
          - { id: wmoop.core/MetrePerSecond, name: m_per_s, instance_of: wmoop.core/Unit, values: { symbol: m/s, quantityKind: wmoop.core/Speed } }
          - { id: wmoop.core/KilometrePerHour, name: km_per_h, instance_of: wmoop.core/Unit, values: { symbol: km/h, quantityKind: wmoop.core/Speed } }
        """),
    "zoo/zoo.wml.yaml": header("wmoop.zoo", "0.2.0", DEP_CORE) + dedent("""\
        datatypes:
          - { id: wmoop.zoo/LegCount, name: LegCount, base: integer, definition: A leg count., constraints: { minimum: 0 } }
        enumerations:
          - id: wmoop.zoo/Diet
            name: Diet
            definition: What an animal eats.
            provenance: @P@
            values:
              - { id: HERBIVORE, definition: Eats plants. }
              - { id: CARNIVORE, definition: Eats animals. }
        interfaces:
          - id: wmoop.zoo/IFeed
            name: IFeed
            definition: Can be fed.
            operations:
              - { name: feed, returns: void, params: [ { name: food, type: string } ] }
        schemes:
          - { id: wmoop.zoo/FolkTaxonomy, name: FolkTaxonomy, definition: Everyday groupings., provenance: @P@ }
        concepts:
        """)
    + concept("wmoop.zoo/Animal", kind="abstract", body="""
        implements: [ wmoop.zoo/IFeed ]
        properties:
          - { id: wmoop.zoo/Animal#legCount, name: legCount, type: wmoop.zoo/LegCount, cardinality: "0..1", definition: Legs., provenance: @P@ }
          - { id: wmoop.zoo/Animal#mass, name: mass, type: wmoop.core/Mass, unit: kg, cardinality: "1", definition: Body mass., provenance: @P@ }
          - { id: wmoop.zoo/Animal#diet, name: diet, type: wmoop.zoo/Diet, cardinality: "0..1", definition: Diet., provenance: @P@ }
        invariants:
          - { id: positive-mass, expr: "self.mass > 0", message: "Mass is positive." }
        """)
    + concept("wmoop.zoo/Bird", extends="wmoop.zoo/Animal", body="""
        classified_as:
          - { scheme: wmoop.zoo/FolkTaxonomy, value: Flyer, provenance: @P@ }
        property_overrides:
          - { property: wmoop.zoo/Animal#legCount, constraints: { maximum: 2 } }
        """)
    + concept("wmoop.zoo/Person")
    + concept("wmoop.zoo/Enclosure", body="""
        relations:
          - { id: wmoop.zoo/Enclosure#houses, name: houses, target: wmoop.zoo/Animal, cardinality: "0..*", inverse: wmoop.zoo/Animal#housedIn }
        """)
    + dedent("""\
        roles:
          - id: wmoop.zoo/Keeper
            name: Keeper
            definition: Looks after animals.
            provenance: @P@
            played_by: wmoop.zoo/Person
            context: wmoop.zoo
            cardinality_per_player: "0..*"
            relations:
              - { id: wmoop.zoo/Keeper#caresFor, name: caresFor, target: wmoop.zoo/Animal, cardinality: "1..*", inverse: wmoop.zoo/Animal#caredForBy }
        associations:
          - id: wmoop.zoo/Feeding
            name: Feeding
            definition: A keeper feeds an animal.
            provenance: @P@
            participants:
              - { name: keeper, type: wmoop.zoo/Keeper, cardinality: "1" }
              - { name: animal, type: wmoop.zoo/Animal, cardinality: "1" }
            properties:
              - { id: wmoop.zoo/Feeding#portion, name: portion, type: wmoop.core/Mass, unit: kg, cardinality: "0..1", definition: How much food., provenance: @P@ }
        individuals:
          - { id: wmoop.zoo/Tweety, name: Tweety, instance_of: wmoop.zoo/Bird, values: { legCount: 2, mass: 0.03, diet: HERBIVORE } }
        """),
    # a cross-module extends along a declared dependency is allowed
    "park/park.wml.yaml": header("wmoop.park", "0.1.0", DEP_CORE + DEP_ZOO) + "concepts:\n"
    + concept("wmoop.park/Aviary", extends="wmoop.zoo/Enclosure", body="""
        properties:
          - { id: wmoop.park/Aviary#height, name: height, type: wmoop.core/Length, unit: m, cardinality: "0..1", definition: Height., provenance: @P@ }
        """),
}


def bad(body: str = "", deps: str = DEP_CORE + DEP_ZOO) -> dict[str, str]:
    """A module 'wmoop.bad' that depends on core and zoo, holding one case's violation."""
    return {"bad/bad.wml.yaml": header("wmoop.bad", "0.1.0", deps) + dedent(body)}


def prop(cid: str, name: str, spec: str) -> str:
    """A `properties:` body with one property of ``cid``; ``spec`` adds type/unit/cardinality."""
    return (f"properties:\n  - {{ id: {cid}#{name}, name: {name}, {spec}, "
            f"definition: A test property., provenance: @P@ }}\n")


def polly(values: str, cls: str = "wmoop.zoo/Bird") -> dict[str, str]:
    """An individual 'Polly' of ``cls`` with the given flow-style values."""
    return bad(f"individuals:\n  - {{ id: wmoop.bad/Polly, name: Polly, instance_of: {cls}, "
               f"values: {values} }}\n")


def chain(n: int) -> dict[str, str]:
    """A single-inheritance chain D1 <- D2 <- ... <- Dn."""
    return bad("concepts:\n" + "".join(
        concept(f"wmoop.bad/D{i}", extends=f"wmoop.bad/D{i - 1}" if i > 1 else None)
        for i in range(1, n + 1)))


VISIT = """\
associations:
  - id: wmoop.bad/Visit
    name: Visit
    definition: A visit.
    provenance: @P@
    participants:
"""

# (name, extra files, expected substrings, expected exit code, run options)
CASES: list[tuple[str, dict[str, str], tuple[str, ...], int, dict]] = [
    ("the base model is valid", {}, ("OK - 0 errors, 0 warning(s)",), 0, {}),
    ("a partial run accepts declared dependencies outside the targets", {},
     ("(partial run)", "OK - 0 errors"), 0, {"target": "park", "complete": False}),

    # resolution and modules (DoD #3/#4, S6)
    ("a typo in a wmoop.core type",
     bad("concepts:\n" + concept("wmoop.bad/Cage", body=prop(
         "wmoop.bad/Cage", "weight", 'type: wmoop.core/Mas, unit: kg, cardinality: "0..1"'))),
     ("unknown type 'wmoop.core/Mas'",), 1, {}),
    ("a reference into a module that does not exist",
     bad("concepts:\n" + concept("wmoop.bad/Cage", extends="wmoop.zooo/Enclosure")),
     ("module 'wmoop.zooo' does not exist",), 1, {}),
    ("a cross-module extends without depends_on",
     bad("concepts:\n" + concept("wmoop.bad/Cage", extends="wmoop.zoo/Enclosure"), deps=DEP_CORE),
     ("which 'wmoop.bad' does not declare in depends_on",), 1, {}),
    ("a dependency on a module that does not exist",
     bad(deps=DEP_CORE + dep("wmoop.ghost", "^1.0.0")),
     ("depends on 'wmoop.ghost', which does not exist",), 1, {}),
    ("a version pin the module does not satisfy",
     bad(deps=DEP_CORE + dep("wmoop.zoo", "^0.1.0")),
     ("pins 'wmoop.zoo' to '^0.1.0', but 'wmoop.zoo' is at 0.2.0",), 1, {}),
    ("a module without a header",
     {"ghost/ghost.wml.yaml": "concepts:\n" + concept("wmoop.ghost/Thing")},
     ("module 'wmoop.ghost' has declarations but no file carries its `module:` header",), 1, {}),
    ("two modules in one directory",
     {**bad(), "bad/other.wml.yaml": header("wmoop.other", "0.1.0", DEP_CORE)},
     ("directory holds several modules",), 1, {}),
    ("a file that declares another module's ids",
     bad("concepts:\n" + concept("wmoop.zoo/Intruder")),
     ("declares ids of module 'wmoop.zoo'",), 1, {}),
    ("a dangling interface parameter type",
     bad("interfaces:\n  - id: wmoop.bad/IClean\n    name: IClean\n    definition: Can be cleaned.\n"
         "    operations:\n      - { name: clean, returns: void, params: [ { name: tool, type: wmoop.zoo/Ghost } ] }\n"),
     ("unknown type 'wmoop.zoo/Ghost'",), 1, {}),

    # inverses
    ("an inverse that is not a member of the target",
     bad("concepts:\n" + concept("wmoop.bad/Cage", body="""
         relations:
           - { id: wmoop.bad/Cage#holds, name: holds, target: wmoop.zoo/Animal, cardinality: "0..*", inverse: wmoop.bad/Cage#heldBy }
         """)),
     ("must be a member of the relation's target 'wmoop.zoo/Animal'",), 1, {}),
    ("a declared inverse that points elsewhere",
     bad("concepts:\n" + concept("wmoop.bad/Cage", body="""
         relations:
           - { id: wmoop.bad/Cage#holds, name: holds, target: wmoop.bad/Bowl, cardinality: "0..*", inverse: wmoop.bad/Bowl#heldBy }
         """) + concept("wmoop.bad/Bowl", body="""
         relations:
           - { id: wmoop.bad/Bowl#heldBy, name: heldBy, target: wmoop.bad/Lid, cardinality: "0..1" }
         """) + concept("wmoop.bad/Lid")),
     ("'wmoop.bad/Bowl#heldBy' targets 'wmoop.bad/Lid', not 'wmoop.bad/Cage'",), 1, {}),
    ("two relations claiming one inverse end",
     bad("concepts:\n" + concept("wmoop.bad/Cage", body="""
         relations:
           - { id: wmoop.bad/Cage#holds, name: holds, target: wmoop.bad/Bowl, cardinality: "0..*", inverse: wmoop.bad/Bowl#heldBy }
           - { id: wmoop.bad/Cage#keeps, name: keeps, target: wmoop.bad/Bowl, cardinality: "0..*", inverse: wmoop.bad/Bowl#heldBy }
         """) + concept("wmoop.bad/Bowl")),
     ("all name 'wmoop.bad/Bowl#heldBy' as their inverse",), 1, {}),

    # units (R5)
    ("a unit that is not in the catalogue",
     bad("concepts:\n" + concept("wmoop.bad/Cage", body=prop(
         "wmoop.bad/Cage", "width", 'type: wmoop.core/Length, unit: furlong, cardinality: "0..1"'))),
     ("unit 'furlong' is not a Unit of the wmoop.core catalogue",), 1, {}),
    ("a unit of the wrong quantity kind",
     bad("concepts:\n" + concept("wmoop.bad/Cage", body=prop(
         "wmoop.bad/Cage", "weight", 'type: wmoop.core/Mass, unit: km/h, cardinality: "0..1"'))),
     ("unit 'km/h' measures Speed, but the slot is typed Mass",), 1, {}),
    ("a quantity without a unit",
     bad("concepts:\n" + concept("wmoop.bad/Cage", body=prop(
         "wmoop.bad/Cage", "weight", 'type: wmoop.core/Mass, cardinality: "0..1"'))),
     ("is a Mass quantity but names no unit",), 1, {}),
    ("a unit of an unknown quantity kind",
     bad("individuals:\n  - { id: wmoop.bad/Furlong, name: furlong, instance_of: wmoop.core/Unit, "
         "values: { symbol: furlong, quantityKind: wmoop.core/Distance } }\n"),
     ("measures 'wmoop.core/Distance', which is not a QuantityKind",), 1, {}),
    ("two units with one symbol",
     bad("individuals:\n  - { id: wmoop.bad/Meter, name: m2, instance_of: wmoop.core/Unit, "
         "values: { symbol: m, quantityKind: wmoop.core/Length } }\n"),
     ("reuses the symbol 'm'",), 1, {}),

    # individuals (DoD #9)
    ("an individual that sets an unknown property", polly("{ mass: 1, wingspan: 3 }"),
     ("sets 'wingspan', which is not a property",), 1, {}),
    ("an individual value of the wrong type", polly("{ mass: 1, legCount: two }"),
     ("'two' is not a valid LegCount",), 1, {}),
    ("an individual value outside an inherited override", polly("{ mass: 1, legCount: 3 }"),
     ("(set by override in 'wmoop.zoo/Bird')",), 1, {}),
    ("an individual that breaks an invariant", polly("{ mass: -1 }"),
     ("violates invariant 'positive-mass'",), 1, {}),
    ("an individual without a required value", polly("{ legCount: 2 }"),
     ("no value for required property 'wmoop.zoo/Animal#mass'",), 1, {}),
    ("an individual of an abstract concept", polly("{ mass: 1 }", cls="wmoop.zoo/Animal"),
     ("instantiates abstract concept 'wmoop.zoo/Animal'",), 1, {}),
    ("an individual with an unknown enumeration value", polly("{ mass: 1, diet: OMNIVORE }"),
     ("'OMNIVORE' is not a value of wmoop.zoo/Diet",), 1, {}),

    # overrides and inheritance (S1, S2)
    ("an override that widens an ancestor's override",
     bad("concepts:\n" + concept("wmoop.bad/Penguin", extends="wmoop.zoo/Bird", body="""
         property_overrides:
           - { property: wmoop.zoo/Animal#legCount, constraints: { maximum: 4 } }
         """)),
     ("widens the maximum 2 -> 4 (set by override in 'wmoop.zoo/Bird')",), 1, {}),
    ("an override enum outside the inherited bounds",
     bad("datatypes:\n  - { id: wmoop.bad/Size, name: Size, base: integer, definition: A size., "
         "constraints: { minimum: 1 } }\nconcepts:\n"
         + concept("wmoop.bad/Box", body=prop("wmoop.bad/Box", "size", 'type: wmoop.bad/Size, cardinality: "0..1"'))
         + concept("wmoop.bad/Crate", extends="wmoop.bad/Box", body="""
         property_overrides:
           - { property: wmoop.bad/Box#size, constraints: { enum: [0, 1] } }
         """)),
     ("allows enum value(s) [0] outside the bounds (>= 1)",), 1, {}),
    ("a subkind that redeclares an inherited property",
     bad("concepts:\n" + concept("wmoop.bad/Penguin", extends="wmoop.zoo/Bird", body=prop(
         "wmoop.bad/Penguin", "legCount", 'type: string, cardinality: "0..1"'))),
     ("redeclares inherited member 'wmoop.zoo/Animal#legCount'",), 1, {}),
    ("an inheritance depth of 6 is warned", chain(6),
     ("inheritance depth 6 is at or just below the cap 6",), 0, {}),
    ("an inheritance depth of 7 fails", chain(7),
     ("inheritance depth 7 exceeds cap 6",), 1, {}),

    # slot typing
    ("a property typed by a role",
     bad("concepts:\n" + concept("wmoop.bad/Cage", body=prop(
         "wmoop.bad/Cage", "keeper", 'type: wmoop.zoo/Keeper, cardinality: "0..1"'))),
     ("is typed by role 'wmoop.zoo/Keeper'",), 1, {}),
    ("a relation that targets a value",
     bad("concepts:\n" + concept("wmoop.bad/Cage", body="""
         relations:
           - { id: wmoop.bad/Cage#count, name: count, target: integer, cardinality: "0..1" }
         """)),
     ("targets primitive 'integer'",), 1, {}),
    ("a cardinality whose minimum is above its maximum",
     bad("concepts:\n" + concept("wmoop.bad/Cage", body=prop(
         "wmoop.bad/Cage", "bars", 'type: integer, cardinality: "5..2"'))),
     ("cardinality '5..2' has a minimum above its maximum",), 1, {}),

    # schemes and associations (ADR 0001, D9)
    ("a classification under an undeclared scheme",
     bad("concepts:\n" + concept("wmoop.bad/Cage", body="""
         classified_as:
           - { scheme: wmoop.zoo/NoSuchScheme, value: Big }
         """)),
     ("unknown type 'wmoop.zoo/NoSuchScheme'",), 1, {}),
    ("a classification under a free-text scheme",
     bad("concepts:\n" + concept("wmoop.bad/Cage", body="""
         classified_as:
           - { scheme: "Folk taxonomy", value: Big }
         """)),
     ("which is not a scheme id",), 1, {}),
    ("an association participant declared twice",
     bad(VISIT + '      - { name: animal, type: wmoop.zoo/Animal, cardinality: "1" }\n'
                 '      - { name: animal, type: wmoop.zoo/Bird, cardinality: "1" }\n'),
     ("participant 'animal' is declared twice",), 1, {}),
    ("an association participant that is a value",
     bad(VISIT + '      - { name: animal, type: wmoop.zoo/Animal, cardinality: "1" }\n'
                 '      - { name: minutes, type: integer, cardinality: "1" }\n'),
     ("participant 'minutes' is a value (integer)",), 1, {}),
    ("an association whose id is a concept's id",
     bad("concepts:\n" + concept("wmoop.bad/Visit") + VISIT
         + '      - { name: animal, type: wmoop.zoo/Animal, cardinality: "1" }\n'
           '      - { name: keeper, type: wmoop.zoo/Keeper, cardinality: "1" }\n'),
     ("duplicate type id 'wmoop.bad/Visit'",), 1, {}),

    # robustness
    ("a multi-player role is reported, not a crash",
     bad("roles:\n  - id: wmoop.bad/Visitor\n    name: Visitor\n    definition: Visits.\n"
         "    provenance: @P@\n    played_by: [ wmoop.zoo/Person, wmoop.zoo/Bird ]\n"),
     ("[grammar]", "played_by must be a single concept QName"), 1, {}),
]


def write_model(root: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text.replace("@P@", PROV), encoding="utf-8")


def invoke(argv: list[str]) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        try:
            code = validate_wml.main(argv)
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 2
    return code, out.getvalue()


def run_case(files: dict[str, str], target: str = "", complete: bool = True) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "model"
        write_model(root, {**BASE, **files})
        argv = ["--no-xsd", "--no-parity", str(root / target if target else root)]
        return invoke((["--complete"] if complete else []) + argv)


def run_under_underscore_dir() -> tuple[int, str]:
    """A checkout that itself lives under a `_...` directory must still find its files."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "_work" / "model"
        write_model(root, BASE)
        shutil.copytree(root, Path(tmp) / "_work" / "copy")  # an unrelated sibling is ignored
        return invoke(["--complete", "--no-xsd", "--no-parity", str(root)])


def main() -> int:
    try:
        import jsonschema  # noqa: F401 - the grammar gate is part of what is tested
    except ImportError:
        print("error: the self-test needs jsonschema: "
              "python -m pip install -r schema/requirements.txt", file=sys.stderr)
        return 2

    results = [(name, run_case(files, **opts), expected, code)
               for name, files, expected, code, opts in CASES]
    results.append(("a checkout under a `_` directory still validates",
                    run_under_underscore_dir(), ("3 module(s)", "OK - 0 errors"), 0))
    failures = 0
    for name, (got, output), expected, code in results:
        problems = [] if got == code else [f"exit code {got}, expected {code}"]
        problems += [f"missing {text!r}" for text in expected if text not in output]
        if "internal error" in output:
            problems.append("the validator crashed")
        print(f"  {'PASS' if not problems else 'FAIL'}  {name}")
        if problems:
            failures += 1
            print("        " + "; ".join(problems))
            print(indent(output.rstrip(), "        | "))
    print(f"\n{len(results) - failures}/{len(results)} validator self-test case(s) passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
