# Writing style

How the NT;RE wiki is written. It applies to every page and to the text generated from game data. The wiki shows the same rules on its About → Style guide page, which includes this file, so change them here.

<!-- --8<-- [start:guide] -->

## Who we write for

Players. Someone between rounds who wants an answer, or someone new who wants to understand a mechanic. They know shooters and the game's own terms (HP, XP, AUX, sprint, loadout). They don't know Source engine internals or C++, and they shouldn't need to.

Their attention is limited, so every sentence has to earn its place.

## Voice

- Plain and direct. Address the player as *you*, in the present tense.
- Open with what the thing is and why it matters. Name the subject in bold in the first sentence.
- Lead with what it means for the player: what to do, what to expect, what to avoid. How the code does it comes second, if at all.
- One idea per sentence. Keep sentences short, and paragraphs to one to three sentences.
- Use everyday words. Say *hitbox*, not *hull*. Leave out function names, file names and engine terms like *tick* and *renormalised* unless the reader needs them; if they do, explain the term once.
- Cut filler, hype and hedging that carries no information.
- British spelling (*colour*, *armour*, *behaviour*). Code identifiers and quoted strings keep their own spelling.
- Headings in sentence case: *Weapon speed scale*, not *Weapon Speed Scale*.

## Keep the load light

- **No more than two numbers in a sentence.** Round in prose ("about 24 seconds") and give exact figures in tables and infoboxes.
- **Move the mechanics out of the way.** Formulas, code behaviour and edge cases most readers can skip go in a collapsed **Technical details** box at the end of the section. The box keeps its citations, so nothing is lost.
- **Put server settings last.** Console variables only server admins can change go under a **For server admins** heading at the end of the page.
- **Use lists for sets of conditions, and tables for comparisons.** A sentence that lists four conditions is a list.
- **One caveat, once.** If something is unconfirmed, say so in one callout, not in every sentence that touches it.

For example, instead of:

> Each cloaked player has a visibility factor from 0 to 1 that controls how strong the shimmer and tint are. Standing still (≤20 u/s) lowers it by 1.1 per second; moving raises it by speed × 0.004 per second.

write:

> The faster you move, the more you shimmer. Stand still and the shimmer fades in about a second.

and put the first version in the Technical details box.

## Facts and sources

- Every gameplay number cites the line it comes from. `[[src:path:line]]` becomes a footnote linked to the game's source at the pinned commit.
- A citation never comes between a number and its unit. Write it after the unit (`5/s[1]`, `200 units per second[1]`). In a numeric table column the build moves it in front of the number, so the numbers in the column stay aligned; you still write it after the value. The build also fixes it if you write a unit after `{{stat:…}}`, whose citation follows the number.
- Never guess. If the code is ambiguous, or client and server disagree, say so in an amber callout labelled **Unconfirmed**, **Unverified** or **Unresolved**.
- Say how a claim was established: "inferred from the code" is different from "tested in game".
- Tables and infoboxes take their numbers from the extracted data, not from hand-typed copies.
- Rewording must not change a fact. Rounding in prose is fine when the exact figure is in a table, infobox or Technical details box on the same page.

## Numbers and units

Spell units out in prose and abbreviate them in data. In data, an abbreviated unit sits right against its number, with no space: `0.5s`, `5/s`, `256u/s`. Game terms keep theirs: `225 HP`. **Prose** is anything written as a sentence: paragraphs, list items, callouts and table captions. **Data** is table cells, infobox values and stat strips.

| Quantity | In prose | In data |
| --- | --- | --- |
| Time | 2.16 seconds, 250 milliseconds, 3.25 minutes | `2.16s`, `250ms`, `3.25min` |
| Speed | 256 units per second | `256u/s` |
| Distance | 150 units; metres only where the game uses them | `150u`, `45.72m` |
| Angle | 1 degree | `1°` |
| Multiplier | ×0.85, times sign and no space | `×0.85` |
| Range | 0.675–1.0, en dash and no spaces | `0.675–1.0` |
| Damage | Effective damage, with the ×1.485 modifier applied, unless labelled base | `17.82` (base 12) |
| Game terms | HP, XP, AUX, RPM: players know these, so keep them short | `225 HP` |

As an adjective, hyphenate: a 10-second delay, a 13-second cloak.

## Names

- **Weapons** use their in-game display names: MPN45, SRM-S, ZR68-L, Murata Supa-7, MilSO.
- **Classes** are capitalised: Recon, Assault, Support.
- **In tight table columns**, Recon, Assault and Support shorten to **R**, **A** and **S**, always in that order. Where a column also gives the XP a class needs, write the letter and the number together: **R4 A10 S20**. A letter alone means no XP is needed. The column's tooltip explains the notation, and each entry has its own tooltip naming the class and the rank.
- **Game modes** take the full name first, then the code: Capture the Ghost (CTG).
- **Teams**: Jinrai and NSF. The objective is *the ghost*, lowercase in running text.
- **Thermoptic camouflage** is *the cloak* after its first mention.
- **Console variables** and file names go in `code`, with their default where it matters: `mp_friendlyfire 1`.

## Page anatomy

1. A `# Title`, and a one-line `description` in the front matter
2. A lead of one or two short paragraphs that stands on its own
3. An **infobox** for classes, modes and mechanics with stats
4. Sections under `##` headings. The contents list on the right is automatic.
5. **For server admins**, if the page has any
6. The generated references, last

**Game mode pages** open with an **Objective** section (what each side is trying to do, then the win conditions table) and a **Round flow** section (the phases of a round in order, and how a match ends), before anything else.

**Weapon pages** follow one layout, in this order: Overview, General stats, Damage, Shots to kill, Time to kill, Handling, then anything weapon-specific (bolt action, heat), Availability, Suppressor and Technical notes. The prose is yours to write; the numbers come from `{{weapon:…}}` snippets, which read the weapon named in the front matter (`weapon: weapon_zr68s`).

- Comparisons go in tables, not lists. Numbers are right-aligned in monospace.
- Every column header in a data table has a tooltip saying what it means. Tips live in `wiki/column-tips.yml`: once per header under `columns`, or under `pages` for a header that means something different on one page. A generated table can also pass its own. Write a tip's header the way the table shows it, with data units closed up (`Pen. to cross 12u`, not `12 u`): the build closes up units before it looks the tip up. The build warns about any header without one.
- Hit locations with the same multiplier share a column: head / chest, stomach / arms, legs.
- Link a page's first mention in each section, not every mention.
- Page addresses follow the menu: `/weapons/rifles/zr68-s/`. Folders and file names are lowercase with hyphens, and every slug is unique across the wiki.

### Markup

- `[[slug|Label]]` links to another page. A slug is the file name without `.md`, or the folder name for an `index.md`.
- `[[slug#heading|Label]]` links to a section of another page.
- `[[src:path:line]]` is a citation. Separate several with `;`.
- `{{table:…}}`, `{{stat:…}}` and `{{weapon:…}}` insert tables and numbers generated from the data.
- `{{stat:player:classes.recon.stats.run_speed}}` inserts one cited value from `wiki/data/player.json`. Name an item in a list by its `id`, never by its position; the build rejects `classes.0`.
- `!!! info "Label"` is a neutral callout, for notes.
- `!!! warning "Label"` is an amber callout, for anything quirky, unverified or in progress.
- `??? note "Technical details"` is the collapsed box for mechanics most readers can skip.

Indent a callout's or box's body by four spaces.

## Rewriting a page

When you reword an existing page, for clarity or to bring it up to this guide:

- **Keep every citation**, word for word. Move it with the fact it supports, for example into a Technical details box, but never drop or edit it.
- **Don't lose a number.** If one leaves the main text, it goes into the Technical details box. Rounding in prose is fine when the exact figure stays on the page.
- **Don't change a fact or add one.** If you can't say something more simply without changing what it means, leave it as it is.
- **Leave generated parts alone:** `{{…}}` snippets, infobox data and table cells. Table captions are prose, so reword those.
- **Check links before renaming a heading.** Other pages link to sections with `[[page#heading|…]]`; search for the heading's anchor first.
- **Build with `mkdocs build --strict`** (from `wiki/`). It fails on broken links and unknown snippets.

## Modes in development

- Game modes still in development are named only on their own pages, along with the roles they assign and the weapons those roles use. Nothing else in the wiki mentions them: not class, weapon or map lists, not comparisons, not the main page, not this guide. The one exception is the table of modes on the Game modes page, where they're tagged **WIP**.
- Their own pages open with an amber **Work in progress** callout and a neutral **Not a class you can pick** callout, and hold everything about the mode: its role, the role's stats and weapon, and its server settings.
- Text that comes from the data is filtered so it doesn't name them. The build warns about any page that does.

<!-- --8<-- [end:guide] -->

## Modes in development: specifics

Kept out of the wiki's style guide page, which follows the rule above.

- The modes in development are **VIP** and **Juggernaut** (JGR). Their pages are `game-modes/vip.md` and `game-modes/juggernaut.md`.
- Their roles are the VIP and the Juggernaut; their weapons are the **SMAC** (VIP) and the **BALC** (Juggernaut). Each weapon is a section of its mode's page: `[[vip#smac|SMAC]]`, `[[juggernaut#balc|BALC]]`.
- `without_wip()` in `wiki/hooks/generators.py` filters them out of data text, and `WIP_TERMS` in `wiki/hooks/wiki_hooks.py` is the build check. `WIP_ALLOWED_IN` there exempts the modes table on the Game modes page. When a mode leaves development, take it out of `WIP_MODES`, `WIP_CLASSES` and `WIP_WEAPONS` and those two places, and list it like any other mode.
