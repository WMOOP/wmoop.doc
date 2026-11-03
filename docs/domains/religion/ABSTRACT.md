# `wmoop.religion` — Religion: abstract

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

*Status: Proposed · Steward: `<student name>` (Faculty of Theology) · Issue: [ISSUE.md](ISSUE.md) ·
Whitepaper: [WHITEPAPER.md](WHITEPAPER.md) · Model: [`religion.wml.yaml`](../../../model/religion/religion.wml.yaml)*
