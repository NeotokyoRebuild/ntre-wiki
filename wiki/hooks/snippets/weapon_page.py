"""The {{weapon:NAME}} sections of a single weapon's page. The weapon comes from the page's
`weapon:` front matter."""

from ._core import (
    WIP_CLASSES,
    WIP_TAG,
    cite,
    cite_text,
    data,
    esc,
    fmt,
    plural,
    snippet,
    table,
    technical,
    val,
    without_wip,
)
from .classes import class_link, player_class
from .weapons import (
    HITGROUPS,
    SUPPRESSED_NOTE_PREFIX,
    TARGETS,
    classes_text,
    cycle_time,
    dps,
    hit_tiers,
    hitmult,
    is_gun,
    per_shot_damage,
    shots_to_kill,
    sval,
    tier_label,
)


# -------- Stats and damage

def stat_strip(cells):
    """One-row table of headline stats: cells is [(label, html, is_numeric), ...]."""
    return table([(label, num) for label, _, num in cells], [[c for _, c, _ in cells]], cls="stat-strip")


@snippet("weapon:stats")
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


@snippet("weapon:damage")
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


@snippet("weapon:stk")
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


@snippet("weapon:ttk")
def weapon_ttk(w):
    ct = cycle_time(w)
    auto = any(m.startswith("auto") for m in w["stats"]["fire_modes"]["value"])

    def cell(d, hp):
        n = shots_to_kill(d, hp)
        return f"{(n - 1) * ct:.2f} s"

    cap = ("Time from your first hit to your last, with every shot landing and no reload: (shots to kill − 1) "
           "× cycle time." + ("" if auto else " You only reach it by firing as fast as the gun allows."))
    return _per_class_table(w, cell, cap)


# -------- Handling and availability

@snippet("weapon:handling")
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


@snippet("weapon:availability")
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


# -------- Weapon-specific sections

SPECIAL_TITLES = {"bolt_action": "Bolt action", "slug": "Slug rounds", "reload": "Reloading",
                  "heat_system": "Heat system", "charge_shot": "Charged grenade",
                  "firemode_switch_delay_s": "Fire-mode switch"}


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


@snippet("weapon:special")
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


# -------- Other sections

@snippet("weapon:suppressor")
def weapon_suppressor(w):
    return ("<p>No muzzle flash, and firing it doesn't make your [[thermoptic-camouflage|cloak]] flash. "
            "Bots also have a harder time hearing it."
            "[[src:src/game/shared/neo/weapons/weapon_neobasecombatweapon.cpp:1011-1020]]</p>")


def technical_notes(w):
    notes = [without_wip(n) for n in w.get("notes", []) if isinstance(n, str) and not n.startswith(SUPPRESSED_NOTE_PREFIX)]
    return [n for n in notes if n]


@snippet("weapon:notes")
def weapon_notes(w):
    """The extraction notes for a weapon: technical by nature, so collapsed."""
    notes = technical_notes(w)
    if not notes:
        return ""
    return technical("<ul>" + "".join(f"<li>{cite_text(n)}</li>" for n in notes) + "</ul>", "Technical notes")


@snippet("weapon:explosive")
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


@snippet("weapon:attacks")
def knife_section(w):
    s = w["stats"]
    toughest = player_class("support")
    return (f"<p>A slash deals {fmt(s['damage']['value'])} damage{cite(s['damage'])} at up to {fmt(s['range']['value'])} units. "
            f"A <b>backstab</b> deals {s['backstab_damage']['value']}{cite(s['backstab_damage'])}: more than "
            f"[[support|Support]]'s {toughest['stats']['max_health']['value']} HP,{cite(toughest['stats']['max_health'])} "
            "so it kills any selectable class outright. The global damage modifier does not apply to the knife.</p>")
