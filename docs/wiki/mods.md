---
title: Mods and expansions
summary: "Nothing is required but RimWorld. What the load-order profile actually means for you."
---

# Mods and expansions

## What is required

**RimWorld 1.6, and nothing else.** No other mod. No expansion.

| | |
|---|---|
| **RimWorld 1.6** | The only requirement |
| **The five expansions** | Royalty, Ideology, Biotech, Anomaly, Odyssey — every one **optional** |
| **Other mods** | All optional |

This build declares **no dependencies at all**. Your mod manager will not ask you for anything,
because nothing is being asked for.

## Load order

**It loads last.** A patch cannot see content from a mod that loads after it.

It publishes a long list of mods as load-order advice, which is a different thing from a
requirement: a sorting manager reads that list and places this mod correctly on its own. Every mod
on it is optional, and the list is advice about *order*, never about what you need to own.

**[RimSort](https://github.com/RimSort/RimSort) is the manager this was sorted with**, and the one
[Install](install.md#with-rimsort-recommended) gives steps for. Any manager that reads a declared
load order will do the same job.

---

## How it treats other mods

| | |
|---|---|
| **Nothing is edited** | No other mod's files are changed, read into this one, or copied |
| **Content is looked up by name** | A missing one degrades what depends on it rather than throwing |
| **Expansion content is gated** | Anything from an expansion is marked as needing it, so it simply is not there without it |
| **Nothing leaks inward** | No content from any other mod appears in Backrooms generation |
| **No Harmony** | Nothing is patched at runtime |

The company panel lists the optional mods this one has a stated position on, whether each is
loaded, and in plain words what will and will not happen with it.

## No start depends on another mod

Every opening reaches its first objective on RimWorld's own content. Where a mod or expansion would
have supplied something, its absence degrades that thing with a stated reason rather than refusing
to continue.

## Doors from other mods

Wider doors work as wider gates — that is the one place another mod's content changes what you can
do. A 2-cell door passes pack animals; 3 cells or more passes anything.

Core alone gives you a 1-cell gate from a door or autodoor, and a 2-cell gate from an ornate door,
with no other mod installed.

## The list itself, mod by mod

**[The mod list](mods-list.md)** carries all 296 of them, grouped by tag.

Each one gets four things: what Rimrooms uses it for, what changes if you leave it out, what to
watch for, and a tag — Required, Recommended, Optional, Visual only or Not needed.

**Required there means required for the experience as it was built.** Nothing on that page is
required to launch.

## What is not claimed

**No compatibility report exists**, and none is implied by the load-order list. Nothing is
announced as working with anything until it has been tested, and that testing has not been
published.

If you hit a conflict, it is worth reporting — see [Links](links.md).

---

## Running a smaller list

Run whatever list you like. Nothing is declared as a requirement, so no manager will warn you, and
the mod is written so that missing content degrades rather than crashes.

A reduced list is untested rather than unsupported — the same as every other list, including the
full one.
