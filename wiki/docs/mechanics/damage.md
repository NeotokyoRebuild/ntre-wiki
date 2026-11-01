---
description: "How bullet damage, hit locations, wall penetration, accuracy and explosions work"
---

# Damage & penetration

**Damage** in NT;RE is simple. A bullet does its weapon's damage, scaled by where it hits, and only loses damage when it passes through a wall.

There's **no armour**, **no headshot bonus** and **no falloff over distance**.

## How damage works

Every bullet's damage is scaled by ×1.485, then by the [[#hit-locations|hit location]].[[src:src/game/shared/neo/neo_gamerules.cpp:53; src/game/server/player.cpp:1004-1027]]

- **Range doesn't matter.** A bullet does the same damage at any distance until it hits something.[[src:src/game/shared/baseentity_shared.cpp:2003-2032]]
- **There's no armour.** Classes differ only in how much health they have.[[src:src/game/shared/neo/neo_player_shared.h:229-234]]
- **Fractions add up.** Each hit takes whole HP only. The leftover fraction is saved for each attacker, and taken once it reaches 1.[[src:src/game/server/neo/neo_player.cpp:3320-3330]]

??? note "Technical details"
    - `damage = weapon damage × 1.485 × hit-location multiplier [× penetration loss]`[[src:src/game/shared/neo/neo_gamerules.cpp:53; src/game/server/player.cpp:1004-1027]]
    - The 1.485 is `sv_neo_wep_dmg_modifier`, applied to every bullet. Explosives use `sv_neo_exp_dmg_modifier`, also 1.485.[[src:src/game/shared/neo/neo_gamerules.cpp:54]]
    - Maximum health is 100 for Recon, 120 for Assault and 225 for Support.[[src:src/game/shared/neo/neo_player_shared.h:229-234]]

## Hit locations

{{table:hitgroups}}

!!! info "No headshot bonus"
    A headshot does exactly as much damage as a chest shot. NT;RE sets the head multiplier to 1.0, where Half-Life 2 uses 2.0.

## Penetration

Bullets can go **through walls**. Every gun has a **penetration** value, and every surface has a value for how easy it is to shoot through. Thinner walls, and surfaces like glass, are easier to get through.[[src:src/game/shared/baseentity_shared.cpp:2336-2340]]

- A bullet that goes through keeps at least a quarter of its damage.[[src:src/game/shared/baseentity_shared.cpp:2366]]
- It can carry on through more walls with the penetration it has left.[[src:src/game/shared/baseentity_shared.cpp:2369]]
- Bullets **never pass through players**.[[src:src/game/shared/baseentity_shared.cpp:2264-2270]]
- Shotgun pellets (buckshot) never go through anything. The [[supa-7|Supa-7]] slug does.

In the table, a **higher** value means the surface is **easier** to shoot through. Dirt and sand (0.2) are the hardest; glass (0.9) is easy.

{{table:penetration}}

??? note "Technical details"
    - When a bullet hits a surface, the game measures how thick it is, up to 12 units, and divides that by the surface's value. If the result is no more than the bullet's remaining penetration, the bullet goes through.[[src:src/game/shared/baseentity_shared.cpp:2336-2340]]
    - Damage after the wall is `damage × max(0.25, 1 − used ÷ penetration)`, so a bullet keeps at least 25% of its damage.[[src:src/game/shared/baseentity_shared.cpp:2366]]
    - The penetration used is subtracted, and the bullet carries on with what's left.[[src:src/game/shared/baseentity_shared.cpp:2369]]
    - Buckshot has penetration 0.
    - The code calls the surface table `PENETRATION_RESISTANCE`, but its values work as a divisor, so a higher number means less resistance.

## Accuracy

Your shots spread wider when you fire, jump, or move without aiming, and tighten again when you stop. One shot pushes the spread most of the way to its maximum, so tap-firing and crouching matter.

{{table:accuracy}}

!!! warning "Unconfirmed: extra recoil on long bursts"
    The [[srs|SRS]] and [[zr68-l|ZR68-L]] also add up to 1 degree of extra vertical recoil after 10 shots in a row. This comes from reading the code and hasn't been tested in play.[[src:src/game/shared/neo/neo_shot_manipulator.cpp:63-147]]

??? note "Technical details"
    Each weapon has a minimum and maximum spread cone, one pair for hip fire and one for aiming. The current cone sits between them according to the **accuracy penalty**, from 0 to 1.[[src:src/game/shared/neo/weapons/weapon_neobasecombatweapon.cpp:854-879]]

## Explosions

Explosions do full damage at the centre, falling evenly to zero at the edge of their radius.[[src:src/game/shared/gamerules.cpp:376,519-520]]

{{table:explosives}}

## Team damage

Friendly fire is **on** by default, so you can hurt your teammates.[[src:src/game/shared/gamevars_shared.cpp:46-55]]

For the first **7 seconds** of a live round, it backfires. Your teammate takes no damage, and you take double what you dealt. If that kills you, you can't respawn that round.[[src:src/game/shared/neo/neo_gamerules.cpp:141-148; src/game/server/neo/neo_player.cpp:3332-3357]]

## For server admins

- `sv_neo_wep_dmg_modifier` (1.485) scales all bullet damage.[[src:src/game/shared/neo/neo_gamerules.cpp:53; src/game/server/player.cpp:1004-1027]] `sv_neo_exp_dmg_modifier` (also 1.485) does the same for explosives.[[src:src/game/shared/neo/neo_gamerules.cpp:54]]
- `sv_neo_hitboxgroup_pen 1` (default 0) changes how limb hits count. A shot that hits an arm or leg is traced again to see whether it would also have hit the head, chest or stomach behind it, and uses that multiplier instead.[[src:src/game/shared/neo/neo_player_shared.cpp:858,902-924]]
- `mp_friendlyfire 1` (the default) turns friendly fire on.[[src:src/game/shared/gamevars_shared.cpp:46-55]]
