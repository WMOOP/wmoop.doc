# Data & Documentation License

WMOOP is **dual-licensed** so that each kind of artifact gets the licence that fits it:

| Artifact | Licence | SPDX id |
|----------|---------|---------|
| **Code** — tooling, generators, examples, and generated language bindings | Apache License 2.0 | `Apache-2.0` ([`LICENSE`](LICENSE)) |
| **Model data & documentation** — the WML model files in `model/`, and the prose in `docs/` and the Markdown documents in this repo | Creative Commons Attribution 4.0 International | `CC-BY-4.0` |

## Why CC-BY-4.0 for the model and docs

The World Model is a **knowledge base**, not a program. It is meant to be copied, remixed,
translated and embedded in other datasets and products as widely as possible. CC-BY-4.0:

- is the standard, well-understood licence for open knowledge (it is what Wikidata's *content*
  contributors and many open-data projects use);
- requires only **attribution**, which aligns exactly with WMOOP's provenance rule (Invariant 4:
  every fact is sourced and creditable);
- is interoperable with most open-data sources WMOOP may cite or import.

> **CC0 was considered** (maximal reuse, no attribution burden) but rejected for v0: because WMOOP
> asks every contributor to *cite their sources*, requiring downstream users to *credit WMOOP* in
> turn is consistent and encourages the citation culture the project depends on. This choice may be
> revisited through the RFC process in [GOVERNANCE.md](GOVERNANCE.md).

## Attribution is required — name the source repository

CC-BY-4.0 lets you copy, remix and redistribute the model data and documentation **only on the
condition that you give credit**. For WMOOP, that credit **must identify the project and link back
to its canonical source repository**, so anyone who receives your work can trace it to the original.
This is the attribution the Licensor requires under CC-BY-4.0 §3(a), and it mirrors Invariant 4 —
every fact is sourced and creditable.

Every published use — a paper, dataset, product, slide, course, derived model, or generated language
binding — must carry, in a place and form reasonable for the medium:

1. the name **WMOOP World Model** (or "the WMOOP project");
2. a link to the **canonical source repository**: <https://github.com/WMOOP/wmoop.doc>;
3. the licence, **CC-BY-4.0**, with its link;
4. if you changed the material, a note that changes were made (and ideally what).

**Attribution string (copy-paste):**
> "World Model data from the WMOOP project — source: https://github.com/WMOOP/wmoop.doc — licensed
> CC-BY-4.0. Changes were made."
>
> *(Drop the final sentence if you redistribute the material unmodified.)*

## Full text

- Apache-2.0: see [`LICENSE`](LICENSE).
- CC-BY-4.0: <https://creativecommons.org/licenses/by/4.0/legalcode>. A copy will be added to the
  repository as `LICENSE-CC-BY-4.0.txt`.

## Third-party data

Facts imported or derived from external sources (Wikidata, GBIF, GeoNames, …) remain subject to
**their** licences. Record each source in the concept's `provenance` and respect the attribution
and share-alike terms of that source. Never import data whose licence is incompatible with
redistribution.
