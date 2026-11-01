# Contributing

Thanks for helping with the NT;RE wiki. This page says where things live and how to make the common kinds of change. It assumes you're comfortable with git, Markdown and a terminal.

Read [`WRITING-STYLE.md`](WRITING-STYLE.md) before you write anything. It covers voice, units, names, page layout and the wiki's markup.

## Set up

```sh
./setup     # once
./serve     # each time you work
```

`./setup` needs Python 3.9 or newer. It asks where your checkouts of the game's repositories are, [NeotokyoRebuild/neo](https://github.com/NeotokyoRebuild/neo) and [NeotokyoRebuild/neoAssets](https://github.com/NeotokyoRebuild/neoAssets). It suggests any it finds next to this repository and offers to clone a missing one there. Then it creates the Python environment in `wiki/.venv`. The paths go in this repository's git config (`ntre.neo`, `ntre.neoassets`), where the data tools read them. Run it again to change a path or repair the environment. Don't change either game checkout: the tools read them by commit.

`./serve` previews the wiki at http://127.0.0.1:8000/. It rebuilds when you save a page, a data file, `column-tips.yml` or the hook code.

The examples here assume `neo` sits next to this repository, at `../neo`.

## How a page is put together

Pages are Markdown files in `wiki/docs/`, in folders that follow the menu: `weapons/rifles/zr68-s.md` is the ZR68-S page. Each page mixes two kinds of content.

- **Prose** is yours to write and edit: headings, paragraphs, lists, callouts and table captions.
- **Data** is generated: `{{table:…}}`, `{{infobox:…}}`, `{{stat:…}}` and `{{weapon:…}}` placeholders. At build time each one becomes a table, an infobox or a number, read from the JSON files in `wiki/data/`, with a citation to the game's code.

So you can rewrite a page without touching a single number. When the data changes, every table and stat on every page follows.

## Fix or rewrite copy

1. Find the page in `wiki/docs/`. The path matches the address: `/mechanics/aux-power/` is `wiki/docs/mechanics/aux-power.md`.
2. Edit the words. Leave `{{…}}` placeholders where they are, and keep every `[[src:…]]` citation with the fact it supports.
3. Check it in the preview, then build with `.venv/bin/mkdocs build --strict` from `wiki/`.

The "Rewriting a page" section of `WRITING-STYLE.md` has the rules: keep citations word for word, don't lose a number, don't change a fact.

A number in prose is fine to type by hand if you round it and cite it, as long as the exact figure is in a table or infobox on the same page. To show an exact value in a sentence, use a stat instead: `{{stat:player:classes.recon.stats.run_speed}}` inserts Recon's run speed with its citation. The path is a chain of keys in `wiki/data/player.json`, and list items are named by their `id`, never by position.

## Add a page

1. Create the file in the folder that matches its place in the menu. The file name is the page's **slug**: lowercase, hyphens, and unique across the whole wiki. A folder's section page is its `index.md`, and its slug is the folder name.
2. Start it with a front matter `description` and a `# Title`:

   ```markdown
   ---
   description: "One line saying what the page covers"
   ---

   # Page title
   ```

3. Add it to `nav` in `wiki/mkdocs.yml`. A page that isn't in the menu fails the build.
4. Link to it from other pages with `[[slug|Label]]`.

To move a page to another part of the menu, move the file and update `nav`; links still work, because they use the slug. Renaming the file is different: the slug changes with it, so search for `[[old-slug` and update every link. The strict build reports any you miss as red links.

Weapon pages are different: they name their weapon in front matter (`weapon: weapon_zr68s`) and take every number from `{{weapon:…}}` snippets. Copy an existing weapon page to get the layout.

## Add or change a table column

Every column header shows a tooltip saying what it means. Tooltips live in `wiki/column-tips.yml`:

- under `columns`, a tip for a header wherever it appears
- under `pages`, a tip for a header that means something different on one page, keyed by that page's slug

If you add a column to a Markdown table, or a new generated table uses a new header, add its tip there. The build warns about any header without one.

## Change or add a number

Every gameplay number traces to a line of the game's code at a pinned commit. The commit is in each data file's `meta.neo_commit`.

1. Find the value in `wiki/data/weapons.json`, `player.json` or `gamemodes.json`. A value is a record like this:

   ```json
   "regen_delay_sec": {
     "value": 0.5,
     "source": "src/game/server/hl2/hl2_player.cpp:2259,2272-2277",
     "note": "Recharge starts 0.5 s after all suit devices turn off."
   }
   ```

2. Check it against the code at the pinned commit, not your checkout's current state:

   ```sh
   git -C ../neo show 120006db:src/game/server/hl2/hl2_player.cpp | sed -n '2255,2280p'
   ```

3. Change the `value`, and the `source` if the lines moved. `source` is a path relative to the repository root, then `:` and a line, a range (`12-15`) or a list (`12,20-22`). Separate several sources with `;`.
4. Run the data check from `wiki/`, then build and look at the pages that show the value:

   ```sh
   python3 tools/check_data.py
   ```

   It confirms, at the pinned commit, that every citation (in the data, the pages and the generators) points at lines that exist, and that every value read straight from a weapon script (`"Damage" "12"`) or a `ConVar` default still matches the code. `--fix` updates values of those two kinds from the code, and lists any derived values you then need to work out again.

The rules:

- **Never guess.** If the code is ambiguous, or the client and server disagree, record both in the `note` and flag it on the page in an amber **Unconfirmed** callout.
- **Show your working.** A value worked out from others carries `"derived": true` and a `formula`.
- **One source of truth.** A number shown in a table or infobox comes from the data, never typed into the page or into the generator code.

### Half-Life 2 leftovers

NT;RE runs on the Source engine, so its code and files still hold parts of Half-Life 2 that the game never uses: weapons, surface materials and so on. They stay out of the wiki, and you'll keep finding new ones. When you do:

- **Prove it's unused.** Cite what shows it: an SDK comment naming HL2 content, or the fact that only HL2's own files use it. Check NT;RE's side too. Some HL2-looking names are real NT;RE things: `weapon_remotedet` is the Detpack.
- **Flag a record you keep.** Add `"hl2_only": {"value": true, "source": "…", "note": "…"}` to it, as the penetration materials do. Generated tables skip flagged records. A new generator that lists records like these must skip them too.
- **List whole leftovers you don't keep.** Unused HL2 weapons go in `excluded` in `weapons.json`, with the reason.
- **Say when it's a judgement call.** If the code can't settle it, flag it anyway only on the maintainer's say-so, and write "by maintainer decision" in the `note`, with what couldn't be confirmed, as the `BLOODYFLESH` material does.

## Move to a newer version of the game

All citations point at one pinned commit of `neo`, so the wiki describes one version of the game. To move it to a newer commit:

1. Fetch the newer code into your checkout: `git -C ../neo fetch`. The tools read files by commit, so you don't need to check anything out.
2. See what changed, from `wiki/`:

   ```sh
   python3 tools/repin.py origin/master
   ```

   It sorts every citation into **unchanged**, **moved** (the same code, at new line numbers), **changed** (the cited code itself changed) and **gone** (its file was deleted), and lists the data records and pages behind each changed one.
3. Apply it with `--write`. That fixes the line numbers of moved citations, gives changed ones their nearest new lines, and updates `meta.neo_commit` in every data file.
4. Run `python3 tools/check_data.py --fix` to update the values read from weapon scripts and `ConVar` defaults, and to see which derived values need working out again.
5. Go through the "changed" list by hand: read the new code, then fix the value, the note or the page's wording. Build, and commit it all together.

## Add a generated table or infobox

Generated tables and infoboxes are Python functions in `wiki/hooks/generators.py`, registered in the `SNIPPETS` dictionary near the end of the file. To add one:

1. Write a function that reads the data with `data("player")` and so on, and returns `table(...)` or `infobox(...)`. Cite each value: `val(record)` gives the value with its citation, and `cite(record)` gives the citation alone.
2. Add it to `SNIPPETS`, for example `"table:cloak": table_cloak`.
3. Put `{{table:cloak}}` on the page.

Text the generators produce follows `WRITING-STYLE.md` like any other copy.

## Before you send a change

Build from `wiki/`, and if you touched the data or any citation, run the data check too:

```sh
.venv/bin/mkdocs build --strict
python3 tools/check_data.py
```

A clean build prints no warnings. It fails or warns on:

- broken `[[…]]` links and unknown `{{…}}` snippets
- stat paths that don't exist, or that use a list position instead of an id
- a page missing from `nav`
- a table column with no tooltip
- a mention of a game mode still in development outside its own pages (see "Modes in development" in `WRITING-STYLE.md`)

Then commit on a branch and open a pull request against `main`.

- **Commit messages** start with a short, imperative summary in sentence case ("Generate the cloak battery table from the data"), then a body that says why.
- **Style changes go with the change.** A change to how the wiki is written updates `WRITING-STYLE.md`, and a change to how it looks updates the Style guide page (`wiki/docs/about/style-guide.md`), in the same commit.
- **Assets** (images, logos) are documented on `wiki/docs/about/logos.md` with their source and rights.

## What not to touch

- `wiki/deploy.sh` publishes the site. Only the maintainer deploys.
- Don't modify the `neo` or `neoAssets` checkouts.
