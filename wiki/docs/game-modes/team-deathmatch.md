---
description: "TDM: respawning team combat scored by kills"
---

# Team Deathmatch

**Team Deathmatch** (TDM) is a respawn mode. Two teams fight for one long round.

The official map is `ntre_bullet_tdm`.

## Objective

Score more points than the enemy team. Every death scores a point for the other team, even a suicide or a teamkill.[[src:src/game/server/neo/neo_player.cpp:2426-2429]] The team with the higher score when time runs out wins.

{{table:win-conditions:tdm}}

## Round flow

1. **Warmup** (45 seconds), once when a match starts. XP doesn't count, and when warmup ends everyone's XP resets to 0.[[src:src/game/shared/neo/neo_gamerules.cpp:49,2875-2928]]
1. **Pre-round freeze** (15 seconds). You can change loadout but can't move, and you can't be hurt.[[src:src/game/shared/neo/neo_gamerules.cpp:50]]
1. **Live round**, about 10 minutes. You respawn after every death.[[src:src/game/shared/neo/neo_gamerules.cpp:408,514]] There's no overtime: equal scores at time-out are a stalemate.[[src:src/game/shared/neo/neo_gamerules.cpp:1479-1481]]
1. **Post-round** (15 seconds), then the next freeze.[[src:src/game/shared/multiplay_gamerules.cpp:67-70]] Nobody respawns during it.[[src:src/game/shared/neo/neo_gamerules.cpp:4561-4569]]

!!! info "One round"
    The default score limit is 1 round won, so a TDM match is a single 10.25-minute round.[[src:src/game/shared/neo/neo_gamerules.cpp:492]]

## Rules

{{table:mode-rules:tdm}}

- You respawn 10 seconds after death, and get the loadout menu again.[[src:src/game/shared/baseplayer_shared.h:34]]
- For the first 5 seconds after spawning, you take no damage. Firing or dropping a weapon ends this early.[[src:src/game/server/neo/neo_player.cpp:2667-2676]]
- For 10 seconds after spawning, you can still change class.[[src:src/game/server/neo/neo_player.cpp:153]]

## Scoring

{{table:mode-scoring:tdm}}
