<!--
SPDX-License-Identifier: CC-BY-4.0
Part of the WMOOP project (World Map Object-Oriented Programming) — github.com/WMOOP
-->

# ADR 0003 — `wmoop.js` (TypeScript) is a conformance-gated v1 binding

- **Status:** **Proposed** (2026-11-03) — pending ratification. Changing a normative constant of [GOVERNANCE.md](../../GOVERNANCE.md) is a **Meta-RFC + TSC supermajority** change (§5/§12). The edits merged in WMOOP/wmoop.doc#20 are provisional until then.
- **Deciders:** core maintainer (approved the move on 2026-11-03); TSC (to ratify)
- **Resolves:** the question WMOOP/wmoop.doc#19 asked. [GOVERNANCE.md](../../GOVERNANCE.md) §1.1 listed `wmoop.js` as a planned binding, although it is generated and runs every active conformance vector.
- **Invariants:** I1, I6 (applied to one more binding, not changed)

## Context

GOVERNANCE.md §1.1 names the bindings that are held to the conformance contract. Before this decision it listed:

- **Conformance-gated bindings (v1):** `wmoop.net` (C#), `wmoop.java`, `wmoop.py`, `wmoop.cpp`;
- **Planned bindings (not yet conformance-gated):** `wmoop.js`, `wmoop.db`.

On 2026-11-03 `wmoop.js` became the TypeScript binding, built the same way as `wmoop.net` and `wmoop.py`:

- **Generated code.** `wmoop.tools` generates its data classes into `generated/` (`--lang typescript`, WMOOP/wmoop.tools#19). CI regenerates them from the pinned `wmoop.doc` and `wmoop.tools` and fails on any difference.
- **Hand-written behaviour.** It is added with the kernel's `extend()` plus module augmentation (`declare module`) in `src/ext/`, so regeneration never touches it. This is the generation gap of [`docs/03-architecture.md`](../../docs/03-architecture.md) §2.2.
- **Conformance.** Its runner, `src/conformance.ts`, runs the shared vectors of `conformance/suite.json` (WMOOP/wmoop.js#2), and CI fails on any failing active case. On 2026-11-03 it reported 25 passed, 0 failed, 3 pending, the same as `wmoop.net` and `wmoop.py`.
- **Regeneration.** A green `main` in `wmoop.doc` or `wmoop.tools` asks it to regenerate (WMOOP/wmoop.doc#18, WMOOP/wmoop.tools#20). A regeneration whose build or tests fail opens no pull request.

So `wmoop.js` already met every condition the gated bindings meet. Only the table still called it planned.

## Decision

1. `wmoop.js` (TypeScript) moves to **Conformance-gated bindings (v1)** in GOVERNANCE.md §1.1, next to `wmoop.net`, `wmoop.java`, `wmoop.py` and `wmoop.cpp`. `wmoop.db` stays the only planned binding.
2. `wmoop.js` is held to the same contract as the other gated bindings:
   - its model code is generated and never edited by hand;
   - it is conformant at a model version only when every active vector passes in its CI ([`docs/03-architecture.md`](../../docs/03-architecture.md) §3.4).
3. The texts that restate §1.1 name it with the other four (WMOOP/wmoop.doc#20).

## Consequences

- One model edit now reaches five conformance-gated bindings, and the contributor guides say so.
- When a `pending` vector becomes active, `wmoop.js` must pass it too. The three pending rules now need a TypeScript implementation as well: property constraints, role capabilities and canonical serialization.
- Gaps against the rest of the spec remain. They do not block this decision:
  - [`docs/03-architecture.md`](../../docs/03-architecture.md) §4.5 (a) asks every binding for one package per domain. `wmoop.js` has a single package, marked `private`, and publishes nothing yet.
  - Some per-language lists have no TypeScript entry yet:
    - deprecation annotations (GOVERNANCE.md §6.4);
    - extension points ([`docs/02-meta-model.md`](../../docs/02-meta-model.md) §9);
    - the member names in [`docs/03-architecture.md`](../../docs/03-architecture.md) §3.4–§3.5.
  - The pattern helpers of `wmoop.py` (`wmoop/patterns.py`) have no TypeScript port yet.

## Alternatives considered

- **Keep `wmoop.js` planned.** Rejected for two reasons:
  - it already passes the same gate, so the table misdescribed it;
  - the contributor guides understated how many bindings one model edit reaches.
- **A separate tier, "generated but not gated".** Rejected: it would add a status no other binding has, for a binding that already passes the same gate.

## Follow-ups

1. Add the TypeScript entries to the per-language lists named under Consequences.
2. Decide how `wmoop.js` is packaged and published (§4.5 (a)).
