"""Snippets for the World pages (docs/world/)."""

from ._core import WIP_MODES, WIP_TAG, cite, data, esc, snippet, table
from .game_modes import MODE_SLUGS, mode_link


# -------- world/maps.md

@snippet("table:maps")
def table_maps():
    gm = data("gamemodes")["maps"]
    rows = []
    for e in gm["list"]:
        md = e["mode"]
        if md in WIP_MODES:
            continue
        if md == "menu background":
            mlabel = '<span class="na">menu background</span>'
        else:
            mlabel = mode_link(md) if md in MODE_SLUGS else esc(md)
        wip = md in WIP_MODES
        cells = [f"<code>{esc(e['map'])}</code>", mlabel + (f" {WIP_TAG}" if wip else ""),
                 "Yes" if e["has_soundscape"] else "—"]
        rows.append(("wip", cells) if wip else cells)
    return table([("Map file", False), ("Mode (by suffix)", False), ("Soundscape", False)], rows,
                 caption=f"Maps on the official list.{cite(gm)} Each map's mode is worked out from its file name.")
