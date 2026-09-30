# Playing together

**Nothing on this page has been tested in play.** No game has ever been launched from this
repository. What follows is what the mod is built to do and what it is built not to do, read out
of the code and the server files. Treat every sentence as a design statement, not a result.

---

## What this mod does, in one line

Each player runs their **own company**. Their own facility, their own gate, their own discoveries,
their own research, their own books.

There is **no shared colony**. There is **no live shared map**. There is **no synchronised
research**. Nothing in this mod transfers a case file, a crew member or a piece of equipment from
one company to another. That is a design decision, not a limitation waiting to be lifted: two
companies that share everything are one company with two keyboards, and the thing that makes the
premise work is that your branch is yours.

What can link two companies is whatever **RimWorld Together** itself supports between two ordinary
colonies — visiting, trading, sending aid. Those are that mod's features and they behave the way
that mod makes them behave. This mod neither extends nor restricts them.

---

## What you need

| | |
|---|---|
| RimWorld | **1.6** |
| RimWorld Together | Workshop ID `3005289691`, package `nova.rimworldtogether` |
| Harmony | required by RimWorld Together, not by this mod |
| This mod | no multiplayer-specific setting, and nothing to turn on |

**This mod requires none of the above.** It is built Core-only with no hard dependencies, and it
does not know whether you are playing alone until it looks — which it only does to tell you, on
the facilities page of the company panel.

---

## Setting up a server

The server is RimWorld Together's, not ours, so its own documentation is the authority. What is
recorded here is what was observed in the local server files, because those observations change
what a player should expect.

**Mods are not enforced.** The server reports `AllowAllMods=true`, `EnforceSettings=false`, and no
configured mod order. It will not push a mod list at anybody, so **every player has to match their
own mod list by hand**, and a mismatch will not be announced to you by the server.

**Match the mod list exactly.** The same mods, in the same order, on every client. A profile that
differs between two players is the single most likely cause of trouble, and it is the one thing
nobody will warn you about.

**Two actions are enabled by default** in the local configuration: aid and trade, both with a 250
cooldown. There is no separate visit or activity action file and no `EnableActivities` field in
`ServerConfig.json`, so **whether offline visiting is available is unknown** from what was
inspected.

**The scenario is forced.** `ScenarioConfig.json` enforces `Crashlanded`. If you want to start a
game any other way — including any of this mod's own three starts — **use a disposable copy of the
configuration** rather than editing the one you rely on.

**Record the build on every client.** The versions and file hashes that were checked are in
[COMPATIBILITY.md](COMPATIBILITY.md) and the
[feasibility audit](research/RWT_AND_GRAVSHIP_FEASIBILITY.md). Matching artefacts proves the files
are the same files. It does not prove the game works.

---

## What playing together is like

You and another player each run a branch of the same company. Neither of you can see the other's
facility, gate or coordinates. You each find your own addresses, keep your own case files, and
spend your own insight on your own projects.

What you can do is what two ordinary colonies can do through RimWorld Together: send each other
things, help each other out, and visit if the server allows it. Because each branch keeps its own
books, a crate of steel arriving from another player is exactly that — a crate of steel — and not
a transfer of anything this mod tracks.

**A coordinate you have found is not an address another player can dial.** Addresses are recorded
per gate, on the branch that recorded them. If you want to tell somebody about a place, you tell
them; there is no mechanism, and there is not meant to be one.

---

## What has not been tested

All of it. Specifically:

- no multiplayer session has been run with this mod loaded;
- no two-client profile match has been performed against a live game;
- no visit, trade or aid action has been observed with this mod present;
- the 294-mod profile has never been loaded into a running game at all.

The mod's own facilities page lists which optional mods it has a recorded position on and which of
them are loaded, and it says the same thing this page says: **loaded means present, not proven.**

When any of the above is actually tested, the result belongs here with the date and what was run.
Until then this page stays as it is.
