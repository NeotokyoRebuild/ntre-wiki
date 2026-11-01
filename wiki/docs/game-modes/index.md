---
description: "The game types NT;RE supports"
---

# Game modes

**[[capture-the-ghost|Capture the Ghost]]** (CTG) is NT;RE's core competitive mode, and 24 of the official maps are built for it.

Alongside it are two respawn modes, [[team-deathmatch|Team Deathmatch]] (TDM) and [[deathmatch|Deathmatch]] (DM).

{{table:modes}}

!!! info "Default values"
    These are the default values. Custom servers may run different values.

## Choosing the mode

Each map sets its own mode by default. A map that doesn't falls back to Free Roam.[[src:src/game/shared/neo/neo_gamerules.cpp:1089-1093]] Servers can override this: see [For server admins](#for-server-admins).

??? note "Technical details"
    A map sets its mode through a `neo_game_config` entity.[[src:src/game/shared/neo/neo_gamerules.cpp:1089-1093]]

## Other modes

- **Training** (`TUT`): tutorial maps (`ntre_class_tut`, `ntre_shooting_tut`) with no round logic. Completing them earns achievements.[[src:src/game/shared/neo/achievements_neo.cpp:7-46]]
- **Free Roam** (`EMT`): no objective and no scoring. You can change team, class and loadout while alive.[[src:src/game/shared/neo/neo_gamerules.cpp:412]]

## Bots

Bots know how to play CTG: they seek, carry and escort the ghost, and some lie in wait as lone wolves. In TDM and DM they just hunt down enemies.

You can command bots with <kbd>Use</kbd>.[[src:src/game/server/neo/bot/behavior/neo_bot_seek_and_destroy.cpp:164-200; src/game/shared/neo/neo_player_shared.cpp:193]]

## For server admins

`sv_neo_gamemode_enforcement` overrides the mode each map sets:

| Value | Behaviour |
| ---: | --- |
| 0 | Mode set by the map (default) |
| 1 | Always `sv_neo_gamemode_single`[[src:src/game/shared/neo/neo_gamerules.cpp:1033-1036]] |
| 2 | Random from the `sv_neo_gamemode_random_allow` bitmask, without repeats until every allowed mode has been played. The default mask, 11, covers TDM, CTG and DM.[[src:src/game/shared/neo/neo_gamerules.cpp:1037-1088]] |
| 3 | Player vote, using each client's `neo_vote_game_mode`[[src:src/game/shared/neo/neo_gamerules.cpp:2333-2365]] |
