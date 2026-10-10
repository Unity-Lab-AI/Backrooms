import io

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()

block = u"""
## Public face: the site, the Workshop page and the collection

**Verbatim owner direction (2026-09-29):** *"fyi when we get to it we will build a github deployable html build that catologs the whole mod and is the main mod site wiki and documentation dump in a beauty of a deployable github page with what ever you can do so the deploy address is not some random git hub address but is a nice backrooms url for github deployed page where we document all the mods capabilities and howto and related public facing docs and information into a website that lays everything out top to bottom beautiffully just like other rimworld mods make theri third party sites, not to metione the building of the steam workkshop mod collection and workshop mod deploy for our mode with write ups for  both with links in them to each other and the deployed site so things will have to be deployed and settled before doing the proper order of setting up the workfshop collection and the mod in the workshop, idk maybe we will use a playwrite thing so you can click through steam and set it all up keeping me from having to do it all"*

**Not started. Owner said *"when we get to it"*, and it is correctly last:** every one of these artefacts describes the mod, so each is written twice if the mod is still changing underneath it. The same reason the player-facing how-to sits at the end of the build order.

### The ordering the owner named, which is a real dependency chain

1. **The mod is settled** - content set final, scenarios in, nothing still being retired.
2. **The site is deployed and working**, at its proper address.
3. **Then** the Workshop mod page, whose write-up links to the site.
4. **Then** the Workshop collection, whose write-up links to both.

Owner's words: *"things will have to be deployed and settled before doing the proper order of setting up the workfshop collection and the mod in the workshop"*. Doing any of it earlier means publishing links that point at nothing.

### The site

- [ ] **A GitHub Pages build that catalogues the whole mod** - capabilities, how-to, and the public-facing documentation, *"top to bottom"*, in the shape other RimWorld mods use for their third-party sites.
- [ ] **A real domain, not a `github.io` path.** *"a nice backrooms url"*. This needs a domain the owner controls plus a `CNAME` file in the Pages branch and DNS records pointing at GitHub. **The domain is the owner's to choose and register** - ask before building the Pages config, because a custom domain and a project-path deploy are configured differently and the wrong one means rebuilding.
- [ ] **Generated, never hand-maintained.** `tools/make-readable-html.py` is already the seed of this: it renders documents to standalone styled HTML with no external dependencies. The site is that tool grown up - more pages, navigation, a real front page - so the site cannot drift from the documentation the way a hand-written site would.
- [ ] **`check-doc-conformance.py` should cover the generated site**, so a published page cannot claim a version or a branch the build does not have.

### The Steam Workshop

- [ ] **The mod page write-up**, linking to the site.
- [ ] **The collection**, with its own write-up, linking to the mod page and the site.
- [ ] **Both written from the same source as the site**, so three descriptions of one mod cannot disagree.
- [ ] **Owner idea, verbatim:** *"idk maybe we will use a playwrite thing so you can click through steam and set it all up keeping me from having to do it all"* - Playwright driving the Steam Workshop UI. **Ask before doing this**: it means automating an authenticated session on the owner's Steam account, which is a different kind of action from anything done so far and needs explicit permission, not an assumption. The alternative is a prepared write-up the owner pastes, which is far less work for whoever is not doing the clicking.

### Standing constraints that still apply

- **No Claude attribution** in any of it - site, Workshop page, collection write-up.
- **The owner alone launches, sorts and publishes.** Deployment of a site is not the same act as launching the game, but the Workshop is the owner's account and the owner's decision.

"""

anchor = u'\n**Verbatim owner direction (2026-09-29):** *"real quick make this html open able'
assert anchor in s, 'anchor not found'
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('publishing phase recorded verbatim in TODO.md')
