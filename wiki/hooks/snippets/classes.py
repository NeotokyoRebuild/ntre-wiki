"""Snippets for the Classes pages (docs/classes/), and the class helpers other modules use."""

from ._core import WIP_CLASSES, WIP_TAG, bar, cite, data, esc, fmt, infobox, snippet, table, val


# -------- Shared

# The classes you can pick. VIP and Juggernaut are roles their game modes assign, covered on those pages.
CLASS_ORDER = ["recon", "assault", "support"]
CLASS_SLUGS = {"recon": "recon", "assault": "assault", "support": "support",
               "vip": "vip", "juggernaut": "juggernaut"}
VISION_NAMES = {"night_vision": "Night vision", "motion_vision": "Motion vision",
                "thermal_vision": "Thermal vision"}


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


def weapon_link(name):
    slug = WEAPON_SLUGS.get(name)
    return f"[[{slug}|{esc(name)}]]" if slug else esc(name)


# -------- classes/index.md

@snippet("table:classes")
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


# -------- classes/<class>.md

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


@snippet("infobox:class")
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


@snippet("table:loadout")
def table_loadout(cid):
    p = data("player")["rank_loadouts"]
    rows = []
    for e in p[cid]:
        xp = e["min_xp"]
        rows.append([weapon_link(e["weapon"]), "Any (even negative)" if xp == "any" else f"{xp}"])
    return table([("Primary weapon", False), (f"Min. XP{cite(p[cid + '_source'])}", True)], rows)
