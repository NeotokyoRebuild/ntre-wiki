---
description: "DM: free-for-all, first to 50 XP"
---

# Deathmatch

**Deathmatch** (DM) is free-for-all. Every other player is an enemy, and there are no teamkill penalties.

## Objective

Be the first player to **50 XP**. Each kill is worth 1 XP.[[src:src/game/shared/neo/neo_gamerules.cpp:532,4198-4226]] If nobody gets there, whoever has the most XP when time runs out wins the map.

{{table:win-conditions:dm}}

## Round flow

1. **Warmup** (45 seconds), once when a match starts. XP doesn't count, and when warmup ends everyone's XP resets to 0.[[src:src/game/shared/neo/neo_gamerules.cpp:49,2875-2928]]
1. **Pre-round freeze** (15 seconds). You can change loadout but can't move, and you can't be hurt.[[src:src/game/shared/neo/neo_gamerules.cpp:50]]
1. **Live round**, up to 10.25 minutes. It ends early as soon as one player reaches 50 XP.[[src:src/game/shared/neo/neo_gamerules.cpp:523,1704-1715]]
1. **Overtime**, if the top players are tied when time runs out. It lasts until one player leads alone.[[src:src/game/shared/neo/neo_gamerules.cpp:1422-1439]]
1. Once there's a winner, the map ends.[[src:src/game/shared/neo/neo_gamerules.cpp:1721-1784]]

Every player's XP resets to 0 at the start of each round.[[src:src/game/shared/neo/neo_gamerules.cpp:3357-3367]]

A round won't start until at least 2 players have joined.[[src:src/game/shared/neo/neo_gamerules.cpp:2728-2734]]

## Rules

{{table:mode-rules:dm}}

Teamplay is off, so there's no reflected team damage. Every kill counts as an enemy kill.[[src:src/game/shared/neo/neo_gamerules.cpp:4535-4538]]

## Spawns

Some maps have a saved list of spawn positions. On those, you spawn at a random unused position from the list. Otherwise the spawn points are shuffled every time.[[src:src/game/shared/neo/neo_gamerules.cpp:4619-4630; src/game/server/neo/neo_spawn_manager.cpp:76-80]]

??? note "Technical details"
    The saved spawn file is `maps/dm_locs/<map>.loc`.[[src:src/game/shared/neo/neo_gamerules.cpp:4619-4630; src/game/server/neo/neo_spawn_manager.cpp:76-80]]

## Scoring

{{table:mode-scoring:dm}}

!!! note ""
    The map file `ntre_apparatus_dm` is in the asset repository but not on the official map list. See [[maps|Maps]].
