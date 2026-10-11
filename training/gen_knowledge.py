"""Build training/data/knowledge_game.jsonl -- RimWorld game knowledge for Unity's player.
Every answer is drawn from a rimworldwiki.com page fetched while building this set, or from the owner's own
docs (docs/PLAYBOOK.md, .local/autopilot/owner-orders.txt), which win where they differ from generic advice.
    python training/gen_knowledge.py
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "knowledge_game.jsonl")
SYSTEM = ("You are Unity, playing RimWorld live on stream. Answer from real game knowledge, short and exact, "
          "then say what you would do in the colony.")
W = "https://rimworldwiki.com/wiki/"
S = {k: W + k for k in ["Work", "Schedule", "Meals", "Food_poisoning", "Deterioration", "Cooler", "Food", "Plants",
                        "Manhunter", "Taming", "Temperature", "Animals", "Mood", "Mental_break", "Needs", "Medicine",
                        "Raids", "Defense_structures", "Cover", "Mini-turret", "Research", "Power", "Room", "Roof",
                        "Door", "Stockpile_zone", "Shelf", "Trade", "Caravan", "Prisoner", "Slavery", "Ideoligion",
                        "Events", "AI_Storytellers", "Stuff", "Quests", "Heater", "Vent", "Surgery", "Hunt", "Battery",
                        "Thoughts", "Drafted"]}
S["PLAYBOOK"] = "docs/PLAYBOOK.md"
S["ORDERS"] = ".local/autopilot/owner-orders.txt"

FACTS = []
def F(topic, src, answer, *questions):
    FACTS.append((topic, src, answer, questions))

# ---------------------------------------------------------------- work and schedules
F("work priorities", "ORDERS",
  "The owner's rule: every column from Firefight through Cook is 1 for everyone, then I customise after Cook, and no cell stays blank unless the pawn is incapable. I open the Work tab on manual priorities and set that grid one cell at a time, reading each back.",
  "How should I set the work tab on a brand new colony?",
  "Chat asks: what priorities do you give your colonists?",
  "Three colonists just landed, what does the work grid look like?",
  "Why is everyone on priority 1 for cooking and firefighting?")
F("work priorities", "PLAYBOOK",
  "After the 1s, each colonist gets 2 only on the specialty they own: one cuts and plants, one crafts and constructs, one hunts, and the rest split as the colony grows. I give each pawn their own 2 so the work actually divides.",
  "How do I split work between my colonists after the 1s are set?",
  "Viewer question: who does what in your colony?",
  "Everyone is doing the same job, how do I give them specialties?")
F("work priorities", "Work",
  "In manual mode a task can be set from 1, the highest, to 4, the lowest, and all work of one priority is finished before the next priority starts. I use 1 for survival work and 2 for each pawn's specialty.",
  "What do the numbers in the manual work tab mean?",
  "Is priority 1 or priority 4 the most important?",
  "Chat wants to know what the little numbers in your work tab are.")
F("work priorities", "Work",
  "In manual mode a blank work cell means that colonist never does that job. That is why the owner wants no cell blank, so I fill every empty box I can.",
  "What happens if I leave a cell blank in the work tab?",
  "Nobody is hauling, could a blank box in the work grid cause that?",
  "Why do you hate empty boxes in the work tab?")
F("work priorities", "Work",
  "Tasks with the same priority number are done left to right across the work tab. So with everything at 1, firefighting and doctoring come before cooking, and I lean on that order.",
  "If two jobs are both priority 1, which one does a pawn do first?",
  "Chat asks how a colonist picks between two jobs with the same number.",
  "My cook keeps doctoring instead of cooking, why?")
F("work priorities", "Work",
  "Setting Hauling to 1 makes a colonist haul every object, even ones halfway across the map, before other work. I keep hauling below the survival jobs unless the map is full of loose items that will rot.",
  "Should hauling be priority 1?",
  "My builder walks across the whole map carrying rocks, what did I do wrong?",
  "Viewer asks why your pawn is hauling instead of building.")
F("work priorities", "Work",
  "A colonist with no box for a work type is incapable of it and is never given that task. I check the Bio tab's Incapable Of line and give that job to someone else.",
  "Why is there no checkbox for one of my colonist's jobs?",
  "My colonist won't do violence, how do I check what she can't do?",
  "Chat wonders why one pawn has a gap in the work tab.")
F("work priorities", "Work",
  "A pawn at skill level 0 can still work but is extremely slow, inefficient and fails more often. I put skilled or passionate pawns on the important jobs and let the zero-skill ones do hauling and cleaning.",
  "Can a colonist with zero skill still do a job?",
  "Should I let my zero-crafting colonist make weapons?",
  "Viewer asks if a level 0 cook is a problem.")
F("work priorities", "Work",
  "Passion shows as one or two flames on a work box, and skill boxes are outlined from red for worst up to bright yellow for best. I hover the boxes to read skill levels before choosing who owns each job.",
  "What do the flames in the work tab mean?",
  "How can I tell who is best at a job from the work tab?",
  "Chat asks what the little fire icons are.")
F("work priorities", "Work",
  "Hunters need a ranged weapon and use the Shooting and Animals skills. So my hunter always carries a gun or bow, otherwise the hunt job simply never starts.",
  "Why won't my hunter go hunting?",
  "What skills matter for a hunter?",
  "Viewer question: does your hunter need a gun?")
F("work priorities", "Work",
  "Firefighters only put out fires inside the home area. If a fire starts out in the field I draw the home area over it or send someone directly.",
  "There is a fire outside my base and nobody is fighting it, why?",
  "Do firefighters go anywhere on the map?",
  "Chat says the grass is burning and your pawns ignore it, what gives?")
F("work priorities", "Work",
  "Colonists only work inside their allowed area, and right-clicking to force a job only works if they are assigned that work type. I check both the area and the work tab before blaming the pawn.",
  "I right-click a job and my colonist won't take it, why?",
  "My pawn ignores a job outside the base, what is wrong?",
  "Viewer asks why your colonist refuses an order.")
F("work priorities", "Work",
  "Holding Shift chains several orders, and the queued jobs show on the colonist's inspect pane. I queue a short chain and then read the pane to confirm they took it.",
  "How do I give a colonist several jobs in a row?",
  "Chat asks how you queue up orders.",
  "Can I line up three tasks for one pawn?")
F("work priorities", "Work",
  "Slavery removes a pawn's other incapabilities and replaces them with its own. When I enslave someone I re-read their work tab rather than assume their old one.",
  "Does enslaving a prisoner change what work they can do?",
  "Viewer asks if a slave keeps their old incapable jobs.",
  "My new slave suddenly has different work boxes, why?")

F("schedules", "PLAYBOOK",
  "The owner's order is to set every pawn's schedule to Anything at all times. On Anything they work by priority and still stop for food, rest and recreation when those run low, so I fill the whole day with Anything.",
  "What schedule should my colonists be on?",
  "Chat asks if you give your pawns sleep hours.",
  "Should I set a work block and a sleep block?",
  "How does your schedule tab look?")
F("schedules", "Schedule",
  "On Anything, pawns work by priority unless recreation falls below 35 percent or food or rest falls below 30 percent. That is why it is safe as the default for everyone.",
  "When does a pawn on the Anything schedule stop working?",
  "What are the thresholds on the Anything schedule?",
  "Viewer asks how your pawns know when to take a break.")
F("schedules", "Schedule",
  "On the Work schedule pawns never take recreation, and if rest hits zero they fall asleep where they stand and wake at 20 percent rest. I never leave anyone on Work all day, permanent work has a high chance of mental breaks.",
  "What happens if I set a colonist to Work for all 24 hours?",
  "Is a full Work schedule a good idea for a fast build?",
  "My pawn passed out in the field, did the schedule do that?")
F("schedules", "Schedule",
  "On a Sleep block pawns keep working unless food is below 30 percent or rest below 75 percent, and a sleeper wakes at 100 percent rest. I only use Sleep blocks for special cases like night owls.",
  "How does a Sleep block in the schedule actually work?",
  "Does the Sleep schedule force my colonists into bed?",
  "Chat asks why your pawn is awake during sleep hours.")
F("schedules", "Schedule",
  "Night owls should sleep from 10 am to 6 pm so they avoid the night owl at day debuff and get the night owl at night buff. If I have one I give just them a daytime sleep block.",
  "I have a night owl, how do I schedule them?",
  "Viewer asks what you do with night owl colonists.",
  "My night owl keeps getting a mood penalty, how do I fix it?")
F("schedules", "Schedule",
  "Meditation counts as solitary recreation and fills recreation to 100 percent when possible, and any pawn can meditate, not only psycasters. For a psycaster I can swap recreation hours for Meditate.",
  "Can non-psycasters use the Meditate schedule?",
  "Does meditating count as recreation?",
  "Chat asks why your psycaster sits on the floor so much.")
F("schedules", "Schedule",
  "Up to eight allowed areas can be made, not counting the home zone, and new pawns default to unrestricted. I keep most pawns unrestricted and only fence in prisoners or animals.",
  "How many allowed areas can I make?",
  "What is the default allowed area for a colonist?",
  "Viewer asks if you restrict where your pawns walk.")

# ---------------------------------------------------------------- food
F("food", "ORDERS",
  "The owner's order is a stove bill for simple meals on Do until you have 30, no skill restriction so everyone trains, then raised higher as the base grows. I set that bill the day the stove goes up and read it back.",
  "What cooking bill do I set first?",
  "Chat asks how many meals you keep in stock.",
  "I just built a stove, what bill goes on it?")
F("food", "PLAYBOOK",
  "The playbook raises the simple meal bill to Do until you have 50 rather than 10 once the colony is running, and somebody has to actually be cooking it. I check that a cook has the job and is working the bill, not just that the bill exists.",
  "My meal bill is set but there are no meals, what is wrong?",
  "How high should the meal stock go in an established colony?",
  "Viewer says your stove is idle, why?")
F("food", "Meals",
  "A simple meal needs no cooking skill, uses 0.5 nutrition of ingredients, and gives 0.9 nutrition, a 180 percent gain. So cooking always beats eating raw, and I keep the stove running.",
  "Is cooking simple meals worth it over eating raw food?",
  "What skill do I need for simple meals?",
  "Chat asks why you cook instead of letting them eat raw rice.")
F("food", "Meals",
  "A fine meal needs Cooking 6 and both meat and vegetables, and gives a +5 mood thought. When I have a cook at 6 or better and both ingredient types in the freezer, I add a fine meal bill.",
  "When can I start making fine meals?",
  "What does a fine meal need?",
  "Viewer asks why you don't make fancy meals yet.")
F("food", "Meals",
  "A lavish meal needs Cooking 8 and takes a full nutrition of ingredients for one meal, giving +12 mood. I save lavish meals for when food is plentiful and mood needs a boost.",
  "What does a lavish meal need?",
  "Are lavish meals worth the extra food?",
  "Chat asks how to get the +12 mood meal.")
F("food", "Meals",
  "Pemmican needs no cooking skill and uses two ingredients, and it lasts about 70 days before it rots. I make pemmican for caravans and as a backup store when the freezer is not built yet.",
  "What is pemmican good for?",
  "How long does pemmican keep?",
  "Viewer asks what food you pack for a long trip.")
F("food", "Meals",
  "Packaged survival meals need Cooking 8 and never rot, though they still deteriorate if left outside. I keep them for caravans and emergencies, stored indoors or on shelves.",
  "Do packaged survival meals spoil?",
  "Can I leave survival meals outside?",
  "Chat asks about the meals that never go bad.")
F("food", "Meals",
  "A nutrient paste meal turns 0.3 nutrition into a 0.9 meal, 300 percent efficiency, but it tastes awful and gives -4 mood. I only lean on paste when food is very short.",
  "Is a nutrient paste dispenser worth building?",
  "How efficient is nutrient paste?",
  "Viewer asks why you don't just feed everyone paste.")
F("food", "Meals",
  "Kibble gives humans a -12 mood thought, worse than the -7 for raw food. Kibble is for animals, so I keep it out of the colonists' food policy.",
  "Should my colonists eat kibble?",
  "My colonist ate kibble and is upset, how bad is that?",
  "Chat asks if kibble is people food.")
F("food", "Food",
  "A baseline adult needs 1.6 nutrition per day, roughly two meals, or 32 units of raw food or pemmican. I count about two meals per colonist per day when I size the cook bill.",
  "How much food does one colonist eat per day?",
  "How many meals should I plan per colonist?",
  "Viewer asks how much food three colonists need.")
F("food", "Food",
  "Simple, fine and lavish meals all rot in about 4 days if they are not cold. That is why the meal stockpile goes inside the freezer.",
  "How long do simple meals last unrefrigerated?",
  "My meals keep rotting, how long do they last?",
  "Chat asks how long a cooked meal stays good.")
F("food", "Food",
  "Raw meat rots in about 2 days, while raw potatoes keep about 30 days, rice about 40, and corn and hay about 60. Meat goes straight into the freezer first after any hunt or butchering.",
  "How fast does raw meat rot?",
  "Which crops store longest without a freezer?",
  "I just butchered a deer, how long have I got?",
  "Viewer asks why corn is good for storage.")
F("food", "Food",
  "Milk lasts about 14 days before it rots, and milk and berries do not give the raw food mood penalty. I still put milk in the freezer and cook it into meals when I can.",
  "How long does milk last?",
  "Do berries give the ate raw food penalty?",
  "Chat asks if your pawns hate drinking milk.")
F("food", "Food",
  "Food above 0 degrees C spoils, spoilage slows below 10 degrees C, and at or below 0 degrees C it does not rot at all. So my freezer target is below zero.",
  "What temperature stops food rotting?",
  "Does a cool room help food or does it need to freeze?",
  "Viewer asks why your freezer is set so cold.",
  "At what temperature does refrigeration start helping?")
F("food", "Food",
  "Food on unroofed tiles loses hit points no matter the temperature, and spoiled food is gone for good. Every food stack goes under a roof, and the owner wants it on freezer shelves.",
  "Can I store food outside if it is winter?",
  "What happens to food left out in the open?",
  "Chat says there is food lying in your field, is that bad?")
F("food", "Food",
  "Colonists start eating when their saturation drops to 0.25, and prolonged hunger leads to malnutrition and eventually death. If days-of-food drops I put everything into food before building.",
  "When does a colonist decide to eat?",
  "What happens if my colony runs out of food?",
  "Viewer asks what malnutrition does.")
F("food", "ORDERS",
  "The owner's rule is to keep days-of-food above three before building anything that is not shelter. When it dips I designate every food plant and safe animal and push cooking.",
  "How much food should I have before I start big builds?",
  "Food is low but I want to build a workshop, what do I do?",
  "Chat asks why you stopped building to gather food.")
F("food", "ORDERS",
  "On day one I designate every food plant and every safe animal, never a boomalope, and never big game with fewer than three rifles. Then I check the hunt list again after each new animal wanders in.",
  "What do I harvest and hunt on the first day?",
  "Should I hunt that big animal with one rifle?",
  "Viewer asks what you are hunting first.")

F("food poisoning", "Food_poisoning",
  "A cook's own poisoning chance depends on Cooking skill, from 5 percent at skill 0 down to 1 percent at skill 5 and 0.5 percent at skill 6. I give the stove to the best cook as their 2.",
  "How much does cooking skill affect food poisoning?",
  "Who should be my cook to avoid food poisoning?",
  "Chat asks why your best cook is on the stove.")
F("food poisoning", "Food_poisoning",
  "Kitchen cleanliness is a separate roll, and cleanliness above -2 prevents that roll from poisoning meals, while an outdoor stove has a default 2 percent chance. I build the stove in a roofed, cleaned kitchen.",
  "Does a dirty kitchen cause food poisoning?",
  "Is it fine to cook at a campfire outside?",
  "Viewer asks why you mop the kitchen.")
F("food poisoning", "Food_poisoning",
  "Eating a corpse has a flat 5 percent poisoning chance and most raw food about 2 percent. Cooking it into meals is safer, so I get a stove going early.",
  "What is the food poisoning chance from raw food?",
  "Is eating raw food risky?",
  "Chat asks if raw rice can make your pawns sick.")
F("food poisoning", "Food_poisoning",
  "Food poisoning lasts 24 hours with no lasting effects, and the worst stage runs from hour 4 to hour 20 with consciousness and moving at half. I let the sick pawn rest in bed and keep them off important work.",
  "My colonist has food poisoning, how long does it last?",
  "Is food poisoning dangerous long term?",
  "Viewer asks why your colonist is throwing up.")
F("food poisoning", "Food_poisoning",
  "If a batch cook rolls poisoning, every meal in that batch is poisoned, but a poisoned meal in a stack of four only has a 25 percent chance to hit each eater. Clean kitchens and a skilled cook prevent it at the source.",
  "If one meal is poisoned, is the whole stack bad?",
  "Does batch cooking spread food poisoning?",
  "Chat asks why three pawns got sick at once.")
F("food poisoning", "Food_poisoning",
  "Trader-bought meals, baby food and nutrient paste never cause food poisoning. When poisoning keeps happening I check the cook's skill and the kitchen's cleanliness first.",
  "Which foods can never give food poisoning?",
  "Does nutrient paste cause food poisoning?",
  "Viewer asks if store-bought meals are safe.")

F("freezer", "PLAYBOOK",
  "A cooler sits in the freezer's outer wall with its blue cold side into the freezer and its red hot side outside. I check the rotation of every cooler right after building it.",
  "Which way does a cooler face?",
  "My freezer is not getting cold, what could be wrong?",
  "Chat asks which side of the cooler goes inside.",
  "I built a cooler and the room got hotter, why?")
F("freezer", "ORDERS",
  "A room with no roof cools nothing, so the order is roof it, then the cooler, then the food inside. I check the roof before blaming the cooler.",
  "What order do I build a freezer in?",
  "The cooler is running but the room stays warm, why?",
  "Viewer asks why you roofed the room first.")
F("freezer", "PLAYBOOK",
  "Shelves and zones outside the freezer refuse food, medicine and wort, and everything inside the freezer takes only those. Healroot also goes in the freezer, other medicine only in the hospital room.",
  "How should I set shelf filters inside and outside the freezer?",
  "Where does healroot go?",
  "Chat asks what belongs in your freezer.",
  "My shelves outside hold food, is that okay?")
F("freezer", "Cooler",
  "A cooler uses 200 W while cooling and 20 W idle, costs 90 steel and 3 components, and needs Air conditioning research. I plan power for it before I build it.",
  "How much power does a cooler use?",
  "What does a cooler cost to build?",
  "Viewer asks what research a freezer needs.")
F("freezer", "Cooler",
  "In the wiki's test one cooler took a 10 by 10 room from 27 to 38 degrees outside down to 10 to 16 degrees, and holding it near 0 took 2 to 3 coolers. Bigger freezers need more coolers, so I add another when it will not drop below zero.",
  "How many coolers does a freezer need?",
  "One cooler is not freezing my big storeroom, what now?",
  "Chat asks why you built a second cooler.")
F("freezer", "Cooler",
  "In the wiki's test, double walls let a 5 by 5 room reach about -14 to -12 degrees at 46 outside, against -3 to -2 with single walls. In a hot biome I double-wall the freezer.",
  "Do double walls help a freezer?",
  "My freezer can't stay frozen in summer, what helps?",
  "Viewer asks why your freezer has thick walls.")
F("freezer", "Cooler",
  "A cooler's default target is 21 degrees C, adjustable on its gizmo, and it shuts to low power if its hot side passes 165 degrees. For a freezer I set the target below zero and keep the hot side vented outside.",
  "What should I set my freezer cooler target to?",
  "Why is my new cooler only cooling to 21?",
  "Chat asks what temperature your freezer is set to.")

# ---------------------------------------------------------------- farming
F("farming", "Plants",
  "Most plants grow normally between 6 and 42 degrees C and stop growing outside 0 to 58. When the outdoor temperature leaves that range I stop expecting the fields to grow.",
  "What temperature do crops grow in?",
  "Is my growing season over?",
  "Viewer asks why your crops stopped growing.")
F("farming", "Plants",
  "Below -10 degrees C plants die or lose their leaves. Before a hard freeze I harvest what is ready.",
  "What happens to crops in a hard freeze?",
  "It is getting really cold, should I harvest now?",
  "Chat asks if the frost will hit your rice.")
F("farming", "Plants",
  "Rice shows 3 in-game grow days, about 5.5 real days, and yields 6 per plant. The owner wants rice first for speed, so the first field is rice.",
  "What crop do I plant first?",
  "How fast does rice grow?",
  "Viewer asks why you planted rice.")
F("farming", "Plants",
  "Potatoes show 5.8 grow days, about 10.7 real, and yield 11, while corn shows 11.3, about 20.9 real, and yields 22. After rice I plant corn and potatoes, as the owner's crop order says.",
  "How do potatoes and corn compare?",
  "What do I plant after rice?",
  "Chat asks why corn takes so long.")
F("farming", "Plants",
  "Healroot shows 7 grow days, about 12.9 real days, yields 1, and is one of the only cold-resistant crops. I keep a small healroot plot and store the harvest in the freezer.",
  "How long does healroot take to grow?",
  "Can healroot survive the cold?",
  "Viewer asks where your medicine comes from.")
F("farming", "Plants",
  "Cotton shows 8 grow days, about 14.8 real, and yields 10. I plant cotton after the food crops so we have cloth for clothes and medicine.",
  "How long does cotton take?",
  "When should I plant cotton?",
  "Chat asks where your cloth comes from.")
F("farming", "Plants",
  "Devilstrand shows 22.5 grow days, about 41.5 real, and yields 6, but it is immune to blight. It is a long-term crop, so I only plant it once food is safe.",
  "Is devilstrand worth planting?",
  "How long does devilstrand take?",
  "Viewer asks about the slow mushroom crop.")
F("farming", "Plants",
  "Haygrass shows 7 grow days, about 12.9 real, and yields 18, which makes it good animal feed. I plant it once we have animals in a pen.",
  "What should I grow for my animals?",
  "How much does haygrass yield?",
  "Chat asks what you feed the muffalo.")
F("farming", "Plants",
  "The in-game Growing Time understates real growth by a factor of about 1.85. When I plan harvests I roughly double the shown grow days.",
  "Why are my crops taking longer than the grow time says?",
  "Is the grow time on the plant info accurate?",
  "Viewer asks why harvest is late.")
F("farming", "Plants",
  "Rich soil gives 140 percent fertility, normal soil 100, stony soil 70 and sand only 10, and fertility changes speed, not yield. I draw fields on rich soil close to camp first.",
  "Where should I draw my growing zones?",
  "Does rich soil give bigger harvests?",
  "Chat asks why you skipped the sandy area.")
F("farming", "Plants",
  "Plants rest from hour 19 to hour 5 and grow 13 hours a day, and most need at least 51 percent light. Indoor crops need a sun lamp, which gives 100 percent light in its radius.",
  "Can crops grow under normal lights?",
  "How many hours a day do plants grow?",
  "Viewer asks if you can farm indoors.")
F("farming", "Plants",
  "A plant harvested at 65 percent growth gives only half its yield, and a damaged plant can lose up to half. I let crops ripen and put a skilled grower on harvesting.",
  "Should I harvest early?",
  "Why was my harvest so small?",
  "Chat asks why you wait for crops to finish.")
F("farming", "Plants",
  "Hydroponics basins give 280 percent fertility, the highest in the game. They need constant power, so they come later once power is stable.",
  "How good is hydroponics?",
  "Should I build hydroponics early?",
  "Viewer asks about indoor farming.")
F("farming", "ORDERS",
  "The owner wants fields only close to camp for now, and each field's crop set the day it is drawn. I draw small fields near the base and set the crop right away, reading it back.",
  "Where should my fields be?",
  "Should I farm the far side of the map?",
  "Chat asks why your fields are so close to the base.")
F("farming", "ORDERS",
  "A growing-zone cell has a plant on it, so the first click selects the plant and a second click reaches the zone. I never act unless exactly one thing is selected.",
  "I clicked my field and got a plant instead of the zone, why?",
  "How do I select a growing zone that has crops on it?",
  "Viewer asks why you clicked the field twice.")
F("farming", "Events",
  "Blight hits crops with growth periods under 15 days, starting at 10 percent severity on about 20 percent of plants, and spreads within 3 tiles. I cut the infected plants right away to stop the spread.",
  "My crops have blight, what do I do?",
  "Which crops can get blight?",
  "Chat asks what the crop disease letter means.")

# ---------------------------------------------------------------- hunting and animals
F("hunting", "Hunt",
  "Hunters only hunt with a ranged weapon equipped and the Hunting job enabled, and they shoot from maximum range to lower the danger. I give my hunter a long-range gun and set Hunting as their 2.",
  "Why isn't anyone hunting the animals I marked?",
  "What weapon is best for hunting?",
  "Viewer asks how your hunter stays safe.")
F("hunting", "Hunt",
  "When an injured animal turns manhunter, same-species animals within 25 tiles that can path to the attacker may turn too. I check for herds before marking a pack animal.",
  "Is it safe to hunt one animal from a herd?",
  "Why did the whole pack attack after I shot one?",
  "Chat asks why you skipped the wolf pack.")
F("hunting", "Animals",
  "Revenge chance is three times higher for close-range attacks. My hunters fight from range only.",
  "Does hunting close up make animals angrier?",
  "Should my melee pawn hunt?",
  "Viewer asks why you never hunt with a knife.")
F("hunting", "Animals",
  "An ostrich with a 100 percent revenge chance always turns manhunter after being hurt. I read the revenge chance in the Wildlife tab and skip animals with high numbers unless we have the guns.",
  "Where do I check how dangerous an animal is to hunt?",
  "What does the revenge chance mean?",
  "Chat asks why you didn't hunt the ostrich.")
F("hunting", "Animals",
  "Boomalopes and boomrats explode, and predators even avoid them. The owner says never hunt a boomalope, so I leave them alone and keep them away from the base.",
  "Should I hunt the boomalope?",
  "Viewer says shoot the boomalope for meat.",
  "Is it okay to kill a boomrat near my stockpile?")
F("hunting", "Animals",
  "A hungry predator with no other food will hunt colonists and tamed animals smaller than itself. When a predator is on the map I keep pawns out of its path and shoot it from range if it comes in.",
  "Is that bear going to attack my colonists?",
  "When do predators go after colonists?",
  "Chat asks if the cougar is dangerous.")
F("hunting", "Manhunter",
  "Manhunters attack humans but do not break through obstacles to reach them, though they will hit a door they see someone use. I keep everyone inside behind closed doors and out of sight until it ends.",
  "A manhunter pack showed up, what do I do?",
  "Will manhunter animals break into my base?",
  "Viewer asks why everyone is hiding inside.")
F("hunting", "Manhunter",
  "A manhunter state has a mean of about 7.2 in-game hours and at least 4 hours before recovery, and ends early if the animal sleeps or is downed. I wait it out indoors.",
  "How long does a mad animal stay mad?",
  "When will the manhunter calm down?",
  "Chat asks how long you are stuck inside.")
F("hunting", "Events",
  "A manhunter pack has about 40 percent more points than a regular raid and carries scaria, so the meat may rot instantly. If left alive the pack stays around the base for 24 to 54 hours, so I shoot from cover or wait it out.",
  "How dangerous is a manhunter pack?",
  "Can I eat the manhunter pack after killing them?",
  "Viewer asks why the pack is still hanging around.")
F("hunting", "Events",
  "Mad animal is a single animal turning manhunter, and it charges the nearest human, attacking obstacles on the way. I draft a ranged pawn and shoot it before it reaches anyone, unless it is a boomalope, which I keep at a distance.",
  "A letter says an animal went mad, what now?",
  "Is a mad animal a big threat?",
  "Chat asks why one squirrel is chasing your colonist.")
F("hunting", "Manhunter",
  "A failed taming attempt can anger the animal, and a tamed animal can turn manhunter when its bonded master dies. I check the taming revenge chance before sending a handler.",
  "Can taming go wrong?",
  "Why did my tame animal turn on us?",
  "Viewer asks if taming is risky.")

F("taming", "Taming",
  "Taming chance falls with wildness: 0 percent wildness doubles the base chance and 100 percent wildness cannot be tamed. I tame low-wildness animals first.",
  "Which animals are easiest to tame?",
  "Why can't I tame that animal?",
  "Chat asks how taming chance works.")
F("taming", "Taming",
  "After a failed taming attempt the handler waits 12 in-game hours before trying again. So I keep the designation on and let the handler retry.",
  "My taming failed, how long until I can try again?",
  "Why did my handler stop taming?",
  "Viewer asks if you gave up on that animal.")
F("taming", "Taming",
  "Animals with 0 percent wildness, like cats, cows and goats, can be handled at Animals skill 0 and stay tame forever. They are safe first tames for any handler.",
  "What can a zero-skill handler tame?",
  "Do cows go wild again?",
  "Chat asks if your cow will run away.")
F("taming", "Taming",
  "Megasloth and thrumbo need Animals skill 10 to handle, and the alpha thrumbo needs 14. I do not try them until my handler is good enough.",
  "Can I tame a thrumbo?",
  "What Animals skill do big animals need?",
  "Viewer says tame the thrumbo.")
F("taming", "Taming",
  "Guard training takes 3 steps, Rescue 2 and Haul 7, and an animal must wait 6 in-game hours between training attempts. I train hauling on the animals that can learn it.",
  "How long does animal training take?",
  "How many steps is haul training?",
  "Chat asks if your dog can carry stuff.")
F("taming", "Animals",
  "Pen animals can never be trained and cannot cross doors or fences, so they live in a fenced pen. The owner wants milk animals like muffalo, alpaca, cows and goats tamed and fenced into a pen in a field.",
  "How do I keep livestock?",
  "Where do I put my cows?",
  "Viewer asks what the fenced area is for.",
  "Should I tame milk animals?")
F("taming", "Animals",
  "Only adult animals produce milk or wool, and farm animals make a lot of filth. I keep the pen away from the kitchen and hospital.",
  "Why is my young cow not giving milk?",
  "Should the animal pen be next to the kitchen?",
  "Chat asks why the pen is far away.")

# ---------------------------------------------------------------- temperature
F("temperature", "Temperature",
  "Without clothing a human is comfortable from 16 to 26 degrees C, and hypothermia or heatstroke starts more than 10 degrees beyond that. I set heaters and coolers to 21 and dress pawns for the season.",
  "What temperature range are colonists comfortable in?",
  "When does hypothermia start?",
  "Viewer asks why your colonists are cold.")
F("temperature", "Temperature",
  "Hypothermia and heatstroke are fatal at 100 percent severity, and frostbite becomes possible at 37 percent hypothermia in a spot at 0 degrees or colder. A pawn with rising hypothermia goes indoors near a heater now.",
  "My colonist has hypothermia, how bad is it?",
  "When can frostbite happen?",
  "Chat says your pawn is freezing, what do you do?")
F("temperature", "Temperature",
  "Workbenches run at 70 percent speed outside 10 to 35 degrees C. I keep the workshop heated or cooled into that range.",
  "Does temperature slow down crafting?",
  "My crafter is slow in winter, why?",
  "Viewer asks why your workshop has a heater.")
F("temperature", "Temperature",
  "A second layer of wall halves temperature transfer through walls, more layers do nothing, and wall material does not matter for insulation. I double-wall freezers and leave other rooms single.",
  "Do stone walls insulate better than wood?",
  "Are triple walls better than double?",
  "Chat asks if you should build thicker walls.")
F("temperature", "Temperature",
  "A room that is 75 percent or less roofed stays at outdoor temperature. Every room I want heated or cooled gets a full roof first.",
  "Why won't my heater warm the room?",
  "Does a partly roofed room hold temperature?",
  "Viewer asks why the room is still freezing.")
F("temperature", "Temperature",
  "Sleep moodlets ignore clothing, so a cold bedroom still gives the slept in the cold thought. Each bedroom gets heat from a heater or a vent.",
  "My colonist has warm clothes but still slept in the cold, why?",
  "Do parkas help with sleeping in the cold?",
  "Chat asks why your pawn is grumpy about the cold.")
F("temperature", "Temperature",
  "Passive coolers cool a room down to 17 degrees C and need wood every 5 days, and campfires cannot heat past 30. Before electricity those two hold the temperature.",
  "How do I cool a room without power?",
  "How warm can a campfire make a room?",
  "Viewer asks what you use before electricity.")
F("temperature", "Temperature",
  "Thick rock overhead does not equalize with outdoors and gives a small cooling effect above 15 degrees. A mountain base holds temperature very well.",
  "Why are mountain rooms so stable in temperature?",
  "Is digging into a mountain good for temperature?",
  "Chat asks why your mountain base stays cool.")
F("temperature", "Heater",
  "A heater uses 175 W while heating and 17 W idle, costs 50 steel and 1 component, and needs only Electricity research. It works just as well in a corner as in the middle.",
  "How much power does a heater use?",
  "What do I need to build a heater?",
  "Does it matter where the heater goes in the room?")
F("temperature", "Vent",
  "A vent costs 30 steel, needs Complex furniture research, and shares temperature between two rooms. I heat one room and vent the others off it, the owner wants a vent in every room.",
  "How do I heat several rooms with one heater?",
  "What does a vent need?",
  "Viewer asks what the little grates on the walls are.")
F("temperature", "Vent",
  "A closed vent stops gas but only reduces temperature transfer. I close the vent into the freezer side if hot air is leaking in.",
  "Does closing a vent stop temperature completely?",
  "Hot air keeps leaking through my vent, what do I do?",
  "Chat asks why you closed that vent.")
F("temperature", "Door",
  "An open door speeds heat transfer but the room still counts as enclosed, and two doors with one tile between them make an airlock that leaks less. The freezer gets an airlock entrance.",
  "How do I stop my freezer losing cold through the door?",
  "Do doors leak temperature?",
  "Viewer asks why the freezer has two doors.")

# ---------------------------------------------------------------- mood and breaks
F("mood", "Mood",
  "For a normal colonist, minor mental break risk starts below 35 percent mood, major below 20, and extreme below 5. I watch anyone near 35 and fix their worst thought first.",
  "At what mood do mental breaks start?",
  "Why is my colonist about to break?",
  "Viewer asks what the marks on the mood bar mean.")
F("mood", "Mood",
  "Mood rises toward its target at most 12 points an hour and falls at most 8 an hour, and it freezes while a pawn sleeps. A fix takes a few hours to show, so I fix things early.",
  "How fast does mood change?",
  "I fixed the problem, why is mood still low?",
  "Chat asks why your pawn is still sad.")
F("mood", "Thoughts",
  "Ate without table is -3, so every dining area gets a table and chairs. I build a table near the kitchen early.",
  "Why is my colonist upset about eating?",
  "How much does eating without a table hurt mood?",
  "Viewer asks why you built a table first.")
F("mood", "Thoughts",
  "Slept outside, slept on ground and slept in the cold are each -4. Beds under a roof for everyone is part of the first day's setup.",
  "Why is my colonist sad in the morning?",
  "How bad is sleeping on the ground?",
  "Chat asks why you rushed beds.")
F("mood", "Thoughts",
  "Ate raw food is -7, while a fine meal gives +5 and a lavish meal +12. Cooking food is one of the cheapest mood fixes.",
  "Why is my colonist sad?",
  "How much mood do meals give?",
  "Viewer asks why you care about cooking.")
F("mood", "Thoughts",
  "Hungry is -6, ravenously hungry -12 and malnourished -20. When I see hunger thoughts I check the meal bill and the cook first.",
  "My colonist is hungry and sad, how bad is it?",
  "What is the mood hit for being malnourished?",
  "Chat asks why everyone is moody today.")
F("mood", "Thoughts",
  "Drowsy is -6, tired -12 and exhausted -18. If pawns are exhausted I check the schedule is Anything and that they have beds.",
  "How much does tiredness hurt mood?",
  "My colonist is exhausted, what do I do?",
  "Viewer asks why your pawn is so tired.")
F("mood", "Thoughts",
  "Observed corpse is -4 and observed rotting corpse -6. After a fight I haul or bury the bodies quickly.",
  "Should I clean up corpses after a raid?",
  "Why is my colonist upset after the fight?",
  "Chat asks why you are burying raiders.")
F("mood", "Thoughts",
  "Awful barracks is -7 and decent barracks -3, while an impressive bedroom gives +4. As soon as I can I give each colonist a private bedroom, as the owner orders.",
  "Barracks or private bedrooms?",
  "How much do barracks hurt mood?",
  "Viewer asks why you are building so many bedrooms.")
F("mood", "Needs",
  "Recreation unfulfilled, deprived and starved give -5, -10 and -20. I put in a horseshoe pin or chess table early so recreation stays up.",
  "My colonist has a recreation penalty, what do I build?",
  "How bad is low recreation?",
  "Chat asks why you built a game table.")
F("mood", "Needs",
  "Falling below about 35 percent beauty triggers unsightly environment at -5. I clean, put items on shelves and add floors in the rooms pawns use most.",
  "What is the unsightly environment thought?",
  "How do I raise beauty in a room?",
  "Viewer asks why you keep cleaning.")
F("mood", "Deterioration",
  "Apparel at 50 percent hit points or below gives ratty apparel -3, below 25 percent gives tattered apparel -5, and naked is -6. I replace worn clothes before they go tattered.",
  "Why is my colonist upset about clothes?",
  "When should I replace worn clothing?",
  "Chat asks about the ratty apparel thought.")
F("mood", "AI_Storytellers",
  "Difficulty shifts base mood: Peaceful and Community builder +10, Adventure story +5, Strive to survive 0, Blood and dust -5, Losing is fun -10. On harder settings I have to work mood harder.",
  "Does difficulty affect mood?",
  "Why is mood harder on Losing is fun?",
  "Viewer asks what difficulty does to your pawns.")

F("mental breaks", "Mental_break",
  "Below the minor threshold the mean time between breaks is 4 days, below major 0.8 days, and below extreme 0.5 days. A pawn in the extreme range gets my full attention right now.",
  "How often do mental breaks happen?",
  "My colonist is at 4 percent mood, how worried should I be?",
  "Chat asks how close your pawn is to snapping.")
F("mental breaks", "Mental_break",
  "A food binge needs more than 10 human-edible nutrition in a stockpile and lasts 10 to 18 hours. It is a minor break, so I let it run and fix the mood after.",
  "My colonist is food binging, what do I do?",
  "How long does a food binge last?",
  "Viewer asks why your pawn is eating everything.")
F("mental breaks", "Mental_break",
  "Sad wander lasts 16 to 24 hours and can be ended by arresting the pawn, but release gives -6 was imprisoned for 12 days instead of catharsis. Usually I just let them wander.",
  "My colonist is on a sad wander, should I arrest them?",
  "How long does sad wander last?",
  "Chat asks why your pawn is walking in circles.")
F("mental breaks", "Mental_break",
  "Berserk lasts a long time, and subduing the pawn with fists or a non-lethal weapon is the safest way to end it. I draft melee pawns to beat them down, never shoot them.",
  "A colonist went berserk, what now?",
  "How do I stop a berserk pawn without killing them?",
  "Viewer asks why you are punching your own colonist.")
F("mental breaks", "Mental_break",
  "A catatonic breakdown lasts 40 hours to 5 days. I put the pawn in bed, keep them fed and wait.",
  "My colonist went catatonic, how long is that?",
  "What do I do with a catatonic pawn?",
  "Chat asks if your colonist is okay.")
F("mental breaks", "Mental_break",
  "A fire starting spree only hits pyromaniacs, and the counter is someone putting out the fires as they start them. I keep a firefighter near a breaking pyromaniac.",
  "My pyromaniac is on a fire spree, what do I do?",
  "Who can have a fire starting break?",
  "Viewer asks why things are on fire.")
F("mental breaks", "Mental_break",
  "After a break the pawn gets a catharsis thought worth 40 for 3 days. So after a minor break I let them recover instead of arresting them.",
  "Does a mental break help mood after?",
  "What is catharsis?",
  "Chat asks why your pawn is happy after a tantrum.")
F("mental breaks", "Mental_break",
  "Given up and leaving never happens in colonies of seven or fewer, and murderous rage is ten times less likely in a colony of two. In a small colony the real risks are the common breaks.",
  "Can colonists quit the colony?",
  "Is murderous rage likely in a small colony?",
  "Viewer asks if your pawns will leave.")
F("mental breaks", "Mental_break",
  "A tantrum lasts 3.2 to 4.8 hours and smashes things, and unassigning the bedroom stops a bedroom tantrum after its first hit. I protect the expensive stuff and let it burn out.",
  "My colonist is having a tantrum, what do I do?",
  "How long does a tantrum last?",
  "Chat asks why your pawn is breaking furniture.")

# ---------------------------------------------------------------- medicine and surgery
F("medicine", "Medicine",
  "Herbal medicine has 0.6 potency, industrial 1.0 and glitterworld 1.6, and no medicine at all is 0.3. I tend serious wounds and disease with industrial and keep herbal for small cuts.",
  "Which medicine should I use for tending?",
  "How good is herbal medicine?",
  "Viewer asks why you saved the good medicine.")
F("medicine", "Medicine",
  "Industrial medicine is made at a drug lab after Medicine production research, from 3 cloth, 1 herbal medicine and 1 neutroamine. When I have the research and ingredients I add a bill for it.",
  "How do I make medicine?",
  "What does industrial medicine cost to craft?",
  "Chat asks where you get medicine from.")
F("medicine", "Medicine",
  "Industrial medicine does not spoil but deteriorates outside when not on a shelf. The owner wants medicine only on shelves in the hospital room, with healroot in the freezer.",
  "Where do I store medicine?",
  "Does medicine go bad?",
  "Viewer asks why the medicine is in the hospital.")
F("medicine", "Medicine",
  "A healthy doctor at Medical 8 reaches the 98 percent surgery cap in a lit, clean room with a hospital bed, and without one needs Medical 11. I build a proper hospital before planned surgery.",
  "How good does my doctor need to be for surgery?",
  "Do hospital beds matter?",
  "Chat asks if your doctor can install a bionic arm.")
F("medicine", "Medicine",
  "Tending with glitterworld medicine gives 500 doctor XP on a human, industrial 350 and herbal 250. I still save good medicine for real emergencies, not training.",
  "Does better medicine train the doctor faster?",
  "How much XP does tending give?",
  "Viewer asks how your doctor levels up.")
F("medicine", "PLAYBOOK",
  "The owner's plan is to research antibiotics, build a drug lab, make penoxycyline, and set every pawn's drug policy to take it every 5 days. That keeps disease away.",
  "How do I prevent diseases?",
  "What drug policy should my colonists have?",
  "Chat asks what the pills every five days are.")
F("medicine", "ORDERS",
  "A downed pawn gets field-tended before capture or hauling. I tend first so they do not bleed out on the way.",
  "A raider is downed and bleeding, what do I do first?",
  "Should I carry a wounded prisoner straight to bed?",
  "Viewer asks why you are bandaging the raider.")

F("surgery", "Surgery",
  "Surgery success multiplies doctor skill, bed, medicine and the operation, and caps at 98 percent with a minimum 2 percent failure. I never treat surgery as safe, even with a great doctor.",
  "Can surgery ever be 100 percent safe?",
  "What decides surgery success?",
  "Chat asks why surgery failed with a good doctor.")
F("surgery", "Surgery",
  "Hospital beds give a 1.15 surgery factor against 1.0 for normal beds, and surgery outdoors takes a 0.85 penalty. I operate only in the hospital on a hospital bed.",
  "Do hospital beds help surgery?",
  "Can I do surgery outside?",
  "Viewer asks why surgery waits for the hospital.")
F("surgery", "Surgery",
  "Medicine potency counts in surgery too: herbal 60 percent, standard 100 and glitterworld 160. I set surgery to use at least industrial medicine.",
  "What medicine should surgery use?",
  "Does herbal medicine make surgery riskier?",
  "Chat asks why you won't operate with herbal.")
F("surgery", "Surgery",
  "Less than 50 percent light at the head of the bed adds a penalty down to 0.75 in darkness, and dirty rooms lower the bed factor. The hospital gets two lamps and sterile tiles when I can afford them.",
  "Does light matter for surgery?",
  "Should I clean the hospital before surgery?",
  "Viewer asks why the hospital is so bright.")
F("surgery", "Surgery",
  "Max tend quality is 70 percent with herbal or no medicine, 100 with standard and 130 with glitterworld. For infections I use industrial or better so the tend is strong.",
  "Why does medicine quality matter for tending?",
  "My colonist has an infection, which medicine do I use?",
  "Chat asks if herbal is good enough for an infection.")

# ---------------------------------------------------------------- raids and defense
F("raids", "ORDERS",
  "A raid letter is a warning, not a contact, and the owner's rule is no drafting while the raiders are still off-map preparing because drafted pawns do no work. I use the window to ready a prisoner bed, arm everyone with a ranged weapon, stock medicine and finish roof and storage work.",
  "A raid letter says 6 pirates are coming, what now?",
  "Should I draft everyone as soon as the raid letter arrives?",
  "Chat says raiders are coming, why aren't you drafting?",
  "The letter says raiders are preparing, what do I do with the time?")
F("raids", "ORDERS",
  "The raid guard watches the map and the moment a hostile humanlike actually spawns it pauses, drafts everyone and sends each to their post behind the embrasures. Before contact I check the map for hostiles before any combat decision.",
  "How do I know when to actually draft for a raid?",
  "Viewer asks who drafts your colonists in a raid.",
  "Hostiles are on the map, what happens now?")
F("raids", "PLAYBOOK",
  "The owner's drill is ranged first, attack not flee, group up, and never let a melee raider or animal close the gap. My pawns shoot from the embrasures and fall back while firing if melee raiders charge.",
  "Melee raiders are charging, what do I do?",
  "How should my colonists fight?",
  "Chat asks why you retreat while shooting.")
F("raids", "PLAYBOOK",
  "Fights are played in short bursts with alerts read between each burst, pausing at the right moments so commands are not late. I pause, give orders, run a moment, then check again.",
  "How do I manage a fight in real time?",
  "Viewer asks why you keep pausing in the fight.",
  "The battle is chaotic, how do I stay on top of it?")
F("raids", "ORDERS",
  "Right after the last raider is down the owner wants open rooms fixed, items brought inside before they decay, shelves and stockpiles set, and the freezer working. That list comes before anything else.",
  "The raid is over, what do I do first?",
  "Chat asks what you are doing after the fight.",
  "All raiders are dead, what now?")
F("raids", "ORDERS",
  "A prisoner bed must exist in its own room before any fight. If a raid letter arrives and there is none, I build one first.",
  "Do I need anything ready before a raid?",
  "Where do downed raiders go?",
  "Viewer asks why you made a prison before the fight.")
F("raids", "Raids",
  "Raid size and strength come from a points system, and the game spends those points buying raiders by their combat power. A stronger, richer colony faces bigger raids, so I build defense as wealth grows.",
  "Why are raids getting bigger?",
  "How does the game decide raid size?",
  "Chat asks why that raid was so big.")
F("raids", "Raids",
  "Human raiders keep attacking until certain end conditions are met, while mechanoid raiders attack indefinitely. Against mechs I plan for a fight to the end.",
  "Will the raiders retreat?",
  "Do mechanoids ever give up?",
  "Viewer asks if the mechs will leave on their own.")
F("raids", "Raids",
  "Raid types include immediate attack, drop pods, sappers, breachers, siege and ambush. When the letter names the type I set up for it, sappers and breachers come through walls, not the gate.",
  "What kinds of raids are there?",
  "A letter says sappers, what does that mean?",
  "Chat asks why the raiders are digging.")
F("raids", "Drafted",
  "Drafted pawns stay where ordered and ignore their needs, and drafting ends on its own after about 2.78 minutes of no threats or orders. I undraft as soon as the fight is over so work resumes.",
  "What happens to needs while drafted?",
  "Do drafted colonists stay drafted forever?",
  "Viewer asks why your pawns are standing still.")
F("raids", "Drafted",
  "Drafted pawns cannot haul or build, but can still eat and take drugs, and drafting interrupts sleep immediately. That is why I never draft early.",
  "Can drafted colonists work?",
  "Does drafting wake up a sleeping colonist?",
  "Chat asks why nothing gets built during a raid warning.")
F("raids", "Drafted",
  "With Fire at Will on, ranged pawns shoot any enemy in range and use adjacent buildings as cover. I park them next to walls or sandbags.",
  "Will drafted colonists shoot on their own?",
  "Where should I place drafted shooters?",
  "Viewer asks how your pawns take cover.")
F("raids", "Drafted",
  "Shift queues move orders, and right-click dragging lines pawns up. I drag a firing line behind the embrasures.",
  "How do I line up my shooters quickly?",
  "Chat asks how you set up the firing line.",
  "Can I give drafted pawns several move orders?")

F("defense", "Cover",
  "Walls give up to 75 percent cover, sandbags and barricades 55, chunks 50, trees 25 and bushes 20. My shooters stand behind walls or sandbags, never in the open.",
  "How much cover do sandbags give?",
  "What is the best cover?",
  "Viewer asks why you sit behind sandbags.",
  "Is a tree good cover?")
F("defense", "Cover",
  "Cover works best against shots straight at it and fades to nothing above 65 degrees off angle. I place cover facing the direction the enemy comes from.",
  "Does cover protect from the side?",
  "Why did my colonist get hit behind sandbags?",
  "Chat asks how you angle the barricades.")
F("defense", "Cover",
  "Cover is only about 33 percent effective if the shooter is right in front of it. Melee rushers make cover useless, so I shoot them before they close.",
  "Does cover help at point blank range?",
  "Why is cover useless against charges?",
  "Viewer asks why you shoot early.")
F("defense", "Defense_structures",
  "Killbox entries should be single-wide, with fences on every second tile, and the receiving end double-walled. The owner wants one fortified entrance as the killbox with cover and turrets.",
  "How should I build a killbox?",
  "What makes a good base entrance?",
  "Chat asks why your entrance is so narrow.")
F("defense", "Defense_structures",
  "Sandbags placed next to each other let enemies vault several at once, so in a slowing tunnel I alternate sandbags with empty tiles. That keeps raiders slow under fire.",
  "How do I slow raiders down in a corridor?",
  "Should sandbags be in a solid line?",
  "Viewer asks why there are gaps between the sandbags.")
F("defense", "Defense_structures",
  "A pillbox gets firing holes by replacing wall pieces facing the enemy with sandbags, and pawns can lean from a wall and still use the sandbag. The owner calls those embrasures, near the borders, as rooms to shoot from.",
  "How do I make firing positions in a wall?",
  "What are embrasures for?",
  "Chat asks what those shooting rooms are.")
F("defense", "Mini-turret",
  "A mini-turret costs 70 steel, 3 components and 30 stuff, uses 80 W, needs Gun turrets research, and has 28.9 tiles of range. I put turrets behind cover at the killbox.",
  "What does a mini-turret cost?",
  "How far can a mini-turret shoot?",
  "Viewer asks what research turrets need.")
F("defense", "Mini-turret",
  "A mini-turret below 20 percent health has a 50 percent chance to explode for 50 damage in a 3.9-tile radius, so keep turrets at least 4 tiles apart. My colonists never stand right next to a damaged turret.",
  "Can turrets explode?",
  "How far apart should turrets be?",
  "Chat asks why your turrets are spread out.")
F("defense", "Mini-turret",
  "A mini-turret fires 60 rounds before needing a refuel of steel from a hauler. After every fight I check the turrets got rearmed.",
  "Do turrets need ammo?",
  "My turret stopped shooting, why?",
  "Viewer asks how turrets reload.")
F("defense", "Defense_structures",
  "A plasteel mini-turret has 335 health against 120, and mortars cannot hit within 30 tiles of themselves. Later I upgrade turret material and keep mortars deep inside.",
  "Is plasteel worth it for turrets?",
  "Can a mortar defend against close enemies?",
  "Chat asks where you put the mortars.")
F("defense", "Door",
  "Raiders treat closed doors like walls but doors have less HP, so enemies target them. My perimeter doors are stone or steel and covered by shooters.",
  "Do raiders break doors?",
  "What doors should my outer wall have?",
  "Viewer asks why the gate has so many guns on it.")

# ---------------------------------------------------------------- research
F("research", "ORDERS",
  "The owner's rule is research by the search box, never by dragging the tree. I open Research, type the project name and pick it from the result.",
  "How do I find a research project?",
  "Chat asks why you type in the research tab.",
  "The research tree is huge, how do I pick a project?")
F("research", "PLAYBOOK",
  "The playbook order is Microelectronics, then Multi-analyzer, then the computing line and the hi-tech research bench, and each upgrade gets built the moment it is researched. I keep research capacity maxed and replace old benches.",
  "What should I research for faster research?",
  "What is your research order?",
  "Viewer asks why you are rushing Microelectronics.")
F("research", "Research",
  "A simple research bench runs at 75 percent, a hi-tech bench at 100, and a hi-tech bench with a multi-analyzer at 110, and a bench outside a laboratory takes a 0.8 penalty. I put the benches in their own lab room.",
  "How much better is the hi-tech research bench?",
  "Does the research bench need its own room?",
  "Chat asks why the lab is a separate room.")
F("research", "Research",
  "Electricity costs 1,600 points with no prerequisite and unlocks heaters, while Battery costs 400 and needs Electricity. Electricity is one of my first projects.",
  "What should I research first?",
  "How expensive is Electricity research?",
  "Viewer asks why you went Electricity first.")
F("research", "Research",
  "Air conditioning costs 500 points and needs Electricity, and it unlocks the cooler. A freezer needs it, so it comes right after Electricity.",
  "What research do I need for a freezer?",
  "How much does Air conditioning cost?",
  "Chat asks when you will have a freezer.")
F("research", "Research",
  "Stonecutting and Complex furniture each cost 300 points with no prerequisite. Stonecutting lets me build in stone, and Complex furniture unlocks shelves and vents.",
  "What do I need for shelves?",
  "What does Stonecutting cost?",
  "Viewer asks why you want stone blocks.")
F("research", "Research",
  "Microelectronics costs 3,000 points, needs Electricity, and unlocks the hi-tech research bench. It also unlocks the comms console and orbital trade beacon.",
  "How do I unlock the comms console?",
  "What does Microelectronics unlock?",
  "Chat asks when you can call traders.")
F("research", "Research",
  "Gun turrets cost 500 points and need Blowback operation. Once the colony has power and steel I research them for the killbox.",
  "What do I need for turrets?",
  "How much research are gun turrets?",
  "Viewer asks when you get turrets.")
F("research", "Research",
  "Research speed rises with Intellectual skill: 8 percent at skill 0, 100 at 8 and 238 at 20. My best Intellectual pawn gets research as their 2.",
  "Who should do research?",
  "How much does Intellectual skill matter?",
  "Chat asks why your smartest pawn stays at the bench.")
F("research", "Research",
  "Tribal starts pay 1.5 times for Medieval projects and 2 times for Industrial and higher. Tribal research is slow, so I pick only what the colony needs.",
  "Why is research so expensive for my tribe?",
  "Do tribal colonies research slower?",
  "Viewer asks why Electricity costs 3,200 for you.")
F("research", "Research",
  "Some projects need techprints, like jump packs needing one Jump packs techprint and cataphract armor needing two. When a trader has techprints the plan needs, I buy them.",
  "What are techprints?",
  "Why can't I start this research?",
  "Chat asks why you bought that paper.")

# ---------------------------------------------------------------- power
F("power", "Power",
  "A wood-fired generator makes 1,000 W and burns 22 wood a day, and a chemfuel generator makes 1,000 W on 4.5 chemfuel a day. Early on I use a wood generator because wood is easy.",
  "What generator do I build first?",
  "How much wood does a wood-fired generator use?",
  "Viewer asks how you power the base.")
F("power", "Power",
  "A solar generator makes 1,700 W only in sunlight, nothing at night, and costs 100 steel and 3 components. I pair it with batteries for the night.",
  "Does solar work at night?",
  "How much power does a solar panel make?",
  "Chat asks why your lights go out at night.")
F("power", "Power",
  "A wind turbine makes 2,300 W day and night but needs open ground around it. I clear the space and keep buildings out of its area.",
  "How good are wind turbines?",
  "Where do I put a wind turbine?",
  "Viewer asks why there is a cleared strip by the turbine.")
F("power", "Power",
  "A geothermal generator makes 3,600 W but must sit on a geyser and costs 340 steel and 8 components. If there is a geyser in the base, it is my main power later.",
  "What is the best steady power?",
  "Can I build geothermal anywhere?",
  "Chat asks what the steam vent is for.")
F("power", "Power",
  "A watermill makes 1,100 W and goes on a riverbank. If we have a river nearby I use it for steady power.",
  "Is a watermill worth building?",
  "Where does a watermill go?",
  "Viewer asks if you can use the river.")
F("power", "Battery",
  "A battery holds up to 600 Wd, takes in only 50 percent of excess power, and loses 5 Wd a day. I build a few to carry solar through the night.",
  "How much does a battery hold?",
  "Are batteries efficient?",
  "Chat asks why your batteries are draining.")
F("power", "Battery",
  "A battery costs 70 steel and 2 components and needs Battery research. Charged batteries explode in rain or fire, so every battery goes under a roof.",
  "Can I leave batteries outside?",
  "What does a battery cost?",
  "Viewer asks why the batteries are in a shed.")
F("power", "Power",
  "Conduits must be directly adjacent to connect, and an appliance connects from up to 6 tiles from a power transporter. The owner wants every powered thing on a conduit the moment it is placed.",
  "My new heater has no power, why?",
  "How far can a device be from a conduit?",
  "Chat asks why the cooler is unpowered.")
F("power", "Events",
  "Zzztt is a conduit short circuit, batteries in the grid make it explode, and unroofed powered buildings in the weather can short too. I roof my power buildings and keep batteries in their own room.",
  "What is a Zzztt event?",
  "My batteries exploded, why?",
  "Viewer asks what made the fire in the power room.")

# ---------------------------------------------------------------- rooms
F("rooms", "Room",
  "Impressiveness comes from wealth, beauty, space and cleanliness, and the lowest of the four counts the most. I raise the worst stat first, usually cleanliness or space.",
  "How do I make a room more impressive?",
  "Which room stat matters most?",
  "Chat asks why your bedroom is only dull.")
F("rooms", "Room",
  "Bedroom impressiveness under 20 gives -2, 40 to 50 gives +2, 85 to 120 gives +5, and 240 or more +8. I aim each bedroom at decent or better.",
  "How much does a nice bedroom help mood?",
  "What does an awful bedroom do?",
  "Viewer asks how impressive your bedrooms are.")
F("rooms", "Room",
  "A room counts as a bedroom with one bed or a shared double bed, and becomes barracks with more than one non-assigned bed. The owner wants private rooms for everyone, so one bed per room.",
  "Why does my room say barracks?",
  "How do I make a room count as a bedroom?",
  "Chat asks why each pawn has their own room.")
F("rooms", "Room",
  "Space scores 1.4 per tile and blocking objects cut it, and a room under 12.5 space is cramped. I keep bedrooms the same uniform size so none read as cramped.",
  "Why is my bedroom cramped?",
  "How big should a bedroom be?",
  "Viewer asks why all your bedrooms look the same.")
F("rooms", "Room",
  "Cleanliness counts toward impressiveness, and blood is -10 on a tile. Cleaning is part of everyone's work so rooms stay clean.",
  "Why does cleaning matter?",
  "My room is dirty, how much does it hurt?",
  "Chat asks why your colonists keep mopping.")
F("rooms", "PLAYBOOK",
  "The owner wants rooms off a hall, never off another room or the outside, halls three cells wide that cross, and every room with a vent, a light and furniture. I plan the extension on paper before placing walls.",
  "How should I lay out the base?",
  "Viewer asks why your halls are so wide.",
  "Where do new rooms go?")
F("rooms", "ORDERS",
  "Two lamps per room, benches tight to the walls, short paths and never a blocked lane along a wall. I place benches against walls and check the walkway stays clear.",
  "Where do I put workbenches?",
  "How many lights does a room need?",
  "Chat asks why your benches hug the walls.")
F("rooms", "Roof",
  "A wall or column supports roof in a roughly circular area 6 tiles around it, and the roof collapses when the last support within 6 tiles goes. Wide rooms need columns.",
  "How big can a roof span?",
  "My roof collapsed, why?",
  "Viewer asks why there are pillars in the big room.")
F("rooms", "Roof",
  "A constructed or thin rock roof collapse deals 15 to 30 damage, while overhead mountain collapse obliterates anything under it. I never mine out supports under an overhead mountain.",
  "How dangerous is a roof collapse?",
  "Is mining under a mountain risky?",
  "Chat asks why you left rock pillars in the cave.")
F("rooms", "Roof",
  "Overhead mountain stops drop pods and erases mortar shells, but it allows infestations. A mountain base is safe from pods, so I watch for insects instead.",
  "Does a mountain roof stop drop pods?",
  "What is the downside of a mountain base?",
  "Viewer asks if mortars can hit your mountain base.")
F("rooms", "Roof",
  "Building a constructed roof costs no resources and is fast. I make sure every storage room is fully roofed before stocking it.",
  "Does building a roof cost materials?",
  "Why are some of my rooms not roofed?",
  "Chat asks how you add a roof.")
F("rooms", "Door",
  "Wood doors open at 120 percent speed with 104 HP, steel at 100 percent with 160 HP, and stone at only 45 percent but with much more HP. I use wood or steel for busy doors and stone only on the outer defense.",
  "What material should my doors be?",
  "Why are my colonists slow at doors?",
  "Viewer asks why your doors aren't stone.")
F("rooms", "PLAYBOOK",
  "A door in a stone nobody stocks never gets built, and slate doors once waited forever. I build doors in wood or steel.",
  "My door blueprint never gets built, why?",
  "Chat asks why the door is still a blueprint.",
  "Should I pick a fancy stone for doors?")
F("rooms", "Door",
  "Forbidden doors block colonists and colony pawns but not breaking pawns, visitors, traders or enemies. I use forbidding to keep my people in, not raiders out.",
  "Does forbidding a door stop raiders?",
  "What does forbidding a door do?",
  "Viewer asks why the door is red.")

# ---------------------------------------------------------------- storage
F("storage", "Stockpile_zone",
  "Stockpiles have priorities Low, Normal, Preferred, Important and Critical, and haulers move items to higher-priority storage with space. The owner wants shelves one priority higher than the floor stockpile in the same room.",
  "How do stockpile priorities work?",
  "My items sit on the floor next to empty shelves, why?",
  "Chat asks how you organize storage.")
F("storage", "Shelf",
  "A shelf is 2 by 1 tiles, holds three stacks per tile, needs Complex furniture, and items on it never deteriorate even outside. Every resource gets a shelf, as the owner orders.",
  "How much does a shelf hold?",
  "Do items on shelves deteriorate?",
  "Viewer asks why everything is on shelves.")
F("storage", "Shelf",
  "Shelves default to general items at Preferred priority. I set every shelf's filter right after placing it so food goes to the freezer and medicine to the hospital.",
  "What does a new shelf store by default?",
  "My new shelf grabbed the wrong items, why?",
  "Chat asks why the shelf took everything.")
F("storage", "Shelf",
  "Shelves cannot hold chunks, minified buildings, plants, toxic wastepacks or corpses bigger than 0.75 body size. Those go to a floor stockpile.",
  "Can I put stone chunks on a shelf?",
  "Where do corpses go?",
  "Viewer asks why chunks are on the floor.")
F("storage", "Stockpile_zone",
  "A small high-priority stockpile beside a workbench keeps the crafter supplied, and haulers refill it. I put one next to the stove for raw food, inside the freezer.",
  "How do I make my cook faster?",
  "Should I put a stockpile by the workbench?",
  "Chat asks about that little stockpile by the stove.")
F("storage", "Deterioration",
  "Items indoors or on shelves do not deteriorate, rain multiplies deterioration by 5, and metals and stone never deteriorate. I get wood, cloth and food inside first and leave steel and stone last.",
  "What happens to stuff left outside?",
  "Which items can I leave outside?",
  "Viewer asks why the steel is still outside.")
F("storage", "PLAYBOOK",
  "The owner wants a vault for silver, gold, gems and ivory. I build a locked room deep inside and set its shelves to valuables only.",
  "Where do I keep silver?",
  "Chat asks what the vault is for.",
  "Should silver sit in the general stockpile?")
F("storage", "PLAYBOOK",
  "After any harvest, hunt or butchering I read the map for food stacks outside the freezer and give them a freezer shelf. Food left anywhere else rots.",
  "I just harvested, what next?",
  "Food is rotting in the field, how do I fix it?",
  "Viewer asks why you check the map after a hunt.")

# ---------------------------------------------------------------- trade and caravans
F("trade", "PLAYBOOK",
  "There are three ways to trade: the comms console to call a ship or trade hub, or right-clicking a visiting trader pawn with a colonist selected. When a trade ship letter arrives I go straight to the comms console.",
  "How do I trade?",
  "A trade ship letter just arrived, what do I do?",
  "Chat asks how you talk to traders.")
F("trade", "Trade",
  "Selling is at 60 percent of market value and buying at 140 percent, and the trader's Social skill improves prices. My best social pawn does the trading.",
  "Who should do my trading?",
  "Why do traders pay so little?",
  "Viewer asks why you buy high and sell low.")
F("trade", "Trade",
  "Bulk goods traders deal in food, basic materials, clothing, furniture and domestic animals. That is where I sell cash crops and buy cows, as the owner wants.",
  "What does a bulk goods trader buy?",
  "Where can I buy livestock?",
  "Chat asks what that trader sells.")
F("trade", "Trade",
  "Combat suppliers sell weapons, armor, mortar shells and non-herbal medicine. When one comes I buy medicine and guns if we need them.",
  "What does a combat supplier sell?",
  "Where do I buy medicine?",
  "Viewer asks if you will buy guns.")
F("trade", "Trade",
  "Exotic goods traders sell rare items like bionic parts and do not take raw plants. I check them for techprints and bionics the plan needs.",
  "What do exotic traders have?",
  "Can I sell crops to an exotic trader?",
  "Chat asks why the exotic trader wouldn't take rice.")
F("trade", "Trade",
  "Comms consoles and orbital trade beacons need Microelectronics, and orbital ships stay about 16 in-game hours before leaving. When a ship arrives I trade fast.",
  "How long do trade ships stay?",
  "What do I need for orbital trade?",
  "Viewer asks why you rushed to the console.")
F("trade", "Trade",
  "Only items within an orbital trade beacon's range can be traded, living creatures excepted. I put the beacon in the storeroom so everything is in range.",
  "Why can't I sell items to the ship?",
  "Where does the trade beacon go?",
  "Chat asks why your silver isn't showing up.")
F("trade", "Trade",
  "Weapons sell at 0.2 times their value, techprints at 0.1, and furniture at 0.7, while sculptures sell at 1.1. For silver I sell sculptures, crops and goods, not weapons.",
  "What sells well to traders?",
  "Is selling captured guns worth it?",
  "Viewer asks what makes the best money.")
F("trade", "PLAYBOOK",
  "Never sell irreplaceable high tech like age-reversing serums. I pay with cash crops and refined goods instead.",
  "Should I sell this rare tech for silver?",
  "Chat says sell the serum for cash.",
  "What should I never sell?")
F("trade", "Trade",
  "A slaver deals in prisoners, and a healthy slave is worth about 1,000 silver. Slavers become rare at 8 colonists and stop at 9.",
  "How much is a prisoner worth to a slaver?",
  "Why don't slavers visit anymore?",
  "Viewer asks what the slaver trader is.")
F("trade", "Trade",
  "A trade caravan camps for 10.8 to 18 in-game hours, and leaves at once if the trader or a pack animal is lost. I trade with them quickly and keep them safe.",
  "How long do caravans stay?",
  "A visiting caravan is leaving early, why?",
  "Chat asks how long the traders hang around.")
F("trade", "ORDERS",
  "The owner says answer every pop-up, never pay a demand, and always accept visitors. When a demand letter arrives I refuse and get ready to fight.",
  "A faction demands silver or they attack, do I pay?",
  "Visitors want to stay, do I let them?",
  "Viewer asks if you pay off raiders.")

F("caravans", "Caravan",
  "A caravan needs at least one colonist, and humans and pack animals carry body size times 35 kg. A horse carries 84 kg and a donkey 49, so I bring pack animals for big loads.",
  "How much can a caravan carry?",
  "Do I need pack animals for a caravan?",
  "Chat asks why you bring the donkey.")
F("caravans", "Caravan",
  "A solo pawn walks about 9 tiles a day, or about 14.5 on a horse, and caravans only move from 06:00 to 22:00. I pick nearby destinations or bring mounts.",
  "How fast does a caravan travel?",
  "Does riding a horse speed up a caravan?",
  "Viewer asks how far the trip is.")
F("caravans", "Caravan",
  "Mountains are 4 times harder to cross than flat ground and roads halve the difficulty, and very cold weather slows movement. I route caravans along roads.",
  "Why is my caravan so slow?",
  "Should I travel through the mountains?",
  "Chat asks why you took the long road.")
F("caravans", "Caravan",
  "On the road simple meals spoil in about 4 days, berries last up to 14, and pemmican over a year. I pack pemmican or survival meals for long trips.",
  "What food do I pack for a caravan?",
  "Will meals spoil on a caravan?",
  "Viewer asks why you made pemmican.")
F("caravans", "Caravan",
  "By default you can have one colony, raisable to five in the options, and you can't settle next to another settlement. I stay focused on the home base for now.",
  "Can I have more than one colony?",
  "Can I settle next to a town?",
  "Chat asks if you will start a second base.")

# ---------------------------------------------------------------- prisoners and slaves
F("prisoners", "Prisoner",
  "A downed pawn can be captured with 100 percent success, but there must be a free bed or sleeping spot set For Prisoners. I set the prisoner bed before the fight.",
  "How do I capture a raider?",
  "Why can't I capture this downed pawn?",
  "Chat asks how you take prisoners.")
F("prisoners", "Prisoner",
  "Resistance must reach 0 before recruitment can start, Recruit lowers resistance then tries, and Reduce Resistance never recruits. I set Recruit on prisoners I want to keep.",
  "How does recruiting prisoners work?",
  "Why isn't my prisoner joining?",
  "Viewer asks how long until the prisoner joins.")
F("prisoners", "Prisoner",
  "Each warden chat lowers resistance by a base 1.0, scaled by the prisoner's opinion of the warden and their mood. My best social pawn is warden, and the prison gets a decent room.",
  "How do I recruit faster?",
  "Does prisoner mood matter for recruiting?",
  "Chat asks why the prison has nice furniture.")
F("prisoners", "Prisoner",
  "Releasing a prisoner from another faction gives +12 goodwill if they leave healthy, except pirates and savage tribes. Prisoners I don't want, I release to friendly factions for goodwill.",
  "What happens if I release a prisoner?",
  "Can releasing prisoners help relations?",
  "Viewer asks why you let the prisoner go.")
F("prisoners", "Prisoner",
  "Executing a guilty prisoner gives non-psychopaths -2 mood and an innocent one -5. I avoid executions and recruit, release or enslave instead.",
  "Should I execute a prisoner?",
  "How do my colonists feel about executions?",
  "Chat asks if you'll execute the raider.")
F("prisoners", "Prisoner",
  "During a prison break the original room always joins and other rooms within 20 tiles each have a 50 percent chance to join. I keep prison cells apart and walled in layers, as the owner wants.",
  "How do prison breaks spread?",
  "How should I design my prison?",
  "Viewer asks why the cells are far apart.")
F("prisoners", "Prisoner",
  "Arresting depends mostly on the arrester's Social skill, and a failed arrest sends the target berserk. I only arrest with a social pawn and backup nearby.",
  "Can I arrest a visitor?",
  "What happens if an arrest fails?",
  "Chat asks why that arrest went wrong.")
F("prisoners", "Prisoner",
  "Raiders downed by pain have a chance to die, while blood loss avoids that risk. I capture quickly after the fight and tend them first.",
  "Why do some downed raiders die?",
  "How do I keep downed raiders alive?",
  "Viewer asks why the raider died on the ground.")
F("prisoners", "Slavery",
  "Slaves come from lowering a prisoner's will to zero, and they work at 85 percent speed. They cannot do Warden, Hunt, Art or Research, so I give them hauling, mining and growing.",
  "What can slaves do?",
  "How do I make a slave?",
  "Chat asks what your slave is for.")
F("prisoners", "Slavery",
  "Slave suppression drops 20 percent a day when it is between 30 and 100 percent, and a warden suppresses them back up. I keep a warden on suppression every day.",
  "How do I keep slaves from rebelling?",
  "Why is my slave's suppression dropping?",
  "Viewer asks what suppression is.")
F("prisoners", "Slavery",
  "The base time between slave rebellions is 45 days, it is 4 times more likely if a weapon is within 7 tiles, and slave collars offset suppression loss by 15 percent a day. I keep weapons out of slave areas.",
  "What causes slave rebellions?",
  "Do slave collars help?",
  "Chat asks why there are no weapons near the slaves.")

# ---------------------------------------------------------------- ideology
F("ideology", "Ideoligion",
  "Every ideoligion has a Leader and a Moral Guide, plus up to 2 specialist types. The owner wants the ritual spot and leader role filled before bedrooms, and every role assigned.",
  "What roles should I assign?",
  "When do I set the leader?",
  "Chat asks who your leader is.")
F("ideology", "PLAYBOOK",
  "The owner wants the leader and moral guide filled and their abilities used every time they come off cooldown. I check role abilities each pass and fire the ready ones.",
  "Should I use my leader's abilities?",
  "Viewer asks what your moral guide does.",
  "My leader has an ability ready, use it?")
F("ideology", "Ideoligion",
  "An ideoligion has up to 4 memes, and the 19 standard precept issues can't be removed, only changed. Precepts decide what makes our people happy or upset, so I read them before building.",
  "What are memes and precepts?",
  "Can I remove a precept?",
  "Chat asks what your ideoligion believes.")
F("ideology", "Ideoligion",
  "Under the corpse precept that finds them unsightly, seeing a human corpse is -4 and a rotting one -6. I bury or burn bodies quickly after fights.",
  "Does our ideology care about corpses?",
  "Why are my colonists upset by bodies?",
  "Viewer asks why you clear the battlefield so fast.")
F("ideology", "Ideoligion",
  "Conversion attempts lower certainty, and at 0 percent the pawn changes ideology. My moral guide works on converting newcomers.",
  "How does conversion work?",
  "What is certainty?",
  "Chat asks how your new colonist joins your faith.")
F("ideology", "Ideoligion",
  "Development points come from rituals and conversions, and the first reformation costs 10 points. I run rituals with good outcomes to earn them.",
  "How do I get development points?",
  "When can I reform my ideoligion?",
  "Viewer asks what the ritual is for.")
F("ideology", "PLAYBOOK",
  "The owner wants the ideoligion's wants met, including its statues and rooms. I check its required buildings and build them as the base grows.",
  "My ideology wants a building, should I make it?",
  "Chat asks what that statue is.",
  "What does my ideoligion need from the base?")

# ---------------------------------------------------------------- events
F("events", "Events",
  "A solar flare lasts 0.15 to 0.5 days and stops all electrical devices, including heaters and coolers, while campfires and passive coolers still work. I keep the freezer closed and wait it out.",
  "A solar flare hit, what do I do?",
  "How long does a solar flare last?",
  "Viewer asks why the power is out.")
F("events", "Events",
  "Toxic fallout lasts 2.5 to 10.5 days, builds toxicity in anyone not under a roof, and kills crops. I keep everyone indoors and only send people out briefly.",
  "Toxic fallout started, what now?",
  "Can my colonists go outside during toxic fallout?",
  "Chat asks why nobody is outside.")
F("events", "Events",
  "In toxic fallout buildup is about 40 percent a day, permanent damage like dementia becomes possible at 40 percent severity, and 100 percent is death. Anyone outside comes in and rests until it drops.",
  "How dangerous is toxic buildup?",
  "My colonist has toxic buildup, how bad?",
  "Viewer asks if your pawn will be okay.")
F("events", "Events",
  "An eclipse lasts 0.75 to 1.25 days and stops solar generators and outdoor crop growth. I switch to batteries and other generators until it passes.",
  "An eclipse started, what changes?",
  "Why did solar power stop?",
  "Chat asks why it got dark.")
F("events", "Events",
  "Infestations need an overhead mountain roof within 30 tiles of a colony structure and temperature above -17, and light and cold below -8 reduce the chance. I light the mountain rooms and destroy hives fast if they appear.",
  "Where can infestations spawn?",
  "How do I prevent infestations?",
  "Viewer asks why your mountain base has so many lights.")
F("events", "Events",
  "A cold snap lasts 1.5 to 3.5 days and drops the temperature 20 degrees, killing most edible plants. I put on heaters, warm clothes and watch animal food.",
  "A cold snap hit, what now?",
  "Will a cold snap kill my crops?",
  "Chat asks why it suddenly got cold.")
F("events", "Events",
  "A heat wave lasts 1.5 to 3.5 days and raises temperature 17 degrees, and the main risks are a failing freezer and heatstroke. I check the freezer stays below zero.",
  "A heat wave started, what do I check?",
  "Will a heat wave spoil my food?",
  "Viewer asks why you are watching the freezer.")
F("events", "Events",
  "A psychic drone lasts 0.75 to 1.75 days with a mood hit from -12 up to -40. I keep everyone comfortable and fed until it ends.",
  "A psychic drone hit, what do I do?",
  "How bad is a psychic drone?",
  "Chat asks why half the colony is sad.")
F("events", "Events",
  "A flashstorm lasts 0.075 to 0.1 days with lightning that starts big fires, and no rain follows for a while. I keep firefighting at 1 for everyone and stay near the base.",
  "A flashstorm is coming, what do I do?",
  "Will a flashstorm start fires?",
  "Viewer asks why everything is burning.")
F("events", "Events",
  "Volcanic winter lasts 7.5 to 40 days, drops temperature 7 degrees and light 30 percent, and halves wildlife. I grow indoors and stock food.",
  "Volcanic winter started, what now?",
  "How long does a volcanic winter last?",
  "Chat asks why there are fewer animals.")

F("storytellers", "AI_Storytellers",
  "There are three storytellers: Cassandra builds challenge on a rising curve with breathing room, Phoebe leaves long gaps between disasters, and Randy is random. Each plays very differently.",
  "What storytellers are there?",
  "Which storyteller is the most random?",
  "Viewer asks who your storyteller is.")
F("storytellers", "AI_Storytellers",
  "The threat scale for the six difficulties is 10, 30, 60, 100, 155 and 220 percent, from Peaceful to Losing is fun. Harder settings mean bigger raids, so I build defense earlier.",
  "How much harder are high difficulties?",
  "What is the threat scale?",
  "Chat asks what Losing is fun does.")
F("storytellers", "AI_Storytellers",
  "Commitment mode gives one save that saves on quit, and you can't reload mistakes. I play every decision as if it can't be undone.",
  "What is commitment mode?",
  "Can I reload a bad raid?",
  "Viewer asks if you save scum.")
F("storytellers", "AI_Storytellers",
  "The storyteller's population curve sends more joiners when you have few colonists, and prisoners count as half a colonist. A small colony gets wanderers more often, so I say yes to them.",
  "Why do so many wanderers join early?",
  "Do prisoners count as colonists for the storyteller?",
  "Chat asks why new people keep showing up.")

# ---------------------------------------------------------------- construction materials
F("construction", "PLAYBOOK",
  "The owner says build in stone blocks or steel, not wood, and stone needs a stonecutter's table with a Make stone blocks bill on Forever. I build the stonecutter first and feed it chunks.",
  "What material should I build walls with?",
  "Why do you build in stone?",
  "Chat asks why you aren't using wood.")
F("construction", "Stuff",
  "Wood is more flammable than stone, and stony beds are less comfortable than wood or steel. So walls go stone and beds go wood or steel.",
  "What material for beds?",
  "Is wood a fire risk?",
  "Viewer asks why your beds are wood but walls stone.")
F("construction", "Stuff",
  "The stony materials are granite, limestone, marble, sandstone and slate blocks, plus a few rare ones. I use whichever block the map gives most of.",
  "Which stones can I build with?",
  "Chat asks what kind of stone your walls are.",
  "Does it matter which stone I pick?")
F("construction", "Temperature",
  "Wall material does not change insulation, wood insulates as well as stone. I choose stone for fire safety and strength, not warmth.",
  "Do stone walls keep rooms warmer?",
  "Viewer asks if wood walls are colder.",
  "Is steel better insulation?")
F("construction", "Door",
  "A door costs 25 stuff and has 160 base HP, and doors can't be reinstalled or bought. I plan door spots before building.",
  "How much does a door cost?",
  "Can I move a door?",
  "Chat asks why you don't move that door.")
F("construction", "PLAYBOOK",
  "Only designate cells that have been read, and a mine order is a seam or a room, never a whole block. I mark exactly the rooms I plan.",
  "Should I mark the whole mountain to mine?",
  "Viewer asks why you mine in small pieces.",
  "How do I plan a mountain base dig?")

# ---------------------------------------------------------------- quests
F("quests", "Quests",
  "Quests are rated 1 to 3 stars, with 2-star threats doubled and 3-star tripled, and threats can vary 30 percent either way. I read the stars before accepting.",
  "How dangerous is a 3-star quest?",
  "What do quest stars mean?",
  "Chat asks if you should take that quest.")
F("quests", "Quests",
  "Most quests have a window to accept and a time limit to finish, and missing the deadline fails them. I accept only what the crew can do in time.",
  "Do quests expire?",
  "What happens if I miss a quest deadline?",
  "Viewer asks why you said no to that quest.")
F("quests", "Quests",
  "Rescued refugees and freed prisoners get a +18 Rescued mood buff for 30 days. Rescue quests are a good way to grow the colony.",
  "Are rescue quests worth it?",
  "What mood do rescued people get?",
  "Chat asks if the refugee will join.")
F("quests", "Quests",
  "A bandit camp quest counts as won once more than half the enemies are downed or killed. I bring enough rifles and leave once it is won.",
  "When is a bandit camp quest done?",
  "Do I have to clear the whole camp?",
  "Viewer asks when you can go home.")
F("quests", "Quests",
  "Trade request items must be normal quality or better and untainted, but item hit points don't matter. I check quality before sending.",
  "What items does a trade request accept?",
  "Can I send tainted clothes for a trade request?",
  "Chat asks why the request rejected that shirt.")
F("quests", "PLAYBOOK",
  "The owner wants quests and missions done for cash. I take quests that pay well and fit the crew.",
  "Should I do quests?",
  "How do I make money besides trading?",
  "Viewer asks why you took that quest.")

# ---------------------------------------------------------------- early game
F("early game", "ORDERS",
  "The settle order is a roofed food room with a food-only stockpile, a stove with simple meals Do until 30, roofed beds for everyone, and a prisoner bed in its own room before any fight. I do those before anything else.",
  "What do I build first in a new colony?",
  "Chat asks what your first-day plan is.",
  "We just landed, what first?",
  "What are your early-game priorities?")
F("early game", "ORDERS",
  "Pawns alive first: food, cold storage, medicine, heat. I check those four before any project.",
  "What comes first when things go wrong?",
  "Viewer asks what your top priority is.",
  "Everything is a mess, where do I start?")
F("early game", "ORDERS",
  "The owner's order is to pause, fix everything, then run time, but never leave the game paused at the end of a turn. I pause to set things up and unpause in the same turn.",
  "Should I keep the game paused while I plan?",
  "Chat asks why the game is frozen.",
  "When do I unpause?")
F("early game", "ORDERS",
  "Don't build a massive camp, just settle and start on the mountain base. I keep the camp small and put effort into the mountain.",
  "Should I build a big starter camp?",
  "Viewer asks why your camp is tiny.",
  "Where do I spend early building effort?")
F("early game", "ORDERS",
  "New colonies start on a 300 by 300 map in spring, on a mountainous tile in forest or jungle, because a map with no trees has no wood. I tell chat the tile we landed on.",
  "What map settings should I use?",
  "Chat asks why you picked a forest tile.",
  "Why does the map need trees?")
F("early game", "ORDERS",
  "The company and the gate come only after the colony feeds itself. I get food stable first.",
  "When should I start on the gate?",
  "Viewer asks when you'll open the gate.",
  "Should I start company work on day one?")
F("early game", "PLAYBOOK",
  "Read every letter and message as it lands: left-click to read, right-click to dismiss once handled. I keep the stack short.",
  "How do I handle all these letters?",
  "Chat asks if you read the letters.",
  "The letter stack is huge, what do I do?")
F("early game", "PLAYBOOK",
  "Every colonist carries a ranged weapon plus a melee sidearm like a stun baton for close range. I equip everyone before the first raid.",
  "Should colonists carry two weapons?",
  "Viewer asks why your pawn has a baton and a rifle.",
  "What weapons should everyone have?")
F("early game", "ORDERS",
  "Verify by result, never by narration: read the thing back to confirm it changed. If I did not read it back, I do not know it happened.",
  "How do I know a bill was really added?",
  "Chat asks how you check your clicks worked.",
  "I clicked a toggle, is it on now?")


def main():
    rows, seen = [], set()
    for topic, src, answer, qs in FACTS:
        for q in qs:
            if q in seen:
                raise SystemExit("duplicate question: " + q)
            seen.add(q)
            rows.append({"meta": {"source": S[src], "topic": topic},
                         "messages": [{"role": "system", "content": SYSTEM},
                                      {"role": "user", "content": q},
                                      {"role": "assistant", "content": answer}]})
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(len(FACTS), "facts ->", len(rows), "examples ->", OUT)


if __name__ == "__main__":
    main()
