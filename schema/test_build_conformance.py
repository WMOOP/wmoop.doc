#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_build_conformance.py - self-test of the conformance checker (build_conformance.py).

The real cases must pass. Then each negative case takes one valid case, breaks one rule, and
must fail with the expected message, so every check the README lists is proven to fire. The
cases are checked against the real model, as in CI.

Usage:
    python schema/test_build_conformance.py   # exit 0 = every case behaved as expected
"""
from __future__ import annotations

import copy
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True  # keep schema/ free of __pycache__
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_conformance as bc  # noqa: E402
import validate_wml as wml  # noqa: E402

MOPED = {"type": "wmoop.transport/Moped", "bind": "moped",
         "with": {"wheelCount": 2, "engineDisplacement": {"value": 49, "unit": "cm3"}}}
BASE = {
    "id": "conf.transport.test.base",
    "category": "relation",
    "description": "A valid case each negative case breaks once.",
    "given": [
        {"construct": {"type": "wmoop.nature/Person", "with": {"fullName": "Ada"}, "bind": "ada"}},
        {"attach_role": {"role": "wmoop.transport/Owner", "to": "ada", "bind": "owner"}},
        {"construct": MOPED},
        {"link": {"subject": "owner", "relation": "owns", "to": "moped"}},
    ],
    "expect": [
        {"get": {"subject": "moped", "property": "ownedBy"}, "equals": [{"ref": "owner"}]},
        {"type_chain": {"subject": "moped"}, "equals": [
            "wmoop.transport/Moped", "wmoop.transport/Motorcycle", "wmoop.transport/RoadVehicle",
            "wmoop.transport/Vehicle"]},
    ],
}


def case(change=None, domain: str = "transport", name: str = "base"):
    """A copy of BASE, changed by ``change(c)``, at conformance/<domain>/<name>.case.yaml."""
    c = copy.deepcopy(BASE)
    if change:
        change(c)
    return bc.CONFORMANCE / domain / f"{name}.case.yaml", c


def step(i: int, key: str, **fields):
    def change(c):
        c["given"][i][key].update(fields)
    return change


def run(cases) -> list[str]:
    report = wml.Report()
    valid = bc.check_schema(cases, report)
    bc.check_cases(valid, REG, CODES, report)
    return report.errors


def pending_without_reason(c):
    c["status"] = "pending"


def error_outcome(code: str):
    def change(c):
        c["expect"] = {"outcome": "error", "error_code": code}
    return change


def call_outside_behaviour(c):
    c["expect"][0] = {"call": {"subject": "moped", "operation": "describe"}, "equals": "x"}


def hand_written_get(c):
    c["expect"][0] = {"get": {"subject": "moped", "property": "classification"}, "equals": "moped"}


def bad_category_value(c):
    c["given"].append({"construct": {"type": "wmoop.transport/Driver", "with": {
        "licenceNumber": "L1", "licenceCategories": ["AM", "Z"]}}})


NEGATIVE = [
    ("schema: an unknown step", lambda c: c["given"].append({"destroy": {"subject": "moped"}}),
     "Additional properties are not allowed"),
    ("schema: a pending case needs a reason", pending_without_reason, "'reason' is a required property"),
    ("schema: a reason without pending", lambda c: c.update(reason="why"), "should not be valid"),
    ("schema: an assertion has one query", lambda c: c["expect"][0].update(roles={"subject": "ada"}),
     "has too many properties"),
    ("model: an unknown type", step(2, "construct", type="wmoop.transport/Hovercraft"),
     "no type 'wmoop.transport/Hovercraft'"),
    ("model: a construct of an enumeration", step(2, "construct", type="wmoop.transport/LicenceCategory"),
     "is an enumeration, not a concept or role"),
    ("model: an unknown property", step(2, "construct", **{"with": {"wheelCount": 2, "colour": "red"}}),
     "has no property 'colour'"),
    ("model: a value outside the enumeration", bad_category_value, "'Z' is not a value of"),
    ("model: an unknown relation end", step(3, "link", relation="drives"), "has no relation end 'drives'"),
    ("model: a role attached to a role", lambda c: c["given"].append(
        {"attach_role": {"role": "wmoop.transport/Owner", "to": "owner"}}), "'owner' is a role, not a concept"),
    ("model: a role with a name", lambda c: c["given"].append(
        {"construct": {"type": "wmoop.transport/Owner", "name": "x"}}), "a role has no id or name"),
    ("names: used before it is bound", step(3, "link", to="car"), "'car' is not bound"),
    ("names: bound twice", step(2, "construct", bind="ada"), "'ada' is bound twice"),
    ("codes: an unknown error code", error_outcome("WM-NOPE"), "WM-NOPE is not in conformance/error-codes.yaml"),
    ("chain: type_chain differs from the model", lambda c: c["expect"][1]["equals"].pop(2),
     "the model's chain for wmoop.transport/Moped is"),
    ("behaviour: call outside a behaviour case", call_outside_behaviour, "call is for behaviour cases"),
    ("behaviour: a hand-written member outside a behaviour case", hand_written_get,
     "has no property or relation end 'classification'"),
]


def main() -> int:
    global REG, CODES
    report = wml.Report()
    REG, CODES = bc.load_registry(), bc.load_codes(report)
    results: list[tuple[str, list[str]]] = []

    real = bc.load_cases(report)
    real_errors = run(real) + report.errors
    results.append((f"the {len(real)} real cases are valid", real_errors))
    results.append(("the base case is valid", run([case()])))

    for name, change, expected in NEGATIVE:
        errors = run([case(change)])
        problems = [] if any(expected in e for e in errors) else [f"no error mentions {expected!r}: {errors}"]
        results.append((name, problems))

    errors = run([case(), case(name="copy")])
    results.append(("ids: a duplicate id", [] if any("duplicate id" in e for e in errors) else [str(errors)]))
    errors = run([case(domain="nature")])
    results.append(("ids: the id names its directory",
                    [] if any("starts with 'conf.nature.'" in e for e in errors) else [str(errors)]))
    errors = run([case(domain="galaxy", name="x")])
    results.append(("ids: the directory names a module",
                    [] if any("no model module wmoop.galaxy" in e for e in errors) else [str(errors)]))

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "transport").mkdir()
        (root / "transport" / "a.case.yaml").write_text(
            "id: conf.transport.a.b\nid: conf.transport.a.c\n", encoding="utf-8")
        (root / "transport" / "b.case.yaml").write_text(
            "when: 2026-01-01\nflag: no\non: true\n", encoding="utf-8")
        loaded_report = wml.Report()
        loaded = dict(bc.load_cases(loaded_report, root))
        dup = [] if any("duplicate key 'id'" in e for e in loaded_report.errors) else [str(loaded_report.errors)]
        results.append(("yaml: a duplicate key is an error", dup))
        values = loaded.get(root / "transport" / "b.case.yaml")
        want = {"when": "2026-01-01", "flag": "no", "on": True}
        results.append(("yaml: dates stay text and only true/false are booleans",
                         [] if values == want else [f"read {values!r}, expected {want!r}"]))

    first = case(lambda c: c.update(id="conf.transport.test.a"), name="a")
    a, b = bc.bundle([case(), first]), bc.bundle([first, case()])
    results.append(("bundle: sorted by id, the same for any input order", [] if a == b else ["bundles differ"]))

    failures = 0
    for name, problems in results:
        print(f"  {'PASS' if not problems else 'FAIL'}  {name}")
        for p in problems:
            failures += 1
            print(f"        {p}")
    print(f"\n{len(results) - sum(1 for _, p in results if p)}/{len(results)} conformance self-test case(s) passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
