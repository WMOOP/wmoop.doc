<!--
SPDX-License-Identifier: CC-BY-4.0
Part of the WMOOP project (World Map Object-Oriented Programming) — github.com/WMOOP
-->

# ADR 0004 — Folders inside a module, and sub-modules for large domains

- **Status:** **Proposed** (2026-11-05) — pending ratification. It changes the validator's layout rule (S6) and the code generators of every binding, so it needs an **RFC + TSC ratification** ([GOVERNANCE.md](../../GOVERNANCE.md) §5). Nothing under Decision is implemented yet, and this ADR moves no file.
- **Deciders:** core maintainer (raised the question on 2026-11-05); TSC (to ratify)
- **Resolves:** the open sub-question of [`docs/03-architecture.md`](../../docs/03-architecture.md) §7.4, whether unusually large domains later split into sub-domain packages
- **Invariants:** I1, I4, I5 (applied, not changed)

## Context

Today a module is one folder, `model/<domain>/`, and all its files sit directly in it:

- A module may span several `*.wml.yaml` files, and exactly one of them carries the `module:` header ([`schema/README.md`](../../schema/README.md) §3). For example, `model/transport/` holds `transport.wml.yaml` and `roles.wml.yaml`. The files of a module are gathered by folder. No file imports another.
- The validator requires one module per directory (S6) and reports a module spread over several directories.
- C# generates one project per module, with one file per type in a single flat folder: `generated/Wmoop.Transport/Moped.Gen.cs`. Python and TypeScript generate one file per module: `wmoop/transport.py`, `wmoop/transport.ts`.

Some modules are already large. On 2026-11-05:

- `model/religion/religion.wml.yaml` has 2,417 lines in one file. About 1,760 of them declare its 113 L2 individuals, 33 of which are traditions;
- the generated `wmoop/religion.py` has 1,652 lines;
- the largest C# projects hold 17 type files (`Wmoop.Religion`) and 14 (`Wmoop.Math`, `Wmoop.Music`).

The registry ([`model/taxonomy.yaml`](../../model/taxonomy.yaml)) names domains much broader than these, such as law, medicine and food. Without a rule, a large domain ends up as one very long model file, one very long Python or TypeScript file, and a C# folder with hundreds of files.

The tools already have parts of a hierarchy, but they disagree:

- The grammar (`wmoop.json`, `moduleQName`) accepts dotted module IDs such as `wmoop.nature.anatomy`.
- The C# generator maps such an ID to the project and namespace `Wmoop.Nature.Anatomy`.
- The Python and TypeScript generators refuse nested modules ("not supported … yet").
- The loader in `wmoop.tools` reads only `model/<folder>/*.wml.yaml`. It reads no subfolder and reports nothing about them. A sub-module placed in a subfolder passes the validator, which searches recursively, but no binding generates any code for it.
- Nothing checks that a module's folder matches its ID.
- S6 says a renamed ID keeps the old one as a `deprecated_alias`, but the grammar has no such field yet.

## Decision

There are two separate mechanisms, and one rule tells them apart.

### 1. Folders inside a module, for organisation only

A module's directory may contain subfolders that group its files by topic. For illustration only:

```
model/religion/
├── religion.wml.yaml          # the module: header and the core concepts
├── teachings/
│   └── teachings.wml.yaml     # Teaching, Doctrine, EthicalValue, Precept, PreceptSet
└── traditions/
    └── traditions.wml.yaml    # the ReligiousTradition individuals
```

1. Such a folder holds no file with a `module:` header. Its files declare only IDs of the enclosing module, as S6 already requires of every file.
2. IDs do not change. A concept in `model/religion/teachings/` is still `wmoop.religion/Doctrine`.
3. A folder's name follows the pattern of a module-ID segment, `[a-z][a-z0-9]*`, so the folder can later become a sub-module without a rename. As today, folders whose names start with `_` or `.` are not part of the model (`model/_template/`).
4. Folders may nest, but they should stay shallow.
5. Moving a declaration to another folder, or reorganising the folders, is a PATCH change. No ID, namespace, import path or API changes.
6. The generated layout follows the folders where a binding emits one file per type:
   - **C#:** the project mirrors the folders, each segment in PascalCase: `generated/Wmoop.Religion/Teachings/Doctrine.Gen.cs`. The namespace stays the module's (`Wmoop.Religion`), so moving a file to another folder never breaks a caller. The hand-written halves may use the same folders under `Wmoop.Net/src/Wmoop.Religion/`, which the generated project already compiles (`**/*.cs`).
   - **Python and TypeScript:** unchanged. They still emit one file per module (`wmoop/religion.py`, `wmoop/religion.ts`), and the folders do not appear in their output.
7. The validator warns, without failing, when one folder directly holds more than 30 declarations, and suggests subfolders. The threshold is a starting value and may be tuned.

### 2. Sub-modules, for a part with its own consumers

A subfolder that contains a file with a `module:` header is a sub-module. For illustration only (today `anatomy.wml.yaml` is a file of `wmoop.nature`):

```
model/nature/
├── nature.wml.yaml            # module wmoop.nature
└── anatomy/
    └── anatomy.wml.yaml       # module wmoop.nature.anatomy, with its own header
```

1. Its ID is the parent's ID followed by the folder name: `model/nature/anatomy/` holds `wmoop.nature.anatomy`. The validator checks that every module's folder matches its ID, top-level modules included (`model/transport/` holds `wmoop.transport`).
2. It is a full module: its own `version`, `title` and `depends_on`, and its own package in every binding ([`docs/03-architecture.md`](../../docs/03-architecture.md) §4.5 (a)). The names follow §4.2: `Wmoop.Nature.Anatomy` in C#, `wmoop.nature.anatomy` in Python, `wmoop/nature/anatomy` in TypeScript.
3. It depends on its parent, and the parent never depends on it. A sub-module extends its parent by addition (§4.5 (b)), and S4 keeps the graph acyclic. In Python the sub-module lives inside the parent's package, so importing it loads the parent anyway.
4. There is one level only: `wmoop.<domain>.<sub>`. A deeper level needs a new ADR, in the spirit of S1's shallow inheritance.
5. Choose a sub-module over a folder when at least one of these holds:
   - consumers would want the part without the rest of the domain, or the rest without the part;
   - the part needs dependencies that the rest of the domain does not, for example anatomy needing chemistry;
   - the part has its own steward, sources or stability tier.

   Otherwise, use a folder.
6. Moving existing declarations into a sub-module changes their IDs (`wmoop.nature/Organ` becomes `wmoop.nature.anatomy/Organ`). Under S6 and §4.3 that is a MAJOR change, and it needs the `deprecated_alias` that S6 specifies but the grammar lacks. Until that field exists, sub-modules hold only new content.

### 3. How to tell them apart

A subfolder of a module is a sub-module if, and only if, one of its files carries a `module:` header. Otherwise it is an organisational folder of the enclosing module. The rule is local: looking at the folder is enough to answer it.

### 4. The loader reads the whole tree

The loader in `wmoop.tools` reads every `*.wml.yaml` under `model/`, in every folder except those starting with `_` or `.`, and assigns each file to a module by the rule above. It fails on a file it cannot assign instead of skipping it, so the validator and the generators always see the same files.

## Consequences

- Authors can split a large module into folders at any time. That needs no version bump and changes no binding's API.
- In C#, a large project gets subfolders instead of one flat folder. Namespaces and type names do not change.
- When an author moves a folder, the C# paths in `generated/` move with it, and the regeneration pull request shows renamed files. The hand-written halves are unaffected, because a `partial` class is matched by namespace and name, not by path.
- Python and TypeScript files keep growing with their module. A sub-module is the way to shrink them. Whether they should also split by folder is left open (Follow-ups).
- Each sub-module adds one more package and one more dependency edge, a cost §4.5 already accepts.
- The loader stops skipping files without a word. That fix is needed whatever else is decided.
- Once this is implemented, `model/README.md`, `schema/README.md` §3 and its S6 row, `docs/03-architecture.md` §4.2 and §7.4, and `docs/08-contributing-a-domain.md` must describe the new layout.

## Alternatives considered

- **Explicit imports between files, as with Sass/SCSS partials (`@import`, `@use`).** Rejected for three reasons:
  - In CSS the order of rules matters (the cascade), so an explicit import list carries meaning. WML is declarative, and the order of files does not matter.
  - An import list would be a second source of truth beside the folder on disk. A file left out of the list would disappear without an error.
  - The module-level part of `@use` already exists as `depends_on`, with SemVer pins and the S4 acyclicity check.
- **Group `model/` by the registry's clusters** (`model/natural/nature/`). Rejected: `model/taxonomy.yaml` declares the clusters organisational only, and they may change. Moving a domain to another cluster would move its folder and its generated paths. About thirty domains are still easy to scan at one level.
- **Let the generator choose the grouping**, by kind (`Enums/`, `Roles/`) or by inheritance root. Rejected: the domain author knows the meaningful groups (organs, instruments, traditions), and a grouping computed from the model would move files whenever the model changes.
- **One C# namespace per folder** (`Wmoop.Religion.Teachings`). Rejected: moving a file to another folder would then break callers, and folders would no longer be organisation only.
- **Split Python and TypeScript files by folder now.** Deferred: it needs a decision on each language's public import surface, and on how the hand-written halves (`wmoop_ext.<domain>`, TypeScript module augmentation) find the generated types.
- **Sub-modules only, no folders.** Rejected: every split would change IDs and add a package, even when the only aim is shorter files.
- **Folders only, no sub-modules.** Rejected: §4.5 (a) promises that consumers install only what they use, and a domain such as medicine would otherwise ship as one package.

## Follow-ups

1. **Loader** (`wmoop_tools/loader.py` in `wmoop.tools`): read the whole tree and fail on any file it cannot assign. This step can land first, because it removes the silent skip whatever else is ratified.
2. **Validator** (`schema/validate_wml.py`): the folder rule, the check that a folder matches its module's ID, the one-level limit, the sub-module's dependency on its parent, and the size warning. Update the S6 row of `schema/README.md`.
3. **C# generator:** mirror the folders inside each project.
4. **Python and TypeScript generators:** generate sub-modules, which they refuse today, and decide whether a module's file splits by folder.
5. **Grammar** (`wmoop.json`): add `deprecated_alias` before any existing declaration moves into a sub-module.
6. **Documentation:** update `model/README.md`, `schema/README.md` §3, `docs/03-architecture.md` §4.2 and §7.4, and `docs/08-contributing-a-domain.md`.
