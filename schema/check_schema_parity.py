#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
check_schema_parity.py - the WML schema-mirror oracle (S4, durable fix).

`schema/wml.schema.json` (JSON Schema) and `schema/wml.xsd` (XSD) are two
serializations of ONE grammar and MUST stay in agreement. They are hand-authored
(the XSD is an XML-idiom projection of the JSON Schema), so without an automated
gate they drift silently - a new enum value, field, or section added to one side
and forgotten on the other. `check_canonical.py` guards freshness against the
canonical `WMOOP/wmoop.json` repo; this script guards the two LOCAL mirrors
against EACH OTHER, catching drift in either direction.

Rather than regenerate `wml.xsd` from `wml.schema.json` (which would erase two
intentional, documented differences - see BY_DESIGN below), this is the *validate*
branch of the S4 durable fix: it mechanically verifies that everything which MUST
match does, and fails CI (exit 1) on any unaccounted-for divergence.

It checks four things, plus a coverage guard so NEW constructs cannot slip through:

  1. Enum parity   - every controlled vocabulary (enum / const) present on one
                     side is present on the other (compared by value-set, so it is
                     name-agnostic and auto-covers new enums).
  2. Field parity  - each corresponding object type has the same field set and the
                     same required-field set (JSON properties <-> XSD attributes +
                     child elements, under a snake_case<->camelCase / plural<->
                     singular rename map).
  3. Section parity- the module's top-level sections (concepts, roles, ...,
                     schemes, associations) and header fields agree.
  4. Coverage      - every JSON object `$def` and every named XSD complexType is
                     either mapped above or in an explicit, reasoned ignore-list;
                     an unmapped new type FAILS (this is what makes drift of a new
                     construct impossible to miss).

Exit 0 = schemas in agreement; 1 = at least one divergence.

Usage:
    python schema/check_schema_parity.py
    python schema/check_schema_parity.py --verbose
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# The only XML we parse is our own committed `wml.xsd` (trusted, version-controlled),
# so stdlib ElementTree is safe here and matches schema/yaml_to_xml.py. Prefer the
# hardened parser when it happens to be installed; fall back otherwise (no new dep).
try:
    from defusedxml import ElementTree as ET  # type: ignore
except ImportError:
    import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
SCHEMA_FILE = HERE / "wml.schema.json"
XSD_FILE = HERE / "wml.xsd"

XS = "http://www.w3.org/2001/XMLSchema"


# --------------------------------------------------------------------------- #
# Correspondence map (JSON $def  <->  XSD complexType) and the rename rules.   #
# --------------------------------------------------------------------------- #

# Named JSON object $def  ->  named XSD complexType.
TYPE_MAP = {
    "provenanceEntry": "provenance",
    "constraints": "constraints",
    "classifiedAsEntry": "classifiedAs",
    "scheme": "scheme",
    "datatype": "datatype",
    "enumeration": "enumeration",
    "interface": "interface",
    "property": "property",
    "propertyOverride": "propertyOverride",
    "invariant": "invariant",
    "relation": "relation",
    "concept": "concept",
    "role": "role",
    "individual": "individual",
    "participant": "participant",
    "association": "association",
}

# Inline JSON object schemas (reached by a dotted path under $defs) -> XSD complexType.
INLINE_MAP = {
    "dependency": "module.properties.depends_on.items",
    "enumValue": "enumeration.properties.values.items",
    "operation": "interface.properties.operations.items",
    "param": "interface.properties.operations.items.properties.params.items",
}

# JSON $defs with no 1:1 XSD object peer, and why (so coverage stays honest).
IGNORED_JSON_DEFS = {
    "moduleQName", "typeQName", "memberQName", "primitive", "typeRef", "returnsRef",
    "semver", "semverRange", "cardinality", "typeName", "memberName", "nonEmptyString",
    "provenanceList",   # array wrapper over provenanceEntry (no own fields)
    "labels",           # map-of-lists vs XSD group/label element tree (representational)
    "module",           # header + sections; checked by section parity, not field parity
}

# XSD complexTypes with no 1:1 JSON object peer, and why.
IGNORED_XSD_TYPES = {
    "label", "labelGroup", "labels",   # labels representation (map vs element tree)
    "implementsRef", "capabilityRef",  # JSON models these as plain QName-string lists
    "individualValue",                 # per-value unit/source: BY_DESIGN #2 below
}

# snake_case / plural JSON key  ->  XSD attribute-or-element spelling.
RENAME = {
    "depends_on": "dependsOn",
    "played_by": "playedBy",
    "cardinality_per_player": "cardinalityPerPlayer",
    "instance_of": "instanceOf",
    "classified_as": "classifiedAs",
    "property_overrides": "propertyOverride",
    "properties": "property",
    "relations": "relation",
    "operations": "operation",
    "params": "param",
    "invariants": "invariant",
    "participants": "participant",
    "capabilities": "capability",
    "values": "value",
}

# Two differences that are intentional and documented (schema/README.md S4 note);
# they are NOT drift and are excluded from the checks.
BY_DESIGN = [
    "XSD validates a complete merged <module> document; JSON validates per-file fragments.",
    "individualValue carries per-value unit/source in the XSD; the JSON side's per-value "
    "provenance is a planned enrichment.",
]


def norm_field(key: str) -> str:
    return RENAME.get(key, key)


# --------------------------------------------------------------------------- #
# JSON side                                                                    #
# --------------------------------------------------------------------------- #
def load_json():
    return json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))


def json_value_sets(node, acc: set) -> None:
    """Collect every enum (list) and const (scalar) value-set in the JSON Schema."""
    if isinstance(node, dict):
        if isinstance(node.get("enum"), list):
            acc.add(frozenset(str(v) for v in node["enum"]))
        if "const" in node and not isinstance(node["const"], (list, dict)):
            acc.add(frozenset([str(node["const"])]))
        for v in node.values():
            json_value_sets(v, acc)
    elif isinstance(node, list):
        for v in node:
            json_value_sets(v, acc)


def json_obj_fields(obj: dict):
    """(normalized field-name set, normalized required set) for a JSON object schema."""
    fields = {norm_field(k) for k in (obj.get("properties") or {})}
    required = {norm_field(k) for k in (obj.get("required") or [])}
    return fields, required


def resolve_path(schema: dict, dotted: str):
    node = schema["$defs"]
    for part in dotted.split("."):
        node = node[part]
    return node


# --------------------------------------------------------------------------- #
# XSD side                                                                     #
# --------------------------------------------------------------------------- #
def load_xsd():
    return ET.parse(XSD_FILE).getroot()


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def xsd_enum_sets(root) -> set:
    out = set()
    for st in root.findall(f".//{{{XS}}}simpleType"):
        vals = [e.get("value") for e in st.findall(f".//{{{XS}}}enumeration")]
        if vals:
            out.add(frozenset(vals))
    return out


def xsd_complex_types(root) -> dict:
    types = {}
    for ct in root.findall(f".//{{{XS}}}complexType"):
        name = ct.get("name")
        if name:
            types[name] = ct
    # the module document is an element with an inline complexType
    mod = root.find(f".//{{{XS}}}element[@name='module']/{{{XS}}}complexType")
    if mod is not None:
        types["__module__"] = mod
    return types


def xsd_fields(ct):
    """(field-name set, required set) for an XSD complexType: attributes + DIRECT
    child elements (does not descend into nested inline complexTypes)."""
    fields, required = set(), set()
    # attributes (direct, or under simpleContent/extension) - no nested complexType
    # in our schema carries attributes, so a recursive scan is safe.
    for att in ct.iter(f"{{{XS}}}attribute"):
        name = att.get("name")
        if name:
            fields.add(name)
            if att.get("use") == "required":
                required.add(name)
    # direct child elements only
    def scan_particle(particle):
        for child in list(particle):
            lt = local(child.tag)
            if lt == "element" and child.get("name"):
                fields.add(child.get("name"))
                if child.get("minOccurs", "1") != "0":
                    required.add(child.get("name"))
            elif lt in ("sequence", "choice", "all"):
                scan_particle(child)
    for particle in list(ct):
        lt = local(particle.tag)
        if lt in ("sequence", "choice", "all"):
            # top-level particle: collect its DIRECT element children only
            for child in list(particle):
                clt = local(child.tag)
                if clt == "element" and child.get("name"):
                    fields.add(child.get("name"))
                    if child.get("minOccurs", "1") != "0":
                        required.add(child.get("name"))
                elif clt in ("sequence", "choice", "all"):
                    scan_particle(child)
        elif lt in ("complexContent", "simpleContent"):
            for ext in particle.iter(f"{{{XS}}}extension"):
                for sub in list(ext):
                    if local(sub.tag) in ("sequence", "choice", "all"):
                        for child in list(sub):
                            if local(child.tag) == "element" and child.get("name"):
                                fields.add(child.get("name"))
                                if child.get("minOccurs", "1") != "0":
                                    required.add(child.get("name"))
    return fields, required


# --------------------------------------------------------------------------- #
# Checks                                                                       #
# --------------------------------------------------------------------------- #
def check_parity(verbose: bool = False) -> list[str]:
    schema = load_json()
    root = load_xsd()
    xsd_types = xsd_complex_types(root)
    problems: list[str] = []
    checked = 0

    # 1. enum / vocabulary parity
    js_sets, xs_sets = set(), set()
    json_value_sets(schema, js_sets)
    xs_sets = xsd_enum_sets(root)
    for s in sorted(js_sets - xs_sets, key=lambda x: sorted(x)):
        problems.append(f"[enum] value-set {sorted(s)} is in the JSON Schema but has no XSD simpleType")
    for s in sorted(xs_sets - js_sets, key=lambda x: sorted(x)):
        problems.append(f"[enum] XSD simpleType value-set {sorted(s)} has no JSON Schema enum/const")
    if verbose:
        print(f"  enum parity: {len(js_sets & xs_sets)} shared value-set(s)")

    # 2a. named object field + required parity
    for jname, xname in TYPE_MAP.items():
        if jname not in schema["$defs"]:
            problems.append(f"[map] JSON $def '{jname}' is missing (parity map is stale)")
            continue
        if xname not in xsd_types:
            problems.append(f"[map] XSD complexType '{xname}' is missing (parity map is stale)")
            continue
        jf, jr = json_obj_fields(schema["$defs"][jname])
        xf, xr = xsd_fields(xsd_types[xname])
        for f in sorted(jf - xf):
            problems.append(f"[field] {jname}: '{f}' is in the JSON Schema but not XSD '{xname}'")
        for f in sorted(xf - jf):
            problems.append(f"[field] {xname}: '{f}' is in the XSD but not JSON '{jname}'")
        for f in sorted(jr - xr):
            problems.append(f"[required] {jname}: '{f}' is required in JSON but optional in XSD '{xname}'")
        for f in sorted(xr - jr):
            problems.append(f"[required] {xname}: '{f}' is required in XSD but optional in JSON '{jname}'")
        checked += 1

    # 2b. inline object field + required parity
    for xname, dotted in INLINE_MAP.items():
        if xname not in xsd_types:
            problems.append(f"[map] XSD complexType '{xname}' is missing (inline map is stale)")
            continue
        try:
            jnode = resolve_path(schema, dotted)
        except (KeyError, TypeError):
            problems.append(f"[map] JSON path '$defs.{dotted}' did not resolve (inline map is stale)")
            continue
        jf, jr = json_obj_fields(jnode)
        xf, xr = xsd_fields(xsd_types[xname])
        for f in sorted(jf - xf):
            problems.append(f"[field] {dotted}: '{f}' is in JSON but not XSD '{xname}'")
        for f in sorted(xf - jf):
            problems.append(f"[field] {xname}: '{f}' is in XSD but not JSON '{dotted}'")
        for f in sorted(jr - xr):
            problems.append(f"[required] {dotted}: '{f}' is required in JSON but optional in XSD '{xname}'")
        for f in sorted(xr - jr):
            problems.append(f"[required] {xname}: '{f}' is required in XSD but optional in JSON '{dotted}'")
        checked += 1

    # 3. top-level section + header parity
    root_props = set((schema.get("properties") or {}).keys())
    sections_json = {norm_field(k) for k in root_props if k != "module"}
    mod_ct = xsd_types.get("__module__")
    if mod_ct is None:
        problems.append("[section] XSD has no <module> element")
    else:
        mod_fields, _ = xsd_fields(mod_ct)
        sections_xsd = mod_fields - {"id", "version", "title", "dependsOn"}
        for s in sorted(sections_json - sections_xsd):
            problems.append(f"[section] '{s}' is a JSON root section but not an XSD module section")
        for s in sorted(sections_xsd - sections_json):
            problems.append(f"[section] '{s}' is an XSD module section but not a JSON root section")
        # module header fields
        hf, hr = json_obj_fields(schema["$defs"]["module"])
        for f in sorted(hf - mod_fields):
            problems.append(f"[section] module header '{f}' is in JSON but not the XSD module element")
        checked += 1

    # 4. coverage guards - a NEW type on either side that nobody mapped is drift.
    json_obj_defs = {
        n for n, d in schema["$defs"].items()
        if isinstance(d, dict) and (d.get("type") == "object" or "properties" in d)
    }
    accounted_json = set(TYPE_MAP) | IGNORED_JSON_DEFS
    for n in sorted(json_obj_defs - accounted_json):
        problems.append(f"[coverage] JSON object $def '{n}' is not in the parity map or ignore-list")

    accounted_xsd = set(TYPE_MAP.values()) | set(INLINE_MAP) | IGNORED_XSD_TYPES
    for n in sorted(set(xsd_types) - accounted_xsd - {"__module__"}):
        problems.append(f"[coverage] XSD complexType '{n}' is not in the parity map or ignore-list")

    if verbose:
        print(f"  field/section parity: {checked} corresponding type(s) checked")
        print(f"  by-design differences (excluded): {len(BY_DESIGN)}")
    return problems


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Check wml.schema.json <-> wml.xsd agreement (S4).")
    ap.add_argument("--verbose", action="store_true", help="print per-check summaries")
    args = ap.parse_args(argv)

    problems = check_parity(verbose=args.verbose)
    if problems:
        print(f"Schema mirrors DIVERGE - {len(problems)} issue(s) between wml.schema.json and wml.xsd:")
        for p in problems:
            print(f"  - {p}")
        print("\nReconcile the two files so the grammar stays one grammar "
              "(see schema/README.md, S4).")
        return 1
    print("OK - wml.schema.json and wml.xsd are in agreement "
          f"(enums, fields, sections; {len(BY_DESIGN)} documented by-design differences).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
