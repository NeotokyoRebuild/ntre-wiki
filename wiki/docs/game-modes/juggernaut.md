---
description: "JGR mode, the JGR56 juggernaut suit and the BALC"
weapon: weapon_balc
---

# Juggernaut

{{infobox:class:juggernaut}}

!!! warning "Work in progress"
    Juggernaut is still in development. Its rules and numbers are likely to change.

!!! info "Not a class you can pick"
    The Juggernaut is a role the Juggernaut mode assigns. You can't choose it from the class menu, and it only exists in this mode.

In **Juggernaut** (JGR), both teams fight over a single **JGR56 suit**. Whoever activates it becomes the Juggernaut, with **990 HP**, a [[#balc|BALC]] heat weapon and night vision.

## Objective

Get the suit. While your team has the Juggernaut, your kills score points. The first team to **20 points** wins the round.[[src:src/game/shared/neo/neo_gamerules.cpp:1577-1590]]

{{table:win-conditions:jgr}}

## Round flow

1. **Warmup** (45 seconds), once when a match starts. XP doesn't count, and when warmup ends everyone's XP resets to 0.[[src:src/game/shared/neo/neo_gamerules.cpp:49,2875-2928]]
1. **Pre-round freeze** (15 seconds). You can change loadout but can't move, and you can't be hurt.[[src:src/game/shared/neo/neo_gamerules.cpp:50]] Anyone above 10 XP is cut back to 10 (Sergeant).[[src:src/game/shared/neo/neo_gamerules.cpp:3414-3421]]
1. **Live round**, 4.25 minutes with the freeze included.[[src:src/game/shared/neo/neo_gamerules.cpp:526]] The suit unlocks 20 seconds after the freeze ends.[[src:src/game/shared/neo/neo_gamerules.cpp:1556-1575]] You respawn after death, with [one exception](#respawning).
1. **Overtime**, if time runs out while a Juggernaut is alive or the trailing team is activating the suit.[[src:src/game/shared/neo/neo_gamerules.cpp:1457-1476]]
1. **Post-round** (15 seconds), then the next freeze.[[src:src/game/shared/multiplay_gamerules.cpp:67-70]]

A match is 5 rounds. The team that wins more of them wins the match, and it ends early once the trailing team can't catch up. A tie after 5 rounds goes to sudden death.[[src:src/game/shared/neo/neo_gamerules.cpp:488,511,3877-3909]] The ready-up lobby and pauses work here as they do in [[capture-the-ghost#competitive-features|CTG]].[[src:src/game/shared/neo/neo_gamerules.cpp:2720-2783; src/game/server/neo/neo_player.cpp:1937]]

## The suit

- It spawns at a juggernaut spawn point each round. It stays locked until **20 seconds** after the freeze ends ("JUGGERNAUT ENABLED").[[src:src/game/shared/neo/neo_gamerules.cpp:1556-1575]]
- To activate it, stand within 150 units and hold <kbd>Use</kbd> for **5 seconds**. You're frozen while you hold. Letting go, dying or moving away cancels it.[[src:src/game/shared/neo/neo_juggernaut.cpp:14-15,150-222]]
- When you activate it, you drop all your weapons and get full health and 100 AUX. Dead teammates respawn immediately.[[src:src/game/shared/neo/neo_juggernaut.cpp:198-216]]
- When the Juggernaut dies, the suit drops where they fell and can be taken again.[[src:src/game/server/neo/neo_player.cpp:4100-4127]]

## Playing as the Juggernaut

- **990 HP**. You don't bleed and can't be gibbed.[[src:src/game/server/neo/neo_player.cpp:4094-4096]]
- Your only weapon is the [[#balc|BALC]]. It has no magazine. It overheats after 50 shots and locks for 5 seconds, and has a charged grenade alt-fire. It doesn't slow you down (×1.0).
- You can't pick up the ghost or any other weapon.
- Everyone can always see your position on the compass.[[src:src/game/server/neo/neo_player.cpp:3946-3950]]
- You jump 1.4 times as high as normal, to 50.4 units.[[src:src/game/shared/gamemovement.cpp:2645-2656]]
- Like the ghost carrier, you lose any speed above your run speed while airborne.[[src:src/game/shared/gamemovement.cpp:1724-1770]]
- One player model, shared by both teams.[[src:src/game/server/neo/neo_model_manager.cpp:375,379]]
- AUX regenerates at 10 per second.

!!! warning "Unresolved: sprint speed"
    The Juggernaut probably sprints at **256** units per second, but the code disagrees with itself. The movement code gives 256. The defined constant and `GetSprintSpeed()` say 270. This hasn't been checked in game yet.

## BALC

The **BALC** is the Juggernaut's heat-cooled machine gun, and the only weapon the suit can use.

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

### Heat system

{{weapon:special:heat_system}}

### Charged grenade

{{weapon:special:charge_shot}}

!!! warning "Unconfirmed: extra recoil on long bursts"
    The BALC adds up to 1 degree of extra vertical recoil after 10 shots in a row. This comes from reading the code and hasn't been tested in play.[[src:src/game/shared/neo/neo_shot_manipulator.cpp:63-147]]

{{weapon:notes}}

## Respawning

JGR has respawns, after a 10-second delay. But the Juggernaut's team **can't respawn** while the Juggernaut is alive, or for 8 seconds after they die.[[src:src/game/shared/neo/neo_gamerules.cpp:4553-4559]]

## Scoring

{{table:mode-scoring:jgr}}

## Rules

{{table:mode-rules:jgr}}

Official maps: `ntre_sentinel_jgr`, `ntre_terminal_jgr`, `ntre_yard_jgr`.

## Bots

Bots have their own behaviour for JGR, rather than just hunting down enemies.

## For server admins

All of the JGR mode's own settings:

{{table:convars:jgr}}
