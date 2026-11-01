---
description: "The three classes you can pick, and how they compare"
---

# Classes

Every player in NT;RE picks one of three classes: **[[recon|Recon]]**, **[[assault|Assault]]** or **[[support|Support]]**. Your class sets your health, speed and vision mode, whether you can cloak, and which primary weapons you can choose at each [[loadouts|rank]].

The two teams, [[factions|Jinrai and NSF]], play the same. They differ only in player models, HUD colour and which spawn they start from.

## Comparison

{{table:classes}}

<div class="grid cards" markdown>

-   **[[recon|Recon]]**

    Fast scout with the longest cloak, a super jump and free sprinting. Fragile.

    <span class="card-stat">100 HP · 270 sprint · 13 s camo</span>

-   **[[assault|Assault]]**

    The all-rounder. Motion vision, a short cloak and the widest choice of weapons.

    <span class="card-stat">120 HP · 256 sprint · 8 s camo</span>

-   **[[support|Support]]**

    The heavy, with the most health by far, thermal vision and machine guns. Can't sprint or cloak.

    <span class="card-stat">225 HP · no sprint · thermal</span>

</div>

## Choosing and changing class

A class change takes effect straight away when:[[src:src/game/server/neo/neo_player.cpp:250-281]]

- you're dead
- it's the freeze before the round, and you haven't fired or dropped a weapon
- it's warmup
- you're playing Deathmatch or Team Deathmatch and spawned less than 10 seconds ago

Otherwise the change waits until your next spawn.

Servers can limit or ban classes. If the class you ask for is full, you get the first class that isn't.[[src:src/game/shared/neo/neo_gamerules.cpp:60-62; src/game/server/team.cpp:393-454]]

## Shared rules

- **No armour.** Health is all you have. No class takes reduced damage.[[src:src/game/server/player.cpp:196-201]]
- **Your weapon sets your speed.** Every weapon scales your class speed by ×0.675–1.0. See [[movement#weapon-speed-scale|Movement]].
- **A knife backstab kills any class.** It does exactly 226 damage, one more than Support's maximum health.[[src:src/game/shared/neo/weapons/weapon_knife.cpp:309-320]]
- **No prone.** You can stand, crouch and lean, and that's all.

## For server admins

`sv_neo_class_limit_recon`, `sv_neo_class_limit_assault` and `sv_neo_class_limit_support` cap each class. The default, `-1`, means no limit, and `0` bans the class.[[src:src/game/shared/neo/neo_gamerules.cpp:60-62; src/game/server/team.cpp:393-454]]
