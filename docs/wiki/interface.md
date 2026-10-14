---
title: The interface
summary: "The Operations panel pane by pane, and what each control refuses and why."
---

# The interface

Everything the company does lives in one tab: **Operations**, first on the bottom bar.

---

## The panes

| Pane | What it is for |
|---|---|
| **Overview** | The branch at a glance; register headquarters; pay obligations |
| **Personnel** | Hire, pay, assign roles, train certificates |
| **Contracts** | Requests first, then priced jobs |
| **Ledger** | Account movements, with a reason for each |
| **Atlas** | Coordinates, bands, surveyed rooms |
| **Activity** | What has been happening |
| **Investigation** | Records, analysis, disputes, sign-off |
| **Machine** | The gate, numbered step by step |
| **Expedition** | Crew planning and dispatch |
| **Facilities** | Rooms, equipment links |
| **Procurement** | The corporate catalogue |
| **Sites** | Places on the books beyond headquarters |
| **Places** | Every place held open, the count against your allowance, and Release |
| **Help** | Glossary, your current keybind, readability |

**Help works with no game loaded.** A glossary you need a running company to open is not help.

## The Machine pane is numbered

Every step is numbered, with a tick when it is done and a line saying how to do it if it is not.
If a connection will not open, this pane says which step you are on.

## Colony controls

Below the panes, **Colony controls** opens the game's own tabs: Architect, Work, Assign, Research,
the world map.

These are the game's own buttons, pressed on your behalf.

---

## Keyboard

The Operations tab is bound to **`\`** (backslash).

The binding is made with RimWorld's own key-binding machinery, so it appears in your Key Bindings
dialog with everything else. **Rebind it freely** — Help reads your current binding, not the
shipped one.

> **Why not a function key.** Across the base game and a large mod list, F1 to F12 are all taken by
> something. Backslash is not.

---

## Colour, size and accessibility

**These screens set no colour and no text size of their own.** Your Options — interface scale,
font, colourblind mode — apply here exactly as they apply to the base game.

**Nothing required is carried by colour, sound or animation alone.** Gate readiness, the return
reserve, route tags, distance, recall warnings and record status each have a written label, and the
Machine pane's indicator lights are paired with the game's own tick glyph.

### The switches, and what each one leaves behind

Everything the mod draws or plays can be turned off, and **nothing turns off a word of text**. These
are in the mod's own settings.

| Setting | Off means |
|---|---|
| **Use the Backrooms background slideshow** | The main menu keeps the game's own background |
| **Reduced motion (show one still image)** | The menu shows one picture instead of cycling |
| **Show native gate aura** | A designated gate has its blue tint and no light of its own |
| **Show company gate frames** | A designated gate is the bare door, with no frame and no animation on it |
| **Reduce gate motion (hide aura; keep status text)** | No gate light and no gate animation. The panes and messages are untouched, which is what the label promises |
| **Mute gate cues** | The gate is silent |
| **Mute field and radio cues** | Reporting sounds are silent — a tag set, a journal filed, an analysis finished, a payment |
| **Cue volume** | Scales every company sound, underneath the game's own volume |

**A muted or hidden thing is never the only way to know something.** That is the rule the gate's
own light is held to: every state it shows already has a message, a pane indicator or both.

---

## Automation file (optional)

The mod can take orders from a file, for an external assistant that plays alongside you without
a mouse on your screen. Nothing uses it unless something writes to it.

- Commands: `RimroomsAutomation/inbox.jsonl` in RimWorld's configuration folder, one JSON object per
  line. Results: `outbox.jsonl` beside it, one line per command, with the command's `id` echoed back.
- Each command is something that otherwise needs a click: a zone's crop, a bed's owner, a bill, work
  priorities, an allowed area; and the setup steps of a colony -- rooms, exploring, stockpiles,
  shelves, stove, butcher table, freezer, crops, hunting; defence (arming, drafting, holding at
  cover, corner towers); building (walls, halls, roofs, conduit); power (a generator with a battery);
  research order; prisoners; trading by comms console; guest bed fees. Every reply says what was
  done or exactly why it was refused.
- It never spawns or destroys anything, never edits a definition, never touches the world map, and
  refuses a name it cannot find rather than guessing. Anything with a real cost in the game -- a
  trade, a request to a faction -- still pays that cost, and a colonist still has to walk there.

Examples, one per line:

```
{"cmd":"add_bill","x":155,"z":141,"recipe":"CookMealSimple","count":30}
{"cmd":"freezer"}
{"cmd":"arm"}
{"cmd":"trade","with":"caravan","sell":"Cloth:200","buy":"Steel:300"}
```

Delete the file to stop everything queued in it. The game's own controls always win.

---

## Two things this deliberately does not do

**It does not remap RimWorld's menus.** Nothing on the base game's tab bar is replaced, reordered
or patched. Remapping the interface would fight every interface mod you have installed, and
reachability was the actual requirement — the company tab is first, and everything it names is
reachable from inside it.

**It does not promise multiplayer.** See [Multiplayer](multiplayer.md).
