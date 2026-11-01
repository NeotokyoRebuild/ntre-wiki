---
description: "Medium all-round class: motion vision, short cloak, widest arsenal"
---

# Assault

{{infobox:class:assault}}

**Assault** is the all-rounder. It has more health than Recon, a short [[thermoptic-camouflage|cloak]], and [[vision-modes#motion-vision|motion vision]] that picks out anything that moves.

It also has the widest choice of primary weapons in the game, from SMGs up to the [[srs|SRS]] sniper rifle and [[aa13|AA13]] auto-shotgun.

## Strengths and weaknesses

- **Biggest sprint boost.** Sprinting takes you from 160 to 256 units per second. Recon still sprints faster, at 270.[[src:src/game/shared/neo/neo_player_shared.h:34-39]]
- **Sprinting costs AUX.** A full bar lasts 20 seconds of sprinting, and it doesn't refill while you sprint.[[src:src/game/server/hl2/hl2_player.cpp:430-435,2040-2055,2215-2228]]
- **Slows on landing.** After a jump you're slowed for 1.15 seconds, like every class except Recon.

??? note "Technical details"
    - Assault sprints at ×1.6 its run speed. Recon sprints at ×1.35.[[src:src/game/shared/neo/neo_player_shared.h:34-39]]
    - Sprinting drains 5 AUX per second while you're moving. Each time you stop sprinting, another 0.5 AUX is taken.[[src:src/game/server/hl2/hl2_player.cpp:430-435,2040-2055,2215-2228]]

## Motion vision

Motion vision highlights anything that moves, and that includes **cloaked players**. A cloaked enemy who stands perfectly still disappears again.[[src:src/game/client/c_baseanimating.cpp:3301-3329]]

See [[vision-modes|Vision modes]].

??? note "Technical details"
    Any model moving faster than 0.5 units per second is drawn with an extra highlight pass.[[src:src/game/client/c_baseanimating.cpp:3301-3329]]

## Thermoptic camouflage

Assault's cloak lasts **8 seconds**, and takes 32 seconds to refill from empty.[[src:src/game/server/neo/neo_player.cpp:3780-3844]]

See [[thermoptic-camouflage|Thermoptic camouflage]] for what gives a cloaked player away.

??? note "Technical details"
    The cloak recharges at 0.25 per second.[[src:src/game/server/neo/neo_player.cpp:3780-3844]]

## Loadout

You always spawn with a [[knife|knife]], a [[tachi|Tachi]] pistol and a grenade.[[src:src/game/server/neo/neo_player.cpp:3458-3463]]

Your primary weapon depends on your rank:

{{table:loadout:assault}}
