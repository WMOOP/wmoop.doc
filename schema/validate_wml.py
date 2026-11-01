#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
validate_wml.py - the WML oracle.

Realises gate 1-3 of the ``wmoopc compile`` pipeline (docs/03-architecture.md Sec 2.4)
against the canonical model in ``model/**``:

  1. Grammar     - every ``*.wml.yaml`` validates against ``wml.schema.json`` (JSON Schema
                   2020-12) from the grammar submodule ``external/wmoop.json``. This is the
                   context-free shape (R1-R12, S5/S6 shapes).
  2. Resolution  - IDs and ``depends_on`` resolve; the module graph and the ``extends``
                   graph are acyclic (S4); a reference into another module follows a
                   declared ``depends_on`` edge (DoD #4) whose version pin that module
                   satisfies (DoD #3).
  3. Semantics   - cross-file rules a grammar cannot express:
                     S1 shallow inheritance (depth <= MAX_DEPTH; warned from MAX_DEPTH-1),
                     S2 LSP-safe overrides (narrow every inherited constraint, ancestors'
                        overrides included; no inherited member declared again),
                     S3 roles are not classes (no role in any ``extends``; agentive-noun lint),
                     S5 provenance honesty (factual nodes sourced) [lint],
                     S6 unique, immutable IDs; one module per directory, one header per module,
                     R5 units: a QuantityKind-typed slot names a ``wmoop.core`` Unit of that kind,
                     relation inverses (the inverse end belongs to the target; declared ends
                        agree; each end has one owner),
                     L2 individuals (values fit their concept's properties, types, cardinality,
                        constraints and simple invariants; required values present - DoD #9),
                     schemes and associations (ADR 0001, D9),
                     referential integrity of every reference.

Optionally (``--xsd`` / on by default when available) validates the WML-in-XML
projections under ``schema/examples/*.wml.xml`` against ``external/wmoop.json/wml.xsd``,
and (``--no-parity`` to skip) checks that ``wml.xsd`` and ``wml.schema.json`` - two
serializations of one grammar - stay in agreement (S4; see check_schema_parity.py).

Exit code 0 = all gates green; 1 = at least one ERROR (warnings alone do not fail
unless ``--strict``). This is the machine-checkable Definition of Done (Invariant 6).

Usage:
    python schema/validate_wml.py                 # validate model/** + any XML examples
    python schema/validate_wml.py model/transport # validate a subtree
    python schema/validate_wml.py --strict        # treat warnings as errors
    python schema/validate_wml.py --no-xsd        # skip the XSD projection check
    python schema/validate_wml.py --no-parity     # skip the XSD<->JSON-Schema parity check
    python schema/validate_wml.py --complete DIR  # DIR holds a whole model (like the default run)
"""
from __future__ import annotations

import argparse
import datetime
import json
import operator
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
# The grammar is the WMOOP/wmoop.json repo, pinned as the git submodule external/wmoop.json.
GRAMMAR_DIR = REPO / "external" / "wmoop.json"
SCHEMA_FILE = GRAMMAR_DIR / "wml.schema.json"
XSD_FILE = GRAMMAR_DIR / "wml.xsd"
EXAMPLES_DIR = HERE / "examples"

# Inheritance depth cap (S1). Configurable per org; warned from MAX_DEPTH-1, failed above.
MAX_DEPTH = 6

# Opt-in S3 lint that flags agentive-noun concepts (set by --lint-agentive).
LINT_AGENTIVE = False

# The L0 module whose individuals are the QuantityKind/Unit catalogue (R5).
CORE_MODULE = "wmoop.core"
QUANTITY_KIND = f"{CORE_MODULE}/QuantityKind"
UNIT = f"{CORE_MODULE}/Unit"

# True when the targets are a whole model (the default run, or --complete): a reference into
# a module that is not present is then dangling. A partial run (a subtree or a single file)
# accepts it when the referencing module declares that module in ``depends_on``.
COMPLETE = True


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


def local_name(qname: str) -> str:
    """wmoop.transport/Vehicle#wheelCount -> wheelCount ; wmoop.transport/Moped -> Moped"""
    return qname.rsplit("#", 1)[1] if "#" in qname else qname.rsplit("/", 1)[-1]


PRIMITIVES = {"string", "boolean", "integer", "decimal", "number", "date", "datetime", "time", "duration", "void"}

TYPE_QNAME = re.compile(r"^wmoop\.[a-z][a-z0-9]*(\.[a-z][a-z0-9]*)*/[A-Z][A-Za-z0-9]*$")
CARDINALITY = re.compile(r"^([0-9]+)(?:\.\.([0-9]+|\*))?$")
SEMVER = re.compile(r"^([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$")
ISO_DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
ISO_DATETIME = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt ][0-9]{2}:[0-9]{2}"
                          r"(:[0-9]{2}(\.[0-9]+)?)?([Zz]|[+-][0-9]{2}:[0-9]{2})?$")


def parse_cardinality(card) -> tuple[int, int | None] | None:
    """'1' -> (1, 1); '0..*' -> (0, None); '2..5' -> (2, 5); None if absent or malformed."""
    m = CARDINALITY.match(card) if isinstance(card, str) else None
    if not m:
        return None
    low = int(m.group(1))
    if m.group(2) is None:
        return low, low
    return low, None if m.group(2) == "*" else int(m.group(2))


def _semver_key(version):
    """A sortable SemVer 2.0.0 precedence key, or None if ``version`` is malformed."""
    m = SEMVER.match(version) if isinstance(version, str) else None
    if not m:
        return None
    pre = m.group(4)
    # a pre-release sorts before its release; numeric identifiers before alphanumeric ones
    pre_key = (1,) if pre is None else (0,) + tuple(
        (0, int(p)) if p.isdigit() else (1, p) for p in pre.split("."))
    return int(m.group(1)), int(m.group(2)), int(m.group(3)), pre_key


def satisfies(version, rng) -> bool | None:
    """Whether ``version`` satisfies a WML range: exact ``x.y.z``, ``~x.y.z`` (same minor) or
    ``^x.y.z`` (same left-most non-zero component, as in npm/Cargo - so ``^0.5.0`` does not
    accept 0.6.0). None when either side is malformed; the grammar gate reports that."""
    if not isinstance(rng, str) or not rng:
        return None
    op = rng[0] if rng[0] in "^~" else ""
    low, ver = _semver_key(rng[len(op):]), _semver_key(version)
    if low is None or ver is None:
        return None
    if not op:
        return ver == low
    if ver < low:
        return False
    major, minor, patch = low[:3]
    if op == "~":
        upper = (major, minor + 1, 0)
    elif major:
        upper = (major + 1, 0, 0)
    elif minor:
        upper = (0, minor + 1, 0)
    else:
        upper = (0, 0, patch + 1)
    return ver[:3] < upper


def _dicts(value) -> list[dict]:
    """The mapping items of a YAML list (anything malformed is the grammar gate's to report)."""
    return [v for v in value if isinstance(v, dict)] if isinstance(value, list) else []


def _strs(value) -> list[str]:
    """The string items of a YAML list."""
    return [v for v in value if isinstance(v, str)] if isinstance(value, list) else []


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
        self.file_header: dict[str, str] = {}        # file -> module whose header it holds
        self.file_modules: dict[str, set[str]] = {}  # file -> modules its type ids belong to
        # the wmoop.core QuantityKind/Unit catalogue (R5), filled by build_catalogue()
        self.quantity_kinds: set[str] = set()
        self.units: dict[str, dict] = {}             # unit id -> {symbol, kind}
        self.unit_by_symbol: dict[str, str] = {}     # unit symbol -> unit id
        self.unchecked_units = 0                     # units seen while no catalogue is loaded

    def note_id(self, ident: str, rel: str) -> None:
        self.id_files.setdefault(ident, []).append(rel)


def build_registry(docs: dict[Path, object], report: Report) -> Registry:
    reg = Registry()
    for path, data in docs.items():
        if not isinstance(data, dict):
            continue
        rel = rel_path(path)
        reg.file_modules[rel] = set()

        header = data.get("module")
        if isinstance(header, dict) and isinstance(header.get("id"), str):
            mid = header["id"]
            reg.file_header[rel] = mid
            if mid in reg.modules:
                report.error(rel, f"module '{mid}' already has a header in "
                                  f"{reg.module_file[mid]} (a module has exactly one header file)")
            else:
                reg.modules[mid] = header
                reg.module_file[mid] = rel

        def add_type(node: dict, kind: str) -> None:
            tid = node.get("id")
            if not isinstance(tid, str) or not tid:
                return
            reg.note_id(tid, rel)
            reg.file_modules[rel].add(module_of(tid))
            if tid in reg.types:
                report.error(rel, f"duplicate type id '{tid}' "
                                  f"(also in {reg.types[tid]['file']}) [S6]")
            reg.types[tid] = {"kind": kind, "file": rel, "node": node}

        def add_member(node: dict, kind: str, owner: str) -> None:
            mid = node.get("id")
            if not isinstance(mid, str) or not mid:
                return
            reg.note_id(mid, rel)
            if mid in reg.members:
                report.error(rel, f"duplicate member id '{mid}' "
                                  f"(also in {reg.members[mid]['file']}) [S6]")
            reg.members[mid] = {"kind": kind, "owner": owner, "file": rel, "node": node}

        for dt in _dicts(data.get("datatypes")):
            add_type(dt, "datatype")
        for en in _dicts(data.get("enumerations")):
            add_type(en, "enumeration")
        for itf in _dicts(data.get("interfaces")):
            add_type(itf, "interface")
        for ind in _dicts(data.get("individuals")):
            add_type(ind, "individual")
        for sch in _dicts(data.get("schemes")):
            add_type(sch, "scheme")
        for con in _dicts(data.get("concepts")):
            add_type(con, "concept")
            owner = con.get("id", "?")
            for p in _dicts(con.get("properties")):
                add_member(p, "property", owner)
            for r in _dicts(con.get("relations")):
                add_member(r, "relation", owner)
        for rol in _dicts(data.get("roles")):
            add_type(rol, "role")
            owner = rol.get("id", "?")
            for p in _dicts(rol.get("properties")):
                add_member(p, "property", owner)
            for r in _dicts(rol.get("relations")):
                add_member(r, "relation", owner)
        for asc in _dicts(data.get("associations")):
            add_type(asc, "association")
            owner = asc.get("id", "?")
            for p in _dicts(asc.get("properties")):
                add_member(p, "property", owner)
    return reg


def build_catalogue(reg: Registry, report: Report) -> None:
    """Index the wmoop.core QuantityKind/Unit individuals (R5) and check the catalogue itself:
    unique symbols, every Unit measures a QuantityKind, every QuantityKind's canonical unit
    is one of its own Units."""
    def values_of(node: dict) -> dict:
        vals = node.get("values")
        return vals if isinstance(vals, dict) else {}

    for tid, t in reg.types.items():
        if t["kind"] == "individual" and t["node"].get("instance_of") == QUANTITY_KIND:
            reg.quantity_kinds.add(tid)
    for tid, t in reg.types.items():
        if t["kind"] != "individual" or t["node"].get("instance_of") != UNIT:
            continue
        vals = values_of(t["node"])
        symbol, kind = vals.get("symbol"), vals.get("quantityKind")
        reg.units[tid] = {"symbol": symbol, "kind": kind}
        if isinstance(symbol, str):
            if symbol in reg.unit_by_symbol:
                report.error(t["file"], f"unit '{tid}' reuses the symbol '{symbol}' of "
                                        f"'{reg.unit_by_symbol[symbol]}' [R5]")
            else:
                reg.unit_by_symbol[symbol] = tid
        if kind not in reg.quantity_kinds:
            report.error(t["file"], f"unit '{tid}' measures '{kind}', which is not a "
                                    f"QuantityKind [R5]")
    for qk in sorted(reg.quantity_kinds):
        t = reg.types[qk]
        canonical = values_of(t["node"]).get("canonicalUnit")
        if canonical is not None and reg.units.get(canonical, {}).get("kind") != qk:
            report.error(t["file"], f"QuantityKind '{qk}' has canonical unit '{canonical}', "
                                    f"which is not one of its Units [R5]")


# --------------------------------------------------------------------------- #
# Reference resolution                                                         #
# --------------------------------------------------------------------------- #
def type_status(reg: Registry, qname: str) -> str:
    """'local' (declared in this run), 'missing' (its module is present but does not
    declare it) or 'absent' (its module is not part of this run)."""
    if qname in reg.types:
        return "local"
    return "missing" if module_of(qname) in reg.modules else "absent"


def deps_of(reg: Registry, module: str) -> set[str] | None:
    """The modules ``module`` declares in depends_on; None when its header is not loaded."""
    header = reg.modules.get(module)
    if header is None:
        return None
    return {d.get("module") for d in _dicts(header.get("depends_on"))}


def check_ref(reg: Registry, ref, src: str, where: str, what: str, report: Report) -> str | None:
    """Resolve a type reference made from module ``src`` (DoD #3/#4).

    Reports a reference into a module that does not exist (in a complete run), a reference
    into another module that ``src`` does not declare in ``depends_on``, and a dangling
    reference into a present module. Returns the referenced element's kind ('primitive' for
    a built-in type), or None when it cannot be resolved in this run."""
    if not isinstance(ref, str) or not ref:
        return None  # malformed: the grammar gate reports it
    if ref in PRIMITIVES:
        return "primitive"
    mod = module_of(ref)
    status = type_status(reg, ref)
    if status == "absent" and COMPLETE:
        report.error(where, f"{what} '{ref}': module '{mod}' does not exist in the model [DoD #3]")
        return None
    deps = deps_of(reg, src)
    if mod != src and deps is not None and mod not in deps:
        report.error(where, f"{what} '{ref}' is in module '{mod}', which '{src}' does not "
                            f"declare in depends_on [DoD #4]")
    if status == "missing":
        report.error(where, f"{what} references unknown type '{ref}' "
                            f"(module '{mod}' is present but has no such type)")
    return reg.types[ref]["kind"] if status == "local" else None


# --------------------------------------------------------------------------- #
# Gate 2/3 - resolution + semantics                                           #
# --------------------------------------------------------------------------- #
def ancestors(reg: Registry, cid: str) -> list[str]:
    """The extends-chain above cid (excluding cid), stopping at an external/missing parent."""
    chain: list[str] = []
    seen: set[str] = {cid}
    cur = reg.types.get(cid, {}).get("node", {}).get("extends")
    while isinstance(cur, str) and cur:
        chain.append(cur)
        if cur in seen:              # cycle guard
            break
        seen.add(cur)
        parent = reg.types.get(cur)
        if not parent or parent["kind"] != "concept":
            break
        cur = parent["node"].get("extends")
    return chain


def check_layout(reg: Registry, report: Report) -> None:
    """S6 / model/README.md: a module lives in one directory and has exactly one header
    file, and a file only declares ids of its own module. (The XML projector groups files
    into modules by directory, so a stray id would silently land in the wrong module.)"""
    dir_modules: dict[str, set[str]] = {}
    module_dirs: dict[str, set[str]] = {}
    for rel, mods in reg.file_modules.items():
        header = reg.file_header.get(rel)
        if header is not None:
            for m in sorted(mods - {header}):
                report.error(rel, f"file holds the header of '{header}' but declares ids of "
                                  f"module '{m}' [S6]")
            own = {header}
        else:
            if len(mods) > 1:
                report.error(rel, f"file declares ids of several modules "
                                  f"({', '.join(sorted(mods))}) [S6]")
            own = mods
        folder = rel.rsplit("/", 1)[0] if "/" in rel else "."
        for m in own:
            dir_modules.setdefault(folder, set()).add(m)
            module_dirs.setdefault(m, set()).add(folder)
    for folder, mods in sorted(dir_modules.items()):
        if len(mods) > 1:
            report.error(folder, f"directory holds several modules ({', '.join(sorted(mods))}); "
                                 f"each module lives in its own directory [S6]")
    for m, folders in sorted(module_dirs.items()):
        if len(folders) > 1:
            report.error(reg.module_file.get(m, sorted(folders)[0]),
                         f"module '{m}' is spread over several directories "
                         f"({', '.join(sorted(folders))}) [S6]")
        if m not in reg.modules:
            where = sorted(f for f, ms in reg.file_modules.items() if m in ms)[0]
            msg = f"module '{m}' has declarations but no file carries its `module:` header [S6]"
            if COMPLETE:
                report.error(where, msg)
            else:
                report.warn(where, msg)


def check_modules(reg: Registry, report: Report) -> None:
    # depends_on resolves (DoD #3), pins are satisfied, and the graph is acyclic (S4)
    graph: dict[str, set[str]] = {}
    for mid, header in reg.modules.items():
        where = reg.module_file[mid]
        deps: set[str] = set()
        for dep in _dicts(header.get("depends_on")):
            dmod, rng = dep.get("module"), dep.get("version")
            if not isinstance(dmod, str):
                continue
            if dmod == mid:
                report.error(where, f"module '{mid}' depends on itself [S4]")
                continue
            if dmod in deps:
                report.warn(where, f"module '{mid}' lists the dependency '{dmod}' twice")
            deps.add(dmod)
            target = reg.modules.get(dmod)
            if target is None:
                if COMPLETE:
                    report.error(where, f"module '{mid}' depends on '{dmod}', which does not "
                                        f"exist in the model [DoD #3]")
                continue
            if satisfies(str(target.get("version", "")), rng) is False:
                report.error(where, f"module '{mid}' pins '{dmod}' to '{rng}', but '{dmod}' is "
                                    f"at {target.get('version')} [DoD #3]")
        graph[mid] = deps

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
    for tid, t in reg.types.items():
        if t["kind"] != "concept":
            continue
        node, where, mod = t["node"], t["file"], module_of(tid)

        # extends resolves, is a concept, and is not a role (S3). A parent in another module
        # is fine along a declared depends_on edge, like any cross-module reference.
        parent = node.get("extends")
        if parent:
            kind = check_ref(reg, parent, mod, where, f"concept '{tid}' extends", report)
            if kind == "role":
                report.error(where, f"concept '{tid}' extends role '{parent}' "
                                    f"- a role is not a class [S3]")
            elif kind not in (None, "concept"):
                report.error(where, f"concept '{tid}' extends '{parent}', "
                                    f"which is a {kind}, not a concept")

        # single, shallow inheritance (S1)
        chain = ancestors(reg, tid)
        depth = len(chain) + 1  # this concept counts as 1
        if depth > MAX_DEPTH:
            report.error(where, f"inheritance depth {depth} exceeds cap {MAX_DEPTH} [S1]: "
                                f"{tid} -> " + " -> ".join(chain))
        elif depth >= MAX_DEPTH - 1:
            report.warn(where, f"inheritance depth {depth} is at or just below the cap "
                               f"{MAX_DEPTH}; justify it in review [S1]")
        if tid in chain:
            report.error(where, f"cyclic inheritance involving '{tid}' [S4]")

        # implements -> interfaces
        for itf in _strs(node.get("implements")):
            kind = check_ref(reg, itf, mod, where, f"concept '{tid}' implements", report)
            if kind not in (None, "interface"):
                report.error(where, f"concept '{tid}' implements '{itf}', which is a "
                                    f"{kind}, not an interface")

        # agentive-noun lint (S3): a concept named like an -er/-or is often really a
        # role. Opt-in (--lint-agentive), because many legitimate concepts end that
        # way (Liver, Brain's sibling organs, River, Number, Motor, ...).
        if LINT_AGENTIVE:
            name = node.get("name", "")
            if isinstance(name, str) and (name.endswith("er") or name.endswith("or")):
                report.warn(where, f"concept '{name}' is an agentive noun - should it be a role? [S3 lint]")

        _check_members(reg, tid, node, where, report)
        _check_redeclared(reg, tid, node, where, report)
        _check_overrides(reg, tid, node, where, report)
        _check_classified_as(reg, tid, node, where, report)

    # roles
    for tid, t in reg.types.items():
        if t["kind"] != "role":
            continue
        node, where, mod = t["node"], t["file"], module_of(tid)
        pb = node.get("played_by")
        if pb is not None and not isinstance(pb, str):
            report.error(where, f"role '{tid}' played_by must be a single concept QName; a role "
                                f"with several kinds of player needs the planned RoleMixin [S3]")
        elif pb:
            kind = check_ref(reg, pb, mod, where, f"role '{tid}' played_by", report)
            if kind not in (None, "concept"):
                report.error(where, f"role '{tid}' played_by '{pb}', which is a "
                                    f"{kind}, not a concept [S3]")
        for cap in _strs(node.get("capabilities")):
            kind = check_ref(reg, cap, mod, where, f"role '{tid}' capability", report)
            if kind not in (None, "interface"):
                report.error(where, f"role '{tid}' capability '{cap}' is a "
                                    f"{kind}, not an interface")
        ctx = node.get("context")
        if isinstance(ctx, str) and ctx not in reg.modules:
            if COMPLETE:
                report.error(where, f"role '{tid}' context '{ctx}' is not a module of the model")
            else:
                report.warn(where, f"role '{tid}' context '{ctx}' is not a module in this checkout")
        _check_cardinality(node.get("cardinality_per_player"), where,
                           f"role '{tid}' cardinality_per_player", report)
        _check_members(reg, tid, node, where, report)
        _check_classified_as(reg, tid, node, where, report)


def check_interfaces(reg: Registry, report: Report) -> None:
    """Operation parameter and return types resolve (referential integrity)."""
    for tid, t in reg.types.items():
        if t["kind"] != "interface":
            continue
        node, where, mod = t["node"], t["file"], module_of(tid)
        for op in _dicts(node.get("operations")):
            label = f"interface '{tid}' operation '{op.get('name', '?')}'"
            check_ref(reg, op.get("returns"), mod, where, f"{label} returns", report)
            for prm in _dicts(op.get("params")):
                check_ref(reg, prm.get("type"), mod, where,
                          f"{label} parameter '{prm.get('name', '?')}' type", report)


def check_datatypes(reg: Registry, report: Report) -> None:
    for tid, t in reg.types.items():
        if t["kind"] != "datatype":
            continue
        _check_constraint_coherence(t["node"].get("constraints"), t["file"],
                                    f"datatype '{tid}'", report)
        _check_unit(reg, t["node"], None, t["file"], f"datatype '{tid}'", report)


def _member_module_matches_owner(owner: str, member_id: str) -> bool:
    return type_of_member(member_id) == owner


# What to use instead when a slot points at the wrong kind of element.
PROPERTY_TYPE_HINT = {
    "role": "link to a role with a relation",
    "interface": "link to an implementor with a relation",
    "association": "link to an association with a relation",
    "scheme": "classify against a scheme with classified_as",
}
RELATION_TARGET_HINT = {
    "primitive": "use a property for a value",
    "datatype": "use a property for a value",
    "enumeration": "use a property for a value",
    "scheme": "classify against a scheme with classified_as",
    "individual": "a relation targets a type; a property can hold an individual",
}


def _check_members(reg: Registry, owner: str, node: dict, where: str, report: Report) -> None:
    mod = module_of(owner)
    for p in _dicts(node.get("properties")):
        pid = p.get("id", "?")
        if not _member_module_matches_owner(owner, pid):
            report.error(where, f"property '{pid}' is declared under '{owner}' but its "
                                f"QName names '{type_of_member(pid)}' [S6]")
        label = f"property '{pid}'"
        _check_cardinality(p.get("cardinality"), where, label, report)
        _check_constraint_coherence(p.get("constraints"), where, label, report)
        ptype = p.get("type")
        kind = check_ref(reg, ptype, mod, where, f"{label} type", report)
        if kind == "individual" and ptype not in reg.quantity_kinds:
            report.error(where, f"{label} is typed by individual '{ptype}', which is not a "
                                f"QuantityKind")
        elif kind in PROPERTY_TYPE_HINT:
            report.error(where, f"{label} is typed by {kind} '{ptype}'; a property holds a "
                                f"value - {PROPERTY_TYPE_HINT[kind]}")
        _check_unit(reg, p, ptype, where, label, report)
    for r in _dicts(node.get("relations")):
        rid = r.get("id", "?")
        if not _member_module_matches_owner(owner, rid):
            report.error(where, f"relation '{rid}' is declared under '{owner}' but its "
                                f"QName names '{type_of_member(rid)}' [S6]")
        label = f"relation '{rid}'"
        _check_cardinality(r.get("cardinality"), where, label, report)
        target = r.get("target")
        kind = check_ref(reg, target, mod, where, f"{label} target", report)
        if kind in RELATION_TARGET_HINT:
            report.error(where, f"{label} targets {kind} '{target}'; "
                                f"{RELATION_TARGET_HINT[kind]}")


def _check_unit(reg: Registry, node: dict, ptype, where: str, label: str, report: Report) -> None:
    """R5: a QuantityKind-typed slot names a Unit of that kind, and any unit given resolves
    to the wmoop.core catalogue - by symbol (``km/h``) or by id (``wmoop.core/KilometrePerHour``)."""
    unit = node.get("unit")
    if not reg.units:
        if unit is not None:
            reg.unchecked_units += 1
        return
    is_quantity = isinstance(ptype, str) and ptype in reg.quantity_kinds
    if unit is None:
        if is_quantity:
            report.error(where, f"{label} is a {local_name(ptype)} quantity but names no unit [R5]")
        return
    if not isinstance(unit, str):
        return  # malformed: the grammar gate reports it
    uid = reg.unit_by_symbol.get(unit) or (unit if unit in reg.units else None)
    if uid is None:
        report.error(where, f"{label} unit '{unit}' is not a Unit of the {CORE_MODULE} "
                            f"catalogue [R5]")
    elif is_quantity and reg.units[uid]["kind"] != ptype:
        report.error(where, f"{label} unit '{unit}' measures "
                            f"{local_name(str(reg.units[uid]['kind']))}, but the slot is typed "
                            f"{local_name(ptype)} [R5]")


def _check_cardinality(card, where: str, label: str, report: Report) -> None:
    bounds = parse_cardinality(card)
    if bounds is None:
        return  # absent or malformed: the grammar gate reports it
    low, high = bounds
    if high is not None and low > high:
        report.error(where, f"{label} cardinality '{card}' has a minimum above its maximum")
    elif high == 0:
        report.warn(where, f"{label} cardinality '{card}' can never hold a value")


def _as_number(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def _upper(c: dict):
    """The tightest upper bound of a constraint set as (value, exclusive), or None."""
    bounds = [(c[k], k == "exclusiveMaximum") for k in ("maximum", "exclusiveMaximum")
              if _as_number(c.get(k)) is not None]
    return min(bounds, key=lambda b: (b[0], not b[1])) if bounds else None


def _lower(c: dict):
    """The tightest lower bound of a constraint set as (value, exclusive), or None."""
    bounds = [(c[k], k == "exclusiveMinimum") for k in ("minimum", "exclusiveMinimum")
              if _as_number(c.get(k)) is not None]
    return max(bounds, key=lambda b: (b[0], b[1])) if bounds else None


def _within(v, low, high) -> bool:
    if low and (v < low[0] or (v == low[0] and low[1])):
        return False
    if high and (v > high[0] or (v == high[0] and high[1])):
        return False
    return True


def _bounds_text(low, high) -> str:
    parts = []
    if low:
        parts.append(f"{'>' if low[1] else '>='} {low[0]}")
    if high:
        parts.append(f"{'<' if high[1] else '<='} {high[0]}")
    return ", ".join(parts)


def _check_constraint_coherence(c, where: str, label: str, report: Report) -> None:
    """A constraint set must admit a value: bounds in order, enum values inside them."""
    if not isinstance(c, dict):
        return
    low, high = _lower(c), _upper(c)
    if low and high and not (low[0] < high[0] or (low[0] == high[0] and not (low[1] or high[1]))):
        report.error(where, f"{label} constraints admit no value ({_bounds_text(low, high)})")
    elif isinstance(c.get("enum"), list):
        outside = [v for v in c["enum"] if _as_number(v) is not None and not _within(v, low, high)]
        if outside:
            report.error(where, f"{label} enum value(s) {outside} lie outside its own bounds "
                                f"({_bounds_text(low, high)})")
    lo_len, hi_len = _as_number(c.get("minLength")), _as_number(c.get("maxLength"))
    if lo_len is not None and hi_len is not None and lo_len > hi_len:
        report.error(where, f"{label} constraints have minLength {lo_len} above maxLength {hi_len}")


def _inherited_members(reg: Registry, cid: str) -> dict[str, str]:
    """Local name -> id of every property and relation ``cid`` inherits."""
    found: dict[str, str] = {}
    for anc in ancestors(reg, cid):
        if anc == cid:
            continue
        anode = reg.types.get(anc, {}).get("node", {})
        for m in _dicts(anode.get("properties")) + _dicts(anode.get("relations")):
            if isinstance(m.get("id"), str):
                found.setdefault(local_name(m["id"]), m["id"])
    return found


def _check_redeclared(reg: Registry, cid: str, node: dict, where: str, report: Report) -> None:
    """S2: a subkind narrows an inherited member with property_overrides; declaring it again
    would let the subkind change its type, unit or meaning."""
    inherited = _inherited_members(reg, cid)
    for m in _dicts(node.get("properties")) + _dicts(node.get("relations")):
        mid = m.get("id")
        if isinstance(mid, str) and local_name(mid) in inherited:
            report.error(where, f"'{mid}' redeclares inherited member "
                                f"'{inherited[local_name(mid)]}'; narrow it with "
                                f"property_overrides instead [S2]")


def _constraint_sources(reg: Registry, cid: str, pid: str, include_self: bool) -> list[tuple[str, dict]]:
    """The constraint sets that a value or an override of ``pid`` on ``cid`` must respect,
    most general first: the property's datatype, the property itself, each ancestor's
    override of it - and, with ``include_self``, the concept's own override."""
    sources: list[tuple[str, dict]] = []
    base = reg.members.get(pid)
    if base:
        ptype = base["node"].get("type")
        dt = reg.types.get(ptype) if isinstance(ptype, str) else None
        if dt and dt["kind"] == "datatype" and isinstance(dt["node"].get("constraints"), dict):
            sources.append((f"datatype '{ptype}'", dt["node"]["constraints"]))
        if isinstance(base["node"].get("constraints"), dict):
            sources.append((f"property '{pid}'", base["node"]["constraints"]))
    chain = list(reversed(ancestors(reg, cid))) + ([cid] if include_self else [])
    for c in chain:
        for ov in _dicts(reg.types.get(c, {}).get("node", {}).get("property_overrides")):
            if ov.get("property") == pid and isinstance(ov.get("constraints"), dict):
                sources.append((f"override in '{c}'", ov["constraints"]))
    return sources


def _widenings(oc: dict, sc: dict) -> list[str]:
    """How an override's constraint set ``oc`` fails to narrow an inherited set ``sc``."""
    found = []
    o, s = _upper(oc), _upper(sc)
    if o and s and (o[0] > s[0] or (o[0] == s[0] and s[1] and not o[1])):
        found.append(f"widens the maximum {s[0]} -> {o[0]}")
    o, s = _lower(oc), _lower(sc)
    if o and s and (o[0] < s[0] or (o[0] == s[0] and s[1] and not o[1])):
        found.append(f"widens the minimum {s[0]} -> {o[0]}")
    o_enum = oc.get("enum")
    if isinstance(o_enum, list):
        s_enum = sc.get("enum")
        if isinstance(s_enum, list):
            extra = [v for v in o_enum if v not in s_enum]
            if extra:
                found.append(f"allows enum value(s) {extra} that are not inherited")
        low, high = _lower(sc), _upper(sc)
        outside = [v for v in o_enum if _as_number(v) is not None and not _within(v, low, high)]
        if outside:
            found.append(f"allows enum value(s) {outside} outside the bounds ({_bounds_text(low, high)})")
    for key, wider in (("maxLength", operator.gt), ("minLength", operator.lt)):
        o_len, s_len = _as_number(oc.get(key)), _as_number(sc.get(key))
        if o_len is not None and s_len is not None and wider(o_len, s_len):
            found.append(f"widens {key} {s_len} -> {o_len}")
    return found


def _check_overrides(reg: Registry, cid: str, node: dict, where: str, report: Report) -> None:
    chain = set(ancestors(reg, cid))
    for ov in _dicts(node.get("property_overrides")):
        pid = ov.get("property")
        if not isinstance(pid, str) or not pid:
            continue
        owner = type_of_member(pid)
        if type_status(reg, owner) != "local":
            continue  # an unresolvable owner is reported through the extends chain
        # the overridden property must belong to an ancestor
        if owner not in chain:
            report.error(where, f"concept '{cid}' overrides '{pid}' but does not inherit "
                                f"from '{owner}' [S2]")
        base = reg.members.get(pid)
        if not base:
            report.error(where, f"concept '{cid}' overrides unknown property '{pid}'")
            continue
        oc = ov.get("constraints")
        if not isinstance(oc, dict):
            continue
        label = f"override of '{pid}' in '{cid}'"
        _check_constraint_coherence(oc, where, label, report)
        # LSP narrowing (S2) against every inherited constraint, not only the base property's
        for source, sc in _constraint_sources(reg, cid, pid, include_self=False):
            for problem in _widenings(oc, sc):
                report.error(where, f"{label} {problem} (set by {source}) [S2]")
        ptype = base["node"].get("type")
        enum_t = reg.types.get(ptype) if isinstance(ptype, str) else None
        if enum_t and enum_t["kind"] == "enumeration" and isinstance(oc.get("enum"), list):
            literals = {v.get("id") for v in _dicts(enum_t["node"].get("values"))}
            for lit in oc["enum"]:
                if lit not in literals:
                    report.error(where, f"{label} lists '{lit}', which is not a value of "
                                        f"'{ptype}' [S2]")


def _check_classified_as(reg: Registry, owner: str, node: dict, where: str, report: Report) -> None:
    """ADR 0001: a classification is a claim against a declared, first-class scheme."""
    mod = module_of(owner)
    seen: set = set()
    for claim in _dicts(node.get("classified_as")):
        scheme, value = claim.get("scheme"), claim.get("value")
        if not isinstance(scheme, str) or not scheme:
            continue
        if not TYPE_QNAME.match(scheme):
            report.error(where, f"'{owner}' is classified under '{scheme}', which is not a "
                                f"scheme id: declare the scheme under `schemes:` and reference "
                                f"its id [ADR 0001]")
        else:
            kind = check_ref(reg, scheme, mod, where, f"'{owner}' classified_as scheme", report)
            if kind not in (None, "scheme"):
                report.error(where, f"'{owner}' classified_as scheme '{scheme}' is a {kind}, "
                                    f"not a scheme [ADR 0001]")
        if (scheme, value) in seen:
            report.warn(where, f"'{owner}' repeats the classification {scheme} = {value!r}")
        seen.add((scheme, value))


def check_inverses(reg: Registry, report: Report) -> None:
    """``inverse`` names the member that navigates back from the target (schema/README.md
    §3.11), so that member belongs to the target. The target may leave it implied (it is
    generated) or declare it; a declared end must point back (inverse symmetry), and each
    inverse end belongs to exactly one relation."""
    claims: dict[str, list[str]] = {}
    for rid, m in reg.members.items():
        if m["kind"] != "relation":
            continue
        node, where, owner = m["node"], m["file"], m["owner"]
        inv, target = node.get("inverse"), node.get("target")
        if not isinstance(inv, str) or not isinstance(target, str):
            continue
        if type_of_member(inv) != target:
            report.error(where, f"relation '{rid}' inverse '{inv}' must be a member of the "
                                f"relation's target '{target}' [inverse]")
            continue
        claims.setdefault(inv, []).append(rid)
        other = reg.members.get(inv)
        if other is None:
            # implied end: generated on the target, so it must not clash with what the target
            # inherits, and it cannot be added to a module that does not depend on this one
            if reg.types.get(target, {}).get("kind") == "concept":
                clash = _inherited_members(reg, target).get(local_name(inv))
                if clash:
                    report.error(where, f"relation '{rid}' inverse '{inv}' clashes with "
                                        f"'{clash}', which '{target}' inherits [inverse]")
            if module_of(target) != module_of(rid):
                report.warn(where, f"relation '{rid}' implies member '{inv}' on '{target}', "
                                   f"but module '{module_of(target)}' cannot gain members from "
                                   f"'{module_of(rid)}' (docs/03-architecture.md §4.5) [inverse]")
            continue
        if other["kind"] != "relation":
            report.error(where, f"relation '{rid}' inverse '{inv}' is a {other['kind']}, "
                                f"not a relation [inverse]")
            continue
        back = other["node"].get("target")
        if back != owner:
            report.error(where, f"relation '{rid}' and its inverse '{inv}' disagree: "
                                f"'{inv}' targets '{back}', not '{owner}' [inverse]")
        back_inv = other["node"].get("inverse")
        if back_inv is not None and back_inv != rid:
            report.error(where, f"relation '{rid}' names '{inv}' as its inverse, but '{inv}' "
                                f"names '{back_inv}' [inverse]")
    for inv, rids in sorted(claims.items()):
        if len(rids) > 1:
            report.error(reg.members[rids[1]]["file"],
                         f"relations {', '.join(rids)} all name '{inv}' as their inverse; "
                         f"an inverse end belongs to one relation [inverse]")


def check_associations(reg: Registry, report: Report) -> None:
    """D9: a reified association ties >= 2 uniquely named participants - entities, not values
    - and carries its own typed, sourced properties."""
    for tid, t in reg.types.items():
        if t["kind"] != "association":
            continue
        node, where, mod = t["node"], t["file"], module_of(tid)
        names: set = set()
        for part in _dicts(node.get("participants")):
            pname, ptype = part.get("name"), part.get("type")
            label = f"association '{tid}' participant '{pname}'"
            if pname in names:
                report.error(where, f"{label} is declared twice [D9]")
            names.add(pname)
            _check_cardinality(part.get("cardinality"), where, label, report)
            kind = check_ref(reg, ptype, mod, where, f"{label} type", report)
            if kind in ("primitive", "datatype", "enumeration"):
                report.error(where, f"{label} is a value ({ptype}); declare it under properties "
                                    f"- participants are the entities the association ties [D9]")
            elif kind in ("scheme", "individual"):
                report.error(where, f"{label} is a {kind}; a participant is a concept, role, "
                                    f"interface or association [D9]")
        for p in _dicts(node.get("properties")):
            pid = p.get("id")
            if isinstance(pid, str) and local_name(pid) in names:
                report.error(where, f"property '{pid}' has the name of a participant of "
                                    f"'{tid}' [D9]")
        _check_members(reg, tid, node, where, report)
        _check_classified_as(reg, tid, node, where, report)


# A simple invariant clause: ``self.<property> <op> <literal>``. Clauses may be joined by
# ``and``; anything richer (quantifiers, arithmetic) waits for WMX (ADR 0002).
SIMPLE_INVARIANT = re.compile(
    r"^self\.([a-z][A-Za-z0-9]*)\s*(<=|>=|==|!=|<|>)\s*"
    r"(-?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?|true|false|'[^']*'|\"[^\"]*\")$")
COMPARE = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge,
           "==": operator.eq, "!=": operator.ne}


def _literal(text: str):
    if text in ("true", "false"):
        return text == "true"
    if text[0] in "'\"":
        return text[1:-1]
    return float(text) if any(ch in text for ch in ".eE") else int(text)


def _evaluate_invariant(expr, values: dict) -> str:
    """'holds', 'violated', 'unknown' (a value it reads is not recorded - open world, so not
    a violation) or 'unsupported' (beyond the simple form; needs WMX)."""
    if not isinstance(expr, str):
        return "unsupported"
    clauses = [SIMPLE_INVARIANT.match(part) for part in re.split(r"\s+and\s+", expr.strip())]
    if not all(clauses):
        return "unsupported"
    verdict = "holds"
    for m in clauses:
        name, op, lit = m.groups()
        value = values.get(name)
        if value is None or isinstance(value, (list, dict)):
            verdict = "unknown"
            continue
        try:
            if not COMPARE[op](value, _literal(lit)):
                return "violated"
        except TypeError:
            verdict = "unknown"  # a mistyped value is reported by the type check
    return verdict


def _is_a(reg: Registry, cls, ancestor: str) -> bool:
    return isinstance(cls, str) and (cls == ancestor or ancestor in ancestors(reg, cls))


def _value_type_error(reg: Registry, ptype, value) -> str | None:
    """Why ``value`` is not a value of WML type ``ptype``; None if it is, or if the type
    cannot be checked in this run."""
    t = reg.types.get(ptype) if isinstance(ptype, str) else None
    base = t["node"].get("base") if t and t["kind"] == "datatype" else ptype
    if t and t["kind"] == "enumeration":
        literals = [v.get("id") for v in _dicts(t["node"].get("values"))]
        return None if value in literals else (
            f"{value!r} is not a value of {ptype} ({', '.join(map(str, literals))})")
    if t and t["kind"] == "concept":
        ref = reg.types.get(value) if isinstance(value, str) else None
        if not ref or ref["kind"] != "individual":
            return f"{value!r} is not the id of an individual"
        cls = ref["node"].get("instance_of")
        return None if _is_a(reg, cls, ptype) else f"'{value}' is a {cls}, not a {ptype}"
    if base == "string":
        ok = isinstance(value, str)
    elif base == "boolean":
        ok = isinstance(value, bool)
    elif base == "integer":
        ok = isinstance(value, int) and not isinstance(value, bool)
    elif base in ("decimal", "number") or ptype in reg.quantity_kinds:
        ok = _as_number(value) is not None
    elif base == "date":
        ok = ((isinstance(value, datetime.date) and not isinstance(value, datetime.datetime))
              or (isinstance(value, str) and bool(ISO_DATE.match(value))))
    elif base == "datetime":
        ok = isinstance(value, datetime.datetime) or (isinstance(value, str) and bool(ISO_DATETIME.match(value)))
    elif base in ("time", "duration"):
        ok = isinstance(value, str)
    else:
        return None
    expected = local_name(ptype) if isinstance(ptype, str) and "/" in ptype else ptype
    return None if ok else f"{value!r} is not a valid {expected}"


def _constraint_violations(value, c: dict) -> list[str]:
    found = []
    if _as_number(value) is not None:
        low, high = _lower(c), _upper(c)
        if not _within(value, low, high):
            found.append(f"{value} is outside the bounds ({_bounds_text(low, high)})")
        step = _as_number(c.get("multipleOf"))
        if step and abs(value / step - round(value / step)) > 1e-9:
            found.append(f"{value} is not a multiple of {step}")
    if isinstance(c.get("enum"), list) and value not in c["enum"]:
        found.append(f"{value!r} is not one of {c['enum']}")
    if isinstance(value, str):
        lo_len, hi_len = _as_number(c.get("minLength")), _as_number(c.get("maxLength"))
        if lo_len is not None and len(value) < lo_len:
            found.append(f"{value!r} is shorter than {lo_len}")
        if hi_len is not None and len(value) > hi_len:
            found.append(f"{value!r} is longer than {hi_len}")
        pattern = c.get("pattern")
        if isinstance(pattern, str):
            try:
                if not re.search(pattern, value):
                    found.append(f"{value!r} does not match the pattern {pattern!r}")
            except re.error as exc:
                found.append(f"the pattern {pattern!r} is not a valid regular expression ({exc})")
        fmt = c.get("format")
        if fmt == "date" and not ISO_DATE.match(value):
            found.append(f"{value!r} is not a date (YYYY-MM-DD)")
        elif fmt == "date-time" and not ISO_DATETIME.match(value):
            found.append(f"{value!r} is not a date-time")
    return found


def _check_value(reg: Registry, tid: str, cls: str, prop: dict, value, where: str, report: Report) -> None:
    pid = prop["id"]
    bounds = parse_cardinality(prop.get("cardinality")) or (0, 1)
    items = value if isinstance(value, list) else [value]
    if isinstance(value, list):
        if bounds[1] == 1:
            report.error(where, f"individual '{tid}' gives a list for single-valued '{pid}' [DoD #9]")
            return
        if len(items) < bounds[0] or (bounds[1] is not None and len(items) > bounds[1]):
            report.error(where, f"individual '{tid}' gives {len(items)} value(s) for '{pid}', "
                                f"outside its cardinality {prop.get('cardinality')} [DoD #9]")
    sources = _constraint_sources(reg, cls, pid, include_self=True)
    for item in items:
        problem = _value_type_error(reg, prop.get("type"), item)
        if problem:
            report.error(where, f"individual '{tid}' value for '{pid}': {problem} [DoD #9]")
            continue
        reported: set[str] = set()
        for source, c in sources:
            for msg in _constraint_violations(item, c):
                if msg not in reported:
                    reported.add(msg)
                    report.error(where, f"individual '{tid}' value for '{pid}': {msg} "
                                        f"(set by {source}) [DoD #9]")


def check_individuals(reg: Registry, report: Report) -> int:
    """DoD #9: an individual instantiates a concrete concept; it sets only properties of that
    concept or its ancestors, with values of the declared type, cardinality and constraints;
    it populates every required property; and it satisfies the simple invariants
    (``self.<property> <op> <literal>``, joined by ``and``). Returns how many invariant
    checks could not be evaluated because they need WMX (ADR 0002)."""
    unsupported = 0
    for tid, t in reg.types.items():
        if t["kind"] != "individual":
            continue
        node, where, mod = t["node"], t["file"], module_of(tid)
        _check_classified_as(reg, tid, node, where, report)
        cls = node.get("instance_of")
        kind = check_ref(reg, cls, mod, where, f"individual '{tid}' instance_of", report)
        if kind is None:
            continue
        if kind != "concept":
            report.error(where, f"individual '{tid}' instance_of '{cls}', which is a "
                                f"{kind}, not a concept")
            continue
        if reg.types[cls]["node"].get("kind") == "abstract":
            report.error(where, f"individual '{tid}' instantiates abstract concept '{cls}' [DoD #9]")
        chain = [cls] + ancestors(reg, cls)
        whole_chain = all(reg.types.get(c, {}).get("kind") == "concept" for c in chain)
        props: dict[str, dict] = {}
        relations: dict[str, dict] = {}
        for c in reversed(chain):
            cnode = reg.types.get(c, {}).get("node", {})
            for p in _dicts(cnode.get("properties")):
                if isinstance(p.get("id"), str):
                    props[local_name(p["id"])] = p
            for r in _dicts(cnode.get("relations")):
                if isinstance(r.get("id"), str):
                    relations[local_name(r["id"])] = r
        values = node.get("values") if isinstance(node.get("values"), dict) else {}
        for key, value in values.items():
            if key in props:
                _check_value(reg, tid, cls, props[key], value, where, report)
            elif key in relations:
                report.error(where, f"individual '{tid}' sets '{key}', which is a relation of "
                                    f"'{cls}'; `values` holds properties only [DoD #9]")
            elif whole_chain:
                report.error(where, f"individual '{tid}' sets '{key}', which is not a property "
                                    f"of '{cls}' or its ancestors [DoD #9]")
        for name, p in props.items():
            bounds = parse_cardinality(p.get("cardinality")) or (0, 1)
            required = p.get("required") is True or bounds[0] >= 1
            if required and name not in values and "default" not in p:
                report.error(where, f"individual '{tid}' has no value for required property "
                                    f"'{p['id']}' [DoD #9]")
        for c in chain:
            for inv in _dicts(reg.types.get(c, {}).get("node", {}).get("invariants")):
                verdict = _evaluate_invariant(inv.get("expr"), values)
                if verdict == "unsupported":
                    unsupported += 1
                elif verdict == "violated":
                    report.error(where, f"individual '{tid}' violates invariant "
                                        f"'{inv.get('id')}' of '{c}': {inv.get('expr')} [DoD #9]")
    return unsupported


def check_provenance_honesty(reg: Registry, report: Report) -> None:
    """S5 lint: a factual node (sourced-looking source, i.e. not 'Original WMOOP definition')
    with no explicit kind should declare kind: sourced."""
    def inspect(node: dict, label: str, where: str) -> None:
        for pv in _dicts(node.get("provenance")):
            src = pv.get("source")
            if not isinstance(src, str):
                continue
            if "kind" not in pv and src and not src.lower().startswith("original wmoop"):
                report.warn(where, f"{label} provenance '{src[:40]}...' has no 'kind' - "
                                   f"mark it 'sourced' or 'definitional' honestly [S5 lint]")

    for tid, t in reg.types.items():
        if t["kind"] in ("concept", "role", "enumeration", "scheme", "association"):
            inspect(t["node"], f"{t['kind']} '{tid}'", t["file"])
            for p in _dicts(t["node"].get("properties")):
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
# Schema-mirror parity (S4): wml.xsd and wml.schema.json are one grammar       #
# --------------------------------------------------------------------------- #
def validate_parity(report: Report) -> None:
    """S4 durable fix: the JSON Schema and the XSD are two serializations of the
    same WML grammar and must agree (enums, fields, sections). Delegates to
    schema/check_schema_parity.py so drift in either mirror fails the DoD."""
    try:
        import check_schema_parity  # same directory (schema/) as this script
    except ImportError as exc:  # pragma: no cover - defensive
        report.warn("parity", f"check_schema_parity not importable ({exc}); S4 parity gate SKIPPED")
        return
    for p in check_schema_parity.check_parity():
        report.error("schema-parity", f"[S4] {p}")


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
            # Skip git/worktree dirs and `_`-prefixed meta dirs (e.g. model/_template,
            # model/_meta) below the scanned root: those hold scaffolds and L0 fixtures, not
            # authored domains. Only the part of the path under the root counts, so a
            # checkout that itself lives under a `_...` or `.claude/...` directory still works.
            for f in sorted(root.rglob("*.wml.yaml")):
                parts = f.relative_to(root).parts
                if not any(p in (".claude", ".git") or p.startswith("_") for p in parts):
                    files.append(f)
    return list(dict.fromkeys(files))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate WML model files (grammar + semantics).")
    ap.add_argument("targets", nargs="*", help="files or dirs (default: model/)")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--no-xsd", action="store_true", help="skip the XSD projection check")
    ap.add_argument("--no-parity", action="store_true",
                    help="skip the XSD<->JSON-Schema mirror parity check (S4)")
    ap.add_argument("--lint-agentive", action="store_true",
                    help="warn on agentive-noun concepts (-er/-or) that may be roles [S3]")
    ap.add_argument("--complete", action="store_true",
                    help="the targets hold a whole model: a reference into a module that is not "
                         "among them is dangling (implied when no target is given)")
    args = ap.parse_args(argv)

    global LINT_AGENTIVE, COMPLETE
    LINT_AGENTIVE = args.lint_agentive
    model_root = (REPO / "model").resolve()
    COMPLETE = args.complete or all((REPO / t).resolve() == model_root for t in args.targets)

    if not SCHEMA_FILE.is_file():
        _die(f"{SCHEMA_FILE.relative_to(REPO).as_posix()} not found - the grammar submodule is "
             "not checked out (run: git submodule update --init)")
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
    unsupported = 0
    for gate in (build_catalogue, check_layout, check_modules, check_concepts, check_interfaces,
                 check_datatypes, check_inverses, check_associations, check_individuals,
                 check_provenance_honesty):
        try:
            result = gate(reg, report)
        except Exception as exc:  # noqa: BLE001 - one crashing gate must not hide the others
            report.error("validator", f"internal error in {gate.__name__}: "
                                      f"{type(exc).__name__}: {exc} (usually malformed input "
                                      f"that the grammar gate reports)")
            continue
        if gate is check_individuals:
            unsupported = result
    if not args.no_xsd:
        validate_xsd(report)
    if not args.no_parity:
        validate_parity(report)

    # ------- report -------
    def count(kind: str) -> int:
        return sum(1 for t in reg.types.values() if t["kind"] == kind)

    print(f"WML validation - {len(files)} file(s), {len(reg.modules)} module(s), "
          f"{count('concept')} concept(s), {count('role')} role(s), "
          f"{count('individual')} individual(s)" + ("" if COMPLETE else " (partial run)"))
    if unsupported:
        print(f"  note: {unsupported} invariant check(s) on individuals go beyond "
              f"`self.<property> <op> <literal>` and wait for WMX (ADR 0002)")
    if reg.unchecked_units:
        print(f"  note: {reg.unchecked_units} unit(s) not checked - the {CORE_MODULE} unit "
              f"catalogue is not part of this run")
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
