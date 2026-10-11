# Inspection and decompiled reference material — provenance note

**What it is.** The repository tracks reference material under `.local/`:

- `.local/inspection-*/` (about thirty folders, roughly 400 C# files in total) — per-feature source
  inspections made while implementing Rimrooms, including decompiled RimWorld Core code and code
  supplied by installed third-party mods (for example the Stargates provider).
- `.local/decomp/` — a larger decompiled reference tree.

**Why it is kept.** It is the evidence behind the implementation records and source reviews in
`docs/implementation/`, which cite exact inspected methods and pinned builds. It is kept as
evidence and is **not** Rimrooms source.

**What it is not.**

- It is **not part of the mod package.** The loadable mod is `Mod/Rimrooms - Async Industries/`
  only, governed by the allowlist in `tools/package-files.json` (200 files when counted on
  2026-10-10). Nothing under `.local/` is built, staged or shipped to players.
- It is **not covered by the MIT licence**, which applies to original Rimrooms source only. The
  material belongs to its respective owners (Ludeon Studios for RimWorld Core, and each mod's
  author for that mod's code).
- It is **not a legal ruling.** No determination has been made about whether tracking or
  publishing it is permitted.

**Correction to older text.** Several guides describe these trees as ignored, local-only or
machine-local (for example the directory map in [ARCHITECTURE.md](ARCHITECTURE.md)), and the project
rules forbid copying another package's source. The trees are in fact tracked. That conflict is
recorded here rather than resolved by deleting or moving anything.

**Needs the owner.** Because the GitHub remote is public, this material needs a **public/private
boundary review by the owner**: whether it stays tracked, moves to a private location, or is reduced
to citations and hashes. Until the owner decides, do not delete, move or untrack it, and do not
copy any of it into `src/` or `Mod/`.

Related: [SOURCE_REGISTER.md](SOURCE_REGISTER.md), [CONTENT_REUSE_POLICY.md](CONTENT_REUSE_POLICY.md),
[DECISIONS_CURRENT.md](DECISIONS_CURRENT.md).
