#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build_conformance.py - check the conformance vectors and write the bundle the bindings read.

The cases under ``conformance/<domain>/*.case.yaml`` are the language-neutral conformance suite of
docs/03-architecture.md Sec 3; conformance/README.md specifies their format. This script:

  1. reads each case with a JSON-only YAML loader: a duplicated key is an error, dates stay text,
     and only ``true``/``false`` are booleans, so every binding sees the same values;
  2. validates it against ``conformance/case.schema.json``;
  3. checks it against the model (the self-check of Sec 2.4, step 5):
       - a unique id that starts with ``conf.<domain>.``, in ``conformance/<domain>/``;
       - existing types, roles, interfaces, properties, relation ends and enumeration values;
       - names bound before they are used, and never bound twice;
       - error codes listed in ``conformance/error-codes.yaml``;
       - an expected ``type_chain`` equal to the model's ``extends`` chain;
  4. writes ``conformance/suite.json``: every case, sorted by id, for the bindings' runners.

Exit code 0 = every case is valid (and, with ``--check``, suite.json is current); 1 otherwise.

Usage:
    python schema/build_conformance.py           # check, then (re)write conformance/suite.json
    python schema/build_conformance.py --check   # check, and fail if suite.json is stale (CI)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # keep schema/ free of __pycache__
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import validate_wml as wml  # noqa: E402 - the model index the cases are checked against

REPO = HERE.parent
CONFORMANCE = REPO / "conformance"
CASE_SCHEMA = CONFORMANCE / "case.schema.json"
ERROR_CODES = CONFORMANCE / "error-codes.yaml"
SUITE = CONFORMANCE / "suite.json"
FORMAT = 1

# What every entity has besides its model properties (the kernel's identity and name).
ENTITY_MEMBERS = {"id", "name"}
QUERIES = ("type_chain", "is_a", "get", "call", "text", "roles", "has_role", "get_role",
           "role_subject", "same_value", "has_capability", "canonical_json")


# --------------------------------------------------------------------------- #
# Reading                                                                      #
# --------------------------------------------------------------------------- #
def json_only_loader():
    """A YAML loader that reads only what JSON can say. YAML 1.1 turns ``2026-01-01`` into a date
    and ``no``/``on`` into booleans, and silently keeps the last of two equal keys; a vector must
    mean the same thing in every binding, so none of that is allowed here."""
    try:
        import yaml
    except ImportError:
        wml._die("PyYAML is required: pip install -r schema/requirements.txt")
    bool_tag, timestamp_tag = "tag:yaml.org,2002:bool", "tag:yaml.org,2002:timestamp"

    class Loader(yaml.SafeLoader):
        pass

    Loader.yaml_implicit_resolvers = {
        first: [(tag, rx) for tag, rx in resolvers if tag not in (bool_tag, timestamp_tag)]
        for first, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
    }
    Loader.add_implicit_resolver(bool_tag, re.compile(r"^(?:true|false)$"), list("tf"))

    def mapping(loader, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = loader.construct_object(key_node, deep=True)
            if key in seen:
                raise yaml.constructor.ConstructorError(
                    None, None, f"duplicate key {key!r}", key_node.start_mark)
            seen.add(key)
        return loader.construct_mapping(node, deep=deep)

    Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    return Loader


def load_cases(report: wml.Report, root: Path = CONFORMANCE) -> list[tuple[Path, object]]:
    import yaml

    loader = json_only_loader()
    cases = []
    for path in sorted(root.rglob("*.case.yaml")):
        try:
            with path.open("r", encoding="utf-8") as fh:
                cases.append((path, yaml.load(fh, Loader=loader)))  # noqa: S506 - a SafeLoader subclass
        except yaml.YAMLError as exc:
            report.error(wml.rel_path(path), f"YAML error: {exc}")
    return cases


def load_codes(report: wml.Report) -> set[str]:
    import yaml

    rel = wml.rel_path(ERROR_CODES)
    with ERROR_CODES.open("r", encoding="utf-8") as fh:
        data = yaml.load(fh, Loader=json_only_loader())  # noqa: S506 - a SafeLoader subclass
    codes: set[str] = set()
    for entry in wml._dicts((data or {}).get("codes")):
        code = entry.get("code")
        if not isinstance(code, str) or not re.fullmatch(r"WM-[A-Z0-9]+(-[A-Z0-9]+)*", code):
            report.error(rel, f"malformed code {code!r}")
        elif code in codes:
            report.error(rel, f"duplicate code {code}")
        elif not isinstance(entry.get("meaning"), str) or not entry["meaning"].strip():
            report.error(rel, f"{code} has no meaning")
        else:
            codes.add(code)
    return codes


def load_registry() -> wml.Registry:
    """The model index of validate_wml.py. The model's own errors are that gate's job, not ours."""
    files = wml.collect_files([])
    docs = {f: wml.load_yaml(f) for f in files}
    return wml.build_registry({p: d for p, d in docs.items() if d is not None}, wml.Report())


# --------------------------------------------------------------------------- #
# Schema                                                                       #
# --------------------------------------------------------------------------- #
def check_schema(cases: list[tuple[Path, object]], report: wml.Report) -> list[tuple[Path, dict]]:
    """The cases that match case.schema.json; every mismatch is reported."""
    try:
        from jsonschema import Draft202012Validator
        from jsonschema.exceptions import best_match
    except ImportError:
        wml._die("jsonschema is required: pip install -r schema/requirements.txt")
    schema = json.loads(CASE_SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    valid = []
    for path, data in cases:
        errors = list(validator.iter_errors(data))
        for err in errors:
            err = best_match([err])
            where = "/".join(str(p) for p in err.absolute_path) or "(case)"
            report.error(wml.rel_path(path), f"{where}: {err.message}")
        if not errors:
            valid.append((path, data))
    return valid


# --------------------------------------------------------------------------- #
# The model, as a case sees it                                                 #
# --------------------------------------------------------------------------- #
def kind_of(reg: wml.Registry, tid: str) -> str | None:
    return reg.types.get(tid, {}).get("kind")


def a_(kind: str | None) -> str:
    """``kind`` with its article: "a role", "an enumeration"."""
    return f"{'an' if (kind or 'x')[0] in 'aeiou' else 'a'} {kind}"


def node_of(reg: wml.Registry, tid: str) -> dict:
    return reg.types.get(tid, {}).get("node", {})


def type_chain(reg: wml.Registry, tid: str) -> list[str]:
    """``tid`` and the concepts it extends, its own type first."""
    return [tid] + (wml.ancestors(reg, tid) if kind_of(reg, tid) == "concept" else [])


def _member_name(m: dict) -> str:
    return m.get("name") or wml.local_name(m.get("id", ""))


def properties(reg: wml.Registry, tid: str) -> dict[str, dict]:
    found: dict[str, dict] = {}
    for t in type_chain(reg, tid):
        for p in wml._dicts(node_of(reg, t).get("properties")):
            found.setdefault(_member_name(p), p)
    return found


def relation_ends(reg: wml.Registry, tid: str) -> set[str]:
    """The relation ends ``tid`` has: its own and inherited relations, and every declared inverse
    end that sits on it or on a concept it extends."""
    lineage = set(type_chain(reg, tid))
    ends = {_member_name(r) for t in lineage for r in wml._dicts(node_of(reg, t).get("relations"))}
    for member in reg.members.values():
        inverse = member["node"].get("inverse") if member["kind"] == "relation" else None
        if isinstance(inverse, str) and wml.type_of_member(inverse) in lineage:
            ends.add(wml.local_name(inverse))
    return ends


def enum_values(reg: wml.Registry, prop: dict) -> set[str] | None:
    """The value ids of an enumeration-typed property, or None for any other type."""
    ptype = prop.get("type")
    if not isinstance(ptype, str) or kind_of(reg, ptype) != "enumeration":
        return None
    return {v.get("id") for v in wml._dicts(node_of(reg, ptype).get("values"))}


# --------------------------------------------------------------------------- #
# One case                                                                     #
# --------------------------------------------------------------------------- #
class CaseCheck:
    """Walks one schema-valid case, tracking the model type of every name a step binds."""

    def __init__(self, reg: wml.Registry, codes: set[str], report: wml.Report, path: Path, case: dict):
        self.reg, self.codes, self.report, self.case = reg, codes, report, case
        self.where = wml.rel_path(path)
        self.behaviour = case["category"] == "behaviour"
        self.bound: dict[str, str] = {}  # name -> type id

    def error(self, msg: str) -> None:
        self.report.error(self.where, msg)

    # -- names -----------------------------------------------------------------
    def bind(self, name: str | None, tid: str, step: str) -> None:
        if name is None:
            return
        if name in self.bound:
            self.error(f"{step}: '{name}' is bound twice")
        self.bound[name] = tid

    def use(self, name: str, step: str, kind: str | None = None) -> str | None:
        """The type bound to ``name``; reports a name not bound yet or bound to the wrong kind."""
        tid = self.bound.get(name)
        if tid is None:
            self.error(f"{step}: '{name}' is not bound by an earlier step")
            return None
        if kind and kind_of(self.reg, tid) != kind:
            self.error(f"{step}: '{name}' is {a_(kind_of(self.reg, tid))}, not {a_(kind)}")
            return None
        return tid

    def refs(self, value, step: str) -> None:
        if isinstance(value, list):
            for item in value:
                self.refs(item, step)
        elif isinstance(value, dict) and "ref" in value:
            self.use(value["ref"], step)

    # -- model elements ----------------------------------------------------------
    def type_id(self, tid: str, step: str, *kinds: str) -> bool:
        kind = kind_of(self.reg, tid)
        if kind is None:
            self.error(f"{step}: no type '{tid}' in the model")
        elif kind not in kinds:
            self.error(f"{step}: '{tid}' is {a_(kind)}, not {a_(' or '.join(kinds))}")
        return kind in kinds

    def enum_value(self, tid: str, prop: dict, value, step: str) -> None:
        allowed = enum_values(self.reg, prop)
        if allowed is None:
            return
        for item in value if isinstance(value, list) else [value]:
            if isinstance(item, str) and item not in allowed:
                self.error(f"{step}: '{item}' is not a value of {prop.get('type')} "
                           f"({tid}#{_member_name(prop)})")

    def with_(self, tid: str, given: dict | None, step: str) -> None:
        props = properties(self.reg, tid)
        for name, value in (given or {}).items():
            prop = props.get(name)
            if prop is None:
                self.error(f"{step}: {tid} has no property '{name}'")
            else:
                self.enum_value(tid, prop, value, step)
            self.refs(value, step)

    def member(self, tid: str, name: str, step: str) -> dict | None:
        """The property a query reads, if the model declares it; reports an unknown member outside
        behaviour cases, where hand-written members are allowed."""
        prop = properties(self.reg, tid).get(name)
        known = prop is not None or name in relation_ends(self.reg, tid) or (
            kind_of(self.reg, tid) == "concept" and name in ENTITY_MEMBERS)
        if not known and not self.behaviour:
            self.error(f"{step}: {tid} has no property or relation end '{name}' "
                       "(hand-written members belong in a behaviour case)")
        return prop

    # -- steps -------------------------------------------------------------------
    def run(self) -> None:
        for i, step in enumerate(self.case.get("given") or [], 1):
            (key, args), = step.items()
            label = f"given[{i}].{key}"
            getattr(self, f"step_{key}")(args, label)
        expect = self.case["expect"]
        if isinstance(expect, dict):
            if not self.case.get("given"):
                self.error("expect: an error outcome needs a step that fails")
            if expect["error_code"] not in self.codes:
                self.error(f"expect: {expect['error_code']} is not in conformance/error-codes.yaml")
            if "violated" in expect and expect["violated"] not in self.reg.members:
                self.error(f"expect: violated names no member '{expect['violated']}'")
        else:
            for i, assertion in enumerate(expect, 1):
                self.assertion(assertion, f"expect[{i}]")

    def step_construct(self, a: dict, label: str) -> None:
        tid = a["type"]
        if not self.type_id(tid, label, "concept", "role"):
            return
        if kind_of(self.reg, tid) == "role" and ("id" in a or "name" in a):
            self.error(f"{label}: a role has no id or name")
        self.with_(tid, a.get("with"), label)
        self.bind(a.get("bind"), tid, label)

    def step_attach_role(self, a: dict, label: str) -> None:
        self.use(a["to"], label, "concept")
        if "ref" in a:
            self.use(a["ref"], label, "role")
            return
        if self.type_id(a["role"], label, "role"):
            self.with_(a["role"], a.get("with"), label)
            self.bind(a.get("bind"), a["role"], label)

    def _relation(self, a: dict, other: str, label: str) -> None:
        tid = self.use(a["subject"], label)
        self.use(a[other], label)
        if tid and a["relation"] not in relation_ends(self.reg, tid):
            self.error(f"{label}: {tid} has no relation end '{a['relation']}'")

    def step_link(self, a: dict, label: str) -> None:
        self._relation(a, "to", label)

    def step_unlink(self, a: dict, label: str) -> None:
        self._relation(a, "from", label)

    def step_assert(self, a: dict, label: str) -> None:
        self.assertion(a, label)

    # -- assertions --------------------------------------------------------------
    def assertion(self, a: dict, label: str) -> None:
        query = next(k for k in a if k != "equals")
        q, equals, label = a[query], a["equals"], f"{label}.{query}"
        self.refs(equals, label)
        if query == "same_value":
            self.refs(q, label)
            return
        if query == "role_subject":
            self.use(q["role"], label, "role")
            return
        if query == "text" and "value" in q:
            self.refs(q["value"], label)
            return
        tid = self.use(q["subject"], label)
        if tid is None:
            return
        if query == "type_chain" and isinstance(equals, list) and equals != type_chain(self.reg, tid):
            self.error(f"{label}: the model's chain for {tid} is {type_chain(self.reg, tid)}")
        elif query == "is_a":
            self.type_id(q["type"], label, "concept")
        elif query in ("get", "text") and "property" in q:
            prop = self.member(tid, q["property"], label)
            if prop is not None and query == "get":
                self.enum_value(tid, prop, equals, label)
        elif query in ("has_role", "get_role"):
            self.type_id(q["role"], label, "role")
        elif query == "roles" and isinstance(equals, list):
            for rid in equals:
                self.type_id(rid, label, "role")
        elif query == "has_capability":
            self.type_id(q["capability"], label, "interface")
        elif query == "call":
            if not self.behaviour:
                self.error(f"{label}: call is for behaviour cases")
            self.refs(q.get("args"), label)


def check_cases(cases: list[tuple[Path, dict]], reg: wml.Registry, codes: set[str],
                report: wml.Report, root: Path = CONFORMANCE) -> None:
    ids: dict[str, str] = {}
    for path, case in cases:
        where, cid = wml.rel_path(path), case["id"]
        if cid in ids:
            report.error(where, f"duplicate id '{cid}' (also in {ids[cid]})")
        ids.setdefault(cid, where)
        domain = path.parent.name
        if path.parent.parent.resolve() != root.resolve():
            report.error(where, "a case lives directly in conformance/<domain>/")
        elif f"wmoop.{domain}" not in reg.modules:
            report.error(where, f"conformance/{domain}/ names no model module wmoop.{domain}")
        elif not cid.startswith(f"conf.{domain}."):
            report.error(where, f"the id of a case in conformance/{domain}/ starts with 'conf.{domain}.'")
        CaseCheck(reg, codes, report, path, case).run()


# --------------------------------------------------------------------------- #
# The bundle                                                                   #
# --------------------------------------------------------------------------- #
def bundle(cases: list[tuple[Path, dict]]) -> str:
    """suite.json: deterministic, LF, every case sorted by id, each with the file it came from."""
    entries = [{"file": wml.rel_path(path), **case} for path, case in sorted(cases, key=lambda c: c[1]["id"])]
    doc = {
        "format": FORMAT,
        "generated_by": "schema/build_conformance.py, from conformance/<domain>/*.case.yaml. Do not edit.",
        "cases": entries,
    }
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Check the conformance vectors and write conformance/suite.json.")
    ap.add_argument("--check", action="store_true", help="write nothing; fail if suite.json is stale")
    args = ap.parse_args(argv)

    report = wml.Report()
    loaded = load_cases(report)
    cases = check_schema(loaded, report)
    check_cases(cases, load_registry(), load_codes(report), report)
    pending = sum(1 for _, c in cases if c.get("status") == "pending")
    summary = f"{len(loaded)} case(s): {len(loaded) - pending} active, {pending} pending"
    for e in report.errors:
        print(f"  ERROR {e}")
    if report.errors:
        print(f"\nFAILED - {len(report.errors)} error(s) in {summary}")
        return 1

    text = bundle(cases)
    current = SUITE.read_text(encoding="utf-8").replace("\r\n", "\n") if SUITE.is_file() else None
    if current == text:
        print(f"OK - {summary}; conformance/suite.json is current")
        return 0
    if args.check:
        print(f"FAILED - conformance/suite.json is stale ({summary}): "
              "run python schema/build_conformance.py and commit the result")
        return 1
    SUITE.write_text(text, encoding="utf-8", newline="\n")
    print(f"OK - {summary}; wrote conformance/suite.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
