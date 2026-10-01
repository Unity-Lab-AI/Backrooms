# Public release plan — the site, the Workshop page, the collection

> **Superseded 2026-10-01 — dependencies.** This document predates the owner's decision that the
> package has hard dependencies. `About.xml` now declares all five expansions and the whole
> collection as requirements, so anything here describing a Core-only route is history rather than
> a current claim. Recorded as a change to D3 and D4 in
> [Gate 0 decisions](GATE_0_DECISIONS.md#decision-log).

**Status: planned, not started.** Owner direction was explicitly *"when we get to it"*, and this
document exists so that when we do, the shape is already decided and the decisions that are
the owner's to make are already named.

---

## The direction, verbatim

> *"fyi when we get to it we will build a github deployable html build that catologs the whole mod and is the main mod site wiki and documentation dump in a beauty of a deployable github page with what ever you can do so the deploy address is not some random git hub address but is a nice backrooms url for github deployed page where we document all the mods capabilities and howto and related public facing docs and information into a website that lays everything out top to bottom beautiffully just like other rimworld mods make theri third party sites, not to metione the building of the steam workkshop mod collection and workshop mod deploy for our mode with write ups for  both with links in them to each other and the deployed site so things will have to be deployed and settled before doing the proper order of setting up the workfshop collection and the mod in the workshop, idk maybe we will use a playwrite thing so you can click through steam and set it all up keeping me from having to do it all"*

---

## 1. Why this is last, and not a matter of taste

Every artefact in this plan **describes the mod**. A site, a Workshop page and a collection
write-up are three more documents that go stale the moment the thing they describe changes.

This project has already paid that bill once: `README.md` announced a version **twenty-five
checkpoints out of date**, on the front page, until a checker caught it. That was one file
that nobody had to deploy. A published site and a Workshop listing are the
same failure with an audience.

So the order below is a dependency chain, not a preference.

---

## 2. The ordering the owner named

> *"things will have to be deployed and settled before doing the proper order of setting up the workfshop collection and the mod in the workshop"*

| # | Stage | Why it cannot come earlier |
|---|---|---|
| 1 | **The mod is settled** | Content set final, scenarios in, nothing still being retired. Anything written before this is written twice. |
| 2 | **The site is deployed and reachable at its real address** | The Workshop write-ups link to it. Publishing a link to a page that does not exist yet is the one mistake that is visible to strangers. |
| 3 | **The Workshop mod page** | Its write-up links to the site. It also needs a `packageId` and a published build that will not change underneath it. |
| 4 | **The Workshop collection** | Its write-up links to *both* the mod page and the site, so both must already exist. |

Stage 1 is tracked in `TODO.md` and `NOW.md`. Stages 2–4 are this document.

---

## 3. The site

### 3.1 What it is

A catalogue of the whole mod — *"capabilities and howto and related public facing docs and
information"* — laid out *"top to bottom"*, in the shape RimWorld mods use for their
third-party sites.

Proposed structure:

| Page | Contents |
|---|---|
| **Front** | What the mod is, in a paragraph. The three starts. A screenshot strip. Install and requirements. |
| **The gate** | Designating a door, sizes and what fits through, bringing a connection up, the address book, power and the cutoff. |
| **The Backrooms** | Coordinates, depth, rooms and facilities, what changes between visits, quiet stretches. |
| **What is down there** | Inhabitants, survivors, anomalies, pursuit, incursion — and the rules each of them obeys. |
| **The company** | Staff, procurement, contracts, the odd-origin economy, bonds, the corporate trader, cross-gate work. |
| **How to play** | The player-facing how-to, which is already a queued task and should be written **once**, for both this and the in-repo copy. |
| **Compatibility** | Core-only claim, DLC use, the 294-mod profile, what is optional. |
| **Changelog** | Generated from `CHANGELOG.md`. |

### 3.2 It must be generated, never hand-maintained

`tools/make-readable-html.py` already does the core of this: it renders documents to
standalone styled HTML with the CSS inlined and no external references. The site is that tool
grown up — more pages, navigation, a front page, screenshots.

**A hand-written site is a fourth copy of the truth that drifts from the other three.** A
generated one cannot: regenerate it and it is current, or it fails to build and somebody
notices.

Corollary: **`check-doc-conformance.py` should cover the generated output**, so a published
page can never claim a version or a branch the build does not have. The rule already exists;
it just needs the output directory in scope once that directory is real.

### 3.3 The address — *"not some random git hub address"*

> *"a nice backrooms url"*

This is the one part that **cannot be decided here**, because it costs money and belongs to
the owner.

A GitHub Pages site can deploy either way:

| Option | Address | What it needs |
|---|---|---|
| **Project path** | `unity-lab-ai.github.io/Backrooms/` | Nothing. Works immediately. |
| **Custom domain** | e.g. `rimrooms.something` | A domain the owner registers, a `CNAME` file in the published branch, and DNS records pointing at GitHub. |

**These are configured differently**, and the internal links a static site generates depend on
which one is used — a project-path deploy needs a base path, a custom domain does not.
Building for the wrong one means rebuilding.

**Open question for the owner, to be asked before the site is built, not assumed:** which
domain, and is it already registered?

### 3.4 Where it is deployed from

The repository is private and mirrors to two remotes. Pages publishes from a branch or a
directory in one of them. That interacts with the existing four-branch cascade
(`feature/* → Prep → Develop → Main`), so the publishing branch and its relationship to that
cascade is a decision to make deliberately rather than by accident — most likely a dedicated
branch that the cascade does not touch.

---

## 4. The Steam Workshop

### 4.1 The mod page

A write-up that links to the site. It is the first thing most players will ever read, and it
is **not** the same text as the site front page — Workshop descriptions are shorter, use
Steam's own markup, and are read by somebody deciding whether to click subscribe.

It should be **generated from the same source** as the site and the About description, so
three descriptions of one mod cannot disagree. That is the same reasoning that produced the
vocabulary rule and the doc-conformance checker.

### 4.2 The collection

Its own write-up, linking to the mod page **and** the site. A collection exists to say what
the mod is *for* and what it is meant to sit alongside — which, for a mod whose whole premise
is *"we are making a mod that works with the other 274"*, is genuinely load-bearing rather
than decoration.

### 4.3 Automation — an open question, not a decision

> *"idk maybe we will use a playwrite thing so you can click through steam and set it all up keeping me from having to do it all"*

Recorded as the owner's idea, and deliberately **not** treated as approval.

Driving the Steam Workshop UI with Playwright means **operating an authenticated session on
the owner's Steam account** and publishing to it. That is a different class of action from
anything done in this project so far — every checkpoint to date has been source, documents and
git, with the standing rule that the owner alone launches and publishes.

**This needs explicit permission at the time, with the scope stated**, not an assumption
carried forward from a sentence that began *"idk maybe"*.

The alternative, which costs the owner very little: **a prepared write-up, formatted in
Steam's markup, ready to paste**, plus a checklist of the settings to set. That removes almost
all of the work without anybody automating a login.

---

## 5. Standing constraints that still apply

- **No Claude attribution** anywhere in any of it — site, Workshop page, collection write-up,
  commit messages, or generated output.
- **The owner alone publishes.** Deploying a documentation site is not the same act as
  launching the game, but the Workshop is the owner's account and the owner's decision.
- **Existing-content-only** still governs what the site may *claim*. It describes what the mod
  does, and it must not describe features that were decided against.
- **`LoadFolders.xml`, `About.xml` and the package allowlist** are the source of truth for what
  actually ships. The site's install and compatibility pages are generated from them, not
  written from memory.

---

## 6. What is already in place

| Piece | State |
|---|---|
| `tools/make-readable-html.py` | Working. Renders About, README, CHANGELOG, NOW, TODO, ROADMAP to standalone styled HTML in `outputs/readable/`. |
| `About.xml` description | Rewritten into four titled sections; no longer a 6,724-character line. |
| `CHANGELOG.md` | Player-facing language throughout, one entry per checkpoint. |
| `check-doc-conformance.py` | Enforces version, branch, retired defs, checker count and LAW #0 across living documents. Ready to extend to generated pages. |
| The player-facing how-to | **Queued, not written.** Should be written once and used by both the repo and the site. |

---

## 7. The first three questions to ask when this starts

1. **Which domain**, and is it registered?
2. **Publish Pages from which branch**, given the four-branch cascade?
3. **Playwright against Steam: yes or no** — and if yes, with what scope?

None of them can be answered from the code, and guessing any of them wastes the work.
