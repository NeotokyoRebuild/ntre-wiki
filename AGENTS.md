# Agent guidelines

Rules for anyone, human or model, working in this repository.

## What this is

A monorepo for the NEOTOKYO Rebuild (NT;RE) wiki. `wiki/` is the wiki, built with MkDocs and the Material theme.

## Layout

- `setup`, `serve`: set up a checkout once, and preview the wiki
- `check`: the checks every change must pass, the strict build and `tools/check_data.py`. CI runs it on every pull request, and `deploy` runs it first.
- `deploy`: publishes a new version of the wiki (the 🚀 Deploy workflow runs it); `deploy rollback VERSION` points `latest` at an earlier version (the ⏪ Rollback workflow runs it); `deploy list` and `deploy delete VERSION...` manage deployed versions, locally only
- `.github/workflows/`: `ci.yml` (🏗 CI, every pull request into `main`), `deploy.yml` (🚀 Deploy, run by hand) and `rollback.yml` (⏪ Rollback, run by hand with the target version as its input; it shares the deploy's queue). `.github/actions/setup/` checks out `neo` and `neoAssets` next to the repository and runs `./setup`, for both.
- `wiki/mkdocs.yml`: site config, including the sidebar menu (`nav`). A new page needs a nav entry.
- `wiki/docs/**/*.md`: pages. Folders follow the menu (`weapons/rifles/zr68-s.md`); a folder's `index.md` is its section page.
- `wiki/data/*.json`: gameplay data extracted from the NT;RE source, one record per value with a `source` citation
- `wiki/hooks/wiki_hooks.py`: the MkDocs hooks: wiki links, citations, snippets, column tooltips and the build checks. `ntre.py` is only the entry point `mkdocs.yml` names; it reloads `wiki_hooks.py` and `generators.py` on every build, so `mkdocs serve` picks up edits without a restart.
- `wiki/column-tips.yml`: the tooltip for every table column header, shared or per page
- `wiki/hooks/generators.py`: builds the `{{table:…}}`, `{{infobox:…}}`, `{{stat:…}}` and `{{weapon:…}}` snippets from the data
- `wiki/tools/`: data tools, standard library only. `check_data.py` checks every citation and the values read from weapon scripts and ConVars against the pinned commit (`--fix` updates those values). Run it after touching the data or citations. `repin.py COMMIT` moves every citation to a newer `neo` commit (see CONTRIBUTING.md); the tools read files with `git show`, never fetch, and never touch the checkouts.
- `wiki/docs/stylesheets/ntre.css`: the skin; colours are `--ntre-*` tokens with dark (`slate`) and light (`default`) sets
- `wiki/overrides/`: theme overrides. `partials/logo.html` inlines `docs/assets/nt-mark.svg` (the primary logo, from Wireframe) into the header. `partials/source.html` draws the header's repository links, one per entry in `extra.repos` (`mkdocs.yml`), and `docs/javascripts/sources.js` fills in each one's release, stars and forks. `repo_url` points at `NeotokyoRebuild/neo`, so `edit_uri` is a full address into this repository.

Set up with `./setup`: it creates `wiki/.venv` and records the `neo` and `neoAssets` checkouts in this repository's git config as `ntre.neo` and `ntre.neoassets`, which the data tools read. Preview with `./serve`; check with `./check`, whose strict build fails on red links and unknown snippets. A clean build prints no warnings. Keep builds and deploys loud: never add `--quiet` to a strict build, because it hides the warnings and strict mode then passes them.

## Deploying

The wiki is published at https://sunmachine.github.io/ntre-wiki/, from the `gh-pages` branch of `sunmachine/ntre-wiki`. The 🚀 Deploy workflow runs `./deploy`, which has `mike` build `main` into a new version folder (by default the next minor version after the one `latest` points at, skipping versions that already exist; the next major when chosen; or an exact version, which must be M.m), points `latest` and the site's root at it, and pushes. It refuses a dirty tree, a commit that isn't on `main` in `sunmachine/ntre-wiki`, a failing `./check`, symlinks, and changes outside the new version, `latest/` and mike's root files. The published address is set only in `deploy`: don't hard-code it in `mkdocs.yml` or in pages. Old versions are removed only by hand, locally: `./deploy delete` lists what goes and what stays, asks before deleting, and refuses the version `latest` points at. Never delete versions without the maintainer's say-so. Never use `mkdocs gh-deploy`: it replaces the whole branch, and every earlier version with it. GitHub Pages rejects symlinks, which is why `mkdocs.yml` sets mike's `alias_type: copy`. Deploying publishes to a public site: do it only when asked.

A ruleset on `main` requires a pull request that passes 🏗 CI, and blocks force pushes and deletion. No approval is needed, except that `.github/CODEOWNERS` makes the maintainer's approval required for changes to `.github/`, `deploy`, `check` and `setup`; add any new file the workflows run to it. A ruleset on `gh-pages` blocks force pushes. Contributors merge their own PRs once CI passes. The maintainer, and agents working with them, push to `main` directly through the admin bypass.

## Style guide

**Read [`WRITING-STYLE.md`](WRITING-STYLE.md) before writing or editing any page, or any text the generators produce.** It covers voice, keeping pages easy to read, sourcing, units, names, page anatomy and markup. The wiki's Style guide page (`wiki/docs/about/style-guide.md`) includes it and adds the visual rules. A change to how the wiki is written updates `WRITING-STYLE.md`, and a change to how it looks updates the style guide page, in the same commit as the change. The Branding pages document every asset with its source and rights; a new or changed asset updates `about/logos.md` too. The palette table on `about/colours-and-type.md` is generated from `ntre.css`, so it needs no hand edits.

[`CONTRIBUTING.md`](CONTRIBUTING.md) is the how-to for human contributors. When a workflow it describes changes (setup, markup, data records, build checks), update it in the same commit.

## Data rules

- Every gameplay number must trace to a `path:line` in `NeotokyoRebuild/neo` or `NeotokyoRebuild/neoAssets`. Where the local checkouts are is up to each contributor: `git config ntre.neo` and `git config ntre.neoassets` give them (the examples here use `../neo`). The commit is pinned in each JSON file's `meta.neo_commit`.
- Read cited code at the pinned commit, never from the checkout's working tree, which can be ahead of or behind it: `git -C ../neo show <commit>:<path> | sed -n '<a>,<b>p'`. Don't number lines with `nl`: it skips blank lines, so every number after one is wrong.
- Never guess a value. If the code is ambiguous or client and server disagree, record both in a `note` and say so on the page.
- Values derived arithmetically carry `derived: true` and a `formula`.
- A number shown in a table or infobox comes from the data: never type one into a page or into the generator code (`generators.py`). A generator that needs a number reads it from the data, like everything else.
- Half-Life 2 leftovers that NT;RE doesn't use stay out of the wiki. Flag such a record `hl2_only`, with its source; generated tables skip it. See "Half-Life 2 leftovers" in CONTRIBUTING.md.
- Don't modify the `neo` or `neoAssets` checkouts.

## Conventions

- Slugs are lowercase with hyphens and unique across the wiki: a page's slug is its file name without `.md`, or its folder name for an `index.md`. Links use slugs, so moving a page to another folder needs only a `nav` change, but renaming its file changes the slug and breaks every `[[slug|…]]` to it: search for `[[old-slug` and update them in the same commit.
- In content, `[[slug|Label]]` is a wiki link and `[[src:path:line]]` is a citation that becomes a footnote. Plain Markdown links work too.
- Weapon pages name their weapon in front matter (`weapon: weapon_zr68s`) and take every number from `{{weapon:…}}` snippets.
- Quote front-matter values that contain a colon.
- Python dependencies are pinned in `wiki/requirements.txt` (MkDocs Material, and `mike` for versioned deploys).

## Engine

The wiki engine is MkDocs Material (decided 2026-11-01). Material reaches end of life on 2027-05-05; its successor, Zensical, reads the same `mkdocs.yml`, so plan the move to it before then.

## Open decisions

- Data model for game facts
- Content and media licensing (currently all rights reserved)
- Hosting: GitHub Pages, from the `gh-pages` branch of `sunmachine/ntre-wiki`, for now
