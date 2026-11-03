# Worked example — the domain proposal issue for `wmoop.religion`

This is the issue as a theology student would open it with the
[New domain](../../../.github/ISSUE_TEMPLATE/new-domain.yml) form, after reading
[Contributing a Domain](../../08-contributing-a-domain.md). The [appendix](#appendix--the-first-draft-and-what-review-changed)
shows the first draft and the review comments that turned it into this version.

---

> **Title:** `[domain] Religion`
> **Labels:** `domain`, `needs-triage`

### Module id

`wmoop.religion`

### Cluster

culture

### Abstract

Religious traditions shape the beliefs, ethics, calendars and institutions of most of humanity, yet
they resist object-oriented modelling: the familiar division into monotheistic and polytheistic
religions breaks on Hinduism, Buddhism and Jainism, branches such as Baptists or Sunni Islam are
parts of larger traditions rather than subtypes, and almost every classification is contested by
someone. `wmoop.religion` models religions as belief systems whose claims are attributed, never
asserted. A shallow identity tree, `BeliefSystem → ReligiousTradition`, carries every tradition as a
reference individual; branches are linked by a part-whole `parentTradition` and historical
derivation by `emergedFrom`; theism type, religious family and regional groupings such as the
Romanian "neo-Protestant" are first-class classification schemes holding sourced, sometimes
competing claims. Deities (as conceptions), founders and prophets (with their historicity stated),
doctrines, values, precepts, sacred texts, symbols and events are concepts of their own, and
religious organizations such as the Romanian Orthodox Church are kept apart from the traditions they
belong to. Version 0.1.0 has 13 concepts, one role, four schemes and 113 reference individuals,
among them 33 traditions in six families. It leaves out personal religious affiliation, which is a
protected attribute, and defers demographics, rituals, festivals and mythology to later sub-domains.

### Scope

**In scope:**
- Religious traditions and their branches, as L2 individuals linked by `parentTradition` and `emergedFrom`.
- What traditions hold, attributed to them: deities (as conceptions), doctrines, ethical values, precepts and precept sets.
- Founders, prophets and reformers as `ReligiousFigure`s with their historicity stated.
- Sacred texts, symbols (Unicode where possible), key historical events.
- Religious organizations (churches, unions, federations) as organizations of a tradition, with their legal status in a jurisdiction.
- Classification schemes: theism typology, religious families, Romanian legal status, Romanian confessional groups.

**Out of scope (and where it belongs instead):**
- The religion of any person — a protected attribute; never modelled (ETHICS.md §3.1).
- Theological truth claims, apologetics, devotional content — not descriptive.
- Demographic estimates — later sub-domain `religion.demographics`, once values can carry `asOf`.
- Rituals, rites of passage, festivals and liturgical calendars — later sub-domains `religion.practice` and `religion.calendar`.
- Mythological narratives — the registered sub-domain `religion.mythology`.
- Places of worship as buildings — `wmoop.architecture` (`Building`), with a role or relation from this domain.
- Philosophies and ideologies that are not religions — `wmoop.philosophy`; `BeliefSystem` is offered as a shared root by a separate issue.

**Neighbouring domains:**
- `wmoop.org` — `ReligiousOrganization` extends `wmoop.org/Organization`.
- `wmoop.nature` — the `Cleric` role is played by `wmoop.nature/Person`.
- `wmoop.philosophy` — doctrines border philosophical positions; no dependency in either direction for now.
- `wmoop.geography` — origin regions are historical names in text, not links to modern states (ETHICS.md §3.2).

### Depends on

`wmoop.core ^1.0.0, wmoop.nature ^0.7.0, wmoop.org ^0.1.0`

### Seed concepts

| Name | Stereotype | Definition | Relation |
|------|------------|------------|----------|
| `BeliefSystem` | Kind (abstract) | A coherent body of beliefs, values and practices about what is ultimately real, meaningful or valuable, shared by a community and passed on over time. | identity root |
| `ReligiousTradition` | Subkind | A belief system passed on as a lineage of teachings, practices, narratives and institutions oriented to what a community holds sacred or ultimate. | `extends BeliefSystem`; branches via `parentTradition` (part-whole) |
| `TheismTypology` | Scheme | Monotheism, polytheism, henotheism, pantheism, nontheism, … as sourced, possibly multiple claims per tradition. | `classified_as` |
| `ReligiousFamilies` | Scheme | Abrahamic, Indian, Iranian, East Asian, indigenous, new religious movements; common usage, with its critique cited. | `classified_as` |
| `ReligiousOrganization` | Subkind | An organization through which a community of a tradition is governed. | `extends wmoop.org/Organization` |

### Contested classifications and uncertainty

- **Theism type.** Hinduism is described as polytheistic, henotheistic, monotheistic or monist
  depending on the strand; Buddhism and Jainism as non-theistic. Each tradition gets one sourced
  claim per view under `TheismTypology`; no view is the parent class.
- **Branch placement.** Whether the Latter Day Saint movement is part of Christianity (its own
  view, and common religious-studies usage) or outside it (the view of many other Christian
  churches); whether Anglicanism is Protestant; whether Vajrayāna is a third vehicle or part of
  Mahāyāna. The default placement follows descriptive religious-studies usage and the note records
  the rival views with sources.
- **"Neo-Protestant".** A grouping common in Romanian scholarship and usage that no official list
  uses, whose name Romanian historians themselves debate, and that English-language scholarship does
  not use; modelled as a regional scheme, never as a class.
- **Founders and dates.** Islam regards Muhammad as the final prophet, not a founder; Hinduism has
  no founder; the dates of the Buddha and of Zarathustra are debated. Founding is an attribution
  and every date keeps its uncertainty in words.
- **Is it a religion?** Confucianism and philosophical Daoism are classified as religions by some
  sources and as philosophies by others; they stay out of the first version until stewards decide
  (whitepaper §12).

### Sources

**Tier A:**
- Smart, N. (1996). *Dimensions of the Sacred*. University of California Press. — the seven dimensions behind the property list.
- Masuzawa, T. (2005). *The Invention of World Religions*. University of Chicago Press. — critique of the family grouping.
- Harvey, P. (2000). *An Introduction to Buddhist Ethics*. Cambridge University Press. — the Five Precepts.
- Legea nr. 489/2006 privind libertatea religioasă și regimul general al cultelor; H.G. nr. 741/2024. — Romanian legal status (18 denominations in the law's annex, 19 since 2024).
- Modoran, G. (2007). "Confesiunile neoprotestante din România în perioada regimului comunist: 1945–1965". *Studia Politica* 7(3). — the neo-Protestant grouping.

**Tier B:**
- Jones, L. (ed.) (2005). *Encyclopedia of Religion*, 2nd ed. Macmillan Reference USA. — per-tradition facts, by entry.
- Encyclopaedia Britannica, by entry. — per-tradition facts, theism typology.
- Pew Research Center (2025). *How the Global Religious Landscape Changed From 2010 to 2020*. — scope check; demographics later.
- Institutul Național de Statistică (2023). Census 2021, table 2.4.1. — the Romanian context.

**Tier C (identifiers / corroboration only):**
- Wikidata item identifiers, for cross-reference.

### Sensitive-domain checklist (ETHICS.md §3)

- [x] Beliefs, doctrines and contested histories are attributed to their holders, never asserted as fact.
- [x] No property or role classifies persons by a protected attribute (religion, ethnicity, sexual orientation, health, …).
- [x] No private living person appears as an individual.
- [x] Disputed places and statuses are not reduced to one point of view.
- [x] Nothing is phrased as medical, legal or financial advice.
- [x] Images, symbols and texts are reused only under a licence that allows it.

### PR plan

1. **PR 1** — module header, `BeliefSystem`, `ReligiousTradition`, `HistoricalYear`, `TraditionVitality`; taxonomy entry `candidate → seeded` and regenerated diagrams.
2. **PR 2** — the four schemes (`TheismTypology`, `ReligiousFamilies`, `RomanianLegalStatus`, `RomanianConfessionalGroups`).
3. **PR 3** — `Deity`, `ReligiousFigure` + `Historicity`, `SacredText`, `ReligiousSymbol` + `UnicodeCodePoint`.
4. **PR 4** — `Teaching` → `Doctrine`, `EthicalValue`, `Precept` (+ `PreceptPolarity`), `PreceptSet`.
5. **PR 5** — `ReligiousEvent`, `ReligiousOrganization`, the `Cleric` role.
6. **PR 6..8** — individuals, one family per PR (Abrahamic; Indian; Iranian, East Asian and historical).

### Stewardship

`<student name>`, 3rd-year student, Faculty of Theology (`<university>`), with `<supervisor name>`,
lecturer in History of Religions, as co-steward until the domain has two independent stewards.
GitHub: `<student-handle>`, `<supervisor-handle>`.

### Notes and open questions

1. Should `BeliefSystem` live in this module or in a shared module that `wmoop.philosophy` can also extend?
2. Is the default branch placement (descriptive religious-studies usage, self-identification first) acceptable as the domain's default projection under ADR 0001 decision 4, or should it be ratified by its own ADR?
3. Confucianism and philosophical Daoism: model now with a "religion or philosophy" scheme claim, or wait?

Full design: `docs/domains/religion/WHITEPAPER.md` (linked once the dossier PR is open).

---

## Appendix — the first draft, and what review changed

The student's first draft was a single paragraph:

> *I want to write about religion. There are two categories: monotheistic and polytheistic.
> Monotheistic religions are Christianity, Islam, Hinduism, Buddhism and Judaism. Christianity
> divides into Protestants, neo-Protestants, Baptists, Mormons, etc. Islam has Sunnis and Shias.
> Common properties: values, the name of God or the gods, laws and commandments, founding year,
> doctrine, country, founder, main events, logo.*

The subject and the property list were a good start: almost every property survived, renamed. The
review comments a steward would leave, and where the answer now lives:

| # | Review comment | Change | Where |
|---|----------------|--------|-------|
| 1 | Hinduism is not usually described as monotheistic, and Buddhism and Jainism are non-theistic. A tradition that does not fit the parent class breaks Liskov. | Theism type is a scheme with sourced, possibly multiple claims. | Whitepaper §5.1, §8 |
| 2 | Christianity, Islam and Baptists differ in data, not in structure. | Traditions are L2 individuals of one class. | §5.2 |
| 3 | "Baptists" is a branch *of* Protestantism, which is a branch *of* Christianity: part-whole, not is-a. The list also mixes levels. | `parentTradition` links; the levels are put right. | §5.3, §5.4 |
| 4 | Catholicism, Eastern Orthodoxy and Oriental Orthodoxy are missing. | Added. | §5.4 |
| 5 | The Latter Day Saint movement is not Protestant, and its place in Christianity is disputed. | Placed under Christianity with the dispute recorded and sourced; alternate label "Mormon". | §5.4, §9 |
| 6 | "Neo-Protestant" is Romanian usage; English scholarship does not use it. | A regional scheme. | §5.5, §8 |
| 7 | Most traditions have no founding year, and some reject having a founder. | `emergencePeriod` in words + years; `founders` as an attribution. | §5.6 |
| 8 | "The name of God" mixes a being, its conception and its names in many languages. | `Deity` (a conception) with multilingual labels. | §5.7 |
| 9 | Religions have symbols, not logos; logos of organizations may be trademarks. | `ReligiousSymbol` with a Unicode code point. | §5.8 |
| 10 | "Country" of origin: modern states are anachronistic and can be disputed. | `originRegion`, the historical name. | §5.6, §9 |
| 11 | A religion and a church are different things. | `ReligiousOrganization` apart from `ReligiousTradition`. | §5.9 |
| 12 | No sources, no scope, no plan, no steward. | Tiered sources, scope, PR plan, stewardship. | this issue |
