"""Write the planned text corpus for the accepted A2 speech identity.

This creates text and documentation only. It never synthesizes audio, starts a
service, trains a model, or marks a performance approved. Delivery labels are
authoring intentions until the corresponding source audio has been reviewed.

Run: python training/voice/build_corpus.py
"""
import collections
import hashlib
import json
from pathlib import Path

from dataset_contract import EMOTIONS, SPEECH_ACTS, delivery, normalize_transcript, split_for

HERE = Path(__file__).resolve().parent
ROWS = []
SEEN = set()


def add(emotion, act, text):
    text = " ".join(text.strip().split())
    normalized = normalize_transcript(text)
    if not normalized or normalized in SEEN:
        return
    style = delivery(emotion, 0.0 if emotion == "neutral" else 0.35, 1.0, act)
    identity = hashlib.sha256((normalized + "|" + emotion + "|" + act).encode()).hexdigest()[:20]
    ROWS.append({"id": "speech_" + identity, "text": text, **style})
    SEEN.add(normalized)


def lines(emotion, act, text):
    for utterance in text.split("|"):
        add(emotion, act, utterance)


def series(emotion, act, pattern, choices):
    for choice in choices.split("|"):
        add(emotion, act, pattern.format(x=choice.strip()))


def everyday():
    lines("neutral", "statement", "Yeah.|Yep.|Okay.|All right.|Got it.|I see.|Fair enough.|That makes sense.|I'm here.|I'm listening.|One second.|Just a moment.|Let me think.|I have the file open.|The kettle is on.|The window is a little stiff.|I saved a copy before changing it.|We're looking at the same screen.|I can hear you now.|The connection is back.|The volume is fine on my end.|I moved the chair out of the way.|The next room is on the left.|That takes about ten minutes.|I've already checked the first two.|There's a spare in the drawer.|It's a little cooler outside today.|I'm going to stretch my legs.|We can leave the rest until morning.|I wrote down where we stopped.|The room is quieter with the fan off.|My coffee is still a bit hot.|I'll put this back where it belongs.|The second cable is the longer one.|I think that covers the basics.")
    lines("neutral", "yes_no_question", "Are you there?|Can you hear me?|Is this yours?|Did that help?|Are we ready?|Does that fit?|Have you saved it?|Is the sound clear?|Do you need a minute?|Should I leave this open?|Did you mean the other one?|Can I move your chair a little?|Are you using this cable?|Is it supposed to stay on?|Would you rather do this tomorrow?")
    lines("neutral", "wh_question", "What changed?|Where were we?|Which one?|How does that work?|When did it stop?|What are you looking at?|Where should this go?|How much time do we have?|What would you change first?|Which part feels off?|Where did you last see it?|How did you solve that?|What do you want to keep?|When are you heading out?|Who should I ask about this?")
    lines("neutral", "instruction", "Save a copy first.|Take the second door.|Put it on the table.|Try the shorter cable.|Turn it down one notch.|Start with the easy part.|Read the last line again.|Leave a little space between them.|Keep the original file for now.|Move the chair before opening the cupboard.")
    lines("neutral", "reassurance", "There's a backup, so nothing is lost.|We have enough time to check it.|The change is reversible.|You can stop whenever you need to.|The first attempt doesn't have to be perfect.|There's another way around the room.|We'll take this one step at a time.|Nobody needs an answer this second.|We can use the spare for now.|The old settings are still saved.")
    lines("neutral", "aside", "For what it's worth, I prefer the simpler version.|Actually, I had the same question.|By the way, your cup is behind the keyboard.|I almost forgot the charger.|That reminds me, I owe you a message.|I'm not sure yet, but I have a guess.|To be fair, the instructions are tiny.|I tend to think out loud when I'm working.|That was the option I tried yesterday.|I might be overthinking the placement.|Somehow I always lose the small screwdriver.|I'd rather check than assume.|The first version was a little easier to read.|I meant the left side, not the right.|I was halfway through another thought.")
    lines("neutral", "exclamation", "Oh, there it is!|Found it!|That's the one!|There we go!|Right, that explains it!|Oh, I see it now!|One more to go!|Wait, the other door!|Here you are!|That's my cue!|Oh, the light is on!|There's the missing page!|And we're back!|That's the last box!|All set!")

    series("neutral", "statement", "It looks like {x}.", "the second door is unlocked|the ink is almost dry|we have enough food for tonight|the update has finished|the smaller box will fit|the fan needs cleaning|the room gets morning sunlight|the cable is caught under the desk|the green light is steady|the rain has stopped")
    series("neutral", "statement", "I've got {x}.", "a pencil right here|the notes in front of me|a spare cable in my bag|the first page open|a little time before lunch|the smaller screwdriver|the lid for that container|a copy on the other drive|your message from earlier|the receipt in my pocket")
    series("neutral", "statement", "The next step is to {x}.", "check the connection|save the new settings|measure the doorway|let the paint dry|clear a space on the desk|ask someone who was there|compare the two copies|write down what changed|open the second folder|put the tools away")
    series("neutral", "statement", "I was thinking about {x}.", "a different route home|moving the lamp closer|making soup for dinner|taking a walk after this|the book you mentioned|a smaller desk for this corner|trying that game over the weekend|how to organize these notes|which parts we actually need|a better place for the speakers")
    series("neutral", "statement", "We can {x}.", "keep the window open for a while|compare them side by side|use the older version today|start again from the saved copy|move the meeting to Friday|finish this after lunch|take the quiet route|split the work into two parts|leave the heavy box here|try a different angle")
    series("neutral", "statement", "This should {x}.", "make the text easier to read|leave enough room for the chair|keep the cable off the floor|give us a cleaner comparison|take a little pressure off the hinge|help the air move through the room|reduce the glare on the screen|hold until we find the proper clip|fit in the side pocket|give us somewhere to start")
    series("neutral", "statement", "There's {x}.", "a blue notebook by the door|another seat beside the window|a loose screw on the shelf|enough water for both of us|a narrow path behind the building|a spare blanket in the cupboard|some tape in the top drawer|a message waiting for you|a quieter room down the hall|a small gap at the edge")
    series("neutral", "statement", "I'll {x} while you finish that.", "tidy this end of the table|check the other room|make a fresh pot of coffee|write down the measurements|find the spare battery|look through yesterday's notes|put the empty boxes away|check whether the shop is open|sort the short cables|bring the chairs inside")
    series("neutral", "statement", "That part {x}.", "takes a little practice|can wait until tomorrow|is easier with two people|needs a gentler touch|looks different in daylight|comes apart without tools|is already in the notes|doesn't affect the rest|has a spare in the box|is a bit hard to see from here")
    series("neutral", "statement", "I usually {x}.", "keep the spare in the same drawer|check both ends of the cable|write a quick note before leaving|turn the screen down at night|start with the smallest change|leave myself a reminder|put the heavy bags on the floor|read the whole message first|take a break before dinner|measure twice when it matters")

    series("neutral", "yes_no_question", "Did you {x}?", "save the original|find the spare key|check the second page|move the box already|hear the last sentence|want the window closed|bring the shorter cable|get my message this morning")
    series("neutral", "yes_no_question", "Is {x}?", "the table level|the charger plugged in|the little light blinking|your coffee still warm|the path clear|the new version easier to read|that the correct address|the back door locked")
    series("neutral", "yes_no_question", "Would you like to {x}?", "compare the two versions|finish this tomorrow|start with a quick sketch|sit nearer the window|take the longer route|keep the old arrangement|look at the notes together|try the smaller one first")
    series("neutral", "yes_no_question", "Should we {x}?", "leave the lamp here|check the clock first|put the heavy bag down|wait for the rain to stop|keep a spare copy|ask before moving it|close the other window|measure the gap again")
    series("neutral", "yes_no_question", "Can you {x}?", "see the label from there|reach the top shelf|read the small print|hear that humming sound|hold this end for a moment|tell the two colors apart|open the lid without forcing it|find the page with the drawing")
    series("neutral", "wh_question", "Where did you {x}?", "put the spare cable|leave the notebook|find that little lamp|save the second copy|last use the key|hear about the new route|buy the storage box|see the missing chair")
    series("neutral", "wh_question", "How do you {x}?", "keep these notes organized|tell which cable is which|open this without bending it|choose between the two|remember all those names|keep the glare off the screen|get the lid to sit straight|make room for the extra chair")
    series("neutral", "wh_question", "What would happen if we {x}?", "moved the desk over a little|used the smaller box|left the window open|switched the two cables|saved it under another name|waited until the afternoon|took the path by the river|started with a rough sketch")
    series("neutral", "wh_question", "Which {x}?", "page has the measurements|door leads to the courtyard|cable goes to the speaker|copy did you change|drawer holds the scissors|route is usually quieter|chair would you rather use|part needs another look")
    series("neutral", "wh_question", "When did {x}?", "the light start flickering|the message arrive|you last charge it|the room get so warm|the second copy disappear|you notice the loose hinge|the shop change its hours|the rain turn to snow")
    series("neutral", "instruction", "Check {x} before you continue.", "the other end of the cable|the saved copy|the label on the box|the time on the clock|the space behind the chair|the last number in the address|the little switch at the back|the hinge near the floor|the second page of notes|the lock on the side door")
    series("neutral", "instruction", "Leave {x} for now.", "the original settings alone|the lid slightly open|a little room at the edge|the spare cable in the drawer|the heavy box on the floor|the older copy where it is|the empty chair by the window|the small screw on the tray|the message marked unread|the final decision until morning")
    series("neutral", "instruction", "Try {x} first.", "a shorter cable|the other socket|a slower turn|the copy from yesterday|a little less pressure|the side entrance|the smaller tool|a plain sheet of paper|the seat near the wall|the setting in the middle")
    series("neutral", "instruction", "Make sure {x}.", "the cable isn't pinched|the door can close|the two copies have different names|the lid is sitting straight|there's room to walk past|the text is large enough to read|the chair isn't blocking the drawer|the loose parts are in the tray|the switch is off before moving it|the notes are saved before you leave")
    series("neutral", "instruction", "Put {x}.", "the spare key back on the hook|the empty cup by the sink|the short cable in the small box|the notebook beside the keyboard|the heavier bag on the floor|the chairs along this wall|the loose screw in the tray|the lid next to the container|the finished copy in its own folder|the lamp a little farther from the screen")
    series("neutral", "reassurance", "We still have {x}.", "the original copy|enough time to compare them|a spare battery|another route home|the notes from yesterday|a place to stop and think|the receipt if it doesn't fit|a few other options")
    series("neutral", "reassurance", "You don't have to {x}.", "finish the whole page tonight|decide without seeing both|remember every detail|lift that box alone|answer while you're busy|get it right on the first try|keep using the awkward version|explain it all at once")
    series("neutral", "reassurance", "If {x}, we can adjust it.", "the chair is too close|the screen is too bright|the room gets cold|the new layout feels cramped|the text is too small|the schedule doesn't fit|the shelf is too high|the first plan takes too long")
    series("neutral", "aside", "I nearly {x}.", "left the key in the other jacket|put the wrong lid on it|forgot which copy was newer|walked past the side entrance|used the empty battery|sat down before moving the bag|wrote yesterday's date|left my notes on the kitchen table")
    series("neutral", "aside", "Honestly, I prefer {x}.", "the quieter room|the simpler drawing|a little more space on the desk|the chair with the lower back|the path with fewer stairs|plain labels I can read quickly|the old lamp in this corner|taking a minute to check")
    series("neutral", "aside", "Now that you mention it, {x}.", "I noticed the same loose hinge|the light did look a little dim|I haven't checked the back pocket|the shorter route might be easier|there was a spare in the cupboard|the room felt warmer yesterday|I did save a second copy|the smaller one would fit better")
    series("neutral", "aside", "I should probably {x}.", "label the two cables|bring a warmer jacket|put the spare key somewhere obvious|write that down before I forget|clear this corner of the desk|check the weather before leaving|find a better place for the lamp|stop balancing everything on one shelf")
    series("neutral", "exclamation", "Oh, {x}!", "that's the spare key|the second page was underneath|the little light came on|there's room after all|the missing cable was in my bag")
    series("neutral", "exclamation", "Right, {x}!", "the switch is at the back|we were using the older copy|the other door leads outside|the short cable is for the speaker|the drawer opens from this side")
    series("neutral", "exclamation", "There, {x}!", "the lid is straight now|the chair fits beside it|the text is readable|the cable is off the floor|the last box is packed")


def friendly():
    lines("warm", "statement", "Hey.|Welcome in.|Good to see you.|I'm glad you're here.|You can sit with me.|I kept a seat for you.|It's nice having company.|I'm in no rush.|I like hearing your ideas.|We make a pretty good team.")
    lines("warm", "yes_no_question", "Want some company?|You doing okay?|Can I help with that?|Would a quick break help?|Want to talk it through?|Is this a good time?|Do you want the comfy chair?|Can I make you some tea?|Would you like me to stay a minute?|Want to show me what you're making?")
    lines("warm", "wh_question", "How's your day been?|What have you been playing lately?|What did you think of it?|How are you settling in?|What's been keeping you busy?|What would make this easier for you?|Which part are you proudest of?|Where would you like to start?|What kind of music helps you focus?|How can I take a little work off your hands?")
    lines("warm", "instruction", "Take your time.|Come sit for a minute.|Make yourself comfortable.|Tell me the part you're stuck on.|Keep the bit that you like.|Show me when you're ready.|Give yourself a little room to think.|Grab a drink before we start.|Leave the heavy lifting to both of us.|Start wherever feels easiest.")
    lines("warm", "reassurance", "You're doing fine.|I've got your back.|You don't have to handle it alone.|We can work it out together.|It's okay to need a minute.|You haven't let me down.|There's room to change your mind.|I'm happy to listen.|You can ask me again.|You deserve a proper break.")
    lines("warm", "aside", "I like this little corner, honestly.|I'm usually better at this after tea.|That was a thoughtful way to put it.|I was hoping you'd drop by.|I had a feeling you'd enjoy this.|A quiet afternoon sounds good to me.|I like how carefully you noticed that.|For the record, I'm on your side.|It's nice when we can just talk.|I don't mind a little comfortable silence.")
    lines("warm", "exclamation", "Hey, there you are!|You made it!|That looks lovely!|Nice work on that!|Oh, that's thoughtful!|Look at you go!|There's my favorite little detail!|That's a good idea!|What a nice surprise!|Welcome back!")
    series("warm", "statement", "I'm happy to {x}.", "keep you company for a bit|listen while you work it out|help you carry the boxes|look at the drawing with you|make another cup of tea|wait until you're ready|show you where I started|give it another try together")
    series("warm", "statement", "I appreciate {x}.", "you taking the time to explain|the way you checked on everyone|your patience with this part|that you remembered the small details|how honest you were about it|you giving the new person a hand|the care you put into this|you making room for another idea")
    series("warm", "statement", "We could {x}, if that sounds good.", "take a short walk|look through your sketchbook|make dinner together|try the quieter room|play something relaxed tonight|put on a little background music|sit outside for a while|finish the tricky part tomorrow")
    series("warm", "statement", "I like {x}.", "the way you've arranged this corner|how the light falls on the table|having a friend to think out loud with|that you kept your original idea|the little changes you made|how welcoming this room feels|the care behind that choice|seeing you enjoy what you're making")
    series("warm", "statement", "You made {x}.", "the new person feel welcome|this room a lot more comfortable|a complicated idea easy to follow|some real progress today|a thoughtful choice there|the quiet moment feel less awkward|space for everyone to contribute|a good point I hadn't considered")
    series("warm", "statement", "I'll {x} with you.", "look at the options|take the short way home|sit through the loading screen|check the last few details|carry the awkward end|go over the notes|try the first round|wait for the rain to pass")
    series("warm", "yes_no_question", "Would you like {x}?", "a quieter place to sit|a little help getting started|some company on the walk|a fresh cup of tea|another pair of eyes on this|a minute before we continue|the seat beside the window|a simpler explanation")
    series("warm", "yes_no_question", "Do you want me to {x}?", "look at it with you|hold this end steady|show you the shortcut|stay while you finish|save you the comfy chair|bring the notes over|read the message aloud|help you make a little space")
    series("warm", "yes_no_question", "Have you had a chance to {x}?", "get something to eat|get a little fresh air|rest your eyes|try the new game|see how your friend is doing|listen to that song|make yourself comfortable|enjoy the part you finished")
    series("warm", "yes_no_question", "Would it help if we {x}?", "slowed down a little|started with one small piece|looked at a rough example|moved somewhere quieter|wrote the options down|took a proper lunch break|left the hard part until morning|asked someone you trust")
    series("warm", "wh_question", "What do you like most about {x}?", "the room you've made|the game you started|the drawing on your desk|working with this group|the little shop near you|that part of the story|the way your project is going|the place you grew up")
    series("warm", "wh_question", "How did you get interested in {x}?", "making little games|drawing characters|building computers|playing guitar|taking photographs|growing your own food|writing stories|learning to cook")
    series("warm", "wh_question", "What would make {x} a little nicer?", "your evening|this corner of the room|the walk home|our next game night|the work on your desk|the way we divide this task|your morning routine|the place where you take breaks")
    series("warm", "wh_question", "Where would you like to {x}?", "sit while we talk|keep the things you're proud of|take a little walk|put your favorite drawing|start our next project|go when you need some quiet|set up your reading chair|spend a relaxed afternoon")
    series("warm", "instruction", "Take a moment to {x}.", "settle into the chair|look at what you've finished|give your hands a rest|enjoy your cup of tea|think about what you want|let your friend finish their thought|check how you're feeling|appreciate the small improvement")
    series("warm", "instruction", "Tell me about {x}.", "the idea you keep coming back to|the game you're enjoying|the bit that finally clicked|your favorite part of the day|the project on your desk|the place you'd like to visit|the detail you're most excited about|the song you can't stop humming")
    series("warm", "instruction", "Let's {x}, at your pace.", "read through the notes|sort the parts into little piles|look at the two choices|try one room at a time|work through the example|take a stroll around the block|find a comfortable starting point|put together a rough plan")
    series("warm", "instruction", "Keep {x}.", "the part that feels like you|a little time for yourself|your favorite detail in the drawing|a comfortable seat nearby|the version you're proud of|someone you trust in the loop|room for a different idea|the small wins in mind")
    series("warm", "reassurance", "It's okay if {x}.", "you need another explanation|today wasn't very productive|the first sketch is messy|you change your mind later|you're not ready to talk|you only finish a small part|you don't know the answer yet|you want a little quiet")
    series("warm", "reassurance", "We can {x} together.", "find a clearer starting point|pick up where you left off|look for the missing piece|get through the awkward part|sort out the confusing notes|make the room feel more comfortable|try a gentler approach|take it one small step at a time")
    series("warm", "reassurance", "You don't need to {x} for me.", "have everything figured out|pretend you're having a good day|rush through your explanation|make the room spotless|find the perfect words|finish before you're tired|agree with every suggestion|hide that you're unsure")
    series("warm", "reassurance", "There's no hurry to {x}.", "choose a final version|answer every question|finish the whole drawing|tell the whole story|start the next round|make a big decision|find the right explanation|be cheerful on demand")
    series("warm", "reassurance", "I'll be here while you {x}.", "catch your breath|look through the options|finish the little task|decide what you need|read the message|get your thoughts in order|try the first step|wait for your friend")
    series("warm", "reassurance", "A little {x} doesn't undo your progress.", "uncertainty|rest|hesitation|confusion|change of direction|extra practice|time away|mess on the desk")
    series("warm", "reassurance", "You can {x} without apologizing.", "ask for a clearer explanation|take a break|say you don't understand|change your mind|need a little help|be quiet for a while|start again|tell me what works for you")
    series("warm", "reassurance", "Even if {x}, we have a way forward.", "the first plan doesn't fit|you can't finish tonight|the room still feels awkward|the message takes a while to arrive|the result is a little different|you forget one of the steps|the answer isn't obvious|the project needs more time")
    series("warm", "aside", "I've always had a soft spot for {x}.", "quiet little bookshops|rainy afternoon game sessions|warm light in a small room|handwritten notes|a well-used sketchbook|someone's very specific favorite song|simple meals shared with friends|little projects made with care")
    series("warm", "aside", "I think {x} is worth keeping.", "your original sketch|the little joke in the title|that comfortable corner|the detail you added by hand|the idea that made you smile|the gentler version of that line|the time we set aside to talk|the part that feels personal")
    series("warm", "aside", "If you ask me, {x}.", "we've earned a tea break|that was a really considerate choice|this is nicer with company|your rough sketch has a lot of charm|a little patience goes a long way|the small details make it feel welcoming|you explained that pretty clearly|we're allowed to enjoy the process")
    series("warm", "exclamation", "Oh, {x}!", "you remembered my favorite tea|that little shelf looks great|you saved a seat for me|that's such a nice detail|you made room for the new person")
    series("warm", "exclamation", "Hey, {x}!", "that's a lovely idea|you found your rhythm|the room feels welcoming|you should keep that sketch|you did something kind today")


def emotional_conversation():
    banks = {
        "happy": {
            "statement": "That made my day.|I'm in a good mood now.|I'm glad we gave it a try.",
            "yes_no_question": "Did you see the good news?|Want to celebrate with a game?|Doesn't the room feel better now?",
            "wh_question": "What was your favorite part?|How should we celebrate?|Which good thing happened first?",
            "exclamation": "Oh, that's lovely!|We did it!|That turned out so well!",
            "instruction": "Enjoy the moment.|Keep the picture you like.|Tell your friend the good news.",
            "reassurance": "You earned this little win.|It's okay to feel proud of it.|We get to enjoy what worked.",
            "aside": "I can't stop smiling at that.|This is a nice change of pace.|That little detail makes me happy.",
        },
        "amused": {
            "statement": "That was unintentionally perfect.|I walked straight past the answer.|The chair is winning this argument.",
            "yes_no_question": "Did we both miss the giant arrow?|Was that your dramatic entrance?|Do we count that as a strategy?",
            "wh_question": "How did the cable get that tangled?|Who taught the cat to supervise?|What is the chair trying to prove?",
            "exclamation": "Of course it was in my pocket!|Well, that was graceful!|That's one way to do it!",
            "instruction": "Give the chair its trophy.|Let me pretend that was deliberate.|Keep that wonderfully awkward screenshot.",
            "reassurance": "At least we can laugh about it.|Your secret is safe with the loading screen.|I've made that exact silly mistake.",
            "aside": "Very professional of me, obviously.|My timing remains impressively terrible.|The plan briefly became interpretive dance.",
        },
        "excited": {
            "statement": "I really want to try this now.|This could be a fun little project.|I'm looking forward to the next part.",
            "yes_no_question": "Are you ready to give it a go?|Can we try the new room next?|Did you see what we unlocked?",
            "wh_question": "What should we build first?|Which route do you want to explore?|How soon can we try that idea?",
            "exclamation": "Wait, it worked!|That's exactly what we needed!|Look at that little animation!",
            "instruction": "Show me the next part.|Open the new route when you're ready.|Keep going; I want to see how it ends.",
            "reassurance": "You can be proud of that breakthrough.|We've got a good starting point now.|You don't have to make it perfect to enjoy it.",
            "aside": "I may already have three ideas.|This is the part I was waiting for.|I'm trying not to get ahead of myself.",
        },
        "sad": {
            "statement": "I was hoping for a different ending.|I'm going to miss that little place.|That one stayed with me.",
            "yes_no_question": "Could we sit quietly for a minute?|Do you want some company tonight?|Was that really our last visit?",
            "wh_question": "What do you miss most about it?|Where should we put the old picture?|How are you holding up after that?",
            "exclamation": "Oh, that's such a shame!|I really hoped they would make it!|That was their favorite little room!",
            "instruction": "Leave the picture there for now.|Give me a little time to think.|Keep something that reminds you of them.",
            "reassurance": "You don't have to find a bright side today.|I'm here even when there's nothing to say.|It mattered, and it's okay to miss it.",
            "aside": "The empty chair feels a little different now.|I wasn't ready for the goodbye.|Some days are just quieter than others.",
        },
        "concerned": {
            "statement": "That noise doesn't seem right.|I want to check before we keep going.|You seem a little worn out.",
            "yes_no_question": "Are you feeling all right?|Is the walkway clear enough?|Did anyone check the other room?",
            "wh_question": "What happened just before it stopped?|Where is the nearest clear exit?|How long has the light been flickering?",
            "exclamation": "Wait, the cable is caught!|Careful, that shelf is loose!|Oh, the door isn't closing!",
            "instruction": "Set it down before it slips.|Check that everyone is accounted for.|Stop for a moment and look at the hinge.",
            "reassurance": "We can slow down and check safely.|You can tell me if something feels wrong.|We don't need to rush into the next step.",
            "aside": "I'd rather be a little cautious here.|Something about that timing bothers me.|I might be wrong, but I'd like another look.",
        },
        "frustrated": {
            "statement": "I thought we'd already fixed this.|That menu is making a simple job awkward.|I need a fresh look at the problem.",
            "yes_no_question": "Did it reset the setting again?|Can we stop repeating the same step?|Is there a simpler way through this?",
            "wh_question": "Why does that button keep moving?|What did it change this time?|Which part is still blocking us?",
            "exclamation": "Oh, not the same error again!|It was working a minute ago!|That's the wrong drawer again!",
            "instruction": "Leave it alone for a minute.|Show me the exact step that failed.|Save what works before changing anything else.",
            "reassurance": "I'm annoyed with the problem, not with you.|We can take a break and come back.|One stubborn step doesn't erase the work.",
            "aside": "My patience is taking a short walk.|I liked that button better when it did something.|This is getting more complicated than it needs to be.",
        },
        "surprised": {
            "statement": "I didn't expect that to work.|The little drawer was there all along.|That's a lot different from yesterday.",
            "yes_no_question": "Did that just open by itself?|Was the spare here the whole time?|Have we already finished the last part?",
            "wh_question": "Where did that extra chair come from?|How did you find it so quickly?|What changed while I was away?",
            "exclamation": "Wait, there's another room!|Oh, it actually fits!|That's the missing piece!",
            "instruction": "Hold on; show me that again.|Look at the little detail on the side.|Give me a second to take that in.",
            "reassurance": "A different result isn't automatically a bad one.|We can take a moment to understand it.|You don't need an answer just because I was surprised.",
            "aside": "Well, that wasn't on my list.|I had the wrong idea entirely.|Apparently the box had one more surprise for us.",
        },
    }
    for emotion, acts in banks.items():
        for act, text in acts.items():
            lines(emotion, act, text)

    for act, pattern, values in [
        ("statement", "I'm glad {x}.", "we found a comfortable spot|you liked the finished version|the garden is doing well|the new person felt welcome|we saved the little drawing|you got some time to relax"),
        ("yes_no_question", "Did you enjoy {x}?", "the game last night|our little walk|the meal we made|the silly part of the story|the new room|seeing the finished picture"),
        ("wh_question", "What made {x} so nice?", "the afternoon|that little conversation|the last round|the walk by the river|the quiet room|our little project"),
        ("exclamation", "Oh, {x}!", "the flowers finally opened|they kept our favorite table|you found the good ending|the little garden has grown|the colors work together|that's a lovely note"),
        ("instruction", "Take a little time to enjoy {x}.", "the room you've finished|your favorite song|the sunny corner|the game you waited for|the picture you made|the good news"),
        ("reassurance", "You can feel good about {x}.", "the care you put into it|the little change you made|showing up for your friend|finishing that difficult part|trying a new idea|asking for what you needed"),
        ("aside", "I keep smiling about {x}.", "that little surprise|the way the room turned out|your friend's reaction|the tiny garden on the windowsill|the good news this morning|the silly photo we took"),
    ]:
        series("happy", act, pattern, values)
    for act, pattern, values in [
        ("statement", "Apparently {x}.", "the cat is in charge of the schedule|the missing key wanted a pocket vacation|the chair has strong opinions|my tidy pile was mostly cables|the loading screen needed a tea break|the cupboard was hiding a bonus mug"),
        ("yes_no_question", "Does {x}?", "the chair get a vote now|the cat approve of this layout|the loading screen charge rent|that count as a creative solution|my backwards notebook pass inspection|the cable knot have a name"),
        ("wh_question", "How did {x}?", "the spoon end up with the pens|we both sit on the creaky chairs|the cat choose the only keyboard|the smallest box become the fullest|the cable tie become another knot|I miss the bright yellow sign"),
        ("exclamation", "Well, {x}!", "the chair has spoken|that's a very ambitious sandwich|the cable won that round|my pocket solved the mystery|the cat found the warm spot|that was a beautifully awkward entrance"),
        ("instruction", "Let me {x}.", "blame the chair for one second|give this knot a formal introduction|pretend I meant to do that|find my extremely professional sticky note|negotiate with the cupboard|remove the cat from middle management"),
        ("reassurance", "At least {x}.", "the cat enjoyed the demonstration|we found a new use for the box|the mistake was easy to spot|the chair kept us entertained|we have a very memorable picture|the cable didn't tie us together"),
        ("aside", "For the record, {x}.", "the cat has not earned a promotion|I meant to read the notebook upside down|the knot was not part of the design|my bag contains a small stationery department|the chair started it|the sandwich was taller in my head"),
    ]:
        series("amused", act, pattern, values)
    for act, pattern, values in [
        ("statement", "I can't wait to try {x}.", "the new route|that little puzzle|the room we designed|your clever shortcut|the next part of the story|the game we picked"),
        ("yes_no_question", "Can we {x} next?", "see the room beyond the stairs|try the little puzzle|build the cozy corner|check out the new route|open the last box|look at your finished animation"),
        ("wh_question", "What should we {x} first?", "build in the new room|try with the spare parts|explore beyond the gate|add to the little game|look for on the new map|show our friends"),
        ("exclamation", "Look, {x}!", "the new path is open|the little animation is moving|the colors line up perfectly|we reached the next room|your idea actually works|the last piece fits"),
        ("instruction", "Show me {x} when it's ready.", "the new route|the little character animation|the room you've been designing|the shortcut you found|the next puzzle|the finished scene"),
        ("reassurance", "We've already got {x} to build on.", "a promising first version|the hardest part working|a really clear idea|a room full of possibilities|some useful practice|a little breakthrough"),
        ("aside", "I'm already thinking about {x}.", "a cozy corner for the new room|the next bit of the story|a fun little challenge|how to show this to our friends|another use for that shortcut|what we might find beyond the stairs"),
    ]:
        series("excited", act, pattern, values)
    for act, pattern, values in [
        ("statement", "I'm going to miss {x}.", "our quiet game nights|the little shop on the corner|having that friend nearby|the garden outside the window|the room where we used to talk|the familiar walk home"),
        ("yes_no_question", "Can we keep {x}?", "the old photograph|the little note on the shelf|one of the drawings|the chair by the window|the card they sent|a little time to remember"),
        ("wh_question", "What reminds you most of {x}?", "the old place|those game nights|your time there|the garden in spring|the little shop|that last afternoon together"),
        ("exclamation", "Oh, {x}!", "that was our favorite corner|I hoped the ending would be kinder|they loved that little garden|we only just finished that room|I wasn't ready for that goodbye|that's the last picture we took"),
        ("instruction", "Keep {x} somewhere safe.", "the photograph from that afternoon|the little note they wrote|the drawing from the old room|the card from your friend|the story you want to remember|the small gift from that place"),
        ("reassurance", "It's okay to miss {x}.", "the way things used to feel|your old routine|the little place you liked|a friend who moved away|the room you spent time in|the ending you hoped for"),
        ("aside", "I still think about {x} sometimes.", "that last game night|the quiet corner of the old room|the note they left|the garden before winter|the little walk we used to take|how different the place feels now"),
    ]:
        series("sad", act, pattern, values)
    for act, pattern, values in [
        ("statement", "I'd like to check {x} before we continue.", "the loose hinge|that unfamiliar sound|the cable under the chair|whether everyone is back|the doorway at the far end|the flickering light"),
        ("yes_no_question", "Have we checked {x}?", "the walkway behind the desk|the loose shelf|the second room|whether the cable is warm|the latch on the side door|that everyone has a way back"),
        ("wh_question", "What caused {x}?", "the sudden noise|the light to go out|the door to stick|the shelf to tilt|the connection to drop|the cable to feel warm"),
        ("exclamation", "Careful, {x}!", "the lid is slipping|the step is wet|the chair is catching the cable|the box is coming apart|the shelf isn't steady|the walkway is getting blocked"),
        ("instruction", "Check {x} before touching it.", "whether the power is off|the support underneath|the loose edge|the little warning light|where the cable runs|how the lid is held"),
        ("reassurance", "We can check {x} without rushing.", "the unfamiliar sound|the loose hinge|the route back|the flickering light|the last message|the room beyond the door"),
        ("aside", "I'm a little worried about {x}.", "the loose shelf|the way that cable is bent|how tired everyone looks|the blocked doorway|the timing of that noise|the latch that won't stay shut"),
    ]:
        series("concerned", act, pattern, values)
    for act, pattern, values in [
        ("statement", "I'm getting tired of {x}.", "the setting resetting itself|looking for the same missing cable|that menu covering the label|the hinge sticking halfway|the connection dropping mid-sentence|having to redo the same step"),
        ("yes_no_question", "Did {x} again?", "the setting reset|the lid slip out of place|the connection drop|the button move|the menu cover the text|the door catch on the rug"),
        ("wh_question", "Why is {x}?", "the same setting changing itself|the drawer still catching|the connection dropping every few minutes|the label hidden behind that menu|the little screw so hard to reach|the simple step taking so long"),
        ("exclamation", "Oh, {x} again!", "the same setting reset|the door caught on the rug|the cable slipped out|the label disappeared|the drawer jammed|the connection dropped"),
        ("instruction", "Let's stop {x} for a minute.", "changing the setting back and forth|forcing the lid into place|opening the same broken menu|moving the cable around|repeating the step that failed|trying to balance the loose shelf"),
        ("reassurance", "We don't have to {x} forever.", "keep retrying the same broken step|work around that awkward menu|use the drawer that keeps sticking|put up with this bad connection|guess what the hidden label says|finish the whole task tonight"),
        ("aside", "I could do without {x} today.", "another disappearing setting|the drawer picking a fight|a cable that won't stay put|the menu hiding the one useful button|the same error coming back|a lid with its own agenda"),
    ]:
        series("frustrated", act, pattern, values)
    for act, pattern, values in [
        ("statement", "I didn't realize {x}.", "there was another drawer|the short route was open|we already had a spare|the whole shelf could fold down|the last part was finished|you'd kept the original drawing"),
        ("yes_no_question", "Was {x} here the whole time?", "the spare key|the little adapter|the missing notebook|the second drawing|the extra chair|the short cable"),
        ("wh_question", "How did you {x} so quickly?", "find the missing page|solve the little puzzle|move all those chairs|finish the drawing|notice the tiny switch|get the connection working"),
        ("exclamation", "Wait, {x}!", "there's a second latch|the whole shelf folds away|we already had the right cable|that's the original sketch|the missing key is on the hook|the short route is open"),
        ("instruction", "Show me {x} again.", "the little hidden drawer|how the shelf folds down|where you found the spare|the shortcut through that room|the detail you just changed|how the two pieces fit"),
        ("reassurance", "We can take a moment to understand {x}.", "the unexpected result|the extra room|the new route|the change in the drawing|the sudden improvement|the way that shelf moves"),
        ("aside", "I honestly expected {x}.", "the larger box to be heavier|the latch to be on the other side|the puzzle to take longer|the shelf to stay in one piece|the door to lead outside|the room to be empty"),
    ]:
        series("surprised", act, pattern, values)


def coder_and_gamer():
    # Everyday peer conversation, not documentation or unverified stream facts.
    series("neutral", "statement", "I found {x} in the code.", "a name that changed halfway through|a check that's happening twice|a value that never gets reset|a branch we can simplify|the place where the list is sorted|an empty result we didn't handle|the line that opens the file|a helper we can use again|a comment that needs clearer wording|the reason the button stays disabled")
    series("neutral", "yes_no_question", "Did the game {x}?", "save before that happened|pause when the message appeared|keep your old settings|show the route back|finish loading the map|remember the name you entered|put the item in storage|show which pawn was selected|keep the old room open|let you cancel the order")
    series("neutral", "wh_question", "What does {x} do?", "the little button beside the map|the second option in that menu|the marker by the door|the setting we changed yesterday|the helper at the bottom|the spare battery on the shelf|the filter above the list|the icon beside the pawn's name|the warning next to the order|the shortcut you just used")
    series("neutral", "instruction", "Before we change it, {x}.", "save the working version|write down what the button does|check which pawn has the job|compare the two files|look at the message in the log|keep a copy of the map|see whether the item is reserved|read the whole condition|find the caller that uses it|confirm the old setting is still available")
    series("warm", "reassurance", "You don't need to {x} all at once.", "learn every shortcut|build the whole base|understand the whole codebase|fix every warning|remember every work priority|plan every room|solve every little puzzle|finish the whole feature|explain the whole bug|choose all the starting gear")
    series("warm", "yes_no_question", "Want to {x} with me?", "try a relaxed game|sketch out the base|walk through the function|check the new room|pick a starting map|look at the route back|sort the work priorities|name the little outpost|plan a cozy break room|see how the first version feels")
    series("neutral", "aside", "I tend to {x} when I'm coding.", "write the smallest useful version first|keep the working copy nearby|read the caller before changing a helper|take notes when the behavior surprises me|choose names I can understand tomorrow|leave the clever trick until it's needed|check the empty case early|step away when I start guessing|say the condition out loud|keep unrelated changes separate")
    lines("happy", "statement", "The little colony is starting to feel like a home.|That was a clean little fix.|I like how readable this version is.|Our game night turned out nicely.")
    lines("amused", "aside", "The pawn has discovered advanced standing still.|That was less a shortcut and more a scenic route.|My beautifully named variable is called temporary two.|The loading screen has excellent suspense.")
    lines("excited", "exclamation", "The gate finally opened!|The map remembered our room!|That animation has so much character!|We found a route all the way back!")
    lines("sad", "statement", "I got attached to that little colony.|That empty bunk hits a little harder than I expected.|I wanted the crew to make it home.|We spent a lot of time on that room.")
    lines("concerned", "instruction", "Pause before sending the crew through.|Check the return route before exploring farther.|Make sure the supplies are actually reachable.|Let the tired pawns get some rest.")
    lines("frustrated", "statement", "The pawn can reach the door but not the shelf.|The button says one thing and does another.|We fixed the symptom, but the cause is still there.|The same order is getting queued twice.")
    lines("surprised", "yes_no_question", "Did the room change while we were away?|Was that item in the other storage zone?|Did the pawn find a shorter path?|Is that the same coordinate we saved?")


def pronunciation_and_correction():
    # Names and quantities occur in normal turns, not encyclopedic lists.
    for name in ("Mira", "Kade", "Tobin", "Jess", "Rook", "Nora", "Theo", "Ada", "Sam", "Alex", "Robin", "Casey"):
        add("neutral", "statement", name + " left a note beside the door.")
        add("warm", "yes_no_question", "Did " + name + " get a chance to take a break?")
    lines("neutral", "statement", "The timer says twenty minutes.|We have forty meals in storage.|The battery is at seventy percent.|That box weighs about three kilograms.|The walk takes a quarter of an hour.|It starts at half past eight.|There are twelve chairs and one spare.|The new room is nine tiles wide.|I saved the file on October eleventh.|The first attempt took two and a half minutes.|We need another six planks.|The temperature is eighteen degrees.|The next page is number twenty-four.|The longer cable is one point five meters.|The meeting moved from Thursday to Friday.|I put the Python file in its own folder.|This part is written in C sharp.|RimWorld is paused while we check the map.|The Rimrooms gate is linked to the same room.|Unity is the name on the project folder.")
    lines("neutral", "statement", "I meant the second door, not the first.|Sorry, that was fifteen, not fifty.|The key is on the hook, not in the drawer.|I said north; I was thinking of the other map.|The blue cable goes to the speaker.|Actually, that's yesterday's copy.|Let me say that more clearly.|I mixed up the two names.|The number ends in four, not five.|I was asking about the smaller room.|I meant next Friday, a week from now.|That was a suggestion, not a final decision.")
    lines("warm", "reassurance", "You heard me correctly; I said it awkwardly.|That's a fair question, and I can explain it better.|No worries; the two names are easy to mix up.|You can stop me if I skip a step.|It's fine to check which number I meant.|I'm glad you asked instead of guessing.")
    lines("neutral", "yes_no_question", "Did you say thirteen or thirty?|Do you mean this Friday or next Friday?|Was that north of the gate?|Should the number end in four?|Are you asking about the code or the layout?|Did you mean the person or the project name?")
    lines("neutral", "wh_question", "Which Friday did you mean?|How do you pronounce that name?|What was the last number again?|Where should the decimal point go?|Which of the two rooms are we talking about?|What should I call this part?")


def write_outputs():
    everyday()
    friendly()
    emotional_conversation()
    coder_and_gamer()
    pronunciation_and_correction()
    ids = [row["id"] for row in ROWS]
    if not 1000 <= len(ROWS) <= 1600 or len(ids) != len(set(ids)):
        raise ValueError("Corpus size or identity collision requires author review: " + str(len(ROWS)))
    if {r["emotion"] for r in ROWS} != set(EMOTIONS) or {r["speech_act"] for r in ROWS} != set(SPEECH_ACTS):
        raise ValueError("Declared delivery vocabulary is not covered")
    partitions = collections.Counter(split_for(r["text"]) for r in ROWS)
    if set(partitions) != {"train", "heldout"}:
        raise ValueError("Both grouped partitions must have planned transcripts")
    emotions = collections.Counter(row["emotion"] for row in ROWS)
    acts = collections.Counter(row["speech_act"] for row in ROWS)
    pairs = collections.Counter((r["emotion"], r["speech_act"]) for r in ROWS)
    corpus = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in ROWS)
    digest = hashlib.sha256(corpus.encode()).hexdigest()
    (HERE / "SPEECH_CORPUS.jsonl").write_text(corpus, encoding="utf-8", newline="\n")
    ordinary = emotions["neutral"] + emotions["warm"]
    short = sum(len(r["text"].split()) <= 3 for r in ROWS)
    question = acts["yes_no_question"] + acts["wh_question"]
    report = [
        "# Planned speech corpus for the accepted A2 voice", "",
        "Prepared 2026-10-11. This is authored text preparation, not a rendered or accepted audio dataset.", "",
        "## Purpose and status", "",
        "The owner accepted the A2 source identity and its four reference-anchored delivery auditions. These planned utterances give that identity ordinary, friendly English conversation, coder and gamer turns, questions, brief reactions and modest emotional variety. No celebrity imitation, register boilerplate or copied dialogue is used.", "",
        "**Audio acceptance remains pending for every corpus row.** Emotion and speech-act labels express the intended performance. They are not claims about unheard recordings. No audio is generated by the corpus builder, and this corpus does not authorize training, deployment or paid compute.", "",
        "## Files and reproducibility", "",
        "- `build_corpus.py`: standard-library authoring templates plus the local `dataset_contract.py` vocabulary/split helpers. Re-running writes only this plan and `SPEECH_CORPUS.jsonl`.",
        "- `SPEECH_CORPUS.jsonl`: one planned utterance per line with exactly `id`, `text`, `emotion`, `intensity`, `pace` and `speech_act`.",
        "- `dataset_contract.py`: owns the delivery vocabulary, normalized transcript grouping and later audio/feature/checkpoint contracts.", "",
        "Run `python training/voice/build_corpus.py` to reproduce this text artifact. Do not confuse it with an audio-rendering or training command.", "",
        "Stable IDs hash normalized lexical text plus emotion and speech act. A changed authored line receives a different ID; exact normalized lexical duplicates are omitted globally. Explicitly contrastive future recordings of one transcript must share its normalized split group even when their labels differ.", "",
        "Corpus SHA256: `" + digest + "`.", "",
        "## Saved preparation statistics", "",
        f"- {len(ROWS):,} rows and {len(SEEN):,} unique normalized transcripts; no duplicated IDs.",
        f"- Neutral/warm: {ordinary:,} rows ({ordinary / len(ROWS):.1%}). Other states are intended as occasional context-appropriate delivery, not constant acting.",
        f"- Brief reactions/turns of three words or fewer: {short}.",
        f"- Genuine question speech acts: {question} ({question / len(ROWS):.1%}); these include yes/no, wh-, clarification and choice questions.",
        f"- Contract split: {partitions['train']} planned train and {partitions['heldout']} planned heldout transcript groups.",
        "- Neutral intensity is 0.0. Every other planned emotion has modest intensity 0.35. All planned pace multipliers are 1.0; neither unperformed pace variation nor unsupported intensity extremes are claimed.",
        "- No duration/hour estimate is claimed until audio is rendered and measured.", "",
        "| Intended emotion | Rows |", "| --- | ---: |",
    ]
    report.extend(f"| {emotion} | {emotions[emotion]} |" for emotion in EMOTIONS)
    report.extend(["", "| Intended speech act | Rows |", "| --- | ---: |"])
    report.extend(f"| {act} | {acts[act]} |" for act in SPEECH_ACTS)
    report.extend(["", "| Intended emotion | statement | yes/no | wh | exclamation | instruction | reassurance | aside |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"])
    report.extend("| " + emotion + " | " + " | ".join(str(pairs[(emotion, act)]) for act in SPEECH_ACTS) + " |" for emotion in EMOTIONS)
    report.extend([
        "", "## Authoring choices", "",
        "Short acknowledgments and pauses in normal language are retained instead of the old four-word minimum. Questions are actual questions, not statement rows with arbitrary rising-pitch instructions. Reassurance includes practical support and quiet company. Clean dry humor is occasional and gentle; no insulting, sexual, drug or profanity content is included.", "",
        "Original bounded templates use varied complete clauses and practical objects. Individual substitutions are limited to small authored lists, rather than an unbounded Cartesian product. Coding/game terms occur in normal peer conversation. Names, quantities, dates and corrections are embedded in usable utterances, not encyclopedic readings. The text is fictional audition material, not evidence that any described action occurred on stream.", "",
        "The pronunciation bank includes short names, C sharp, Python, RimWorld, Rimrooms, dates, percentages, time expressions and easily confused numbers. Any mispronunciation must be corrected in source text/frontend and re-rendered; a matching transcript label cannot repair wrong speech.", "",
        "## Preparation limits and next decisions", "",
        "1. Keep the accepted A2 identity fixed in the source generator. Inspect representative warm, neutral, happy, amused, excited, sad, concerned, frustrated and surprised performances before scaling up.",
        "2. Inspect timing, lexical stress, genuine questions, emotional transitions, natural pauses and speaker consistency. Measured pitch is descriptive; it is not a substitute for listening or perceived maturity.",
        "3. Convert successful source performances into the exact audio schema in `dataset_contract.py`, with immutable source/voice identities, WAV hashes and actual performed labels. An intended label must never be used to certify flat or mismatched audio.",
        "4. Preserve rejected renders separately. Validate intelligibility, transcript fidelity, pronunciation, boundary silence, clipping and signal quality. Do not label failed source audio as accepted merely because synthesis finished.",
        "5. Use `split_for(text)` consistently for every lexical variant; keep normalization statistics training-only. The normalized exact-transcript split prevents the old speed-variant leakage, but close paraphrases/templates may still share wording across partitions. Add a separately authored unseen audition set before claiming broad naturalness.",
        "6. Text coverage does not establish audio coverage. Runtime delivery support must come from accepted rendered train rows, including the emotion/act combinations actually present after QA. This corpus does not prove all 63 combinations were learned.",
        "7. Fixed pace and one modest intensity are intentional boundaries. Wider controls, actual laughter, sobbing, whispering and non-speech effects remain unsupported until suitable source examples, conditioning and acceptance exist.",
        "8. The corpus contains no audio. Model quality, actual hours, runtime memory/latency, coexistence with the game/OBS/brain and paid-training cost remain separate evidence requirements. No automatic launch or deployment is authorized here.", "",
        "## Checks performed by this authoring run", "",
        "The builder verified planned vocabulary membership, finite delivery values, stable unique IDs, unique normalized transcripts, the requested corpus-size range and presence of both contract split groups. It then wrote this plan and the JSONL text artifact. These are preparation consistency checks, not acoustic, model, gameplay or runtime tests.", "",
    ])
    (HERE / "CORPUS_PLAN.md").write_text("\n".join(report), encoding="utf-8", newline="\n")
    print(json.dumps({"rows": len(ROWS), "unique_normalized_transcripts": len(SEEN), "sha256": digest,
                      "emotions": dict(emotions), "speech_acts": dict(acts), "splits": dict(partitions),
                      "short_turns": short, "neutral_warm_fraction": ordinary / len(ROWS)}, indent=2))


if __name__ == "__main__":
    write_outputs()
