# Workshop copy — the mod page and the collection, ready to paste

**Owner's own alternative, verbatim from the queue row that proposed automating Steam:** *"The
alternative is a prepared write-up the owner pastes, which is far less work for whoever is not
doing the clicking."*

And on automation, asked directly: *"Not yet — ask again when the mod is ready to publish"*.

**So this is the write-up and nothing here touches Steam.** No Playwright, no account access, no
page created, no collection created. The owner alone publishes.

## The rule this file exists to satisfy

The queue row asks that the Workshop page, the collection and the site be *"written from the same
source as the site, so three descriptions of one mod cannot disagree."*

**Two of the three are already generated**, and that is the stronger half: the public repository's
readme is built from `About.xml`, so the sentence a player reads in the mod list and the sentence
they read on the repository are **one copy**. The site's reading order and page summaries are
imported by the renderer rather than duplicated.

**A Workshop page cannot be generated, because Steam is not a file this repository writes.** What
it can be is **derived from the same two sources and from nothing else** — `About.xml` for the
description and the wiki for the structure — which is what the text below is. Anything in it that
is not in one of those two is a defect.

**When `About.xml` changes, this file is re-derived**, not patched. That is the whole point of
recording where each paragraph came from.

---

## 1. The mod page

### Title

```
Rimrooms - Async Industries
```

### Short description — the line Steam shows in a list

```
Run a Backrooms salvage branch. Build a gate, hold a connection open, send a crew through, and
bring back what pays. Needs no other mod and no expansion.
```

**Source:** `About.xml` `name` and the dependency position. The last sentence is the single most
important thing on the page and it is the one a reader will not believe without being told twice —
the mod's `loadAfter` list is 294 entries long and **none of them is required.**

### Body

```
[h1]Rimrooms - Async Industries[/h1]

A Backrooms company, run as a business. You are a branch office: you build the gate, you keep the
power on, you hold a connection open, and you send three people through it to bring back
something the parent corporation will pay for.

[b]This mod needs nothing.[/b] Not Harmony, not an expansion, not another mod. RimWorld Core on
its own is the supported way to play it. It knows how to sit beside a few hundred other mods and
that is sorting advice, not a requirement.

[h1]What you actually do[/h1]

[list]
[*][b]Build and certify a gate.[/b] Eleven startup steps, and two of them are the table and the
console being set to gate control. If you have done everything and it still will not open, that
is the first thing to check.
[*][b]Hold a connection.[/b] A connection has a duration and it is the only clock in this mod.
Power, tech, maintenance and whether somebody is at the console all decide how long it lasts. The
top research rung removes the countdown entirely.
[*][b]Send a crew.[/b] Three people, and they can work on the other side — hauling,
construction, bills, research, medicine, cooking, mining. The far side is a map your colony
actually uses, not a cutscene.
[*][b]Get paid.[/b] The company buys what came out of a coordinate above market and ordinary
valuables below it. A trader is still the better price if you are willing to wait for one.
[*][b]Answer requests.[/b] Six of them teach you the job, the seventh is the hinge, and after
that they are generated. [b]None of them has a time limit.[/b] No mission, offer, contract or
trade in this mod expires, is cancelled for slowness, or penalises you for taking your time.
[*][b]Research nine branches.[/b] Not a line. Nine separate tracks across five bands, and a
project only exists where it changes something you could name.
[/list]

[h1]What is down there[/h1]

Levels get stranger with depth, in five bands — yellow rooms near the surface, then poolrooms,
machinery, abandoned offices, cold storage, and whatever the deepest band turns out to be. Room
scale, materials and how much the architecture agrees with itself are all functions of how far
down you are. Near the surface the place makes sense. It stops.

The free ways through reach the sixth level. There are inhabitants. They stay down there:
[b]nothing crosses a gate under its own will[/b], an open gate is never an objective, a lure or a
spawn target, and anything that comes back came back because one of your people carried it.

[h1]Before you install[/h1]

[b]This is a development build and nobody has played a full campaign yet.[/b] Everything is built
and checked against the game's own code. Whether it is any fun is the question nobody has
answered.

[list]
[*][b]Nothing is claimed as tested with other mods.[/b] It loads beside a lot of them. That is
not the same thing, and it will not be claimed until somebody has run it.
[*][b]Co-op is not promised.[/b] Playing alongside another colony needs RimWorld Together, which
has its own requirements. Whether this behaves correctly across it has not been established.
[*][b]Saves may break between development builds.[/b] While the version starts with 0., a new
build is not promised to open an old save. The build that wrote a save can always open it.
[*][b]Balance is unjudged.[/b] Costs and payments are first passes. There are sliders in the mod
settings so you do not have to wait for somebody else to decide.
[/list]

[h1]The guide[/h1]

The full documentation is a thirteen-page site: what a gate is, how a connection works, what you
find down there, what the company wants, the interface, multiplayer, and what to do when
something refuses.

[b]Link:[/b] (the site address goes here)

[h1]Licence and credits[/h1]

MIT. RimWorld and its assemblies are Ludeon Studios' and are not bundled. Kane Pixels' series and
the A24 feature inform an indirect adaptation; no frames, footage, audio or dialogue are
included. No other mod's files are bundled or modified. No gameplay art or audio ships - every
object in play is existing game content.
```

**Where each section came from:** the opening two paragraphs are `About.xml`'s description. *What
you actually do* is the wiki's first-hour and gates pages. *What is down there* is the backrooms
page and the palette's five bands. *Before you install* is `WHATS_NEW.md`'s four statements, which
exist precisely so this section cannot be softer than the repository's. *Licence and credits* is
the credits page, sentence for sentence.

### What the owner fills in

**One thing: the site address**, written as `(the site address goes here)` above. It is deliberately
not written here, for the same reason `CNAME.example` is an example and the generated readme links
the wiki by relative path: **a document must not claim a URL that may not serve.** Paste the
address that is actually live at the moment the page goes up.

---

## 2. The collection

### Title

```
Rimrooms - Async Industries and what it plays well with
```

### Body

```
[h1]Rimrooms - Async Industries[/h1]

The mod and the things it is comfortable beside. [b]Nothing in this collection is required.[/b]
Rimrooms needs RimWorld Core and nothing else - including nothing else in this collection.

[b]Link to the mod page:[/b] (the mod page address goes here)
[b]Link to the guide:[/b] (the site address goes here)

[h1]Why a collection at all, if nothing is required[/h1]

Because the question a reader actually has is [i]what did you build this against[/i], and the
honest answer is a long list. Rimrooms is developed against a large mod profile and its
load-order advice names every entry in it. That is advice: it tells a mod manager where to put
Rimrooms, not what to install.

[b]Nothing here is announced as tested.[/b] Loading beside a mod is not compatibility with it,
and no combination has been verified in play yet. When combinations have been run, the results
will be published - including the ones that fail.

[h1]If you want co-op[/h1]

You need RimWorld Together, and it needs Harmony. [b]Rimrooms does not need either.[/b] Everyone
on a server needs the same mod list, because the server does not enforce mod order or settings.
Whether Rimrooms behaves correctly across it is not established and is not claimed.
```

**Where it came from:** the mods page and the multiplayer page, which was rewritten from register
row 196 and is the only place in this project that names RimWorld Together to a reader.

### What the owner fills in

**Two addresses**, both marked, both for the same reason as the mod page's.

---

## 3. The order these go up in, which is a real dependency chain

The owner named it and it is not negotiable, because doing any step early means publishing links
that point at nothing:

1. **The mod is settled** — content final, nothing still being retired.
2. **The site is deployed and working**, at its proper address. **Done.** It is live and read back
   over HTTP.
3. **Then** the mod page, whose write-up links to the site.
4. **Then** the collection, whose write-up links to both.

**Steps 3 and 4 are the owner's to perform**, and step 1 is the owner's to declare. This file
exists so that when they are, neither step is an authoring job.

## Links

- [`WHATS_NEW.md`](WHATS_NEW.md) — the player-facing record, and the source of the honesty section
  on both pages. If one is softened, they disagree.
- [`PUBLIC_RELEASE_PLAN.md`](PUBLIC_RELEASE_PLAN.md) — the ordering chain and the decisions that
  are the owner's.
- [`PUBLISHING.md`](PUBLISHING.md) — §8 is the release ritual the mod page should follow a tag of,
  not precede.
