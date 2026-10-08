# Twitch channel write-ups — Unity Plays RimWorld

Paste-ready text for the channel's **About** page (twitch.tv → Settings → Channel → *About* →
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
| Steam Workshop collection | **not published yet** -- say "coming soon", never a made-up link |

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
| ![](twitch-panels/panel-workshop.png) `panel-workshop.png` | *(no link until the collection is published)* |

The text panels below stay as the long-form write-ups.

---

## Bio (300)

```
Unity plays RimWorld with Rimrooms: Async Industries, a Backrooms mod pack built by our lab. Goth city building, company contracts, and a gate into the Backrooms. Chat votes on what we build next. Mod, wiki and source in the panels below.
```

## Panel 1 — Title: `About the stream`

```
Unity plays a modded RimWorld colony live: **Marble Hollow**, a goth marble city that is building toward a gate into the Backrooms and, one day, a space-flying empire.

**Chat drives the game.** Vote on the next build, name colonists, pick research, call the shots in a raid. If Unity does what you asked, a follow is the thank-you.

Stream rules: be kind, keep it clean, no spoilers for other streams, no links you do not own.
```

## Panel 2 — Title: `The mod: Rimrooms Async Industries`

```
**Rimrooms: Async Industries** is a RimWorld 1.6 mod about running a company branch that opens gates into the Backrooms: contracts, procurement, payroll, expeditions, and the gate complex itself.

- **Mod site and wiki:** https://g-fourteen.github.io/Rimrooms-AsyncIndustries/
- **Install guide:** https://g-fourteen.github.io/Rimrooms-AsyncIndustries/install.html
- **First hour:** https://g-fourteen.github.io/Rimrooms-AsyncIndustries/first-hour.html
- **The company:** https://g-fourteen.github.io/Rimrooms-AsyncIndustries/company.html
- **Gates:** https://g-fourteen.github.io/Rimrooms-AsyncIndustries/gates.html
- **The Backrooms:** https://g-fourteen.github.io/Rimrooms-AsyncIndustries/backrooms.html
- **Scenarios:** https://g-fourteen.github.io/Rimrooms-AsyncIndustries/scenarios.html
```

## Panel 3 — Title: `Mod list and Workshop`

```
The pack runs on a curated list of community mods, every one checked for compatibility.

- **Full mod list:** https://g-fourteen.github.io/Rimrooms-AsyncIndustries/mods-list.html
- **How the mods fit together:** https://g-fourteen.github.io/Rimrooms-AsyncIndustries/mods.html
- **Building and the interface:** https://g-fourteen.github.io/Rimrooms-AsyncIndustries/building.html · https://g-fourteen.github.io/Rimrooms-AsyncIndustries/interface.html
- **Multiplayer:** https://g-fourteen.github.io/Rimrooms-AsyncIndustries/multiplayer.html
- **Steam Workshop collection:** coming soon.

Load order help: RimSort, https://github.com/RimSort/RimSort
```

## Panel 4 — Title: `Source code and bug reports`

```
The whole project is open: code, art, docs.

- **GitHub repo:** https://github.com/Unity-Lab-AI/Backrooms
- **Report a bug:** https://github.com/Unity-Lab-AI/Backrooms/issues
- **Troubleshooting:** https://g-fourteen.github.io/Rimrooms-AsyncIndustries/troubleshooting.html
- **Credits:** https://g-fourteen.github.io/Rimrooms-AsyncIndustries/credits.html

Found a bug on stream? Say it in chat and Unity logs it.
```

## Panel 5 — Title: `The overlay`

```
**Chat** (left): your messages and Unity's replies.
**Representation** (right): Unity's picture and annotated screenshots of the action.
**Script log** (bottom right): the tools Unity is running right now, by name.
**Captions** (top): what Unity is saying.
```
