<!--
SPDX-License-Identifier: CC-BY-4.0
Part of the WMOOP project (World Map Object-Oriented Programming) — github.com/WMOOP
-->

# ADR 0001 — Classification is a scheme-aware layer over an OOP identity tree

- **Status:** **Proposed** (2026-10-18) — pending ratification. Adopting it requires (a) an **RFC + TSC ratification** for the new L0 `Scheme` construct and the WM-schema change ([GOVERNANCE.md](../../GOVERNANCE.md) §5), and (b) a **Meta-RFC + TSC supermajority** for the `ETHICS.md` §2.5 change (ETHICS §7). The edits already made to 02, ETHICS, GOVERNANCE and the roadmap are **provisional** until both gates pass.
- **Deciders:** TSC (to ratify); drafted from the D1 design review
- **Resolves:** the **D1** contradiction between [`docs/02-meta-model.md`](../../docs/02-meta-model.md) and [`ETHICS.md`](../../ETHICS.md)
- **Invariants:** I2, I3, I4, I8 (clarified, not loosened)

## Context

Two **normative** documents disagreed about what the *authored source of truth* is for
**classification**:

- `docs/02-meta-model.md` modelled it as a single **rigid identity tree**: every concrete individual
  instantiates exactly one identity-giving `Kind`, `extends` is single-parent, §2.5 declared
  "classification is crisp", and generated code bakes one scheme in as structure
  (`Tomato extends Berry`; Pluto `instance_of DwarfPlanet`).
- `ETHICS.md` §2.5 modelled it as a **scheme-aware graph**: schemes are "first-class, versioned
  objects", a concept may be classified under several at once, each sourced and dated (`asOf`), and
  "reviewers reject PRs that delete a well-sourced rival scheme".

An independent steelman + adversarial stress-test of three options — **A** (keep the OOP tree as-is),
**B** (invert to a graph source with OOP as one projection), **C** (keep the OOP tree **and** add an
additive scheme layer) — found:

- The classification machinery ETHICS requires **does not exist at fidelity today**, under any
  option: `schema/wml.schema.json`'s `classifiedAsEntry` is a bare `{scheme, value}` with no
  provenance / `asOf` / rank; `classified_as` is wired only onto `concept` (not `individual`, so
  Pluto cannot hold one); there is no first-class `Scheme` construct; `wmid` is unused on every
  seeded entity; and `model/nature` shipped an **unsourced** NCBI classification tag.
- "Keep as-is" (**A**) is therefore non-compliant with ETHICS, and once hardened **becomes** the
  hybrid.
- Full inversion (**B**) reverses the reasoned format decision in `docs/03-architecture.md` §1.2,
  makes the project's **first** generator its hardest unbuilt component (a deterministic
  scheme-selection + depth-flattening projector), and guts the authoring-based pedagogy in
  `docs/04-academic.md` (the A0–A6 ladder is built on students authoring the `extends` tree).
  GOVERNANCE already classifies a "new classification scheme" as a **MINOR, additive** change —
  evidence the project imagined schemes as additive, not as a source inversion.
- **No option removes a default privileged tree:** any idiomatic OOP output must pick one; B merely
  moves that choice into generation config.

## Decision

**Keep the OOP identity tree as the authored source for identity and code shape, and add a
first-class, sourced, dated *classification scheme* layer additively (option C). Do not invert the
source to a graph (option B) for v1.**

1. **Identity + code shape stay OOP.** The authored WML `extends` single-parent `Kind` tree remains
   the source of identity and the thing codegen maps 1:1 to idiomatic classes. 02's backbone, the
   seeded domains, and the generator plan stand.
2. **Classification becomes a first-class, additive layer.** Introduce a versioned `Scheme`
   construct + registry, and a `classifiedUnder` / enriched `classified_as` claim that carries
   **provenance, rank, `asOf` (dated), tier, and status**, attachable to **concepts, individuals,
   and roles**. A concept/individual may be classified under many schemes at once; none is deleted
   (ETHICS §2.5).
3. **Identity stays structural; current classification is a dated claim.** `extends`/`instance_of`
   remain **structural** — they give identity and the default code projection. The **authoritative
   current classification** is carried as a *separate* sourced, dated, scheme-qualified
   `classifiedUnder` claim — **not** by re-typing `instance_of`. Identity is the immutable **`wmid`**,
   which survives reclassification (Pluto keeps its `wmid`, and its identity edge, when a dated claim
   moves it from Planet to DwarfPlanet). A `Kind` supplies a principle-of-identity template.
   (Implements Invariant 8, currently unwired — see Follow-ups 1 and 3.)
4. **One default projection scheme per domain, chosen by a sourced ADR.** The generated class library
   materializes exactly one scheme per domain (unavoidable for idiomatic OOP); rival schemes ship as
   queryable annotations. NPOV lives in the **source + annotations**, not in pretending no tree is
   privileged.
5. **Taxonomy depth lives in the scheme layer.** Deep rank ladders (Linnaean, ~8 levels) are modelled
   as scheme claims (uncapped), so the `extends` spine stays shallow and the depth cap (≤ 6) is not
   under pressure.
6. **02 §2.5 is reworded** from "classification is crisp" to **"crisp within a scheme, contested
   across schemes"**, backed by the machinery above — not by wording alone.

## Sequencing

Build the **simple** concept→class generator first (emit the reference binding from WML with
constraints enforced and conformance green) **before** any scheme-aware projector. The
scheme-selection / depth-flattening projector is never on the v1 critical path.

## Consequences

- ETHICS §2.5 **will become** structurally true once Follow-up 1 (the schema enrichment) lands;
  **until then it is reconciled in prose and direction only** — the schema still has no first-class
  `Scheme` and a bare `{scheme, value}` `classified_as`. 02's tree is honestly re-scoped to
  "identity + default projection", so the two docs are reconciled rather than one defeating the other.
- **New L0 surface (roadmapped, additive):** the `Scheme` construct + registry; an enriched
  `classified_as` / `classifiedUnder` claim (provenance + rank + `asOf` + tier + status) allowed on
  concepts, individuals and roles; validator gates (every `scheme` resolves; no well-sourced rival
  scheme deleted; reclassification preserves `wmid`). Additive (GOVERNANCE MINOR scope), but each
  field is a conservative, reviewed change to the "small, fixed" L0.
- **`wmid` must be wired** as the real immutable identity (Invariant 8), currently optional/unused.
- **Honest residual:** the shipped default library still privileges one scheme per domain; that
  choice is a sourced governance decision, not an objective truth claim.
- **Rejected for v1:** full graph inversion (option B) — reserved for a post-v1 RFC only if the
  additive layer provably fails.

## Alternatives considered

- **A — keep the OOP tree as-is.** Rejected: non-compliant with ETHICS today; hardening it converges
  on this decision anyway.
- **B — invert to a scheme-aware graph source; OOP as one projection.** Rejected for v1: reverses
  `docs/03-architecture.md` §1.2, front-loads the hardest unbuilt projector, and guts the
  authoring-based academic program; the same ETHICS requirement is met additively at MINOR scope.

## Follow-ups

1. Enrich `schema/wml.schema.json` (+ the generated `wml.xsd`, kept in sync): add the `Scheme`
   construct + registry; the classification-claim fields (provenance, rank, `asOf`, tier, status);
   attach `classified_as`/`classifiedUnder` to **`individual` and `role`** (today only `concept` has
   it — so Pluto cannot hold one); and add a **`wmid`** property to concept/role/individual (all nodes
   are `additionalProperties:false` today and carry no `wmid` field). Promoting `wmid` from "optional
   in v0" (02 §6.1, GOVERNANCE §1.1) to the authoritative identity is part of this L0 change, not a
   data back-fill. Add the validator gates (every `scheme` resolves; no well-sourced rival deleted;
   reclassification preserves `wmid`). Until this lands, per-claim provenance on `classified_as` rests
   on the owning concept's provenance.
2. Back-fill sourced, dated classification claims where they matter (Pluto's Planet→DwarfPlanet;
   biology rank ladders; the tomato; disputed sovereignty).
3. Wire `wmid` as the immutable identity across the seeded model.
