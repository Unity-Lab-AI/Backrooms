# PUBLISHING — the exact way to push this repository to both remotes

This is the procedure that works. It was written after doing it, not before. Follow it literally; every deviation the previous agents made (assuming an `origin` remote, lowercase branch names, creating local tracking branches and then a "receipt" file, trying to use the browser session for Git transport, using the other host's CLI against Forgejo) is a way it has failed before.

## 0. Facts about this repository's remotes that you must not guess

| | `forgejo` (PRIMARY) | `github` |
|---|---|---|
| URL | `ssh://git@git.unityailab.com/GFourteen/Backrooms.git` | `https://github.com/Unity-Lab-AI/Backrooms.git` |
| Transport | **SSH, key-based.** The signed-in browser session does nothing for Git; the ed25519 key registered on the Forgejo account does. | **HTTPS with the `gh` credential helper.** `gh auth status` must show a logged-in account with `Git operations protocol: https`. |
| Host CLI | None. Do not point `gh` at it. Verify with `git ls-remote`. | `gh` works for visibility checks (`gh repo view Unity-Lab-AI/Backrooms --json visibility,owner`) and nothing else in this procedure. |
| Push-to-create | **Disabled server-side.** The repo must already exist. It does. | n/a |
| Visibility | Lab-owned host on the `.claude/` IP-boundary allowlist | PRIVATE, owner `Unity-Lab-AI` (verified 2026-09-28) |
| Branches | `feature/connected-colony-portals`, `Prep`, `Develop`, `Main` — **capitalised** | identical set, identical casing |
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

## 5. Read back all eight refs — this IS the publication evidence

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

```bash
git status --short && git log -1 --oneline                 # sanity
git push forgejo feature/connected-colony-portals
git push github  feature/connected-colony-portals
for r in forgejo github; do
  for b in Prep Develop Main; do git push $r feature/connected-colony-portals:$b; done
done
git ls-remote --heads forgejo; git ls-remote --heads github; git rev-parse HEAD
```

If any push in the loop is refused as non-fast-forward, stop, go to §4 Case B for that remote/branch, and do not continue the loop until it is resolved.
