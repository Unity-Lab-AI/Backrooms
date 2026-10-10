# -*- coding: utf-8 -*-
"""Rewrite every player-facing string that names equipment this mod retired.

Fifteen strings, found by `tools/check-retired-content.py` rather than by eye -- six more than
reading the language files turned up. Three of them are dead keys for defs that no longer exist
and are deleted; the other twelve are reworded to name what the mod actually has.

The vocabulary is taken from strings already shipped, not invented here:

    RR_Event_CorridorUnmarked   "Set a glow pod down at that junction and mark it as the route
                                 home, then come back and compare."
    RR_Marker_DesignateDesc     "Designate this glow pod as a route marker ... There is no limit
                                 on how many you place."
    RR_Portals_Explanation      "the saved return threshold of a Backrooms coordinate"

Two substitutions are NOT rewords, and are called out because getting them wrong would ship an
instruction that cannot be followed:

  * **custody is a place now.** "return it with the evidence case" becomes "bring it to the shelf
    designated as the records archive". The player does something different, not something
    differently worded.
  * **a marker is still numbered.** `CompRimroomsMarker.Number` is live, so the numbering survived
    the survey tag. "numbered tag" becomes "numbered marker", never nothing.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEYED = os.path.join(REPO, 'Mod', 'Rimrooms - Async Industries', '1.6', 'Languages', 'English', 'Keyed')

# (file, key, new value) -- the whole value is replaced, so each is readable as the shipped text.
REWRITES = [
    ('RR_Company.xml', 'RR_UI_ContractTerms',
     u'Survey the route, record the distortion, recover the record book and analyse it at '
     u'headquarters. The optional bonus requires all three crew to return with route, distortion '
     u'and entity observations. Combat is optional; a recoverable injury does not cancel the bonus.'),

    ('RR_FieldAndThreats.xml', 'RR_Event_CorridorMismatch',
     u'{0}: a door repeats the last room’s label, but the route counter disagrees. Stop and '
     u'compare the markers a crew has actually placed. The last validated junction is room {1}; a '
     u'numbered marker there identifies the safe route, and the coordinate’s own return '
     u'threshold is the way out. Continuing deeper risks a loop.'),

    ('RR_FieldAndThreats.xml', 'RR_UI_FieldObjectives',
     u'Survey the six required room families with the record book, document the route mismatch, '
     u'carry the book home and shelve it in the records archive. A clear entity observation and all '
     u'three original crew returning qualify for the bonus. Set glow pods down at known junctions '
     u'and designate them as route markers to counter the loop.'),

    ('RR_FieldAndThreats.xml', 'RR_UI_RecoverEvidence',
     u'Order {0} to collect the record book'),

    ('RR_Generation.xml', 'RR_Clue_Text_borrowed_corridor',
     u'The paired planters offer a familiar shape without a reliable direction. Compare the real '
     u'numbered markers with their recorded rooms when the route changes.'),

    ('RR_Generation.xml', 'RR_Clue_Text_office_copy',
     u'Two workstations repeat the same arrangement. The record book is stored separately in this '
     u'room; pick it up and carry it back for analysis.'),

    ('RR_Generation.xml', 'RR_Clue_Text_service_passage',
     u'A shelf and disconnected standing lamp mark this passage. Set a glow pod down at a verified '
     u'junction and designate it as a numbered route marker before proceeding into the Borrowed '
     u'Corridor.'),

    ('RR_Investigation.xml', 'RR_Event_EvidenceSecured',
     u'The record book is at headquarters. Complete the route and distortion observations, shelve '
     u'it in the records archive, then assign a researcher to analysis.'),

    ('RR_Investigation.xml', 'RR_Observation_room_survey',
     u'Room {0}: surveyed with the crew’s record book in hand.'),

    ('RR_Investigation.xml', 'RR_UI_EvidenceFieldWorkRemaining',
     u'Carry the record book through each required room. At the corridor junction, set a glow pod '
     u'down and designate it as a numbered marker before investigating the next passage. A second '
     u'marker at the last good junction gives you something stable to compare against. Incomplete '
     u'observations can be finished on a later trip to the same site.'),

    ('RR_OperationsExpeditions.xml', 'RR_UI_NextAnalysis',
     u'Assign Research work to an available staff member with Intellectual 4. Keep the record book, '
     u'the shelf designated as the records archive, and a powered analysis bench at headquarters. '
     u'Completed analysis settles the survey once.'),

    ('RR_OperationsExpeditions.xml', 'RR_UI_NextRecoverEvidence',
     u'Return the record book to headquarters and shelve it in the records archive. A missing item '
     u'stays missing until recovered; another opening does not produce a copy.'),
]

# Dead keys: the defs they labelled were retired, and grep confirms nothing references them.
DELETIONS = [
    ('RR_Generation.xml', 'RR_Generation_ClimateUnitLabel'),
    ('RR_Generation.xml', 'RR_Generation_FluorescentLabel'),
    ('RR_Generation.xml', 'RR_Generation_FluorescentDescription'),
]


def path_of(name):
    return os.path.join(KEYED, name)


def replace_value(text, key, value):
    open_tag = u'<%s>' % key
    close_tag = u'</%s>' % key
    start = text.index(open_tag)
    end = text.index(close_tag, start)
    return text[:start + len(open_tag)] + value + text[end:]


def delete_key(text, key):
    open_tag = u'<%s>' % key
    close_tag = u'</%s>' % key
    start = text.index(open_tag)
    end = text.index(close_tag, start) + len(close_tag)
    # Take the whole line, including its indentation and newline.
    line_start = text.rfind(u'\n', 0, start) + 1
    line_end = text.index(u'\n', end) + 1
    return text[:line_start] + text[line_end:]


rewritten = 0
for name, key, value in REWRITES:
    text = io.open(path_of(name), encoding='utf-8').read()
    assert u'<%s>' % key in text, '%s: %s missing' % (name, key)
    assert text.count(u'<%s>' % key) == 1, '%s: %s not unique' % (name, key)
    io.open(path_of(name), 'w', encoding='utf-8', newline='').write(replace_value(text, key, value))
    rewritten += 1

deleted = 0
for name, key in DELETIONS:
    text = io.open(path_of(name), encoding='utf-8').read()
    assert u'<%s>' % key in text, '%s: %s missing' % (name, key)
    io.open(path_of(name), 'w', encoding='utf-8', newline='').write(delete_key(text, key))
    deleted += 1

print('rewritten %d string(s), deleted %d dead key(s)' % (rewritten, deleted))
