---
description: "CTG, NT;RE's core competitive mode"
---

# Capture the Ghost

{{infobox:ctg}}

**Capture the Ghost** (CTG) is NT;RE's core mode, a take on capture the flag. Each round, an AI core called the **[[ghost|ghost]]** spawns somewhere on the map.

You get one life per round.

## Objective

Find the ghost and carry it into your team's capture zone. Wiping out the enemy team also wins the round.

{{table:win-conditions:ctg}}

!!! info "Time-out is always a draw"
    When the clock runs out, it's a stalemate. It doesn't matter who holds the ghost or how many players are alive. The code has a "win by numbers" outcome, but nothing triggers it.[[src:src/game/shared/neo/neo_gamerules.cpp:1479-1481,3934-3936]]

## Round flow

Every round follows the same cycle:[[src:src/game/shared/neo/neo_gamerules.cpp:2720-2930]]

1. **Warmup** (45 seconds). This runs once, when a match starts. You respawn freely and XP doesn't count.[[src:src/game/shared/neo/neo_gamerules.cpp:49]]
1. **Pre-round freeze** (15 seconds). You can look around and change loadout, but you can't move. You can't be hurt either.[[src:src/game/shared/neo/neo_gamerules.cpp:50]]
1. **Live round.** The freeze counts towards the round timer, so a 3.25-minute round has about 3 minutes of live play.[[src:src/game/shared/neo/neo_gamerules.cpp:1876,2852]]
1. **[Overtime](#overtime)**, if the server has turned it on.
1. **Post-round** (15 seconds), then the next freeze.[[src:src/game/shared/multiplay_gamerules.cpp:67-70]]

When warmup ends, team scores and rounds won reset to 0. So does **every player's XP**.[[src:src/game/shared/neo/neo_gamerules.cpp:2875-2928]] The teams swap spawn sides and capture zones every round.[[src:src/game/shared/neo/neo_player_spawnpoint.cpp:86-95]]

If you haven't spawned yet, you can still spawn for up to 15 seconds after the freeze ends.[[src:src/game/shared/neo/neo_gamerules.cpp:51]]

A round won't start while either team is empty. The game tries again every 10 seconds.[[src:src/game/shared/neo/neo_gamerules.cpp:2768]]

## Match length

- The first team to win **7 rounds** wins the match.[[src:src/game/shared/neo/neo_gamerules.cpp:494]] The score limit counts rounds won, not kills.[[src:src/game/shared/neo/neo_gamerules.cpp:3866-3873]]
- If there's a round limit, the match ends early once the trailing team can no longer catch up.[[src:src/game/shared/neo/neo_gamerules.cpp:3877-3893]]
- If rounds won are tied when the limit is reached, play goes to **sudden death**. It continues until a team wins a round.[[src:src/game/shared/neo/neo_gamerules.cpp:488,3894-3909]]

## Rules

{{table:mode-rules:ctg}}

## Capture zones

A capture zone belongs to one team or is neutral. The zones swap between the teams every round, along with the spawns.[[src:src/game/shared/neo/neo_ghost_cap_point.cpp:132-141]]

The capture counts the instant a living ghost carrier reaches the zone. There's no hold timer.[[src:src/game/shared/neo/neo_ghost_cap_point.cpp:226-264]]

??? note "Technical details"
    Capture zones are `neo_ghost_retrieval_point` entities. The game checks them 10 times a second, using the 3D distance from the zone's centre to see whether the carrier is within the zone's radius.[[src:src/game/shared/neo/neo_ghost_cap_point.cpp:226-264]]

## Overtime

Overtime is off by default. When it's on, the round can run past the clock while someone is carrying the ghost. Dropping the ghost cuts the extra time short.[[src:src/game/shared/neo/neo_gamerules.cpp:1282-1294,1879-1908]]

??? note "Technical details"
    Overtime starts when the ghost is being carried with 10 seconds or less left. The round can then run up to 45 seconds past the limit while the ghost stays in hand. If the carrier drops it, the time left shrinks back to the 10-second grace.[[src:src/game/shared/neo/neo_gamerules.cpp:1282-1294,1879-1908]]

## XP and rewards

A ghost capture is the most valuable thing you can do in NT;RE. Every **surviving** player on the capturing team goes straight up to the next rank. Dead teammates get the normal +1.[[src:src/game/shared/neo/neo_gamerules.cpp:1813-1824,4002-4020]]

Winning by elimination gives:[[src:src/game/shared/neo/neo_gamerules.cpp:4029-4038]]

- +1 to the whole team
- +1 more to each survivor
- +1 more to the ghost carrier, so a surviving carrier gets +3

See [[loadouts|Loadouts & ranks]].

??? note "Technical details"
    Surviving capturers are raised straight to the next rank threshold: 0 → 4 → 10 → 20.[[src:src/game/shared/neo/neo_gamerules.cpp:1813-1824,4002-4020]]

### Cap prevention

Sometimes the enemy is carrying the ghost when the last living player on your team:

- kills themselves
- disconnects
- dies to their own team's grenade

The enemy team then still gets the capture reward when it wins the round.[[src:src/game/shared/neo/neo_gamerules.cpp:4106-4163]]

## Scoring

{{table:mode-scoring:ctg}}

## Competitive features

CTG supports competitive extras:[[src:src/game/shared/neo/neo_gamerules.cpp:197-215,2720-2783]]

- a ready-up lobby, 5 players per team by default
- `.pause` and `.unpause`, for 60 seconds or 180 seconds
- spectators can only watch their own team
- paired ghost spawns

## Maps

24 of the 32 official maps are CTG maps. See [[maps|Maps]].

## For server admins

- `sv_neo_comp 1` turns on all the [competitive features](#competitive-features) at once.[[src:src/game/shared/neo/neo_gamerules.cpp:197-215,2720-2783]]
- `mp_chattime` sets the 15-second post-round.[[src:src/game/shared/multiplay_gamerules.cpp:67-70]]
- `sv_neo_latespawn_max_time` sets the 15-second late-spawn window.[[src:src/game/shared/neo/neo_gamerules.cpp:51]]
- Sudden death needs `neo_round_sudden_death 1`.[[src:src/game/shared/neo/neo_gamerules.cpp:488,3894-3909]]
- `sv_neo_ctg_ghost_overtime_enabled` turns on overtime. It's 0 by default.[[src:src/game/shared/neo/neo_gamerules.cpp:1282-1294,1879-1908]]
- `sv_neo_suicide_prevent_cap_punish 1` gives the enemy the capture reward described under [Cap prevention](#cap-prevention).[[src:src/game/shared/neo/neo_gamerules.cpp:4106-4163]]
