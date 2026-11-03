<!--
Copy to docs/domains/<id>/WHITEPAPER.md. Keep every numbered section; write "None." rather than
deleting one. Guide: docs/08-contributing-a-domain.md §2.3 (outline) and §3 (writing standard).
Delete these comments.
-->

# `wmoop.<id>` — <Domain Title>
### Domain design document

| | |
|---|---|
| **Module** | `wmoop.<id>` |
| **Version proposed** | 0.1.0 |
| **Status** | Proposed |
| **Cluster** | <foundation \| formal \| natural \| place \| society \| culture \| technology \| health> |
| **Depends on** | `wmoop.core` ^1.0.0, … |
| **Steward(s)** | <name, affiliation> |
| **Issue** | <link> |
| **Last updated** | <YYYY-MM-DD> |

---

## 1. Abstract

<The text of ABSTRACT.md, verbatim.>

## 2. Motivation and use cases

<Why this domain belongs in WMOOP. Then two or three concrete uses, each one sentence: who uses the
model and what they do with it (a course exercise, a data integration, an application feature).>

## 3. Scope

**In scope.**
- <…>

**Out of scope.**
- <…> — <why, and where it belongs instead>

**Neighbouring domains.** <Which existing or candidate domains border this one, and where the border
runs. Name the concepts you reuse by id.>

## 4. Background

<The scholarly frame of the subject in a few paragraphs: the standard vocabulary, the main reference
works, the classification systems in use, and the known debates. Every claim cited (author–date).>

## 5. Analysis — from the first sketch to the model

<The model a newcomer would draw first (a diagram or a list), then each problem with it and the
change it leads to. One subsection per problem: what the sketch says, why it fails (which rule,
which counter-example), what the model does instead.>

### 5.1 <Problem>

## 6. The model

<A class diagram (mermaid `classDiagram`), then:>

| Node | WML kind | L0 category | Stereotype | Purpose |
|------|----------|-------------|------------|---------|
| `wmoop.<id>/<Name>` | concept / role / datatype / enumeration / scheme | Endurant / Perdurant / Abstract | Kind / Subkind / Role / Category / … | <one line> |

**Reference individuals (L2).** <Which concepts have individuals, how many, chosen how.>

## 7. Property catalogue

| Property | Type | Card. | Meaning | Why it exists | Source |
|----------|------|-------|---------|---------------|--------|
| `<Concept>#<prop>` | | | | | |

## 8. Classification schemes

<For each scheme: what it classifies, its authority and consensus level, its values, and two or three
example claims, including at least one contested one.>

## 9. Ethics and neutrality

<Answer every line of the checklist in docs/08-contributing-a-domain.md §5, and any red line of
ETHICS.md §3 that this domain touches.>

## 10. Validation

```bash
python schema/validate_wml.py --strict
python tools/gen_taxonomy.py --check
```

<Paste the summary line of the green run.>

## 11. Roadmap

| PR | Content | Nodes |
|----|---------|-------|
| 1 | module header, identity root, taxonomy entry | ≤ 5 |

**Later sub-domains.** <…>

## 12. Open questions

1. **<Question>** — options: (a) …, (b) …; proposed: …

## 13. References

<Author, A. (Year). *Title*. Publisher. ISBN/DOI. — one style throughout, alphabetical.>
