# WMOOP Governance

<!--
SPDX-License-Identifier: CC-BY-4.0
Part of the WMOOP project (World Map Object-Oriented Programming) — github.com/WMOOP
Canonical home: wmoop.doc. This document governs the whole organization and all per-language repos.
-->

## WMOOP Governance

> **WMOOP — World Map Object-Oriented Programming.**
> *Describe World into OOP; Map all World Objects into Programming Languages.*

This document defines **how decisions get made** in WMOOP: who may change what, how changes are proposed, reviewed, versioned, and retired, and how disputes are resolved. It is written to be followed by **humans and AI agents alike**, and to be as machine-checkable as possible.

For *what makes a contribution factually and ethically acceptable*, see **[ETHICS.md](./ETHICS.md)**. For *how to physically make a contribution* (branches, PR mechanics, local tooling), see **CONTRIBUTING.md**. For behaviour expectations, see **[CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)**.

---

### 1. Scope and first principles

WMOOP maintains a single, language-neutral **World Model (WM)** — the canonical, declarative ontology that lives in `wmoop.doc` — and a set of per-language repositories (`wmoop.net`, `wmoop.java`, `wmoop.py`, `wmoop.cpp`) that are **generated from and conformance-tested against** the WM, built by the tooling in `wmoop.tools`. The full repo list and every CI-enforced constant are fixed in the **Normative constants** table (§1.1).

This governance is bound by eight **architectural invariants**. They are not up for casual change; altering any of them requires a **Meta-RFC** (§6) and a Technical Steering Committee (TSC) supermajority (§4.4).

| # | Invariant | One-line governance consequence |
|---|-----------|----------------------------------|
| I1 | **Schema-first / ontology-first.** The WM in `wmoop.doc` is the *single source of truth*. | Changes to meaning start in `wmoop.doc`; language repos never diverge the model by hand. |
| I2 | **Three layers.** L0 meta-model (small, fixed), L1 domain models, L2 instances. | L0 changes are the most tightly governed; L2 is the most open. |
| I3 | **Roles & composition over deep inheritance.** Inheritance models only stable `is-a-kind-of` essence; cross-cutting facets are roles. | Reviewers reject `Driver : Person`; they require `Person` + `Driver` role (§ ETHICS modelling rules). |
| I4 | **Every concept is sourced.** Stable global ID, human name, definition, provenance/citation, units for quantities. | CI blocks any merge missing these; see Definition of Done (§8). |
| I5 | **Domains are versioned modules with an acyclic dependency graph.** Cross-domain links are declared and versioned. | A PR that introduces a dependency cycle fails CI and cannot be merged. |
| I6 | **Everything is machine-checkable.** | The Definition of Done is automated; humans and AI contribute against the same gate. |
| I7 | **Ontological completeness.** L0 represents endurants, perdurants and abstracts as first-class — not physical-objects-with-properties only. | Domains needing processes (perdurants) or abstractions (Math, Music) are first-class; reviewers don't force them into object-with-fields shapes. |
| I8 | **Identity lifecycle & world-stance.** Stable id with first-class deprecation/`sameAs`/merge; open-world for facts, closed-world for schema conformance. | IDs are never reused; absence of a fact is not its negation; the DoD checks are the closed-world contract. |

**"Write once, replicate everywhere" is mechanical.** Per-language code is *generated* and *conformance-tested*, never manually re-authored from the model. A human (or AI) who wants to change a concept in C# does not edit `wmoop.net` by hand — they change the WM, regenerate, and the change flows to every language.

#### 1.1 Normative constants (single source of truth)

> Every CI-enforced or cross-document constant has **exactly one value here**. Any other
> document that needs one of these MUST link to this table, never restate it; a CI check
> asserts the authored artefacts match these values. This table resolves the prior drift
> between the meta-model, architecture, schema, contribution and pattern docs.

| Constant | Normative value |
|----------|-----------------|
| **Concept / Role / Type ID (QName)** | `wmoop.<domain>(.<subdomain>)*/<PascalName>` — e.g. `wmoop.transport/Driver` |
| **Member ID** | `<TypeQName>#<camelName>` — e.g. `wmoop.transport/Vehicle#wheelCount` |
| **Module ID** | `wmoop.<domain>(.<subdomain>)*` — e.g. `wmoop.transport` |
| **Opaque identity (optional backing)** | `wmid:` + Crockford-base32 ULID (26 chars). The QName is the working identifier in v0; `wmid` is reserved for stable identity across renames/merges. |
| **Forbidden ID forms** | colon separators (`wm:x:Y`), dot-before-local-name CURIEs (`wm:x.Y`), reserved kind segments (`…role.`/`…prop.`/`…rel.`/`…ind.`), a `/role/` path segment, and the bare `wm:` prefix. Kind is a node property, never part of the id. |
| **Inheritance keyword (WML)** | `extends` |
| **Inheritance depth** | CI **error** at depth > 6; **warning** at depth 5. ("≤ 3–4 levels" in teaching material is a heuristic, not the gate.) |
| **Role-player keyword (WML)** | `played_by` (rendered `playedBy` in the XML projection and camelCase bindings). `AddRole`/`HasRole`/`GetRole` are the generated runtime API, not the model keyword. |
| **Provenance `kind` enum** | `sourced \| definitional \| convention` |
| **Core invariants** | Eight: I1 schema-first · I2 three layers · I3 composition/roles over inheritance · I4 sourced/identified/measured · I5 versioned, acyclic domains · I6 machine-checkable · I7 ontological completeness · I8 identity lifecycle & open/closed-world stance |
| **Canonical format** | WML (authored in YAML, compiled to canonical JSON) |
| **Meta-schema (grammar)** | `wmoop.doc/schema/wml.schema.json` (JSON Schema; `wml.xsd` is a generated XML projection) |
| **Compiled model artefact** | `wm-<ver>.json` (RFC 8785 JCS), published as a GitHub Release of `wmoop.doc`. Not named `wmoop.json`. |
| **Compiler / tooling home** | `wmoop.tools` (ships `wmoopc`, the generators, projectors, conformance runner) |
| **Conformance-gated bindings (v1)** | `wmoop.net` (C#), `wmoop.java`, `wmoop.py`, `wmoop.cpp` |
| **Planned bindings (not yet conformance-gated)** | `wmoop.js`, `wmoop.db` |
| **License — code** | Apache-2.0 (chosen) |
| **License — model & docs** | CC-BY-4.0 (chosen) |
| **AI PR — routine size** | ≤ 5 node files per automated PR; larger imports require an RFC + a sponsoring steward |
| **AI PR — throughput** | ≤ 5 open automated PRs per bot; ≤ 10 automated PRs merged per domain per day |
| **Contribution labels** | `human \| ai-assisted \| ai-generated` |
| **Domain status** | `seeded` (module exists in `model/`) · `candidate` (needs steward + sources). Living list: `model/taxonomy.yaml`; map: `docs/06-domain-taxonomy.md`. |
| **Geography** | Its own top-level domain (`wmoop.geography`); Transport depends on it — not a sub-domain of Nature. |

---

### 2. Roles and responsibilities

WMOOP uses a small, explicit role ladder. Roles are about **responsibility and merge rights**, not status. Every role is recorded in machine-readable files so tooling (and AI agents) can check authority programmatically.

| Role | Who | Can do | Recorded in |
|------|-----|--------|-------------|
| **Contributor** | Anyone (human or AI-assisted) who opens an issue, RFC, or PR | Propose changes; review; discuss | Git history |
| **Domain Steward** | Maintainer of one or more L1 domains | Approve & merge PRs *within their domain*; triage domain issues; own the domain roadmap | `MAINTAINERS.yaml` + `CODEOWNERS` |
| **Core Maintainer** | Cross-cutting maintainers (tooling, codegen, CI, L0) | Approve & merge infra/L0/codegen changes; cut releases | `MAINTAINERS.yaml` |
| **Technical Steering Committee (TSC)** | 5–9 elected core maintainers + senior stewards | Decide escalations; ratify Meta-RFCs; appoint/remove stewards; final arbiter | `TSC.yaml` |
| **Release Manager** | Rotating core maintainer | Owns a release train, changelog, and stability-tier transitions | `TSC.yaml` (rotation) |
| **Emeritus** | Former maintainers | Advisory voice; no merge rights | `MAINTAINERS.yaml` |

**Contributor — baseline rights and duties.**
- May open issues, RFCs, and PRs against any repo.
- Must follow ETHICS.md (sourcing, NPOV, red lines) and this document.
- Must **disclose AI involvement** (§9) on every PR.
- Has no merge rights; two independent approvals are still required for anything they author (§4).

**Domain Steward.**
- Owns a bounded set of L1 domains (e.g. `nature.animals`, `space`, `transport`). Ownership is 1→many; a domain has **at least one, ideally two** stewards to avoid a bus-factor of one.
- Accountable for the domain's **scientific/epistemic quality**, its taxonomy choices, its cross-domain links, and its deprecations.
- Reviews and merges in-domain PRs under lazy consensus (§4.1).
- May **not** unilaterally change L0, codegen, cross-domain contracts owned by another domain, or this governance.

**Core Maintainer.**
- Owns the meta-model (L0), the WM schema, code generators, conformance test harness, and CI.
- Because L0 and codegen affect *every* language and *every* domain, their changes always run through the RFC process (§6) and require broader review.

**Technical Steering Committee (TSC).**
- The backstop for everything consensus cannot settle.
- Ratifies Meta-RFCs, resolves escalated conflicts, appoints and (rarely) removes stewards, and owns this governance document.
- Operates by lazy consensus internally; falls back to a vote (§4.4) when needed.
- Publishes minutes for every decision in `wmoop.doc/governance/tsc-minutes/`.

#### 2.1 Becoming, and ceasing to be, a steward

**Path to Domain Steward:** sustained, high-quality contribution to a domain (a rule of thumb: ~5+ substantive merged PRs with correct provenance, demonstrated understanding of ETHICS.md, and endorsement by an existing steward of that domain or a core maintainer). Nomination is an issue in `wmoop.doc`; lazy consensus of current stewards + TSC confirms.

**Inactivity.** A steward with no review/merge activity for **6 months** is moved to Emeritus after a public heads-up. This is administrative hygiene, not a judgement — re-activation is a one-line request.

**Removal for cause** (red-line violations, Code-of-Conduct breaches, sustained bad-faith action) requires a TSC vote (§4.4) and is documented.

---

### 3. Domain ownership

Ownership is expressed in two coupled files so that it is both human- and machine-readable, and enforced by CI.

```yaml
# MAINTAINERS.yaml  (illustrative)
domains:
  nature.animals:
    tier: stable
    stewards: [ "@ada", "@linnaeus-bot-sponsor:@grace" ]   # bots are sponsored by a human
    depends_on: [ "nature", "meta.quantities" ]
  transport:
    tier: experimental
    stewards: [ "@karl" ]
    depends_on: [ "nature", "meta.roles" ]
```

```gitignore
# CODEOWNERS  (illustrative; GitHub enforces review routing)
/model/nature/animals/   @ada @grace
/model/transport/        @karl
/model/_meta/            @core-maintainers          # L0 — core only
/tooling/codegen/        @core-maintainers
/GOVERNANCE.md           @tsc
/ETHICS.md               @tsc
```

**Rules of ownership.**
1. Every path under `model/` **must** map to at least one owner in `CODEOWNERS`. CI fails on orphaned paths.
2. A PR that touches a domain requires approval from **that domain's** owner. A PR that touches multiple domains requires an owner from **each**.
3. **No self-merge of your own authored changes** without a second independent approval — this applies to stewards and core maintainers too, and to AI-sponsored PRs.
4. L0 (`model/_meta/`) is owned by core maintainers *and* gated by the RFC process (§6). Touching L0 is never a routine review.

---

### 4. How decisions are made

WMOOP runs on **lazy consensus with a clear escalation ladder**. The goal is to let the common case (a well-sourced, in-scope, in-domain change) move fast, while making structural changes deliberate.

#### 4.1 Lazy consensus (the default)

- A proposal is **approved by silence**: if no WMOOP maintainer with standing in the affected area raises a *substantive, unresolved objection* within the review window, and the Definition of Done (§8) is green, it may be merged.
- **Review windows:**

  | Change class | Minimum open time | Approvals required |
  |--------------|-------------------|--------------------|
  | L2 instance data, typo/prose, provenance fix | 24 h | 1 owner |
  | L1 additive (new concept/property/relation, new optional attribute) | 72 h (3 working days) | 1 owner + 1 other maintainer |
  | L1 breaking (rename/remove/semantics change of a *stable* item) | 7 days | 2 owners, announced in release notes |
  | Cross-domain link or new domain dependency | 7 days | an owner of **each** affected domain |
  | L0 / meta-model / codegen / schema | RFC (§6) | TSC ratification |
  | This governance / ETHICS.md | Meta-RFC (§6) | TSC supermajority |

- A **substantive objection** is a concrete, reasoned concern (e.g. "this citation does not support the claim", "this introduces a dependency cycle", "this violates the race red line"). "I'd have named it differently" is a suggestion, not a blocker.

#### 4.2 Escalation ladder

```
Discussion on the PR/issue
        │  (unresolved objection, or disagreement between maintainers)
        ▼
Domain Steward decision (for in-domain matters)
        │  (steward conflict, cross-domain disagreement, or appeal)
        ▼
Technical Steering Committee  →  TSC vote (§4.4) if consensus fails
```

Each step has a **soft clock**: if a step stalls for more than 14 days without progress, any participant may escalate to the next level with a one-line note. Nothing is allowed to die silently; nothing is forced through silently.

#### 4.3 ADRs — Architecture Decision Records

Any decision that (a) sets a precedent, (b) rejects a plausible alternative, or (c) will be asked "why did we do it this way?" later, is recorded as a short **ADR** in `wmoop.doc/governance/adr/NNNN-title.md`.

```markdown
# ADR 0007 — Roles are not subclasses

- Status: Accepted (2026-02-11)
- Deciders: TSC
- Context: Contributors kept proposing `Driver : Person`.
- Decision: Cross-domain facets are modelled as Roles attached by composition. (Invariant I3.)
- Consequences: Codegen emits role interfaces/traits; linter rejects cross-domain inheritance.
- Alternatives considered: multiple inheritance (rejected: fragile, language-dependent); mixins only (rejected: loses identity of the role).
```

ADRs are **append-only**: a later decision supersedes an earlier one by a new ADR that links back (`Superseded by ADR 0019`); the old one is never edited away.

#### 4.4 Voting (the last resort)

When consensus genuinely fails:
- **TSC quorum** = ⌈⅔ of seated members⌉.
- **Ordinary decision** = simple majority of those voting; abstentions don't count against quorum.
- **Supermajority decision** (changing an invariant I1–I8, this document, ETHICS.md red lines, or removing a maintainer for cause) = **two-thirds of seated members**.
- Votes and rationale are public in the TSC minutes. A conflicted member (e.g. voting on removing themselves, or on their own employer's data source) **must recuse**.

---

### 5. RFC process (for L0, codegen, schema, cross-cutting, and governance)

Routine domain work does **not** need an RFC. RFCs exist for changes whose blast radius is the whole project.

**An RFC is required for:**
- any change to the **L0 meta-model / upper ontology** (new foundational category, changed semantics of `Concept`, `Property`, `Relation`, `Role`, `Scheme`);
- changes to the **WM schema** or the **provenance model**;
- changes to **code generators** or the **conformance contract** that affect all languages;
- introducing a **new top-level domain**;
- changing **stability-tier rules, versioning, or deprecation policy**;
- a **Meta-RFC**: changing an invariant (I1–I8), this governance, or ETHICS.md.

**RFC lifecycle:**

```
Draft ──▶ Discussion ──▶ Final Comment Period (FCP, 10 days) ──▶ Accepted / Rejected / Postponed ──▶ Implemented ──▶ (optionally) Superseded
```

1. **Draft.** Open `wmoop.doc/rfcs/0000-title.md` from the template; PR it. A sponsoring maintainer is assigned.
2. **Discussion.** Open-ended, but a stalled RFC can be timed out after 30 days of inactivity (→ Postponed).
3. **Final Comment Period.** The sponsor proposes a disposition; a 10-day clock starts; new *blocking* concerns must be raised with rationale.
4. **Disposition.** L0/schema/codegen RFCs need TSC ratification; Meta-RFCs need TSC supermajority. Outcome recorded as an ADR.
5. **Implemented.** Tracked to merge; the RFC's `Status` updated and cross-linked to the PRs.

**RFC template (abridged):** Summary · Motivation · Guide-level explanation (with worked examples in ≥2 languages) · Reference-level detail · **Backwards-compatibility & migration** · **Impact on provenance/ethics** · Alternatives · Unresolved questions.

---

### 6. Versioning and stability

#### 6.1 Identity is forever

- Every concept carries a **stable global ID** (Invariant I4), e.g. `wmoop.nature.animals/Cetacean`.
- **IDs are immutable and never reused.** You do not rename an ID. A rename is: mint a **new** ID, mark the old one `deprecated` with `replacedBy: <new-id>` and (where meaning is identical) a `sameAs` link. Consumers get a clean migration path and nothing silently changes meaning under them.

#### 6.2 Semantic versioning of modules

Each domain module is versioned with **SemVer** (`MAJOR.MINOR.PATCH`).

| Bump | Trigger | Examples |
|------|---------|----------|
| **MAJOR** | Breaking change to a **stable** item | remove/rename a stable ID; tighten cardinality; change a definition's meaning; change units of a quantity |
| **MINOR** | Backward-compatible addition | new concept, new relation, new *optional* property, new classification scheme |
| **PATCH** | No structural change | fix prose/definition wording, add/repair provenance, fix a typo'd citation |

Cross-domain dependencies are pinned to **version ranges** (e.g. `nature >=2.1 <3`). A dependency cycle **anywhere** in the graph is a CI failure (Invariant I5).

#### 6.3 Stability tiers

Every concept, property, relation, and scheme carries a **stability tier**:

| Tier | Guarantee | Who may add | Change rules |
|------|-----------|-------------|--------------|
| `experimental` | None. May change or vanish in a MINOR/PATCH. | Any contributor via normal review | Must be clearly flagged; not emitted in "stable" codegen profiles by default |
| `stable` | SemVer applies. Breaking change ⇒ MAJOR + deprecation first. | Promoted by a steward after it has proven out | Normal breaking-change process |
| `deprecated` | Still present; scheduled for removal. | Marked by a steward | Carries `deprecatedSince`, `replacedBy`, `removeAfter` |

**Promotion** experimental → stable is a steward decision recorded in release notes. **Nothing is born stable** except by explicit decision.

#### 6.4 Deprecation policy

1. Mark the item `deprecated` with machine-readable metadata:
   ```yaml
   status: deprecated
   deprecatedSince: "nature@4.2.0"
   replacedBy: "wmoop.nature.animals/Cetacean"
   removeAfter: "nature@5.0.0"     # never sooner than the next MAJOR
   reason: "Folk grouping 'sea-fish' conflated mammals and fish; superseded by sourced taxonomy."
   ```
2. A deprecated item must remain for **at least one MAJOR release and at least 180 days**, whichever is longer.
3. Removal happens only in a MAJOR release, is listed in the migration guide, and codegen emits deprecation annotations (`[Obsolete]` in C#, `@Deprecated` in Java, `DeprecationWarning` in Python, `[[deprecated]]` in C++) so downstream users get compiler/runtime warnings.

---

### 7. Change management and the Definition of Done

A contribution is **Done** when the automated gate is green **and** a human/accountable reviewer has signed off. The gate is the same for humans and AI (Invariant I6).

**Automated Definition of Done (CI-enforced):**

- [ ] **Schema-valid.** The change validates against the WM schema.
- [ ] **Identity.** Every new concept has a unique, well-formed, never-before-used stable ID.
- [ ] **Completeness (I4).** Name, definition, provenance/citation present; units present for every quantity.
- [ ] **Provenance resolvable.** Every citation has a resolvable locator (DOI/ISBN/URL + accessed date) and a declared **source tier** (see ETHICS §2).
- [ ] **No cycles (I5).** Domain dependency graph stays acyclic.
- [ ] **No illegal inheritance (I3).** Linter finds no cross-domain `is-a`; facets are roles.
- [ ] **Red-line linter (ETHICS).** No forbidden constructs (e.g. race-as-subclass-of-human); sensitive-domain flags present where required.
- [ ] **Codegen round-trips.** The model generates valid code in every active language and passes conformance tests.
- [ ] **Versioning.** SemVer bump and stability tier are correct for the kind of change.
- [ ] **AI disclosure (§9).** Provenance `method` and PR labels set.

**Human sign-off** confirms the things a machine can't: that the citation *actually supports* the claim, that the taxonomy choice is defensible, and that ETHICS.md is honoured in spirit.

---

### 8. AI-specific governance

AI agents are **first-class, welcome contributors** — the project is explicitly designed so AI can help describe the world — but they contribute under extra guardrails, because AI can generate large volumes of plausible-but-wrong content and fabricate citations.

**Principle: *AI proposes, humans dispose.*** No AI-generated or AI-assisted change reaches `main` without a **named, accountable human reviewer**.

1. **Disclosure is mandatory.**
   - Every PR declares its method with a label: `human`, `ai-assisted` (human-authored, AI-helped), or `ai-generated` (AI-authored).
   - Every *asserted fact* records it in provenance:
     ```yaml
     assertedBy: "model:claude-opus-4-8"     # or a human handle
     sponsoredBy: "@grace"                    # the accountable human
     method: ai-generated                     # human | ai-assisted | ai-generated
     assertedOn: "2026-10-16"
     ```
   - Commit trailer: `Generated-With: <model-id>` and the standard co-authorship trailer.

2. **Human review is non-negotiable.** For `ai-generated` and `ai-assisted` PRs, the human reviewer must **independently verify that each cited source exists and supports the claim** (anti-hallucination check). Signing off means the human takes responsibility for the content. A bot cannot be the accountable approver.

3. **Every AI contributor has a human sponsor.** Bot accounts are registered in `MAINTAINERS.yaml` with a named human sponsor who is answerable for the bot's output and whose review rights the bot does **not** inherit.

4. **Rate limits on automated PRs.** To keep review load and quality sustainable:

   | Limit | Default |
   |-------|---------|
   | Open automated PRs per bot at once | ≤ 5 |
   | Automated PRs merged per domain per day | ≤ 10 |
   | Node files added or changed per routine automated PR | ≤ 5 (larger imports go through an RFC + bulk-import review) |
   | Bulk import (new dataset / hundreds of instances) | Requires an RFC and a sponsoring steward regardless of size |

   Bots that exceed limits are auto-throttled by CI; repeated abuse → the sponsor is notified and the bot can be suspended by any core maintainer.

5. **Same gate, no shortcuts.** AI PRs pass the exact Definition of Done (§8). There is no "trusted AI" fast-path.

6. **Provenance over fluency.** A confident, well-written assertion with no resolvable source is rejected — from humans and AI equally. Fluency is not evidence.

---

### 9. Conflict resolution

1. **Assume good faith; argue the artefact, not the author.** Disagreements are about claims, sources, and model shape.
2. **Technical disputes** follow the escalation ladder (§4.2): PR discussion → steward → TSC → vote.
3. **Competing taxonomies are not a conflict to "win."** If two contributors disagree about *the* correct classification, the WM represents **both** as separate, sourced classification schemes (see ETHICS §2.5). The reviewer's job is to ensure each scheme is well-formed and attributed, not to pick a winner.
4. **Conduct disputes** go to the Code of Conduct process ([CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)), not the technical ladder.
5. **Deadlock** is broken by the TSC (§4.4). A recorded decision, even an imperfect one, beats an indefinite stall.

---

### 10. Licensing governance

WMOOP is a *provenance-first* project, and the license choice reflects that ethos.

| Material | License | Rationale |
|----------|---------|-----------|
| **Code** (generators, tooling, per-language outputs, tests) | **Apache-2.0** *(chosen)* | Permissive, patent grant, industry-standard for broad adoption across ecosystems. Already selected in the repos. |
| **Model content & documentation** (definitions, prose, curated structure, the WM itself, these docs) | **CC-BY-4.0** *(chosen)* | See §10.1. |

Every file/module carries an **SPDX identifier** (`SPDX-License-Identifier: Apache-2.0` or `CC-BY-4.0`) so licensing is machine-checkable. A top-level `LICENSES/` directory holds the full texts; `NOTICE` carries required attributions.

#### 10.1 Why CC-BY-4.0 for content (CC-BY-4.0 vs CC0)

Both are excellent open licenses; the choice is about **ethos fit**, not openness.

- **CC-BY-4.0 (chosen).** Reuse is unrestricted *provided attribution is preserved*. This is a near-perfect match for a project whose entire value proposition is **traceable provenance**: attribution culture is not friction here, it is the point. It aligns with academic citation norms (helping the academic/educational adoption the project is designed for), keeps the chain of credit intact as the model is reused in papers, courses, and downstream datasets, and is broadly interoperable with other open-data ecosystems (e.g. Wikidata is CC0, OpenStreetMap is ODbL — CC-BY sits comfortably as a *consumer* of both with proper attribution).
- **CC0 (considered, not chosen).** Maximises reuse and removes attribution-stacking friction, and is the cleanest fit for *bare facts*. We decline it as the project-wide content license because dropping attribution would undercut the provenance discipline we are trying to teach and reward.
- **Important nuance (documented so contributors don't over-claim).** In most jurisdictions, **individual facts and raw data are not copyrightable** — copyright attaches to *creative selection, arrangement, definitions, and prose*, not to "a whale is a mammal." So CC-BY-4.0 primarily governs WMOOP's **curated expression**: the definitions we write, the structure we design, the documentation. Contributors must not use the license to claim ownership of underlying facts, and must still honour each upstream source's own attribution/licensing (§10.2).
- **Alternative noted for the record.** `CDLA-Permissive-2.0` is a reasonable data-specific alternative; CC-BY-4.0 is preferred for its ubiquity and academic familiarity.

#### 10.2 Third-party data, attribution, and provenance

1. **License compatibility is a merge gate.** Data ingested into the WM must be under a license compatible with CC-BY-4.0 redistribution. **Do not ingest** NonCommercial (`-NC`), NoDerivatives (`-ND`), or unknown/all-rights-reserved sources into the corpus. Share-alike/copyleft data (e.g. ODbL) may be *referenced and cited* but is only *incorporated* under its own terms, flagged distinctly, and reviewed case-by-case.
2. **Every external source is registered** in `wmoop.doc/SOURCES.yaml` with: canonical name, URL/DOI/ISBN, license (SPDX), source tier (ETHICS §2.2), and date accessed. Facts reference a source by key.
3. **Attribution is preserved end to end.** Upstream attributions propagate into `NOTICE` and into generated artefacts. Removing or obscuring a required attribution is a licensing violation and blocks merge.
4. **A Contributor License / DCO.** Contributors sign off with the **Developer Certificate of Origin** (`Signed-off-by:`), certifying they have the right to contribute the material under the project's licenses. AI-sponsored contributions are signed off by the human sponsor.

---

### 11. Code of Conduct

WMOOP adopts the **Contributor Covenant v2.1**. See **[CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)** for the full text, scope, reporting channel, and enforcement ladder. Conduct enforcement is independent of the technical governance in this document.

---

### 12. Amending this document

This document and the invariants it protects are changed only by **Meta-RFC** (§5) with a **TSC supermajority** (§4.4). Every amendment is accompanied by an ADR explaining the change and its consequences. Minor editorial fixes (typos, broken links, clarifications that change no rule) may be merged under ordinary lazy consensus by a TSC member and noted in the changelog.

---

### Appendix A — File map of governance artefacts

| File / path | Purpose |
|-------------|---------|
| `GOVERNANCE.md` | This document |
| `ETHICS.md` | Epistemic standards, sensitive-domain red lines |
| `CODE_OF_CONDUCT.md` | Behaviour standards (Contributor Covenant 2.1) |
| `CONTRIBUTING.md` | Practical how-to for contributing |
| `MAINTAINERS.yaml`, `TSC.yaml`, `CODEOWNERS` | Machine-readable authority |
| `SOURCES.yaml` | Third-party source & license registry |
| `wmoop.doc/rfcs/` | RFCs and Meta-RFCs |
| `wmoop.doc/governance/adr/` | Architecture Decision Records |
| `wmoop.doc/governance/tsc-minutes/` | TSC decision log |
| `LICENSES/`, `NOTICE` | License texts and required attributions |

---
---
