---
description: "Night, motion and thermal vision"
---

# Vision modes

Every class has a **vision mode** you can switch on and off. Each class gets a different one.

Vision modes are free. They cost no [[aux-power|AUX]], have no time limit, and switch off when you die or respawn.[[src:src/game/server/neo/neo_player.cpp:728,1638]] You can toggle at most once every 0.1 seconds.[[src:src/game/shared/neo/neo_player_shared.cpp:797-801]]

| Mode | Classes | Highlights | Reveals cloak? |
| --- | --- | --- | --- |
| [[#night-vision\|Night vision]] | [[recon\|Recon]] | Nothing specific: brightens the whole scene | No |
| [[#motion-vision\|Motion vision]] | [[assault\|Assault]] | Any moving model | **Yes**, while the target moves |
| [[#thermal-vision\|Thermal vision]] | [[support\|Support]] | Uncloaked players, NPCs, bodies | No; also sees through smoke |

## Night vision

<figure class="infobox" style="width:260px"><div class="ib-image" style="border:0">Night vision screenshot</div></figure>

[[recon|Recon]] uses night vision. It's a screen filter only: it brightens everything, but doesn't draw any player or object differently.[[src:src/game/client/viewpostprocess.cpp:2341-2381]]

## Motion vision

<figure class="infobox" style="width:260px"><div class="ib-image" style="border:0">Motion vision screenshot</div></figure>

The [[assault|Assault]] uses motion vision. Anything that moves is highlighted, including players, physics props and **cloaked players**.[[src:src/game/client/c_baseanimating.cpp:3301-3329]] A target that stands completely still isn't highlighted.

??? note "Technical details"
    Along with the screen filter, any model moving faster than 0.5 units per second is drawn again with a highlight material.[[src:src/game/client/c_baseanimating.cpp:3301-3329]]

## Thermal vision

<figure class="infobox" style="width:260px"><div class="ib-image" style="border:0">Thermal vision screenshot</div></figure>

The [[support|Support]] uses thermal vision. Uncloaked players, NPCs and bodies show up hot, and you can see through [[smoke-grenade|smoke]].[[src:src/game/client/neo/c_neo_player.cpp:622-646; src/game/client/smoke_fog_overlay.cpp:145-156]]

Cloaked players **don't** show up hot. They look normal, which makes thermal a poor counter to [[thermoptic-camouflage|thermoptic camouflage]].[[src:src/game/client/neo/c_neo_player.cpp:686-696]]

??? note "Technical details"
    The bodies drawn hot are ragdolls and gibs. Thermal vision switches off the smoke screen overlay, which is how Support sees through smoke.[[src:src/game/client/neo/c_neo_player.cpp:622-646; src/game/client/smoke_fog_overlay.cpp:145-156]]
