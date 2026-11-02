"""Snippets for the About pages (docs/about/)."""

import re

from ._core import ROOT, esc, snippet, table


# -------- about/logos.md

@snippet("asset:mark")
def asset_mark():
    svg = (DOCS / "assets" / "nt-mark.svg").read_text()
    return re.sub(r"^\s*<!--.*?-->\s*", "", svg, flags=re.S).strip()


# -------- about/colours-and-type.md

DOCS = ROOT / "docs"
STYLESHEET = DOCS / "stylesheets" / "ntre.css"
TOKEN_USES = {
    "bg": "Page background",
    "surface-2": "Code, table headers, infobox images, hover",
    "surface-3": "Current nav item, stat bar track",
    "border": "Hairlines",
    "border-strong": "Callout rules, tags",
    "text": "Body text",
    "text-strong": "Headings, emphasis, link text",
    "muted": "Secondary text, labels, captions",
    "red": "Brand dot: page titles, current nav item",
    "underline": "Link underline and hover fill",
    "underline-hot": "Brief pulse at the end of the hover fill",
    "red-soft": "Red of the Open Collective badge",
    "jinrai": "Jinrai team colour",
    "nsf": "NSF team colour",
    "warn": "Warning callouts",
    "danger": "Links to missing pages",
    "bar": "Stat bar fill",
}


@snippet("table:palette")
def table_palette():
    css = STYLESHEET.read_text()
    block = re.search(r'^\[data-md-color-scheme="slate"\] \{(.*?)^\}', css, re.S | re.M).group(1)
    rows = []
    for name, value in re.findall(r"--ntre-([\w-]+):\s*(#[0-9a-fA-F]{3,8});", block):
        if name not in TOKEN_USES:
            continue
        swatch = f'<span class="swatch" style="background:{value}"></span>'
        rows.append([f"{swatch}<code>--ntre-{esc(name)}</code>", f"<code>{value.lower()}</code>", esc(TOKEN_USES[name])])
    return table([("Token", False), ("Value", False), ("Used for", False)], rows,
                 caption="Read from the dark-scheme block of <code>docs/stylesheets/ntre.css</code> at build time.")
