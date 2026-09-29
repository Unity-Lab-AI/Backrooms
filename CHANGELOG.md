# Changelog

## 0.8.7-dev - 2026-09-29 - the deeper it is, the less it pretends

- **Hallways can hold anything.** A production bench in a corridor is not a mistake down there.
- **Shallow spaces still make sense.** Deep ones stop bothering, and the change is gradual rather than a switch.
- **Some rooms in a deep space still read as ordinary**, on purpose. If everything is wrong, nothing is unsettling.
- **The strange kinds of room get commoner the further in you go**, until the ordinary ones are the surprise.
- **What you find scales with what you have researched and how deep you have pushed.** A young colony finds crude things; an advanced one starts turning up spacer equipment.
- **A deep space is worth going back to.** The same coordinate after a hundred hours of research is a different place.

Full record: [coherence and tech scaling](docs/implementation/COHERENCE_AND_TECH_SCALING_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.8.6-dev - 2026-09-29 - the shape of the place

- **Deep spaces are not built to a grid any more.** Rooms stretch, shrink and go wrong, and they go wronger the further in you are.
- **Some of them are shaped like rooms you built.** The place took their proportions when it opened - not what you have built since.
- **Lots of hallways.** Long narrow corridors that are corridors on purpose, not by accident.
- **The shallow yellow rooms stay regular.** That monotony is the look, and it is left alone. The wrongness is something you travel toward.
- Spaces you already found are completely unchanged, down to the last cell.
- Building an extension at home does not reshape a space you have already opened.

Full record: [room shape echoes](docs/implementation/ROOM_SHAPE_ECHO_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.8.5-dev - 2026-09-29 - the place copies your people

- **Somebody you know can be standing in a deep space**, wearing your colonist's name and the clothes they put on this morning.
- **That colonist is at home right now.** That is the whole point of it.
- It is not them. It has their name and their coat and nothing else - not their skills, not their history, not their mind.
- **It is never hostile**, and you cannot recruit it. It is not a person you can save.
- Your actual colonist is untouched and keeps their own clothes.
- If everyone is down there with you, or hurt, or gone, no echo appears at all.
- **Nothing you have not found yet can die of neglect.** People and bodies in rooms you have not reached are held exactly as they were - nobody starves, freezes or rots behind a door you have not opened.
- **Finding them is what starts their clock.** Once you have seen a room, everything in it lives and suffers normally.

Full record: [colonist echoes](docs/implementation/COLONIST_ECHO_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.8.4-dev - 2026-09-29 - things that happen

- **Things happen in the Backrooms now**, not just things being there. A noise with nothing making it. Every light switching itself off. Cold with no source. The place getting filthier. Loose things not where you left them.
- **Everything that happens has an answer you can actually perform.** The lights come back on with the same switch you already use. Cold is answered by clothing or a heater or leaving. Filth is answered by cleaning, which already works through a gate.
- **Nothing that happens can trap you.** No event hurts anyone, destroys anything, or blocks a route, and the room you arrive in is never touched.
- **Nothing that moves is ever lost** - it is somewhere else in the same space. Your money is never moved at all.
- At most two things happen per visit, and a space does not replay the same trick every time you go back.
- **Deep spaces now also contain things you have owned**, not just things you have built.

Full record: [anomaly events](docs/implementation/ANOMALY_EVENTS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.8.3-dev - 2026-09-29 - getting somebody out, and earning what comes against you

- **You can offer a survivor passage home.** They accept - there is no negotiation and no recruitment roll. Somebody lost down there who meets a team with a way out wants to leave.
- **Joining is what lets them walk out.** Until they accept they are an inhabitant, and an inhabitant cannot use a gate at all - the only way out for them is to be carried, like anything else you find.
- One of your people has to actually be standing there to make the offer.
- **The Backrooms now starts by sending one thing at a time**, not three.
- **It only sends more once you have gone deeper than you ever have**, and when that happens it is written into your branch history so you can see the moment the rules changed.
- Stay shallow and it stays at one, however rich or advanced you get.
- It never goes past three.

Full record: [survivors and cap progression](docs/implementation/SURVIVORS_AND_CAP_PROGRESSION_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.8.2-dev - 2026-09-29 - who you find down there

- **There are people in the Backrooms now.** Wanderers who do not explain themselves, survivors who will leave with you, people who went missing, and ones who have been down there far too long.
- **A missing person may be somebody you lost.** The Backrooms remembers people it keeps, and gives you the name back.
- **Bodies are there from the first visit**, carrying what they came in with. Older ones have been picked over.
- **Living things are not there on your first visit.** They arrive as a space gets worse, and a space only gets worse from what you did there.
- **Never more than three hostiles at once**, at any depth, at any wealth.
- **You get told before you meet one.** Hostiles hold their ground rather than hunting you, so backing out is always a real option.
- Nothing you find down there will follow you through a gate on its own.
- Nobody is ever standing between you and the way back.

Full record: [inhabitants](docs/implementation/INHABITANTS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.8.1-dev - 2026-09-29 - the place starts copying you

- **Push far enough into the Backrooms and the rooms start containing things you built.** Your benches, your beds, your machines - arranged by something that has clearly seen them.
- It counts what you build anywhere: in the colony, or inside a coordinate.
- **It does not copy its own furniture**, so deep spaces do not slowly all turn into the same room.
- **It only copies some of it.** The rest of the room stays strange, which is the whole point.
- Only spaces three or more portals in do this. The first couple still feel like somewhere that existed before you did.
- It forgets. Stop building something and it eventually stops appearing down there.
- A brand-new colony that has built almost nothing still gets fully furnished deep rooms.

Full record: [the construction echo](docs/implementation/CONSTRUCTION_ECHO_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.8.0-dev - 2026-09-29 - the Backrooms paces against what you have built

- **How dangerous a space becomes is now paced against your colony's wealth**, the same measure the game's own storyteller uses.
- **A space only gets worse from things you actually did** - how often you went in, and how long you stayed. Never from the clock, never from a reroll when you reload, never from simply having a gate open.
- **Going back to a space you know resumes where it was.** It does not get worse for revisiting, and it does not get safer either.
- **Walking in is never the dangerous part.** A first visit is always quiet, however rich you are and however deep the space.
- **Half of every space is quiet, always.** Not by luck - by count. You will never open a coordinate with something in every room.
- **No more than three things can ever act at once**, at any depth, at any wealth. That is a hard number, not a curve.
- Several open gates never add up into one bigger threat.
- Shallow spaces stay survivable no matter how rich you get.

Nothing acts yet - this is the pacing the inhabitants will be held to.

Full record: [the escalation ladder](docs/implementation/ESCALATION_LADDER_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.7.9-dev - 2026-09-29 - rooms that are a kind of place

- **Deeper coordinates now contain recognisable rooms** - laboratories, workshops, dormitories, canteens, storerooms, offices, wards, machine halls, nurseries and salvage caches.
- **Further in, some of them are wrong.** A gallery. A room you have already been in, laid out exactly the same. An assembly of things that belong in different rooms. A hoard.
- **Two rooms of the same kind are not the same room**, and the same room is the same every time you go back to it.
- **The shallow yellow rooms stay empty.** That emptiness is the look, and nothing will be put in them.
- The room you arrive in is never dressed, so the way back is never buried.
- **Furniture comes from whatever you have installed.** A mod that adds a workbench puts it in Backrooms workshops without either mod knowing about the other.

Full record: [room archetypes](docs/implementation/ROOM_ARCHETYPES_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.7.8-dev - 2026-09-29 - the yellow rooms

- **The first Backrooms space now looks like the Backrooms.** Yellow carpet, yellow wood walls, and lights on the walls instead of lamps standing in the middle of the floor.
- **The first one always looks like that**, on every seed. It is the image the whole thing rests on.
- **Deeper spaces do not.** Coordinates now know how far in they are, and the look changes with depth: poolrooms, machinery, abandoned offices, cold storage, and one band where the place stops agreeing with itself.
- The same deep space looks the same every time you go back to it.
- Spaces in an existing save read as shallow, so nothing you have already found changes.

Full record: [the palette](docs/implementation/BACKROOMS_PALETTE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.7.7-dev - 2026-09-29 - the company will buy, and pay you in paper

- **Sell to the company at a credit beacon.** Everything tradeable in the beacon's range goes at once, and you see the total before you commit.
- **Odd goods fetch half again over market**, because nobody else can get them. Ordinary valuables go slightly under, because the company is instant and a trader is not.
- **Traders are still the better price for ordinary goods if you can wait for one.** That is on purpose.
- Your gold and silver finally have somewhere to go that is not a passing caravan.
- **Company bonds in range are never sold** - banking one is a different thing, and selling your own money by accident is not a feature.
- **Withdraw credits as paper at the gate console.** Pick a denomination off the ladder, get one bond of that size.

Full record: [the exchange](docs/implementation/VALUABLES_EXCHANGE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.7.6-dev - 2026-09-29 - the corporation will sell you things, eventually

- **The parent corporation is now a trader you can call in** from the gate console. It arrives in orbit like any other trade ship, and trading works exactly as it always does, beacon and all.
- **Its catalogue is tiered, and each tier has three locks**: research you have to finish, company work you have to have completed, and an access fee in credits.
- **That access fee is what your bonds are for.** A vault of paper now buys capability, not just goods.
- **A locked tier sells nothing and buys nothing** - it will not quietly take your goods off you for a catalogue you have not opened.
- **A locked tier tells you which lock is holding it**, rather than just refusing.
- The first tier is open from the start, because a supplier who sells you nothing until you have already made it is not a supplier.
- Each tier sells whatever the loaded game puts in its category, so mods that add materials show up in the catalogue without this mod knowing they exist.

Full record: [corporate supply](docs/implementation/CORPORATE_SUPPLY_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.7.5-dev - 2026-09-29 - company bonds, from ten credits to a quadrillion

- **Company credits can now be held as physical bearer bonds.** Print them at a machining table, haul them, stack them in a vault, hand them around.
- **Fifteen denominations**, every power of ten from 10 credits up to a quadrillion. Ten of any size is worth one of the next size up.
- **You are always paid in the fewest, largest bonds.** Withdraw a trillion and you get one piece of paper, not a warehouse.
- **A trade beacon can be designated as a credit beacon.** It shows the face value of every bond in its range, and banks them into the company account on command.
- **Banking a bond destroys it.** No spent certificate left lying around.
- **Bonds are physical, and that means physical.** They burn. They can be carried off. That is the price of holding your money where you can reach it, and it is why the company account still exists.
- Silver, gold, jade and ivory are untouched. Your vault works exactly as it always did.

Full record: [company bonds](docs/implementation/COMPANY_BONDS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.7.4-dev - 2026-09-29 - the place gets into people, and everything from it is marked

- **Everything that comes out of a coordinate is odd now, not just what was lying there.** Rock you mined from its walls, material from a partition you pulled down, plants you cut in its rooms - all of it.
- **Things you carry in stay ordinary, permanently.** Haul your own cotton down there and back and it is still your own cotton.
- **Being in the Backrooms wears on people.** Minus one the moment they step through, sliding toward minus ten over about an hour of real time down there.
- **It follows them home.** The feeling fades after they leave rather than switching off at the door, so rotating shifts works and living down there does not.
- **You can build against it.** A lit, properly enclosed room made of material you hauled in slows it right down. Fixtures you found in place do nothing - it has to be real material from outside.
- Nothing you build makes the place ordinary. The first point never goes away.

Full record: [origin and pressure](docs/implementation/BACKROOMS_PRESSURE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.7.3-dev - 2026-09-29 - somebody wants the odd goods

- **Buyers now turn up wanting goods recovered from the Backrooms**, and they will not take the ordinary equivalent. Your own cotton is no substitute for cotton that came out of a coordinate.
- **They only ask for things a space you have actually opened really held.** No contract will ever send you looking for something that was never down there.
- **They pay well over the ordinary rate** - these are goods nobody else can source.
- Up to three demands stand open at a time, and a new one arrives about once a day.
- Delivery is automatic once the goods are home: the contract settles and pays, and it pays once even if you reload in the middle of it.
- Uninstalled buildings count. Haul a machine home from down there and it is still the thing the buyer wanted.

Full record: [odd supply contracts](docs/implementation/ODD_SUPPLY_CONTRACTS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.7.2-dev - 2026-09-29 - what comes out of the Backrooms is marked

- **Anything you carry out of a Backrooms coordinate is marked odd.** A stove you found down there, a stack of cotton off a shelf, a door you uninstalled: it comes home labelled `(odd)`.
- **Odd goods never stack with ordinary ones.** Odd cotton and your own cotton sit in the same stockpile as two separate stacks, and neither one absorbs the other. Split an odd stack and both halves stay odd.
- **Uninstalled buildings keep the mark.** Uninstalling a machine you found and hauling it home does not launder it back into an ordinary one.
- **Bringing your own goods in does not make them odd.** Only what was already down there counts.

Nothing asks for odd goods yet. This is the marker the contracts will be written against.

Full record: [odd origin](docs/implementation/ODD_ORIGIN_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.7.1-dev - 2026-09-29 - the gate assembly needs looking after

- **A gate now holds a condition that slowly wears down**, and somebody has to recondition it before it runs out. A gate with nothing left will not open until it is seen to.
- **How fast it wears depends on how you keep the room.** A clean, sterile gate chamber wears at half rate; a filthy one wears at triple. Look after the place and the gate mostly looks after itself.
- **An unpowered assembly degrades eight times faster**, so cutting the power has a cost beyond closing the gate.
- Holding a connection open wears it faster too.
- **Nobody is sent to it until it actually needs it.** Above a quarter condition the job is not offered at all, so your people are not forever fiddling with the gate. Reconditioning restores it fully in one visit.
- Running out **never slams a gate shut on people who are already through**. It stops the next opening; it does not end one in progress.

Existing gates load in full condition, so nothing you already built is suddenly out of service.

Full record: [gate servicing](docs/implementation/GATE_SERVICING_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.7.0-dev - 2026-09-29 - a cutoff you can throw

- **A gate can now be given an emergency cutoff**: a power switch on its own circuit that somebody can throw to shut an open gate at once.
- **The switch has to actually carry the gate's power.** One that is not wired into the line feeding the gate cannot be chosen at all, and says why. No believing in a cutoff that would not work.
- Throwing it ends the opening immediately and says so plainly — *the cutoff was thrown*, not *the power failed*. Those were the same message before, and they are not the same event.
- **Anyone still on the other side keeps their emergency return window.** That window is the whole reason the gate holds its own power reserve, and one flick should not strand people for good.
- Throwing a switch is ordinary work, so you can order somebody at home to do it while a team is still inside. That is what it is for.
- Gates without a cutoff work exactly as before. Nothing needs rebuilding or rebinding.

Worth knowing: cutting a gate's power already closed it. What was missing was the gate knowing *which* switch was its own, checking that the switch really powers it, and telling you apart a deliberate shutdown from a broken wire.

Full record: [the kill switch](docs/implementation/GATE_KILL_SWITCH_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.6.9-dev - 2026-09-29 - a way out, and it comes up where you said

- **A doorway in the Backrooms can now lead back out into the world**, instead of only ever leading deeper. Roughly one in three ways onward does, once you have somewhere for it to come up.
- **You choose where it comes up.** Any door on a map you hold can be marked as a way home, with one command on the door itself. Nothing is ever marked for you — a way out only ever arrives at a door you picked.
- A door inside the Backrooms cannot be marked, because a way out cannot come up in the place it leads away from.
- With nothing marked, doorways simply lead deeper as before. Nothing is refused and nothing is lost.
- The same doorway always leads to the same place. Saving, reloading and revisiting never change it.
- Unmarking a door stops new ways out coming up there, and deliberately leaves any that already exists alone.

Two unrelated fixes found while working: one message on the gate was sharing a name with another, so one of the two was always wrong — the operator-away refusal and the operator readout now have separate names. And there is now a check that no two messages can share a name again.

Full record: [a way out](docs/implementation/CONNECTED_EMERGENCE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.6.8-dev - 2026-09-29 - zones work on both sides of a gate

- **A growing zone inside the Backrooms no longer traps the person you sent to it.** Backrooms floors are concrete, and nothing can be planted in concrete — but somebody was being sent to sow there anyway, and once they arrived the game correctly refused while the mod still believed there was work, so they stood there doing nothing and never came back. Nobody is sent now unless the ground can actually take the crop.
- Everything else about zones on both sides of a gate was checked rather than assumed. Stockpiles on the far side pull goods across and honour their own filters and priority. Fishing zones, home areas and per-colonist allowed areas all read the far side's own settings.
- Zones you paint in a Backrooms space survive leaving and coming back, along with their settings.

One honest note on what "continuous" can mean: the game does not allow a single zone to cover two maps, so two zones either side of a gate stay two zones. They already behave as one in the way that matters — put something in one and a hauler will move it to the other when that is a better home for it.

Full record: [zones and areas across a gate](docs/research/ZONES_AND_AREAS_ACROSS_A_GATE.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.6.7-dev - 2026-09-29 - every kind of work in the game now crosses a gate

- **Containers on the other side get tended.** A fermenting barrel that wants wort or has beer ready, an egg box with eggs in it, and a pack animal you marked to unload will all now pull somebody across a gate.
- Nobody crosses for a barrel with no wort on that side, or one sitting at a temperature that would ruin it.
- **Somebody will cross a gate to flick a switch, open a container, or eject fuel** — but only where you marked it. Nothing is guessed.
- **With the Odyssey expansion, somebody will cross to fish** a zone you painted on the other side. Water you never zoned attracts nobody.
- All of it is tunable while the game runs, like the rest.

That closes the last of the gaps found when every kind of work in the game was listed out and checked. Every one is now either handled or deliberately left alone with the reason written down.

Full record: [the last work type gaps](docs/implementation/WORK_TYPE_GAPS_CLOSED_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.6.6-dev - 2026-09-29 - study what you contain, through a gate

- **A researcher now crosses a gate to study a contained entity on the other side.** A containment facility reached through a portal is the whole idea of this mod, and until now nobody would walk to one.
- An empty holding platform attracts nobody. Neither does an entity still on its study cooldown, or one whose study you switched off.
- The game's own study work does the studying once your researcher is standing there, exactly as it does at home.
- This needs the Anomaly expansion. Without it the work simply does not exist, rather than misbehaving.

**A load error fixed, present since 0.6.4-dev.** The two cross-gate childcare work entries referred to a work type that only the Biotech expansion adds, with nothing marking them as needing it. On a copy of the game without Biotech that produced an error at startup — in a mod that is supposed to need nothing but the base game. Both are now marked correctly, and a new check reads the game's own data to make sure no future entry can slip through the same way.

Full record: [dark study](docs/implementation/CONNECTED_DARK_STUDY_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.6.5-dev - 2026-09-29 - somebody actually runs the bill on the other side

- **A bench on the other side of a gate now gets worked.** Until now ingredients were carried through to a bill and then nobody came to make anything, so a workshop in the Backrooms just accumulated material. A cook, crafter, smith, tailor or sculptor will now cross a gate to run the bill itself.
- **The game's own crafting does the work, exactly as it does at home.** Nothing about recipes, quality, skill gain or part-finished items is reimplemented here — your colonist walks over and the game takes it from there.
- **A bill you restricted to one person still only pulls that person**, and a bill with a skill minimum only pulls somebody who meets it. Neither ever drags the wrong colonist through a gate.
- **Nobody crosses for a bench that has no materials.** A workshop over there with nothing to work with attracts nobody, rather than sending someone on a pointless walk over and over.
- **Nobody crosses for a bench that has simply run out of fuel** either — fuel gets carried to it instead, which already worked.
- Local work always wins. Somebody only crosses when there is nothing of that kind to do on this side at all, and somebody already on their way is never turned around.
- All of it is tunable while the game runs, like the rest.

One fix to something already shipped: bills belonging to the automatic production and mech systems were being supplied with ingredients even though the mod's own notes said they were left alone. They are now genuinely left alone until they get a proper look.

Full record: [bill work](docs/implementation/CONNECTED_BILL_WORK_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## Repository tooling - 2026-09-29 - the 294-mod register actually opens now

**No change to the mod itself.** The mod build is byte-for-byte identical to 0.6.4-dev and the version was deliberately not bumped. This entry covers the project's own research register, which lives beside the mod rather than inside it.

- **The register now opens.** The spreadsheet never could on this machine: there is no spreadsheet program installed and Windows has no idea what a `.xlsx` is, so it was being handed to an unrelated application. There is now an **HTML register beside it** that opens straight in a browser with no install and no internet — same four views, plus a search box that filters all 294 mods across every column as you type, and dropdowns for how each mod is treated and whether that decision is settled yet.
- The 294-mod integration register workbook also had four real faults, now fixed for anyone who does have a spreadsheet program. Every text cell in it claimed to be a formula result when nothing in the file was a formula; all 294 rows were pinned to a fixed height that the spreadsheet was then forbidden to expand, so five columns — including every evidence field — were cut off on screen; its summary page counted 45 categories where the rows hold 66, with eleven wrong numbers; and there was no way to rebuild it, while six columns of work existed in that one file and nowhere else.
- Both versions are now four views instead of two: a summary, an **index** that fits on one screen with a link to each mod, the **full grid** for filtering, and a **card per mod** where no field is ever cut off.
- The counts on the summary page are now worked out from the rows each time it is built, so they cannot quietly go stale again.
- It can be rebuilt from plain text files that live in the repository, and a second tool reads every cell back out and checks it against them.
- A broken link in the task list that had been failing the project's own audit was found and fixed along the way.

Full record: [the register rebuild](docs/implementation/MOD_REGISTER_REBUILD.md) and [the work type coverage audit](docs/research/WORK_TYPE_COVERAGE_AUDIT.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.6.4-dev - 2026-09-29 - the Backrooms has no sky, and the last three kinds of work

- **A Backrooms space now has no outside anywhere in it.** Every cell of it sits under thick mountain rock, and the space between its rooms is solid stone rather than open ground. Previously most of a generated space was open to the sky, which was wrong.
- **That ceiling can never be opened.** Marking a no-roof area inside the Backrooms does nothing, and if anything else removes a piece of roof it is put straight back. There is no way to make a hole in the world from the inside.
- **You can still take the place apart completely.** Walls and doors deconstruct, the stone is mineable in several materials, and floors can be lifted. Mine a whole space out if you like — the ceiling collapses into rubble the way a mountain does, and it still never leaves a gap.
- **Your own colony is untouched by all of this.** Building roof, removing mountain roof and building mountain wall all work exactly as they always did anywhere outside the Backrooms.
- Wardens now cross a gate to prisoners held on the other side, and food already reaches them, so the two work together without anything extra.
- Carers cross to a baby on the far side, where the expansion that adds babies is present.
- Animal handlers cross for animals you marked for slaughter, taming or release — but not merely because an animal over there could be sheared some day.

One thing named rather than assumed: lifting a floor does not return materials in the base game, so carpet and tile being reused or sold is its own piece of work still to come.

Full record: [containment and care](docs/implementation/CONTAINMENT_AND_CARE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.6.3-dev - 2026-09-29 - a way onward can turn up out in the world

- Doorways that lead somewhere else can now be found out in the ordinary world, not only deep in the Backrooms. Much rarer out there, and at most one per map, because it should be a notable thing rather than a fixture.
- **A door your own people built is never one of them.** A way onward is found in something that was already standing there, so installing this mod never quietly turns part of your base into a permanent hole in the world.
- A doorway that already has a gate machine on it is left alone too.
- The same doorway always leads to the same place. Reloading or revisiting never rerolls it, and every space already found in an older save still leads exactly where it did.

Two things worth knowing about what was already true, because they did not need building: a portal found inside a space reached by a portal already works to any depth, and a way onward has always led to a genuinely new place with its own seed rather than linking two you already knew. What is still to come is a portal that opens out onto the ordinary world rather than into another Backrooms space; the groundwork for it is named in the register.

Full record: [continuous topology](docs/implementation/CONTINUOUS_TOPOLOGY_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.6.2-dev - 2026-09-29 - eight more kinds of work cross a gate

- Cleaning, repair and firefighting now happen across a gate — but only inside a Home area you set on that side. A Backrooms corridor nobody called home attracts nobody, exactly as it already did for the game's own colonists.
- Mining, hunting, cutting plants and working a growing zone all cross a gate too, and every one of them only where **you** marked it wanted. Nothing is guessed: no designation, no zone, nobody goes.
- Fuel and shells are carried through a gate to anything of yours that has run dry — a generator, a smithy, a mortar, an autocannon. Each takes whatever it actually accepts, so a modded machine with its own odd fuel is handled without anything special.
- A machine you told not to auto-refuel is left alone, and nothing crosses if fuel it can use is already sitting on that side.
- A colonist will not cross toward a fire if the route to the gate breaks the danger rules you set. A fire on the other side does not override what you allowed.
- A local emergency, and local work of the same kind, always come first for every one of these.
- All of it is tunable while the game runs, like the rest.

Full record: [eight more families](docs/implementation/CONNECTED_WORK_FAMILIES_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.6.1-dev - 2026-09-29 - a casualty gets a bed where they lie

- Somebody will now cross a gate to put a downed colonist into a bed on that side, instead of carrying them all the way home first. Taking an injured person through a gate is one more trip for somebody who cannot walk, so if there is a bed over there, the help goes to them.
- If there is no bed on that side, nothing changes: they are carried home to one, exactly as before.
- Babies are never picked up this way, and a prisoner bed is never used for one of your own people.
- A casualty at home still comes first, and a rescuer already on their way to a gate is not turned around by one somebody else can reach.

Two things deliberately **not** added. A tired colonist will not walk through a gate to go to bed, and this one is not a judgement call: the game itself refuses to let anyone use a bed that is not on the same map they are, so the walk could never have worked even if it were safe. The same goes for owning or being assigned a bed on the other side of a gate. What does work is building beds over there, and that already works through the existing cross-gate construction: material is carried to the site and a builder crosses to finish it.

Full record: [rest and beds](docs/implementation/CONNECTED_REST_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.6.0-dev - 2026-09-29 - food crosses a gate, and nobody starves for want of a delivery

- Food is now carried through a gate to your people on the other side when there is nothing there they will eat. Ordinary hauling only ever moves things to better storage, so without this a colonist could starve beside an empty larder while the pantry at home was full.
- The last food never leaves a side that still has hungry people of its own. Moving starvation from one side of a gate to the other is not work.
- Only your own people and your guests are fed. A hungry animal or hostile on the far side attracts nothing.
- What anybody will actually eat stays entirely the game's decision, so ideology restrictions, royal titles, teetotalling and race diets are all respected without this mod having an opinion.
- Someone will also cross a gate to feed a patient who cannot feed themselves, but only once there is food on that side to feed them with. Sending a carer to an empty larder helps nobody.
- Treatment still beats meals: a patient who needs a doctor outranks a patient who needs feeding, and an urgent local patient outranks both.
- Food that arrives after the hunger has passed is simply put away rather than treated as a wasted trip, because food keeps.

One thing deliberately **not** added, and worth saying plainly: a hungry colonist will not walk through a gate to go and eat. Hunger is handled by the game at a level this mod does not reach into, and more importantly a gate can close while somebody is still on the far side. Sending a starving person on that walk risks stranding them with no food and no way back, which is worse than being hungry at home. Food goes to people instead. Full record: [food across a gate](docs/implementation/CONNECTED_FOOD_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.9-dev - 2026-09-28 - a doctor crosses a gate, and so does the medicine

- A doctor will now walk through a gate to treat a patient lying in a bed on the other side, instead of the patient being carried home first. Somebody already settled in a bed is better off treated where they are.
- Medicine is carried through a gate to a patient whose own side has none. The treating is the game's own; all this does is make sure there is something to treat them with.
- Medicine never decides whether somebody gets treated, only how well. The game treats patients with or without it, so a delivery that arrives late costs nothing.
- Your medical care settings are respected exactly. A patient set to no medicine has none carried for them, a patient set to herbal or worse never has glitterworld medicine hauled across a gate, and the amount carried is the amount the game says will heal them.
- Nothing crosses if the patient already has enough medicine they are allowed to use nearby, counting every kind they allow rather than just one.
- A local emergency always wins. A doctor only partway to a gate turns back for an urgent patient at home, and a doctor only ever crosses when there is no doctoring left to do on this side at all.
- An injured colonist wandering around does not pull a doctor through a gate; only somebody actually in a bed does.
- Works alongside your medical mods with nothing special needed for any of them, including the one that lets doctors carry medicine in their own inventory.

Surgery, patient feeding and prisoner or guest care are each a separate piece of work and are named as such rather than quietly assumed. Full record: [tending across a gate](docs/implementation/CONNECTED_TENDING_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.8-dev - 2026-09-28 - a researcher crosses a gate to work

- A researcher will now walk through a gate to use a research bench on the other side, when there is nothing to research on this side.
- The research itself is the game's own, on that side, at its normal speed. Nothing about how research works is changed or replaced.
- A researcher partway to a gate is not turned around by a bench freeing up at home, and nobody is ever dragged back. When the far bench stops being usable, or there is no project left to research, the colonist is simply free where it stands.
- A bench that is unpowered, or missing a facility it needs, is not treated as somewhere worth walking to.
- This works alongside your research mods without needing anything special for any of them. Because the mod only decides that the walk is worth it and then gets out of the way, whatever handles research on that side does the work — including mods that pick projects for you, reprioritise them, redraw the tree, or run a completely separate research system of their own.
- How eagerly researchers cross a gate is a setting like the rest, adjustable while the game runs.

Full record: [research across a gate](docs/implementation/CONNECTED_RESEARCH_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.7-dev - 2026-09-28 - ingredients reach a bill through a gate

- A workbench whose bill is short of leather can now be supplied from the other side of a gate. A colonist picks up the real leather, carries it through, and puts it where the bill can reach it.
- The crafting itself is untouched. Your colonist on that side finds the ingredients and runs the recipe with the game's own bill work, exactly as if the leather had always been there.
- Deliveries land inside the bill's own ingredient radius, measured the same way the game measures it. So if you have deliberately kept a bill's radius small, the goods arrive near that bench rather than in some far-off stockpile.
- Nothing crosses a gate if the ingredient is already within reach of the bench. A recipe that will accept two different materials also will not trigger a trip when one of them is already plentiful there.
- Half-finished work is never picked up or carried. The game binds a part-made item to the one colonist who started it, so nobody else can finish it; carrying one anywhere would strand it.
- The bill a delivery is for is remembered properly, so reordering your bill list mid-delivery does not redirect the goods to a different bill.
- Medical, mechanitor and autonomous bills are not supplied yet, and each is named as its own future piece of work rather than quietly skipped.

- The loaded mod version no longer has a long build identifier stuck on the end of it internally, which also means a given release of the mod now builds to a byte-identical file every time.

Full record: [bill ingredients](docs/implementation/CONNECTED_BILLS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.6-dev - 2026-09-28 - tune how eagerly colonists cross a gate, while the game runs

- You can now set how eagerly colonists cross a gate to work, for all four kinds of cross-gate errand, in the mod settings. Changes take effect the moment you close the window: no restart, no reload.
- Starting a trip is always kept below finishing one, and the settings screen tells you when it has done that. Otherwise a colonist standing on the far side holding something could be sent on a fresh errand instead of finishing the delivery.
- The shipped numbers stay the shipped numbers. Only values you actually change are saved, and there is a reset button.
- Checked the whole package against RimWorld and Steam requirements and wrote the position down with the evidence behind it: no game or expansion file is included, nothing of the base game is overwritten or deleted, no expansion is required, no third-party mod is required, and the mod targets official RimWorld and official expansions only. Those checks now run automatically on every build, so the position cannot quietly rot.
- Nothing in this project is waiting on anybody. Every item that can only be confirmed by playing is now marked as belonging to the single test pass that happens once the mod is finished, and none of them holds up any work.

Full record: [tunable priorities and the test phase](docs/implementation/TUNABLE_PRIORITIES_AND_TEST_PHASE.md) and the [compliance position](docs/COMPLIANCE_AND_OFFICIAL_VERSIONS.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.5-dev - 2026-09-28 - a builder crosses a gate to finish the job

- A frame on the other side of a gate that already has all its material can now be finished. A builder walks through and builds it. Nothing is carried, because nothing needs carrying — this is the other half of last build's material delivery.
- The building itself is entirely the game's own. Your colonist finishes the frame with the game's normal construction job, its normal reservation and its normal speed. All this mod does is decide that walking over there is worth it.
- A builder will not cross a gate while there is any construction work left on this side — not even smoothing a wall. Local work always comes first.
- A builder already on the way is not turned around by a frame that appears at home while it walks, so it does not get stuck oscillating at a doorway.
- Nobody is ever dragged home. When the work over there runs out, the colonist is simply free where it stands, with its own needs and whatever local work it finds, exactly like anyone else who walked through a gate.
- A colonist can only ever owe one cross-gate errand at a time. It cannot be promised a haul and a building job at once and then abandon one of them.
- Respects your work assignments as always: a colonist with construction switched off is never sent, and nothing here is ever a forced order.
- Operations lists people working across a gate separately from people carrying things across one, because reading the first as hauling would be misleading.

Also captured this build: the campaign opens in the 1990s, and the world's factions are the universe's own — the US government, rival corporations after proprietary technology, disgruntled ex-employees, high-tech thieves, corporate espionage and sabotage, and concerned citizens — default-set per scenario and tailored to each. They begin neutral and earn their hostility from what your company actually does. That layer is authored after the remaining cross-gate work families. Source and compiler evidence: [travel-to-work record](docs/implementation/CONNECTED_TRAVEL_TO_WORK_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.4-dev - 2026-09-28 - a gate you can actually work through, and a company you name

- A laboratory gate's first opening now lasts about thirty real minutes instead of about fourteen real seconds. The old value could not support a single round trip, which would have made every cross-gate work family unusable on a laboratory gate. Each research advance multiplies the duration, and at the top of the ladder a supported opening has no countdown at all.
- "No countdown" still means "while supported". Power, the operator on station and the energy supply are all checked every tick exactly as before, so running the supply dry ends the opening the same way cutting power does. A sustained draw needs real sustained generation behind it, not just batteries.
- Duration advances on *completed* research, never on spendable insight. Gating it on the currency would have meant spending research to advance shrank your gate.
- Natural gates are untouched and still permanently open, with no timer, operator, power or close command of any kind. Confirmed in the source rather than assumed.
- Every scenario researches the same tree and can build a full company, so nothing about duration or research is tied to which start you chose.
- You name your own company. A field at setup on every start, the name shown throughout Operations, and renaming any time through the game's own rename dialog. The old fixed identity survives only as a suggested default.

Two questions open since the earliest planning are now answered: the inside start has a configurable party, and its first exit lets the player choose the destination settlement rather than revealing a fixed one. Note one honest gap: only one company project exists so far, so the top of the duration ladder cannot be reached until the research tree lands. Source and compiler evidence: [gate duration and naming record](docs/implementation/GATE_DURATION_AND_COMPANY_NAMING.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.3-dev - 2026-09-28 - material reaches a build site through a gate, and the dependency position is audited

- A half-built structure stalled for want of steel can now be supplied from the other side of a gate. A colonist picks up the real material, carries it through, and puts it into the build site. Blueprints work as well as part-built frames, because the game's own delivery step turns a blueprint into a frame on the first material that arrives.
- Nothing about building is reimplemented. The site's own material requirement, the frame's own resource store and the work of building all stay the game's; only the carrying is ours.
- Audited what this mod actually requires and confirmed it needs nothing but the base game. Every game definition it uses was traced to base Core: no DLC, no Harmony, no other mod. The mod description now says so precisely instead of just claiming it.
- Fixed four places where a missing definition would have thrown an error at you instead of quietly reporting the action as unavailable. A definition can go missing because of another mod or a load-order clash, and that should never be a crash. There are now none of those left.
- Confirmed two compatibility claims are real rather than intended: stack-size mods are respected automatically because no stack size is ever hardcoded, and modded doors work as gate thresholds because doors are recognised by what they are rather than by name.
- Corrected a recorded blocker that was simply wrong: the gate's power draw was said to exceed every single generator in the game, while the same sentence named one that exceeds it. A draw is supplied by a power network in any case.

Recorded the method behind the above as binding: decide what to build a feature on by the capability it needs, never by a name. Because this mod adds behaviour to existing game objects rather than inventing objects, every piece of custom gear still awaiting replacement now has an existing-content answer, which unblocks that work on content grounds. See the [dependency and capability record](docs/implementation/DEPENDENCIES_AND_CAPABILITY_MATCHING.md) and the [construction record](docs/implementation/CONNECTED_CONSTRUCTION_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.2-dev - 2026-09-28 - our own people and our dead come home

- A colonist who goes down on the far side of a gate can now be fetched. Another of our people crosses, picks them up, carries them back and puts them in a bed. If no bed is free on arrival they are set down on this side and ordinary rescue takes over from there, because being home is what the trip was for.
- Our dead come back too, to a grave or to storage. This needed no new machinery: the game already treats carrying a corpse as ordinary hauling, and a grave is reached the same way any other container is.
- Fixed a real gap that would have made that silently not work: the planner only looked for open floor space, and a grave is not floor space. A corpse whose only home was a grave would never have been planned for, and the container delivery route added last build would have sat unreachable for exactly the case it was built for.
- Capture stays a player order, not automatic work, which is both how the game does it and what the gate rule says: people and monstrosities come back because you directed it.

This is the casualties-and-remains work family, built ahead of construction because carrying people back through an opening is something the gate rule names explicitly and no route reached it at all. Tending someone across a gate is a different capability and is not implemented. Source and compiler evidence: [casualties record](docs/implementation/CONNECTED_CASUALTIES_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.1-dev - 2026-09-28 - nine deferments closed, and doorways that lead onward

- Doorways deeper in can now be found. One of our own people walks up to a doorway in the Backrooms, studies it, and records that it leads somewhere else: a permanently open way through to a further space. A doorway's answer comes from its own position under that space's saved seed, so it is always the same answer and revisiting never rerolls it. At most two ways onward per space, so a chain of spaces stays finite.
- Storage containers are now valid delivery destinations for cross-gate hauling, not just open stockpile cells. This follows the game's own rule for which destinations take which route, which is also what makes the storage-framework mods work here without special handling for each one.
- A worker no longer plans a trip whose arrival its allowed area forbids. The game offers no way to ask about a zone on a map a pawn is not standing on, so instead we write down what we saw while we were standing there, and an unseen map is treated as unrestricted exactly as the game itself treats it. A destination that turns someone away is left alone for a while afterwards.
- Finished crossing records are now bounded. Automatic hauling made these an everyday event rather than a rare order, so they would otherwise have grown in the save forever. Unresolved records are never touched, because those hold real people and real cargo.
- Fixed four pieces of missing text that would have shown the player a raw internal name, including the Procurement tab label.
- Internal: one implementation each for branch map ownership and for choosing a threshold's approach cell, instead of two and three.

Nine deferred items closed, seven of which turned out to be blocked on nothing and three of which had already shipped and were still listed as outstanding. The deferment register now carries the four audit questions that caught them, so it gets checked rather than only added to. Source and compiler evidence: [audit and closures record](docs/implementation/DEFERMENT_AUDIT_AND_CLOSURES.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.0-dev - 2026-09-28 - colonists work across a gate

- Added cross-gate work as ordinary work. A colonist can now haul an actual object from the map that holds it, carry it through a gate in real hands under native mass and stack limits, and put it into storage the other side's own settings accept. Both directions. No dispatch, no crew list, no cargo manifest.
- Added the saved work intent that makes a trip survive its job boundaries, a save and a reload: it remembers the worker, the one real object, the destination, and the gate the plan was made against. The next physical step is always worked out from the worker's actual current position, so an interruption or an unexpected location resolves by itself.
- Added the planning lease, which stops two of our own planners promising the same stack and does nothing else. It is not a reservation, it excludes nobody, and it expires.
- Work reaches people through ordinary work priorities, within-type order, schedules, disabled work types and required capacities, because it is an ordinary work giver rather than something that pushes errands. Hunger, sleep, danger, drafting and mental states keep winning. Nothing is ever marked as a forced player order.
- Nothing is counted, cloned, teleported or consumed at a distance. The object that arrives is the object that left, or the honest split of a stack that a partial pickup produced. A delivery that merges into an existing stack is a finished delivery, not a lost item.
- Added a list of the work trips currently crossing a gate, because saved state that moves people and goods must never be invisible.

Storage hauling is the first of the work families and the only one in this version. Construction, bills, research, medical care, food and rest are specified with named owner steps in the [deferment register](docs/DEFERRED.md) and are not claimed here. Also recorded permanently in the [pinned Core API reference](docs/implementation/CONNECTED_WORK_CORE_API.md): RimWorld 1.6 does ship its own map-portal system, and it cannot serve this design, because its hauling does nothing without a player-filled loading manifest and its crossing drops carried cargo on arrival. Source and compiler evidence: [connected-work record](docs/implementation/CONNECTED_WORK_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.4.3-dev — 2026-09-28 — inhabitants stay in the Backrooms

- Added the rule that people and monstrosities on the far side do not cross a gate. Nothing but this company's own people walks through, an open gate is never an objective, lure, spawn target, raid route or attack trigger, and no setting, research or upgrade changes that.
- Everything else comes back because one of our own people carried it: materials, tools, equipment, resources, minified furniture and production benches, corpses, and people or monstrosities that are genuinely downed, dead or held prisoner. Anyone still on their own feet cannot be taken through.
- One chokepoint enforces it for every gate at once, so no future work adapter, scheduler, generator or threat can reintroduce the behaviour by accident.
- Added player-facing text for each refusal.

Gate, machine door and portal mean the same thing; every start can eventually run several gates, and nothing assumes one gate per branch, map or coordinate. The gradual-escalation half of the same rule — how much pressure a space presents and how it grows — is specified but not yet implemented; it is owned by the procedural-inhabitants work in the [deferment register](docs/DEFERRED.md). Source and compiler evidence: [connected-travel record](docs/implementation/CONNECTED_TRAVEL_IMPLEMENTATION.md). No gameplay result is claimed.

## 0.4.2-dev — 2026-09-28 — remembered portal addresses and ordinary crossing

- Added explicit portal addresses: a designated native gate can remember a laboratory connection to a saved coordinate, and any actual doorway can hold a permanently open natural connection. Addresses are derived from the branch, coordinate and threshold object, so remembering the same address twice changes nothing.
- Added an explicit repair for sites generated before their return threshold was an actual door. It replaces that one object with a Core door under a saved receipt and keeps the site's map, room graph, construction, recovered items and discoveries.
- Added a deterministic record for newly discovered coordinates so an address can never invent a coordinate identity or seed. Visited coordinates are never removed to make room.
- Added ordinary crossing: order one colonist and they walk to the saved threshold and cross carrying what they already carry. No crew list, manifest or dispatch. Opening a doorway normally still moves nobody.
- Added laboratory session controls, a reconcile action for every unresolved crossing, and an emergency-return route that pays the physical recovery cost once and teleports nobody.
- Added player-facing text for every portal address, travel and crossing result.

Source and compiler evidence is in the [connected-travel record](docs/implementation/CONNECTED_TRAVEL_IMPLEMENTATION.md). Cross-map work, materials, hauling, bills, research and needs are not implemented by this version; they remain the next steps in the [deferment register](docs/DEFERRED.md). No gameplay, save-migration or compatibility result is claimed.

## 0.3.0-dev — 2026-09-28 — company operations and content reuse

- Added voluntary native-pawn applicants, inspection, hiring, recovery, staff role assignments and payroll registration. Offers retain the original pawn through interrupted arrivals; unavailable offers have an explicit safe dismissal route.
- Added quoted procurement of existing Core goods, saved physical cargo, ledger-backed payment/refund records, receiving stockpiles, partial deliveries, redirection and bounded history.
- Added an HQ Facilities pane for actual buildings, rooms, power, bed ownership and staff care needs, with native inspection and assignment routes.
- Moved company laboratory work to an explicitly designated native research bench. New field evidence uses a real Core TextBook, with saved creation/custody records and retry of the same original object.
- Replaced the four custom gameplay audio files with references to existing Core sounds. Preserved old files outside the loadable package as historical evidence.
- Added two original painted Backrooms menu images, a quiet slideshow, reduced-motion/disable settings and the exact mod title/current build version beside native top-left version information.
- Recorded the owner's existing-content-only rule throughout the build documents and mapped the remaining older custom content for replacement.

This is an implementation checkpoint toward the full mod TODO. The [company build record](docs/implementation/PHASE_3_BUILD_RECORD.md) owns compiler/package evidence and limitations. Custom gameplay content from 0.2.0 still awaits replacement; gameplay, balance, save migration, optional integrations and release acceptance remain open.

## 0.2.0 — 2026-09-28 — first-expedition development slice

- Added the Async Industries facility start, five staff, physical supplies and one-time branch funding.
- Added the USD ledger, wages/overhead, arrears, initial survey contract, case/evidence records and company projects.
- Added physical machine assembly, staffed calibration/operation, power reserve, warnings and recovery openings.
- Added a saved finite first destination, real inventory/crew transfer, recall, relief/casualty recovery, abandonment history and auditable cargo declarations.
- Added deployable numbered tags/beacon, corridor mismatch, bounded Quiet Pursuer, physical evidence analysis, once-only settlement and insight-gated Gate Telemetry.
- Added actionable Operations panes, next objectives and original equipment/encounter sprites with provenance and source masters.
- Added bounded layout candidates/fallback, furnished room families, fog-preserving native doors, observed clues, physical salvage, original carpet and native wall paint.
- Added frozen evidence reports, explicit AI-01 resurvey preparation, persistent gate warnings and development identity/performance logging.
- Added four original quiet audio cues with native game/master volume, independent gate/field mute and a mod volume control.

The [build record](docs/implementation/PHASE_2_BUILD_RECORD.md) records exact implementation, source and evidence boundaries. Gate 2, runtime/presentation acceptance, full campaign systems, optional integrations, co-op and release remain in progress. This is a private development checkpoint.

## 0.1.0 — 2026-09-28 — private foundation

- Added the Core-referenced C# library, logging entry point and inactive save-local campaign component with explicit schema version.
- Added the localized Operations main tab, with foundation status and guarded links to native Work and Research tabs.
- Added exact mod identity, original package preview and the separate copyable 1.6 package.
- Added pinned build references, locked dependency restore, package manifests and scoped RimSort Local Mods staging with backups.
- Added contributor/build/migration guidance, production asset specifications and implementation evidence linked to the existing design contracts.

The company scenario, economy, machine gate, expeditions, generation, analysis, threats, main-menu slideshow and optional integrations are not implemented in this version. Compilation and package/staging evidence do not establish in-game behavior or profile compatibility. No public release or save-support promise is made.

## Preparation — 2026-09-28

Gate 0 documentation/source preparation completed, including owner decisions, 294-mod source review, design contracts, feature traceability, source registers and future acceptance plans. See the [closure audit](docs/research/GATE_0_COMPLETION_AUDIT.md).
