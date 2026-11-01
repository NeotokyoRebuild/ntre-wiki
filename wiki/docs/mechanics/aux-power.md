---
description: "The energy bar behind sprinting and the Recon super jump"
---

# AUX power

{{infobox:aux}}

**AUX power** is the energy bar on your HUD. In NT;RE it powers only two things: **sprinting** and the [[recon#super-jump|Recon super jump]].

[[thermoptic-camouflage|Thermoptic camouflage]] has its own separate battery, and [[vision-modes|vision modes]] are free.[[src:src/game/client/hl2/c_hl2_playerlocaldata.h:34; src/game/server/neo/neo_player.cpp:3775-3778]]

## Regeneration by class

AUX starts refilling half a second after you stop using it.[[src:src/game/server/hl2/hl2_player.cpp:2259,2272-2277]] Recon keeps refilling even while it sprints. Support never refills, and can't sprint.

{{table:aux-regen}}

## Sprint costs

- Sprinting drains 5 AUX per second, but only while you're moving. Holding sprint while standing still costs nothing.[[src:src/game/server/hl2/hl2_player.cpp:2040-2062]]
- Each time a sprint ends, you lose an extra **0.5 AUX**. Tapping sprint on and off costs more than holding it.[[src:src/game/server/hl2/hl2_player.cpp:2215-2228]]
- **Recon is exempt** from both. Its sprint drains nothing and costs nothing to stop.

!!! warning "Unverified: Recon's refill delay"
    For Recon, ending a sprint doesn't restart the half-second delay before AUX refills. The code returns early, before it updates the timer.[[src:src/game/server/hl2/hl2_player.cpp:2237-2239]] Whether it makes a visible difference in play hasn't been confirmed.

??? note "Technical details"
    Only horizontal movement counts towards the sprint drain.[[src:src/game/server/hl2/hl2_player.cpp:2040-2062]]

## For server admins

- `sv_infinite_aux_power` (default `0`, cheat) disables AUX drain.[[src:src/game/server/hl2/hl2_player.cpp:112-113]]
