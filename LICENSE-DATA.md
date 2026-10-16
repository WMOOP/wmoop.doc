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

## Full text & attribution

- Apache-2.0: see [`LICENSE`](LICENSE).
- CC-BY-4.0: <https://creativecommons.org/licenses/by/4.0/legalcode>. A copy will be added to the
  repository as `LICENSE-CC-BY-4.0.txt`.

**Attribution string (suggested):**
> "World Model data from the WMOOP project (https://github.com/WMOOP), licensed CC-BY-4.0."

## Third-party data

Facts imported or derived from external sources (Wikidata, GBIF, GeoNames, …) remain subject to
**their** licences. Record each source in the concept's `provenance` and respect the attribution
and share-alike terms of that source. Never import data whose licence is incompatible with
redistribution.
