# Monotheism is not a base class

*Why the most natural way to sort the world's religions makes a bad object model — and what a
better one teaches about classification, neutrality and code.*

`<student name>` · Faculty of Theology, `<university>` · November 2026 · part of the
[`wmoop.religion`](WHITEPAPER.md) domain of WMOOP

## The question

Ask a class of first-year students to sort the world's religions and most will draw the same tree.
At the top, *Religion*. Below it, two boxes: *monotheistic* and *polytheistic*. Under the first,
Christianity, Islam and Judaism; under Christianity, Catholics, Orthodox and Protestants; under the
Protestants, Baptists and Pentecostals. It looks like biology, and it looks like object-oriented
programming: every box a class, every line an `extends`.

I drew that tree too, when I proposed a religion domain for WMOOP, an open project that describes
the world once, in a language-neutral model, and generates code from it in C#, Python and TypeScript.
The review of my first draft taught me more about my own subject than a semester of reading, and
this article is about what it taught.

## The first answer, and where it breaks

The trouble starts with the second row. *Monotheistic* is supposed to be a property every child
inherits. Then where does Hinduism go? Reference works describe it as polytheistic, as
henotheistic — the very word was coined for the hymns of the Vedas — as monotheistic in the devotion
of Vaishnavas to Vishnu, and as monist in the Advaita philosophy for which the self and the ultimate
reality are one. Buddhism and Jainism have gods in their cosmologies but no creator on whom
liberation depends; scholars call them non-theistic. Zoroastrianism is monotheist to some
scholars and dualist to others. Even Judaism, the textbook monotheism, is reconstructed by
historians as having passed through a stage in which Israel worshipped one god without denying
that others existed.

In programming terms, the box *monotheistic* breaks the Liskov substitution principle: something
said of the parent is not reliably true of the children. In scholarly terms, it treats an analytic
label — a word scholars apply from outside — as if it were the identity of a tradition.

The lower rows have a different problem. A `Baptist` class would add nothing to a `Protestant`
class, which would add nothing to `Christianity`: they all have a period of emergence, a region,
founders, texts and symbols, only with different values. Classes that differ only in data are not
classes; they are a table pretending to be a hierarchy. And *"Baptists are Protestants"* is not even
an is-a statement. It says that the Baptist tradition is a **branch within** Protestantism — a part,
not a kind.

## How WMOOP models it

The model that came out of the review has three moves.

**One shallow kind.** There is a single class for traditions, `ReligiousTradition`, under an
abstract `BeliefSystem`. Christianity, Islam, Protestantism and the Baptists are **instances** of it,
as Mars and Venus are instances of `Planet`.

**Branches are links between instances.** Each tradition may point to the tradition it is a branch
of, and separately to the traditions it historically emerged from without belonging to them. The
two links let the model say that Christianity emerged from Second Temple Judaism without being part
of it, and that the Bahá'í Faith emerged from Shia Islam although Bahá'ís, and Muslims, agree that
it is not a branch of Islam.

```yaml
- id: wmoop.religion/BaptistTradition
  name: Baptists
  instance_of: wmoop.religion/ReligiousTradition
  values:
    vitality: LIVING
    emergencePeriod: "1609 CE"
    originRegion: "English Separatist exiles in Amsterdam, Dutch Republic"
    parentTradition: wmoop.religion/Protestantism
    founders: [ wmoop.religion/JohnSmyth, wmoop.religion/ThomasHelwys ]
  classified_as:
    - { scheme: wmoop.religion/RomanianConfessionalGroups, value: NeoProtestant }
```

**Groupings are schemes.** *Monotheistic*, *Abrahamic* and *neo-Protestant* are kept, but as
**classification schemes**: named, sourced systems under which a tradition can carry one claim or
several. Hinduism carries four theism claims of equal rank, each with its source. Judaism carries a
current claim, monotheism, and a historical one, monolatry, dated to the period before the
Babylonian exile. And the Baptist tradition carries the claim *neo-Protestant* under a scheme for
Romanian usage, because that grouping, familiar to every Romanian theology student, is not used in
English-language scholarship. Nothing is deleted; nothing is promoted to a parent class.

From this file WMOOP generates code. In Python the Baptist tradition becomes a typed instance whose
lineage a program can walk:

```python
from wmoop.religion import ReligiousTradition as T

t, chain = T.BaptistTradition, []
while t is not None:
    chain.append(t.name)
    t = t.parent_tradition
print(" -> ".join(chain))      # Baptists -> Protestantism -> Christianity
```

## What else changed

The rest of my original list of properties survived, but almost every one was renamed, and each
rename is a small lesson.

*Founding year* became an **emergence period** in words — *"no single beginning; Vedic roots
c. 1500–500 BCE"* — with sortable years beside it, because most traditions took shape over centuries
and some deny having a beginning at all.

*Founder* became **figures regarded as founders**, each with a stated **historicity**: historians
agree that the Buddha, Muhammad and Guru Nanak lived; they debate Moses and Laozi; Abraham is known
only from scripture. Islam itself does not call Muhammad a founder but the last of the prophets. The
tradition's account and the historian's are two claims, and the model keeps both.

*The name of God* became a **conception with many names**. The Hebrew Tetragrammaton, which
observant Jews do not pronounce; *Allāh*, the Arabic word for God that Arab Christians use too; the
Trinity — each is recorded as a tradition's conception, with its names in every language as labels.
Whether two traditions worship the same God is not a question a data model should answer.

*Logo* became **symbol**, stored as a Unicode character, because traditions have symbols, not
trademarks — and the notes say that many Muslims do not regard the star and crescent as a religious
symbol at all.

*Country* became a **historical region** — *Judaea and Galilee, Roman Empire* — because projecting
ancient regions onto modern states is anachronistic and, in some places, takes a side.

And one thing was never added: a property that records a person's religion. A model that can be
used to label people by belief is a model that can be used against them.

## What this teaches beyond the domain

Three lessons travel well beyond religion. First, **a classification is a claim made by someone**,
and a good model records who made it rather than hard-coding it into structure. Second, **inheritance
is for kinds, not for groupings**: when the children of a class differ only in data, or when the
grouping depends on the point of view, the right tool is an instance, a link or a scheme. Third,
**neutrality is a design property**: attribution, schemes and open-world lists make it possible to
describe contested subjects fairly, and their absence makes it impossible however careful the
wording.

The tree I drew on the first day is still useful — as one scheme among several, with its sources.

## Further reading

- Smart, N. (1996). *Dimensions of the Sacred: An Anatomy of the World's Beliefs*. University of California Press.
- Masuzawa, T. (2005). *The Invention of World Religions*. University of Chicago Press.
- Smith, M. S. (2002). *The Early History of God*, 2nd ed. Eerdmans.
- Harvey, P. (2000). *An Introduction to Buddhist Ethics*. Cambridge University Press.
- The domain design document: [WHITEPAPER.md](WHITEPAPER.md).
