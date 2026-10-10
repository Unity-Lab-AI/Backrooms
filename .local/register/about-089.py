import io

p = 'Mod/Rimrooms - Async Industries/About/About.xml'
s = io.open(p, encoding='utf-8-sig').read()

anchor = ' Gameplay acceptance is pending;'
addition = (' Every laboratory gate keeps its own list of everywhere it has connected to, which you can rename, pin, '
            'remove and clear. Opening a connection is no longer a button: the operator brings the gate up at the '
            'console over time, the console shows the progress, and leaving it unattended loses the charge. A route '
            'your crew has run before comes up faster than one they have never taken. A gate you have designated is '
            'a plainly blue door with a blue glow around it, so you can tell one from an ordinary door at a glance.')

assert anchor in s
assert 'blue glow around it' not in s
s = s.replace(anchor, addition + anchor, 1)
io.open(p, 'w', encoding='utf-8-sig', newline='').write(s)
print('About.xml description updated')
