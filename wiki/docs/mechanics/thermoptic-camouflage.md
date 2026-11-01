---
description: "The active cloak used by Recon and Assault"
---

# Thermoptic camouflage

{{infobox:cloak}}

**Thermoptic camouflage**, the cloak, makes you nearly invisible. Only [[recon|Recon]] and [[assault|Assault]] have it.[[src:src/game/server/neo/neo_player.cpp:1263-1266,3832-3844]]

The cloak has its own battery, so it never competes with sprinting or jumping for [[aux-power|AUX]].

## Battery

A full battery lasts 13 seconds for Recon and 8 seconds for Assault. It only recharges while the cloak is off.

{{table:cloak}}

??? note "Technical details"
    The battery drains 1 unit per second, taken in whole-second steps. The cloak switches off when the battery drops to 0.1.[[src:src/game/server/neo/neo_player.cpp:1102-1133]]

## What gives you away

The cloak works best when you stand still. These give you away, worst first:

- **Motion vision.** [[assault|Assault]] players see anything that moves highlighted, cloaked or not.[[src:src/game/client/c_baseanimating.cpp:3301-3329]]
- **Moving.** The faster you move, the more you shimmer. Stand still and the shimmer fades in about a second.[[src:src/game/client/neo/c_neo_player.cpp:1213-1224]]
- **Switching it on.** You flash blue for half a second, and players nearby hear it.[[src:src/game/server/neo/neo_player.cpp:1173-1255]]
- **Firing.** An unsuppressed weapon makes you flash. Suppressed weapons don't.[[src:src/game/shared/neo/weapons/weapon_neobasecombatweapon.cpp:1011-1019]]

[[game-modes#bots|Bots]] also find you more easily for a moment after you cloak or fire an unsuppressed weapon.[[src:src/game/server/neo/neo_player.cpp:1220,2692-2697]]

In your favour: you cast **no shadow** while cloaked.[[src:src/game/client/neo/c_neo_player.cpp:698-708]]

### Against thermal vision

[[support|Support]] players see everyone glowing with heat, except cloaked players. You look normal to them, with no glow.[[src:src/game/client/neo/c_neo_player.cpp:622-646,686-696]]

??? note "Technical details"
    - Motion vision highlights any model moving faster than 0.5 units per second.[[src:src/game/client/c_baseanimating.cpp:3301-3329]]
    - Each cloaked player has a visibility value from 0 to 1 that sets how strong the shimmer and tint are. Moving at 20 units per second or less lowers it by 1.1 per second. Moving faster raises it by your speed × 0.004 per second: about 0.8 per second at a full 200-unit-per-second run.[[src:src/game/client/neo/c_neo_player.cpp:1213-1224; src/game/client/neo/material_proxies/neo_matproxy_thermoptic.cpp:47-99]]
    - The activation flash is a blue light with a 96-unit radius.[[src:src/game/server/neo/neo_player.cpp:1173-1255]] The firing flash lasts 0.1 seconds.[[src:src/game/shared/neo/weapons/weapon_neobasecombatweapon.cpp:1011-1019]]

## What doesn't break it

Taking damage, firing and picking up the [[ghost|ghost]] don't switch the cloak off. Only four things do: the battery running out, switching it off yourself, dying and respawning.[[src:src/game/server/neo/neo_player.cpp:1121-1126,1257-1283]]

## For server admins

`sv_neo_infinite_cloak` is a cheat that stops the battery draining.[[src:src/game/server/neo/neo_player.cpp:227,3803-3806]]
