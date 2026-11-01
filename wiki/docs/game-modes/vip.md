---
description: "Extract or Kill the VIP, the VIP role and the SMAC"
weapon: weapon_smac
---

# VIP

{{infobox:class:vip}}

!!! warning "Work in progress"
    VIP is still in development. Its rules and numbers are likely to change, and no official map is built for it yet.

!!! info "Not a class you can pick"
    The VIP is a role the VIP mode assigns. You can't choose it from the class menu, and it only exists in this mode.

In **Extract or Kill the VIP** (VIP), one team escorts a lightly armed **VIP** to its extraction zone. The other team tries to kill them.

VIP is also the name of the special class the escorted player becomes. The mode uses the same capture zones as [[capture-the-ghost|Capture the Ghost]] (CTG).

## Objective

- **Escorting team:** get the VIP into your extraction zone.
- **Other team:** kill the VIP.

Wiping out the enemy team also wins the round.[[src:src/game/shared/neo/neo_gamerules.cpp:1691-1702]]

{{table:win-conditions:vip}}

## Round flow

1. **Warmup** (45 seconds), once when a match starts. XP doesn't count, and when warmup ends everyone's XP resets to 0.[[src:src/game/shared/neo/neo_gamerules.cpp:49,2875-2928]]
1. **Pre-round freeze** (15 seconds). You can change loadout but can't move, and you can't be hurt.[[src:src/game/shared/neo/neo_gamerules.cpp:50]]
1. **Live round.** You get one life, as in CTG, and the round timer is 3.25 minutes with the freeze included.[[src:src/game/shared/neo/neo_gamerules.cpp:410,520]] Time running out is a stalemate.[[src:src/game/shared/neo/neo_gamerules.cpp:1479-1481]]
1. **Post-round** (15 seconds), then the next freeze.[[src:src/game/shared/multiplay_gamerules.cpp:67-70]]

The teams take turns escorting, and the VIP goes back to their old class at the start of the next round. See [Who becomes the VIP](#who-becomes-the-vip).

The first team to win 7 rounds wins the match.[[src:src/game/shared/neo/neo_gamerules.cpp:496]] The ready-up lobby and pauses work here as they do in [[capture-the-ghost#competitive-features|CTG]].[[src:src/game/shared/neo/neo_gamerules.cpp:2720-2783; src/game/server/neo/neo_player.cpp:1937]]

## Who becomes the VIP

The escorting team is picked at random in the first round, then the teams take turns.

The VIP is a random player on that team with `cl_neo_vip_eligible 1`, which is the default. If nobody has it set, anyone on the team can be picked.[[src:src/game/shared/neo/neo_gamerules.cpp:2239-2285,3331-3340]]

At the start of the next round, the VIP goes back to their previous class.[[src:src/game/shared/neo/neo_gamerules.cpp:3392-3403]]

## The VIP class

- **100 HP**, with Assault's movement speeds: 160 run, 256 sprint.
- No [[thermoptic-camouflage|cloak]] and no [[vision-modes|vision mode]].
- Like the ghost carrier, loses any speed above their run speed while airborne.[[src:src/game/shared/gamemovement.cpp:1724-1770]]
- One player model, shared by both teams.[[src:src/game/server/neo/neo_model_manager.cpp:375,379]]
- Can't pick up a knife, and can't change class while VIP.[[src:src/game/shared/neo/weapons/weapon_knife.cpp:109; src/game/server/neo/neo_player.cpp:429-435]]
- Spawns with a [[milso|MilSO]]. The primary loadout starts with the [[#smac|SMAC]], which has one 90-round magazine and no reserve. More unlock with rank:

{{table:loadout:vip}}

## SMAC

The **SMAC** is the VIP's own fully automatic submachine gun. No other class can pick it.

### General stats

{{weapon:stats}}

### Damage

!!! info "No headshot bonus"
    A headshot deals the same damage as a shot to the chest.

{{weapon:damage}}

### Shots to kill

{{weapon:stk}}

### Time to kill

{{weapon:ttk}}

### Handling

{{weapon:handling}}

{{weapon:notes}}

## Rules

{{table:mode-rules:vip}}

A server setting can stop the VIP's death from ending the round. Instead, "HVT DOWN" is announced and a ghost spawns where the VIP fell. The round carries on as a ghost capture.[[src:src/game/shared/neo/neo_gamerules.cpp:1596-1618]]

## Scoring

{{table:mode-scoring:vip}}

!!! info "Maps"
    None of the official maps has a `_vip` suffix, and VIP is left out of the default random rotation. The mode is supported in code, but no official map is built for it.

## Bots

Bots have no special VIP behaviour: they just hunt down enemies.

## For server admins

`sv_neo_vip_ctg_on_death 1` turns the VIP's death into a ghost capture, as described under [Rules](#rules).[[src:src/game/shared/neo/neo_gamerules.cpp:1596-1618]]

All of the VIP mode's own settings:

{{table:convars:vip}}
