# Twitch channel write-ups — Unity Plays RimWorld

> **Current game target — 2026-10-12:** prepare for **RimWorld 1.7 unstable / Waylith**, retaining **1.6**. Both loader versions use the shared `1.7/` content folder. [The migration record](implementation/RIMWORLD_1_7_MIGRATION.md) owns the current target and remaining checks. Earlier 1.6 source, build and play observations remain historical; no 1.7 runtime or full-profile acceptance is recorded.

**Applied to the live channel 2026-10-08** (owner: *"the uirls dont work"* -- bare URLs are not links in Twitch Markdown; every URL is now written `[text](url)`, and every picture panel carries its *Image links to*). Paste-ready text for the channel's **About** page (twitch.tv → Settings → Channel → *About* →
*Edit panels*, one panel per section below) and the **Bio**. Twitch has no API for panels, so these
are pasted by hand. Limits: panel title 45 characters, panel description 1,000 characters (Markdown
links work), bio 300 characters. Everything here is stream-clean.

Owner direction, 2026-10-08: *"put all the mod wiki urls and github mod repo and stuff in the twitch write ups they are all blank too"*.

Links (checked 2026-10-08, all answer 200):

| What | URL |
|------|-----|
| Mod site / wiki | https://g-fourteen.github.io/Rimrooms-AsyncIndustries/ |
| Source repo | https://github.com/Unity-Lab-AI/Backrooms |
| Bug reports | https://github.com/Unity-Lab-AI/Backrooms/issues |
| RimPLC wiki | https://g-fourteen.github.io/RimPLC/ |
| RimPLC source | https://github.com/G-Fourteen/RimPLC (and https://git.unityailab.com/GFourteen/RimPLC) |
| RimPLC bug reports | https://github.com/G-Fourteen/RimPLC/issues |
| Steam Workshop collection | https://steamcommunity.com/sharedfiles/filedetails/?id=3815722702 (the owner's pack collection *"Rimrooms: Async Industries - full mod pack (RimWorld 1.6)"*, 288 items, made 2026-10-08; owner 2026-10-08: *"and the rwmods is the mod collection"* · *"on steam"* · *"its mine"* · *"the first one i made"*) |

---

## Link icon panels

Owner, 2026-10-08: *"we need all the url links in a link icon thingy"*. One Twitch panel per link: upload
the image, put the URL in **Image links to**, leave the title and description empty (the image says
it). Images are 320x110 in the overlay's style, rendered by [`twitch-panels/render.py`](twitch-panels/render.py).

| Panel image | Image links to |
|-------------|----------------|
| ![](twitch-panels/panel-site.png) `panel-site.png` | https://g-fourteen.github.io/Rimrooms-AsyncIndustries/ |
| ![](twitch-panels/panel-install.png) `panel-install.png` | https://g-fourteen.github.io/Rimrooms-AsyncIndustries/install.html |
| ![](twitch-panels/panel-modlist.png) `panel-modlist.png` | https://g-fourteen.github.io/Rimrooms-AsyncIndustries/mods-list.html |
| ![](twitch-panels/panel-source.png) `panel-source.png` | https://github.com/Unity-Lab-AI/Backrooms |
| ![](twitch-panels/panel-bugs.png) `panel-bugs.png` | https://github.com/Unity-Lab-AI/Backrooms/issues |
| ![](twitch-panels/panel-workshop.png) `panel-workshop.png` | https://steamcommunity.com/sharedfiles/filedetails/?id=3815722702 |
| ![](twitch-panels/panel-rimplc-wiki.png) `panel-rimplc-wiki.png` | https://g-fourteen.github.io/RimPLC/ |
| ![](twitch-panels/panel-rimplc-github.png) `panel-rimplc-github.png` | https://github.com/G-Fourteen/RimPLC |
| ![](twitch-panels/panel-rimplc-forgejo.png) `panel-rimplc-forgejo.png` | https://git.unityailab.com/GFourteen/RimPLC |
| ![](twitch-panels/panel-rimplc-bugs.png) `panel-rimplc-bugs.png` | https://github.com/G-Fourteen/RimPLC/issues |

RimPLC rows added 2026-10-13 (owner: *"do the twitch setup for the RimPLC mod and its links and such for the infor
in twitch streams and stuff with all the image like text and chain emoji things for the mods and wiki links"* ·
*"im not really trusting the model to do that just yet"*). All four URLs answered 200 on 2026-10-13. **Applied to the live channel 2026-10-13** through the stream's Twitch window (Playwright over CDP :9333): the four RimPLC link panels, the RimPLC panel, the new bio, and the social link *Report a bug* replaced by *RimPLC mod & wiki* (owner's choice; Twitch caps social links at 5).

The text panels below stay as the long-form write-ups.

---

## Bio (300)

```
Unity plays RimWorld with our lab's mods: Rimrooms Async Industries (company contracts and a gate into the Backrooms) and RimPLC (live colony logic). Chat votes on what we build next. Mods, wikis and source in the panels below.
```

## Panel 1 — Title: `About the stream`

```
Unity plays a modded RimWorld colony live: **Marble Hollow**, a goth marble city that is building toward a gate into the Backrooms and, one day, a space-flying empire.

**Chat drives the game.** Vote on the next build, name colonists, pick research, call the shots in a raid. If Unity does what you asked, a follow is the thank-you.

Stream rules: be kind, keep it clean, no spoilers for other streams, no links you do not own.
```

## Panel 2 — Title: `The mod: Rimrooms Async Industries`

```
**Rimrooms: Async Industries** is a RimWorld mod, being prepared for 1.7 while retaining 1.6, about running a company branch that opens gates into the Backrooms: contracts, procurement, payroll, expeditions, and the gate complex itself.

- **[Mod site and wiki](https://g-fourteen.github.io/Rimrooms-AsyncIndustries/)**
- **[Install guide](https://g-fourteen.github.io/Rimrooms-AsyncIndustries/install.html)**
- **[First hour](https://g-fourteen.github.io/Rimrooms-AsyncIndustries/first-hour.html)**
- **[The company](https://g-fourteen.github.io/Rimrooms-AsyncIndustries/company.html)**
- **[Gates](https://g-fourteen.github.io/Rimrooms-AsyncIndustries/gates.html)**
- **[The Backrooms](https://g-fourteen.github.io/Rimrooms-AsyncIndustries/backrooms.html)**
- **[Scenarios](https://g-fourteen.github.io/Rimrooms-AsyncIndustries/scenarios.html)**
```

## Panel 3 — Title: `Mod list and Workshop`

```
The pack uses a curated community-mod list played on RimWorld 1.6. The new 1.7 unstable target
and each mod's 1.7 compatibility still need their own checks.

- **[Full mod list](https://g-fourteen.github.io/Rimrooms-AsyncIndustries/mods-list.html)**
- **[How the mods fit together](https://g-fourteen.github.io/Rimrooms-AsyncIndustries/mods.html)**
- **[Building and the interface](https://g-fourteen.github.io/Rimrooms-AsyncIndustries/building.html)** · [interface](https://g-fourteen.github.io/Rimrooms-AsyncIndustries/interface.html)
- **[Multiplayer](https://g-fourteen.github.io/Rimrooms-AsyncIndustries/multiplayer.html)**
- **[Steam Workshop collection](https://steamcommunity.com/sharedfiles/filedetails/?id=3815722702)**

Load order help: RimSort, [RimSort](https://github.com/RimSort/RimSort)
```

## Panel 4 — Title: `Source code and bug reports`

```
The whole project is open: code, art, docs.

- **[GitHub repo](https://github.com/Unity-Lab-AI/Backrooms)**
- **[Report a bug](https://github.com/Unity-Lab-AI/Backrooms/issues)**
- **[Troubleshooting](https://g-fourteen.github.io/Rimrooms-AsyncIndustries/troubleshooting.html)**
- **[Credits](https://g-fourteen.github.io/Rimrooms-AsyncIndustries/credits.html)**

Found a bug on stream? Say it in chat and Unity logs it.
```

## Panel 5 — Title: `RimPLC: colony logic mod`

```
**RimPLC** is our separate colony-logic mod: it reads the colony live, checks your rules and shows what to do next in an in-game ladder window. Unity uses it on stream to keep the colony alive.

- **Live sensors**: health, mood, food, materials, threats, research, temperature, alerts and buildings
- **Editable rules**: comparisons, OR, NOT, timers, counters and one-shots, saved with the colony
- **Advice first**: it tells you what to do; it never takes over your pawns
- No Harmony, no required mods, works with any mod list

- **[RimPLC wiki](https://g-fourteen.github.io/RimPLC/)**
- **[Source on GitHub](https://github.com/G-Fourteen/RimPLC)** · [Forgejo](https://git.unityailab.com/GFourteen/RimPLC)
- **[Report a RimPLC bug](https://github.com/G-Fourteen/RimPLC/issues)**
```

## Panel 6 — Title: `The overlay`

```
**Game** (big frame): the colony, live.
**Representation** (top right): Unity's picture and her scribbled screenshots of the action.
**Chat** (right): your messages and Unity's replies.
**Now saying** (bottom middle): what Unity is saying.
**Script log** (bottom right): the tools Unity is running right now, by name.
```

---

## Steam Workshop collection page

The owner's collection (https://steamcommunity.com/sharedfiles/filedetails/?id=3815722702) holds
exactly the 288 Workshop mods of the 294-mod pack (the other 6 are Core and the five DLCs). Owner,
2026-10-08: *"might need to update it"* · *"like i said might need to update it too"* -- the page, not
the list: title, description, cover. Edit it at Steam -> the collection -> *Edit*; the owner's Steam
login lives only in their own browser and app, so it is pasted there by the owner (or edited by Unity
in the separate window after a QR sign-in with the Steam mobile app).

**Title**

```
Rimrooms: Async Industries — full mod pack (RimWorld 1.6)
```

**Description** (Steam BBCode)

```
[h1]Rimrooms: Async Industries — the full pack[/h1]
Every Workshop mod the Rimrooms: Async Industries pack runs on: 288 mods, plus Core and all five DLCs (Royalty, Ideology, Biotech, Anomaly, Odyssey).

[b]Load order:[/b] use RimSort and the pack's mod list.
[list]
[*][url=https://g-fourteen.github.io/Rimrooms-AsyncIndustries/]Mod site & wiki[/url]
[*][url=https://g-fourteen.github.io/Rimrooms-AsyncIndustries/install.html]Install guide[/url]
[*][url=https://g-fourteen.github.io/Rimrooms-AsyncIndustries/mods-list.html]Full mod list[/url]
[*][url=https://github.com/Unity-Lab-AI/Backrooms]Source code[/url] · [url=https://github.com/Unity-Lab-AI/Backrooms/issues]Report a bug[/url]
[*][url=https://www.twitch.tv/unityplaysrimworld]Watch it played live: Unity Plays RimWorld[/url]
[/list]
```

**Applied 2026-10-08** in the owner's own Chrome tab (owner: *"edfit it directly"* / *"page is open"*): title, description, categories Mod + 1.6, *Items that work together*. Steam then holds it **hidden** until its automated link check passes.

**Cover image:** [`twitch-panels/steam-collection-cover.jpg`](twitch-panels/steam-collection-cover.jpg) -- **not applied yet**: Steam refused every upload with *"There was a problem uploading the file. Please try again in a little while"* (the owner's own try too); retry after the check clears.
