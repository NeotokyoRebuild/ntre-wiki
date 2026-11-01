# NT;RE Wiki

A wiki for [NEOTOKYO Rebuild](https://github.com/NeotokyoRebuild/neo). Pre-alpha. The wiki is built with [MkDocs](https://www.mkdocs.org/) and the Material theme, in `wiki/`.

## Quick Start

```sh
git clone https://github.com/sunmachine/ntre-wiki.git
cd ntre-wiki
./setup
```

### Modifying the wiki

```sh
./serve
```

## Layout

- `wiki/`: the MkDocs wiki, built from Markdown pages and game data extracted from the NT;RE source
- `setup`: sets up a checkout once: asks where your checkouts of the game's repositories are, and creates the Python environment
- `serve`: previews the wiki at http://127.0.0.1:8000/

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for how to edit pages, add one, or change the game data, and [`WRITING-STYLE.md`](WRITING-STYLE.md) for how the wiki is written.

## Deploy

The wiki is published at https://sunmachine.github.io/ntre-dev/wiki/, under `wiki/` on the `gh-pages` branch of [sunmachine/ntre-dev](https://github.com/sunmachine/ntre-dev). That branch also hosts other write-ups, so deploys go through [mike](https://github.com/jimporter/mike), which only touches `wiki/` and keeps one folder per version for the header's version menu.

Once per checkout, add the remote and a local `gh-pages` branch:

```sh
git remote add ntre-dev git@github.com:sunmachine/ntre-dev.git
git config remote.ntre-dev.fetch '+refs/heads/gh-pages:refs/remotes/ntre-dev/gh-pages'
git fetch ntre-dev && git branch --track gh-pages ntre-dev/gh-pages
```

Then commit, push to git, and run:

```sh
wiki/deploy.sh                          # redeploy the current latest version
wiki/deploy.sh 0.2 "0.2 (prototype)"    # deploy a new version and make it latest
wiki/deploy.sh --dry-run                # everything except the push
```

It does what a CI job would: it only deploys commits already pushed to `main` in git, from a clean tree, after a strict build. Then it checks that nothing outside `wiki/` changed and that there are no symlinks (GitHub Pages rejects them), pushes, and waits for GitHub Pages to report success.

The published address lives only in `deploy.sh` (override it with `NTRE_WIKI_URL`). `mkdocs.yml` reads it from that variable, so local builds carry no host URL, and every version's pages name `latest/` as their canonical address.

## License

All rights reserved. No license is granted at this stage.
