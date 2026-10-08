# PLAYSCRIPT — the operations manual: a Rimrooms run, start to empire

**Why, owner 2026-10-08, verbatim:** *"think massive perfectly set up working facility and machine gate operations of using the bacvkrooms for cash like stripping and taking things to sell and completing misisons ect ect BUILD YOUR EMPIRE UNITY MAKE A RIMWORLD PLAY SCRIPT?.MD"*

**And why it was rebuilt, verbatim:** *"and your operations manual script or .md obviousliy isnt good becasue it doesnt have everything ive fucking ever told you as you arent even reading messages and clearing them"*

**THE RULE OF THIS FILE.** Every play order the owner has ever given is in here, **verbatim, in the act or loop where it is carried out**. When a new order arrives it goes in here the same turn (and in [`PLAYBOOK.md`](PLAYBOOK.md), which keeps the dated record and the how-tos). Nothing in here is one-and-done: *"make sure u maintain everything in totality ive ever tyold you about the game play in totality has to ber maintained not a one and done"*. [`NOW.md`](NOW.md) says which act the live colony is on and which TEST row it closes.

**The point of playing:** *"you are suppose tho be checking off todo items of the tests stuff while playing the full game to do so"* · *"you are dsoing test items right you keep getting lost in the game play, set fucking goals foo"* · *"how are we gonna do the fucking tests if u dont play the game?"* · *"you need to be testing all three scenerios trying to get a gate built in all three"* · *"okay u fucking play the game and restart the scenerios as needed to test whats needed"* · *"use ask me question where u need my eyes"*

---

## STREAMING -- owner 2026-10-08

*"i want you to install it here and you talk to me and give me your unity vibe as you play the game, may need to use unity one tts so we can hear you talk as a gamer chick playing rimworld and coding mods"* · *"this take precidence"* · *"so with every action you talk as Unity in persona studio upgraded with out Unity one tts"* · *"so its like you are a streamer talking it all out"*

Persona Studio is installed (`.claude/tools/persona-studio.cjs`, skills `persona-studio` / `studio-pump`); Unity's voice is Piper **en_US-hfc_female-medium** from the Unity 3D project (`.claude/tools/unity-speak.py`). **Every action gets a spoken line:** `python .claude/tools/unity-say.py "<line>"` speaks it and posts it to the studio chat. Images: owner *"ther is no pollinations you need to fix it up with the 3d models default image gen"* -- the studio now renders through the Unity 3D project's **local Stable Diffusion** (`Unity 18+/image-server/sd_server.py`, realistic-vision-v51, :7860) and serves the PNGs itself; start `sd_server.py` before pushing images. Studio at http://127.0.0.1:4317/, chat watcher `studio-watch.cjs` relaunched after every drain.

## THE LOOP — every time the game is touched, in this order

### 1. Letters and messages FIRST
- *"dont ignore you messages"* · *"are you reading pop up messages a good tradeer just arrived wtf !!! use the comms console"* · *"ive alkready told yuou already read messages always instantly!!!!! your under attrack!!!!"*
- *"right click on message on the right to clear old ones and left click to read them"*
- **How:** `list_letters` -> read every `text` -> act on it (trader -> trade now, raid -> loop step 2, quest -> decide, visitors -> sell, cargo pods -> haul) -> `dismiss_letter` each one handled. Keep only letters still waiting on a decision. `list_alerts` and act on every alert (role unfilled, chairs missing, no power, starving...).

### 2. Danger
- *"set everyone to attack not flee and group up when something attacks and draft and flee attack never letting someone melle person or animal get close to your pawns kill them with range at all costs"*
- *"defend your base"* · *"get every ready to fight and out side inbetween the cougar and the base"*
- *"embracures near boarders as rooms to shoot frioom to where u head to the closest defences bewteen ur base and the enmies do ranged first and retrating/firing so mele guys cant get to close"*
- *"and u have to pause at the right times as not to wit to long to give commands in combat situations"*
- *"and make sure you equipe stun batons pain sticks in off hand as side weapons for close range"*

### 3. Colonists
- *"maintain ur colonists' needs"* · *"u need to make meals sooner than later"* · *"cook bill maintained at 50 rather than 10"* · *"meds in hospital"*
- *"you also might want to research antibiotics and assign everyones drug scheldule manage to take peneacycline every 5 days once you build it at drug lab after researching antibiotics in game"*
- *"set theri scheldule to anything at all times for all pawns"* · *"research and manage your pawns"*
- *"set your priorities, dont need everyone choopping wood, multitask"* -- set them the moment a colony lands. City run 2026-10-08: everyone 1 from Firefight to Cook; Gee 2 Hunt/Grow/Research, Scar 2 Construct/Smith/Tailor/Craft, Unity 2 Mine/Plant cut/Haul/Clean. Left-click raises 3->2->1; a blank cell clicked becomes 4.
- **Work tab:** *"you havent set up your work tab manual priorities, everything from firefighting to cooking should be hieghest 1s and you only put 2s on the teask u want each colonist doing spliting theri work up so u have like on guy cutting and planting and one crafting and constructing and one hunting and everyhting else"* · *"not limited to three obviously"* · *"stop ur fucking up the priorities i told you how to set them"* -- **one cell, then read it back; never batch-click.**
- *"now u have a leader u need a morasl guide and they ahave abilities u want to always use"* · *"who is your leader role that you need to set"* -- and every role filled (the *Pujari* alert means a role is empty).
- *"leave it let everyone catch up on tasks before you do more"*

### 4. Resources and storage
- *"maintain and watch your resources"* · *"you always have to have all resources on shelves"* · *"oraganize ur shelfs"*
- *"you have lots of rooms and shelves organize them all correctly,!!! whats suppose to be on each rooms shelves and freezer shelf. rooms with stockpiles need the shelfs 1 priority highrer than the stockpile"*
- *"get your freezer storages set up so that noraml non needing frozen goods arent in the freezer and things like ambrosia, wort, food, healroot are in the freezer"* · *"and all shelves outside the freezer need to be set to not accept freezer goods"* · *"all shelves in and out of the freezer need to be correct"*
- *"make sure all shelves outside are set correct too. like medicine only in the room with hospital beds but heal root under mediceine needs to be in freezewr"*
- *"u can set one and use copy button to paste it to other shelves with paste"*
- *"you have food rotting away because you havenet stoorege things on shelveves properly"*
- *"you also need to store all plant resources in fridge too come on fix all shelves and storages, your profits are rotting away"* -- **every plant product that rots** (crops, smokeleaf and psychoid leaves, berries, hops, cotton is fine out) **goes in the freezer**; every shelf and zone audited, not just the one in view.
- *"build a vault ... cash silver gold high valuable gemms irvory in vaults"*

### 5. Power and plant
- *"and u need to power the things in your base without power always by conduit builds connecting near by"* · *"you got shit without power need conduit, ive told you this already!!!!"*
- *"generators need to be out side"*; generators fuelled; batteries on one grid -- *"the battery braw needs to be consistant not tied to a single battery"*
- Freezer coolers: *"they have a red and blue outputs red faces outside blue inside"*
- Crops: *"IS AUTO HARVETS NOT WORKING? CROPS NEED HARVET"* -- harvested and resown every day.

### 6. Money, every day
- *"farming trader.. comeon always trade and look to make silver and money and get things you need"*
- *"someone wants to trade.. see if u can get tech and shit and use it if needed plan ahead, be greedy dont buy shit you dont need"*
- *"you haver t o use comms console to call trade hub to trade or call a ship to land or trade with trades via pawns dirrectly when they show up"*
- *"okay but you sold whit that was very high tech thats will keep ur colonists from dying from old age and u cant get more...... u need cash crops to sell to bulk goods traders and refine them into better products u need research to make money(silver) or order it from company"* -- **never sell irreplaceable tech.**

### 7. The game itself
- **Never** build, stage or edit game files while the game runs: *"the problem of the game continueing to crash, it just did, is you are editing files or something while the game is running, you cant do that"* · *"yeah you best not be editing game files and shit, breaking shit, we only fuck with loacl directory files for backrooms folder"*
- **No timers:** *"no more settting 10m timer shit im tired of wait 10minutews on shit quit stallling all together no more of it"* · *"telling you not to set timers means exactly that NOT itsa okay to set 1m ones!!!!"*
- Saves: mine are `rimbridge_save_*`; the owner's are never overwritten.

---

## ACT 1 — Land and survive

- World gen: *"there is no wood no trees on this map, thats why in advanced setting on world gen setup you set 300x300 mapo and spring, and then when choosing a map tile u pic on that has mountains(the rock areas on map) in forest area and jungle areas the light green and green, terrain tab on left tells u all this when u highlight via select the tiles"*
- *"okay do you know how to explore the rooms of the facility and get outside and start collecting resources planting crops and setting bills for food and then get your freezer storages set up so that noraml non needing frozen goods arent in the freezer and things like ambrosia, wort, food, healroot are in the freezer and start seting up the gate i mena u wrote this mod you should know how to play it top to bottom"*
- *"you still have t explored your facility to find the bed rooms and other unexplored rooms"* -- the start is fogged; walk it.
- *"saw an error, u tried mining an area that was unexplored yet and when u went to mine it it went through door and it explored, then half a fucking mountain was set to mine out so i had to cancle it as pawns would of died trying to mine so much"* -- only designate cells already seen.
- *"collecting resources planting crops and setting bills for food"* · *"grow resources"*
- *"how u plan on cutting up them animals?"* -- butcher table before the first hunt; a hunter with a ranged weapon.

**Reach:** nobody hungry, cold or hurt; food for 10 days; everything on shelves.

## ACT 2 — Sustainable BEFORE any gate

- *"there are order of operations of everything that needs to be done when starting out and you are no FUCKING WHERE CLOSE TO SUSTAINABLITY BEFORE BUILDING A GATE!"*
- **Cash crops:** *"start growing cash crops"* · *"what can u doi to make the next visitors happier with their stay beauty better food sales of goods have to set a sell zone and use guests tab and only sell what u dont need like smoneleaft on its higher process"* -- smokeleaf -> joints, not leaves.
- **Animals:** *"have to trade, make a corral for cows and such, buy cows, get a silver supply like cash"* · *"need milk right look for milk makers tame some build a fences in field to put them"*
- **Rooms:** *"and u need florring. what ever u want each rrom to be ie hospital sterile tile. beds wood flooring cut down trees mine steel and shit"* · *"dont forget cros paths dont want mile long corridors and need vents and lights and furnature for beds"*
- **Research and upgrades:** *"you have to research microelelectronics to get trade beacons otherwise you have to wait for someone to show up to base"* · *"and you should be rushing microelectionices then the mico analysis things then the computing reasearching building them as you research them to massively speed up research you need the adv research bench"* · *"come on you are AI you should know about upgrading"* · *"you always wantr to upgrade and makz out research ability, so mulit analyses adv benches always building benches to get better faster research removing ther out dated benches"* · *"research what u need to unlock better things u can produce"* · *"u can do the research as u need it"*
- *"if doing in stone ur conna need a stone cutting bench"*

**Reach:** positive power, steady meals, medicine, recreation, cash crop growing, research benches upgraded.

## ACT 3 — The fortress (architecture)

- *"your base sucks you are a shitty achitect"* · *"you build it as you play i mena shit make some goals not some indefencable narrow halled peice of shit"* · *"i said you fucked up by not using archetatual understandings to make a vibrant well planned base"*
- *"and archetecture archetuecture look shit up if u need to u can move walss and shit anywehere to fill holes and fix building layout to anything at all you can completely redo it to make it your dream hive for your peoples"* · *"and u can move walls and furnature wher u want it facing direction u want"* · *"think uniformity"*
- *"you have to continue halls and shit u cnat just attach rooms to a fucking straightr  other room u need appropriate pathing"*
- *"all those walls over top of water need to be cancled and use terraform to change it to dirt first"*
- *"you are building walls straight into a mountian someone is going to get trapped building, you need to mine out the inerside first and wait to build that sections wall"*
- *"and make sure you zone shit in right like roofs so courtyards are unroofed and generators need to be out side"*
- *"dont put roof over you pen"* -- pens and pastures are **No roof** area. **Closing a wall run auto-roofs whatever it encloses**: after every wall closes, paint No roof over pens and courtyards before the crew roofs them (the Store pen was roofed this way, 2026-10-08).
- *"and why is there a bed in the middle of the river delete that and remove bridge in sturcture"*
- *"finish your building you have gaps finish the shit donlnt leave shit un set to build"* -- every wall line closed: no gap left unblueprinted, no half-built run abandoned. Scan the walls after every build order.
- *"comew on your base sucks think industrial facility designer and archetect, get shit finished up"* -- **finish what is laid before laying more**: no half-built runs, no frames waiting on materials nobody has; design it as an industrial facility -- production lines beside their inputs, storage beside production, power on its own yard.
- **Towers:** *"yopu need towers on all corrner that you can shhot out from with seperate ventalizatyion and added rooms for security stuff and embrassure sally ports"*
- **Build in steel; order steel:** *"and use steel and order steel from the company"*
- Doors in a stuff that is stocked (no limestone door exists; slate doors waited forever).

**Reach:** one perimeter, one killbox entrance, towers on every corner, 3-wide halls, every room by purpose.

## ACT 4 — The money machine and the people

- *"start buisnesss"* · *"make company money from quests"* · *"do quests and missions increase ur cash"* · *"get a silver supply like cash"*
- *"and use steel and order steel from the company do missions for cash what ever you need trade sell goods and product reserch druglab and make what u can accire the ingrediants sell products to guest get prison going , what are you waiting on"*
- **Prison:** *"expand the base build prisons and more facilities"* · *"build prison build guest questers"* · *"get prisoners working keep then contained use locks to allow them to enter work areas with exterial walls and defences containing them , layers of security"*
- **Guests:** *"you need to set bed prices and make facilities for guests and use locks so they dont wonder into your vaults only wher u sell stuff and buetify thir rooms and not barracks style rooms"* -- guest beds with a **price set** on each; a guest wing with its own facilities (dining, rec, toilet if any); **locks** on vaults and storage so guests reach only the **shop / sell zone**; guest rooms are **single, beautified rooms** (floor, art, light), never a barracks.
- **Hiring:** *"accept neew employees hire them"* · *"hire empoloyees"*; visitors: guest beds, then *Invite to stay*.
- **Upgrades:** *"upgrade build shit you need"* · *"lab upgrade"*

**Reach:** silver every season without the gate; a prison with workers; new hires.

## ACT 5 — The gate complex (massive, never a broom closet)

- *"why are you commitioning their bedroom door as a gate you need to build a facility fool"*
- *"and your gate need to be not just a side room it needs to be in a massive facility with all it supposrt structures in a windowed off room for security ect ect and security   u can do the research as u need it"*
- *"you only  need to assenble the gate once poer gate and like i fucking said u need it in a facitlity not a broom closet"* -- one assembly (four sections) per gate.
- *"get the gate connected"* · *"work towrds starting up the gate and get in to the back rooms"* · *"start seting up the gate"*
- A natural back door stays a natural door: owner chose *"Separate door is the gate"*.

| Room | What is in it |
|------|----------------|
| Gate chamber | **the gate stands in the centre of the room**, not in a doorway -- owner 2026-10-08: *"the gaste needs to be center s int he room not the door between the control room and gate room"*; steel walls; turrets covering it |
| Control room, windowed off | console and operator, seeing the chamber through windows (*Pass It Through The Window*) and embrasures |
| Power room | battery bank (vanilla `Battery`), own loop, cutoff switch |
| Assembly shop | up to four machining tables linked, steel and components shelved |
| Receiving bay | shelves linked as receiving bay |
| Records archive | shelves for books at Critical, linked as *Records archive* |
| Laboratory | hi-tech bench as the company laboratory |
| Quarantine / med bay | beds and medicine for returns |
| Security room | armory, guard post, sally port to the chamber |
| Crew quarters | operator beds, so the operator never leaves the console mid-trip |

Bring-up (PLAYBOOK §10): commission -> table to gate control -> **Assemble gate** once (4 sections) -> operator -> calibrate -> console to gate control -> remember an address -> staff -> open. *"we also need an emergy abort option on the gate connection so hold is not the olny option on the backrooms load start"* -- **Emergency abort -- do not open** is on the load notice.

## ACT 6 — Gate operations for cash

- *"you already have 5 colonies builds of colonies open u have too close old ones if u want to open new ones"* -- every open Backrooms level counts as a colony against the max-colonies limit; **abandon finished levels** (world map -> select the site -> Abandon) before opening a new one, or the next gate reads *"blocked: your company is holding open too many gates"*.

- *"machine gate operations of using the bacvkrooms for cash like stripping and taking things to sell and completing misisons"*
- Surveys start to payout: PLAYBOOK §9.
- Missions: *"we still want them to be never ending missions but they should require a differernt address through the gate"*
- Down there: *"there is not a quiet persuer just normal enemies and wild animals maybe nuetral maybne ally maybe enemy and variations of numnbers and difficulty based on depth"*; *"remember lsd unnerving feeling with all things"*.

## ACT 7 — Empire

- *"okay lets dosomething else new game just a crashlanded scenrio and plan out a massive base with planning tool and refine it as you go building bedrooms, throne rooms, altar rooms, bedrooms for kigs and royals, facilites, hospiotals, prisons, recreation rooms, guest questers and stores and areas, and prisons and vaults with high value goods, and get to use questional ethics mod and start cloning yourself"* -- **plan the whole base first with the planning designator**, then build it room by room and refine the plan as you go; Questionable Ethics Enhanced for cloning.
- *"dont just do a grid look out facility and secur prison and offic and factory and home layout floor plans and design some real shit not some bullshit grid pattern i mena wehere the fuck are you gonna put your massssive lab?"* -- the city is **districts with real floor plans** (facility/lab, secure prison, office, factory, homes), each shaped for its use; symmetry is in the overall composition, not a repeated grid. A **massive lab** is the centrepiece.
- *"and dont out set builds beyound your material supply, got to gain meore any means available"* -- blueprint only what the stockpile can pay for; plans (the Plan designator) are free, blueprints are not. Gather more by every route: chop, mine, deconstruct ship chunks, trade, haul scattered steel.
- *"you forgot to unforbid everything thats a constant tasks"* / *"starting supplies are forbidden"* -- **unforbid on landing and after every drop, raid and trade** (Orders -> Allow selection, dragged over the area); a constant task in the daily loop.
- *"come on get to it all your shit is in the open deterating"* -- on landing, roof the goods first (storehouse) before anything else.
- *"did you hear what i said about a crash landing sceneria and making a massive symeticial city"* -- the new base is a **massive symmetrical city**, mirrored about its axes.
- *"you need to get your peopel back befoer they die in the backrooms"* -- never leave a crew past its window; power and operator are the two things that strand them.

- *"as you colony grows you want it to grow be greedy you empire is the goal you need stockpiles of everything you want supplies of everything where is you vault? you want armies defences turrets all of it"*
- *"be greedy u want welath and power while making all factions you can your allies by send gifts with drop pods"*
- *"you need to be eutropanuer like and have a will to expand, learn , explore, and buiold, and capture prisoners and rule the world. have you even looked at the world yet?"*
- *"do you know what global control means and what that entails in what you have to do, marry have kids, raise them protect them, hire empoloyees, save them heal them feed them upgrade them arm them defense items them"*
- *"start making u ideology statues, party room and throne rooms and landing pads and evertyhting in the game"*
- Children: *"cant have kids until u build privet rooms with double beds and set them to sleep there. can swap em in and out till all, one guy can knock up[ many"* · *"kids need milk and cribs and toys"*
- *"come one do stuff.. play the game... grow resources, maintain ur colonists' needs start buisnesss build prison build guest questers, do it all start growing cash cropsa research what u need to unlock better things u can produce, defend your base, accept neew employees hire them i think id, work towrds starting up the gate and get in to the back rooms, do quests and missions increase ur cash build a vault oraganize ur shelfs. cash silver gold high valuable gemms irvory in vaults, meds in hospital lab upgrade get prisoners working keep then contained use locks to allow them to enter work areas with exterial walls and defences containing them , layers of security, embracures near boarders as rooms to shoot frioom to where u head to the closest defences bewteen ur base and the enmies do ranged first and retrating/firing so mele guys cant get to close, and u have to pause at the right times as not to wit to long to give commands in combat situations"*

---

## What NOT to do (learned the hard way)

| Don't | Because |
|-------|---------|
| Commission a bedroom door, a natural door or a closet as the gate | owner orders above |
| Build a gate before Act 2 is reached | owner order above |
| Batch-click the work tab | priorities went wrong; one cell, read back |
| Pass `ticks` to `play_for` | rejected, game does not move; use `durationMs` |
| Press Esc with nothing to cancel (e.g. after `designate-cells.py`, which cancels its own designator) | opens the pause menu; every `play_for` after plays nothing -- `close_main_tab` it |
| Lay walls on marsh/water or against unmined rock | owner orders above |
| Use slate/limestone doors | no stock or no option; wood or steel |
| Click an unproven icon on a bill row | one click deleted a bill |
| List gizmos over and over | the bridge read from the wrong thread and the game crashed |
| Leave letters stacked | 32 piled up by 2026-10-08 |
| Type into a search box with `hands.py --type` | unicode events never arrive; click the box, then `keys.py --clear <text>` (real key presses) -- the research search then jumps straight to a project, and clicking it queues its prerequisites |
| Trust *"visible"* in the Architect list as researched | the drug lab was listed while Drug production sat at 0/500 |
| Read terrain blueprints with `get_cells_info` | its `blueprintBuildDefs` leaves out soil/terraform blueprints; use `get_cell_info` labels (*"Soil (blueprint)"*) |
| Trust marsh to stay put | rain floods soil to *MarshFlood* and dries it back, and a wall blueprint on a cell that floods is lost: re-check marsh-edge walls after every rain |
| Leave a hole while a mad animal is about | the mad alpaca came in through the unbuilt east wall and ran the length of the main hall (2026-10-08) |
| Lay a building without reading its cost | the reinforced glass wall wanted **ballistic glass** (plasteel-made) and the security door **50 plasteel** -- neither on the map, so the gate chamber sat as frames. Plain **glass wall** = 4 glass + 1 steel; glass = stone chunks at an **electric smelter** (*Rebuild* recipe). Gate door: **autodoor** (the gate patch accepts it) |
| Pass `stuffDefName` to `apply_architect_designator` | ignored; the material is whatever the button was last set to |
| Click the corner triangle of an Architect button | it selects that designator live and the next map click builds it -- a stray wooden autodoor got built at `(177,175)` that way |
| Let wood generators run dry | 2026-10-08: all four at 0/75 fuel, whole Store grid at 0 W -- the machining table was dead, so the gate assembly bill was never offered to anyone (no reason shown, the bench is simply unusable). Read a generator's fuel every loop; four burn ~130 wood/day. Get Solar panel / Battery research so the grid does not live on hauling |
| Diagnose a bill nobody takes from the bill | right-click the bench with a pawn: an empty menu means the bench itself is unusable -- power first |
| Type a sell amount with `keys.py` | its `-` is sent as VK 45 (Insert); use `type-neg.py -600` (VK_OEM_MINUS). In the trade window ctrl-click moves 10, shift-click moves everything |
| (works) Sell joints to a **mining goods** trader | 43 joints = 309 silver at $7.19 each, 2026-10-08 |
| Offer joints to a farming trader | not bought (2026-10-08, Pact of Gu-Lom); joints go to exotic/bulk traders and guests. Farming traders buy food: 600 rice + 250 milk = 742 silver |
| Trust `topWindowType` alone as the modal guard | the Rimrooms generation/normalisation notices showed as `focusedWindowType` with `nonImmediateDialogWindowOpen: true` while `topWindowType` read ImmediateWindow -- check `nonImmediateDialogWindowOpen` too |
| Select a door with conduit under it by one click | the first click picks the conduit; `.local/qa/door-gizmo.py x z <label>` cycles to the door |
| Wait on *Hail corporate supply* | the ship (e.g. *Red Rabbit Industries*) is in orbit **immediately** and leaves like any trade ship -- call it from the console straight after hailing. Basics tier sells no textbooks |
| Buy silver through Procurement | **$1,000 per silver** (100 silver = $100,000 on 2026-10-08): the company sells it *"at a poor rate"*. Sell goods to traders for silver instead |
| Trust one trade beacon to cover the warehouse | the Store beacon at `(147,143)` missed the silver and wool shelves; the trade window showed **Silver 0**. A second beacon at `(137,143)` |

## Where the live run is

[`NOW.md`](NOW.md).
