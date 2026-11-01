---
description: "How XP, rank and class decide which weapons you can pick"
---

# Loadouts & ranks

You earn **XP** by killing enemies and winning rounds, and lose it for teamkills and suicides. Your XP sets your **rank**, and your rank unlocks primary weapons for your [[classes|class]].

XP can go negative, which drops you to *Rankless Dog*.

## Ranks

{{table:ranks}}

## Earning XP

{{table:xp}}

Capturing the ghost is worth far more than a kill. The **capture reward** lifts each surviving player on the winning team to the next rank threshold. A Lieutenant gets +1 instead.[[src:src/game/shared/neo/neo_gamerules.cpp:1797-1825,4002-4028]]

XP doesn't change while the game is paused.[[src:src/game/shared/neo/neo_gamerules.cpp:4180-4185]]

## Unlocks by class

A weapon is available once your XP reaches its threshold.[[src:src/game/shared/neo/neo_weapon_loadout.cpp:28-109]]

{{table:loadouts}}

Recon also gets a [[detpack|detpack]] from 4 XP.[[src:src/game/server/neo/neo_player.cpp:3408-3417]]

??? note "Technical details"
    Builds with `INCLUDE_WEP_PBK` add the [[pbk56|PBK56]] to Support at 20 XP.

## Changing loadout

You have **25 seconds** after spawning to change your loadout. Firing or dropping a weapon closes the window early. During idle, warmup and countdown there's no limit.[[src:src/game/server/neo/neo_player.cpp:3485-3496]]

## For server admins

- `sv_neo_cap_reward` replaces the capture reward with a flat amount. `sv_neo_cap_reward_dead` extends it to dead players.
- `sv_neo_detpack_xp_limit` (default 4) sets the XP Recon needs for a detpack.[[src:src/game/server/neo/neo_player.cpp:3408-3417]]
- `sv_neo_time_alive_until_cant_change_loadout` sets the 25-second window for changing loadout.[[src:src/game/server/neo/neo_player.cpp:3485-3496]]
