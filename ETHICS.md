# WMOOP Ethics & Quality Manual

<!--
SPDX-License-Identifier: CC-BY-4.0
Part of the WMOOP project — github.com/WMOOP. Canonical home: wmoop.doc.
Binding on all contributors, human and AI. Governed by GOVERNANCE.md (Meta-RFC + TSC supermajority to change red lines).
-->

## WMOOP Research Ethics & Epistemic Standards

WMOOP describes the real world. That is a responsibility, not just an engineering task. This document sets the **epistemic standards** every contribution must meet and the **hard red lines** that no contribution may cross. It applies equally to humans and to AI agents.

The short version:

> **We model the map, not the territory, and we always say who drew the map.**
> We represent *sourced claims and viewpoints with provenance* — not decreed truths. Where the world is contested, we hold multiple viewpoints side by side, each attributed, rather than picking a winner.

Violations of the **red lines (§3)** are grounds for immediate rejection and, if deliberate or repeated, removal (GOVERNANCE §2.1, §4.4).

---

### 1. The core stance: claims, not decrees

Every fact in the WM is a **claim held by a source**, never an unattributed assertion of absolute truth. The data model reflects this: a fact is not `whale.class = Mammalia`; it is "*Source S, a Tier-A reference, classifies the whale as Mammalia under the Linnaean scheme (confidence: established).*"

This single design choice is what lets WMOOP stay neutral, handle disagreement, and remain honest about uncertainty.

```yaml
# Illustrative shape of a sourced claim
claim:
  subject: wmoop.nature.animals/BlueWhale
  predicate: classifiedAs
  object: wmoop.nature.animals/Mammal
  scheme: wmoop.scheme/Linnaean          # which classification system (see §2.5)
  provenance:
    source: src:iucn-redlist           # key into SOURCES.yaml
    tier: A
    locator: "https://doi.org/10.xxxx"
    accessed: "2026-10-16"
    assertedBy: "@ada"
    method: human                      # human | ai-assisted | ai-generated
  epistemicStatus:
    confidence: established            # see §2.3
    consensus: scientific-consensus    # see §2.4
```

---

### 2. Epistemic standards

#### 2.1 Neutral point of view (NPOV)

WMOOP describes viewpoints; it does not adjudicate between them except where there is genuine scientific consensus (and even then it *attributes* that consensus rather than decreeing it).

- **Describe, attribute, don't endorse.** "Tradition T teaches X" (sourced) — not "X."
- **Proportionality.** Represent viewpoints in rough proportion to their standing among reliable sources. A fringe view may be *recorded and labelled as fringe*; it is not given parity with consensus.
- **No editorialising.** Definitions are descriptive and value-neutral. Loaded, promotional, or disparaging language is rejected.

#### 2.2 Sourcing: every factual claim is cited

Nothing factual enters the WM without a resolvable citation (Invariant I4). Sources are ranked into tiers, recorded in `SOURCES.yaml`:

| Tier | What | Examples | Use |
|------|------|----------|-----|
| **A** | Primary scholarship & authoritative standards | peer-reviewed literature, standards bodies (ISO, BIPM/SI, IUPAC, IAU, ITIS/Catalogue of Life), major scientific consensus statements | Preferred for all factual claims |
| **B** | Edited reference works & official datasets | reputable textbooks, encyclopedias with editorial oversight, government/intergovernmental statistics | Acceptable; prefer A where it exists |
| **C** | Maintained community references | large curated wikis, well-run community databases | Only with corroboration; flag as `tier: C` |
| **✗** | **Not acceptable as sole support** | blogs, forums, social media, press releases, predatory journals, **AI-generated text with no underlying source**, "common knowledge" | Reject or require a real source |

Rules:
- **Units for every quantity** (SI preferred; record the unit and, where relevant, the measurement's uncertainty and date). A number without a unit is rejected.
- **Citations must be verified to support the claim** — especially for AI contributions (GOVERNANCE §8.2). A real-looking citation that does not actually say what the claim says is treated as a fabrication.
- **Date facts that change.** Populations, borders-in-dispute, political status, "largest/longest/fastest" superlatives, and prices carry an `asOf` date; they are claims-at-a-time, not eternal truths.

#### 2.3 Marking uncertainty

Every claim carries a machine-readable **confidence**, so consumers (and AI learners) can tell solid ground from shifting sand:

| `confidence` | Meaning |
|--------------|---------|
| `established` | Strong, convergent, Tier-A support |
| `probable` | Good support, some open questions |
| `contested` | Reputable sources actively disagree (→ model all sides, §2.5) |
| `uncertain` | Thin or preliminary evidence |
| `historical` | Formerly held, now superseded (kept for provenance, e.g. "whales were once grouped with fish") |

#### 2.4 Scientific consensus vs folk / common-sense models

Both are legitimate to model — people *do* think of whales as "big sea creatures" and tomatoes as "vegetables" — but they must be **distinguished and labelled**, never conflated.

- Tag each claim's `consensus` as `scientific-consensus`, `scholarly-majority`, `folk-model`, `common-usage`, `historical`, or `contested`.
- A **folk or common-usage** classification is modelled in its **own classification scheme** (§2.5), clearly labelled, and never presented as the scientific account.
- Worked example — **the tomato:** `classifiedAs Fruit` under `scheme.botanical` (Tier A), *and* `classifiedAs Vegetable` under `scheme.culinary-common-usage` (Tier B, `consensus: common-usage`). Both are true *within their scheme*; neither is deleted.

#### 2.5 Competing taxonomies — multiple schemes, no "one true tree"

**This is a foundational rule of WMOOP.** The world is classified differently by different disciplines and traditions, and WMOOP does **not** declare one tree correct. Classification schemes are **first-class, versioned objects** (L0), and any concept may be classified under several of them, each with provenance.

```yaml
# Illustrative: the whale under three schemes, all retained, all sourced
schemes:
  - id: wmoop.scheme/Linnaean
    name: "Linnaean taxonomy"
    authority: src:catalogue-of-life
  - id: wmoop.scheme/Phylogenetic
    name: "Phylogenetic / cladistic"
    authority: src:peer-reviewed-phylogenomics
  - id: wmoop.scheme/Folk
    name: "Common/folk classification"
    consensus: folk-model

classifications:
  - { subject: BlueWhale, under: wmoop.scheme/Linnaean,     path: "Animalia > Chordata > Mammalia > Cetacea",            tier: A }
  - { subject: BlueWhale, under: wmoop.scheme/Phylogenetic, path: "... > Artiodactyla (whales nested within even-toed ungulates)", tier: A }
  - { subject: BlueWhale, under: wmoop.scheme/Folk,         path: "sea creature",  consensus: folk-model, status: historical-also-current, tier: C }
```

Decision rule for contributors and reviewers:

> **When sources classify something differently, do NOT choose. Add (or reuse) a scheme for each, attribute each, and link the concept under all of them.** Reviewers reject PRs that delete a well-sourced rival scheme in favour of a single "correct" one.

This covers cladistics vs Linnaean vs common usage in biology, and generalises: ICD vs DSM in medicine, competing music-theory systems, competing geological or astronomical classifications, and so on.

> **Realization & status (ADR 0001).** This rule **will be** realized by an **additive** first-class `Scheme` L0 construct plus sourced, dated `classifiedUnder` claims layered over the OOP identity tree — **not** by inverting the source to a graph. (The construct is accepted in direction but **not yet in the schema**; the enrichment is a tracked follow-up.) The generated class library still materializes one **default** scheme per domain (a sourced governance choice); rival schemes ship as queryable annotations, never deleted. See [ADR 0001](governance/adr/0001-classification-source-of-truth.md) and the Normative constants table in [GOVERNANCE.md](GOVERNANCE.md).

---

### 3. Sensitive domains and red lines

These are **hard constraints**, enforced by the red-line linter (GOVERNANCE §8) and by human review. Changing a red line requires a Meta-RFC and TSC supermajority. "I was just modelling what a source says" does **not** license crossing them.

#### 3.1 Humans

Humans are the most ethically fraught subject in the model. Default to caution and dignity.

- **RED LINE — no race/ethnicity as biological subclasses of humans.** You must **not** model `WhiteHuman`, `BlackHuman`, `AsianHuman`, or any race/ethnicity as a subclass of `Homo sapiens`, nor attach pseudo-biological "racial traits" to such classes. The scientific consensus is that human "race" is a **social construct, not a biological taxon** (human genetic variation is overwhelmingly continuous and within-group, not cleaved into discrete biological races). Model **ethnicity / nationality / ancestry** as **self-identified socio-cultural attributes or roles** with provenance, explicitly flagged `nonBiological: true`, never as inheritance.
  ```yaml
  # WRONG:  class CaucasianHuman : Human { ... }        # rejected by linter
  # RIGHT:  Person has attribute selfIdentifiedEthnicity: { value, source, nonBiological: true }
  #         Geographic genetic ancestry, if modelled at all, is a sourced, probabilistic attribute,
  #         framed per population genetics (Tier A) — never a discrete human subclass.
  ```
- **RED LINE — no pseudoscience as fact.** No phrenology, race science, astrology-as-causation, "scientific" hierarchies of human worth, debunked medical claims, or similar. Such belief systems may be modelled **only** as *historical/belief-system content*, clearly labelled `consensus: pseudoscience` or `historical`, with the scientific refutation cited alongside — never as established fact.
- **Sex and gender — model carefully, respectfully, and separately.**
  - **Biological sex** is modelled as sourced biological attributes (e.g. chromosomal, gonadal, hormonal, phenotypic markers), framed per Tier-A biology, and **must acknowledge natural variation** (intersex variations exist; sex is not a clean binary at the biological level). Do not assert a strict binary essence.
  - **Gender** is modelled as a **distinct** social/identity attribute — self-identified, culturally variable, and **not** derived from or equated with biological sex. Use attributes/roles, not subclasses.
  - Gender categories are **culturally relative** (§3.6): represent culture-specific categories within their cultural scheme with attribution; do not impose one culture's taxonomy as universal.
  - Use people's self-identification; keep language respectful and clinical where biological, respectful and person-centred where social. No contribution may be structured to demean or erase any sex or gender.
- **No modelling of private individuals' sensitive personal data.** WMOOP models *concepts and public reference instances* (the planets, chemical elements, notable public landmarks), not dossiers on private living people. Do not create instance records compiling personal data about private individuals (privacy carries over from GOVERNANCE and applicable law).

#### 3.2 Geography and politics

- **RED LINE — no single political POV on disputed status.** Disputed borders, territories, sovereignty, and nation/statehood status are **never** a single `country`/`sovereign` field. Model them as **multiple attributed claims**, with de-facto control and de-jure claims distinguished:
  ```yaml
  # Illustrative — a disputed territory holds claims, not a verdict
  territory:
    id: wmoop.geography/<NeutralId>
    sovereigntyClaims:
      - { claimant: entityA, basis: "de-jure claim", source: src:..., asOf: "2026" }
      - { claimant: entityB, basis: "de-facto control", source: src:..., asOf: "2026" }
    recognition:
      - { recognizedBy: "UN member states (N of M)", source: src:..., asOf: "2026" }
    note: "WMOOP records the claims and their sources; it does not declare a rightful owner."
  ```
- Place names that differ by viewpoint (**exonyms/endonyms, contested names**) are modelled as multiple `name` claims, each attributed, with usage/context — not one "correct" name that erases others.
- Administrative hierarchies (country → region → city) are fine as structure; it is *status and ownership* that must stay multi-viewpoint where contested.

#### 3.3 Religion and belief

- **RED LINE — belief is modelled as belief, with attribution; never asserted as objective fact.** Deities, doctrines, cosmologies, and religious histories are represented as **claims held by traditions**: "Tradition T holds that D created the world" (sourced to scholarship of that tradition) — not "D created the world."
- Model religions, philosophies, and ideologies as **belief systems** (a first-class concept) with their tenets attributed to the tradition and, where possible, to scholarly sources *about* the tradition.
- Treat all traditions even-handedly (NPOV, §2.1). Do not rank religions, assert one as true or false, or use disparaging framing. Scholarly factual claims *about* a religion (its history, demographics, textual tradition) follow normal Tier-A/B sourcing.

#### 3.4 Medical, legal, and financial content

- **RED LINE — descriptive only; never advice.** WMOOP may model medical, legal, and financial **concepts** (what a disease *is* per pathology; a drug's mechanism per pharmacology; what a contract *is*; what an index fund *is*) with Tier-A sourcing. It must **never** emit **advice**: no diagnoses, no "you should take X mg", no treatment plans, no legal counsel for a situation, no "buy/sell" or investment recommendations.
- Concepts in these areas carry a machine-readable flag that **forces a disclaimer** into generated artefacts and **blocks prescriptive/imperative phrasing** in definitions:
  ```yaml
  advisoryDomain: medical          # medical | legal | financial
  disclaimerRequired: true
  # Linter rejects imperative/prescriptive wording ("take", "you should", "invest in") in such concepts.
  ```
- Standard disclaimer text (emitted by codegen): *"WMOOP content is a descriptive knowledge model for educational and research use. It is not medical, legal, or financial advice. Consult a qualified professional."*

#### 3.5 Dangerous knowledge

WMOOP is an educational ontology, not an operational manual. Do not model **actionable instructions** for causing serious harm (e.g. synthesis routes for weapons, explosives, or bioagents; exploit recipes). Describing *that* a category of thing exists, at an encyclopedic level, is fine; **operational how-to that uplifts harm is not**. When in doubt, model the concept, omit the recipe, and ask a steward.

#### 3.6 Cultural relativity (cross-cutting)

Many categories are **culturally relative** — kinship systems, colour terms, "vegetable," foodways, calendars, gender categories, etymology. Flag these `culturallyRelative: true` and model culture-specific taxonomies within their own schemes (§2.5) with attribution, rather than universalising one culture's categories. This is both an epistemic and an ethical requirement.

---

### 4. Provenance and data ethics

1. **Provenance is mandatory and end-to-end** (Invariant I4; GOVERNANCE §10.2). Every claim traces to a `SOURCES.yaml` entry with license and tier.
2. **Respect upstream licenses and attribution.** Do not ingest license-incompatible data; do not strip required attribution (GOVERNANCE §10.2).
3. **Privacy.** No compilation of personal data on private living individuals (§3.1). Public reference instances only.
4. **No laundering of bias as fact.** Where a source is known to carry systemic bias, note it (`sourceCaveat`) rather than silently propagating it as neutral truth.

---

### 5. Ethics of AI contribution

AI is welcome and expected to contribute, under GOVERNANCE §8. The ethics-specific duties:

- **Disclose** AI involvement on every PR and in every claim's `method` (GOVERNANCE §8.1).
- **No fabricated sources — ever.** An AI (or human) that cites a source which does not exist or does not support the claim has committed the most serious epistemic violation in the project. Human reviewers verify citations before merge (GOVERNANCE §8.2).
- **AI must honour every red line in §3.** "A source said so" is not a licence to cross a red line; the modelling constraints apply regardless of source.
- **Humility over fluency.** When evidence is thin, the correct output is `confidence: uncertain` (or no claim), not a confident fabrication.

---

### 6. Reporting and enforcement

- **Factual/epistemic problems** (bad citation, NPOV breach, mis-tiered source): open an issue or PR; the domain steward adjudicates under lazy consensus; escalate per GOVERNANCE §4.2.
- **Red-line violations:** open a confidential report to the stewards/TSC (contact in [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)) or a public issue if non-sensitive. Red-line content is reverted immediately; deliberate or repeated violations lead to removal (GOVERNANCE §4.4).
- **Conduct problems** (harassment, bad-faith behaviour): Code of Conduct process, separate from technical review.

---

### 7. Amending this document

ETHICS.md — and especially the red lines in §3 — are changed only by **Meta-RFC with a TSC supermajority** (GOVERNANCE §5, §4.4), with an ADR recording the rationale. Clarifications that tighten or better explain an existing red line may be fast-tracked; **loosening a red line always requires the full supermajority process.**

---
---
