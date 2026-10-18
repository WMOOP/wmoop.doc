# WMOOP — Brand & Logo System

> One mark for the world model; one derived mark per language. The logo is built the
> same way the project is: a single canonical thing, specialised per language by
> mechanical rules — never redrawn from scratch.

All assets are **SVG** (vector, theme-friendly, editable text). Open
[`preview.html`](preview.html) in a browser to see the whole system in light and dark.

📖 **Full design document:** [`DESIGN.md`](DESIGN.md) — the design rules, the embedded
logo gallery, the palette, and the per-repo recipe, all in one page.

---

## What the mark means

The concept mark is a **wire globe** (the *World*) whose intersections carry **nodes**
— objects / classes — linked into a **graph** (the object-oriented model). One node is
**amber**: it is a **role**, attached to the whole by a **composition diamond**. That is
the project's central thesis drawn into the logo — *composition and roles over deep
inheritance* (the `Person` → `Driver` example from the README), Invariant #3.

So the identity is not decoration: it is the architecture, made visible.

---

## File map

| File | Use |
|------|-----|
| `logo/wmoop-mark.svg` | **Primary logomark** (full colour). App icon, avatar, favicon source. |
| `logo/wmoop-mark-mono.svg` | Single-colour mark (uses `currentColor`). Stamps, favicons, embossing. |
| `logo/wmoop-emblem.svg` | **Academic / community seal** — the *scientific concept*. Papers, slides, the community hub. Best on light/neutral backgrounds. |
| `logo/wmoop-logo-light.svg` | **Organisation lockup** for light backgrounds. |
| `logo/wmoop-logo-dark.svg` | Organisation lockup for dark backgrounds. |
| `logo/wmoop-logo.svg` | Organisation lockup that flips automatically with the OS theme (`prefers-color-scheme`). |
| `repos/wmoop.<ext>.svg` | **Per-repo lockups** — one per language binding. |
| `template/wmoop.repo-template.svg` | The blank per-repo frame + recipe, for new bindings. |

### GitHub README tip — auto light/dark

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="brand/logo/wmoop-logo-dark.svg">
  <img alt="WMOOP" src="brand/logo/wmoop-logo-light.svg" width="360">
</picture>
```

---

## Palette

| Token | Hex | Role |
|-------|-----|------|
| Globe start | `#2563EB` | globe gradient (blue) |
| Globe end | `#06B6D4` | globe gradient (cyan) |
| Edge | `#3B82F6` | relations / graph edges |
| Node stroke | `#1D4ED8` | object outlines |
| Ink | `#0F172A` | wordmark on light |
| Paper | `#F8FAFC` | wordmark on dark |
| Muted | `#475569` | taglines |
| **Role / composition** | `#F59E0B` | the amber role node + diamond (accent — use sparingly) |

On dark backgrounds the globe lightens to `#60A5FA → #22D3EE` and the role accent to
`#FBBF24` (see `wmoop-logo-dark.svg`).

### Language colours (per repo)

| Repo | Colour | Glyph |
|------|--------|-------|
| `wmoop.doc` | `#475569` slate | stacked document sheets |
| `wmoop.net` | `#512BD4` | `#` (sharp — C#/.NET) |
| `wmoop.java` | `#E76F00` | coffee cup |
| `wmoop.py` | `#3776AB` + `#FFD43B` | two interlocking squares |
| `wmoop.cpp` | `#00599C` | `C++` |
| `wmoop.tools` | `#0D9488` teal | gear |
| `wmoop.js` | `#CA8A04` gold | yellow `JS` tile |
| `wmoop.json` | `#E11D48` rose | `{ }` braces |
| `wmoop.db` | `#15803D` green | database cylinder |

> The glyphs are **original, simplified renderings**, not the official language logos.
> Language names and signature colours are used nominatively, only to identify which
> binding a repo holds.

---

## The per-repo pattern (how to add a new language)

Everything that is **the model** stays constant: the blue→cyan globe, the graph, and
the amber role + composition diamond. Only three things change per repo:

1. a **language-coloured orbit ring** around the globe (`<circle r="51">`),
2. a **corner chip** (white tile, coloured border) holding the **language glyph**, and
3. the coloured **`.ext`** in the wordmark.

To make `wmoop.<new>`:

1. Copy `template/wmoop.repo-template.svg` to `repos/wmoop.<ext>.svg`.
2. Replace the placeholder colour (`#94A3B8`) everywhere with the language colour.
3. Swap the chip glyph (centred at `(98,98)` inside the `scale(0.85)` group). Copy one
   of the six built-in glyphs from the matching `repos/*.svg` as a starting point.
4. Set the wordmark `.ext` and the one-line role in the tagline.

Keep the globe, ring radius, chip position, and the composition/role motif unchanged —
that consistency is the brand.

---

## Usage

**Do** — give the mark clear space (≈ half its height on all sides); use the mono mark
below ~24 px; use the auto or matching light/dark lockup for the background.

**Don't** — recolour the globe per repo (only the ring/chip/`.ext` carry language
colour); stretch or rotate the mark; move the amber role node to a different spoke; drop
the composition diamond (it is the point).

---

## Licensing

These brand assets are part of `wmoop.doc` and released under **CC-BY-4.0** like the rest
of the model data & documentation — reuse must credit the WMOOP project and link back to
<https://github.com/WMOOP/wmoop.doc> (see [`../LICENSE-DATA.md`](../LICENSE-DATA.md)).
The **WMOOP name, wordmark, and marks** identify the project; please don't use them to
imply endorsement of a fork or unaffiliated work.
