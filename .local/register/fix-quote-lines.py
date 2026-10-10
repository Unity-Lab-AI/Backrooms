import io

p = 'docs/FINALIZED.md'
s = io.open(p, encoding='utf-8').read()

# Four directions had been put on one blockquote line, so they extracted as a single blob and
# one of them had been shortened. One quote per line is the convention everywhere else, and
# it is what lets each be matched against the queue individually.
start = s.index('> *"real quick make this html open able')
end = s.index('\n', s.index('now the about.xml show a blank screen', start))
old = s[start:end]

new = (
'> *"real quick make this html open able : \\" '
'file:///C:/Users/gfour/Desktop/Backrooms/Mod/Rimrooms%20-%20Async%20Industries/About/About.xml\\" '
'as if i open this with edge to read it its all fucked up"*\n'
'\n'
'> *"and its a massive text wall needs style formating and beautiful layout"*\n'
'\n'
'> *"check for other shit text walls youve made too after you fix this one"*\n'
'\n'
'> *"now the about.xml show a blank screen when i open it with edge and i still dont see the html versions"*'
)

s = s[:start] + new + s[end:]
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('archive quotes split, one per line')
