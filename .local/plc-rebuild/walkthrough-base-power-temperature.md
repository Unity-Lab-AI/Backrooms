# Walkthrough distillation: base layout, rooms, doors, light, cleanliness, power, temperature, fire, events
# Format: one imperative rule per line, [family], source URL. Lines with "THRESHOLD:" are PLC-testable.
# Numbers are vanilla wiki values; mods may shift them.

## Mountain base layout
- Pick a base site at a mountain edge so the main base sits under overhead mountain and the killbox entrance faces open ground. [base-and-fortress] https://rimworldwiki.com/wiki/Roof
- THRESHOLD: every overhead-mountain tile must keep a wall/column support within 6 tiles; never mine out the last support or the roof collapses and kills anything below. [base-and-fortress] https://rimworldwiki.com/wiki/Roof
- Leave a 1x1 rock pillar (or build a column) every 5-6 tiles when mining large halls under overhead mountain. [base-and-fortress] https://rimworldwiki.com/wiki/Roof
- Keep constructed-roof rooms 12 interior tiles wide or less, or add columns, so they roof fully. [base-and-fortress] https://rimworldwiki.com/wiki/Roof
- Wall off unused overhead-mountain voids within 30 tiles of any structure; walls (not doors/columns) block infestation spawns, a wall every 2nd tile is enough. [base-and-fortress] https://rimworldwiki.com/wiki/Infestation
- THRESHOLD: infestation possible when an overhead-mountain tile is > -17C (chance falls below -8C), dark, far from unroofed tiles, within 30 tiles of a structure; max once per 20 days; none at 30+ hives. [war] https://rimworldwiki.com/wiki/Infestation
- Keep mountain-base rooms lit and close to the outside to cut infestation weight; a space held at -17C or colder cannot spawn hives. [base-and-fortress] https://rimworldwiki.com/wiki/Infestation
- Keep turrets and a fallback chokepoint inside the base covering the largest dark mountain halls. [war] https://rimworldwiki.com/wiki/Infestation
- Use a single fortified entrance (killbox) as the only ground path in; solid walls everywhere else. [war] https://rimworldwiki.com/wiki/Defense_structures
- Rely on overhead mountain against mortars and drop pods; nothing lands or hits through it. [war] https://rimworldwiki.com/wiki/Roof
- Place freezer, kitchen, dining as an adjoining cluster in the base centre; bedrooms on a quiet side corridor. [base-and-fortress] https://rimworldwiki.com/wiki/Room
- Keep fields, wind turbines and solar outside the mountain (they need sky); keep conduits to them short and walled. [base-and-fortress] https://rimworldwiki.com/wiki/Power

## Room sizes and stats
- Size a standard bedroom about 4x6 interior (space 29-55 "average"); minimum usable bedroom 3x4. [base-and-fortress] https://rimworldwiki.com/wiki/Room
- THRESHOLD: room space < 12.5 = cramped (mood debuff); target >= 29 for bedrooms and dining. [base-and-fortress] https://rimworldwiki.com/wiki/Room
- THRESHOLD: bedroom impressiveness < 20 Awful (-2); >= 30 +1; >= 40 +2; >= 50 +3; >= 65 +4; >= 85 +5; >= 120 +6. [growth] https://rimworldwiki.com/wiki/Room
- Use a shared barracks only while the colony is 3-4 pawns early; give private bedrooms once materials allow. [start] https://rimworldwiki.com/wiki/Room
- Build dining with tables and chairs before day 5; eating without a table gives a mood debuff. [base-and-fortress] https://rimworldwiki.com/wiki/Room
- Give dining/rec rooms >= 40 tiles (beauty is penalised under 40 tiles). [base-and-fortress] https://rimworldwiki.com/wiki/Room
- THRESHOLD: hospital cleanliness >= 0.4 (Sterile) and light 50%; separate room with hospital/medical beds. [base-and-fortress] https://rimworldwiki.com/wiki/Room
- THRESHOLD: workshop temperature 10-35C, else work speed drops to 70%. [base-and-fortress] https://rimworldwiki.com/wiki/Temperature
- Build the first research bench by day 3 in its own clean, lit room (laboratory role). [research] https://rimworldwiki.com/wiki/Room
- Smooth stone floors and walls in mountain rooms to raise beauty and impressiveness for free. [growth] https://rimworldwiki.com/wiki/Room

## Doors and airlocks
- Use a double door (two doors in series with a 1-tile vestibule) on freezers, hospitals and heated rooms in extreme biomes. [base-and-fortress] https://rimworldwiki.com/wiki/Temperature
- Never hold doors open on freezers or heated rooms; open doors and vents equalise temperature quickly. [base-and-fortress] https://rimworldwiki.com/wiki/Temperature
- Build freezer and outer walls two layers thick; two layers halve heat exchange, more layers add nothing. [base-and-fortress] https://rimworldwiki.com/wiki/Temperature
- Replace corridor doors with autodoors once researched; they open faster. [research] https://rimworldwiki.com/wiki/Autodoor
- Restrict door access to prisoner/guest wings and the armoury. [base-and-fortress] https://rimworldwiki.com/wiki/Door

## Lighting
- THRESHOLD: light < 30% = "In darkness" mood debuff plus work-speed penalty; keep every work/living tile >= 30%. [base-and-fortress] https://rimworldwiki.com/wiki/Standing_lamp
- Place one standing lamp (30W, 15W after Advanced Lights) per ~7-tile radius; lamps never exceed 50%. [base-and-fortress] https://rimworldwiki.com/wiki/Standing_lamp
- Light the operating room to 50% for surgery success. [base-and-fortress] https://rimworldwiki.com/wiki/Standing_lamp
- THRESHOLD: indoor crops need >= 51% light; only sun lamps give it (high power, run daytime only). [growth] https://rimworldwiki.com/wiki/Sun_lamp
- Put sun lamps and hydroponics on a switched circuit; they are the first load to cut in a power shortage. [base-and-fortress] https://rimworldwiki.com/wiki/Power

## Cleanliness
- THRESHOLD: cleanliness < -0.4 Dirty, < -1.1 Very dirty; target >= -0.05 (Clean) in kitchen, dining, hospital. [base-and-fortress] https://rimworldwiki.com/wiki/Room
- Floor kitchen and hospital (smoothed stone, then sterile tile); dirty kitchens raise food poisoning. [base-and-fortress] https://rimworldwiki.com/wiki/Food_poisoning
- Keep the butcher table out of the kitchen (it makes filth); place it next to the freezer instead. [base-and-fortress] https://rimworldwiki.com/wiki/Butcher_table
- Keep at least one pawn on Cleaning once the colony has more than 3 rooms. [configuration] https://rimworldwiki.com/wiki/Work
- Floor the entrance paths and keep a home area over all buildings so dirt is cleaned. [base-and-fortress] https://rimworldwiki.com/wiki/Home_area

## Power
- Start power with a wood-fired generator (1000W, 22 wood/day) or wind turbine (2300W peak, clear 7x2 plus lanes); solar is 1700W daytime only. [base-and-fortress] https://rimworldwiki.com/wiki/Power
- Build geothermal (3600W, no fuel) on any steam geyser once researched; watermill (1100W) on riverbanks. [base-and-fortress] https://rimworldwiki.com/wiki/Power
- Keep a chemfuel generator (1000W, 4.5 chemfuel/day) as backup only. [base-and-fortress] https://rimworldwiki.com/wiki/Power
- THRESHOLD: keep generation >= 1.25x continuous demand; if stored energy < one night of demand, add generation or batteries. [base-and-fortress] https://rimworldwiki.com/wiki/Power
- Build batteries (600 Wd each, 50% efficiency, -5 Wd/day) to bridge nights for solar and calm for wind. [base-and-fortress] https://rimworldwiki.com/wiki/Power
- Roof every battery and outdoor electrical building; unroofed electrics short-circuit in rain or snow. [base-and-fortress] https://rimworldwiki.com/wiki/Events
- Split battery banks with power switches; a short circuit with >= 20 Wd stored explodes (radius 1.5-14.9 tiles) and drains the banks. [base-and-fortress] https://rimworldwiki.com/wiki/Events
- Use hidden/waterproof conduits for main runs once researched to stop conduit short circuits. [research] https://rimworldwiki.com/wiki/Events
- Keep batteries in a stone-walled, stone-floored room away from bedrooms and stockpiles. [base-and-fortress] https://rimworldwiki.com/wiki/Battery
- During a solar flare (0.15-0.5 days) electrics, heaters, coolers and turrets stop; keep campfire/passive cooler and pawn weapons ready. [survival] https://rimworldwiki.com/wiki/Events
- During an eclipse (0.75-1.25 days) solar gives 0; keep batteries >= one day of demand. [survival] https://rimworldwiki.com/wiki/Events

## Heaters, coolers, temperature targets
- THRESHOLD: human comfort 16-26C before clothing; hypothermia/heatstroke start 10C past the pawn's comfort range. [survival] https://rimworldwiki.com/wiki/Temperature
- Set living-room heaters and coolers to 21C. [survival] https://rimworldwiki.com/wiki/Temperature
- THRESHOLD: freezer must hold < 0C (spoilage stops at 0C, slows below 10C); target -5C to -10C for margin. [survival] https://rimworldwiki.com/wiki/Temperature
- Give freezers over ~50 tiles or in hot biomes two coolers (0C and -2C), double walls and a double door. [survival] https://rimworldwiki.com/wiki/Temperature
- Mount coolers in a wall with the hot side exhausting outdoors, never into another room. [base-and-fortress] https://rimworldwiki.com/wiki/Cooler
- Put one heater in each living room in cold biomes; add a second when outdoors < -20C. [survival] https://rimworldwiki.com/wiki/Heater
- Use a passive cooler (holds ~17C, 5 days per wood load) when no power exists. [survival] https://rimworldwiki.com/wiki/Temperature
- Use a campfire for day-1 heat and cooking only; it cannot heat past 30C. [start] https://rimworldwiki.com/wiki/Temperature
- THRESHOLD: crops slow < 6C, stop at 0C, die at -10C; slow > 42C, stop at 58C. [growth] https://rimworldwiki.com/wiki/Temperature
- THRESHOLD: fermenting barrel -1C to 32C; eggs viable 0-50C. [economy] https://rimworldwiki.com/wiki/Temperature
- Hold overhead-mountain storage at -17C or colder where power allows to block infestations there. [base-and-fortress] https://rimworldwiki.com/wiki/Infestation
- Use vents, not open doors, to share heat between rooms on purpose. [base-and-fortress] https://rimworldwiki.com/wiki/Temperature

## Fire
- Build kitchens, battery rooms and smelter/crematorium rooms from stone; wood burns. [base-and-fortress] https://rimworldwiki.com/wiki/Fire
- THRESHOLD: items ignite around 235C; vent or extinguish before a room reaches it. [survival] https://rimworldwiki.com/wiki/Temperature
- Give every capable pawn Firefighting at priority 1 and keep a home area over all buildings. [configuration] https://rimworldwiki.com/wiki/Fire
- Place firefoam poppers in battery, stockpile and kitchen rooms once researched. [base-and-fortress] https://rimworldwiki.com/wiki/Firefoam_popper
- Clear a 3+ tile firebreak of grass/trees around the base and fields. [survival] https://rimworldwiki.com/wiki/Fire
- Store chemfuel and mortar shells in a separate walled store away from bedrooms. [base-and-fortress] https://rimworldwiki.com/wiki/Chemfuel

## Events
- Cold snap (1.5-3.5 days, -20C): heat bedrooms, dress pawns in parkas/tuques, harvest crops before -10C. [survival] https://rimworldwiki.com/wiki/Events
- Heat wave (1.5-3.5 days, +17C): add coolers/passive coolers, confirm freezer stays < 0C, watch for fires. [survival] https://rimworldwiki.com/wiki/Events
- THRESHOLD: toxic fallout (2.5-10.5 days, not before day 60): keep pawns roofed; pull any pawn inside at toxic buildup >= 40%; harvest unroofed crops. [survival] https://rimworldwiki.com/wiki/Events
- Blight: cut blighted plants at once; it spreads 3-4 tiles, so split fields with gaps. [growth] https://rimworldwiki.com/wiki/Events
- Volcanic winter (7.5-40 days, -7C, -30% light, not before day 60): stockpile >= 20 days of food and build a heated, lit greenhouse. [survival] https://rimworldwiki.com/wiki/Events
- Flashstorm: keep pawns out of the storm radius, firefight once it ends. [survival] https://rimworldwiki.com/wiki/Events
- Solar flare: do not start fights relying on turrets; harvest hydroponics if power stays off. [war] https://rimworldwiki.com/wiki/Events
