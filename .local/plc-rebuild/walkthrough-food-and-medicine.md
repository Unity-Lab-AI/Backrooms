# Walkthrough distillation: food chain + medicine (one rule per line)
Sources: F=https://rimworldwiki.com/wiki/Food  I=https://rimworldwiki.com/wiki/Infection  C=https://rimworldwiki.com/wiki/Cold_storage  M=https://rimworldwiki.com/wiki/Medicine  D=https://rimworldwiki.com/wiki/Doctor  H=https://rimworldwiki.com/wiki/Hospital_bed  P=https://rimworldwiki.com/wiki/Nutrient_paste_dispenser  B=https://rimworldwiki.com/wiki/Butcher_table  G=https://rimworldwiki.com/wiki/Plague  K=https://rimworldwiki.com/wiki/Malaria  L=https://rimworldwiki.com/wiki/Flu  S=https://rimworldwiki.com/wiki/Sterile_tile  R=https://rimworldwiki.com/wiki/Food_poisoning  T=https://rimworldwiki.com/wiki/Hunting
Only F and I were fetched this session (2026-10-13). Rules tagged with any other source come from general guide knowledge. Check them in game.

## Food: budget
- Budget 1.6 nutrition per adult each day: about 2 meals, or 32 raw units / pemmican. [survival] F
- Count a meal as 0.9 nutrition (lavish 1.0); raw food is 0.05 per unit. [survival] F
- Always cook: a simple meal costs 0.5 raw nutrition and gives 0.9 (180%). [survival] F
- Before the first winter, hold count_MealSimple+MealFine >= 10 x colonists (2 meals x 5 days). [survival] F
- Food emergency when meals + raw nutrition < 1.6 x colonists x 2 days: hunt and forage berries now. [survival] F
- Eat packaged survival meals last: they never spoil, so keep them for caravans and emergencies. [survival] F
- Make pemmican (rots in 70 days) when there is no freezer or a caravan is planned. [economy] F

## Food: farming
- Plan 25 tiles of rice/potato/corn per colonist on normal soil (20 on rich soil) at Plants 6. [growth] F
- Plant rice first for the fastest early yield; potatoes on poor/gravel soil; corn for long storage (60 days). [start] F
- Grow healroot (needs Plants 8) in a 10-20 tile field once someone qualifies, so herbal medicine keeps coming. [growth] M
- Plant 1 cotton/devilstrand field for clothes and 1 haygrass field per 2-3 large animals. [animals] F
- Harvest every field before the first frost; stop planting when outdoor temps will stay below 0C. [growth] F
- Berries, milk and insect jelly can be eaten raw with no "Ate raw food" penalty. [survival] F

## Food: hunting and butchering
- Hunt only safe game (deer, ibex, rabbits, alpaca, single muffalo); never hunt boomrats/boomalopes near the base, predators or thrumbos with a weak hunter. [survival] T
- Skip animals with manhunter revenge chance above 10% unless the hunter has a ranged weapon and a clear escape route. [war] T
- Butcher corpses within 2 days (raw meat rots in about 2 days above 0C). [survival] F
- Put a butcher spot down on day one; later build a butcher table beside the freezer, outside the kitchen room. [base-and-fortress] B
- Floor the kitchen and keep it clean; a dirty kitchen raises food poisoning risk. [base-and-fortress] R
- Set cooking bills to "Do until you have X" with X = 10 x colonists, not "Forever". [configuration] F
- Cook with the highest Cooking skill pawn; poisoning risk drops as Cooking skill rises. [configuration] R

## Food: storage and temperature
- Food spoils above 0C: keep the freezer below -1C, target -5C to -10C for margin. [base-and-fortress] C
- Below 10C spoilage slows (factor 1/temp C); a cool room helps when you cannot freeze. [base-and-fortress] F
- Freezer = walled, roofed room, 1 cooler per about 20-30 tiles, hot side vented outdoors, double-door airlock to the kitchen. [base-and-fortress] C
- Store food under a roof: unroofed food deteriorates even when cold. [base-and-fortress] F
- If power fails and the freezer goes above 0C, cook all raw meat into meals/pemmican at once. [survival] C
- Meals rot in about 4 days unfrozen; never cook more than 2 days ahead without a freezer. [survival] F
- Freezer stockpile: food + corpses to butcher; store medicine in a separate room near the hospital. [configuration] C
- In winter, a roofed outdoor stockpile below 0C works as a free freezer. [survival] C

## Food: nutrient paste
- A nutrient paste dispenser makes 0.9 nutrition from 0.3 raw (300%), never poisons, gives -4 mood. [economy] P
- Build one at 6+ colonists or during a food shortage, after Nutrient paste research; it needs power and hoppers. [growth] P
- Put the hoppers inside the freezer (dispenser built into the freezer wall) so its feed does not rot. [base-and-fortress] P
- Do not make paste the only food in a mood-fragile colony; keep fine meals going too. [growth] F

## Mood and food
- Block raw food (-7 mood) and human meat unless an ideology or trait allows it; take human corpses off food stockpiles. [configuration] F
- Cook fine meals (+5) once Cooking is 6+; lavish meals (+12) for mood emergencies. [growth] F

## Medicine and doctors
- Make the highest Medicine skill pawn the doctor (Doctor priority 1); give one backup Doctor priority 2-3. [configuration] D
- Have herbal medicine from day one; keep at least 5 medicine per colonist. [survival] M
- Medicine potency: herbal 0.6, industrial 1.0, glitterworld 1.6; herbal for small cuts, industrial for infections/disease, glitterworld only when a pawn is about to die. [configuration] M
- Default medical care: colonists "best up to industrial"; prisoners/animals "herbal or worse". [configuration] M
- Research Medicine Production; craft industrial medicine at a drug lab (cloth + herbal medicine + neutroamine) when stock runs low. [research] M
- Tend bleeding wounds at once; 100% blood loss kills. [survival] D
- Never leave a downed colonist outside; rescue them to a medical bed. [survival] D

## Hospital
- Hospital = 2-4 medical beds in a floored, lit, clean room near the main entrance. [base-and-fortress] H
- Mark beds Medical; add a vitals monitor once researched (better tend quality and immunity gain). [base-and-fortress] H
- Sterile tile floors: room infection factor 32%, against 50% for a clean floored room and 100% outdoors/caravan. [base-and-fortress] I S
- Keep the hospital at 16-26C with a heater/cooler. [base-and-fortress] H
- Clean the hospital first; someone has Cleaning priority 1. [configuration] I

## Infection and disease
- Infection chance per wound: bites/burns 30%, frostbite 25%, shredded 20%, other bleeds 15%; blunt wounds and missing parts never get infected. [survival] I
- Tend quality cuts infection chance from 85% (0% quality) to 5% (100% quality); always tend with medicine. [survival] I
- An untreated infection can kill in about 1.2 days; tend every 12 h until immune (about 1.55 days at 100% immunity gain). [survival] I
- If an illness's severity is rising toward or past immunity: bed rest, better medicine, best doctor. [survival] I
- Plague: severity grows fast; tend as often as allowed with industrial medicine and bed rest until immune. [survival] G
- Malaria / sleeping sickness: long; bed rest and daily tending; glitterworld only if near death. [survival] K
- Flu: tend daily; herbal medicine and bed rest usually enough. [survival] L
- Food poisoning lasts about 1 day and is not lethal; prevent it with cooking skill and a clean kitchen. [survival] R
- Gut worms / muscle parasites: chronic; keep tending until healed. [survival] M
- Severity above 0.8 means the pawn is near death: best medicine, best doctor, now. [survival] I

## Decision thresholds for the PLC
- food_days < 3 -> hunt + harvest + cook rung. [survival] F
- freezer temp > -1C -> add a cooler or restore power. [base-and-fortress] C
- count_MedicineHerbal + count_MedicineIndustrial < 5 x colonists -> grow healroot / craft medicine. [survival] M
- colonists >= 6 and research_NutrientPaste done -> dispenser in the freezer wall. [growth] P
- any infection/disease hediff -> doctor priority 1, bed rest, tend every 12 h. [survival] I
- research bench by day 3; Refrigeration early; Medicine Production after Electricity. [research] M C
- raw meat in an unpowered storage room at >0C for more than 1 day -> butcher and cook now. [survival] F
