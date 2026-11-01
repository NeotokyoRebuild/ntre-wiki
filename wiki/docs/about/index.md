---
description: "What this prototype is, where its numbers come from, and what it leaves out"
---

# About this wiki

This is a prototype wiki for **NEOTOKYO Rebuild** (NT;RE). It's built with [MkDocs](https://www.mkdocs.org/) and the [Material](https://squidfunk.github.io/mkdocs-material/) theme.

Its job is to settle the structure, page types and visual design.

## How the numbers are sourced

Every stat on this site was extracted from the [NeotokyoRebuild/neo](https://github.com/NeotokyoRebuild/neo) repository. It comes from one of two places: the weapon scripts in `game/neo/scripts/`, or the C++ gameplay code in `src/game/`.

Each number has a footnote that links to the exact file and line it came from. The links are pinned to a specific commit (see the page footer).

Tables and stat blocks are generated from the data when the site is built, so no number is typed by hand twice. When the game changes, the data can be re-extracted and every page rebuilt.

## Page types demonstrated

- **Hub pages**: [[index|Main page]], [[weapons|Weapons]], [[classes|Classes]], [[game-modes|Game modes]]
- **Weapon pages**: one Markdown file per weapon, in a fixed layout (overview, general stats, damage, shots to kill, time to kill, handling, availability). You can edit the prose by hand. Every number comes from a `{{weapon:…}}` snippet.
- **Mechanic articles**: hand-written explanations with citations, such as [[thermoptic-camouflage|Thermoptic camouflage]] and [[damage|Damage & penetration]]
- **Reference tables**: [[console-variables|Console variables]], [[maps|Maps]], [[loadouts|Loadouts & ranks]]

## Not in the prototype

- **Editing and page history.** Pages are Markdown files in the repository.
- **Images.** Grey boxes mark where screenshots or renders would go, until asset licensing is decided.
- **Lore and story.** This pass covers gameplay mechanics and stats only.
- **Terminology and external resources pages.**

## Build

In `wiki/`, install the requirements with `pip install -r requirements.txt`, then run `mkdocs serve`.

- **Pages** live in `docs/`.
- **Extracted game data** lives in `data/`.
- **Snippets, wiki links and citations** are handled by `hooks/wiki_hooks.py` and `hooks/generators.py`.

See [[style-guide|Style guide]] for the markup.
