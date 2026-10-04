# Rimrooms — Async Industries

**A RimWorld 1.6 campaign. You run a branch office of a company that does contract work in the
Backrooms.**

Ordinary colony play is untouched. What this adds is an employer, a machine that opens a way into
somewhere else, and paperwork about both.

**Current development version: 0.12.93-dev.** No balance, performance or compatibility result is
claimed.

---

## 📖 [Read the wiki →](docs/wiki/index.md)

| | |
|---|---|
| **[Install](docs/wiki/install.md)** | Requirements, mod manager setup, load order |
| **[Your first hour](docs/wiki/first-hour.md)** | Power, gate, crew, first crossing |
| **[The three starts](docs/wiki/scenarios.md)** | Which opening to pick |
| **[Gates and connections](docs/wiki/gates.md)** | The gate, and what fits through it |
| **[Beyond the gate](docs/wiki/backrooms.md)** | Coordinates, bands, what lives there |
| **[The company](docs/wiki/company.md)** | Money, requests, research, staff |
| **[Troubleshooting](docs/wiki/troubleshooting.md)** | When something refuses |
| **[Links](docs/wiki/links.md)** | Workshop, collection, issues |

---

## What it is

- A **gate** is an ordinary door you designate. No custom buildings, no new items.
- Door width decides what fits: people, then pack animals, then anything.
- Opening a **connection** is work an operator does at a console over time — not a button.
- Everything through it is a **coordinate**: a saved address you can return to.
- Things move between visits. Nothing tells you.
- The company pays into an **account**. Physical goods stay ordinary RimWorld goods.
- Your colonists work across a live connection — hauling, building, bills, research, medicine.
- **A branch never dies.** Lose everyone and the company arrives, cleans up, and bills you.

## Requirements

RimWorld 1.6, all five expansions, and the collection this build is authored against. Every
requirement is **declared**, so your mod manager names anything missing before the game loads.

See **[Install](docs/wiki/install.md)**.

---

## Building from source

```powershell
./tools/build.ps1          # restore, compile, package
./tools/stage-mod.ps1      # copy the package to your local mods folder
```

Needs the .NET SDK and a local RimWorld 1.6 install. The build treats warnings as errors and is
**deterministic** — two clean rebuilds produce an identical assembly hash.

Details in **[BUILDING.md](docs/BUILDING.md)**.

## Contributing

See **[CONTRIBUTING.md](CONTRIBUTING.md)** and the **[changelog](CHANGELOG.md)**.

Bug reports: **[open an issue](https://github.com/Unity-Lab-AI/Backrooms/issues)** with your
RimWorld version, your mod list, and the exact text of any message.

## Licence

Original source under **[MIT](LICENSE)**. RimWorld is supplied by Ludeon Studios and is not
bundled. No other mod's files are included or modified.

Full attribution in **[credits](docs/wiki/credits.md)**.
