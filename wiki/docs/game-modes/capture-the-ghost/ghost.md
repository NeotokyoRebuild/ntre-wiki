---
description: "The objective item in Capture the Ghost"
---

# The Ghost

{{infobox:ghost}}

The **ghost** is the objective in [[capture-the-ghost|Capture the Ghost]] (CTG). Whoever carries it can see every enemy within about 46 metres.

The catch: everyone else on the map can see where the carrier is.

## Picking it up

- It goes in the **primary slot**. You can't pick it up while holding a primary weapon, so drop yours first.[[src:src/game/server/neo/neo_player.cpp:2803-2807]]
- It can't shoot or aim.[[src:src/game/shared/neo/weapons/weapon_ghost.h:60-67]]
- Picking it up stops your sprint. You can't use the [[recon#super-jump|Recon super jump]] while you carry it.[[src:src/game/shared/neo/weapons/weapon_ghost.cpp:209-213; src/game/shared/neo/neo_player_shared.cpp:951-952]]

!!! warning "Unconfirmed"
    Whether a carrier can sprint again after picking it up is unclear. The client blocks it, but the server's check doesn't mention the ghost. This needs testing in game.

## Enemy beacons

Hold the ghost as your **active weapon**. After a few seconds of boot-up, it marks every living enemy within about 46 metres with a red beacon, through walls. Each beacon shows how far away that enemy is.[[src:src/game/shared/neo/neo_player_shared.cpp:60-64]]

Your teammates don't see the beacons. Spectators watching you do.[[src:src/game/client/neo/ui/neo_hud_ghost_beacons.cpp:99-152]]

The ghost also beeps faster the closer the nearest enemy gets.[[src:src/game/shared/neo/weapons/weapon_ghost.cpp:173-174]]

??? note "Technical details"
    - Boot-up takes 3.3 seconds. The beacons reach **45.72 metres (1800 units)**.[[src:src/game/shared/neo/neo_player_shared.cpp:60-64]]
    - The ghost beeps every `0.1 × distance in metres` seconds, between 1 and 3.5 seconds.[[src:src/game/shared/neo/weapons/weapon_ghost.cpp:173-174]]

## Being the carrier

Everyone else sees a pulsing marker on the ghost or its carrier. It's red to the enemy and your team colour to friendlies.[[src:src/game/client/neo/ui/neo_hud_ghost_marker.cpp:141-178]]

You can't bunny-hop the ghost across the map.[[src:src/game/shared/gamemovement.cpp:1725,1756]]

??? note "Technical details"
    The carrier gets the objective air friction, which stops bunny-hopping.[[src:src/game/shared/gamemovement.cpp:1725,1756]]

## Spawning and dropping

- One ghost spawns each round, at a random ghost spawn point.[[src:src/game/shared/neo/neo_gamerules.cpp:2057-2064]] In competitive play, rounds come in pairs from the same spawn, so each team gets the same start once.[[src:src/game/shared/neo/neo_gamerules.cpp:2065-2078]]
- It drops when the carrier dies or disconnects, or presses drop while holding it. A dropped ghost is never removed.[[src:src/game/server/neo/neo_player.cpp:2414; src/game/shared/neo/weapons/weapon_ghost.cpp:322]]
- If it's thrown or carried out of bounds, it goes back to the last spot where its last carrier stood on solid ground.[[src:src/game/server/neo/neo_ghost_boundary.cpp:80-185]]

## For server admins

`sv_neo_ghost_spawn_bias` pairs the ghost spawns as described above. It's on in competitive play.[[src:src/game/shared/neo/neo_gamerules.cpp:2065-2078]]
