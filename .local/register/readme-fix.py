import io

p = 'README.md'
s = io.open(p, encoding='utf-8').read()

old = ('**Current development version: 0.4.1-dev.** The [connected-colony checkpoint](docs/implementation/CONNECTED_COLONY_CHECKPOINT.md) '
       'records the source/build foundation, unfinished integration and owner-requested pause to conserve usage. The '
       '[native-provider checkpoint](docs/implementation/PHASE_3_NATIVE_PROVIDER_BUILD.md) remains the preceding staged build. It extends the '
       '[0.3.0 company systems](docs/implementation/PHASE_3_BUILD_RECORD.md): hiring, physical procurement, facility observations, native '
       'research/evidence and menu presentation. Existing-content replacement, the full campaign and runtime acceptance remain in progress; '
       'no game launch is required to continue independent implementation.')

new = (
'**Current development version: 0.9.9-dev.** Every checkpoint has its own record under '
'[`docs/implementation/`](docs/implementation/), and [`docs/NOW.md`](docs/NOW.md) is the single '
'page that says what is true right now: the published commit, the build counts, the reproduced '
'assembly hash, and what is open in order.\n'
'\n'
'What works in source today, briefly: a gate is an **ordinary door you designate** rather than a '
'custom machine, at sizes from 1x1 to 2x3; **bringing a connection up is work** an operator does '
'at a console, faster on a route the crew has run before; each gate keeps its own **address book** '
'of everywhere it has dialled; colonists and animals cross, with the gate\'s width deciding what '
'fits through; coordinates generate as rooms, corridors and **facilities** that span several rooms '
'at once; what lives there **follows a crew to the doorway** in the worst spaces and, on an '
'advanced machine, can come through behind them; and an **odd-origin economy**, company bonds, a '
'corporate trader and a credits ladder sit on top of it.\n'
'\n'
'Six checkers run without the game and gate every checkpoint: package integrity, keyed strings, '
'DLC gating, info cards, documentation conformance, and the Gate 0 documentation audit. The build '
'is **deterministic** and proved so by recompiling twice from clean and comparing the assembly '
'hash. **Existing-content replacement, the remaining scenarios and all runtime acceptance are '
'still open**, and no game launch is required to continue implementation.')

assert old in s, 'README paragraph not found verbatim'
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('README current-state paragraph rewritten')
