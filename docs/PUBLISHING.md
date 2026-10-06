# PUBLISHING — the exact way to push this repository to both remotes

This is the procedure that works. It was written after doing it, not before. Follow it literally; every deviation the previous agents made (assuming an `origin` remote, lowercase branch names, creating local tracking branches and then a "receipt" file, trying to use the browser session for Git transport, using the other host's CLI against Forgejo) is a way it has failed before.

> ## ⛔ PUBLICATION IS FOUR REPOSITORIES NOW, NOT TWO ⛔
>
> **Owner direction, 2026-10-05, verbatim:** *"and remember staging now includeds pushes to the mod only repo"*.
>
> Since 0.12.94-dev there is a **second pair of remotes** holding the mod and its public face only — `Rimrooms-AsyncIndustries` on Forgejo and on GitHub — and it is **where the wiki actually deploys from**. A publication that updates this repository and not that one leaves the published site and the downloadable mod behind, silently, with every instrument still green.
>
> **This document said nothing about it until 0.12.98-dev**, which is exactly the gap the owner's reminder was aimed at: this file is the cascade authority and the one thing an agent is told to read instead of improvising, so a step that is not in here is a step that gets forgotten.
>
> **So the full publication is twelve refs, not ten:**
>
> | | refs | how |
> |---|---|---|
> | This repository | **10** — `forgejo` and `github` × five branches | §4, by refspec from the feature branch |
> | The mod-only repository | **2** — `forgejo` and `github` × `main` | `python tools/export-public-repo.py --push` |
>
> **The exporter receipts its own push**, reading both remotes back and refusing if either does not hold the export commit — because `git push` exiting zero is not the same statement as *the remote holds this commit*, and §5 below exists because nobody noticed an eight-ref publish was missing a branch for forty-five checkpoints.
>
> **Order matters, and only one way round works.** Export and push the mod-only repository **before** committing here: the export is built from `artifacts/build/package-manifest.json` and verifies every file's SHA256 against the working tree, so it must run against the tree that was built and checked. It refuses outright on a package edited after the build — which it has done twice, both times correctly, when a version bump landed after a build.

## ⛔ STAGING IS NOT ONLY A PUBLICATION STEP. IT BELONGS BEFORE EVERY LAUNCH ⛔

**This cost a whole launch report on 2026-10-06 and it is the most expensive ordering mistake in
this repository's history.** The owner reported the solo start broken. The staged assembly was
**02:51** and the build on disk was **23:00** — they had tested a DLL **twenty-one hours old**, and
every conclusion drawn from that launch was about code that had already been replaced.

**The instrument had already said so.** `check-package-integrity` rule 10 reported *"THE STAGED COPY
IS NOT THIS BUILD"* with **nine differing files** before the launch, and it was read as an expected
environmental note because RimWorld was open at the time. **It was the warning working.**

So the rule is an ordering one rather than a new instrument:

| When | What must run |
|---|---|
| After the last build, **before telling the owner anything is testable** | `powershell -File tools/stage-mod.ps1 -UpdateExisting` |
| Before any launch report is trusted | `python tools/check-package-integrity.py` must read **PASS** |
| At publication | the same two, as step 0 of §7 below |

**A launch loads the staged copy and nothing else.** The version string is a label; the bytes are
what runs, which is why rule 10 compares every file by content and not by version. And
`stage-mod.ps1` refuses outright on a package edited after the build — it has done so correctly
whenever a keyed string or a def changed between the build and the stage, which is the common case
and the whole reason the refusal exists.

## ⛔ FORGEJO IS HELD. SIX REFS, NOT TWELVE, UNTIL THE OWNER SAYS OTHERWISE ⛔

**Owner, 2026-10-06, verbatim:** *"fyi the git.unityailab.com is going down so stop pushes to it until further notice, github two repos is still good"*

So the cascade is **six refs** while the hold stands:

| | Refs |
|---|---|
| `github` on this repository | **5** — `feature/bug-testing`, `feature/connected-colony-portals`, `Prep`, `Develop`, `Main` |
| `github` on the mod-only repository | **1** — `main` |
| ~~`forgejo`, both repositories~~ | **0. Held.** |

**The remote is HELD, not removed, and that distinction is the whole point.** Deleting it would make every receipt read *complete* and a future reader would never learn a destination had gone missing — which is precisely the eight-ref publication that went unnoticed for forty-five checkpoints, wearing a different hat. `tools/export-public-repo.py` keeps `forgejo` in `REMOTES`, skips it by name through `HELD_REMOTES`, **prints the hold and its reason on every run**, and **refuses outright if every remote is held** — a publication with no destination must not report success.

**Restored by the owner saying the host is back. Never by time passing, and never because a push happens to succeed.** When it is lifted, delete the `forgejo` entry from `HELD_REMOTES` and restore the twelve-ref read-back below; both halves are one edit each.

**Do not push to forgejo to - test whether it is up.** The owner has said it is going down; a push that half-succeeds against a host mid-shutdown is how a remote ends up holding a commit nobody recorded.

---

## 0. Facts about this repository's remotes that you must not guess

| | `forgejo` (PRIMARY) | `github` |
|---|---|---|
| URL | `ssh://git@git.unityailab.com/GFourteen/Backrooms.git` | `https://github.com/Unity-Lab-AI/Backrooms.git` |
| Transport | **SSH, key-based.** The signed-in browser session does nothing for Git; the ed25519 key registered on the Forgejo account does. | **HTTPS with the `gh` credential helper.** `gh auth status` must show a logged-in account with `Git operations protocol: https`. |
| Host CLI | None. Do not point `gh` at it. Verify with `git ls-remote`. | `gh` works for visibility checks (`gh repo view Unity-Lab-AI/Backrooms --json visibility,owner`) and nothing else in this procedure. |
| Push-to-create | **Disabled server-side.** The repo must already exist. It does. | n/a |
| Visibility | Lab-owned host on the `.claude/` IP-boundary allowlist | **PUBLIC on purpose**, owner `Unity-Lab-AI`. The line here read `PRIVATE` until 0.12.79-dev and was wrong: the owner made it public deliberately — *"i made it public on purpose becasue thats how its suppose to be"* — and the exception is declared by exact URL in `.claude/project-config.json` under `claude_ip_boundary`. A new remote never inherits that approval |
| Branches | `feature/bug-testing` (**the working branch since 2026-09-30**), `feature/connected-colony-portals`, `Prep`, `Develop`, `Main` — **capitalised** | identical set, identical casing |
| Remote named `origin` | **does not exist** | **does not exist** |

Consequences:

- `git push` with no arguments fails. **Always name the remote and the branch.**
- `.claude/project-config.json` names `main`/`develop`; those branches do not exist anywhere. The real integration branches are `Prep`, `Develop`, `Main`. Do not create lowercase twins.
- `Prep`, `Develop`, `Main` normally have **no local branch**. You do not need one. Push by refspec from the feature branch (below). Only create a local branch when a merge is genuinely required (§4).
- The `.claude/` IP-boundary hook fires on every `git add` / `commit` / `push` that touches `.claude/`. It passes the Forgejo remote by hostname and checks the GitHub remote through `gh`. If `gh` is logged out, the push is blocked until `gh auth login`.

## 1. Before you push — the docs-before-push checklist

Publication happens only at a substantive milestone (`AGENTS.md` publication cadence). Every publication carries **all** current project changes; no separate unpublished batch.

1. Work is on `feature/connected-colony-portals` (or another `feature/*`). Never commit on `Prep`/`Develop`/`Main`.
2. `./tools/build.ps1` ran clean if any source/XML changed; evidence folder + build record written; `About.xml` + `CHANGELOG.md` bumped if the version changed.
3. Ledger is current: `docs/TODO.md`, `docs/FINALIZED.md` (verbatim entries), master TODO bounded ticks, `docs/ARCHITECTURE.md` if structure changed, `README.md` if anything player-facing changed.
4. `git status` shows nothing you do not intend to ship. Machine-local `.claude/` state files are gitignored; `.local/`, `artifacts/`, DLLs are gitignored.
5. `git config user.name` / `user.email` are your own identity. No AI attribution anywhere in the commit message.

## 2. Commit

```bash
git add -A
git status --short            # read it; confirm nothing unexpected
git commit -m "<one-line summary of the milestone>" -m "<what changed, what evidence, what remains>"
```

## 3. Push the feature branch to BOTH remotes

```bash
git push forgejo feature/connected-colony-portals
git push github  feature/connected-colony-portals
```

Read the output. `ssh: connect` / `Permission denied (publickey)` on Forgejo means the SSH key is not loaded or not registered; fix that, do not switch transports. `remote: Repository not found` on GitHub means `gh` is logged into the wrong account.

## 4. Cascade `feature → Prep → Develop → Main` on BOTH remotes, fast-forward only

First look at where the integration branches are:

```bash
git fetch forgejo && git fetch github
git ls-remote --heads forgejo
git ls-remote --heads github
```

**Case A — all four refs on a remote already point at the same commit, or at an ancestor of your feature HEAD** (the normal case when only one agent works the repo). Push by refspec, in order, no local branches needed. A non-force push is refused by Git if it is not a fast-forward, so this is safe by construction:

```bash
# Forgejo
git push forgejo feature/connected-colony-portals:Prep
git push forgejo feature/connected-colony-portals:Develop
git push forgejo feature/connected-colony-portals:Main
# GitHub
git push github  feature/connected-colony-portals:Prep
git push github  feature/connected-colony-portals:Develop
git push github  feature/connected-colony-portals:Main
```

**Case B — a remote integration branch has commits your feature branch does not have** (someone pushed there directly, or the two remotes diverged). Do NOT force. Merge the normal way, one branch at a time, and keep the feature branch as the thing you push:

```bash
git fetch forgejo Prep
git merge --no-ff forgejo/Prep          # resolve conflicts, commit
git push forgejo feature/connected-colony-portals
git push forgejo feature/connected-colony-portals:Prep
# then Develop, then Main, same pattern; then repeat for github
```

If the two remotes disagree with each other, reconcile against Forgejo first (it is the lab's primary), then push the reconciled result to GitHub.

**Never:** `git push --force`, `--force-with-lease`, `-f`, or deleting a remote branch to "clean up". Never merge `Main` back into a feature branch to "sync" unless the owner asks.

## 5. Read back all TEN refs — this IS the publication evidence

> **It is ten, not eight, and the count is the trap.** The eight-ref read-back was the only
> publication receipt for forty-five checkpoints, and it was written when the work lived on
> `feature/connected-colony-portals`. Work moved to `feature/bug-testing` on 2026-09-30, so the set
> is now that branch on both remotes **plus** the original feature branch, `Prep`, `Develop` and
> `Main` on both. A publish that reads back eight and stops has left the branch the work is actually
> on unpublished, silently. **Count the branch you are on.**

```bash
git ls-remote --heads forgejo
git ls-remote --heads github
git rev-parse HEAD
```

All eight lines must show the same commit hash as local `HEAD` (Case A) or the expected merge commits (Case B). Paste that output into the session report and into the `FINALIZED.md` entry. **Do not write a separate receipt file** for the push; the read-back in tool output is the receipt (owner direction, recorded in `GATE_0_DECISIONS.md` and `CONNECTED_COLONY_CHECKPOINT.md`).

## 6. After the push

- **Do not edit any file after the push.** The working tree must stay clean; the eight-ref read-back in the session output is the publication evidence. Editing `FINALIZED.md` to add the hash would leave an uncommitted change that then rides in the next commit and confuses the audit.
- Instead, write the `FINALIZED.md` entry **before** committing with the wording "published via the cascade in `PUBLISHING.md`; refs read back in session output", and let the **next** session's entry cite the previous commit hash if it needs to.
- `docs/NOW.md` Active section is reset to _(none)_ before the commit if the milestone closed the task.

## 7. One-screen version

**Two things were wrong with the version that used to be here**, and both are the kind that pass silently: the loop pushed three integration branches and not `feature/connected-colony-portals`, so it produced an eight-ref publish — the exact defect §5 warns about in its own words — and it said nothing about the mod-only repository, so running it published this repository and left the wiki and the downloadable mod behind.

```bash
# 0. STAGE THE BUILD INTO THE GAME'S MODS FOLDER. This step was missing from this file until
#    0.12.99-dev and the omission was caught with the staged copy a whole version behind the
#    build, minutes before a launch. It is the copy the owner LAUNCHES: stale means they test a
#    build whose defects are already fixed.
powershell -NoProfile -ExecutionPolicy Bypass -File tools/stage-mod.ps1 -UpdateExisting

# 1. THE MOD-ONLY REPOSITORY. It is built from the build manifest and verifies every
#    file's SHA256, so it must run against the tree that was built -- and it receipts its own
#    push by reading both remotes back.
python tools/export-public-repo.py --push

# 2. Then this repository, all five branches on both remotes.
BRANCH=$(git rev-parse --abbrev-ref HEAD)                  # never hard-code it; that is how eight became wrong
git status --short && git log -1 --oneline                 # sanity
for r in forgejo github; do
  git push $r "$BRANCH"
  for b in Prep Develop Main feature/connected-colony-portals; do
    git push $r "$BRANCH:$b"
  done
done

# 3. Read back TWELVE refs: ten here, two there.
git ls-remote --heads forgejo; git ls-remote --heads github; git rev-parse HEAD
git -C .local/export/Rimrooms-AsyncIndustries ls-remote --heads forgejo
git -C .local/export/Rimrooms-AsyncIndustries ls-remote --heads github
```

If any push in the loop is refused as non-fast-forward, stop, go to §4 Case B for that remote/branch, and do not continue the loop until it is resolved.

If the exporter refuses, **do not work around it**. It refuses for two reasons and both are real: a package edited after the build, which means rebuild and re-export; or something in the export that must never be published, which means read the refusal and fix what it names.

## 8. Cutting a release — the ritual, and the archive it leaves behind

**This section is the M6a half of the tag-release row, and the queue row itself says which half that is:** *"the ritual and the archive close here; the actual tag cannot be cut until M6b supplies the acceptance results this row requires."*

So: **the procedure is written and the first tag is not cut.** The row asks to *"publish only features that passed their listed acceptance criteria"*, and nothing has passed anything because nothing has run. A tag is a claim about what works; this one would be a claim nobody has earned.

### 8.1 What a release is here

A release is **a cascade that is additionally marked**. It is not a different act. Everything in §0–§6 happens exactly as written, and then three things more.

### 8.2 The preconditions, every one of them refusable

| | Precondition | How it is established |
|---|---|---|
| 1 | The whole battery is green **in one run** | checkers, then proofs, then plant suites, then `check-plant-residue.py` |
| 2 | The package is the one that was built | the stager and the exporter both verify every file's SHA256 against the build manifest |
| 3 | The queue holds **no** finished item | `check-queue-integrity.py`, and `[x]` must be zero |
| 4 | The twelve refs are level | read back with `git ls-remote`, pasted into the session output |
| 5 | The published site answers over HTTP | `curl` the index, a deep page, the stylesheet, the cover and one banner |
| 6 | **Every feature in the release notes has a recorded acceptance result** | this is the one that is not met and the reason no tag exists yet |

**Precondition 6 is the gate.** The other five are met today.

### 8.3 The three extra acts

**One — the version is final, not `-dev`.** `About.xml`'s `modVersion` and the project's `Version` are the same string, and `check-doc-conformance.py` already refuses a document that names a different one. A release drops the `-dev` suffix; a `0.x` release is still pre-release under the standing version policy, and `1.0.0` is the first stable.

**Two — an annotated tag on both remotes, from the commit that was published.**

```bash
V=$(python - <<'PY'
import io, re
print(re.search(r"<modVersion>([^<]+)</modVersion>",
      io.open("Mod/Rimrooms - Async Industries/About/About.xml", encoding="utf-8-sig").read()).group(1))
PY
)
git tag -a "v$V" -m "Rimrooms - Async Industries $V"
for r in forgejo github; do git push "$r" "v$V"; done
git ls-remote --tags forgejo | grep "v$V"
git ls-remote --tags github  | grep "v$V"
```

**Annotated rather than lightweight**, because a tag is a record and a record carries who and when. Read back, for the same reason every push here is read back: `git push` exiting zero does not mean the remote holds the ref.

**Three — the same tag on the mod-only repository.** It is a separate repository with its own history, and the downloadable mod is what a player actually has. A version that exists here and not there is a version nobody can obtain.

```bash
cd .local/export/Rimrooms-AsyncIndustries
git tag -a "v$V" -m "Rimrooms - Async Industries $V"
for r in forgejo github; do git push "$r" "v$V"; done
```

### 8.4 The archive, which is a property rather than a folder

The row asks to *"archive exact source and build artifacts, preserve a known-good server profile"*. **Two of those three are already archived by construction, and saying so is better than copying files into a folder nobody maintains.**

| What | Where it already is | Why that is the archive |
|---|---|---|
| Exact source | the tagged commit on **four** remote refs | a tag on an immutable history is a stronger archive than a copy, and there are four of them |
| Build artifacts | the build manifest, with a SHA256 per file, committed beside the package | the manifest is what lets a later reader prove a downloaded copy is the one that was built — a zip could not |
| **A known-good profile** | **nothing. This is the gap.** | the profile is 294 rows of the owner's own mod list, and *known-good* is a launch result |

**So the archive is complete except for the one piece that requires a launch**, and that piece is M6b's. What a release must do is record the profile it was published **against** — the pinned list, the game build, the expansion set — and `docs/research/installed-mod-metadata-2026-09-27.csv` is that snapshot, carrying a parsed `About.xml` SHA256 for all 294 entries. A release names the snapshot it used; it does not claim the snapshot was good.

### 8.5 What a release must never do

- **Claim a tested order, a verified combination or a compatibility result.** D1 is unchanged: *"do not announce compatibility until validation is complete."*
- **Promise a save migration it has not written.** While the version starts with `0.`, a development save may break and the release notes say so plainly.
- **Ship the development changelog.** `docs/WHATS_NEW.md` is the player-facing record and it is authored, not filtered.
