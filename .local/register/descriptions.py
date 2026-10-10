import io, re

M = 'Mod/Rimrooms - Async Industries/1.6/'

# --- facility categories ---------------------------------------------------
# Each says what the category is for and what goes wrong for a branch without it, because a
# facilities overview whose rows are bare nouns tells a player nothing they did not already
# know from the word.
facility = {
 'RR_Facility_Quarters':
   'Where staff sleep. A branch short of beds runs its people tired, and a tired operator is '
   'the one standing at the console when a connection needs holding.',
 'RR_Facility_Medical':
   'Where injuries are treated. Crews come back hurt more often than not, and a hospital bed '
   'with a vitals monitor beside it is the difference between a recovery and a grave.',
 'RR_Facility_Mess':
   'Where food is cooked and eaten. Stock arriving by procurement is raw; somebody has to turn '
   'it into meals, and a branch eating off the floor loses morale it cannot spare.',
 'RR_Facility_Recreation':
   'Where staff recover from what they have seen. Time spent past a gate is not restful, and a '
   'branch with nowhere to sit is a branch with breakdowns waiting in it.',
 'RR_Facility_Laboratory':
   'Where what you carry back is studied. Company projects are worked at a research bench you '
   'have designated, and an unstudied find is a curiosity rather than an advantage.',
 'RR_Facility_Workshop':
   'Where materials become equipment. The gate assembly is worked at a machining table, and '
   'everything a crew carries through was made at one of these first.',
 'RR_Facility_Machine':
   'The gate itself and the station it is run from. A designated door, a comms console to '
   'operate it, a machining table to assemble it and a switch that can cut it. Without all '
   'four, a branch has a door rather than a gate.',
 'RR_Facility_Power':
   'What keeps the lights on and a connection open. A gate draws heavily while open and draws '
   'more the wider it is, and it is fed from the battery you bound to it rather than from the '
   'grid directly.',
 'RR_Facility_Storage':
   'Where stock is kept off the floor. Shelving decides how much a branch can actually hold '
   'and how quickly haulers can find what a bill is short of.',
}

p = M + 'Defs/RimroomsFacilityDefs/RR_FacilityCategories.xml'
s = io.open(p, encoding='utf-8-sig').read()
for name, text in facility.items():
    marker = '<defName>%s</defName>' % name
    assert marker in s, name
    assert ('<description>' not in s.split(marker)[1].split('</RimroomsAsyncIndustries')[0])
    # Description goes straight after the label on the same compact line style this file uses.
    pattern = re.compile(r'(<defName>%s</defName><label>[^<]*</label>)' % re.escape(name))
    s, n = pattern.subn(r'\1<description>' + text + '</description>', s, count=1)
    assert n == 1, name
io.open(p, 'w', encoding='utf-8-sig', newline='').write(s)
print('facility categories described')

# --- procurement catalogue -------------------------------------------------
# Lead time and price are already on the row; the description says what the thing is FOR,
# which is the part a player cannot read off a number.
procurement = {
 'RR_Procurement_Silver':
   'Ordinary silver, bought rather than dug. The company sells it at a poor rate because you '
   'are paying for delivery to a branch that has no mine.',
 'RR_Procurement_Steel':
   'Structural steel. Everything a branch builds and most of what it repairs is made of this, '
   'and a gate assembly that lapses cannot be reconditioned without it.',
 'RR_Procurement_Components':
   'Industrial components. The limiting part of almost every machine worth having, and the one '
   'thing a branch is most likely to be short of at the worst moment.',
 'RR_Procurement_Wood':
   'Wood logs. Cheap, flammable and useful, and the fastest way to put a floor and a few walls '
   'up around a gate before the first connection is opened.',
 'RR_Procurement_Cloth':
   'Plain cloth. Clothing, bedding and the soft parts of a branch that keep people working; '
   'also the material the yellow rooms are remembered for.',
 'RR_Procurement_Medicine':
   'Industrial medicine. Crews come back from a coordinate needing it more reliably than they '
   'come back with anything worth selling.',
 'RR_Procurement_SurvivalMeals':
   'Packaged survival meals. They keep indefinitely and need no kitchen, which is the entire '
   'reason to carry them through a gate instead of cooking.',
}

p = M + 'Defs/RimroomsProcurementCatalogDefs/RR_ProcurementCatalog.xml'
s = io.open(p, encoding='utf-8-sig').read()
for name, text in procurement.items():
    pattern = re.compile(r'(<defName>%s</defName>\s*\n(\s*)<label>[^<]*</label>)' % re.escape(name))
    match = pattern.search(s)
    assert match, name
    indent = match.group(2)
    s = pattern.sub(lambda m: m.group(1) + '\n' + indent + '<description>' + text + '</description>', s, count=1)
io.open(p, 'w', encoding='utf-8-sig', newline='').write(s)
print('procurement catalogue described')
