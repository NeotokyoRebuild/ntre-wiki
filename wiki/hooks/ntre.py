"""MkDocs entry point for the wiki's hooks.

`mkdocs serve` imports this file once, when it starts. To pick up edits to the hook code
without a restart, the real hooks live in wiki_hooks.py and are reloaded at the start of
every build (on_config runs once per build), then each event is passed on to them.
"""

import importlib.util
from pathlib import Path

_HOOKS = Path(__file__).resolve().parent
_impl = None


def _load():
    spec = importlib.util.spec_from_file_location("ntre_wiki_hooks", _HOOKS / "wiki_hooks.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def on_config(config):
    global _impl
    _impl = _load()
    return _impl.on_config(config)


def on_env(env, config, files):
    return _impl.on_env(env, config, files)


def on_files(files, config):
    return _impl.on_files(files, config)


def on_page_markdown(markdown, page, config, files):
    return _impl.on_page_markdown(markdown, page, config, files)


def on_page_content(html, page, config, files):
    return _impl.on_page_content(html, page, config, files)
