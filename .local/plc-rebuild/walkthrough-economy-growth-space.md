# Walkthrough distillation: economy, research, growth, animals, space
# One rule per line: [family] imperative rule -- threshold -- source (W = https://rimworldwiki.com/wiki/)

## Research order to the ship
[research] Build a simple research bench by day 3; keep 1 researcher (highest Intellectual) on it full time -- W Research
[research] Early order: Battery -> Passive cooler -> Complex furniture -> Stonecutting -> Smithing -> Machining -> Microelectronics -- W Research
[research] After Microelectronics build the hi-tech research bench, then research Multi-analyzer and build one beside it -- W Hi-tech_research_bench
[research] Mid order: Gun turrets -> Air conditioning -> Hydroponics -> Multi-analyzer -> Fabrication -> Advanced fabrication -> Mortars -- W Research
[research] Ship tree: Starflight basics -> Ship basics -> Ship cryptosleep -> Ship reactor -> Ship engine -> Ship computer core -> Ship sensor cluster -- W Research
[research] Advanced component = 1 plasteel + 2 components + 20 steel + 3 gold at fabrication bench (needs Fabrication) -- W Advanced_component
[research] Keep research room clean, lit, floored, 15-24C; dirty room slows research -- W Research_speed

## Production chains
[economy] Food chain: crops/hunt -> freezer -> butcher table + stove -> dining room; keep >= 10 meals per colonist -- W Meal
[economy] Freezer must stay below -1C (target -10C to -5C); raw food rots fast above 10C -- W Freezer
[economy] Meal bill "do until X": X = 10-15 per colonist (owner value 50); fine meals once Cooking >= 6 -- W Bills
[economy] Butcher table next to freezer; butcher corpses within 1 day -- W Butcher_table
[economy] Plant rice first (fastest growth ~3 days), corn for long storage, healroot when a grower has Plants >= 8 -- W Rice_plant
[economy] Cotton -> cloth -> tailoring bench: parkas before winter, dusters for heat; 1 spare set per colonist -- W Tailoring_bench
[economy] Stockpile >= 200 wood before first winter for stove/heaters -- W Wood
[economy] Smithing bench for melee, machining table for guns and to smelt/scavenge -- W Machining_table
[economy] Electric smelter on slag when steel < 300 -- W Electric_smelter
[economy] Deep drill + ground-penetrating scanner once surface steel/plasteel/uranium run out -- W Deep_drill
[economy] Drug lab output is trade goods only (colonists on No drugs per owner policy) -- W Drug_lab
[economy] Stonecutter table: keep >= 200 stone blocks for fireproof walls -- W Stonecutter%27s_table

## Trade / silver / vault
[economy] Build comms console after Microelectronics to call orbital traders and factions -- W Comms_console
[economy] Orbital trade beacons must cover the sell stockpile (radius ~7.9) -- W Orbital_trade_beacon
[economy] Sell art, clothes, drugs, devilstrand, non-tainted raid gear; buy components, plasteel, advanced components, neutroamine -- W Trade
[economy] Trader = highest Social colonist (sets prices) -- W Trade
[economy] Vault silver in a locked inner room, 2-thick walls; silver is wealth and raises raid size -- W Wealth_management
[economy] Raid points scale with wealth: burn/sell tainted apparel and junk rather than hoard -- W Raid_points
[economy] Sculptor's table art with Artistic >= 6 for high-value trade -- W Art

## Recruitment and colonist growth
[growth] Prepare prisoner bed in a closed room before a fight; capture downed raiders and treat them -- W Prisoner
[growth] Prisoner mode Reduce resistance then Recruit; warden = highest Social -- W Recruitment
[growth] Keep prisoner mood > 35% (bed, food, 15-24C) to avoid break/escape -- W Prisoner
[growth] Accept wanderer/refugee quests unless pursuers exceed colony defence -- W Quests
[growth] Target 6-8 colonists by year 1, 10-15 by ship time; ship holds max 25 caskets -- W Ship
[growth] Recruit to fill skill gaps (Construction, Mining, Cooking, Medicine); avoid pyromaniac / incapable of violence as fighters -- W Traits
[growth] Keep 1 spare bed per expected recruit; bedroom interior >= 2x3 -- W Bedroom

## Mood / recreation / beauty
[growth] Private bedroom each (avoid shared-barracks debuff) once materials allow -- W Bedroom
[growth] Dining room with table + chairs (avoid "ate without table") -- W Table
[growth] Recreation: horseshoes pin days 1-3, then chess/billiards/TV; >= 2 recreation types -- W Recreation
[growth] Floors, lights, clean rooms; cleaning priority on low-skill pawns -- W Beauty
[growth] Impressive dining/rec room: art + floors + >= 30 tiles -- W Room_stats
[growth] Mental breaks: minor < 35%, major < 20%, extreme < 5% mood; intervene below 35% -- W Mental_break
[growth] Indoor 15-24C all year; heaters in winter, coolers in summer -- W Temperature
[growth] Hospital room with hospital beds; doctor = highest Medicine; keep >= 10 medicine -- W Hospital_bed

## Animals
[animals] Hunt when food < 5 days and safe game is on map; never hunt boomalopes near base, thrumbos or packs -- W Hunting
[animals] Fenced animal area with sleeping spots once Animals >= 5 -- W Animals
[animals] Good tames: muffalo/dromedary (wool, milk, pack), chickens (eggs), huskies/labradors for war -- W Animals
[animals] Kibble: 50 meat/eggs + 50 hay/rice -> 75 kibble; feed animals kibble not meals -- W Kibble
[animals] Plant haygrass for grazers in growing season -- W Haygrass
[animals] Slaughter excess animals in autumn when count > winter food capacity -- W Animals

## Ship building and launch defence
[space] Ship: 1 reactor, 3 engines, 1 computer core, 1 sensor cluster, 1+ cryptosleep caskets, structural beams connecting; min ~1740 steel, 740 plasteel, 294 uranium, 40 advanced comps, 12 comps, 74 gold, 1 persona core -- W Ship
[space] Persona core from ancient shrines, crashed ship parts or exotic traders -- W AI_persona_core
[space] Build ship inside/adjacent to the fortified base -- W Ship
[space] Reactor startup = 15 days of constant human+mech raids -- W Ship
[space] Before reactor: turrets + kill box + mortars, food >= 30 days, medicine >= 20, every colonist armed -- W Ship
[space] Do not build parts early: each part raises wealth and raid size -- W Ship
[space] One casket per colonist/animal leaving; load all before launch -- W Ship
[space] Alternatives: journey offer ship (18 colonists), royal ascent, archonexus, void endings -- W Ending

## PLC thresholds
[meta] research_bench_count == 0 and day >= 3 -> build research bench
[meta] freezer temp > -1C -> add/repair cooler
[meta] meals < 10 x colonists -> raise meal bill
[meta] any mood < 0.35 -> recreation/rest priority
[meta] wealth rising and defence weak -> spend silver on arms/turrets before vault
[meta] ship research done and plasteel >= 740 and uranium >= 294 and advanced comps >= 40 -> build ship parts
[meta] all ship parts built and defence ready -> activate reactor
