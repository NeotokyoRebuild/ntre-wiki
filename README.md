# NT;RE Wiki

A wiki for [NEOTOKYO Rebuild](https://github.com/NeotokyoRebuild/neo). Pre-alpha. The wiki is built with [MkDocs](https://www.mkdocs.org/) and the Material theme, in `wiki/`.

## Quick Start

```sh
git clone https://github.com/sunmachine/ntre-wiki.git
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
- `deploy`: publishes the wiki; the 🚀 Deploy workflow runs it
- `.github/workflows/`: the 🏗 CI and 🚀 Deploy workflows

## Contributing

Contributions reach `main` through pull requests. Push your branch and open a PR against `main`: 🏗 CI runs `./check` on it, and once it passes you can merge your own PR.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for how to edit pages, add one, or change the game data, and [`WRITING-STYLE.md`](WRITING-STYLE.md) for how the wiki is written.

## Deploy

The wiki is published at https://sunmachine.github.io/ntre-wiki/. Maintainers deploy it with the 🚀 Deploy workflow, from the Actions tab. Each run publishes `main` as the next minor version (0.3 → 0.4) and makes it `latest`; choose `major` to start the next major version (0.4 → 1.0). Earlier versions stay in the header's version menu.

## License

All rights reserved. No license is granted at this stage.
