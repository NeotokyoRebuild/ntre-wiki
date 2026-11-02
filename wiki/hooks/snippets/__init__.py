"""Data-driven snippets for the NT;RE wiki (MkDocs).

expand(body, meta) replaces {{kind:arg:...}} placeholders in Markdown pages with tables and
infoboxes built from data/*.json. Snippets return HTML that may contain [[slug|Label]] wiki
links and [[src:path:line]] citations; wiki_hooks.py resolves those afterwards.

Each snippet is a function marked with the name pages use for it, so searching for a
placeholder finds its code:

    @snippet("table:modes")
    def table_modes(): ...

The functions live in one module per wiki section, named after the folder under docs/:

    _core.py              shared helpers, table(), infobox(), the registry, {{stat:...}}
    classes.py            docs/classes/
    weapons.py            docs/weapons/ hub and category tables, and the weapon helpers
    weapon_page.py        {{weapon:NAME}} sections of a single weapon's page
    mechanics.py          docs/mechanics/, grouped by page
    game_modes.py         docs/game-modes/
    world.py              docs/world/
    console_variables.py  docs/console-variables.md
    about.py              docs/about/

Within a module, a divider comment names the page each group of snippets is for.
"""

import re

from . import about, classes, console_variables, game_modes, mechanics, weapon_page, weapons, world  # noqa: F401
from ._core import SNIPPETS, WEAPON_SNIPPETS, SnippetError, column_tip, data, esc
from .about import asset_mark
from .weapons import weapon

__all__ = ["SnippetError", "asset_mark", "column_tip", "data", "expand"]

# Every {{kind:...}} a registered snippet can answer, plus {{weapon:...}}.
KINDS = sorted({name.split(":")[0] for name in SNIPPETS} | {"weapon"})
SNIPPET_RE = re.compile(r"\{\{((?:" + "|".join(KINDS) + r"):[^}]+)\}\}")
INLINE_KINDS = ("stat", "asset")


def expand(body, meta=None, warn=print):
    """Replace {{...}} snippets. Block snippets (tables, infoboxes) are padded with blank
    lines so Markdown treats them as raw HTML blocks. A bad snippet is reported through
    warn() and left visible on the page."""
    meta = meta or {}

    def render(spec):
        if spec.startswith("weapon:"):
            name, _, arg = spec[len("weapon:"):].partition(":")
            wid = meta.get("weapon")
            if not wid:
                raise SnippetError(f"{{{{{spec}}}}} needs `weapon:` in the page's front matter")
            fn = WEAPON_SNIPPETS.get(name)
            if not fn:
                raise SnippetError(f"unknown snippet {{{{{spec}}}}}")
            w = weapon(wid)
            return fn(w, arg) if arg else fn(w)
        for key in sorted(SNIPPETS, key=len, reverse=True):
            if spec == key or spec.startswith(key + ":"):
                arg = spec[len(key) + 1:]
                return SNIPPETS[key](arg) if arg else SNIPPETS[key]()
        raise SnippetError(f"unknown snippet {{{{{spec}}}}}")

    def repl(m):
        try:
            out = render(m.group(1))
        except SnippetError as e:
            warn(str(e))
            return f'<code class="snippet-error">{esc(m.group(0))}</code>'
        inline = m.group(1).startswith(INLINE_KINDS)
        return out if inline else f"\n\n{out}\n\n"

    return SNIPPET_RE.sub(repl, body)
