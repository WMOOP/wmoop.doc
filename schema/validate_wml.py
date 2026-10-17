#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
validate_wml.py - the WML oracle.

Realises gate 1-3 of the ``wmoopc compile`` pipeline (docs/03-architecture.md Sec 2.4)
against the canonical model in ``model/**``:

  1. Grammar     - every ``*.wml.yaml`` validates against ``schema/wml.schema.json``
                   (JSON Schema 2020-12). This is the context-free shape (R1-R12, S5/S6 shapes).
  2. Resolution  - IDs and ``depends_on`` resolve; the module graph and the ``extends``
                   graph are acyclic (S4).
  3. Semantics   - cross-file rules a grammar cannot express:
                     S1 shallow inheritance (depth <= MAX_DEPTH),
                     S2 LSP-safe overrides (narrow only; no widening),
                     S3 roles are not classes (no role in any ``extends``; agentive-noun lint),
                     S5 provenance honesty (factual nodes sourced) [lint],
                     S6 unique, immutable IDs,
                     unit presence on quantity-typed properties [lint],
                     referential integrity of every reference.

Optionally (``--xsd`` / on by default when available) validates the WML-in-XML
projections under ``schema/examples/*.wml.xml`` against ``schema/wml.xsd``.

Exit code 0 = all gates green; 1 = at least one ERROR (warnings alone do not fail
unless ``--strict``). This is the machine-checkable Definition of Done (Invariant 6).

Usage:
    python schema/validate_wml.py                 # validate model/** + any XML examples
    python schema/validate_wml.py model/transport # validate a subtree
    python schema/validate_wml.py --strict        # treat warnings as errors
    python schema/validate_wml.py --no-xsd        # skip the XSD projection check
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SCHEMA_FILE = HERE / "wml.schema.json"
XSD_FILE = HERE / "wml.xsd"
EXAMPLES_DIR = HERE / "examples"

# Inheritance depth cap (S1). Configurable per org; warned at MAX_DEPTH-1, failed above.
MAX_DEPTH = 6

# Opt-in S3 lint that flags agentive-noun concepts (set by --lint-agentive).
LINT_AGENTIVE = False

# L0 modules that are canonical but whose module file is still pending (taxonomy: core).
# References into them resolve as "external", not as dangling.
EXTERNAL_MODULES = {"wmoop.core"}

# Type names that denote a measured Quantity (used only for the unit-presence lint).
QUANTITY_HINTS = {
    "Speed", "Velocity", "Volume", "Mass", "Length", "Distance", "Height", "Width",
    "Area", "Temperature", "Duration", "Time", "Energy", "Power", "Force", "Pressure",
    "Frequency", "Angle", "Density", "Weight", "Acceleration",
}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"{where}: {msg}")


def _die(msg: str) -> "None":
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(2)


def rel_path(path: Path) -> str:
    """A display path relative to the repo when possible, else the raw path."""
    try:
        return path.resolve().relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


def load_yaml(path: Path):
    try:
        import yaml
    except ImportError:
        _die("PyYAML is required: pip install pyyaml")
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


# --------------------------------------------------------------------------- #
# ID helpers                                                                   #
# --------------------------------------------------------------------------- #
def module_of(qname: str) -> str:
    """wmoop.transport/Moped -> wmoop.transport ; wmoop.transport/Vehicle#wheelCount -> wmoop.transport"""
    return qname.split("/", 1)[0]


def type_of_member(member_qname: str) -> str:
    """wmoop.transport/Vehicle#wheelCount -> wmoop.transport/Vehicle"""
    return member_qname.split("#", 1)[0]


PRIMITIVES = {"string", "boolean", "integer", "decimal", "number", "date", "datetime", "time", "duration", "void"}


# --------------------------------------------------------------------------- #
# Gate 1 - grammar (JSON Schema)                                               #
# --------------------------------------------------------------------------- #
def validate_grammar(docs: dict[Path, object], report: Report) -> None:
    try:
        import jsonschema
    except ImportError:
        report.warn("grammar", "jsonschema not installed - grammar gate SKIPPED "
                               "(pip install jsonschema). Semantic gates still run.")
        return
    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    validator_cls = jsonschema.validators.validator_for(schema)
    validator_cls.check_schema(schema)
    validator = validator_cls(schema)
    for path, data in docs.items():
        rel = rel_path(path)
        for err in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
            loc = "/".join(str(p) for p in err.absolute_path) or "(root)"
            report.error(rel, f"[grammar] at {loc}: {err.message}")


# --------------------------------------------------------------------------- #
# Build a cross-file registry                                                  #
# --------------------------------------------------------------------------- #
class Registry:
    def __init__(self) -> None:
        self.modules: dict[str, dict] = {}           # module id -> header
        self.module_file: dict[str, str] = {}        # module id -> file that holds the header
        self.types: dict[str, dict] = {}             # type QName -> {kind, file, node}
        self.members: dict[str, dict] = {}           # member QName -> {kind, owner, file, node}
        self.id_files: dict[str, list[str]] = {}     # any id -> [files it appears in]  (S6 dup check)

    def note_id(self, ident: str, rel: str) -> None:
        self.id_files.setdefault(ident, []).append(rel)


def build_registry(docs: dict[Path, object], report: Report) -> Registry:
    reg = Registry()
    for path, data in docs.items():
        if not isinstance(data, dict):
            continue
        rel = rel_path(path)

        header = data.get("module")
        if isinstance(header, dict) and "id" in header:
            mid = header["id"]
            if mid in reg.modules:
                report.error(rel, f"module '{mid}' already has a header in "
                                  f"{reg.module_file[mid]} (a module has exactly one header file)")
            else:
                reg.modules[mid] = header
                reg.module_file[mid] = rel

        def add_type(node: dict, kind: str) -> None:
            tid = node.get("id")
            if not tid:
                return
            reg.note_id(tid, rel)
            if tid in reg.types:
                report.error(rel, f"duplicate type id '{tid}' "
                                  f"(also in {reg.types[tid]['file']}) [S6]")
            reg.types[tid] = {"kind": kind, "file": rel, "node": node}

        def add_member(node: dict, kind: str, owner: str) -> None:
            mid = node.get("id")
            if not mid:
                return
            reg.note_id(mid, rel)
            if mid in reg.members:
                report.error(rel, f"duplicate member id '{mid}' "
                                  f"(also in {reg.members[mid]['file']}) [S6]")
            reg.members[mid] = {"kind": kind, "owner": owner, "file": rel, "node": node}

        for dt in data.get("datatypes", []) or []:
            add_type(dt, "datatype")
        for en in data.get("enumerations", []) or []:
            add_type(en, "enumeration")
        for itf in data.get("interfaces", []) or []:
            add_type(itf, "interface")
        for ind in data.get("individuals", []) or []:
            add_type(ind, "individual")
        for con in data.get("concepts", []) or []:
            add_type(con, "concept")
            owner = con.get("id", "?")
            for p in con.get("properties", []) or []:
                add_member(p, "property", owner)
            for r in con.get("relations", []) or []:
                add_member(r, "relation", owner)
        for rol in data.get("roles", []) or []:
            add_type(rol, "role")
            owner = rol.get("id", "?")
            for p in rol.get("properties", []) or []:
                add_member(p, "property", owner)
            for r in rol.get("relations", []) or []:
                add_member(r, "relation", owner)
    return reg


# --------------------------------------------------------------------------- #
# Reference resolution                                                         #
# --------------------------------------------------------------------------- #
def type_exists(reg: Registry, qname: str) -> str:
    """Return 'local', 'external', or 'missing' for a type QName."""
    if qname in reg.types:
        return "local"
    mod = module_of(qname)
    if mod in EXTERNAL_MODULES:
        return "external"
    if mod not in reg.modules:
        return "external"  # module not in this (possibly partial) checkout
    return "missing"       # module present, but the type is not declared in it


def check_type_ref(reg: Registry, ref: str, where: str, what: str, report: Report) -> None:
    # A reference into a module that is not in this checkout is treated as an
    # external/pending reference (the model is authored incrementally against the
    # canonical domain registry); only a dangling reference *within a present
    # module* is a hard error.
    if ref in PRIMITIVES:
        return
    if type_exists(reg, ref) == "missing":
        report.error(where, f"{what} references unknown type '{ref}' "
                            f"(module '{module_of(ref)}' is present but has no such type)")


# --------------------------------------------------------------------------- #
# Gate 2/3 - resolution + semantics                                           #
# --------------------------------------------------------------------------- #
def ancestors(reg: Registry, cid: str) -> list[str]:
    """The extends-chain above cid (excluding cid), stopping at an external/missing parent."""
    chain: list[str] = []
    seen: set[str] = {cid}
    cur = reg.types.get(cid, {}).get("node", {}).get("extends")
    while cur:
        chain.append(cur)
        if cur in seen:              # cycle guard
            break
        seen.add(cur)
        parent = reg.types.get(cur)
        if not parent or parent["kind"] != "concept":
            break
        cur = parent["node"].get("extends")
    return chain


def check_modules(reg: Registry, report: Report) -> None:
    # depends_on resolves + acyclic (S4)
    graph: dict[str, set[str]] = {}
    for mid, header in reg.modules.items():
        graph[mid] = {dep.get("module") for dep in (header.get("depends_on", []) or [])}

    # cycle detection over the local module graph
    WHITE, GREY, BLACK = 0, 1, 2
    color = {m: WHITE for m in graph}

    def visit(m: str, stack: list[str]) -> None:
        color[m] = GREY
        for d in graph.get(m, ()):
            if d not in graph:
                continue
            if color[d] == GREY:
                cyc = " -> ".join(stack[stack.index(d):] + [d])
                report.error(reg.module_file.get(m, "model"),
                             f"cyclic module dependency [S4]: {cyc}")
            elif color[d] == WHITE:
                visit(d, stack + [d])
        color[m] = BLACK

    for m in graph:
        if color[m] == WHITE:
            visit(m, [m])


def check_concepts(reg: Registry, report: Report) -> None:
    role_ids = {tid for tid, t in reg.types.items() if t["kind"] == "role"}

    for tid, t in reg.types.items():
        if t["kind"] != "concept":
            continue
        node, where = t["node"], t["file"]

        # extends resolves, is a concept, and is not a role (S3)
        parent = node.get("extends")
        if parent:
            if parent in role_ids:
                report.error(where, f"concept '{tid}' extends role '{parent}' "
                                    f"- a role is not a class [S3]")
            else:
                st = type_exists(reg, parent)
                if st == "missing":
                    report.error(where, f"concept '{tid}' extends unknown type '{parent}'")
                elif st == "local" and reg.types[parent]["kind"] != "concept":
                    report.error(where, f"concept '{tid}' extends '{parent}', "
                                        f"which is a {reg.types[parent]['kind']}, not a concept")

        # single, shallow inheritance (S1)
        chain = ancestors(reg, tid)
        depth = len(chain) + 1  # this concept counts as 1
        if depth > MAX_DEPTH:
            report.error(where, f"inheritance depth {depth} exceeds cap {MAX_DEPTH} [S1]: "
                                f"{tid} -> " + " -> ".join(chain))
        elif depth == MAX_DEPTH - 1:
            report.warn(where, f"inheritance depth {depth} is one below the cap {MAX_DEPTH} [S1]")
        if tid in chain:
            report.error(where, f"cyclic inheritance involving '{tid}' [S4]")

        # implements -> interfaces
        for itf in node.get("implements", []) or []:
            st = type_exists(reg, itf)
            if st == "missing":
                report.error(where, f"concept '{tid}' implements unknown interface '{itf}'")
            elif st == "local" and reg.types[itf]["kind"] != "interface":
                report.error(where, f"concept '{tid}' implements '{itf}', which is a "
                                    f"{reg.types[itf]['kind']}, not an interface")

        # agentive-noun lint (S3): a concept named like an -er/-or is often really a
        # role. Opt-in (--lint-agentive), because many legitimate concepts end that
        # way (Liver, Brain's sibling organs, River, Number, Motor, ...).
        if LINT_AGENTIVE:
            name = node.get("name", "")
            if name.endswith("er") or name.endswith("or"):
                report.warn(where, f"concept '{name}' is an agentive noun - should it be a role? [S3 lint]")

        _check_members(reg, tid, node, where, report)
        _check_overrides(reg, tid, node, where, report)

    # roles
    for tid, t in reg.types.items():
        if t["kind"] != "role":
            continue
        node, where = t["node"], t["file"]
        pb = node.get("played_by")
        if pb:
            st = type_exists(reg, pb)
            if st == "missing":
                report.error(where, f"role '{tid}' played_by unknown concept '{pb}'")
            elif st == "local" and reg.types[pb]["kind"] != "concept":
                report.error(where, f"role '{tid}' played_by '{pb}', which is a "
                                    f"{reg.types[pb]['kind']}, not a concept [S3]")
        for cap in node.get("capabilities", []) or []:
            st = type_exists(reg, cap)
            if st == "missing":
                report.error(where, f"role '{tid}' capability '{cap}' is unknown")
            elif st == "local" and reg.types[cap]["kind"] != "interface":
                report.error(where, f"role '{tid}' capability '{cap}' is a "
                                    f"{reg.types[cap]['kind']}, not an interface")
        ctx = node.get("context")
        if ctx and ctx not in reg.modules and ctx not in EXTERNAL_MODULES:
            report.warn(where, f"role '{tid}' context '{ctx}' is not a module in this checkout")
        _check_members(reg, tid, node, where, report)


def _member_module_matches_owner(owner: str, member_id: str) -> bool:
    return type_of_member(member_id) == owner


def _check_members(reg: Registry, owner: str, node: dict, where: str, report: Report) -> None:
    for p in node.get("properties", []) or []:
        pid = p.get("id", "?")
        if not _member_module_matches_owner(owner, pid):
            report.error(where, f"property '{pid}' is declared under '{owner}' but its "
                                f"QName names '{type_of_member(pid)}' [S6]")
        check_type_ref(reg, p.get("type", ""), where, f"property '{pid}' type", report)
        # unit presence lint (R5): quantity-typed properties should carry a unit
        ptype = p.get("type", "")
        tname = ptype.split("/")[-1] if "/" in ptype else ptype
        if tname in QUANTITY_HINTS and not p.get("unit"):
            report.warn(where, f"property '{pid}' looks like a quantity ({ptype}) "
                               f"but has no unit [R5 lint]")
    for r in node.get("relations", []) or []:
        rid = r.get("id", "?")
        if not _member_module_matches_owner(owner, rid):
            report.error(where, f"relation '{rid}' is declared under '{owner}' but its "
                                f"QName names '{type_of_member(rid)}' [S6]")
        check_type_ref(reg, r.get("target", ""), where, f"relation '{rid}' target", report)
        inv = r.get("inverse")
        if inv:  # the inverse's owning concept must resolve; the member is the "other end"
            inv_owner = type_of_member(inv)
            st = type_exists(reg, inv_owner)
            if st == "missing":
                report.error(where, f"relation '{rid}' inverse '{inv}' names unknown "
                                    f"concept '{inv_owner}'")


def _as_number(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def _check_overrides(reg: Registry, cid: str, node: dict, where: str, report: Report) -> None:
    chain = set(ancestors(reg, cid))
    for ov in node.get("property_overrides", []) or []:
        pid = ov.get("property")
        if not pid:
            continue
        owner = type_of_member(pid)
        # the overridden property must belong to an ancestor
        if owner not in chain and type_exists(reg, owner) == "local":
            report.error(where, f"concept '{cid}' overrides '{pid}' but does not inherit "
                                f"from '{owner}' [S2]")
        base = reg.members.get(pid)
        if not base:
            if type_exists(reg, owner) == "local":
                report.error(where, f"concept '{cid}' overrides unknown property '{pid}'")
            continue
        # LSP narrowing (S2): a clear widening is an error
        bc = base["node"].get("constraints", {}) or {}
        oc = ov.get("constraints", {}) or {}
        b_max, o_max = _as_number(bc.get("maximum")), _as_number(oc.get("maximum"))
        if b_max is not None and o_max is not None and o_max > b_max:
            report.error(where, f"override of '{pid}' widens maximum {b_max} -> {o_max} [S2]")
        b_min, o_min = _as_number(bc.get("minimum")), _as_number(oc.get("minimum"))
        if b_min is not None and o_min is not None and o_min < b_min:
            report.error(where, f"override of '{pid}' widens minimum {b_min} -> {o_min} [S2]")
        if isinstance(bc.get("enum"), list) and isinstance(oc.get("enum"), list):
            if not set(oc["enum"]).issubset(set(bc["enum"])):
                report.error(where, f"override of '{pid}' enum is not a subset of the parent's [S2]")


def check_individuals(reg: Registry, report: Report) -> None:
    for tid, t in reg.types.items():
        if t["kind"] != "individual":
            continue
        node, where = t["node"], t["file"]
        cls = node.get("instance_of")
        if not cls:
            continue
        st = type_exists(reg, cls)
        if st == "missing":
            report.error(where, f"individual '{tid}' instance_of unknown concept '{cls}'")
        elif st == "local" and reg.types[cls]["kind"] != "concept":
            report.error(where, f"individual '{tid}' instance_of '{cls}', which is a "
                                f"{reg.types[cls]['kind']}, not a concept")


def check_provenance_honesty(reg: Registry, report: Report) -> None:
    """S5 lint: a factual node (sourced-looking source, i.e. not 'Original WMOOP definition')
    with no explicit kind should declare kind: sourced."""
    def inspect(node: dict, label: str, where: str) -> None:
        for pv in node.get("provenance", []) or []:
            src = (pv.get("source") or "")
            if "kind" not in pv and src and not src.lower().startswith("original wmoop"):
                report.warn(where, f"{label} provenance '{src[:40]}...' has no 'kind' - "
                                   f"mark it 'sourced' or 'definitional' honestly [S5 lint]")

    for tid, t in reg.types.items():
        if t["kind"] in ("concept", "role", "enumeration"):
            inspect(t["node"], f"{t['kind']} '{tid}'", t["file"])
            for p in t["node"].get("properties", []) or []:
                inspect(p, f"property '{p.get('id')}'", t["file"])


# --------------------------------------------------------------------------- #
# Optional XSD projection check                                               #
# --------------------------------------------------------------------------- #
def validate_xsd(report: Report) -> None:
    xmls = sorted(EXAMPLES_DIR.glob("*.wml.xml")) if EXAMPLES_DIR.exists() else []
    if not xmls:
        return
    try:
        import xmlschema
    except ImportError:
        report.warn("xsd", "xmlschema not installed - XSD projection gate SKIPPED "
                           "(pip install xmlschema)")
        return
    if not XSD_FILE.exists():
        report.warn("xsd", f"{XSD_FILE.name} not found - XSD gate SKIPPED")
        return
    schema = xmlschema.XMLSchema11(str(XSD_FILE))
    for xml in xmls:
        rel = rel_path(xml)
        try:
            schema.validate(str(xml))
        except xmlschema.XMLSchemaValidationError as exc:
            report.error(rel, f"[xsd] {exc.reason or exc}")


# --------------------------------------------------------------------------- #
# Driver                                                                       #
# --------------------------------------------------------------------------- #
def collect_files(targets: list[str]) -> list[Path]:
    roots = [Path(t) for t in targets] if targets else [REPO / "model"]
    files: list[Path] = []
    for root in roots:
        root = root if root.is_absolute() else (REPO / root)
        if root.is_file() and root.name.endswith(".wml.yaml"):
            files.append(root)
        elif root.is_dir():
            files.extend(sorted(root.rglob("*.wml.yaml")))
    # Exclude git/worktree dirs and `_`-prefixed meta dirs (e.g. model/_template,
    # model/_meta): those hold scaffolds and L0 fixtures, not authored domains.
    def excluded(f: Path) -> bool:
        return any(p == ".claude" or p == ".git" or p.startswith("_") for p in f.parts)
    return [f for f in files if not excluded(f)]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate WML model files (grammar + semantics).")
    ap.add_argument("targets", nargs="*", help="files or dirs (default: model/)")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--no-xsd", action="store_true", help="skip the XSD projection check")
    ap.add_argument("--lint-agentive", action="store_true",
                    help="warn on agentive-noun concepts (-er/-or) that may be roles [S3]")
    args = ap.parse_args(argv)

    global LINT_AGENTIVE
    LINT_AGENTIVE = args.lint_agentive

    files = collect_files(args.targets)
    if not files:
        _die("no *.wml.yaml files found")

    docs: dict[Path, object] = {}
    report = Report()
    for f in files:
        try:
            docs[f] = load_yaml(f)
        except Exception as exc:  # noqa: BLE001 - surface any YAML error as a gate failure
            report.error(rel_path(f), f"YAML parse error: {exc}")

    parsed = {p: d for p, d in docs.items() if d is not None}

    validate_grammar(parsed, report)
    reg = build_registry(parsed, report)
    check_modules(reg, report)
    check_concepts(reg, report)
    check_individuals(reg, report)
    check_provenance_honesty(reg, report)
    if not args.no_xsd:
        validate_xsd(report)

    # ------- report -------
    print(f"WML validation - {len(files)} file(s), {len(reg.modules)} module(s), "
          f"{sum(1 for t in reg.types.values() if t['kind'] == 'concept')} concept(s), "
          f"{sum(1 for t in reg.types.values() if t['kind'] == 'role')} role(s)")
    for w in report.warnings:
        print(f"  WARN  {w}")
    for e in report.errors:
        print(f"  ERROR {e}")

    failed = bool(report.errors) or (args.strict and bool(report.warnings))
    if failed:
        print(f"\nFAILED - {len(report.errors)} error(s), {len(report.warnings)} warning(s)")
        return 1
    print(f"\nOK - 0 errors, {len(report.warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
