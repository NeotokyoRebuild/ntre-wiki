"""Data-driven snippets for the NT;RE wiki (MkDocs).

expand(body, meta) replaces {{kind:arg:...}} placeholders in Markdown pages
with tables and infoboxes built from data/*.json. Snippets return HTML that
may contain [[slug|Label]] wiki links and [[src:path:line]] citations; the
wiki_hooks.py hook resolves those afterwards.

Weapon pages are Markdown files whose front matter names a weapon
(`weapon: weapon_zr68s`); their {{weapon:...}} snippets default to it.
"""

import json
import re
from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent  # wiki/
DATA = ROOT / "data"

# Loadout / display names -> page slugs. Content pages link to these slugs.
WEAPON_SLUGS = {
    "MPN45": "mpn45",
    "SRM": "srm",
    "SRM (silenced)": "srm-s",
    "Jitte": "jitte",
    "Jitte (with scope)": "jitte-s",
    "ZR68C": "zr68c",
    "ZR68-S (silenced)": "zr68-s",
    "ZR68-L (accurized)": "zr68-l",
    "Murata Supa-7": "supa-7",
    "Mosok": "mosok",
    "Mosok Silenced": "mosok-s",
    "MX": "mx",
    "MX Silenced": "mx-s",
    "AA13": "aa13",
    "SRS": "srs",
    "PZ252": "pz252",
    "SMAC": "vip#smac",
    "PBK56": "pbk56",
}

# The classes you can pick. VIP and Juggernaut are roles their game modes assign, covered on those pages.
CLASS_ORDER = ["recon", "assault", "support"]
CLASS_SLUGS = {"recon": "recon", "assault": "assault", "support": "support",
               "vip": "vip", "juggernaut": "juggernaut"}
VISION_NAMES = {"night_vision": "Night vision", "motion_vision": "Motion vision",
                "thermal_vision": "Thermal vision"}

# VIP and Juggernaut are work-in-progress modes. Stat lists keep them, but
# last, muted and tagged, so they don't compete with the core game.
WIP_CLASSES = {"vip", "juggernaut"}
WIP_MODES = {"vip", "jgr"}
WIP_WEAPONS = {"weapon_smac": "VIP weapon", "weapon_balc": "Juggernaut weapon"}
WIP_TAG = '<span class="tag wip" title="Work in progress">WIP</span>'


@lru_cache(maxsize=None)
def data(name):
    path = DATA / f"{name}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def cite(obj):
    """Citation markup for a {"value", "source"} record (or a raw source string)."""
    src = obj if isinstance(obj, str) else (obj or {}).get("source")
    if not src:
        return ""
    return f"[[src:{src}]]"


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


def weapon_link(name):
    slug = WEAPON_SLUGS.get(name)
    return f"[[{slug}|{esc(name)}]]" if slug else esc(name)


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


# ---------------------------------------------------------------- player

def player_class(cid):
    for c in data("player")["classes"]:
        if c["id"] == cid:
            return c
    raise KeyError(cid)


def class_link(cid):
    c = player_class(cid)
    return f"[[{CLASS_SLUGS[cid]}|{c['name']}]]"


def vision_of(c):
    v = c["vision"].get("value")
    if not v:
        return f'None{cite(c["vision"])}'
    return f'[[vision-modes#{v.replace("_", "-")}|{VISION_NAMES[v]}]]{cite(c["vision"])}'


def infobox_class(cid):
    c = player_class(cid)
    s = c["stats"]
    p = data("player")
    aux = p["aux_power"]["regen_per_sec"]
    cloak = s.get("cloak_capacity", {})
    rows = [
        ("section", "Survivability"),
        ("Health", val(s["max_health"], " HP")),
        ("Armour", "None"),
        ("section", "Movement (u/s)"),
        ("Run", val(s["run_speed"])),
        ("Sprint", val(s["sprint_speed"]) if s.get("can_sprint", {}).get("value") else f'Cannot sprint{cite(s.get("can_sprint"))}'),
        ("Walk / crouch", val(s["crouch_speed"])),
        ("Crouch-walk", val(s.get("crouch_walk_speed"))),
        ("Aiming", val(s.get("aim_speed"))),
        ("Jump height", val(s["jump_height"], " u")),
        ("section", "Abilities"),
        ("Vision mode", vision_of(c)),
        ("Thermoptic camo", f'{fmt(cloak["value"])} s{cite(cloak)}' if cloak.get("value") else "No"),
        ("AUX regen", f'{fmt(aux["value"].get(cid, 0))}/s{cite(aux)}'),
    ]
    items = c["default_items"]
    rows += [("section", "Spawns with"),
             ("Items", ", ".join(_item_name(i) for i in items["value"]) + cite(items))]
    return infobox(c["name"], rows, image=f"{c['name']} player model")


ITEM_NAMES = {
    "weapon_knife": "[[knife|Knife]]",
    "weapon_milso": "[[milso|MilSO]]",
    "weapon_tachi": "[[tachi|Tachi]]",
    "weapon_kyla": "[[kyla|Kyla]]",
    "weapon_grenade": "[[frag-grenade|Frag grenade]]",
    "weapon_smokegrenade": "[[smoke-grenade|Smoke grenade]]",
    "weapon_balc": "[[juggernaut#balc|BALC]]",
}


def _item_name(raw):
    if raw.startswith("weapon_remotedet"):
        return "[[detpack|Detpack]] (4+ XP)"
    return ITEM_NAMES.get(raw, esc(raw))


def table_classes():
    rows = []
    hp_max = 225
    for cid in CLASS_ORDER:
        c = player_class(cid)
        s = c["stats"]
        cloak = s.get("cloak_capacity", {}).get("value") or 0
        sprint = s["sprint_speed"]["value"] if s.get("can_sprint", {}).get("value") else None
        hp = s["max_health"]["value"]
        wip = cid in WIP_CLASSES
        cells = [
            class_link(cid) + (f" {WIP_TAG}" if wip else ""),
            f"{hp}{cite(s['max_health'])}{bar(hp, hp_max)}",
            val(s["run_speed"]),
            f"{sprint}{cite(s['sprint_speed'])}" if sprint else '<span class="na">—</span>',
            val(s["crouch_speed"]),
            val(s["jump_height"]),
            f"{fmt(cloak)} s" if cloak else '<span class="na">—</span>',
            vision_of(c),
        ]
        rows.append(("wip", cells) if wip else cells)
    return table(
        [("Class", False), ("Health", True), ("Run", True), ("Sprint", True),
         ("Crouch", True), ("Jump", True), ("Camo", True), ("Vision", False)],
        rows,
        caption="Speeds are in units per second, before the weapon in your hands slows you down.",
    )


def table_weapon_speed():
    p = data("player")
    values = p["movement"]["weapon_speed_scale"]["values"]
    rows = []
    wip_slugs = {WEAPONS[wid][0] for wid in WIP_WEAPONS}
    # Core weapons first, fastest to slowest; work-in-progress mode weapons last.
    for w in sorted(values, key=lambda w: -w["value"]):
        name = re.sub(r"\s*\(.*?\)", "", w["weapon"]).strip()
        slug = _slug_for_speed_name(w["weapon"])
        if slug in wip_slugs:
            continue
        label = f"[[{slug}|{esc(name)}]]" if slug else esc(name)
        wip = slug in wip_slugs
        cells = [
            label + (f" {WIP_TAG}" if wip else ""),
            f"×{w['value']:g}{cite(w)}{bar(w['value'], 1)}",
            f"{200 * w['value']:g}",
            f"{160 * w['value']:g}",
        ]
        rows.append(("wip", cells) if wip else cells)
    return table(
        [("Weapon in hand", False), ("Speed scale", True), ("Recon run", True), ("Assault/Support run", True)],
        rows,
        caption="Your run speed is your class's run speed times the scale of the weapon you're holding.",
    )


SPEED_NAME_SLUGS = {
    "BALC": "juggernaut#balc", "Knife": "knife", "Milso": "milso", "Tachi": "tachi", "Kyla": "kyla",
    "Grenade": "frag-grenade", "Smoke grenade": "smoke-grenade", "Detpack": "detpack",
    "Ghost": "ghost", "MPN45 (silenced": "mpn45", "MPN45 Unsilenced": "mpn45",
    "SRM (silenced)": "srm-s", "SRM": "srm", "Jitte (with scope)": "jitte-s", "Jitte": "jitte",
    "SMAC": "vip#smac", "ZR68C": "zr68c", "PBK56": "pbk56", "ZR68-S": "zr68-s", "ZR68-L": "zr68-l",
    "MX Silenced": "mx-s", "MX": "mx", "Mosok scoped": "mosok-l", "Mosok silenced": "mosok-s",
    "Mosok": "mosok", "AA13": "aa13", "SRS": "srs", "Murata Supa-7": "supa-7", "PZ252": "pz252",
}


def _slug_for_speed_name(name):
    for prefix, slug in SPEED_NAME_SLUGS.items():
        if name.startswith(prefix):
            return slug
    return None


def table_ranks():
    p = data("player")
    rows = []
    for r in p["ranks"]:
        lo = r["xp_min"]
        hi = r["xp_max_exclusive"]
        if lo is None:
            rng = f"below {hi}"
        elif hi is None:
            rng = f"{lo}+"
        else:
            rng = f"{lo}–{hi - 1}"
        rows.append([f"<b>{esc(r['name'])}</b>", esc(r["short"]), f"{rng}{cite(r)}"])
    return table([("Rank", False, "The rank's name"), ("Short", False, "Its short form, as shown in game"),
                  ("XP", True, "The XP that puts you at this rank")], rows)


def table_loadout_matrix():
    """Weapons × classes matrix of XP unlock thresholds."""
    p = data("player")["rank_loadouts"]
    classes = CLASS_ORDER
    order = []
    for cid in classes:
        for e in p[cid]:
            if e["weapon"] not in order:
                order.append(e["weapon"])
    rank_name = {0: "Pvt", 4: "Cpl", 10: "Sgt", 20: "Lt", "any": "Any"}
    rows = []
    for w in order:
        row = [weapon_link(w)]
        for cid in classes:
            hit = next((e for e in p[cid] if e["weapon"] == w), None)
            if hit is None:
                cell = '<span class="na">—</span>'
            else:
                xp = hit["min_xp"]
                label = rank_name.get(xp, xp)
                cell = f'<span class="tag {cid}">{label}</span> {xp if xp != "any" else ""}'
            row.append(f'<span class="wip-cell">{cell}</span>' if cid in WIP_CLASSES else cell)
        # A weapon only the VIP can pick is muted along with the VIP column.
        rows.append(row)
    hdr = [("Weapon", False)] + [
        (f"{class_link(c)}{cite(p[c + '_source'])}", False, f"The rank, and XP, at which {c.capitalize()} unlocks it")
        for c in classes]
    return table(hdr, rows, caption="Each cell shows the rank, and the XP, at which that class unlocks the weapon. "
                                    "“Any” means it's available even with negative XP.")


def table_loadout(cid):
    p = data("player")["rank_loadouts"]
    rows = []
    for e in p[cid]:
        xp = e["min_xp"]
        rows.append([weapon_link(e["weapon"]), "Any (even negative)" if xp == "any" else f"{xp}"])
    return table([("Primary weapon", False), (f"Min. XP{cite(p[cid + '_source'])}", True)], rows)


def table_xp():
    x = data("player")["xp_rules"]
    labels = [
        ("enemy_kill", "Kill an enemy"),
        ("kill_assist", "Kill assist"),
        ("team_kill", "Kill a teammate"),
        ("suicide_or_environment_death", "Suicide / environmental death"),
        ("round_win", "Team wins the round"),
        ("ghost_capture_or_vip_escape", "Ghost capture"),
        ("ctg_vip_win_without_capture", "Win without capture (CTG)"),
        ("team_kill_assist", "Team-kill assist"),
    ]
    rows = []
    for key, label in labels:
        r = x[key]
        v = r["value"]
        if isinstance(v, int):
            v = f"{v:+d}"
        note = without_wip(r.get("note", "")) or ""
        rows.append([label, f"<b>{esc(v)}</b>{cite(r)}", esc(note)])
    return table([("Event", False), ("XP", False), ("Notes", False)], rows)


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


def cloak_classes():
    return [player_class(cid) for cid in data("player")["cloak"]["classes"]["value"]]


def infobox_cloak():
    cloak = data("player")["cloak"]
    rows = [("Classes", ", ".join(class_link(c["id"]) for c in cloak_classes()) + cite(cloak["classes"])),
            ("section", "Battery")]
    for c in cloak_classes():
        s = c["stats"]
        rows.append((c["name"], f"{val(s['cloak_capacity'], ' s')}, +{val(s['cloak_regen_per_sec'], '/s')}"))
    full = cloak["full_recharge_time_sec"]
    rows += [("Drain", val(cloak["drain_per_sec"], " /s")),
             ("Min. to activate", val(cloak["min_power_to_activate"])),
             ("Full recharge", " / ".join(f"{fmt(full['value'][c['id']])} s" for c in cloak_classes()) + cite(full)),
             ("Refills on spawn", val(cloak["refill_on_spawn"]))]
    return infobox("Thermoptic camo", rows, image="Cloak effect screenshot")


def table_cloak():
    """Cloak battery by class: capacity, how long it lasts, and how fast it comes back."""
    cloak = data("player")["cloak"]
    drain = cloak["drain_per_sec"]["value"]
    rows = []
    for c in cloak_classes():
        s = c["stats"]
        cap, regen = s["cloak_capacity"]["value"], s["cloak_regen_per_sec"]["value"]
        rows.append([class_link(c["id"]), val(s["cloak_capacity"]), f"{fmt(cap / drain)} s",
                     val(s["cloak_regen_per_sec"]), f"{fmt(round(cap / regen, 1))} s"])
    return table([("Class", False), ("Capacity", True), ("Max duration", True), ("Recharge /s", True),
                  ("Empty → full", True)], rows,
                 caption=f"Max duration is capacity ÷ the drain of {fmt(drain)} per second;{cite(cloak['drain_per_sec'])} "
                         "empty to full is capacity ÷ the recharge rate.")


def infobox_aux():
    aux = data("player")["aux_power"]
    return infobox("AUX power", [
        ("Maximum", val(aux["max"])),
        ("Sprint drain", val(aux["sprint_drain_per_sec"], " /s")),
        ("Min. to sprint", val(aux["sprint_start_minimum"])),
        ("Sprint-stop cost", val(aux["sprint_stop_penalty"])),
        ("Regen delay", val(aux["regen_delay_sec"], " s")),
        ("Super jump", val(aux["super_jump_cost"])),
    ], image=None)


def table_aux_regen():
    """AUX regeneration and sprint drain by class."""
    aux = data("player")["aux_power"]
    na = '<span class="na">—</span>'
    full = aux["max"]["value"]
    rows = []
    for cid in CLASS_ORDER:
        s = player_class(cid)["stats"]
        regen = val(s["aux_regen_per_sec"])
        if not s["can_sprint"]["value"]:
            rows.append([class_link(cid), regen, na, na, f"Cannot sprint{cite(s['can_sprint'])}"])
            continue
        drain = s["aux_sprint_drain_per_sec"]
        while_sprinting = aux["regen_per_sec"]["value"][f"{cid}_while_sprinting"]
        rows.append([class_link(cid), regen, f"{fmt(while_sprinting)}{cite(aux['regen_per_sec'])}", val(drain),
                     f"{fmt(full / drain['value'])} s" if drain["value"] else "Unlimited"])
    return table([("Class", False), ("Regen /s", True), ("While sprinting", True), ("Sprint drain /s", True),
                  ("Sprint time (full bar)", True)], rows,
                 caption=f"Sprint time is a full bar of {fmt(full)} divided by the drain rate.")


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


# ---------------------------------------------------------------- weapons

# Script id -> (page slug, display name). Order is the order used in hub tables.
WEAPONS = {
    "weapon_mpn": ("mpn45", "MPN45"),
    "weapon_mpn_unsilenced": ("mpn45-unsilenced", "MPN45 (unsilenced)"),
    "weapon_srm": ("srm", "SRM"),
    "weapon_srm_s": ("srm-s", "SRM-S"),
    "weapon_jitte": ("jitte", "Jitte"),
    "weapon_jittescoped": ("jitte-s", "Jitte-S"),
    "weapon_smac": ("vip#smac", "SMAC"),
    "weapon_zr68c": ("zr68c", "ZR68C"),
    "weapon_zr68s": ("zr68-s", "ZR68-S"),
    "weapon_mx": ("mx", "MX"),
    "weapon_mx_silenced": ("mx-s", "MX-S"),
    "weapon_m41": ("mosok", "Mosok"),
    "weapon_m41s": ("mosok-s", "Mosok-S"),
    "weapon_m41l": ("mosok-l", "Mosok-L"),
    "weapon_zr68l": ("zr68-l", "ZR68-L"),
    "weapon_srs": ("srs", "SRS"),
    "weapon_supa7": ("supa-7", "Murata Supa-7"),
    "weapon_aa13": ("aa13", "AA13"),
    "weapon_pz": ("pz252", "PZ252"),
    "weapon_pbk56s": ("pbk56", "PBK56S"),
    "weapon_balc": ("juggernaut#balc", "BALC"),
    "weapon_milso": ("milso", "MilSO"),
    "weapon_tachi": ("tachi", "Tachi"),
    "weapon_kyla": ("kyla", "Kyla"),
    "weapon_knife": ("knife", "Knife"),
    "weapon_grenade": ("frag-grenade", "Frag grenade"),
    "weapon_smokegrenade": ("smoke-grenade", "Smoke grenade"),
    "weapon_remotedet": ("detpack", "Detpack"),
    "weapon_ghost": ("ghost", "Ghost"),
}

CATEGORY_LABELS = [
    ("SMG", "Submachine guns"),
    ("rifle", "Rifles"),
    ("sniper", "Marksman & sniper rifles"),
    ("shotgun", "Shotguns"),
    ("MG", "Machine guns"),
    ("pistol", "Sidearms"),
    ("melee", "Melee"),
    ("grenade", "Grenades"),
    ("explosive", "Explosives"),
    ("special", "Objective items"),
]
CATEGORY_SINGULAR = {
    "SMG": "submachine gun", "rifle": "rifle", "sniper": "marksman rifle", "shotgun": "shotgun",
    "MG": "machine gun", "pistol": "sidearm", "melee": "melee weapon", "grenade": "grenade",
    "explosive": "explosive", "special": "objective item",
}

HITGROUPS = [("head", "Head"), ("chest", "Chest"), ("stomach", "Stomach"), ("arms", "Arms"), ("legs", "Legs")]
# (class id, name, max health) for the classes damage tables are worked out against.
TARGETS = [(cid, player_class(cid)["name"], player_class(cid)["stats"]["max_health"]["value"]) for cid in CLASS_ORDER]

SUPPRESSED_NOTE_PREFIX = "Suppressed (NEO_WEP_SUPPRESSED"
PATH_RE = re.compile(r"((?:src|game)/[\w/.\-]+\.\w+:\d+(?:-\d+)?(?:,\s?\d+(?:-\d+)?)*)")


def weapons():
    return data("weapons")["weapons"]


def weapon(wid):
    return next(w for w in weapons() if w["id"] == wid)


def wlink(wid):
    slug, name = WEAPONS[wid]
    return f"[[{slug}|{esc(name)}]]"


def sval(w, key):
    rec = w["stats"].get(key)
    return rec.get("value") if isinstance(rec, dict) else None


def cite_text(text):
    """Turn inline 'path:line' references in agent notes into citations."""
    text = esc(text)
    text = PATH_RE.sub(lambda m: f"[[src:{m.group(1)}]]", text)
    # Drop parentheses left holding only citations/commas.
    text = re.sub(r"\(\s*((?:\[\[src:[^\]]+\]\][\s,;]*)+)\)", lambda m: re.sub(r"[\s,;]+", "", m.group(1)), text)
    return text


def per_shot_damage(w):
    d = sval(w, "effective_damage_body")
    if d is None:
        return None
    return d * (sval(w, "pellets") or 1)


def shots_to_kill(dmg, hp):
    if not dmg:
        return None
    n = 1
    while n * dmg < hp:
        n += 1
    return n


def hitmult():
    hg = data("weapons")["damage_model"]["hitgroup_multipliers"]
    return {k: hg[k]["value"] for k, _ in HITGROUPS}


def is_gun(w):
    return sval(w, "effective_damage_body") is not None and w["category"]["value"] not in ("melee", "special")


def pickup_text(w):
    text = re.sub(r"\s*\(no CanBePickedUpByClass override\)", "", w["pickup_classes"]["value"])
    return without_wip(text) or text


def classes_text(w):
    return esc(pickup_text(w)) + cite(w["pickup_classes"])


def cycle_time(w):
    return sval(w, "cycle_time_s")


def dps(w):
    """Damage per second to the body: per-shot damage ÷ cycle time (a ceiling for semi-auto)."""
    dmg, ct = per_shot_damage(w), cycle_time(w)
    return dmg / ct if dmg and ct else None


def hit_tiers():
    """Hit locations grouped by equal multiplier, in order: [(mult, [label, ...], [key, ...]), ...]."""
    mult = hitmult()
    tiers = []
    for key, label in HITGROUPS:
        if tiers and tiers[-1][0] == mult[key]:
            tiers[-1][1].append(label)
            tiers[-1][2].append(key)
        else:
            tiers.append((mult[key], [label], [key]))
    return tiers


def tier_label(labels):
    return " / ".join([labels[0]] + [l.lower() for l in labels[1:]])


def stat_strip(cells):
    """One-row table of headline stats: cells is [(label, html, is_numeric), ...]."""
    return table([(label, num) for label, _, num in cells], [[c for _, c, _ in cells]], cls="stat-strip")


def weapon_stats(w):
    """General stats: the headline numbers for any weapon type."""
    s = w["stats"]
    cat = w["category"]["value"]
    move = ("Move speed", f"×{fmt(s['movement_speed_scale']['value'])}{cite(s['movement_speed_scale'])}", True)
    if is_gun(w):
        pellets = sval(w, "pellets")
        clip = s["clip_size"]["value"]
        cells = [
            ("Damage", f"{fmt(round(sval(w, 'effective_damage_body'), 2))}{cite(s['effective_damage_body'])}"
                       + (f" ×{pellets}" if pellets else ""), True),
            ("Cycle time", f"{cycle_time(w):.3g} s{cite(s['cycle_time_s'])}", True),
            ("RPM", f"{s['rpm']['value']}{cite(s['rpm'])}", True),
            ("DPS", f"{round(dps(w))}", True),
            ("Magazine", "Heat" if clip == -1 else val(s["clip_size"]), True),
            ("Penetration", val(s.get("penetration")), True),
            move,
        ]
        cap = ("Damage is per " + ("pellet" if pellets else "bullet") + " to the head or chest, with the ×1.485 "
               "modifier applied. DPS is damage" + (" × pellets" if pellets else "") + " ÷ cycle time: the most it "
               "can do" + (", which you only reach by firing as fast as the gun allows." if not any(
                   m.startswith("auto") for m in s["fire_modes"]["value"]) else ", with every shot landing."))
        out = stat_strip(cells)
        return out.replace("</table>", f"<caption>{cap}</caption></table>", 1)
    if cat in ("grenade", "explosive"):
        cells = []
        if "blast_damage_effective" in s:
            cells += [("Blast damage", f"{fmt(s['blast_damage_effective']['value'])}{cite(s['blast_damage_effective'])}", True),
                      ("Radius", val(s["blast_radius"], " u"), True)]
        if "fuse_s" in s:
            cells.append(("Fuse", val(s["fuse_s"], " s"), True))
        if "smoke_duration_s" in s:
            cells.append(("Smoke lasts", val(s["smoke_duration_s"], " s"), True))
        cells += [("Carried", val(s.get("count")), True), move]
        return stat_strip(cells)
    if cat == "melee":
        return stat_strip([
            ("Slash", val(s["damage"]), True),
            ("Backstab", val(s["backstab_damage"]), True),
            ("Range", val(s["range"], " u"), True),
            ("Swing rate", f"{s['rpm']['value']} /min{cite(s['rpm'])}", True),
            move,
        ])
    return ""


def weapon_damage(w):
    """Damage by hit location, with prose on how the multipliers apply."""
    eff = sval(w, "effective_damage_body")
    pellets = sval(w, "pellets") or 1
    mult = hitmult()
    hg_src = data("weapons")["damage_model"]["hitgroup_multipliers"]
    rows = [[f"{label}{cite(hg_src[key])}", f"×{fmt(mult[key])}", f"{fmt(round(eff * mult[key], 2))}"]
            for key, label in HITGROUPS]
    unit = "pellet" if pellets > 1 else "bullet"
    out = [f"<p>Each {unit} does <b>{fmt(round(eff, 2))}</b> damage to the head or chest, and less to the "
           "stomach, arms and legs. Damage doesn't drop off with distance.</p>"]
    out.append(table([("Hit location", False), ("Multiplier", True),
                      ("Damage" + (" / pellet" if pellets > 1 else ""), True,
                       f"Damage per {unit} that lands on this part of the body")], rows))
    pen = sval(w, "penetration")
    if pen:
        out.append(f"<p>Its penetration is <b>{fmt(pen)}</b>.{cite(w['stats']['penetration'])} "
                   "See [[damage#penetration|how penetration works]] for what that gets through.</p>")
    elif pen == 0:
        out.append("<p>Pellets never pass through walls or other surfaces.</p>")
    out.append(technical(
        f"<p>Damage is the weapon's base damage of {sval(w, 'damage')}, × the global bullet modifier of 1.485 "
        f"(<code>sv_neo_wep_dmg_modifier</code>){cite(data('weapons')['damage_model']['damage_formula']['global_bullet_damage_modifier'])}, "
        "× the hit-location multiplier.</p>"))
    return "".join(out)


def _per_class_table(w, cell, caption):
    """Rows = selectable classes, columns = hit-location tiers; cell(dmg_per_shot, hp) -> html."""
    dmg = per_shot_damage(w)
    tiers = hit_tiers()
    rows = []
    for cid, _, hp in TARGETS:
        rows.append([f"{class_link(cid)} ({hp} HP)"] + [cell(dmg * m, hp) for m, _, _ in tiers])
    hdr = [("Class", False, "The target's class and its maximum health")] + [
        (f"{tier_label(labels)} ×{fmt(m)}", True, f"Every hit lands on the {tier_label(labels).lower()}, "
                                                   f"which take ×{fmt(m)} damage") for m, labels, _ in tiers]
    return table(hdr, rows, caption=caption)


def weapon_stk(w):
    pellets = sval(w, "pellets")
    clip = sval(w, "clip_size")
    over = []

    def cell(d, hp):
        n = shots_to_kill(d, hp)
        if clip and clip > 0 and n > clip:
            over.append(n)
            return f"{n}†"
        return str(n)

    t = _per_class_table(w, cell, "")
    cap = "Hits needed from full health" + (", assuming every pellet hits." if pellets else ".")
    if over:
        cap += f" † More than one magazine ({clip})."
    return t.replace("<caption></caption>", "").replace("</table>", f"<caption>{cap}</caption></table>", 1)


def weapon_ttk(w):
    ct = cycle_time(w)
    auto = any(m.startswith("auto") for m in w["stats"]["fire_modes"]["value"])

    def cell(d, hp):
        n = shots_to_kill(d, hp)
        return f"{(n - 1) * ct:.2f} s"

    cap = ("Time from your first hit to your last, with every shot landing and no reload: (shots to kill − 1) "
           "× cycle time." + ("" if auto else " You only reach it by firing as fast as the gun allows."))
    return _per_class_table(w, cell, cap)


def weapon_handling(w):
    return handling_section(w)


def weapon_availability(w):
    return availability_section(w)


def weapon_special(w, key):
    return special_block(w, key)


def weapon_suppressor(w):
    return ("<p>No muzzle flash, and firing it doesn't make your [[thermoptic-camouflage|cloak]] flash. "
            "Bots also have a harder time hearing it."
            "[[src:src/game/shared/neo/weapons/weapon_neobasecombatweapon.cpp:1011-1020]]</p>")


def weapon_notes(w):
    """The extraction notes for a weapon: technical by nature, so collapsed."""
    notes = technical_notes(w)
    if not notes:
        return ""
    return technical("<ul>" + "".join(f"<li>{cite_text(n)}</li>" for n in notes) + "</ul>", "Technical notes")


def weapon_explosive(w):
    return explosive_section(w)


def weapon_attacks(w):
    return knife_section(w)


def handling_section(w):
    h = w.get("handling")
    if not h:
        return ""
    sp = h["spread"]
    rows = [
        ["Hip fire", f"{fmt(sp['hip_min']['cone_degrees'])}°", f"{fmt(sp['hip_max']['cone_degrees'])}°"],
        ["Aimed", f"{fmt(sp['aim_min']['cone_degrees'])}°", f"{fmt(sp['aim_max']['cone_degrees'])}°"],
    ]
    out = [f"<p>Your shots spread out as you keep firing, move or jump, and tighten again when you stop. "
           f"Aiming keeps them tighter.{cite(h)} See [[damage#accuracy|accuracy]] for how fast it changes.</p>"]
    out.append(table([("Spread", False), ("Min cone", True), ("Max cone", True)], rows))
    kick = h.get("view_kick", {})
    rec = h.get("view_recoil", {})
    notes = []
    if any(kick.get(k) for k in ("minX", "maxX", "minY", "maxY")):
        notes.append(f"View kick per shot: pitch {fmt(kick['minX'])}–{fmt(kick['maxX'])} degrees, "
                     f"yaw {fmt(kick['minY'])}–{fmt(kick['maxY'])} degrees.")
    if rec.get("hipFactor") or rec.get("adsFactor"):
        notes.append(f"Camera recoil: pitch {fmt(rec['minX'])} to {fmt(rec['maxX'])}, yaw {fmt(rec['minY'])} to {fmt(rec['maxY'])}, "
                     f"scaled ×{fmt(rec['hipFactor'])} from the hip and ×{fmt(rec['adsFactor'])} aimed.")
    if w["stats"].get("aim_fov"):
        notes.append(f"Aimed field of view: {val(w['stats']['aim_fov'], ' degrees')} (lower is more zoom).")
    if notes:
        out.append(technical("<ul>" + "".join(f"<li>{n}</li>" for n in notes) + "</ul>"))
    return "".join(out)


def availability_section(w):
    out = []
    lo = [e for e in (w.get("loadout") or []) if e["class"].lower() not in WIP_CLASSES]
    if lo:
        rows = []
        for e in sorted(lo, key=lambda e: e["class"].lower() in WIP_CLASSES):
            cid = e["class"].lower()
            xp = e["min_xp"]
            wip = cid in WIP_CLASSES
            cells = [class_link(cid) + (f" {WIP_TAG}" if wip else ""), esc(e["rank"]),
                     f"{'Any' if xp in (-255, 'any', None) else xp}{cite(e)}"]
            rows.append(("wip", cells) if wip else cells)
        out.append(table([("Class", False, "A class that can pick it"),
                          ("Rank", False, "The rank at which that class unlocks it"),
                          ("Min. XP", True, "The XP you need to pick it")], rows))
    defaults = [d for d in (w.get("class_default_for") or w.get("special", {}).get("class_default_for") or [])
                if d["value"].lower() not in WIP_CLASSES]
    if defaults:
        out.append("<p>Spawns with: " + ", ".join(
            f"{class_link(d['value'].lower())}{cite(d)}" + (f" ({esc(d['note'].split(' (')[0])})" if d.get("note") else "")
            for d in defaults) + ".</p>")
    if not lo and not defaults:
        out.append("<p>Not part of any class loadout.</p>")
    out.append(f"<p>Can be picked up by: {classes_text(w)}.</p>")
    return "".join(out)


SPECIAL_TITLES = {"bolt_action": "Bolt action", "slug": "Slug rounds", "reload": "Reloading",
                  "heat_system": "Heat system", "charge_shot": "Charged grenade",
                  "firemode_switch_delay_s": "Fire-mode switch"}


def special_keys(w):
    return [k for k in (w.get("special") or {}) if k != "class_default_for"]


def special_title(key):
    return SPECIAL_TITLES.get(key, key.replace("_", " ").capitalize())


def _field(block, name):
    rec = block.get(name)
    return rec if isinstance(rec, dict) and "value" in rec else None


def _num(block, name, unit=None):
    """A cited number from a special block, with its unit spelled out for prose."""
    rec = _field(block, name)
    if rec is None:
        return None
    text = plural(rec["value"], unit) if unit else fmt(rec["value"])
    return f"{text}{cite(rec)}"


def special_lead(w, key, block):
    """Plain-language opening for a weapon-specific section, built only from the block's own cited fields."""
    n = lambda name, unit=None: _num(block, name, unit)
    if key == "bolt_action":
        aim = _field(block, "cannot_aim_while_bolting")
        return ("You work the bolt after every shot, and can't fire again until it's done"
                + (f", or aim while you do it.{cite(aim)}" if aim and aim["value"] else "."))
    if key == "slug" and n("slug_damage_multiplier"):
        pellets = sval(w, "pellets")
        return ("Use the secondary attack to load a slug. Your next shot fires a single slug"
                + (f" instead of {pellets} pellets" if pellets else "")
                + f". It hits {n('slug_damage_multiplier')} times as hard as one pellet and goes through more.")
    if key == "reload" and n("shell_insert_interval_s"):
        return f"Shells load one at a time, one every {n('shell_insert_interval_s', 'second')}."
    if key == "heat_system" and n("capacity"):
        return (f"There's no magazine. Each shot uses up part of a {n('capacity')}-shot heat reserve, which refills "
                "by itself while the gun isn't overheated. Run it dry and the gun overheats, locking up for "
                f"{n('overheat_lockout_s', 'second')}.")
    if key == "charge_shot" and n("charge_time_s"):
        return (f"In its alternate fire mode, hold fire for {n('charge_time_s', 'second')} to charge it, "
                "then fire a bouncing grenade that does blast damage.")
    return None


def _code_like(v):
    return isinstance(v, str) and (any(c in v for c in "()[]=<>_") or v.isupper())


def special_block(w, key):
    block = w["special"][key]
    title = special_title(key)
    if isinstance(block, dict) and "value" in block and "description" not in block:
        if key == "firemode_switch_delay_s":
            return f"<p>Switching fire mode takes {plural(block['value'], 'second')}.{cite(block)}</p>"
        return f"<p>{esc(title)}: {plural(block['value'], 'second')}{cite(block)}.</p>"
    out, hidden = [], []
    lead = special_lead(w, key, block)
    if lead:
        out.append(f"<p>{lead}</p>")
    if block.get("description"):
        hidden.append(f"<p>{cite_text(block['description'])}</p>")
    rows, code_rows = [], []
    for k, v in block.items():
        if isinstance(v, dict) and "value" in v:
            label = k.replace("_s", " (s)").replace("_", " ").strip().capitalize()
            value = "Yes" if v["value"] is True else "No" if v["value"] is False else v["value"]
            cell = [esc(label), f"{esc(fmt(value))}{cite(v)}"]
            (code_rows if _code_like(value) else rows).append(cell)
    if rows:
        out.append(table([("Property", False), ("Value", False)], rows))
    if code_rows:
        hidden.append(table([("Property", False), ("Value", False)], code_rows))
    if hidden:
        out.append(technical("".join(hidden)))
    return "".join(out)


def technical_notes(w):
    notes = [without_wip(n) for n in w.get("notes", []) if isinstance(n, str) and not n.startswith(SUPPRESSED_NOTE_PREFIX)]
    return [n for n in notes if n]


def explosive_section(w):
    s = w["stats"]
    out = []
    if "blast_damage_effective" in s:
        base = s["blast_damage_base"]["value"]
        eff = s["blast_damage_effective"]["value"]
        r = s["blast_radius"]["value"]
        out.append(f"<p>Base damage {fmt(base)}{cite(s['blast_damage_base'])} × the explosive modifier 1.485 = <b>{fmt(eff)}</b> at the centre, "
                   f"falling linearly to 0 at {fmt(r)} units.{cite(s.get('falloff'))}</p>")
        rows = []
        for frac in (0, 0.25, 0.5, 0.75, 0.9):
            d = eff * (1 - frac)
            rows.append([f"{fmt(round(r * frac))} u", f"{round(d)}",
                         *("Kill" if d >= hp else f"{round(d)}/{hp}" for _, _, hp in TARGETS)])
        out.append(table([("Distance", True), ("Damage", True, "Damage at this distance from the centre")]
                         + [(class_link(c), True, f"Damage to a full-health {c.capitalize()}, or Kill")
                            for c, _, _ in TARGETS], rows,
                         caption="Damage by distance from the blast, ignoring cover."))
    if "smoke_duration_s" in s:
        out.append(f"<p>Pops after {plural(s['fuse_s']['value'], 'second')}{cite(s['fuse_s'])} and lasts "
                   f"{plural(s['smoke_duration_s']['value'], 'second')}, starting to thin at "
                   f"{plural(s['smoke_fade_start_end_s']['value'][0], 'second')}.{cite(s['smoke_fade_start_end_s'])} "
                   f"A {fmt(s['los_blocker_size']['value'])}-unit line-of-sight blocker for bots appears after "
                   f"{plural(s['los_blocker_delay_s']['value'], 'second')}.{cite(s['los_blocker_size'])} [[support|Support]] thermal vision sees through it.</p>")
    if "max_throw_speed" in s:
        out.append(f"<p>Maximum throw speed: {fmt(s['max_throw_speed']['value'])} units per second.{cite(s['max_throw_speed'])}</p>")
    if "trigger" in s:
        out.append(f"<p>Detonation: {esc(s['trigger']['value'])}.{cite(s['trigger'])} Damage does not set it off.{cite(s.get('detonated_by_damage'))}</p>")
    return "".join(out)


def knife_section(w):
    s = w["stats"]
    toughest = player_class("support")
    return (f"<p>A slash deals {fmt(s['damage']['value'])} damage{cite(s['damage'])} at up to {fmt(s['range']['value'])} units. "
            f"A <b>backstab</b> deals {s['backstab_damage']['value']}{cite(s['backstab_damage'])}: more than "
            f"[[support|Support]]'s {toughest['stats']['max_health']['value']} HP,{cite(toughest['stats']['max_health'])} "
            "so it kills any selectable class outright. The global damage modifier does not apply to the knife.</p>")


def loadout_letters(w):
    """R4 A10 S20: which selectable classes can pick the weapon and the XP each needs.

    A letter alone means no XP is needed (any rank, or the class spawns with it). Missing
    classes show a faint dot, so the slots line up down a column. Each slot has a tooltip."""
    lo = {e["class"].lower(): e for e in (w.get("loadout") or [])}
    spawn = {d["value"].lower() for d in (w.get("class_default_for") or w.get("special", {}).get("class_default_for") or [])}
    out = []
    for cid in CLASS_ORDER:
        name = cid.capitalize()
        if cid in lo:
            e = lo[cid]
            xp = e["min_xp"]
            if xp in (-255, "any", None):
                out.append(f'<span class="cls" title="{name}: any rank">{name[0]}</span>')
            else:
                out.append(f'<span class="cls" title="{name}: from {esc(e["rank"])} ({xp} XP)">{name[0]}{xp}</span>')
        elif cid in spawn:
            out.append(f'<span class="cls" title="{name}: spawns with it">{name[0]}</span>')
        else:
            out.append(f'<span class="cls none" title="Not in {name}\'s loadout">·</span>')
    return f'<span class="cls-letters">{"".join(out)}</span>'


def table_weapons(only=None):
    """Comparison of every gun, or with `only` (a category id such as "rifle") just that category."""
    rows = []
    max_dps = 0
    entries = []
    for wid in WEAPONS:
        w = weapon(wid)
        if not is_gun(w):
            continue
        if wid in WIP_WEAPONS:
            continue
        dmg = per_shot_damage(w)
        d = dps(w)
        max_dps = max(max_dps, d)
        if only and w["category"]["value"] != only:
            continue
        entries.append((w, dmg, d))
    # Core categories first; weapons that belong to work-in-progress modes get their own group last.
    groups = [(label, [e for e in entries if e[0]["category"]["value"] == cat and e[0]["id"] not in WIP_WEAPONS])
              for cat, label in CATEGORY_LABELS]
    for label, group in groups:
        if not group:
            continue
        if not only:
            rows.append(f'<tr class="group"><th colspan="9">{label}</th></tr>')
        for w, dmg, wdps in group:
            s = w["stats"]
            clip = s["clip_size"]["value"]
            traits = []
            if w["flags"].get("suppressed"):
                traits.append('<span class="tag">S</span>')
            if w["flags"].get("scoped"):
                traits.append('<span class="tag">Scope</span>')
            if w["id"] in WIP_WEAPONS:
                traits.append(WIP_TAG)
            pel = f" ×{s['pellets']['value']}" if "pellets" in s else ""
            cells = [
                wlink(w["id"]) + " " + "".join(traits),
                f"{fmt(round(sval(w, 'effective_damage_body') ,1))}{pel}",
                f"{s['rpm']['value']}",
                f"{round(wdps)}",
                fmt(sval(w, "penetration")),
                "heat" if clip == -1 else str(clip),
                f"{shots_to_kill(dmg, 100)} / {shots_to_kill(dmg, 120)} / {shots_to_kill(dmg, 225)}",
                f"×{fmt(sval(w, 'movement_speed_scale'))}",
                loadout_letters(w),
            ]
            rows.append(("wip", cells) if w["id"] in WIP_WEAPONS else cells)
    # second pass to fill bars now that max_dps is known
    out = []
    for r in rows:
        cells = r[1] if isinstance(r, tuple) else r
        if isinstance(cells, list):
            v = int(cells[3])
            cells[3] = f"{v}{bar(v, max_dps)}"
        out.append(r)
    return table(
        [("Weapon", False), ("Damage", True), ("RPM", True), ("DPS", True), ("Pen.", True),
         ("Mag", True), ("STK", True), ("Speed", True),
         ("Classes", True, "Which classes can pick it, and the XP each needs: R Recon, A Assault, S Support. "
                            "R4 means Recon from 4 XP; a letter alone means no XP needed.")],
        out,
        cls="compare",
        caption="Damage is per bullet to the body, with the ×1.485 modifier applied. DPS is damage ÷ cycle time: "
                "the most a gun can do, which semi-automatic guns only reach if you fire at their cap. The bars "
                "compare each gun with the highest DPS. STK is chest shots to kill Recon / Assault / Support. "
                "Each weapon's page cites its numbers.",
    )


def table_stk():
    mult = hitmult()
    rows = []
    for wid in WEAPONS:
        w = weapon(wid)
        if not is_gun(w) or wid in WIP_WEAPONS:
            continue
        dmg = per_shot_damage(w)
        wip = wid in WIP_WEAPONS
        row = [wlink(wid) + (f" {WIP_TAG}" if wip else "")]
        for _, _, hp in TARGETS:
            row.append(f"{shots_to_kill(dmg, hp)} / {shots_to_kill(dmg * mult['legs'], hp)}")
        rows.append(("wip", row) if wip else row)
    return table([("Weapon", False)] + [(f"vs {class_link(c)} ({hp} HP)", True,
                                         f"Hits to kill a full-health {c.capitalize()}: head or chest / legs")
                                        for c, _, hp in TARGETS], rows,
                 caption="Hits to kill: to the head or chest / to the legs. Shotguns assume every pellet hits.")


def table_explosives():
    """Blast damage and radius for everything that explodes, from the weapon records."""
    rows = []
    for wid in ("weapon_grenade", "weapon_remotedet"):
        st = weapon(wid)["stats"]
        rows.append([wlink(wid),
                     f"{fmt(st['blast_damage_effective']['value'])} (base {fmt(st['blast_damage_base']['value'])})"
                     f"{cite(st['blast_damage_effective'])}",
                     f"{fmt(st['blast_radius']['value'])} u{cite(st['blast_radius'])}"])
    return table([("Explosive", False), ("Damage", True, "Damage at the centre of the blast; in brackets, the base damage before the ×1.485 modifier"),
                  ("Radius", True)], rows,
                 caption="Damage includes the ×1.485 explosive modifier.")


def _carried_by(w):
    """Classes that spawn with the item, each linked and cited."""
    return ", ".join(class_link(e["value"].lower()) + cite(e) for e in w.get("class_default_for") or [])


def table_items():
    """Explosives, the knife and the ghost, for the weapons hub."""
    na = '<span class="na">—</span>'
    frag, det, smoke, knife, ghost = (weapon(wid) for wid in (
        "weapon_grenade", "weapon_remotedet", "weapon_smokegrenade", "weapon_knife", "weapon_ghost"))
    fs, ds, ss, ks, gs = (w["stats"] for w in (frag, det, smoke, knife, ghost))
    detpack_xp = next(c for c in data("player")["convars"] if c["name"] == "sv_neo_detpack_xp_limit")
    backstab_kills = ks["backstab_damage"]["value"] > max(hp for _, _, hp in TARGETS)
    rows = [
        [wlink("weapon_grenade"), val(fs["blast_damage_effective"]), val(fs["blast_radius"], " u"),
         _carried_by(frag), f"{fmt(fs['fuse_s']['value'])} s fuse{cite(fs['fuse_s'])}, linear falloff{cite(fs['falloff'])}"],
        [wlink("weapon_remotedet"), val(ds["blast_damage_effective"]), val(ds["blast_radius"], " u"),
         f"{_carried_by(det)} ({detpack_xp['default']}+ XP){cite(detpack_xp)}", f"Remote detonation{cite(ds['trigger'])}"],
        [wlink("weapon_smokegrenade"), val(ss["damage"]), na,
         f"{_carried_by(smoke)} (×{fmt(ss['count']['value'])}){cite(ss['count'])}",
         f"{fmt(ss['smoke_duration_s']['value'])} s smoke{cite(ss['smoke_duration_s'])}"],
        [wlink("weapon_knife"), f"{val(ks['damage'])} / {val(ks['backstab_damage'])}", val(ks["range"], " u"),
         _carried_by(knife), "Backstab kills any class" if backstab_kills else ""],
        [wlink("weapon_ghost"), na, na, "Anyone" + cite(ghost["pickup_classes"]),
         f"CTG objective; reveals enemies within {fmt(gs['enemy_detection_range_units']['value'])} u"
         f"{cite(gs['enemy_detection_range_units'])}"],
    ]
    return table([("Item", False),
                  ("Damage", True, "Damage at the centre of the blast, or per hit for the knife (slash / backstab)"),
                  ("Radius", True, "Where the blast's damage falls to zero, or the knife's reach"),
                  ("Carried by", False), ("Notes", False)], rows)


def table_accuracy():
    """What widens the spread, and how fast it recovers."""
    a = data("weapons")["damage_model"]["accuracy_model"]
    rows = [
        ["Each shot fired", f"+{val(a['penalty_per_shot'])}"],
        ["Airborne, per second", f"+{val(a['airborne_penalty_per_s'])}"],
        ["Moving without aiming (speed > 5), per second", f"+{val(a['moving_unaimed_penalty_per_s'])}"],
        ["Recovery, per second", f"−{val(a['decay_per_s'])}"],
        ["Extra recovery while crouched, per second", f"−{val(a['crouch_extra_decay_per_s'])}"],
    ]
    return table([("Effect", False), ("Penalty", True)], rows,
                 caption=f"Changes to the accuracy penalty. The penalty runs from 0 to {fmt(a['max_penalty']['value'])}"
                         f" and is capped there.{cite(a['max_penalty'])}")


def table_hitgroups():
    hg = data("weapons")["damage_model"]["hitgroup_multipliers"]
    rows = [[label, f"×{fmt(hg[k]['value'])}{cite(hg[k])}{bar(hg[k]['value'], 1)}"] for k, label in HITGROUPS]
    return table([("Hit location", False), ("Damage multiplier", True)], rows)


def table_penetration():
    mats = [m for m in data("weapons")["penetration_materials"]
            if m["material"] != "UNUSED" and not m.get("hl2_only", {}).get("value")]
    rows = []
    for m in sorted(mats, key=lambda m: m["resistance_value"]["value"]):
        v = m["resistance_value"]["value"]
        reach = 12 * 1
        note = esc(m.get("note", "")).split(" (")[0]
        rows.append([f"<code>{esc(m['material'].lower())}</code>", f"{fmt(v)}{cite(m['resistance_value'])}{bar(v, 1)}",
                     f"{fmt(round(12 / v, 1))}", note])
    return table([("Surface", False), ("Value", True), ("Pen. to cross 12u", True), ("Notes", False)], rows,
                 caption="Higher values are easier to shoot through. The third column is how much penetration a "
                         "bullet needs to cross 12 units of that surface. Surfaces only Half-Life 2 uses are left out.")


def weapon_count():
    return str(sum(1 for w in weapons() if w["id"] in WEAPONS and w["id"] not in WIP_WEAPONS))


# ---------------------------------------------------------------- game modes

def mode(mid):
    return next(m for m in data("gamemodes")["game_modes"] if m["id"] == mid)


MODE_SLUGS = {"ctg": "capture-the-ghost", "vip": "vip", "tdm": "team-deathmatch", "dm": "deathmatch",
              "jgr": "juggernaut", "tut": None, "emt": None}


def mode_link(mid):
    m = mode(mid)
    slug = MODE_SLUGS.get(mid)
    return f"[[{slug}|{esc(m['name'])}]]" if slug else esc(m["name"])


def rule(m, key, suffix=""):
    r = m["rules"].get(key)
    if not r or r.get("value") is None:
        return '<span class="na">—</span>'
    v = r["value"]
    if isinstance(v, bool):
        v = "Yes" if v else "No"
    return f"{fmt(v)}{suffix}{cite(r)}"


def table_modes():
    rows = []
    for mid in ("ctg", "tdm", "dm", "vip", "jgr"):
        m = mode(mid)
        r = m["rules"]
        resp = r.get("respawns") or r.get("respawns_flag")
        rt = r.get("round_time")
        lim = r.get("score_limit") or r.get("round_limit")
        if mid == "dm":
            lim_txt = f"{r['win_xp']['value']} XP{cite(r['win_xp'])}"
        elif mid == "jgr":
            lim_txt = f"{r['round_limit']['value']} rounds{cite(r['round_limit'])}"
        elif lim and lim.get("value"):
            lim_txt = f"{plural(lim['value'], 'win')}{cite(lim)}"
        else:
            lim_txt = '<span class="na">—</span>'
        wip = mid in WIP_MODES
        cells = [
            f"<b>{mode_link(mid)}</b>" + (f" {WIP_TAG}" if wip else ""),
            f"<code>{m['short_code']}</code>",
            ("Yes" if resp["value"] else "No") + cite(resp) if resp else "—",
            f"{fmt(rt['value'])} min{cite(rt)}" if rt else '<span class="na">—</span>',
            lim_txt,
            esc(m["objective"]),
        ]
        rows.append(("wip", cells) if wip else cells)
    return table([("Mode", False), ("Code", False), ("Respawns", False), ("Round", True), ("Match to", False),
                  ("Objective", False)], rows,
                 caption="Round times include the 15-second freeze at the start.", cls="modes")


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


def table_mode_rules(mid):
    m = mode(mid)
    labels = {
        "respawns": "Respawns", "respawn_delay": "Respawn delay", "round_time": "Round time",
        "preround_freeze_time": "Pre-round freeze", "score_limit": "Score limit", "round_limit": "Round limit",
        "overtime_enabled": "Overtime", "overtime_max_extension": "Max overtime", "overtime_grace": "Overtime grace",
        "win_xp": "XP to win", "max_points_per_round": "Points to win round", "juggernaut_unlock_delay": "Suit unlocks after",
        "xp_cap_at_round_start": "XP cap each round", "class_change_window_on_respawn": "Class change window",
        "ghost_on_vip_death": "Ghost on VIP death", "competitive_mode": "Competitive features", "teamplay": "Teams",
    }
    rows = []
    for key, rec in m["rules"].items():
        if key not in labels or not isinstance(rec, dict) or rec.get("value") is None:
            continue
        v = rec["value"]
        if isinstance(v, bool):
            v = "Yes" if v else "No"
        unit = rec.get("unit", "")
        unit = "" if unit.startswith("rounds (") else unit
        cv = f"<code>{esc(rec['convar'])}</code>" if rec.get("convar") else ""
        rows.append([labels[key], f"{fmt(v)} {esc(unit)}{cite(rec)}", cv])
    return table([("Setting", False), ("Default", False), ("Console variable", False)], rows)


CODE_TOKEN = re.compile(r"\b\w+_\w+\b|\b[a-z]+[A-Z]\w*\b|\b[A-Z][a-z]+[A-Z]\w*\b|\w+\(\)")


def plain(text):
    """Extraction notes in player language: drops asides about code, keeps the rule.

    Returns (text, changed). text is None when nothing readable is left, e.g. a note
    that is all about map scripting."""
    t = re.sub(r"\s*\(([^()]*)\)", lambda m: "" if CODE_TOKEN.search(m.group(1)) else m.group(0), text)
    t = re.sub(r"\b\w+_\w+ \((\d+(?:\.\d+)?)\)", r"\1", t)   # "sv_neo_dm_win_xp (50) XP" -> "50 XP"
    t = re.sub(r"\s*>=\s*", " at least ", t)
    t = re.sub(r"\s*<=\s*", " at most ", t)
    if CODE_TOKEN.search(t):
        return None, True
    return t, t != text


def list_win_conditions(mid):
    m = mode(mid)
    shown, originals = [], []
    for c in m["win_conditions"]:
        text, changed = plain(c["condition"])
        if text:
            shown.append(f"<li>{esc(text)}{cite(c)}</li>")
        if changed:
            originals.append(f"<li>{cite_text(c['condition'])}{cite(c)}</li>")
    out = "<ul>" + "".join(shown) + "</ul>"
    if originals:
        out += technical("<p>As extracted from the code:</p><ul>" + "".join(originals) + "</ul>")
    return out


def mode_scoring(mid):
    m = mode(mid)
    rows = []
    for e in m["scoring"]:
        pts = e.get("team_points", "")
        xp = e.get("xp", "")
        notes = e.get("notes", "").replace("See xp_scoring.round_end. ", "")
        text, _ = plain(notes)
        rows.append([esc(e["event"]), esc(pts), esc(xp if isinstance(xp, str) else f"{xp:+d}"),
                     (esc(text) if text is not None else cite_text(notes)) + cite(e)])
    return table([("Event", False), ("Team points", False), ("XP", False), ("Notes", False)], rows)


def infobox_ghost():
    g = data("gamemodes")["ghost"]
    props, beacons = g["properties"], g["beacons"]
    gw = weapon("weapon_ghost")["stats"]
    bucket = props["slot"]["value"]
    slot = {0: "Primary"}.get(bucket, f"Bucket {bucket}")  # the script's "bucket"; 0 is the primary slot
    carried = without_wip(props["pickup_restriction"]["value"]) or props["pickup_restriction"]["value"]
    return infobox("Ghost", [
        ("Slot", slot + cite(props["slot"])),
        ("Carried by", esc(carried) + cite(props["pickup_restriction"])),
        ("Can shoot", val(props["can_attack"])),
        ("Move speed", "×" + val(gw["movement_speed_scale"])),
        ("section", "Enemy beacons"),
        ("Range", f"{val(beacons['range'], ' m')} ({fmt(gw['enemy_detection_range_units']['value'])} u)"),
        ("Boot-up", val(beacons["bootup_delay"], " s")),
    ], image="Ghost world model")


def infobox_ctg():
    m = mode("ctg")
    g = data("gamemodes")
    hold = g["ghost"]["capture_zones"]["hold_time"]
    return infobox("Capture the Ghost", [
        ("Code", esc(m["short_code"]) + cite(m["short_code_source"])),
        ("Maps", f"<code>{esc(m['map_prefix'])}</code> ({g['maps']['counts']['ctg']}){cite(g['maps']['source'])}"),
        ("Round", rule(m, "round_time", " min")),
        ("Match to", rule(m, "score_limit", " rounds")),
        ("Lives", ("Respawns" if m["rules"]["respawns"]["value"] else "One per round") + cite(m["rules"]["respawns"])),
        ("Capture time", ("Instant" if not hold["value"] else plural(hold["value"], "second")) + cite(hold)),
    ], image="Ghost capture screenshot")


# ---------------------------------------------------------------- branding

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


def asset_mark():
    svg = (DOCS / "assets" / "nt-mark.svg").read_text()
    return re.sub(r"^\s*<!--.*?-->\s*", "", svg, flags=re.S).strip()


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


# ---------------------------------------------------------------- column tooltips

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


# ---------------------------------------------------------------- dispatch

SNIPPETS = {
    "infobox:class": infobox_class,
    "table:classes": table_classes,
    "table:weapon-speed": table_weapon_speed,
    "table:ranks": table_ranks,
    "table:loadouts": table_loadout_matrix,
    "table:loadout": table_loadout,
    "table:xp": table_xp,
    "table:convars": table_convars,
    "table:weapons": table_weapons,
    "table:stk": table_stk,
    "table:hitgroups": table_hitgroups,
    "table:explosives": table_explosives,
    "table:items": table_items,
    "table:penetration": table_penetration,
    "table:accuracy": table_accuracy,
    "table:cloak": table_cloak,
    "table:aux-regen": table_aux_regen,
    "infobox:cloak": infobox_cloak,
    "infobox:aux": infobox_aux,
    "infobox:ghost": infobox_ghost,
    "infobox:ctg": infobox_ctg,
    "table:modes": table_modes,
    "table:maps": table_maps,
    "table:mode-rules": table_mode_rules,
    "table:mode-scoring": mode_scoring,
    "table:win-conditions": list_win_conditions,
    "stat:weapon-count": weapon_count,
    "asset:mark": asset_mark,
    "table:palette": table_palette,
    "stat": stat,
}

# {{weapon:NAME}} or {{weapon:NAME:ARG}}: the weapon comes from the page's `weapon:` front matter.
WEAPON_SNIPPETS = {
    "stats": weapon_stats,
    "damage": weapon_damage,
    "stk": weapon_stk,
    "ttk": weapon_ttk,
    "handling": weapon_handling,
    "availability": weapon_availability,
    "special": weapon_special,
    "suppressor": weapon_suppressor,
    "notes": weapon_notes,
    "explosive": weapon_explosive,
    "attacks": weapon_attacks,
}

SNIPPET_RE = re.compile(r"\{\{((?:infobox|table|stat|asset|weapon):[^}]+)\}\}")


class SnippetError(Exception):
    pass


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
        inline = m.group(1).startswith(("stat", "asset"))
        return out if inline else f"\n\n{out}\n\n"

    return SNIPPET_RE.sub(repl, body)
