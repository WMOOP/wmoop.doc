#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
yaml_to_xml.py - project the canonical WML (YAML) to the WML-in-XML serialization.

The YAML under ``model/**`` is the single source of truth (Invariant 1); the XML is a
*generated projection*, exactly like the OWL/JSON-Schema/Protobuf projections in
docs/03-architecture.md Sec 2.1. This script merges every ``*.wml.yaml`` file of a module
into ONE ``<module>`` document and writes ``schema/examples/<module-id>.wml.xml``, with
child elements in the order the XSD (``schema/wml.xsd``) requires. The output is
deterministic, so it doubles as a CI diff-guard.

Usage:
    python schema/yaml_to_xml.py                 # (re)generate schema/examples/*.wml.xml
    python schema/yaml_to_xml.py --check         # fail (exit 1) if committed XML is stale
    python schema/yaml_to_xml.py --out DIR       # write elsewhere
"""
from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
MODEL = REPO / "model"
EXAMPLES = HERE / "examples"
NS = "https://wmoop.org/wml/1"
ET.register_namespace("", NS)


def _die(msg: str):
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(2)


def load_yaml(path: Path):
    try:
        import yaml
    except ImportError:
        _die("PyYAML is required: pip install pyyaml")
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _s(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def el(parent, tag: str, attrs: dict | None = None, text: str | None = None):
    e = ET.SubElement(parent, f"{{{NS}}}{tag}")
    for k, v in (attrs or {}).items():
        if v is not None:
            e.set(k, _s(v))
    if text is not None:
        e.text = text
    return e


# --------------------------------------------------------------------------- #
# per-node builders (children emitted in XSD sequence order)                   #
# --------------------------------------------------------------------------- #
def add_provenance(parent, node: dict):
    for pv in node.get("provenance", []) or []:
        el(parent, "provenance", {
            "source": pv.get("source"), "kind": pv.get("kind"), "ref": pv.get("ref"),
            "note": pv.get("note"), "url": pv.get("url"), "retrieved": pv.get("retrieved"),
            "doi": pv.get("doi"), "isbn": pv.get("isbn"), "author": pv.get("author"),
            "title": pv.get("title"), "year": pv.get("year"), "type": pv.get("type"),
            "locator": pv.get("locator"),
        })


def add_labels(parent, node: dict):
    labels = node.get("labels")
    if not labels:
        return
    g = el(parent, "labels")
    for kind, entries in labels.items():
        grp = el(g, "group", {"kind": kind})
        for entry in entries:
            el(grp, "label", {"lang": entry.get("lang")}, text=entry.get("value"))


def add_constraints(parent, cons: dict | None):
    if not cons:
        return
    attrs = {k: cons.get(k) for k in
             ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
              "multipleOf", "minLength", "maxLength", "pattern", "format")}
    c = el(parent, "constraints", attrs)
    for v in cons.get("enum", []) or []:
        el(c, "enum", text=_s(v))


def add_property(parent, p: dict):
    e = el(parent, "property", {
        "id": p.get("id"), "name": p.get("name"), "type": p.get("type"),
        "unit": p.get("unit"), "cardinality": p.get("cardinality"),
        "required": p.get("required"),
        "default": p.get("default") if "default" in p else None,
    })
    el(e, "definition", text=(p.get("definition") or "").strip())
    add_labels(e, p)
    add_constraints(e, p.get("constraints"))
    add_provenance(e, p)


def add_relation(parent, r: dict):
    e = el(parent, "relation", {
        "id": r.get("id"), "name": r.get("name"), "target": r.get("target"),
        "cardinality": r.get("cardinality"), "rel": r.get("rel"), "inverse": r.get("inverse"),
    })
    if r.get("definition"):
        el(e, "definition", text=r["definition"].strip())
    add_provenance(e, r)


def add_datatype(parent, d: dict):
    e = el(parent, "datatype", {
        "id": d.get("id"), "name": d.get("name"), "base": d.get("base"), "unit": d.get("unit"),
    })
    el(e, "definition", text=(d.get("definition") or "").strip())
    add_labels(e, d)
    add_constraints(e, d.get("constraints"))
    add_provenance(e, d)


def add_enumeration(parent, en: dict):
    e = el(parent, "enumeration", {"id": en.get("id"), "name": en.get("name")})
    el(e, "definition", text=(en.get("definition") or "").strip())
    add_labels(e, en)
    add_provenance(e, en)
    for v in en.get("values", []) or []:
        ve = el(e, "value", {"id": v.get("id"), "name": v.get("name")})
        el(ve, "definition", text=(v.get("definition") or "").strip())


def add_interface(parent, itf: dict):
    e = el(parent, "interface", {"id": itf.get("id"), "name": itf.get("name")})
    el(e, "definition", text=(itf.get("definition") or "").strip())
    add_labels(e, itf)
    add_provenance(e, itf)
    for op in itf.get("operations", []) or []:
        oe = el(e, "operation", {"name": op.get("name"), "returns": op.get("returns")})
        for prm in op.get("params", []) or []:
            el(oe, "param", {"name": prm.get("name"), "type": prm.get("type")})


def add_concept(parent, c: dict):
    e = el(parent, "concept", {
        "id": c.get("id"), "name": c.get("name"), "kind": c.get("kind"), "extends": c.get("extends"),
    })
    el(e, "definition", text=(c.get("definition") or "").strip())
    add_labels(e, c)
    add_provenance(e, c)
    for ca in c.get("classified_as", []) or []:
        el(e, "classifiedAs", {"scheme": ca.get("scheme"), "value": ca.get("value")})
    for impl in c.get("implements", []) or []:
        el(e, "implements", {"ref": impl})
    for p in c.get("properties", []) or []:
        add_property(e, p)
    for ov in c.get("property_overrides", []) or []:
        oe = el(e, "propertyOverride", {
            "property": ov.get("property"),
            "default": ov.get("default") if "default" in ov else None,
        })
        add_constraints(oe, ov.get("constraints"))
    for inv in c.get("invariants", []) or []:
        ie = el(e, "invariant", {"id": inv.get("id")})
        el(ie, "expr", text=(inv.get("expr") or "").strip())
        if inv.get("message"):
            el(ie, "message", text=inv["message"].strip())
    for r in c.get("relations", []) or []:
        add_relation(e, r)


def add_role(parent, r: dict):
    e = el(parent, "role", {
        "id": r.get("id"), "name": r.get("name"), "playedBy": r.get("played_by"),
        "context": r.get("context"), "cardinalityPerPlayer": r.get("cardinality_per_player"),
    })
    el(e, "definition", text=(r.get("definition") or "").strip())
    add_labels(e, r)
    add_provenance(e, r)
    for cap in r.get("capabilities", []) or []:
        el(e, "capability", {"ref": cap})
    for p in r.get("properties", []) or []:
        add_property(e, p)
    for rel in r.get("relations", []) or []:
        add_relation(e, rel)


def add_individual(parent, ind: dict):
    e = el(parent, "individual", {
        "id": ind.get("id"), "name": ind.get("name"), "instanceOf": ind.get("instance_of"),
    })
    if ind.get("definition"):
        el(e, "definition", text=ind["definition"].strip())
    add_labels(e, ind)
    for prop, val in (ind.get("values") or {}).items():
        el(e, "value", {"property": prop}, text=_s(val))
    add_provenance(e, ind)


# --------------------------------------------------------------------------- #
# module assembly                                                              #
# --------------------------------------------------------------------------- #
def ordered_files(files: list[Path]) -> list[Path]:
    """Header-bearing files first (sorted), then fragments (sorted) - deterministic."""
    headers, frags = [], []
    for f in sorted(files):
        data = load_yaml(f)
        (headers if isinstance(data, dict) and "module" in data else frags).append(f)
    return headers + frags


def build_module_xml(module_id: str, files: list[Path]) -> ET.ElementTree:
    header = None
    sections: dict[str, list] = {k: [] for k in
                                 ("datatypes", "enumerations", "interfaces", "concepts", "roles", "individuals")}
    for f in ordered_files(files):
        data = load_yaml(f) or {}
        if "module" in data and header is None:
            header = data["module"]
        for key in sections:
            sections[key].extend(data.get(key, []) or [])
    if header is None:
        _die(f"module group '{module_id}' has no header file")

    root = ET.Element(f"{{{NS}}}module", {
        "id": header["id"], "version": _s(header["version"]), "title": header["title"],
    })
    for dep in header.get("depends_on", []) or []:
        el(root, "dependsOn", {"module": dep.get("module"), "version": dep.get("version")})

    if sections["datatypes"]:
        w = el(root, "datatypes")
        for d in sections["datatypes"]:
            add_datatype(w, d)
    if sections["enumerations"]:
        w = el(root, "enumerations")
        for en in sections["enumerations"]:
            add_enumeration(w, en)
    if sections["interfaces"]:
        w = el(root, "interfaces")
        for itf in sections["interfaces"]:
            add_interface(w, itf)
    if sections["concepts"]:
        w = el(root, "concepts")
        for c in sections["concepts"]:
            add_concept(w, c)
    if sections["roles"]:
        w = el(root, "roles")
        for r in sections["roles"]:
            add_role(w, r)
    if sections["individuals"]:
        w = el(root, "individuals")
        for ind in sections["individuals"]:
            add_individual(w, ind)

    ET.indent(root, space="  ")
    return ET.ElementTree(root)


def group_modules() -> dict[str, list[Path]]:
    """Group *.wml.yaml by owning module id (via header; fragments inherit their dir's header)."""
    by_dir: dict[Path, list[Path]] = {}
    for f in sorted(MODEL.rglob("*.wml.yaml")):
        if any(p.startswith("_") for p in f.relative_to(MODEL).parts):
            continue
        by_dir.setdefault(f.parent, []).append(f)
    groups: dict[str, list[Path]] = {}
    for _dir, files in by_dir.items():
        mid = None
        for f in files:
            data = load_yaml(f)
            if isinstance(data, dict) and isinstance(data.get("module"), dict):
                mid = data["module"]["id"]
                break
        if mid is None:
            _die(f"directory {_dir} has WML files but no module header")
        groups.setdefault(mid, []).extend(files)
    return groups


def serialize(tree: ET.ElementTree) -> str:
    body = ET.tostring(tree.getroot(), encoding="unicode")
    header = ('<?xml version="1.0" encoding="UTF-8"?>\n'
              "<!-- GENERATED from model/**/*.wml.yaml by schema/yaml_to_xml.py - DO NOT EDIT.\n"
              "     The YAML is the single source of truth; regenerate with:\n"
              "       python schema/yaml_to_xml.py -->\n")
    return header + body + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Project WML YAML to WML-in-XML.")
    ap.add_argument("--check", action="store_true", help="fail if committed XML is stale")
    ap.add_argument("--out", default=str(EXAMPLES), help="output directory")
    args = ap.parse_args(argv)
    out = Path(args.out)

    groups = group_modules()
    stale, written = [], []
    out.mkdir(parents=True, exist_ok=True)
    for mid, files in sorted(groups.items()):
        tree = build_module_xml(mid, files)
        text = serialize(tree)
        target = out / f"{mid}.wml.xml"
        current = target.read_text(encoding="utf-8") if target.exists() else None
        if args.check:
            if current != text:
                stale.append(target.relative_to(REPO).as_posix() if target.is_relative_to(REPO) else str(target))
        else:
            target.write_text(text, encoding="utf-8", newline="\n")
            written.append(target)

    if args.check:
        if stale:
            print("STALE XML projections (run: python schema/yaml_to_xml.py):")
            for s in stale:
                print(f"  - {s}")
            return 1
        print(f"OK - {len(groups)} XML projection(s) are up to date")
        return 0

    for w in written:
        rel = w.relative_to(REPO).as_posix() if w.is_relative_to(REPO) else str(w)
        print(f"wrote {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
