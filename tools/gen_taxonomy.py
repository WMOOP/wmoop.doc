#!/usr/bin/env python3
"""Keep the Mermaid diagrams in docs/06-domain-taxonomy.md in sync with the model.

Sources of truth
  model/taxonomy.yaml     clusters, domains, status, planned/candidate depends_on
  model/**/*.wml.yaml     the `module:` headers - the real, seeded dependency edges

Outputs (rewritten in place between `<!-- GEN:<name> START/END -->` markers in the doc)
  cluster-map   containment: clusters as subgraphs, domains inside, colour = status
  dep-graph     dependency: `A --> B` reads "A depends on B"; solid = declared by a
                seeded module's header, dashed = planned/candidate

Usage
  python tools/gen_taxonomy.py            regenerate the doc in place
  python tools/gen_taxonomy.py --check    CI gate: exit 1 if the doc is stale

Either mode first checks the registry against the model (acyclic, every seeded domain's
`depends_on` equals its module header's) and refuses to draw an inconsistent picture.

Needs Python 3.9+ and PyYAML.
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("gen_taxonomy.py needs PyYAML: pip install pyyaml")

DEFAULT_ROOT = Path(__file__).resolve().parent.parent

# status -> (emoji in the node label, Mermaid class). \U0001F7E2 green, \U0001F7E1 yellow, ⚪ white.
STATUS = {
    "seeded": ("\U0001F7E2", "seed"),
    "planned": ("\U0001F7E1", "plan"),
    "candidate": ("⚪", "cand"),
}
CLASS_DEFS = (
    "classDef seed fill:#1b7f3b,stroke:#0d5024,color:#fff;",
    "classDef plan fill:#b8860b,stroke:#7a5a07,color:#fff;",
    "classDef cand fill:#5a6472,stroke:#3a414b,color:#fff;",
)

# The unnumbered, un-boxed cluster drawn at the top of the cluster map.
FOUNDATION = "foundation"
# Every module depends on core; ignore it when comparing registry and header edges.
IMPLICIT_DEPS = frozenset({"core"})
# Mermaid keywords that cannot be used as bare node ids.
RESERVED_IDS = frozenset({"end", "graph", "subgraph", "flowchart", "direction", "class",
                          "classdef", "style", "linkstyle", "click", "default"})
ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")


class TaxonomyError(Exception):
    """Carries every problem found, one per entry, so a contributor can fix them in one pass."""

    def __init__(self, problems: list[str]):
        super().__init__("\n".join(problems))
        self.problems = problems


# --------------------------------------------------------------------------- loading

def load_yaml(path: Path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise TaxonomyError([f"{path.name}: cannot read: {exc}"]) from exc


def load_headers(model_dir: Path, root: Path) -> tuple[dict, list[str]]:
    """Map module id -> {"path", "depends_on"} from every `module:` header under model/.

    Files without a `module:` header (e.g. transport/roles.wml.yaml, a continuation file)
    are skipped.
    """
    headers: dict[str, dict] = {}
    problems: list[str] = []
    for path in sorted(model_dir.rglob("*.wml.yaml")):
        rel = path.relative_to(root).as_posix()
        doc = load_yaml(path)
        header = doc.get("module") if isinstance(doc, dict) else None
        if not isinstance(header, dict) or "id" not in header:
            continue
        deps = []
        for dep in header.get("depends_on") or []:
            name = dep.get("module") if isinstance(dep, dict) else dep
            if isinstance(name, str):
                deps.append(name)
            else:
                problems.append(f"{rel}: depends_on entry {dep!r} has no module id")
        if header["id"] in headers:
            problems.append(f"{rel}: module {header['id']} is also declared in "
                            f"{headers[header['id']]['path']}")
            continue
        headers[header["id"]] = {"path": rel, "depends_on": deps}
    return headers, problems


# ------------------------------------------------------------------------ validation

def check_registry(reg) -> list[str]:
    """Structural checks on model/taxonomy.yaml alone."""
    problems: list[str] = []
    if not isinstance(reg, dict) or not isinstance(reg.get("clusters"), list) \
            or not isinstance(reg.get("domains"), list):
        return ["taxonomy.yaml: expected top-level `clusters:` and `domains:` lists"]

    cluster_ids: set[str] = set()
    for c in reg["clusters"]:
        cid = c.get("id") if isinstance(c, dict) else None
        if not isinstance(cid, str) or not isinstance(c.get("label"), str):
            problems.append(f"taxonomy.yaml: cluster {c!r} needs a string `id` and `label`")
        elif cid in cluster_ids:
            problems.append(f"taxonomy.yaml: duplicate cluster id {cid!r}")
        else:
            cluster_ids.add(cid)

    domain_ids: set[str] = set()
    modules: set[str] = set()
    for d in reg["domains"]:
        did = d.get("id") if isinstance(d, dict) else None
        if not isinstance(did, str) or not ID_RE.match(did) or did in RESERVED_IDS:
            problems.append(f"taxonomy.yaml: domain id {did!r} must match {ID_RE.pattern} "
                            f"and not be a Mermaid keyword")
            continue
        if did in domain_ids:
            problems.append(f"taxonomy.yaml: duplicate domain id {did!r}")
        domain_ids.add(did)
        module = d.setdefault("module", f"wmoop.{did}")
        if module in modules:
            problems.append(f"taxonomy.yaml: domain {did!r}: module {module!r} is used twice")
        modules.add(module)
        if d.get("cluster") not in cluster_ids:
            problems.append(f"taxonomy.yaml: domain {did!r}: unknown cluster {d.get('cluster')!r}")
        if d.get("status") not in STATUS:
            problems.append(f"taxonomy.yaml: domain {did!r}: status {d.get('status')!r} "
                            f"is not one of {', '.join(STATUS)}")
        if not isinstance(d.setdefault("depends_on", []), list):
            problems.append(f"taxonomy.yaml: domain {did!r}: depends_on must be a list")
    if problems:
        return problems  # the checks below assume well-formed domains

    for d in reg["domains"]:
        for dep in d["depends_on"]:
            if dep not in domain_ids:
                problems.append(f"taxonomy.yaml: domain {d['id']!r} depends_on unknown domain {dep!r}")
            elif dep == d["id"]:
                problems.append(f"taxonomy.yaml: domain {d['id']!r} depends on itself")
    for cid in cluster_ids:
        if not any(d["cluster"] == cid for d in reg["domains"]):
            problems.append(f"taxonomy.yaml: cluster {cid!r} has no domains")

    graph = reg.get("dependency_graph")
    if graph is not None:
        if not isinstance(graph, list) or len(set(graph)) != len(graph):
            problems.append("taxonomy.yaml: dependency_graph must be a list without duplicates")
        else:
            problems += [f"taxonomy.yaml: dependency_graph lists unknown domain {g!r}"
                         for g in graph if g not in domain_ids]
    return problems


def resolve_edges(reg, headers: dict) -> tuple[dict[str, list[str]], list[str]]:
    """Compare the registry with the module headers; return (domain id -> its edges, problems).

    A seeded domain's edges come from its module header - the real model - so the diagram
    can never draw an edge the model does not have. Everything else uses the registry.
    """
    problems: list[str] = []
    by_id = {d["id"]: d for d in reg["domains"]}
    module_to_id = {d["module"]: d["id"] for d in reg["domains"]}
    declared: dict[str, list[str]] = {}

    for module, h in headers.items():
        if module not in module_to_id:
            problems.append(f"{h['path']}: declares module {module!r}, which is not in "
                            f"model/taxonomy.yaml - register it as a domain")
            continue
        deps = []
        for dep in h["depends_on"]:
            if dep in module_to_id:
                deps.append(module_to_id[dep])
            else:
                problems.append(f"{h['path']}: {module} depends_on {dep!r}, which is not in "
                                f"model/taxonomy.yaml")
        declared[module_to_id[module]] = deps

    edges: dict[str, list[str]] = {}
    for did, d in by_id.items():
        if d["status"] != "seeded":
            if did in declared:
                problems.append(f"domain {did!r} has a module header ({headers[d['module']]['path']}) "
                                f"but status {d['status']!r} in model/taxonomy.yaml - set it to 'seeded'")
            edges[did] = d["depends_on"]
            continue
        if did not in declared:
            problems.append(f"domain {did!r} is 'seeded' but no model/**/*.wml.yaml declares "
                            f"module {d['module']!r} - add the module or fix its status")
            continue
        registry_deps = set(d["depends_on"]) - IMPLICIT_DEPS
        header_deps = set(declared[did]) - IMPLICIT_DEPS
        if registry_deps != header_deps:
            problems.append(
                f"domain {did!r}: depends_on in model/taxonomy.yaml disagrees with the module "
                f"header in {headers[d['module']]['path']}\n"
                f"      registry: {', '.join(d['depends_on']) or '(none)'}\n"
                f"      header:   {', '.join(declared[did]) or '(none)'}\n"
                f"      fix the registry (the header is the truth) or the header")
        edges[did] = declared[did]
    return edges, problems


def find_cycle(edges: dict[str, list[str]]) -> list[str] | None:
    """Return one dependency cycle as [a, b, ..., a], or None (Invariant 5)."""
    state: dict[str, int] = {}  # absent = unseen, 1 = on the current path, 2 = done
    path: list[str] = []

    def visit(node: str) -> list[str] | None:
        state[node] = 1
        path.append(node)
        for dep in edges.get(node, []):
            if state.get(dep) == 1:
                return path[path.index(dep):] + [dep]
            if dep not in state and (cycle := visit(dep)):
                return cycle
        path.pop()
        state[node] = 2
        return None

    for node in edges:
        if node not in state and (cycle := visit(node)):
            return cycle
    return None


def featured_domains(reg, edges: dict[str, list[str]]) -> tuple[list[str], list[str]]:
    """Domains drawn in the dependency graph, in order, plus problems with that selection."""
    problems: list[str] = []
    featured = reg.get("dependency_graph") or [d["id"] for d in reg["domains"]]
    shown = set(featured)
    for d in reg["domains"]:
        if d["status"] == "seeded" and d["id"] not in shown:
            problems.append(f"taxonomy.yaml: seeded domain {d['id']!r} must be listed in dependency_graph")
    for did in featured:
        for dep in edges.get(did, []):
            if dep not in shown:
                problems.append(f"taxonomy.yaml: dependency_graph lists {did!r} but not its "
                                f"dependency {dep!r} - add it so no edge is hidden")
    return featured, problems


# -------------------------------------------------------------------------- rendering

def roman(n: int) -> str:
    out = ""
    for value, numeral in ((10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= value:
            out += numeral
            n -= value
    return out


def node(d) -> str:
    emoji, cls = STATUS[d["status"]]
    return f'{d["id"]}["{d["id"]} {emoji}"]:::{cls}'


def fence(lines: list[str]) -> str:
    return "```mermaid\n" + "\n".join(lines) + "\n```\n"


def render_cluster_map(reg) -> str:
    domains = reg["domains"]
    lines = ["flowchart TB"]
    flat = [d for d in domains if d["cluster"] == FOUNDATION]
    if flat:
        lines += [f"  {node(d)}" for d in flat] + [""]
    numbered = [c for c in reg["clusters"] if c["id"] != FOUNDATION]
    for n, cluster in enumerate(numbered, start=1):
        members = [d for d in domains if d["cluster"] == cluster["id"]]
        label = cluster["label"].replace('"', "#quot;")
        lines.append(f'  subgraph {roman(n)}["{roman(n)} · {label}"]')
        if len(members) > 1:
            lines.append("    direction LR")
        lines += [f"    {node(d)}" for d in members]
        lines.append("  end")
    return fence(lines + [""] + [f"  {c}" for c in CLASS_DEFS])


def render_dep_graph(reg, edges: dict[str, list[str]], featured: list[str]) -> str:
    by_id = {d["id"]: d for d in reg["domains"]}
    lines = ["flowchart LR"] + [f"  {node(by_id[f])}" for f in featured]
    for seeded, comment, arrow in (
        (True, "%% seeded edges (from the modules' depends_on headers)", "-->"),
        (False, "%% planned / candidate edges", "-.->"),
    ):
        pairs = [(a, b) for a in featured if (by_id[a]["status"] == "seeded") == seeded
                 for b in edges[a]]
        if pairs:
            lines += ["", f"  {comment}"] + [f"  {a} {arrow} {b}" for a, b in pairs]
    return fence(lines + [""] + [f"  {c}" for c in CLASS_DEFS])


def splice(text: str, name: str, block: str) -> str:
    """Replace what lies between the GEN:<name> START and END marker lines with `block`."""
    pattern = re.compile(
        rf"^<!-- GEN:{re.escape(name)} START[^\n]*-->\n(?P<body>.*?)^<!-- GEN:{re.escape(name)} END -->$",
        re.S | re.M)
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise TaxonomyError([f"doc: expected exactly one `<!-- GEN:{name} START -->` ... "
                             f"`<!-- GEN:{name} END -->` pair, found {len(matches)}"])
    m = matches[0]
    return text[:m.start("body")] + block + text[m.end("body"):]


# ------------------------------------------------------------------------------ main

def generate(root: Path) -> tuple[Path, str, str, str]:
    """Return (doc path, doc newline style, current doc text, regenerated doc text), \\n-normalised."""
    reg = load_yaml(root / "model" / "taxonomy.yaml")
    problems = check_registry(reg)
    if problems:
        raise TaxonomyError(problems)

    headers, problems = load_headers(root / "model", root)
    edges, more = resolve_edges(reg, headers)
    problems += more
    if not problems and (cycle := find_cycle(edges)):
        problems.append("dependency cycle (Invariant 5): " + " -> ".join(cycle))
    featured, more = featured_domains(reg, edges)
    problems += more
    if problems:
        raise TaxonomyError(problems)

    doc = root / "docs" / "06-domain-taxonomy.md"
    try:
        raw = doc.read_bytes().decode("utf-8")
    except OSError as exc:
        raise TaxonomyError([f"{doc.name}: cannot read: {exc}"]) from exc
    newline = "\r\n" if "\r\n" in raw else "\n"  # a Windows checkout may have CRLF
    current = raw.replace("\r\n", "\n")
    new = splice(current, "cluster-map", render_cluster_map(reg))
    new = splice(new, "dep-graph", render_dep_graph(reg, edges, featured))
    return doc, newline, current, new


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):  # keep the status emoji printable on any console
        stream.reconfigure(errors="backslashreplace")
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="do not write; exit 1 if the doc is stale or the registry is inconsistent")
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    try:
        doc, newline, current, new = generate(args.root.resolve())
    except TaxonomyError as exc:
        print(f"gen_taxonomy: cannot generate - {len(exc.problems)} problem(s) in the registry, "
              f"the model or the doc:\n", file=sys.stderr)
        for problem in exc.problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    rel = doc.relative_to(args.root.resolve()).as_posix()
    if new == current:
        print(f"gen_taxonomy: {rel} is up to date")
        return 0
    if args.check:
        print(f"gen_taxonomy: {rel} is stale - its diagrams do not match model/taxonomy.yaml "
              f"and the module headers.\nRun `python tools/gen_taxonomy.py` and commit the result.\n",
              file=sys.stderr)
        sys.stderr.writelines(difflib.unified_diff(
            current.splitlines(keepends=True), new.splitlines(keepends=True),
            fromfile=f"{rel} (committed)", tofile=f"{rel} (generated)"))
        return 1
    doc.write_bytes(new.replace("\n", newline).encode("utf-8"))
    print(f"gen_taxonomy: updated {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
