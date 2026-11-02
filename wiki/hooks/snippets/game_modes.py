"""Snippets for the Game modes pages (docs/game-modes/)."""

import re

from ._core import (
    WIP_MODES,
    WIP_TAG,
    cite,
    cite_text,
    data,
    esc,
    fmt,
    infobox,
    plural,
    snippet,
    table,
    technical,
    val,
    without_wip,
)
from .weapons import weapon


# -------- Shared

MODE_SLUGS = {"ctg": "capture-the-ghost", "vip": "vip", "tdm": "team-deathmatch", "dm": "deathmatch",
              "jgr": "juggernaut", "tut": None, "emt": None}


def mode(mid):
    return next(m for m in data("gamemodes")["game_modes"] if m["id"] == mid)


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


# -------- game-modes/index.md

@snippet("table:modes")
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


# -------- game-modes/<mode>.md

@snippet("table:mode-rules")
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


@snippet("table:win-conditions")
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


@snippet("table:mode-scoring")
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


# -------- game-modes/capture-the-ghost/

@snippet("infobox:ctg")
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


@snippet("infobox:ghost")
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
