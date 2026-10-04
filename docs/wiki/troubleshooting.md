---
title: Troubleshooting
summary: "Symptoms, what each one usually means, and what to send if it is ours."
---

# Troubleshooting

**Every refusal in the game names its own cause.** Read it — the cause is the instruction.

---

## The connection will not open

Operations names exactly one reason. Find it on the **Machine** pane, which numbers every step.

| It says | Do this |
|---|---|
| Not set to gate control | **Check both** — the machining table and the comms console each need it, separately |
| Assembly unfinished | Run the **assemble gate** bill: 100 steel, 8 industrial components |
| Nobody certified | Run the **train gate operator** bill. A machining table or a crafting spot will do |
| Out of calibration | Have a certified staff member calibrate it |
| No operator at the controls | Keep someone at the console — it is a job, not a checkbox |
| Reserve too low | More batteries, or more generation |
| No crew ready | Check the crew planner; it names who is not ready and why |
| No address to open to | Take one from a request, or **dial an unknown address** |
| No validated way home | The coordinate has no exit route yet |
| Gate damaged | Below half condition it will not hold. Repair it, then calibrate again |
| Connection was cut | Somebody threw the kill switch, or a containment breach cut everything |
| Too many places held open | You are at your allowance. Release one, or board up a free way in |

## Every box is ticked and it still will not connect

**Check gate control on both buildings.** The machining table and the communications console are
set to it separately, and setting one and not the other leaves a gate that looks finished and does
nothing.

These are steps 4 and 8 of eleven, and the Machine pane names which one is outstanding.

Then check the **address**. A gate needs a registered coordinate to dial, and the Machine pane will
say when the list is empty.

---

## This gate is blocked — too many places held open

Every place you hold open costs a loaded map, and so does each colony. You are at your allowance,
which is your own colony limit from Options.

Three ways on: **Release** a place you no longer need, **board up** a free way in for 25 wood, or
raise the colony limit in Options.

The Places pane shows the count, so you can check before walking anywhere.

## My crew is stuck on the other side

The return window expired. They are alive and their cargo is with them, at the saved address.

- **Reopen that route.** Fix whatever failed — power, calibration, the operator — and dial the same
  address again.
- **Or send a relief trip.** One extra person per run; the same relief member is reused for further
  attempts.

Nothing is lost by waiting, and the original crew is unchanged.

## I released a place and my stock was in it

**Release is permanent, and the confirmation says so.** It counts the items first and tells you how
many would be left behind.

A place you *found* rather than built is recoverable: it moves to a second list on the Places pane,
and selecting the door that led there offers it back.

A place reached through a gate you built does not come back.

---

## Other messages

| | |
|---|---|
| **"A company is not established"** | Overview offers to register headquarters. Do that first |
| **"The save uses a different record version"** | Keep the original save and use a matching build. **Do not re-save it** |
| **"A coordinate failed to generate"** | Atlas says so, keeps the address, and offers to re-address the survey. Your crew and stock are accounted for |
| **A colony control is unavailable** | Return to a colony map. Some tabs do not exist in the world view |

---

## The Operations tab is missing

- You are in the **world view**. Return to a colony map.
- Or the mod did not load — see [Install](install.md).

## The keybind does nothing

Another mod took `\`. Rebind Operations in your Key Bindings dialog; the Help pane will show your
new binding.

---

## Things moved while I was away

That is deliberate. Coordinates change between visits. Not every time, and nothing announces it.

## Something followed my crew home

Also deliberate, at the deepest band through an advanced gate. Closing the connection before it
arrives is what stops it.

## I took too long and missed a deadline

**There are no deadlines.** No request, contract, offer, quote or trade in this mod expires, and
nothing is penalised for delay. If something became unavailable it was not a clock — read the
message, which names its own cause.

---

## Everyone is down and the company turned up

Working as intended — see [A branch never dies](company.md#a-branch-never-dies).

It costs you every bond on the map and up to 25,000,000 from the account. The letter gives you the
figures.

This applies once a branch is in contact with the corporation. The Store and Lone survivor starts
have no such protection until they earn it.

---

## Reporting a problem

Include your RimWorld version, your mod list, and the exact text of the message. See
[Links](links.md).
