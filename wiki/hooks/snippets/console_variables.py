"""Snippets for the Console variables page (docs/console-variables.md)."""

import re

from ._core import cite, data, esc, snippet, table, without_wip


# -------- console-variables.md, vip.md, juggernaut.md

@snippet("table:convars")
def table_convars(mode=None):
    """All console variables, or with mode="vip"/"jgr" only that in-development mode's own settings."""
    seen = {}
    for src in ("player", "gamemodes", "weapons"):
        d = data(src)
        if not d:
            continue
        for cv in d.get("convars", []):
            seen.setdefault(cv["name"], cv)
    rows = []
    for name in sorted(seen):
        cv = seen[name]
        own = re.search(r"(?:^|_)(vip|jgr)(?:_|$)", name)
        desc = cv.get("description", "")
        if mode:
            if not (own and own.group(1) == mode):
                continue
        else:
            if own:
                continue
            desc = without_wip(desc)
            if desc is None:
                continue
        rows.append([f"<code>{esc(name)}</code>", f"<code>{esc(cv.get('default', ''))}</code>", esc(desc) + cite(cv)])
    caption = None if mode else f"{len(rows)} variables extracted from the NT;RE source."
    return table([("Variable", False), ("Default", False), ("Description", False)], rows, caption=caption)
