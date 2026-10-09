# TEST — the post-completion test phase

**Tier 4 of 4, and the only tier whose rows a build cannot close.** Almost every row needs the game
running, and **only the owner launches RimWorld, through RimSort**.

**Two rows were confirmed by reading rather than by launching** and are closed — *"All four get [T]
rows"*, 2026-10-06, and two of those four needed no game. The file's premise is *a build cannot
close this* rather than *a launch is the only way*, and those two could not be closed by a build
either.

## ⛔ THE OWNER DOES NOT READ THIS LIST ⛔

**Owner direction, 2026-10-06, verbatim:** *"you are gooing toi monitor the rimbridge and do the work
of checking off whats comes and passes as i cant read 100 tasks then game them out and tell you to
check em constantly"*

So the owner plays and reports nothing. `.local/qa/test-watch.py` attaches to the live game through
RimBridge, journals every letter, message, alert and warning with a timestamp and a game tick, and
survives the game restarting. Evidence is matched to these rows and recorded on them without the
owner being asked what happened.

**What that cannot do is judge.** A row about whether the art *looks* right, whether text is
readable at a given UI scale, or whether the economy *feels* balanced needs a human eye, and the
bridge has none. Those rows say so, and they wait for a sentence from the owner rather than being
closed on a letter that happened to arrive.

**Owner direction, 2026-10-06, verbatim:** *"we should make a seperate todo=Test.md and move all
test items to it to be done and clear todo , if its true all items are done."*

It was true of [`TODO.md`](TODO.md): zero open, zero partial, and every remaining row `[T]`. So the
whole body moved here unchanged and that file went back to its template state.

| Ledger | Grain |
|--------|-------|
| [`ROADMAP.md`](ROADMAP.md) | MAJOR — phases and milestones |
| [`TODO.md`](TODO.md) | MINOR — the working queue, **open buildable work only** |
| [`DECOMPOSED.md`](DECOMPOSED.md) | smallest execution units, open only |
| **`TEST.md`** (this file) | **the test phase — `[T]` only, 74 rows, and a build closes none of them** |
| [`FINALIZED.md`](FINALIZED.md) | permanent archive, append-only |

Status markers here are `[T]` and nothing else. A row that turns out to be buildable after all goes
**back to `TODO.md`** as `[ ]`; it is not quietly built from here, because this file's whole meaning
is *waiting on a launch*.

**LAW #0 still binds every row:** the owner's verbatim words are preserved exactly as they were in
`TODO.md`. Nothing was reworded on the way across.

**Closing a row needs evidence from a running game** — a letter, a log line, a save that reloads —
recorded on the row, and then the row moves to `FINALIZED.md` by the usual archive ceremony.

**Read a launch log in this order:** `Player.log`, grep the **first** `[Rimrooms]` line, then
`python .local/qa/bridge.py call rimworld/list_letters '{}'`.

---

## In progress

### Owner direction — play the QA colony top to bottom, as a player would (2026-10-07)

**Verbatim owner direction (2026-10-07):** *"okay do you know how to explore the rooms of the facility and get outside and start collecting resources planting crops and setting bills for food and then get your freezer storages set up so that noraml non needing frozen goods arent in the freezer and things like ambrosia, wort, food, healroot are in the freezer and start seting up the gate i mena u wrote this mod you should know how to play it top to bottom"*

**And, the same hour:** *"set everyone to attack not flee and group up when something attacks and draft and flee attack never letting someone melle person or animal get close to your pawns kill them with range at all costs, expand the base build prisons and more facilities , maintain and watch your resources, research and manage your pawns , set theri scheldule to anything at all times for all pawns, ect ect all aspects of the game are to be taken in"*

**And on how a test colony is set up, verbatim (2026-10-07):** *"there is no wood no trees on this map, thats why in advanced setting on world gen setup you set 300x300 mapo and spring, and then when choosing a map tile u pic on that has mountains(the rock areas on map) in forest area and jungle areas the light green and green, terrain tab on left tells u all this when u highlight via select the tiles"* — the first QA colony sat on a flat treeless tile from *Select random site*, and every colony after it is rolled this way: 300×300, Spring, mountains, forest or jungle, read off the Terrain pane before Next.

**And a correction while watching the colony, verbatim (2026-10-07):** *"saw an error, u tried mining an area that was unexplored yet and when u went to mine it it went through door and it explored, then half a fucking mountain was set to mine out so i had to cancle it as pawns would of died trying to mine so much"* — an 840-cell Mine order laid on fogged rock east of the compound. **A designation is only laid on cells that have been read first, and a mine order is a seam or a room, never a block.** The owner cancelled it by hand; the orders that follow are sized to what three people can finish.

**And the full brief, verbatim (2026-10-07):** *"come one do stuff.. play the game... grow resources, maintain ur colonists' needs start buisnesss build prison build guest questers, do it all start growing cash cropsa research what u need to unlock better things u can produce, defend your base, accept neew employees hire them i think id, work towrds starting up the gate and get in to the back rooms, do quests and missions increase ur cash build a vault oraganize ur shelfs. cash silver gold high valuable gemms irvory in vaults, meds in hospital lab upgrade get prisoners working keep then contained use locks to allow them to enter work areas with exterial walls and defences containing them , layers of security, embracures near boarders as rooms to shoot frioom to where u head to the closest defences bewteen ur base and the enmies do ranged first and retrating/firing so mele guys cant get to close, and u have to pause at the right times as not to wit to long to give commands in combat situations"*

**The colony is `rimbridge_save_20261007_105853.rws` and its successors:** Async Industries on the owner's own flow — Preset3 through Prepare Carefully, the Godsmultiplayer ideoligion — three staff, Gee, Scar and Unity. Every order below goes through the bridge; every result is read back from the map, the log or a save, never assumed.

- [T] **"collecting resources planting crops and setting bills for food"** — a growing zone outside, a cook bill, wood and stone coming in. **PART DONE 2026-10-07:** two growing zones laid outside the east wall, **396 cells on soil the crew had actually walked**, and an **electric stove** built in the mess on the new conduit run. **Open:** the cook bill itself, and chopping, which the flat first tile had nothing to chop on. -- **MORE 2026-10-07, after the owner's *"u need to make meals sooner than later"* and *"how u plan on cutting up them animals?"*.** The stove refused to cook with *"Missing 0.5x raw food"*: the rice was still growing and there was no butcher table anywhere. Now: the stove's simple-meal bill is **Do until you have X at 50**, a **wooden butcher table** stands in the kitchen at (151,140) with **Butcher creature on Forever**, seventeen wild berry and ambrosia plants within reach are marked to harvest, and fourteen animals are marked to hunt -- deer, alpaca, ibex, raccoon, turkey, hare; the muffalo herd and a boomrat were left alone. **Hunting needed guns**: *"No hunter has a valid hunting weapon"* until three charge rifles from the security room went to Gee, Scar and Unity. Six corpses were hauled and butchering started. **Open:** chopping. -- **MORE 2026-10-07, and the cash crop the owner kept asking for.** A second growing zone of 122 cells south of the rice, set to **Smokeleaf** (*"Plant: Smokeleaf plant"* on the zone); the plant list also offers healroot, psychoid, hops and tinctoria for the next field. Three more wood-fired generators were built and all seven refuelled to 57–75. **Open:** chopping.
- [T] **"set everyone to attack not flee and group up when something attacks and draft and flee attack never letting someone melle person or animal get close to your pawns kill them with range at all costs"** — the hostile-response setting on every pawn, and the drill when something comes. **THE SETTING IS DONE 2026-10-07 and confirmed by the game's own tooltip:** *"Change how this person will react to nearby enemies when not drafted. Current mode: Attack"* on all three, where all three read **Flee** before. **Open:** the drill itself, which needs something hostile to arrive. -- **DRILL RUN TWICE 2026-10-08 (Crashlanded city colony, Marble Hollow), and neither was clean.** *Shamblers approach* (4): all three drafted, advanced to ~20 cells and stood to fire -- three dropped at range with headshots, but the crew first **kited while moving** (moving pawns do not fire) and one shambler closed on **Scar**: bites, cracks, *"Bleeding: 184%/d (death in 12 hours)"*; undrafted to bed and tended to *"no immediate danger"*. *Raid: Choke Toxers* (1 waster, club): Gee and Unity held the hall, but **Unity was unarmed** (the earlier bridge equip had not taken) and **all three were back on Flee** -- this colony was new and the setting had never been made here. Waster *Mitch* killed in the storehouse; Unity took three cracked bones. **Fixed in play:** all three set to **Attack** (fist icon read back on each), charge rifle + steel-knife sidearm on each. *Mad gazelle* (same day): all three armed and on Attack, drafted at once; Unity was 1 cell from it when the letter landed and killed it point-blank, but took a bite and two bruises first (bleeding 8.2%/d, no danger). Closer, still not clean. *Mad guinea pigs* (8, same day, 8 colonists): rifles drafted to a line north of the field and the first pig died at range (Gee), but two came round the east side; the line was **re-ordered across the whole base and still walking** when they arrived, and Unity took a bite and two scratches before both were shot at (168,78)/(173,78) (bleeding 37%/d, no danger; nobody downed). Lesson: hold one firing position and let them come -- never re-position through the base under attack. *Mad doe* (same day): landed on Alfonzoid and Stee at the throne-hall site; all nearby drafted at once, Steve (11) sent to the hall, Unity and Gee to positions; the doe was down within seconds and finished off -- **no medical alert, nobody touched**. First clean run; the row closes on a clean run against a raid. **Still open:** a drill run where nobody is touched -- range held, standing fire, every pawn armed and on Attack before the letter. *Raid: Hachthsonss Runship* (3 imps, 2026-10-08, 10 colonists): before they moved, every pawn's weapon was read off the autosave (4 guns; a machine pistol and a revolver from the prison stock equipped on Rev and Steeve -> 6 guns; Alfonzoid, Stee and two Steves unarmed or melee, all on Attack). The imps then crossed **~120 cells in one 6-second Superfast slice** and were in the hospital before anyone was placed. The six guns were drafted and sent to **one standing line** at the east end of the corridor south of the hospital (132-134, 111-114), the unarmed drafted and walked east out of it; all three imps went down at range (Roznath, Ltzrov, Cazich). **Not clean:** **Steeve and a Steve were wounded** (*Medical treatment needed*, tended at once), and the imps' fire set the hospital alight (20 burning cells, out within the minute by ordinary firefighting). Capture was refused -- no free prisoner bed. **Lessons:** with imps the line has to be **standing before they move** -- draft and place at the raid letter, not when they come; keep one prisoner bed free so downed raiders can be taken. *Psychic pulse: mad quails* (5, same day): four circled outside the west wall, one came in from the north-east and was killed inside; the four got **Hunt** orders so hunters engaged from weapon range instead of walking a line out through a door; all five dead in about two in-game hours. One Steve shows *Medical treatment needed* afterwards -- **not separable from his imp-raid wounds**, so not counted clean. Mad animals, not a raid: the row still closes only on a clean run against a raid. *Manhunter pack: 7 crows (scaria)* (same day): `play.py` now reads manhunter, mad-animal and psychic-pulse letters and puts **Hunt** on every animal of that kind; all seven died to hunters' fire within about two in-game hours, colonists otherwise inside. *Revenge wargs* (2): the first caught **Scar, hunting with her knife equipped** (rifle in her inventory) -- she held it in melee until four guns arrived and downed it; the second was answered by pulling the fence crew inside and manning the south bastion's embrasures, and it never closed. **Not clean:** Scar wounded by the warg, Steeve shows *Medical treatment needed* after the crows. Lesson: a hunter must hold a **gun** in hand, never a sidearm knife. *Raid: Horax cultists* (2, Anomaly, winter, same colony): five guns marched as one group to a standing line ~20 cells from the ritual site (x220-224, z49-51) and fired from there; **Pyrrha killed at range**, but **Elk charged the line** and closed to melee before she went down, wounding **two Steves** (*Medical treatment needed*). Not clean. Lesson: against chargers, the line stands **further back** (30+) or behind cover, and every pawn on it holds a gun -- the melee-armed stay home. *Raid: Kolku yttakin* (4 with pack animals, winter, 10 colonists, 8 guns): the line of eight was drafted and standing at the raid letter (x86-87, z118-125) while the raiders were still preparing ~60 cells west; when they had not moved after a long wait the line advanced as one to x52-53 and **stood** there. The raiders charged; **Oyytt and Orytt downed at range** at (58,109) and (65,114), the other two fled. **Not clean:** blood of **Gee and Rev** at the line afterwards (a raider, Hysyon, reached it). Lesson: a line that walks toward a raid gives them the closing distance -- stand still and let them come the whole way. *Raid: Horax cultists* (2, spring, ritual in the south-west corner at (16,1)/(27,3)): every gun drafted at the letter and sent as one line to x45-46, z14-21, ~20 cells off; two pawns' first move orders did not take and were re-issued. The cultists **left the map before contact** -- no shot fired, nobody hurt. Not counted: no engagement.
- [T] **"expand the base build prisons and more facilities , maintain and watch your resources, research and manage your pawns , set theri scheldule to anything at all times for all pawns"** — a research project queued, every pawn's schedule on Anything, a prison, and the base growing. **PART DONE 2026-10-07:** every hour of every pawn's schedule painted **Anything**, and research is running — **Prisoner containment finished** and *"Gee Fourteen has started a new research: Crude torture methods"*. A conduit spine now reaches the batteries, the console, the machining table, the gate hall, the coolers and the mess. **Open:** the prison itself, and further building. -- **MORE 2026-10-07.** Three wood-fired generators (seven total, +3.9 kW with the gate closed); a **records desk** at `(149, 132)`, where the first research write-up was filed (*"Choose a direction — 1 of 1 filed"*); a **hospital** -- the two beds in the north room switched to *Medical* and its shelf set to medicine and glitterworld medicine only; **a prison cell started** -- two beds framed in the west storeroom at `(132, 155)` and `(135, 155)`. **Open:** the cell beds finished and set for prisoners, then the first prisoner. **PRISON GOING 2026-10-08 (Store colony):** Prisoner containment researched; a prison cell set up in the old gate chamber `(166-172,170-175)`, bed *For prisoners*; **Lenka** (34, town councilman, crashed POW) captured by Scar and jailed, interaction **Recruit**, *Force to work* on (Prison Labor). Facilities added this run: gate complex, drug lab, electric smelter, assembly shop, 2nd trade beacon, 4 generators. Still open: layers of locks, prisoner work areas. **CITY COLONY 2026-10-08 (Marble Hollow, Crashlanded + founded branch):** two marble cells built (`x171-183, z102-108`), bed set *For prisoners* (Hospitality hides it under the *For colonists* gizmo); *Raid: Choke Toxers* beaten with nobody downed and waster **Reaper (minstrel)** shot down, captured by Scar, carried to the cell and tended (*"Gunshot (charge rifle) tended"*); Prisoners tab interaction set **Recruit** (read back), legcuffs/handcuffs/intel ticked, Prison Labor work row present.

### Owner direction — storage, cash crops and ambition (2026-10-07)

**Verbatim:** *"you still havent started growing cash crops and you still havent figured out you freezer storage as ive already told you how , you have shelfs outside the freezer set to hold freezer goods and good in the freezer not ment to be frozen, i already told you how to set up the shelves and zones, do it"*

**Verbatim:** *"all shelves in and out of the freezer need to be correct"*

**Verbatim:** *"make sure all shelves outside are set correct too. like medicine only in the room with hospital beds but heal root under mediceine needs to be in freezewr"*

**Verbatim:** *"and all shelves outside the freezer need to be set to not accept freezer goods"*

**Verbatim:** *"u can set one and use copy button to paste it to other shelves with paste"*

**Verbatim:** *"you need to be eutropanuer like and have a will to expand, learn , explore, and buiold, and capture prisoners and rule the world. have you even looked at the world yet?"*

- [T] **"start growing cash crops"** — **SOWN 2026-10-07, 122 cells of Smokeleaf.** Closes when the first harvest is sold.
- [T] **"have you even looked at the world yet?"** — **LOOKED 2026-10-07.** Within a few tiles: Cuvin Flamehome outposts with **1** and **2** enemies, a Yowoo Fur outpost with 2, a hostile Yowoo Fur settlement (−100), and the active quest *Hidden Mechanitor Lair*. **Plan:** finish the prison, then raid the one-man Cuvin outpost with three rifles and bring the defender home as the first prisoner.

### Owner direction — global control (2026-10-07)

**Verbatim:** *"keep going and wtf.. your selvels have none set to hold your resources, you always have to have all resources on shelves, and why are you not expanding where are your private rooms who is your leader role that you need to set and do all the ideology stuff start making u ideology statues, party room and throne rooms and landing pads and evertyhting in the game, you are doing to little, you need to expand you thinking.. do you know what global control means and what that entails in what you have to do, marry have kids, raise them protect them, hire empoloyees, save them heal them feed them upgrade them arm them defense items them"*

**Verbatim:** *"cant have kids until u privet rooms with double beds, one guy can knock up[ many"* -- *"read now.md to continue : cant have kids until u build privet rooms with double beds and set them to sleep there. can swap em in and out till all, one guy can knock up[ many"*

**Verbatim:** *"kids need milk and cribs and toys"*

**Verbatim:** *"have to trade, make a corral for cows and such, buy cows, get a silver supply like cash"*

**Verbatim:** *"be greedy u want welath and power while making all factions you can your allies by send gifts with drop pods"*

**Verbatim:** *"and make sure you equipe stun batons pain sticks in off hand as side weapons for close range"*

**Verbatim:** *"you are suppose tho be checking off todo items of the tests stuff while playing the full game to do so, you havent even started other scenrios yet but i guess yuou are following the test todo work as needed right?"*

- [T] **"you always have to have all resources on shelves"** -- a shelf for every resource, one priority above the floor zone.
- [T] **"private rooms" / "privet rooms with double beds and set them to sleep there"** -- **FOUND 2026-10-07: Gee, Scar and Unity are all *age 14*** (pawn pane: *"Male, age 14"*, *"Female, age 14"* twice). The mod sets no ages (grep of `src/` for `ageTracker` finds only the Personnel age label), so this is the colony as created. At 14 vanilla allows no romance and fertility is near zero, so **children need an adult hire**. Ground south of the base wall (`x 128-158, z 117-127`) read as soil, gravel and rough limestone with grass, a few trees and chunks -- buildable. Six 4x4 wood rooms with a double bed each were blueprinted there along the base's south wall (`x 142-172, z 123-127`, doors facing out). **The owner, verbatim: *"cancle that contruction"*** -- the owner cancelled it by hand; a read-back finds no blueprint left in the rect. Asked why, the owner answered **"1-3"** -- wrong place, wrong material (wood), wrong order (ritual spot and leader first) -- and, verbatim: *"you have to continue halls and shit u cnat just attach rooms to a fucking straightr  other room u need appropriate pathing"*. Then, verbatim: *"dont forget cros paths dont want mile long corridors and need vents and lights and furnature for beds"*, *"and u can move walls and furnature wher u want it facing direction u want"*, *"think uniformity"*. **THE WING, BLUEPRINTED 2026-10-07 in limestone** (`terrain-map.py 147 104 165 129` shows it): the base's own x156 hall continues south through a limestone door at `(156,128)`; a **cross hall at z115** runs x150-162 with limestone doors out at `(149,115)` and `(163,115)`; **four identical 5x5 bedrooms** (x150-154 / x158-162, z117-121 / z123-127), each with a double bed head-north at the same offset, an end table at its head, a dresser on the south wall, a standing lamp in the south-west corner and a door onto the hall at its middle row; a **nursery** (two cribs, a toy box, a baby decoration, a lamp) and a **guest room** (four beds, a lamp) on the south row; **vents** through the hall wall at z124/z118 for every bedroom; hidden conduit from the base's x156 line down the hall and along z123, z117 and z106 to every lamp. The walls already rising were read back as *"Limestone wall (blueprint)"*. **Open:** the build itself; the east bedroom vent at `(157,124)` once that built wall cell is deconstructed; guest beds toggled for guests; pawns assigned to the double beds. **STORE COLONY 2026-10-08:** Scar and Gee became lovers (letter *New lovers*); a private room in the gate complex `(147-152,190-195)` got a **double bed**, both assigned (the Mint assign menu re-sorts after each click -- read it back before the next). Lenka (34) is the first adult, a prisoner on Recruit.
- [T] **"who is your leader role that you need to set"** / **"now u have a leader u need a morasl guide and they ahave abilities u want to always use"** -- **BOTH FILLED 2026-10-07.** *Assign role...* first refused: *"No reachable altar, ideogram or ritual spot"*, so a **ritual spot** went down at `(158, 147)` in the control room. Then two role-change ceremonies: *"Gee now holds the role of God Almighty"* and *"Unity now holds the role of Lord"* (100% quality each, 2 of 1 spectators). Abilities read off the gizmos -- Gee: *Leader speech, Trial, Work drive, Combat command*; Unity: *Convert, Keep Converting, Reassure, Counsel, Preach health*. First **Leader speech** given at once: *"Uninspiring leader speech"*, total quality 51% (Gee's social impact 101%, room impressiveness 42.9/120, 2 of 10 participants). **Open:** the abilities used on every cooldown as a standing habit; a more impressive ritual room. **Marble Hollow, 2026-10-08:** roles filled (Gee leader *God Almighty*, Unity moral guide); a **grand altar** (3x3, Altar_Grand) built in the altar room west of the throne hall. Gee's **Leader speech** (gizmo on Gee -> *Dialog_BeginRitual* -> Begin; it chose the grand altar) read back *"Encouraging leader speech ... total quality was 68%"* -- social impact +30%, 9/10 participants +38%, **room impressiveness 0/120** (the altar room's walls not yet up). Up from the first speech's 51% *Uninspiring*. Still open: room impressiveness (enclose and furnish the altar room) and the abilities used on cooldown as a habit.
- [T] **"start making u ideology statues, party room and throne rooms and landing pads"** -- the ideoligion asks for *The Galaxy*, *The Universe*, *The Man*, *The Solar System*, an *Open Platform* and *Pew* seats.
- [T] **"red faces outside blue inside, fix themn" -- the freezer's coolers, and the start that put them in sideways.** The four freezer coolers in the compound's east wall were authored `<rotation>0</rotation>` in `RR_AsyncIndustriesStart`. Decompiled `Building_Cooler.TickRare` cools `South.RotatedBy(Rotation)` and heats `North.RotatedBy(Rotation)`, and does nothing unless both are passable, so at rotation 0 in an east wall **both sides ran into a wall cell or the next cooler: the freezer never froze**, which is why food rotted. **FIXED IN THE DEF** -- rotation 1 (East: blue west into the freezer, red east outside) -- and `tools/check-start-layout.py` now fails any cooler with a side in a wall or its blue side outside; run against the old def it reports all four, against the new one it passes. **FIXED IN THE COLONY:** the four deconstructed and rebuilt facing East (placement ghost read: blue cell inside, red cell outside, outline green), target set to **16 F** each. **Built and staged** (0.13.0-dev, 200 files hash-checked; checkers 32 of 33, the stale plant anchors as before). **Open:** a freezer temperature read once it has run.
- [T] **"hire empoloyees"** -- **REQUESTED 2026-10-07:** Operations -> Personnel -> *Request applicants*: *"Pending applicant -- candidate requested"*, *"One-time onboarding: $100,000 USD. Daily wage: $5,000 USD"*. Next request window *Day 24*. Closes when an applicant is hired and on the map. **REQUESTED AGAIN 2026-10-08 on Marble Hollow** (the branch founded on a Crashlanded colony, staff of 3 -- Gee, Scar, Unity -- because only the founders were colonists when it was founded): Operations -> Personnel -> scrolled to *Voluntary applicants* -> *Request applicants*: *"Pending applicant -- candidate requested"* x3, *"One-time onboarding: $100,000 USD. Daily wage: $5,000 USD"*, next request *Day 43*. Closes when one is hired and on the map.

- [T] **Company deliveries land while shelves outrank the receiving stockpile.** Found in play 2026-10-08 (Marble Hollow): steel and components paid for through Procurement waited as *AwaitingReceivingSpace* / `RR_Proc_ReceivingStockpileNotPreferred` because the shelves outranked *Stockpile zone 1*. Worked around in play by setting the zone to **Critical** (steel x3 stacks, components and medicine landed at once). **Fixed in source** (the preferred-target gate removed; 0.13.0-dev builds clean) -- **not yet staged**: the game was running. Closes when the staged build delivers an order with the receiving zone back at **Normal** and the shelves still preferred.
- [T] **"someone wants to trade.. see if u can get tech and shit and use it if needed plan ahead, be greedy dont buy shit you dont need"** / **"use comms console to call trade hub to trade or call a ship to land or trade with trades via pawns dirrectly"** -- **FIRST TRADE DONE 2026-10-07** with *Tail, exotic goods trader (Welpog Concord)*, a caravan south of the wall; found by right-clicking each caravan pawn with Gee selected until one offered *"Trade with Tail, exotic goods trader"*. Bought **plasteel x145, advanced components x2, glitterworld medicine x3**, paid with **2 of our 10 age-reversing mech serums**, and took **906 of the trader's 948 silver** on top. Read back: *"Relations with Welpog Concord have changed from 0 to 5 (traded)"*, *"Gee has gained 7688 social experience from this trade"*. Passed over: genepacks, airship / ox-carryall techprints, serums, car parts. **A MISTAKE, owner, verbatim:** *"okay but you sold whit that was very high tech thats will keep ur colonists from dying from old age and u cant get more...... u need cash crops to sell to bulk goods traders and refine them into better products u need research to make money(silver) or order it from company"* -- the serums were irreplaceable; the remaining 8 are kept, and trades are paid from cash crops, refined goods or company-ordered silver from here on. **THE COMMS CONSOLE ROUTE, DONE 2026-10-07:** Gee right-clicked the comms console at `(151-153, 152-153)` -> *"Call Arnprior Import Company of Space Syndicate (combat supplier)"*; the trade window opened with the ship's 6,407 silver. Bought **stun batons x3 for 483 silver** -- the owner's named sidearm -- and nothing else: its guns are worse than our charge rifles and its armour is awful-quality or a lone legendary flak pants at 1,366. The company record books it offered to buy are job paperwork and were not sold. The batons came down by pod at `(145-146, 157-159)` and all three were taken *"Equip stun baton as sidearm"*; none left on the ground. **Open:** a cash-crop-to-product chain.
- [T] **Visitors can be recruited.** Every visiting pawn's menu offers *"Invite {name} to stay (No guest beds)"* (Hospitality) -- guest beds are the way to take on adult employees, and with them the children route. **Open:** a guest room with guest beds. -- **GUEST ROOMS BUILT 2026-10-08 (Marble Hollow, Crashlanded + founded branch):** three single marble rooms on a 3-wide hall (`x111-129, z102-108`), a bed and a standing lamp each; every bed switched *For guests* (gizmo) and priced **$20** with the Hospitality price arrows (read back *"Guest bed ... Price: $20"*). Rocan Covenant visitors arrived with *Assure safety* and **Ramar** claimed a guest bed at once. Guests tab (Hospitality) then listed **Goose (butcher), Isaosa (crashbaby), Bool (hunter)** in the three beds (*"Beds in use: 3/3"*) and the **recruit** toggle was switched on for all three (star column, read back as green ticks; recruitment 76% / 85% / 59%). **Open:** a guest actually joining the colony.
- [T] **"dont ignore you messages"** / **"right click on message on the right to clear old ones and left click to read them"** -- **DONE 2026-10-07 for the backlog:** every letter read, ~60 handled ones dismissed; six live ones kept (*Help wanted* from Gop-Poinmur, *Intercepted Message*, *Somebody is here* (Feeb), *Someone still alive* (Misha, *"wants out. They will leave with anyone who can carry them through a gate"*), *Request: Choose a direction*, *Quest active: Hidden Mechanitor Lair*). Stays open as a standing habit.
- [T] **"making all factions you can your allies by send gifts with drop pods"** -- needs *Transport pod* research and launchers.
- [T] **"kids need milk and cribs and toys"** -- the nursery, before any birth.


### Owner direction — every scenario, a gate in each (2026-10-07)

**Verbatim:** *"how are we gonna do the fucking tests if u dont play the game?"* -- then *"you need to be testing all three scenerios trying to get a gate built in all three"*

- [T] **Async Industries branch opening -- a gate built.** **DONE IN PLAY 2026-10-07** on the QA colony: the facility gate assembled, calibrated, operated and crossed (AI-01 and AI-03 surveys). Stays open as the reference run.
- [T] **Solo or group, inside -- a gate built.** Not started: the crew starts inside a coordinate with one shell on the surface.

### Owner direction — the unnerving register is not a room feature, it is the register everything plays in (2026-10-04)

**Verbatim owner direction (2026-10-04):** *"remember lsd unnerving feeling with all things ie events random spanwns, enemies, allies, nuetrals, even all the crazy things ive mentioned in the past and anything u can find in the many many prep docs on the Backrooms Universe"*

**THE WORD THAT CHANGES THE SCOPE IS *"all things"*.** The LSD direction has been read as an *architecture* direction for eight versions — bent corridors, seven room shapes, roads, neighbourhoods, a per-coordinate motif. All of that is built. **None of it reached a single encounter, spawn or event**, and the owner has now said twice that the register is wider than the walls: *"even wild waky carzxzy creepy things when u add places and events"*, and the complaint that produced it, *"zero weird events or people"*.

**This direction asked to be gathered, so it is gathered here rather than cited.** Every line below is the owner's own, verbatim, with where it was said:

| Owner's words, verbatim | Where it bears |
|---|---|
| *"its suppose to be a lsd trip when it comes to archeteture and shit"* | the original, and the half that is built |
| *"i want you to expand and expound on everything in a lsd way"* | answered at a fork; **"everything"**, not the walls |
| *"andf remmeber thats just the main backrooms looks further in it gets very varied and weird"* | the register deepens with depth |
| *"not just room shape echoes but echos of thier inhabitance in weird ways and items and equipment and production benches"* | **the mechanism: who WAS here, read off what they left** |
| *"even wild waky carzxzy creepy things when u add places and events"* | places **and events** |
| *"not enough weird stuff like a room with a lost person or a room full of bodies or suppplies or a labratory ofr class room or hospital of manufactuing room or tool sheed or weapons locker with loot and supplies anssd furnuture"* | named examples, and three of them are **people**, not rooms |
| *"zero weird events or people"* | the complaint, in four words |
| *"with wild random events and layouts and spawns to find and loot!!!!!!"* | events, layouts **and spawns** |
| *"really want the creepy insane looks and feel of the universe"* | the acceptance condition |
| *"so that a solo group has ability to build and get supplies on backrroms instances and find a way out before dying from metting monstrositeitys and insay psychopaths and the like in high teir hard seed ed levels of all variations"* | the register scales with depth and band, and must stay survivable |
| *"they should be nutral, allies, and enemy in all differnt kinds and relations and scenrios"* | the relations this applies across |
| *"and remembner alot of things you should be reviewing the prep materials and registry for especially backroom themed items equip,memntn and questes and logic and game paly and factions and random events and backrooms make ups you should be doing deep dives into the univers's make up of backrroms to properly design all the sustems events and specialities involved with this mod"* | the instruction to do exactly this gathering |

**AND THE PREP DOCUMENTS ALREADY SAY HOW THE FEELING IS PRODUCED, which is the part that was never applied to people.** `docs/UNIVERSE_ADAPTATION.md` line 21, on translating the source: *"Ordinary industrial interiors become uncanny through exact changes ... Use intentional spatial changes such as a shifted doorway, impossible adjacency, repeated hall, changed room dimensions, or a feature that has moved since the last visit."*

**The uncanny is an exact change to something ordinary.** It is not a new monster, a darker palette or a louder sound — the generator already applies that rule to space and it is why the floors read. Applied to an encounter it means: an ordinary RimWorld pawn, in an ordinary RimWorld relation, with **one exact thing wrong about it that the player can read**.

**`docs/THREAT_DESIGN_SHEETS.md` supplies the fairness frame and it binds every row below:** every encounter has *"a visible or otherwise accessible warning, a learnable rule, at least one countermeasure, and a recorded outcome"*; *"Do not use color or sound as the only way to notice a tell"*; first contact *"must not kill a healthy pawn instantly"*; effects are *"bounded, seed-stable, logged against a coordinate, and recoverable after saving and reloading"*. Its own closing section already named this gap — *"The other proposed monstrosities, world-town openings, missing-crew outcomes, infected or altered arrivals, containment escapes, hostile sites ... remain open design work. Do not reuse these two behaviors as a generic random-threat generator."*

- [T] **"remember lsd unnerving feeling with all things"** — **the standing acceptance condition on every encounter, spawn and event**, in the owner's words. A spawn that is merely a hostile, or merely a neutral, is the thing being complained about. The uncanny is one exact wrong detail on something ordinary, and it must be **readable** — text, never atmosphere alone. — **MECHANISM BUILT AND ENFORCED 0.12.88-dev; **the row stays open because only a launch judges a feeling.** What exists now: a `tellKey` on all twelve inhabitant families and a `traceKey` on all eight events, both refused at load if absent, both read off the thing rather than out of a notification, and both held to *one exact wrong fact, never a mood adjective* by `proof-unnerving-register.py` — the rule taken straight out of `UNIVERSE_ADAPTATION.md`. `plant-unnerving-register.py` is **32 of 32**. **What it does not cover yet**, named rather than implied: loot and equipment carry no tell of their own, the room clue texts are still instructional rather than uncanny (deliberately — they teach the vertical slice and rewriting them would remove teaching the owner valued), and *"all things"* is open-ended by construction. This is an acceptance row like *"its suppose to be a lsd trip"* and it closes when the owner plays it, not when a checker passes.** — **THE OBJECT HALF LANDED 0.12.89-dev; **the row stays open because only a launch judges a feeling.** 0.12.88-dev reached people and events; this batch reached **objects**, which the owner had named specifically — *"items and equipment and production benches"*. Twenty object tells across nine classes, each one exact wrong fact read off the thing, held to the **same no-mood-adjective gate** taken from `UNIVERSE_ADAPTATION.md`, and kept to a small derived minority of placed objects so the quiet rooms stay quiet. `plant-unnerving-register.py` is **50 of 50**. **What *"all things"* still does not cover**, named rather than implied: the room clue texts are still instructional rather than uncanny, deliberately, because they teach the vertical slice and rewriting them would remove teaching the owner valued. This is an acceptance row like *"its suppose to be a lsd trip"* and it closes when the owner plays it.** — **RECLASSIFIED TO THE TEST PHASE 0.12.98-dev, on the row's own words.** It already records the mechanism as *built and enforced* at 0.12.88-dev and says it stays open because **only a launch judges a feeling.** That is the definition of the post-completion test phase rather than of open work: there is nothing left to build, and the next step is the owner reading a spawn and saying whether it lands.

## Pending

### Owner report — one battery drains while its neighbour on the same conduit does not (2026-10-07)

**Verbatim owner report (2026-10-07):** *"hold up now, the batteryies only one is drain, thats incorrect.. one is draing very fast but they are on the same string on conductiut, soo that second line of draw u set up to one better is wrong and not needed the battery braw needs to be consistant not tied to a single battery"*

- [T] **"the battery braw needs to be consistant not tied to a single battery"** — seen in a running game. Load `rimbridge_save_20261007_before_battery_fix`, where the AI-01 connection is open on a circuit with two batteries and wood-fired generators. **What to look for:** the gate's card reads *"Gate load"* and no longer *"direct drain"*; the two batteries' stored figures fall **together** rather than one going flat; with the generators fuelled and in surplus the batteries do not fall at all; and letting the generators run dry closes the connection at the emergency-return floor rather than at zero. -- **TWO OF FOUR SEEN 2026-10-07, in the running game on `rimbridge_save_20261007_before_battery_fix`.** The card reads *"Stored on the gate's circuit: 1495.23/2400.00 watt-days. Gate load: 3500 W, carried by the grid like any building"*, and Core's own line on the door reads *"Power needed: 3550 W"* -- the door's 50 plus the gate's 3500 as one load. **The batteries fall together:** over ticks 472507 to 474313 the three holding charge went 547 to 518, 242 to 214 and 546 to 518, read off each battery's own pane -- 29, 28, 28. The fourth reads 0 / 600: the old code had already emptied it before the fix landed, and it refills only from surplus. **The generators carry first:** the net reads *"Grid excess: -2733 W"*, not the 3550 the gate and door draw, so storage covers only the shortfall. **Still unseen:** batteries holding steady under a generator surplus, which this circuit cannot produce against a 3500 W gate, and the connection closing at the emergency-return floor. -- **THREE OF FOUR SEEN 2026-10-07.** With seven generators fuelled and the AI-01 expedition holding the gate open, the net read *"Grid excess: 695 W (2400 Wd stored)"* and all four batteries read 600 / 600 Wd before and after a burst -- **storage does not fall while generators carry the gate**. The battery the old code had emptied refilled from that surplus. **Still unseen:** the connection closing at the emergency-return floor.

### Owner direction — original equipment, paper journal and gate world frames (2026-10-06)

**Verbatim owner direction:** *"gate size variants too right and any other things we need like journal and such and converting into game world"*

**Verbatim journal choice:** *"Paper field journal with matching closed, open and upright views (Recommended)"*

- [T] **Original artwork world acceptance.** After the owner launches through RimSort, inspect the six authored equipment objects in all four facings at normal zoom, including sprite scale/origin, console and bench interaction access, the bench's rotated 1x2 work side, uninstall/minify/carry/reinstall, and unchanged facility, power and storage links. Inspect the paper journal's closed ground/icon, all open and upright facings, native book reading, company issuance and field recording, physical evidence custody and analysis, then save/reload without losing identity or duplicating evidence. Inspect the 1x1, 1x2, 1x3 and 2x3 gate frames in every orientation on native doors and bound runs: centered full-footprint trim, visible animated native leaves, native access permissions, physical crossings and arrival/return cells, fog hiding and the separate `GateFramesEnabled` disable option. Record actual observations against the [authored rotation and journal artifact record](implementation/AUTHORED_ROTATION_PIPELINE.md); the compiled renderer and converted PNGs are source/build evidence and do not close this row.


### Owner direction — phase 2 is back on: our own items and benches and gates, with our own art and audio (2026-10-06)

**Verbatim owner direction (2026-10-06):** *"read now.md to get back to it and hey i have big question and im excited i just saw the pngs in C:\Users\gfour\Desktop\Backrooms\assets\source\phase2 whats phase 2 are we making our own items and benches and gates? becasue if so i fucking love it! analysis and examination of these pngs and what they are for and if we have what we need to do this all and a audio folder! sounds dope!!! how do we do sounds can we? can we do all of this for all our shit?"*

**Verbatim owner decision, asked and answered the same message (2026-10-06):** *"Full reversal — our own items and benches"* — chosen over sound-only, over sound-plus-gate-identity, and over leaving it archived.

- [T] **The mod's own art and audio appear in a running game.** The package ships **52 drawings and 17 cues** and every one is referenced by a def or by code, which a build can prove. What a build cannot prove is that the game draws and plays them. **What to look for:** each of the six rotatable buildings showing our texture from every side rather than a placeholder or a missing-texture box; the gate frame on a designated door at each of the four footprints; the charge, activation and live sequences running over it; and the cues at their moments — the rev on spin-up, the detent at each quarter, the payoff at full, the resolved latch on close. **Five of the cues had no consumer until 0.13.0-dev and had never once played**, so a tag set, a journal filed, an analysis finished, a payout and a cutoff thrown are each worth hearing specifically.

### Owner direction — the mod must not need any dependency mods (2026-10-03)

**Verbatim owner direction (2026-10-03):** *"and something i dont like that is going to take major major work and should be added to the todo : rework mod to not need any depeancie mods"*

Recorded here because the owner said *"should be added to the todo"*. **It supersedes owner decision D3/D4 as amended 2026-10-01**, which currently reads *"the five expansions and the collection are declared requirements"* — recorded in [`GATE_0_DECISIONS.md`](GATE_0_DECISIONS.md), [`ROADMAP.md`](ROADMAP.md) §Decision log and [`ARCHITECTURE.md`](ARCHITECTURE.md) §B1. Those three say the opposite of this direction and all three are rewritten in the same commit as the work, per `.claude/CONSTRAINTS.md §DOCS BEFORE PUSH`.

**Measured 2026-10-03 before writing this row, because the shape of the job is not what the words suggest:**

| What | Measurement | Where |
|---|---|---|
| Hard `modDependencies` declared | **294** | `Mod/Rimrooms - Async Industries/About/About.xml` |
| `loadAfter` entries | **294** | same file |
| Assembly references | **4 — `Assembly-CSharp` + `UnityEngine.CoreModule` / `IMGUIModule` / `TextRenderingModule`. Nothing else. No Harmony.** | `src/RimroomsAsyncIndustries/RimroomsAsyncIndustries.csproj` |

**So the two halves of this are wildly different sizes, and saying so is the point of measuring first.**

- [T] **Core-only startup actually observed.** The audit above closes on source evidence; a clean Core-only load with zero red errors is a launch, and only the owner launches. Post-completion test phase, gates nothing.

### Open rows carried out of the play-testing checkpoints (2026-09-30 to 2026-10-01)

**Lifted here 2026-10-02 by owner direction:** *"we need to move all finished items to finalized.md from the todo, the todods sahll never hold completed items, they are always to be moved to finalized first then deleted from the todods once confirmed virbatium transfer"* and, on being shown the queue still at ~96 KB, *"BEcause the todos are still like 100kb and i know that not all unfinished work and only unfinished work like it shall be"*.

Nine `##` sections titled as dated checkpoint records held **20.9 KB** between them, most of it the finished write-up of a launch or a rebuild stage, with these open rows buried inside. **A section called "Fifth launch findings - 2026-09-30" is a thing that happened, not a thing to do.** Each section is archived whole in `FINALIZED.md`, record intact; every open row it held is below, verbatim, tagged with the checkpoint it came out of.

**1 row(s) repeated verbatim across checkpoints and are carried once.** The same open item written three times is one open item; the repeats are named in the archive rather than dropped silently.

**From `## The first walked level — 2026-09-30 (0.12.61-dev) — DONE`:**

**Adjudicated against the source 2026-10-03.** The section title was never the marker, per `.claude/CONSTRAINTS.md §FINALIZED BEFORE DELETE`: *"A section titled DONE whose rows are still `[ ]` does not move. The title is not the marker."* So each row below was read against the code rather than promoted on the heading's word. **Eleven of the twelve were built and nobody had ticked them.** `RoomLayoutPlanner.cs` (1,351 lines) and `RoomArchetypeService.cs` (392) were read in full; `RoomContentBuilder.cs`, `BackroomsPalette.cs`, `GuaranteedFrontiers.cs` and the four Def folders were read at the named sites. **Register checked:** `python tools/register-query.py trace RR-SPACE` → 15 rows, Core *Required* and the rest *Optional* / *Configuration only* / *No integration*; none applied, because this pass changes no code.












- [T] **"there is a weird route thing name a self in one of the rooms and this is kinda weird and odd"** — owner's own read: *"we probably havent gotten to a routing system yet for emergency exit and glow pods with the company start but lets try and fix this"* — **THE STATED CAUSE IS ANSWERED AND THE SIGHTING IS NOT, so this is the one row of the twelve that moves to the test phase rather than closing.** The routing system the owner supposed was missing **exists**: `CompRimroomsMarker` with five `RimroomsMarkerTypeDefs` — `RR_Marker_Route` labelled *"route home"*, plus `_Cleared`, `_Danger`, `_Cache`, `_Lead` — numbered through `FirstSliceSiteComponent.NextMarkerNumber`, and the survey tag is a Core `GlowPod` since 0.10.7-dev. **But markers are player-deployed, so a freshly generated level should carry none**, and **what the owner actually saw cannot be identified from here** — naming it needs somebody looking at the object on a map. Deliberately not guessed: editing a label on a hunch is the same move that lost three launches in one method.

**From `## Lights and geometry — 2026-09-30 (0.12.61-dev) — DONE`:**

**Adjudicated against the source 2026-10-03, same pass as the section above.** **All ten were built and none had been ticked.** Seven of them are implemented by one function, `RoomLayoutPlanner.RockIntrusionCells`, whose seven forms exist precisely because of these rows.











### Major M1 — Connected colony portals (ROADMAP M1; master TODO §Native-provider foundation — 0.4.0-dev)

Binding contract: [`CONNECTED_COLONY_PORTALS.md`](CONNECTED_COLONY_PORTALS.md). Baseline commit `8ed4e32`, 0.4.1-dev, 75 C# files, 71 package files, zero warnings/errors. Read `implementation/CONNECTED_COLONY_CHECKPOINT.md`, `CONNECTED_COLONY_IMPLEMENTATION_TASK.md`, `CONNECTED_NETWORK_IMPLEMENTATION.md`, `CONNECTED_CROSSING_IMPLEMENTATION.md`, `CONNECTED_WORK_CORE_API.md`, `CONNECTED_PORTAL_STATE_MIGRATION.md`, `CONNECTED_WORK_PROFILE_BOUNDARIES.md` before editing `src/RimroomsAsyncIndustries/Portals/` or `Gate/`. Source fact: nothing in the repo calls `RimroomsPortalNetwork.Register`, `PortalCrossingService.Cross`/`Recover`, or `CompRimroomsGate.BeginPortalOpening` yet.

**Master TODO items (verbatim):**

- [T] Implement every open item in [connected colony portals](CONNECTED_COLONY_PORTALS.md#required-implementation-backlog): independent connection ownership, permanent natural portals, free crossing, shared cross-map work/materials, persistent seeds and dynamic inhabitants/complexity. This supersedes dispatch-only travel as the target. — **PARTLY BUILT**; what shipped is archived. **Open:** runtime acceptance of the built routes, and nothing in code. -- **EVERY ROUTE ON THIS ROW IS BUILT; WHAT IS LEFT IS A LAUNCH. 0.12.99-dev.** The pointer *"the individual routes listed below"* was the shape checker 25 was written against, and replacing it with the subjects is what showed the row was finished: **independent connection ownership, permanent natural portals, free crossing, shared cross-map work/materials, persistent seeds and dynamic inhabitants** all ship. Cross-gate work is **31 families, 23 of them deployments**, and every work type in Core and all five expansions is covered or decided against with its reason recorded (`research/WORK_TYPE_COVERAGE_AUDIT.md`). **The only remaining step on any of its routes is runtime acceptance, which only the owner's launch can give**, so it belongs in the test phase rather than the working queue where it reads as something somebody could pick up.

**Resume order (verbatim from `implementation/CONNECTED_COLONY_CHECKPOINT.md`; these are the working sequence for the items above):**

- [T] **Resume step 6:** "Continue source/build milestones. Runtime acceptance remains deferred until the owner launches through RimSort; no agent game launch or profile change." — each milestone: `./tools/build.ps1`, evidence folder under `implementation/evidence/<name>-<date>/`, build record, master TODO ticks, then cascade-publish per `PUBLISHING.md`. — **Open and structurally must stay open:** runtime acceptance, because only the owner launches. -- **MOVED TO THE TEST PHASE 0.12.99-dev, on the row's own words.** It says *"Open and structurally must stay open: runtime acceptance, because only the owner launches."* **Every source and build milestone it asks for is met** -- build, evidence folder, build record, ticks, cascade -- and the cascade is now twelve refs with the tool receipting itself. What is left is acceptance, and acceptance is a launch. **A row whose only remaining step is an owner launch does not belong in the working queue.**

**Required implementation backlog (verbatim from `CONNECTED_COLONY_PORTALS.md`; the acceptance list the majors above must satisfy):**

- [T] Implement cross-map job discovery, destination targets, route costs and reservations; preserve native per-pawn schedules and restrictions. *(source partially complete in 0.5.0-dev: discovery, destination targets, bounded routing, planning leases and real native destination reservations exist and are proven for the storage-hauling family only; the other families are not implemented and runtime acceptance is open)* -- **MOVED TO THE TEST PHASE 0.12.99-dev -- THE PARENTHETICAL WAS A 0.5.0-dev STATUS NOTE AND IS STALE.** It says discovery, destination targets, bounded routing, planning leases and real native destination reservations exist *"and are proven for the storage-hauling family only; the other families are not implemented"*. **Thirty-one families are implemented**, 23 of them deployments, and `research/WORK_TYPE_COVERAGE_AUDIT.md` shows every work type in Core and all five expansions either covered or decided against with its reason recorded -- plus, as of this batch, the thirteen work types the 294 profile adds. Native priorities, schedules and restrictions are preserved and the handling closed earlier. **The row's own last clause is what remains:** *"runtime acceptance is open"*, and only the owner launches.
- [T] Implement connected-site scheduling/streaming and measure performance after an owner-launched build. — **STILL OPEN.** Scheduling and streaming ship. **Measuring performance requires an owner-launched build, which is the one thing this project cannot do for itself.** -- **MOVED TO THE TEST PHASE 0.12.99-dev, on the row's own words.** It says *"Scheduling and streaming ship. Measuring performance requires an owner-launched build, which is the one thing this project cannot do for itself."* **A row whose only remaining step is an owner launch does not belong in the working queue**, where it reads as something somebody could pick up today. Every scan in `ConnectedWork/` is already a bounded rotating window rather than a prefix, by invariant 5, with roughly thirty budgets -- so the bounding half is done and the measuring half is a launch.
- [T] Record owner-launched acceptance for multi-map work, both directions, permanent natural portals, intermittent laboratory links, saving/reloading, every supported work adapter and applicable DLC/profile variants. — post-completion test phase (owner RimSort launch).

**Task-record subitems still open (verbatim from `implementation/CONNECTED_COLONY_IMPLEMENTATION_TASK.md`):**

- [T] Owner-launched acceptance: both directions; chains/loops; closed/blocked endpoints; permanent natural links; save/reload; cargo identity; interrupted jobs; all supported native/provider routes. — post-completion test phase (owner RimSort launch).

**Undeferred 2026-09-29 by owner direction** — moved here verbatim from `DEFERRED.md`, which is now empty of open rows:

- [T] **Connected-site scheduling and streaming, then measurement.** Active connected job destinations must not be silently unloaded to meet a budget. Measurement itself belongs to the post-completion test phase and gates nothing. Source: `CONNECTED_COLONY_PORTALS.md`, `research/PERFORMANCE_BENCHMARK_PLAN.md`.

### Owner direction — the starting facilities get fixed by hand and the fix becomes the default (2026-10-05)

**Verbatim owner direction (2026-10-05), the loop:** *"as i load up the different scenerios we will be needing to fix the layout of the starting facilities(i will be manual using pawns to change the layout and fix some thing, to which you will use the api mod to see what exactly i change/add to the starting facilities that you will be making standard and default to the starting scenrios so that the problems like broken conduit lines are repaired by me, then updated to match for the mods defualt facilities)"*

**And verbatim on the first thing to do, also 2026-10-05:** *"check off open items that we complete/you complete, when i start it up"*

**Asked at two forks before the launch and answered.** On the wiring: *"I'll hand-fix it, you read it back"*. On the missing battery: *"optrion 2 but ill fix it manually like question 1 and u will use the api mod to look where i change things and then fix the scenerio to have those changes on start next time"* — option 2 being **Async Industries only**. **So nothing is auto-authored.** The owner places it, the tool reads it, the def follows.

- [T] **The starting-facility feedback loop.** `.local/qa/facility-diff.py` is built and its offline half is verified: `authored` renders a start def's layout exactly, `snapshot` tiles the facility rect through `rimworld/get_cells_info` (read-only, 31×31 tiles under the bridge's 1024-cell cap, one cell of margin because the owner may build just outside the authored rect), `diff` reports what changed and **emits paste-ready `<conduits>` and `<buildings>` XML**, and `power` checks grid connectivity from the def alone. **Blueprints and frames count as the owner's intent**, so a fix is readable before pawns finish building it. **Open:** the authoring itself, which happens as the owner launches each start.
  - [T] **THE PRE-LAUNCH BASELINE, measured 2026-10-05 before any launch, so the diff has something true to compare against.** **Neither facility has working power as authored.** `RR_AsyncIndustriesStart`: **34 of 34** power-drawing buildings are unconnected, the nearest conduit to any of them is **3 to 7 cells away**, there are **5 separate conduit grids** (167/15/8/8/7 cells), and of the two `WoodFiredGenerator`s **one sits off the wire by 2 cells**. `RR_FurnitureStoreStart`: **8 of 8** unconnected and its single generator is **3 cells off the wire**. **Neither authors a battery**, though the Async Industries start card promises *"one utility generator with a small reserve battery"*. **The number was checked before it was believed** — 34 of 34 is exactly the too-round figure that caught a false reachability result at 0.12.9x, so the distances were measured individually rather than trusted: 3, 3, 3, 6 and 7 cells on the sample. The conduit runs are corridor spines with no spur reaching anything. **This is the owner's reported *"broken conduit lines"* found deterministically, from data, with no launch needed.**
  - [T] **What the loop can and cannot carry, read off `RimroomsStartDef` rather than hoped for.** **Carries:** a building's `thing`, `stuff`, `cell` and `rotation`; a conduit run; a door; an autodoor; a pillar; `batteryFraction`; `fuelFraction`; a glazing wall run. **Does not carry:** a **per-cell floor change**, because flooring is one facility-wide `floorTerrain` plus a per-room boolean and there is no per-cell terrain list; and a **knocked-through wall**, because walls are generated from the room rectangles, so a removal is a room edit rather than a building edit. **Both limits are stated before the session rather than discovered after it**, since a change the def cannot express is owner time that cannot be kept.

### Owner direction — anything standing on your map may cross a gate, and zoning is the control (2026-10-06)

**Verbatim owner direction (2026-10-06), four messages in a row.** The first, on finding the wiki saying no guests arrive:

> *"what??? vistors cant walk through the gate to find work and beds??? we need cross map cordinator or something thats automatic merging maps to cross control so pawns auto get command to cross when mpas call them like a empty bed work task or job ect ect or anything at all"*

**Then, correcting the scope of who:**

> *"not anyone in base, but anyone on your map.. a enemy can break in and cross the gate to get valuables and members"*

**Then, widening it again:**

> *"hold up now friendlys can too"*

**Then, on the control surface:**

> *"all one person choices in zoning"*

**And then, asked what that meant, the owner settled it before it could be guessed:**

> *"i mena its upto the play to zone pawns where they want them,, that was the whole cross zone support"*

**And two forks were answered before those last three arrived**, both at the permissive end, both with their cost stated in the option text before it was chosen: needs **"commute"** rather than pawns living on the far side, which the option named as *the window closes mid-sleep and the pawn is stranded*; and crossing open to **"Anyone standing in your base"**, which the option named as *they can die down there, and that is a faction incident with no good explanation*. **Message two then superseded "in your base" with "on your map"**, which is wider and sharper: a raider does not need to be a guest.

**WHAT IS ALREADY BUILT, MEASURED BEFORE ANY OF THIS WAS DESIGNED, because the first message asks for a thing that largely exists.** `WorkGiver_ConnectedDeployment` has **56 work givers** running on RimWorld's own work loop, so a colonist on the surface is offered a job on the far map and crosses by itself. `WORK_TYPE_COVERAGE_AUDIT` puts **21 of the game's 23 work types** across a gate. **The automatic cross-map coordinator the owner asked for is shipped for WORK.** The gap the owner put their finger on is exact: beds appear in that code only for carrying a **downed** patient to one, so **no healthy pawn ever crosses for a need** -- not an empty bed, not food, not recreation. *"like a empty bed work task"* is the missing half.

- [T] **Anything standing on your map may cross a gate, and zoning is the control.** **Both halves shipped after that paragraph was written**, so the *"missing half"* above is closed: `CrossForNeed.cs` sends a healthy pawn across for rest, food or recreation — **as a component rather than the think-tree insert the brief specified**, because an insert edits Core's most contested structure and fails silently when another mod moves its tag — and `GateEgress.cs` sends somebody who is not yours **outbound**, with `canSteal` and `canKidnap` from the owner's own *"to get valuables and members"*. **What to look for:** a raider breaking in and walking through an open gate rather than ignoring it; a colonist crossing on their own for a bed or a meal and **coming back** — the stranding guard checks all three legs before committing, so a pawn should never begin a crossing it cannot finish; a friendly crossing and the faction surviving it; and **zoning actually holding** — restrict somebody to the colony and they stop being offered the far side, restrict them to a coordinate and they stay in it. **Throwing the kill switch is the counterplay to all of it.**

## Public face: the site, the Workshop page and the collection

**Verbatim owner direction (2026-09-29):** *"fyi when we get to it we will build a github deployable html build that catologs the whole mod and is the main mod site wiki and documentation dump in a beauty of a deployable github page with what ever you can do so the deploy address is not some random git hub address but is a nice backrooms url for github deployed page where we document all the mods capabilities and howto and related public facing docs and information into a website that lays everything out top to bottom beautiffully just like other rimworld mods make theri third party sites, not to metione the building of the steam workkshop mod collection and workshop mod deploy for our mode with write ups for  both with links in them to each other and the deployed site so things will have to be deployed and settled before doing the proper order of setting up the workfshop collection and the mod in the workshop, idk maybe we will use a playwrite thing so you can click through steam and set it all up keeping me from having to do it all"*

**Full plan: [`PUBLIC_RELEASE_PLAN.md`](PUBLIC_RELEASE_PLAN.md)** - structure, the ordering chain, the domain question, and the three decisions that are the owner's to make.

**Not started. Owner said *"when we get to it"*, and it is correctly last:** every one of these artefacts describes the mod, so each is written twice if the mod is still changing underneath it. The same reason the player-facing how-to sits at the end of the build order.

### The ordering the owner named, which is a real dependency chain

1. **The mod is settled** - content set final, scenarios in, nothing still being retired.
2. **The site is deployed and working**, at its proper address.
3. **Then** the Workshop mod page, whose write-up links to the site.
4. **Then** the Workshop collection, whose write-up links to both.

Owner's words: *"things will have to be deployed and settled before doing the proper order of setting up the workfshop collection and the mod in the workshop"*. Doing any of it earlier means publishing links that point at nothing.

### Phase 1 leftovers (master TODO §Phase 1 — repository, build, and content foundations)

- [T] Define RimSort-managed test profiles: preserve the 295-entry product target (the existing 294 plus Rimrooms), then record RimBridgeServer as a separate QA overlay (normally 296 loaded entries). RimSort owns sorting, saving mod lists, and every launch; the owner starts sessions through RimSort. Do not add direct RimWorld or GABS launch profiles or remove target mods to offset the bridge. — post-completion test phase (owner-operated RimSort action). **PRE-LAUNCH STATE MEASURED 2026-10-06, so this row starts from a fact rather than from an assumption.** `ModsConfig.xml` holds **301 entries and 296 unique** — the content reconciles exactly with the owner's own *"296 (6DLCs, Rimbridge, Rimrooms(locally))"*, and **both `rimrooms.asyncindustries` and `brrainz.rimbridgeserver` are active**, so the QA overlay is in place as this row intends. **Two things about the ORDER are not what this project documents, and neither is a mod defect:** all five expansions appear **twice**, and the second set sits **after Rimrooms**, so the mod that `install.md` and `mods.md` both say *loads last* currently has five entries behind it. **The 2026-10-05 log shows the game did not complain** — no duplicate-packageId line — and its only two red lines are `ThreadAbortException` at shutdown beside `Memory Statistics:`, which is close-down noise rather than a fault. **A sort and save in RimSort rewrites the list and settles both.** Recorded, not corrected: `ModsConfig.xml` is the player's own config and the sorter's output, and no instrument here edits a profile. **CORRECTED 2026-10-07 — THAT READING WAS WRONG.** Owner: *"i dont know what ur talking about Rimsort only has my DLCs once so if the mod is fucked fucking fix it!"* Re-read: `<activeMods>` holds 296 entries with each expansion **once** and Rimrooms **last**; the second set of five is `<knownExpansions>`, RimWorld's own record of which expansions it has seen, which is not part of the load order. Nothing to sort, nothing to fix; the order is exactly what the docs say.
- [T] After the first owner-launched full-target startup, collect matched Core/profile performance baselines on RR-DEV-01 and implement any missing counters per the [benchmark plan](research/PERFORMANCE_BENCHMARK_PLAN.md). Enforce the recorded budgets before promoting features or larger room/map bands. — post-completion test phase (owner RimSort launch).

### Phase 2 — code architecture and safe vertical slice (master TODO; source largely present per `implementation/PHASE_2_BUILD_RECORD.md`, full stated scope + Gate 2 acceptance still open)

**Vertical slice implementation:**

- [T] Save, reload, revisit the same coordinate, and confirm map state and unique rewards persist without duplication. — post-completion test phase (owner RimSort launch).

**Gate 2 passes when** (master TODO): "the first complete loop plays from a fresh save through build, staff, expedition, extraction, analysis, reward, save/reload, and a second visit without a softlock or lost state." — owner-launched only.

### Major M3 — Phase 3 interconnected company simulation (ROADMAP M3; master TODO §Phase 3)

**Scenario framework and alternate starts** (contract: [`SCENARIO_SETUP_AND_PORTAL_NETWORK.md`](SCENARIO_SETUP_AND_PORTAL_NETWORK.md); owner questions still open: inside-start party size; first-exit fixed vs chosen):

- [T] Verify every start's reload behavior, deterministic coordinate, objective idempotency, optional-DLC fallback, solo behavior, and RWT eligibility against `SCENARIOS.md`. — post-completion test phase (owner RimSort launch).

**Procedural sites and propagation** (contract: [`PROCEDURAL_SPACE_CONTRACT.md`](PROCEDURAL_SPACE_CONTRACT.md)):

- [T] Bound active map count, pawn/thing count, graph search, event evaluation, and background tick cost; profile large, long-running saves. — **Bounding is done; profiling is not and cannot be.** Every scan in `ConnectedWork/` is a bounded rotating window, never a prefix (invariant 5), with roughly thirty `Maximum*` scan budgets. **Profiling a long-running save requires launching the game, which only the owner does.** — **RECLASSIFIED TO THE TEST PHASE 0.12.98-dev, on the row's own words.** It says in its own text: *"Bounding is done; profiling is not and cannot be"*, and that profiling a long-running save **requires launching the game, which only the owner does.** Every scan is already a bounded rotating window rather than a prefix, with roughly thirty budgets. **A row whose only remaining step is an owner launch belongs in the test phase**, not in the working queue where it reads as something somebody could pick up.

### Major M4 — Phase 4 multiplayer, DLC, and the full profile (ROADMAP M4; master TODO §Phase 4)

Every item in this major needs a Rimrooms build the owner has launched; source-side preparation (feature detection, guards, adapters) can proceed, verification cannot.

**RimWorld Together adapter** (pinned release 26.8.31.1; no supported client extension API identified 2026-09-27):

- [T] Verify guild identity, facility mapping, configured visits/snapshot behavior, visits when online/offline, transfer spot, chill/defense spots, caravan interactions, events, sites, roads, aid, gifts, and trading. — post-completion test phase (owner-launched two-client run).
- [T] Verify transfer receipt IDs and item/pawn state prevent duplicates, loss, stale ownership, and broken stacks on disconnect/reconnect. — post-completion test phase (owner-launched two-client run).
- [T] Verify Backrooms Research Dossier item transfer; receiving branch must explicitly study it locally and be unable to claim it twice in one save. — post-completion test phase (owner-launched two-client run); dossier binds to an existing physical document object per the content-reuse rule.
- [T] Test unsupported/complex modded items and define an honest fallback message rather than promising an unverified transfer. — post-completion test phase (owner-launched two-client run).
- [T] Test separate colony saves, shared world actions, mod order/config enforcement, RWT server restart/backups, and an admin changing settings during play. — post-completion test phase (owner-launched two-client run).

**Five DLC layers:**

- [T] Before implementing or advertising optional VGE support, verify the clean Core + Harmony + Odyssey + VEF + both VGE chapters stack, Chapter 1 operations, Chapter 2 threat/defense/salvage, optional Insectoids 2, save/reload, and the gravship-touch profile graph. Keep this in the per-integration acceptance gate; it is not a Gate 0 requirement. See the [gravship profile review](research/GRAVSHIP_PROFILE_INTERACTIONS.md). — post-completion test phase (owner RimSort launch).
- [T] Verify all five individually enabled/disabled, then all combined. Maintain a 32-row DLC bitmask matrix (all combinations of five DLCs) if claiming full combinatorial support; at minimum, explicitly publish exactly which combinations were run. — post-completion test phase (owner RimSort launch).

**All 294 profile entries** (all rows source-reviewed; zero rows runtime-cleared):

- [T] Pin the exact profile and test clean Core, Core+RWT/Harmony, selected VGE stack, each high-risk family, and the full ordered profile. — post-completion test phase (owner RimSort launch).
- [T] Verify all QoL features remain available, including work-priority, UI, scheduling, storage, movement, hauling, selection, visitors, prisoners, health, combat, map, and scenario helpers represented in the list. — post-completion test phase (owner RimSort launch).
- [T] Resolve duplicate Defs/patch collisions in the exact 294 profile; use load-after patches only where a reproducible conflict requires one. — **STILL OPEN.** **Structurally requires a launch with the 294 profile loaded**, which only the owner does, through RimSort. -- **MOVED TO THE TEST PHASE 0.12.99-dev, on the row's own words:** *"Structurally requires a launch with the 294 profile loaded, which only the owner does, through RimSort."* A collision is a thing two mods do to each other at load; it cannot be found by reading.
- [T] Test gravship-changing profile mods against both VGE chapters; publish incompatible combinations rather than hiding known conflicts. — post-completion test phase (owner RimSort launch).
- [T] Add a user-facing compatibility report with tested order, versions, DLC, known issues, unsupported features, and save caveats. — **STILL OPEN.** Cannot honestly state a tested order before anything has been tested. -- **MOVED TO THE TEST PHASE 0.12.99-dev, on the row's own words:** *"Cannot honestly state a tested order before anything has been tested."* D1 forbids announcing compatibility before validation, so writing this report now would be the exact claim the rule exists to stop.

### Major M5 — Phase 5 complete Company Command interface and polish (ROADMAP M5; master TODO §Phase 5)

Contracts: [`OPERATIONS_ACTION_CONTRACTS.md`](OPERATIONS_ACTION_CONTRACTS.md), [`research/VISUAL_AUDIO_STYLE_BRIEF.md`](research/VISUAL_AUDIO_STYLE_BRIEF.md), [`research/CONTENT_ACCESSIBILITY_BRIEF.md`](research/CONTENT_ACCESSIBILITY_BRIEF.md), [`TUTORIAL_SCRIPT.md`](TUTORIAL_SCRIPT.md). Source checkpoint: ten Operations panes, two original menu images, slideshow controller, settings, dynamic title/version exist.

- [T] Review every slideshow image with the actual menu overlay across supported aspect ratios, resolutions, and UI scales; check text contrast, crop safety, quiet transitions, reduced-motion behavior, and no-audio use. — post-completion test phase (owner RimSort launch).
- [T] Review text length, font scale, combat readability, motion sensitivity, audio levels, UI overlap at supported screen sizes, and translations. — post-completion test phase (owner RimSort launch).
- [T] Verify no UI panel conceals urgent health, fire, power, missing crew, gate recall, containment, or contract priorities. — post-completion test phase (owner RimSort launch).

**Undeferred 2026-09-29 by owner direction** — moved here verbatim from `DEFERRED.md`, which is now empty of open rows:

- [T] Slideshow integration review, additional menu images per shipped scenario. — **Open, and it needs a launch:** the integration **review** itself — how the slides read behind the menu buttons, and whether 30 s dwell and 2 s crossfade feel right — cannot be judged from here. (Six slides and `proof-menu-slides.py` closed at 0.12.17-dev; archived.) -- **MOVED TO THE TEST PHASE 0.12.99-dev, on the row's own words:** *"Open, and it needs a launch: the integration review itself -- how the slides read behind the menu buttons, and whether 30 s dwell and 2 s crossfade feel right -- cannot be judged from here."*
- [T] Validation sweep, invalid-state matrix, balance, release report, packaging. — **split 2026-09-29 by owner decision 19.** The validation sweep and packaging halves are M6a and close without a launch; the invalid-state matrix, balance and release report are M6b and cannot. Tracked as separate rows in `TODO.md`. — **STILL OPEN.** **Structurally requires a launch.** Balance in particular cannot be claimed: nothing in this mod has ever been played. -- **MOVED TO THE TEST PHASE 0.12.99-dev. Its two closable halves are closed and the rest is a launch.** The row's own split says the validation sweep and packaging halves are M6a; **both closed in this batch as their own rows** -- nine instrumented subjects, and the release ritual written into `PUBLISHING.md`. What the row still names is the **invalid-state matrix, balance and release report**, which are M6b, and its own text says why: *"Balance in particular cannot be claimed: nothing in this mod has ever been played."*
- [T] **Automated fixtures for deterministic room generation, gate transitions, ledger idempotency, transfer receipt IDs and schema migration.** Deferred **by explicit owner instruction**, 2026-09-29 (decision 20, verbatim *"option 2 and option 3"*), not by dependency: the owner authorised automated fixtures **and** chose to hold them until after the first launch so their content follows observed failures rather than guessed ones. This is the **only** exception to the `CONTRIBUTING.md` no-tests rule anywhere in the repo, it covers this row alone, and **nothing for it may be written before the owner has launched the game once**. Owned by M6b.
- [T] **Screenshots, trailer and preview art for the mod page.** Need a running game, so they split from the M6a mod-page row into M6b. Everything else on that row — description, feature list, installation guide, dependencies, DLC matrix, RWT setup, credits, provenance, license, FAQ, update plan — closes without a launch and is M6a.

### Major M6b — Phase 6 work that structurally requires the owner's launch (ROADMAP M6b; master TODO §Phase 6)

**Exit condition (D1, changed 2026-09-29):** the Core-only solo path passes. The private RWT prototype is no longer a release prerequisite and co-op validation no longer gates the first publication. The no-compatibility-claim rule stays binding and is now the main protection.

- [T] Create a reproducible fresh-start/save/reload/revisit checklist and automated or manual fixtures for deterministic room generation, gate transitions, ledger idempotency, transfer receipt IDs, and schema migration. — **owner decision 20, 2026-09-29, verbatim: *"option 2 and option 3"***, being *automated fixtures in code* **and** *defer until after the first launch*, taken together. So: **automated fixtures are authorised** for this row, replacing the manual-checklist-only reading, **and none of it is written until the owner has launched the game once**, so its content is shaped by observed failures rather than guessed ones. The exception is narrow — the five subjects named in this row and nothing else — and is not permission for a general test suite.
- [T] Run the scenario acceptance checklist for every shipped opening: fresh start, reload, failure/recovery, route back to the shared campaign, and optional-mod/DLC absence. — post-completion test phase (owner RimSort launch).
- [T] Exercise invalid states: insufficient power, no operator, blocked route, missing exit, destroyed gate, overloaded expedition cargo, receiving bay full, split/delayed bulk shipment, missing/changed OgreStack setting, dead/missing crew, unsafe return, destroyed relay, unavailable RWT feature, failed item transfer, missing DLC, bad mod order, and old save migration. Include a one-million-silver case: 67 stacks under the active OgreStack default assumption, 2,000 under Core limits; verify actual in-save settings and record hauling/storage/transfer results. — post-completion test phase (owner RimSort launch).
- [T] Check performance on worst-case room graphs, multi-outpost company, long play time, many evidence/case records, visitors/prisoners, active threats, and gravship combat. — post-completion test phase (owner RimSort launch).
- [T] Balance economy and progression from fresh-start play through late game; check grind, runaway money, research skip routes, dead-end tech, exploitative optimal choices, and difficulty scaling. — post-completion test phase (owner-launched play).
- [T] Verify the full mod list one final time and capture game/RWT/DLC/profile versions, settings, logs, save, known compatibility issues, and results in a release report. — post-completion test phase (owner RimSort launch).
- [T] Test clean install/uninstall, load order, Workshop update, dedicated RWT server setup, player join, server backup/restore, save migration, and rollback to previous mod release. — post-completion test phase (owner-operated).
- [T] The launch-gated half of the mod-page row: **screenshots, trailer/preview art**, and any known-issues entry that needs an observed failure. The row itself lives in M6a with its full verbatim text; only these pieces need a running game. — post-completion test phase (owner RimSort launch).
- [T] The launch-gated half of the tag-release row: *"publish only features that passed their listed acceptance criteria"* — **nothing has passed anything, because nothing has run.** The row itself lives in M6a with its full verbatim text; the tag cannot be cut until the acceptance results above exist. — post-completion test phase (owner RimSort launch).

### Owner direction — the place copies you, and who you find in it (2026-09-29)

**Verbatim owner direction (2026-09-29), on ordering the remaining work:** *"we are doing it all so order needs to be logical and your intelkligent educated choise based on logical programming order of operations"*


- [T] **"to the extent we want normal and really want the creepy insane looks and feel"** — the balance between recognisable and wrong is currently fixed by the depth curve. Whether it lands is a play question and belongs to the post-completion test phase. -- **MOVED TO THE TEST PHASE 0.12.99-dev, on the row's own words:** *"Whether it lands is a play question and belongs to the post-completion test phase."* The mechanism is built and measured -- the look is a function of depth across five bands, and the architecture's agreement with itself falls from 89.4% to 36.4% by depth. **Whether that feels right is a judgement only a launch can make.**

### Owner direction — the look, and the seed generator that has to carry the universe (2026-09-29)

**Verbatim owner request (2026-09-29):** *"and we can use the floor lights i guess for the yellow carpet and yellow wood walls for the main backrooms look as we dont have over head florrecent lights unless we could repurpose floor lights correctly, and remmeber when building the seed genrator for the back rooms everything ive said and how the backrooms universe works to be lots of furnature and equipment and different types of rooms and materials of all types from labs, to workshops, to nursaries, to everything imanginable and every variation of them and even wild waky carzxzy creepy things when u add places and events to proper balance levels of colony wealth and the like so that a solo group has ability to build and get supplies on backrroms instances and find a way out before dying from metting monstrositeitys and insay psychopaths and the like in high teir hard seed ed levels of all variations"*

**And immediately after:** *"andf remmeber thats just the main backrooms looks further in it gets very varied and weird"*

That second message is what shaped the palette: a single global look could only ever deliver half the direction, so the look is a **function of depth**. Record: [`implementation/BACKROOMS_PALETTE_IMPLEMENTATION.md`](implementation/BACKROOMS_PALETTE_IMPLEMENTATION.md).

- [T] **"so that a solo group has ability to build and get supplies on backrroms instances and find a way out before dying"** — **THE ARITHMETIC GUARANTEES IT AS OF 0.8.0-dev**, as three properties rather than tuning: an **absolute** cap of three simultaneous encounters at any depth and any wealth; **half of every coordinate's rooms bare by count rather than by chance**, so an unlucky run of rolls cannot produce a space with something in every room; and a first visit always quiet. Shallow coordinates are also capped below the top band regardless of wealth. **Stays in progress until inhabitants exist and the condition can actually be observed.** — **an acceptance condition on the whole generator, not a nice-to-have.** A high-tier coordinate that cannot be survived solo by building, supplying and finding a way out has failed this direction regardless of how good it looks. — **RECLASSIFIED TO THE TEST PHASE 0.12.98-dev, on the row's own condition.** It says it stays in progress *"until inhabitants exist and the condition can actually be observed"*. **Inhabitants exist** — twelve defs, wanderers through to the dead and the psychotic — and the three guarantees are constants in source rather than tuning: `MaxSimultaneousEncounters = 3`, half of every coordinate's rooms bare by count, and a quiet first visit. **So nothing buildable remains; what remains is watching it**, which is the owner's launch and belongs in the test phase rather than the working queue.

### Owner direction — the 294-mod register must actually work and be human navigable (2026-09-29)

**Verbatim owner request (2026-09-29, seven items):** *"read Now. md and any and all revent prep docs as you continue the todo work and take not there is a mode .xlml like thing that im not sure is fully working i try to open it but its not human navigatable but its suppose to spreeadsheet out all the mods and potential uses and issues and theri uses and descriptions and shit if i remember correctly and you should definatly be using it and or fixing it up as you go along with build the Mod here and or update it where need of past work already done and continue it forward and making sure it is human havigate able becasue i open it up and i dont see what the preview images show, so idk how it works or if it does"*

**Verbatim owner identification (2026-09-29):** *"Rimrooms_Async_Industries_294_Mod_Integration_Register this thing is what i was talking about"*

**Verbatim owner report (2026-09-29, the root cause):** *"wtf is this xlsx??? i thought it was a spread sheet but it just opens up codex for chatgpt??? wtf i thought it was the mod spreedsheeet! fix it"*

Full record in [`implementation/MOD_REGISTER_REBUILD.md`](implementation/MOD_REGISTER_REBUILD.md); the work-type findings it produced are in [`research/WORK_TYPE_COVERAGE_AUDIT.md`](research/WORK_TYPE_COVERAGE_AUDIT.md).



**Undeferred 2026-09-29 by owner direction** — moved here verbatim from `DEFERRED.md`, which is now empty of open rows:

- [T] **The register opens without a repair prompt or a layout complaint** in whatever the owner actually uses. This is the one claim structural verification cannot make; it belongs to the post-completion test phase.

### Post-completion test phase — `[T]`, gates nothing

- [T] Runtime regression acceptance for these increments and their connected first-expedition loop, after the owner launches the disposable RimSort profile. *(master TODO §Earlier company/scenario increments)* — Needs, in the post-completion test phase: the owner's RimSort launch of the 295-entry product target (296 with the RimBridgeServer QA overlay attached afterward). Claude never starts RimWorld, never touches the active RimSort list, never attaches RimBridgeServer outside `research/RIMBRIDGE_TEST_HARNESS.md`.

**Undeferred 2026-09-29 by owner direction** — moved here verbatim from `DEFERRED.md`, which is now empty of open rows:

- [T] **Every runtime acceptance row** across M1–M6 (Gate 2 onward), including the per-checkpoint acceptance lists at the foot of each implementation record. These feed the phase above. They gate nothing.
