---
description: "Light scout class: fastest, longest cloak, most fragile"
---

# Recon

{{infobox:class:recon}}

**Recon** is the scout. It's the fastest class, with the longest [[thermoptic-camouflage|cloak]] and a super jump.

The trade-off is health: Recon has the least of the three main classes, and the fewest primary weapons to choose from.

## Strengths and weaknesses

- **Fastest.** Runs at {{stat:player:classes.recon.stats.run_speed}} units per second and sprints at {{stat:player:classes.recon.stats.sprint_speed}}. Assault manages {{stat:player:classes.assault.stats.run_speed}} and {{stat:player:classes.assault.stats.sprint_speed}}.
- **Sprints for free.** Sprinting costs no [[aux-power|AUX]], and AUX keeps recharging while you run.[[src:src/game/server/hl2/hl2_player.cpp:424-429,2056-2062]] You only spend AUX on the super jump.
- **Lands cleanly.** Other classes slow down for a moment after landing a jump. Recon doesn't.[[src:src/game/server/neo/neo_player.cpp:889-898]]
- **Jumps highest.** 54 units, half again the normal height.[[src:src/game/shared/gamemovement.cpp:2645-2656]]
- **Fragile.** 100 HP, the lowest of any class.

## Super jump

Hold <kbd>Sprint</kbd>, then press <kbd>Jump</kbd> while moving forward or backward. You leap forward as well as up. It costs **45 AUX**.[[src:src/game/server/neo/neo_player.cpp:1144-1155; src/game/shared/neo/neo_player_shared.h:178]]

It only works when:[[src:src/game/shared/neo/neo_player_shared.cpp:942-974]]

- you're sprinting on the ground, and not wading
- you're not carrying the [[ghost|ghost]]
- you have at least 45 AUX

Look straight ahead when you jump. Looking up or down makes the leap shorter.[[src:src/game/server/neo/neo_player.cpp:1568-1571]]

!!! warning "Unconfirmed: strafing wastes the jump"
    Holding only a strafe key seems to spend the 45 AUX without the forward leap. Strafing while holding forward seems to shorten it. This comes from reading the code and hasn't been tested in play.[[src:src/game/server/neo/neo_player.cpp:1148-1154,1565-1584]]

??? note "Technical details"
    - The leap adds your current maximum speed on top of a normal jump.[[src:src/game/server/neo/neo_player.cpp:1144-1155]]
    - It follows your view direction with the vertical part removed but not renormalised, so it shrinks by the cosine of your pitch.[[src:src/game/server/neo/neo_player.cpp:1568-1571]]
    - The 45 AUX is taken whenever the conditions above pass, but the boost only applies if exactly one of forward or back is held. With a strafe key held alongside, it's scaled by ×0.707.[[src:src/game/server/neo/neo_player.cpp:1148-1154,1565-1584]]

## Thermoptic camouflage

Recon's cloak lasts **13 seconds**, the longest in the game, and refills from empty in about 24 seconds. Assault's lasts 8.[[src:src/game/server/neo/neo_player.cpp:3780-3844]]

See [[thermoptic-camouflage|Thermoptic camouflage]] for what gives a cloaked player away.

## Night vision

Recon gets [[vision-modes#night-vision|night vision]]. It brightens the whole screen but doesn't pick anything out.

## Loadout

You always spawn with a [[knife|knife]] and a [[milso|MilSO]] pistol. From Corporal (4 XP) you also get a [[detpack|detpack]].[[src:src/game/server/neo/neo_player.cpp:3408-3417,3452-3457]]

Your primary weapon depends on your rank:

{{table:loadout:recon}}

## Hitbox

Recon is the smallest target: 64 units tall standing and 46 crouched. Support is 70 and 59.[[src:src/game/shared/shareddefs.h:88-90; src/game/shared/neo/neo_gamerules.cpp:388-394]]

??? note "Technical details"
    Eye height is 57 units for Recon and 60 for Support.[[src:src/game/shared/shareddefs.h:88-90; src/game/shared/neo/neo_gamerules.cpp:388-394]]
