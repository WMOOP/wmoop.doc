<!-- Thanks for contributing to WMOOP! Fill this in; it maps to the Definition of Done. -->

## What does this PR change?

<!-- One or two sentences. Link the issue it closes: "Closes #123". -->

## Modelling decision

<!-- If you added or changed a concept, state which meta-model relation you used and WHY. -->

- [ ] **Inheritance** (`subclass_of`) — a genuine, permanent, substitutable *is-a*; hierarchy stays shallow.
- [ ] **Composition / Role** (`has_role`) — a contextual or cross-domain facet, not a subtype.
- [ ] **Part-of** (`part_of`) — a whole/part containment, not a subtype.
- [ ] **Category / tag** (`classified_as`) — a perspectival or contested classification.
- [ ] **Property / quality** (`has_quality`) — with units if measurable.

Rationale:

## Definition of Done (see CONTRIBUTING.md)

- [ ] Every new concept has a stable **id**, **name**, and **definition**.
- [ ] Every factual claim has **provenance** (a citation to a reputable source).
- [ ] Every measurable property carries a **unit**.
- [ ] No new **dependency cycle** between domains.
- [ ] Naming follows the conventions in the meta-model doc.
- [ ] Validators / conformance tests pass locally.
- [ ] Sensitive-domain rules in [ETHICS.md](../ETHICS.md) are respected (no race-as-biology,
      disputed geography/politics handled with provenance, beliefs attributed, no advice).

## AI-authored?

- [ ] This contribution was produced with AI assistance. If checked, I have followed
      [AI_CONTRIBUTING.md](../AI_CONTRIBUTING.md) (disclosure, grounding, small-PR discipline,
      human review) and I have personally verified every fact and citation.
