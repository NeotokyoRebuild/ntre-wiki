"""Weapon data helpers, and the snippets for the Weapons hub and its category pages."""

import re

from ._core import WIP_TAG, WIP_WEAPONS, bar, cite, data, esc, fmt, snippet, table, val, without_wip
from .classes import CLASS_ORDER, class_link, player_class


# -------- Shared with weapon_page.py and mechanics.py

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
HITGROUPS = [("head", "Head"), ("chest", "Chest"), ("stomach", "Stomach"), ("arms", "Arms"), ("legs", "Legs")]
# (class id, name, max health) for the classes damage tables are worked out against.
TARGETS = [(cid, player_class(cid)["name"], player_class(cid)["stats"]["max_health"]["value"]) for cid in CLASS_ORDER]
SUPPRESSED_NOTE_PREFIX = "Suppressed (NEO_WEP_SUPPRESSED"


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


# -------- weapons/index.md and the category pages

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


@snippet("table:weapons")
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


@snippet("table:stk")
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


def _carried_by(w):
    """Classes that spawn with the item, each linked and cited."""
    return ", ".join(class_link(e["value"].lower()) + cite(e) for e in w.get("class_default_for") or [])


@snippet("table:items")
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


@snippet("stat:weapon-count")
def weapon_count():
    return str(sum(1 for w in weapons() if w["id"] in WEAPONS and w["id"] not in WIP_WEAPONS))
