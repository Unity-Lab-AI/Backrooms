# -*- coding: utf-8 -*-
"""Record the close-out direction verbatim, close it, and sharpen the half that is still open."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

SECTION = NL.join([
"",
"## Owner direction — the hold notice closes out with a normalization notice (2026-10-05)",
"",
"**Verbatim owner direction (2026-10-05):** *\"do it and the notice needs to appear before the map bagins to load then close out with a normalization notice\"*",
"",
"**The hold notice makes a promise** — *nothing on this side advances until this finishes* — **and a promise with no close is a player wondering whether it ever did.** The pair is the feature: one says the stop is expected, the other says it is over.",
"",
"- [x] **\"the notice needs to appear before the map bagins to load\"** — **ALREADY TRUE AND NOW ASSERTED HARDER, 0.12.98-dev.** The ordering is the whole requirement and it was built this way: `EnsureSite` generates **synchronously** and hands the map back through an `out` parameter, so a window added immediately before it would draw on the *next* frame — **after** the freeze it was warning about. The work therefore moves into `LongEventHandler.QueueLongEvent`, the warning is drawn and dismissed while the game can still draw, and Core's own wait box then carries our keyed text through the freeze itself.",
"- [x] **\"then close out with a normalization notice\"** — **BUILT 0.12.98-dev, on Core's own completion callback rather than on a guess about timing.** `QueueLongEvent` takes a **`callback`** and invokes it after the event finishes — **read out of `LongEventHandler` in the shipped assembly rather than assumed.** The two alternatives were both worse: calling it at the end of the work would run it while the event is still the thing on screen, and `ExecuteWhenFinished` fires when the **whole queue** drains, a different moment the first time two events are ever queued together. "
"**It is deliberately not the full-screen surface the hold notice uses** — the player has just been put somewhere new and the first thing they should see is the place, not another picture of a corridor over the top of it. **It does not force a pause either**, because a notice announcing that time is moving again has no business stopping it. "
"**Toned per start like its other half, through one shared rule:** `Toned(baseKey)` was lifted out when the close-out needed the identical scoping, because two copies of a key-scoping rule is how a hold notice and its close-out end up toned for different scenarios. Four strings authored, each answering its own hold notice in the same voice — the company bills the interval, the shopkeeper counts the lights back on, the person alone checks their own hands. **Four claims and four plants**, including the one that matters: *the hold never closes out*.",
"",
"### And the measured half that is still open",
"",
"**Three paths can still reach generation with no notice at all**, measured rather than assumed — every caller of `EnsureSite` and of the three address registrars was read:",
"",
"| Path | Why it is uncovered |",
"|---|---|",
"| `GateSpinUp` completing the ramp | **A tick.** It needs `connectionId` back from `RegisterLaboratoryAddress` on the spot |",
"| `NaturalFrontierService` — walking into a found door | **A job tick**, same shape |",
"| `RimroomsExpeditionComponent.Dispatch` | Returns a `CompanyActionResult` its caller reads |",
"",
"**A long event is only legal where nothing is waiting on a return value**, which is why this hooks buttons rather than `EnsureSite`. The Operations pane, the gate's own address gizmo and the scenario opening are all covered; these three are not.",
"",
"- [ ] **Defer the result chain on the three tick-driven paths so they can announce too.** The owner named this entry point explicitly — *\"on gate enter and or using the operations tab machine when finally opening the gate\"* — and **the gate-enter half is the one still missing.** Each needs its continuation moved inside the long event instead of its result being read immediately, which is a real refactor of `GateSpinUp`'s completion and of the natural-door job, not a wrapper. **Until it lands, a player who starts a ramp from the console and walks away still meets an unexplained freeze**, which is the exact failure the feature exists to prevent.",
"",
])

text = io.open(TODO, encoding="utf-8").read()
if "closes out with a normalization notice" in text:
    print("section already present; nothing written")
    sys.exit(1)
if not text.endswith(NL):
    text += NL
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text + SECTION)
print("recorded: %d closed, %d open" % (SECTION.count("- [x] "), SECTION.count("- [ ] ")))
