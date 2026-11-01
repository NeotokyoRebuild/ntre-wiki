---
description: "Heavy class: 225 HP, thermal vision, machine guns; no sprint, no cloak"
---

# Support

{{infobox:class:support}}

**Support** is the heavy class. With **225 HP** it can take almost twice the punishment of an Assault. It can't sprint and can't cloak.

[[vision-modes#thermal-vision|Thermal vision]] shows uncloaked players as hot silhouettes, even through smoke. Support is also the only class that can carry the [[pz252|PZ252]] machine gun.

## Strengths and weaknesses

- **Most health.** 225, the most of any class you can pick, with no armour on top.[[src:src/game/shared/neo/neo_player_shared.h:229-232]] Only a knife backstab (226 damage) is guaranteed to kill you outright.[[src:src/game/shared/neo/weapons/weapon_knife.cpp:309-320]]
- **Sees through smoke.** Smoke isn't drawn while thermal vision is on.[[src:src/game/client/smoke_fog_overlay.cpp:145-156]]
- **Can't sprint.**[[src:src/game/server/neo/neo_player.cpp:3750-3755; src/game/shared/neo/neo_player_shared.h:40,61]]
- **No AUX and no cloak.** Support doesn't use AUX at all, and has no thermoptic camouflage.
- **Biggest target.** Standing, Support is 70 units tall, the largest of the classes you can pick.

??? note "Technical details"
    The code has a Support sprint speed of 216, but it's commented as reserved for future use.[[src:src/game/server/neo/neo_player.cpp:3750-3755; src/game/shared/neo/neo_player_shared.h:40,61]]

## Thermal vision and cloak

Thermal vision shows uncloaked players, NPCs and corpses as hot. **Cloaked players don't glow.** They look normal, with no heat highlight, so they don't stand out against the cold background the way you might expect.[[src:src/game/client/neo/c_neo_player.cpp:622-646,686-696]]

## Loadout

You always spawn with a [[knife|knife]], the [[kyla|Kyla]] revolver and a [[smoke-grenade|smoke grenade]].[[src:src/game/server/neo/neo_player.cpp:3464-3469]]

Your primary weapon depends on your rank:

{{table:loadout:support}}

??? note "Technical details"
    Builds compiled with `INCLUDE_WEP_PBK` add the [[pbk56|PBK56]] at 20 XP.
