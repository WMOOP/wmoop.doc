---
name: wml-contribute
description: >-
  Turn a well-documented source into a conformant WML contribution to this repo
  (edits in model/** only) — one concept or a tight sibling cluster. Use whenever the
  task is to add, model, or extend a domain/concept/property from a source (a standard,
  dataset, paper, or textbook), or to author/propose/review WML here. Extracts the
  concepts, maps each to the right L0 stereotype (is-a vs role vs quality vs category),
  fills every slot with its own definition + provenance, extends existing concepts by
  ADDING (roles/qualities) rather than editing them, then self-verifies against the
  machine-checkable Definition of Done before opening a small, green, disclosed PR.
---

# Contribute WML from a source

You are authoring a contribution to the **WMOOP canonical model** (`model/**`). The normative
protocol is **`AI_CONTRIBUTING.md`** and **`CONTRIBUTING.md`** (read them if you have not); the WML
shape and its rules are in **`docs/03-architecture.md`**, the meta-model decision rules in
**`docs/02-meta-model.md`**, and the pattern/abstraction standard in **`PATTERNS.md`**. This skill is
the operational checklist that runs those docs in order. Do not skip the gates, and do not restate
source prose as your own.

## Preconditions (stop here if unmet)

- You have a **well-documented, resolvable source** (standard + clause, paper + DOI, official dataset
  + URL + `retrieved` date, textbook + ISBN + page). **No resolvable source → open an issue, do not
  author** (`AI_CONTRIBUTING.md` §5–6).
- You will touch **only `model/**`** — never generated bindings, `wmoop.json`, or L0 (`_meta`).
- The change is **small**: one concept or a tight cluster, **≤ 5 node files**, one logical concern.

## The loop — in = source, out = exactly the needed WML

Follow `AI_CONTRIBUTING.md` → *"The generation workflow — from a well-documented source to
conformant WML"*, which is the authoritative version of these steps:

1. **Qualify the source**; if not resolvable, open an issue instead of authoring.
2. **Scope** to one atomic unit (≤ 5 files); reuse existing concepts/datatypes/properties before
   creating new ones.
3. **Classify each thing against the L0 stereotypes _before_ writing** (`docs/03-architecture.md`
   §1.4; `PATTERNS.md` prime directive):
   - genuine shallow substitutable **is-a** → `subclass_of`;
   - contextual, non-permanent **facet** → a **role** by composition (an agentive noun — Driver,
     Owner, Employee, **Student**, **Teacher** — is almost always a role, *never* a subclass);
   - measurable **attribute** → `quality`/Quantity **with a unit**;
   - **perspectival/contested** category → `classified_as` / multiple sourced schemes, not a forced
     tree;
   - **part-whole** → `part_of`; general link → `association`/relation with an inverse.
4. **Fill the slots:** stable ID (S6), name, a concise **own-words** definition, parent or role
   target, and **properties — each with its own `definition` and `provenance`** (per-property rule,
   S5), a `unit` on every quantity, and a cardinality.
5. **Source everything, honestly typed:** every concept, role, enumeration **and property** carries
   `provenance` — `kind: sourced` + resolvable citation for a fact; `kind: definitional`/`convention`
   for a modelling/naming choice. Never dress a convention as a fact.
6. **Extend by _adding_, never by editing the base** (`docs/03-architecture.md` §4.5). To let a
   `Person` act as a Student/Teacher/Driver, add that **role** in the appropriate (possibly new)
   domain `played_by wmoop.nature/Person`; the base concept is untouched.
7. **Apply the engineering standard** (`PATTERNS.md`): best-established patterns at the **right** level
   of abstraction — proven over clever, no over-engineering.

## Before you finish

- Run the oracle: `wmoop validate && wmoop lint && wmoop conformance`, then the
  `AI_CONTRIBUTING.md` §8 self-verification checklist.
- **Disclose:** fill `contributedBy.agent`, add the `Assisted-by:` commit trailer, label the PR
  `ai-authored`, name a human **sponsor** (§4).
- **Flag uncertainty** (`confidence` / `uncertain` / `disputed`) rather than smoothing it over (§6).
- Open a **≤ 5-file, all-green** PR with the `ai_contribution` block (§13) — or, if anything is
  unsourced or shaky, open an **issue** instead. Never self-merge; never `--force` or bypass a gate.

## How this skill is invoked

- **Automatically, by description.** An agent working in this repo should invoke `wml-contribute`
  whenever a task means turning a source into WML, or when a contributor asks to add, model, or
  extend a concept or domain. The description above is the trigger.
- **Explicitly.** A contributor can run `/wml-contribute`.
- **As an enforced gate (optional).** To make it fire on every contribution rather than relying on
  description-matching, wire it as a `UserPromptSubmit` (or pre-PR) hook; the hard enforcement
  backstop stays the CI oracle — `wmoop validate && wmoop lint && wmoop conformance`. Ask a
  maintainer before adding the hook, since it changes contributor-side behaviour.
