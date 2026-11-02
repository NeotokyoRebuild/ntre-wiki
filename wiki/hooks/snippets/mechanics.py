"""Snippets for the Mechanics pages (docs/mechanics/), grouped by page."""

import re

from ._core import (
    WIP_CLASSES,
    WIP_TAG,
    WIP_WEAPONS,
    bar,
    cite,
    data,
    esc,
    fmt,
    infobox,
    snippet,
    table,
    val,
    without_wip,
)
from .classes import CLASS_ORDER, class_link, player_class, weapon_link
from .weapons import HITGROUPS, WEAPONS, weapon, wlink


# -------- mechanics/movement.md

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


@snippet("table:weapon-speed")
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


# -------- mechanics/loadouts.md

@snippet("table:ranks")
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


@snippet("table:loadouts")
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


@snippet("table:xp")
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


# -------- mechanics/thermoptic-camouflage.md

def cloak_classes():
    return [player_class(cid) for cid in data("player")["cloak"]["classes"]["value"]]


@snippet("infobox:cloak")
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


@snippet("table:cloak")
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


# -------- mechanics/aux-power.md

@snippet("infobox:aux")
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


@snippet("table:aux-regen")
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


# -------- mechanics/damage.md

@snippet("table:hitgroups")
def table_hitgroups():
    hg = data("weapons")["damage_model"]["hitgroup_multipliers"]
    rows = [[label, f"×{fmt(hg[k]['value'])}{cite(hg[k])}{bar(hg[k]['value'], 1)}"] for k, label in HITGROUPS]
    return table([("Hit location", False), ("Damage multiplier", True)], rows)


@snippet("table:accuracy")
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


@snippet("table:penetration")
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


@snippet("table:explosives")
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
