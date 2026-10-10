# -*- coding: utf-8 -*-
"""Ledger for 0.12.30-dev: two of three starts had no campaign."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read(rel):
    return io.open(os.path.join(REPO, rel), encoding='utf-8').read()


def write(rel, s):
    io.open(os.path.join(REPO, rel), 'w', encoding='utf-8', newline='').write(s)
    print('updated %s' % rel)


def sub(rel, old, new):
    s = read(rel)
    assert old in s, '%s: anchor missing %r' % (rel, old[:70])
    assert s.count(old) == 1, '%s: anchor not unique %r' % (rel, old[:70])
    write(rel, s.replace(old, new, 1))


sub('CHANGELOG.md', u'## 0.12.29-dev', u"""## 0.12.30-dev - 2026-09-29 - you can call the company

- **Two of the three starts could never reach the campaign at all.** The shop opening and the solo/group opening both begin with no corporation watching, and there was no way to change that - which meant no contracts, no company catalogue, and no clean-up team coming for a stranded crew, for the whole game.
- **You can now call them, from a communications console.** Once they have you on the books the Async Industries request line starts, exactly as it does for the company start.
- **You have to have something to tell them.** A powered console, somebody awake who can speak, a coordinate you have actually been into, and a record book you brought home and had analysed. You are not calling for help; you are calling to say you found something.
- **The button always shows why it is not ready yet** rather than hiding until it is.
- **There is no way to take the call back.**

Full record: [two of three starts had no campaign](docs/implementation/CORPORATE_CONTACT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.29-dev""")

sub('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - two of three starts had no campaign (0.12.30-dev)

**Verbatim user quote:** *"keep at it, 27 to go thats the goal and any realted work"*

**Owner direction given mid-build, verbatim:** *"once they "contact the cvompany in comms" they can start async quest line"*

### What shipped

The caller `EstablishCorporationContact()` never had, which was the largest reachability hole found in this project so far.

### Files touched

`src/.../Company/CorporateContact.cs` **new**, `src/.../Company/CorporateContactGizmo.cs` **new**, `src/.../Gate/CompRimroomsGateConsole.cs`, `1.6/Languages/English/Keyed/RR_Requests.xml`, `.local/register/proof-corporate-contact.py` **new**, `.local/register/fault-plant-1230.py` **new**, `docs/implementation/CORPORATE_CONTACT_IMPLEMENTATION.md` **new**, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, `NOW.md`, `TODO.md`.

### Closure notes

- **FOUND BY FOLLOWING A ROW ABOUT SOMETHING ELSE.** I opened *"the solo/group start has no tutorial line"*, went looking for where a solo line would hook in, and found that `EstablishCorporationContact()` - one-way, event recorded, keyed string already written - **had no caller anywhere in the source.**
- **TWO OF THREE SHIPPED STARTS HAD NO CAMPAIGN AT ALL, PERMANENTLY.** `corporationContact` gates the entire tutorial line (`RequestLine.cs:305`), generated requests and the Purchase route (`RequestGeneration.cs:186`, `:90`), and **the clean-up team that comes for a stranded crew** (`FacilityRelief.cs:122`). Both the Store and Solo/Group starts declare `beginsInCorporationContact false`. No tutorial, no requests, no catalogue, no rescue, and no way to ever get any - two thirds of the openings a player can choose were a sandbox with a locked door.
- **BOTH DOCUMENTS SAID SO AND NEITHER WAS WRONG.** The chart: Store - *"Its own layout, and reaching contact is the achievement"*; Solo/Group - *"Same, from a different point of view"*. And `RR_Starts.xml` in its own comment: *"Reaching contact is the achievement here, not the starting condition."* **The achievement had no mechanism.** `SoloGroupHints` was already telling the player to build a comms console - a hint pointing at a thing with nothing to do with it.
- **THE OWNER'S ANSWER DELETED MOST OF THE WORK.** *"once they contact the cvompany in comms they can start async quest line"* settled two things: it happens on a comms console, and what it starts is **the existing Async line**, not a parallel one. `OfferNextTutorialRequest` already refuses until contact, so **nothing had to be authored for the line at all.** I had already found the obstacle to a separate line - `TutorialLine()` returns every def with `tutorial = true` with no notion of which start it belongs to, so a solo line would have needed a discriminator threaded through the def, the selector and the offer routine. **None of that was needed.**
- **It is earned, because the chart calls it the achievement.** Eight separate refusals: not operating, already in contact, no comms console, not a map the branch holds, unpowered, nobody employed who is present and able to speak, no coordinate the branch has been into, and **no analysed record**. That last is the substance - it means a crew found the door, went through, got a book home and somebody read it. **You are not calling to ask for help, you are calling to say you found something**, which is why the corporation takes the call. The refusal says it in as many words.
- **The reason shows on a DISABLED button, not a missing one** - invariant 28, a vanished gizmo teaches nothing. And the action **re-checks every condition** rather than trusting the button, because a gizmo can be clicked on the tick the generator goes off.
- **No new comp and no new patch.** Core's `CommsConsole` already carries `CompProperties_RimroomsGateConsole`, which already yields two Procurement gizmo providers, so this is a third on an established seam. **That component is also on `TableMachining`**, so the provider refuses anything that is not a `Building_CommsConsole` - nobody telephones a corporation from a machining table - and the proof fault-plants exactly that.
- **Twenty-seventh proof, fault-planted nine ways and caught 9 of 9**, including the gizmo no longer being yielded (which would restore the original hole), the tutorial line no longer gating on contact (which would make the call meaningless), and a start being *given* contact instead of earning it.
- Build 0.12.30-dev, **178 C# files, 87 package files**, **0 warnings, 0 errors**. Assembly `90E0885C229B6972E5209E3C30B4487F9BB3431AB5B5490A75B6B36188AA1923`, identical across two clean rebuilds. Ten checkers pass, **twenty-seven** proofs exit zero. **Starts that could reach the campaign before: 1 of 3. Now: 3 of 3.** **No game was launched, so nobody has placed this call.**

---

## Completed sessions""")

print('ledger written for 0.12.30-dev')
