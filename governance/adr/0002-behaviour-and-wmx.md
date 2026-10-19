<!--
SPDX-License-Identifier: CC-BY-4.0
Part of the WMOOP project (World Map Object-Oriented Programming) — github.com/WMOOP
-->

# ADR 0002 — Invariant 1 covers data + constraints + pure derivations; behaviour via WMX

- **Status:** **Proposed** (2026-10-19) — pending ratification. Scoping a normative invariant (I1) is a **Meta-RFC + TSC supermajority** change ([GOVERNANCE.md](../../GOVERNANCE.md) §5/§12); the doc edits are provisional until then.
- **Deciders:** TSC (to ratify); drafted from the design review
- **Resolves:** the behaviour gap in Invariant 1; architecture (`docs/03-architecture.md`) §7 open questions 3 & 6
- **Invariants:** I1 (scoped/clarified, not loosened)

## Context

OOP is defined by **behaviour** (methods), but WML is almost entirely **data** (properties, relations, constraints). The generation-gap pattern puts every method body in the **hand-written** half, per language — so each behaviour is re-authored in C#, Java, Python and C++ by hand and can silently **drift**, and conformance pins only structure, constraints and serialization, not behaviour. Even a universal, language-neutral formula (circle `area`, `canDrive`, a unit conversion) must be written four times. So "write once, replicate everywhere" holds for the data skeleton, not for the part of OOP that is behaviour. (Adversarial review finding #1.)

## Decision

1. **Scope Invariant 1** to **data structure + declarative constraints + PURE DERIVATIONS**. The *conceptual model* (types, properties, relations, roles, constraints, and pure derivations) is authored once and generated; it is never hand-copied across languages.
2. **Introduce WMX** — a small, **sandboxed, total, deterministic, language-neutral expression language** — for pure functions: derived properties, `invariant` expressions, unit conversions, and pure operations such as `area`/`perimeter`/`canDrive`. WMX expressions are **code-generated into every binding AND behaviour-conformance-tested** with input→output vectors, so they cannot drift.
3. **Declare imperative behaviour OUT of the single-source guarantee.** I/O, side-effecting, and heuristic behaviour is **per-binding**, hand-written, and a **known drift surface**; where cross-language agreement matters it carries its own input/output conformance vectors, but it is not claimed to be generated.
4. **WMX is pure and total:** no I/O, no mutation, no unbounded loops/recursion; bounded time/memory; the same inputs yield the same outputs in every binding (this is also the security sandbox — see `SECURITY.md`).

This resolves architecture §7 open question 3 (expression language → WMX) and open question 6 (behaviour conformance → WMX behaviours are conformance-tested; hand-written behaviour is explicitly out of scope).

## Consequences

- The whitepaper/abstract and the Invariant 1 wording are corrected: WMOOP generates **data structure + declarative constraints + pure derivations**; imperative behaviour is per-binding and a declared drift surface.
- **New, planned:** the WMX grammar + evaluator (one shared reference evaluator, plus a per-language emitter), a **behaviour** conformance-vector category (input→output), and a sandbox. These are a tracked follow-up — WMX does not exist yet (nor does the generator; see `docs/05-adversarial-review.md`).
- Pure, universal formulas stop being a four-times-written drift surface.

## Alternatives considered

- **Keep behaviour hand-written, claim nothing changes.** Rejected: it leaves the "write once" claim false for behaviour and the pure formulas a drift surface.
- **A full (Turing-complete) behaviour language.** Rejected: not sandboxable/total, and most imperative behaviour is genuinely per-binding; WMX deliberately covers only pure, total functions.

## Follow-ups

1. Specify the WMX grammar + the reference evaluator + per-language emitters.
2. Add the `behaviour` conformance-vector category (input→output) and wire WMX into the DoD.
3. Move the universal pure formulas (area/perimeter, canDrive, unit conversions) from the hand-written half into WMX.
