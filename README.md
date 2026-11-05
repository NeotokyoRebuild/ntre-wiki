# NT;RE Wiki

A wiki for [NEOTOKYO Rebuild](https://github.com/NeotokyoRebuild/neo). Pre-alpha. The wiki is built with [MkDocs](https://www.mkdocs.org/) and the Material theme, in `wiki/`.

## Quick Start

```sh
git clone https://github.com/NeotokyoRebuild/ntre-wiki.git
cd ntre-wiki
./setup
```

> [!NOTE]
> **Windows:** use WSL. Clone inside your Linux home folder, not under `/mnt/c`, so `./serve` sees your edits. On Ubuntu, run `sudo apt install python3-venv` before `./setup`.

### Modifying the wiki

```sh
./serve
```

## Layout

- `wiki/`: the MkDocs wiki, built from Markdown pages and game data extracted from the NT;RE source
- `setup`: sets up a checkout once: asks where your checkouts of the game's repositories are, and creates the Python environment
- `serve`: previews the wiki at http://127.0.0.1:8000/
- `check`: the checks every change must pass: the strict build, and the data checked against the game's code
- `deploy`: publishes the wiki, rolls it back and puts up the maintenance page (the 🚀 Deploy, ⏪ Rollback and 🚧 Maintenance workflows run it), and lists and deletes deployed versions
- `.github/workflows/`: the 🏗 CI, 🚀 Deploy, ⏪ Rollback and 🚧 Maintenance workflows

## Contributing

Contributions reach `main` through pull requests. Push your branch and open a PR against `main`: 🏗 CI runs `./check` on it, and once it passes you can merge your own PR. A PR that changes `.github/` (the workflows), `deploy`, `check` or `setup` also needs the maintainer's approval.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for how to edit pages, add one, or change the game data, and [`WRITING-STYLE.md`](WRITING-STYLE.md) for how the wiki is written.

## Deploy

The wiki is published at https://neotokyorebuild.github.io/ntre-wiki/. Maintainers deploy it with the 🚀 Deploy workflow, from the Actions tab. Each run publishes `main` as the next minor version after `latest` (0.3 to 0.4, skipping any version that already exists) and makes it `latest`. Choose `major` for the next major version (0.4 to 1.0), or type an exact version in M.m form, such as `0.4`. Earlier versions stay in the header's version menu. A run that would publish the same site `latest` already serves stops without deploying.

To undo a bad deploy, run the ⏪ Rollback workflow with the version to go back to (such as `0.2`). It points `latest` at that version without rebuilding anything. It doesn't change `main`, so fix or revert the change there before the next deploy, which publishes `main` again.

To take the wiki offline, run the 🚧 Maintenance workflow with its box checked. Every address into the wiki then shows a maintenance page, `wiki/maintenance.html`. The wiki itself moves, untouched, to `offline/` on the `gh-pages` branch, where it still works at https://neotokyorebuild.github.io/ntre-wiki/offline/latest/ for anyone who has the address. While the page is up, 🚀 Deploy and ⏪ Rollback still work, on the hidden wiki, so you can check a fix at that address first. Run the workflow again with the box unchecked to take the page down and bring the wiki back, with any deploys made in the meantime. If a run fails while waiting for GitHub Pages, run it again with the same choice: the branch is already right, so it asks Pages to build it again.

To remove old versions, run these locally. `delete` shows what it will delete and keep, asks first, and never deletes the version `latest` points at:

```sh
./deploy list
./deploy delete 0.1 0.2
```

## License

All rights reserved. No license is granted at this stage.
