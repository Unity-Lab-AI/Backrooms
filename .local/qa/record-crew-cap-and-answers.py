# -*- coding: utf-8 -*-
"""Record the crew-cap removal (closed) and the three fork answers (open)."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)
ANCHOR = "### Owner direction — the journal and quest system itself, which the brief specified and nothing tracked (2026-10-06)"

S = NL.join([
"### Owner direction — pawns cross as they please, there is no maximum, and three was never their number (2026-10-06)",
"",
"**Verbatim owner direction (2026-10-06), four messages:**",
"",
"> *" + Q + "rememberber pawns can cross gate as they plkease so no max number" + Q + "*",
"",
"> *" + Q + "dont know where 3 came from" + Q + "*",
"",
"> *" + Q + "thats gonna have down stream effects especially in operations tab" + Q + "*",
"",
"> *" + Q + "and wiki and other things, all need accounted for" + Q + "*",
"",
"**THEY WERE RIGHT ON ALL FOUR COUNTS, AND THE THIRD WAS THE ONE THAT MATTERED.**",
"",
"- [x] **The crew cap is gone from every place it was enforced, claimed or implied.** "
"**Where three came from, measured rather than remembered:** it is the number of staff roles the "
"Async Industries start ships, and `SCENARIOS.md` ties a records bonus to *" + Q + "all three "
"crew" + Q + "* returning. **A scenario's headcount became a design cap by being written down "
"somewhere else.** Nothing ever asked the owner whether a crew had a maximum size. "
"**AND `CrewPlanner.MaxCrew` WAS NOT THE CAP, which is why the owner's warning about downstream "
"effects was the important message.** That constant only ever printed a number in a panel -- the "
"class's own documentation says it *" + Q + "returns a report and never a refusal" + Q + "* and that "
"*" + Q + "removing it entirely would change no outcome in the game" + Q + "*. **The real refusals "
"were `crew.Count > 3` in TWO dispatch paths**, `ExpeditionCargo` and "
"`RimroomsExpeditionComponent`. Removing only the panel's number would have left the planner saying "
"*as many as you send* while dispatch refused a fourth person -- **a worse state than the cap**, and "
"exactly what the owner predicted. Both upper bounds are gone; the lower bound of one stays, because "
"a dispatch with nobody in it is not a trip. "
"**A SECOND, REAL DEFECT THE CAP HAD BEEN HIDING.** `EvidenceSettlement` tested "
"`source.InitialCrew.Count == 3` for the records bonus, so **the bonus could only ever be earned by "
"a crew of exactly three** -- send two or four and it was silently unreachable while the contract "
"card still promised it. The rule was always *everybody who went came back*; the three was the start "
"def's roster. **With the cap in place no player could easily send four and discover it**, which is "
"the precise way a ceiling conceals a fault beneath it. "
"**Everything else accounted for, per *" + Q + "and wiki and other things" + Q + "*:** "
"`RR_Exp_InvalidCrew` said *" + Q + "one to three" + Q + "* and is the refusal a player actually "
"reads, so it was the most visible place the cap could have survived; `RR_UI_ContractTerms` and "
"`RR_UI_FieldObjectives` both claimed *" + Q + "all three crew" + Q + "*; `docs/wiki/first-hour.md` "
"said *" + Q + "Up to three field staff" + Q + "*; and `docs/SCENARIOS.md` carried the original "
"sentence, which now names where the figure came from so nobody reintroduces it. "
"**And the constant was deleted rather than set to `int.MaxValue`:** a cap of maximum-integer is "
"still a cap somebody can read as a rule, and nothing needs the number -- **the absence is the "
"rule.**",
"",
"## ⛔ AND THIS SUPERSEDES AN ANSWER THE OWNER GAVE MINUTES EARLIER, WHICH THEY NEED TO SEE ⛔",
"",
"Asked which research tiers to build, the owner answered **" + Q + "All six, including the fourth "
"crew member" + Q + "**. The sweep's fifth candidate is **Fieldcraft T5, " + Q + "the fourth "
"hand" + Q + "** -- a project whose whole effect is raising `MaxCrew` from three to four.",
"",
"**With no maximum, there is nothing for it to raise.** A project that unlocks a fourth crew member "
"when a branch can already send everybody is *" + Q + "a project that promises something and changes "
"nothing" + Q + "*, which is the exact phrase this repository has deleted four research projects "
"for. **So it is not built, and the decision is recorded rather than quietly dropped** -- the owner "
"may still want a Fieldcraft T5, but it has to be about a different number.",
"",
"- [ ] **Build the four clean research tiers**, which the owner approved: **Facilities T5** servicing "
"interval, which fills a gap **§1.1 itself names** -- maintenance is one of the four factors deciding "
"a gate's window and the only one with no project on it; **Measurement T5** the trained eye; "
"**Spatial T5** the near exit, the most visible unclaimed number in the mod; and **Entities T5** as "
"**`MaxEventsPerOpening` only**, confirmed at a second fork.",
"- [ ] **Entities T5 must not touch `QuietRoomFraction`, confirmed by the owner at the fork.** It is "
"half of the solo survivability guarantee -- *" + Q + "half of every coordinate's rooms bare by count "
"rather than by chance" + Q + "* -- and **a research project that moves a guarantee turns an absolute "
"into a tech gate.** The checker that asserts the absolutes has to refuse a project def that reads "
"that constant, or the rule is a note rather than a rule.",
"- [ ] **Spatial T6, the seventh level, which the owner approved and which needs content first.** The "
"sweep records it as *" + Q + "A CONTENT DECISION, NOT A SWEEP RESULT" + Q + "*: the palette carries "
"five bands and a seventh depth level has no look of its own. **Either a sixth band is authored or "
"level seven reuses the deepest existing band**, and the second is a stated limitation rather than a "
"blocker. Not started, and it is the one approved tier with a dependency outside research.",
"- [ ] **Fieldcraft T5 is superseded and needs a new subject if it is to exist.** See the "
"interdiction above: with no crew maximum its stated effect is unreachable. **Recorded rather than "
"dropped**, because the owner approved a Fieldcraft tier and what they approved was a tier, not that "
"particular number.",
"- [ ] **Four machine benches: split the gate's component count across the linked benches.** Owner's "
"fork answer, chosen over *any linked bench satisfies the bill* and over leaving it documented. "
"**The cost was named in the option and is the thing the build has to answer:** a destroyed or "
"unlinked bench leaves an unfinishable remainder, so the split has to be recomputed when the set of "
"linked benches changes rather than fixed at the moment the bill is placed. Owner's words for why any "
"of it exists: *" + Q + "with say upto 4 of them available so pawns can do geate process better and "
"faster" + Q + "*.",
"",
])


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    if "pawns cross as they please, there is no maximum" in text:
        print("already recorded")
        return 1
    if text.count(ANCHOR) != 1:
        print("anchor matched %d time(s); refusing" % text.count(ANCHOR))
        return 1
    at = text.index(ANCHOR)
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(text[:at] + S + NL + text[at:])
    print("recorded: 1 closed, 5 open")
    return 0


if __name__ == "__main__":
    sys.exit(main())
