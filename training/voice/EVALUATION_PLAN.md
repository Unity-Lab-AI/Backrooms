# Reserved final listening evaluation

Prepared 2026-10-11. This is a future evaluation text suite, not synthesized audio or evidence of a trained voice.

## Reservation and format

Keep `LISTENING_EVAL_TEXT.jsonl` out of teacher dataset construction, acoustic/vocoder training and normalization. Its 38 cases have zero normalized lexical overlap with the existing combined 1,378 planned training rows. Two statement/question pairs intentionally share evaluation-only lexical groups.

Every row has exactly `id`, `text`, `emotion`, `intensity`, `pace` and `speech_act`. IDs include a stable content hash. Neutral intensity is 0.0; other intended states use 0.35. Pace is 1.0. These are the current narrow training intentions, not calibrated control ranges.

Suite SHA256: `32e3b1287df1e93c4ea022db1e57e048af909c75315480929f78cfb421cf0481`.

The suite covers all nine intended spoken states and all seven speech acts: two brief turns, two ordinary/question contrast pairs, two laughter-marked cases, four name/number/coder pronunciation cases and one long paragraph. The long paragraph has 174 words; duration is unmeasured. It is intended to exercise a turn exceeding 30 seconds, but that criterion must be checked against actual audio.

## Exact cases

| ID | Intended state / act | Text |
| --- | --- | --- |
| `eval_ordinary_215eb6a5c64c` | neutral / statement | The spare adapter belongs in the lower tray. |
| `eval_yesno_0cfda4f236f1` | neutral / yes_no_question | Did the blue indicator stay on? |
| `eval_wh_d53b2ccca95b` | neutral / wh_question | Which connection came loose first? |
| `eval_company_65adb5ca8a55` | warm / statement | It's nice to have someone to puzzle this out with. |
| `eval_support_c9caac37b9e0` | warm / reassurance | You can tell me when the explanation gets too dense. |
| `eval_gentle_start_9a21d874512b` | warm / instruction | Start with whichever part feels comfortable. |
| `eval_quiet_pleased_f8dbb135a58d` | happy / statement | That little change made the whole room feel brighter. |
| `eval_pleased_lift_1625059e0943` | happy / exclamation | Oh, the pieces finally line up neatly! |
| `eval_happy_chuckle_d84702a0b9d9` | happy / aside | [laughter] We solved it before I could complicate the plan. |
| `eval_dry_humor_1319e611ba03` | amused / aside | The tidy pile has quietly become a cable habitat. |
| `eval_amused_question_b445c111e6d5` | amused / yes_no_question | Did the cat just claim the entire help desk? |
| `eval_amused_chuckle_3a709544e60b` | amused / statement | I found the missing note beneath my very organized notes. [laughter] |
| `eval_anticipation_ce01b959ff4a` | excited / statement | I want to see what the next corridor leads to. |
| `eval_eager_next_6b03d3523ff4` | excited / instruction | Let's try the new route while the gate is ready. |
| `eval_breakthrough_d1b126e63e5c` | excited / exclamation | Oh, that opens up a whole new possibility! |
| `eval_disappointed_e1fcca027c69` | sad / statement | I thought we'd have a little more time there. |
| `eval_gentle_loss_question_1c814d2c5c56` | sad / wh_question | What do you wish we could have kept? |
| `eval_quiet_reassurance_4145a12eb736` | sad / reassurance | You don't need to make this feel better right away. |
| `eval_caution_fddd2a2bb83f` | concerned / statement | The return marker is harder to see from this angle. |
| `eval_safety_question_c09da98cd6ab` | concerned / yes_no_question | Is there enough room for everyone to get back? |
| `eval_cautious_instruction_c972f6dd2752` | concerned / instruction | Check the loose panel before we lean anything against it. |
| `eval_mild_irritation_28d3e4d15399` | frustrated / statement | That same tiny problem has interrupted us three times. |
| `eval_frustrated_question_0a6d4afc7a6a` | frustrated / wh_question | Why did the menu forget the choice we just made? |
| `eval_not_blame_4e7b64893894` | frustrated / reassurance | I'm frustrated with the delay; you haven't done anything wrong. |
| `eval_unexpected_082d84372fb6` | surprised / statement | I thought that space ended at the far wall. |
| `eval_surprised_question_65e0d0da5499` | surprised / yes_no_question | Was that drawer always built into the side? |
| `eval_unexpected_space_3bbd8fe6c394` | surprised / exclamation | Oh, there's an entire shelf behind that panel! |
| `eval_bridge_statement_2937cdfb801d` | neutral / statement | You're taking the narrow bridge. |
| `eval_bridge_question_a2a34d0a6087` | neutral / yes_no_question | You're taking the narrow bridge? |
| `eval_latch_statement_9e2f48910af5` | neutral / statement | That latch is working. |
| `eval_latch_question_c00d8c22df66` | neutral / yes_no_question | That latch is working? |
| `eval_brief_neutral_16f71faec20a` | neutral / statement | Sounds sensible. |
| `eval_brief_warm_d8676d513285` | warm / statement | Lovely, thanks. |
| `eval_names_bays_1ec86195f282` | neutral / statement | Mira marked bay 12, and Tobin checked bay 20. |
| `eval_fifteen_fifty_96708f687463` | neutral / instruction | Bring 15 boards, not 50. |
| `eval_time_date_6e3a385df8d5` | neutral / yes_no_question | Is the meeting at 8:30 on October 12? |
| `eval_coder_names_54d835d13755` | neutral / yes_no_question | Did Kade use Python or C sharp for the Rimrooms tool? |
| `eval_chunk_long_8ed990a08ad6` | neutral / statement | Here's where the little project stands this afternoon. We have a working first version, a short list of changes, and enough notes to explain why we chose the simpler route. The button now uses the same label in both menus, and the drawer opens without catching on the cable. I kept the older copy because comparing the two makes the improvement easier to understand. There is still one awkward corner near the window, but it can wait until we have finished the parts people use every day. The next pass will focus on clear names, useful messages, and an easy way to undo a mistaken choice. Nobody needs to remember the whole arrangement at once. A good starting point is enough, and the rest can become familiar through use. I would rather take a little extra time now than leave someone guessing later. When we stop for the evening, the notes will say what works, what needs another look, and where to begin tomorrow. That should make coming back feel comfortable instead of confusing. |

## Listening protocol

Render only after an identity-bound student pair exists and rendering is authorized. Keep this reserved suite distinct from training-heldout reconstruction/prosody probes. Record exact pair/checkpoint hashes, voice identity, actual delivery support, frontend/environment, source text and per-case output hashes.

Begin each short listening group with the approved original A2 reference, then use equal listening level without pitch shift, time stretch, synthetic emotion effects or aggressive processing. Ask for exceptions by case ID rather than making the owner navigate hundreds of examples.

1. Ordinary, brief and contrast cases: mature low-register A2 identity, comfortable conversational pace, connected words, natural endings and question timing. Yes/no questions often rise; wh-questions can fall. Do not force every question upward.
2. Warm, happy, amused and excited cases: distinguish friendly warmth, quiet pleasure, dry amusement and actual eagerness without perpetual high pitch, cartoon delivery or sarcasm. Keep the same speaker through the changes.
3. Sad, concerned and frustrated cases: distinguish quiet disappointment, attentive caution and mild irritation. Frustration is directed at the problem, not the listener; concern must not simply become sadness. No sobbing or theatrical distress is requested.
4. Surprise: a modest responsive lift that remains adult and intelligible, not a new high-pitched character.
5. Names and numbers: hear Mira, Tobin, Kade, Python, C sharp and Rimrooms clearly; distinguish 15 from 50, bay 12 from bay 20 and the time/date. Accept ordinary American English equivalents such as eight thirty; do not require one mechanical reading.
6. Laughter: run the two marked cases only if the actual TRAIN feature manifest contains accepted laughter supervision and the pair advertises that event support. A short audible chuckle must occur at the marked position; a voiced smile or spoken word laughter does not satisfy it. No giggle subtype is asserted.
7. Long turn: use bounded runtime chunking. Preserve complete wording, punctuation, ordering, one identity and natural gaps between chunks. Record source case ID, ordered chunk texts/IDs/hashes and total actual duration. A truncated or unrendered case is not a pass.

## Source API and limits

The architecture review reports source support for `Voice.say(text, emotion, intensity, pace, speech_act)` with optional out-of-band `pauses` and `focus=None`. Non-None word focus is refused because there is no word-level supervision. This is a source contract; the untrained student has not demonstrated the behavior.

The long case ID starts `eval_chunk_long_`. Current source plans chunks of at most 240 characters at punctuation/whitespace, without splitting event markers, with limits of 12,000 input characters, 64 chunks and 120 seconds of output. One explicit speech act applies to all chunks; absent intent is inferred per chunk. The long case uses neutral statements throughout to avoid hiding mixed intents in one label.

Automatic joins use 80 ms of silence and 5 ms edge fades. These are mechanical timing choices, not learned breaths or evidence of natural joins. The long case must evaluate whether the actual result remains comfortable. Explicit pauses, if separately evaluated, are 50 ms to 2 seconds after a unique exact phrase, at most 16; retain their schedule in the result artifact. No pause markup is present in this JSONL.

There is no word-focus, SSML, manual pitch-contour, whisper, sobbing, breath or multiple-laugh-type command in these rows. Natural stress is evaluated by listening, not requested through unsupported syntax. Wider intensity/pace ranges and continuous emotional interpolation remain uncalibrated and must not be inferred from these fixed settings.

## Outcomes and evidence

For each heard case record accepted/rejected/relabel or pending with the actual reviewer, output hash and brief reason. Correct words, identity, intended delivery, nonverbal events and listening comfort are separate criteria. Unheard, unsupported or failed cases remain pending; an ASR match or low loss is not listening acceptance.

Source voices and the 32 heard pilot recordings were approved. That does not establish trained-student acceptance, approval of every future source row, performance on this reserved suite or permission to provision a pod. The owner explicitly prohibited starting training and renting a pod while preparation is finished.

Only JSON/text authoring and metadata comparison were performed to create this suite. No ASR/model execution, audio generation, training or acoustic test was performed.
