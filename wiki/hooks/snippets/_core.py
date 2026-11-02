"""Shared helpers for every snippet module: data loading, citations, formatting, the table()
and infobox() builders, the work-in-progress filters, and the @snippet registry."""

import json
import re
from functools import lru_cache
from pathlib import Path

import yaml


# -------- Snippet registry

class SnippetError(Exception):
    """A snippet a page asked for can't be built. The build reports it and fails."""


# "table:modes" -> function. Filled by @snippet as each section module is imported.
SNIPPETS = {}
# "stats" -> function, for {{weapon:stats}}. Each function takes the page's weapon first.
WEAPON_SNIPPETS = {}


def snippet(name):
    """Register a function as the {{name}} snippet, so the name a page uses sits on the function.

    @snippet("table:modes") makes {{table:modes}} call it, and {{table:modes:ARG}} call it with ARG.
    @snippet("weapon:stats") makes {{weapon:stats}} call it with the page's weapon."""
    registry, key = (WEAPON_SNIPPETS, name[len("weapon:"):]) if name.startswith("weapon:") else (SNIPPETS, name)

    def register(fn):
        if key in registry:
            raise ValueError(f"{{{{{name}}}}} is registered twice: {registry[key].__name__} and {fn.__name__}")
        registry[key] = fn
        return fn

    return register


# -------- Paths and data

ROOT = Path(__file__).resolve().parents[2]  # wiki/
DATA = ROOT / "data"


@lru_cache(maxsize=None)
def data(name):
    path = DATA / f"{name}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


# -------- Work-in-progress modes

# VIP and Juggernaut are work-in-progress modes. Stat lists keep them, but
# last, muted and tagged, so they don't compete with the core game.
WIP_CLASSES = {"vip", "juggernaut"}
WIP_MODES = {"vip", "jgr"}
WIP_WEAPONS = {"weapon_smac": "VIP weapon", "weapon_balc": "Juggernaut weapon"}
WIP_TAG = '<span class="tag wip" title="Work in progress">WIP</span>'
# Game modes still in development (VIP, Juggernaut), their roles and their weapons are named only
# on their own pages. without_wip() takes them out of text that comes from the data.
WIP_NAME = re.compile(r"\bVIP\b|[Jj]uggernaut|\bJGR\b|\bSMAC\b|\bBALC\b")
WIP_SCRUB = [
    (re.compile(r" except (?:VIP and )?Juggernaut\b"), ""),       # "All classes except Juggernaut"
    (re.compile(r",? (?:VIP|vip) and [Jj]uggernaut\b"), ""),     # "ghost carrier, VIP and juggernaut"
    (re.compile(r" and (?:VIP|Juggernaut)\b"), ""),               # "Recon and VIP", "Recon and Juggernaut"
    (re.compile(r"\b(?:VIP|JGR)=\d+,\s*|,\s*(?:VIP|JGR)=\d+"), ""),  # "TDM=0, CTG=1, VIP=2, DM=3"
    (re.compile(r" or escaping as (?:the )?VIP\b"), ""),
    (re.compile(r"\s*\(not a loadout choice\)"), ""),
]


def without_wip(text):
    """Text with mentions of the in-development modes removed, or None if it's about them."""
    for rx, rep in WIP_SCRUB:
        text = rx.sub(rep, text)
    return None if WIP_NAME.search(text) else text


# -------- Formatting

def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def cite(obj):
    """Citation markup for a {"value", "source"} record (or a raw source string)."""
    src = obj if isinstance(obj, str) else (obj or {}).get("source")
    if not src:
        return ""
    return f"[[src:{src}]]"


PATH_RE = re.compile(r"((?:src|game)/[\w/.\-]+\.\w+:\d+(?:-\d+)?(?:,\s?\d+(?:-\d+)?)*)")


def cite_text(text):
    """Turn inline 'path:line' references in agent notes into citations."""
    text = esc(text)
    text = PATH_RE.sub(lambda m: f"[[src:{m.group(1)}]]", text)
    # Drop parentheses left holding only citations/commas.
    text = re.sub(r"\(\s*((?:\[\[src:[^\]]+\]\][\s,;]*)+)\)", lambda m: re.sub(r"[\s,;]+", "", m.group(1)), text)
    return text


def fmt(n):
    if isinstance(n, float):
        return f"{n:g}"
    return str(n)


def plural(n, unit):
    """Prose units, spelled out: plural(1, "second") -> "1 second", plural(2.5, "second") -> "2.5 seconds"."""
    return f"{fmt(n)} {unit}" + ("" if n == 1 else "s")


def val(obj, suffix=""):
    """Format a {"value", "source"} record as value + citation."""
    if obj is None or obj.get("value") is None:
        return '<span class="na">—</span>'
    v = obj["value"]
    if isinstance(v, bool):
        v = "Yes" if v else "No"
    return f"{fmt(v)}{suffix}{cite(obj)}"


def technical(inner, summary="Technical details"):
    """A collapsed box for mechanics and code detail most readers can skip."""
    return f'<details class="note"><summary>{summary}</summary>{inner}</details>'


def bar(v, vmax):
    if not isinstance(v, (int, float)) or not vmax:
        return ""
    return f'<span class="bar" style="--v:{min(v / vmax, 1):.3f}"></span>'


# -------- Tables and infoboxes

def col_tip(label, tip):
    """A column header with a tooltip. The hook adds tips from column-tips.yml to headers without one."""
    return f'<span class="col-tip" title="{esc(tip)}">{label}</span>' if tip else label


def table(headers, rows, caption=None, cls=""):
    """headers: list of (label, is_numeric) or (label, is_numeric, tooltip).

    A row is a list of cells, a pre-rendered <tr> string, or (row_class, cells).
    """
    headers = [(h[0], h[1], h[2] if len(h) > 2 else None) for h in headers]
    th = "".join(f'<th class="num">{col_tip(h, t)}</th>' if num else f"<th>{col_tip(h, t)}</th>"
                 for h, num, t in headers)
    headers = [(h, num) for h, num, _ in headers]
    body = []
    for row in rows:
        if isinstance(row, str):  # pre-rendered row (e.g. group header)
            body.append(row)
            continue
        row_cls = ""
        if isinstance(row, tuple):
            row_cls, row = row
        tds = []
        for (h, num), cell in zip(headers, row):
            tds.append(f'<td class="num">{cell}</td>' if num else f"<td>{cell}</td>")
        attr = f' class="{row_cls}"' if row_cls else ""
        body.append(f"<tr{attr}>{''.join(tds)}</tr>")
    cap = f"<caption>{caption}</caption>" if caption else ""
    return (f'<div class="table-wrap"><table class="wikitable {cls}">{cap}'
            f"<thead><tr>{th}</tr></thead><tbody>{''.join(body)}</tbody></table></div>")


def infobox(title, rows, image="Image pending", cls=""):
    """rows: list of (label, html) or ("section", label)."""
    out = [f'<aside class="infobox {cls}"><div class="ib-title">{title}</div>']
    if image:
        out.append(f'<figure class="ib-image">{esc(image)}</figure>')
    out.append("<table>")
    for label, content in rows:
        if label == "section":
            out.append(f'<tr class="ib-section"><th colspan="2">{content}</th></tr>')
        else:
            out.append(f"<tr><th>{label}</th><td>{content}</td></tr>")
    out.append("</table></aside>")
    return "".join(out)


# -------- Column tooltips, from wiki/column-tips.yml

# What each column header means, for its tooltip, from wiki/column-tips.yml. Headers whose
# meaning depends on the table get their tip where the table is built
# (table(..., (label, numeric, tip))), or a page entry in the file.
COLUMN_TIPS_FILE = ROOT / "column-tips.yml"


def _column_tips():
    tips = yaml.safe_load(COLUMN_TIPS_FILE.read_text())
    pages = {(slug, header): tip for slug, by_header in (tips.get("pages") or {}).items()
             for header, tip in by_header.items()}
    return tips.get("columns") or {}, pages


COLUMN_TIPS, PAGE_COLUMN_TIPS = _column_tips()


def column_tip(slug, header):
    return PAGE_COLUMN_TIPS.get((slug, header)) or COLUMN_TIPS.get(header)


# -------- {{stat:DATASET:PATH}}, used on any page

@snippet("stat")
def stat(path):
    """{{stat:player:classes.recon.stats.run_speed}}: a single cited value from a dataset.

    The path is dotted keys into wiki/data/<dataset>.json. A list item is named by its
    `id` (or `name`), never by its position, so adding a record can't shift the path."""
    src, _, dotted = path.partition(":")
    node = data(src)
    if node is None:
        raise SnippetError(f"{{{{stat:{path}}}}}: there is no wiki/data/{src}.json")
    walked = []
    for part in dotted.split("."):
        if isinstance(node, list):
            if part.isdigit():
                ids = [str(x.get("id") or x.get("name")) for x in node if isinstance(x, dict)]
                raise SnippetError(f"{{{{stat:{path}}}}}: name the item in {'.'.join(walked)} by its id "
                                   f"instead of position {part} (one of: {', '.join(ids)})")
            node = next((x for x in node if isinstance(x, dict) and part in (x.get("id"), x.get("name"))), None)
        else:
            node = node.get(part) if isinstance(node, dict) else None
        walked.append(part)
        if node is None:
            raise SnippetError(f"{{{{stat:{path}}}}}: no {'.'.join(walked)} in wiki/data/{src}.json")
    if isinstance(node, dict) and "value" in node:
        v = node["value"]
        if isinstance(v, bool):
            v = "Yes" if v else "No"
        return f"{fmt(v) if not isinstance(v, dict) else esc(v)}{cite(node)}"
    return esc(node)
