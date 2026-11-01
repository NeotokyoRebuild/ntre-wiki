---
description: "Speeds, sprinting, jumping, leaning and fall damage"
---

# Movement

How fast you move depends on your **class**, the **weapon in your hands**, your **stance**, and whether you're **sprinting** or **aiming**.

Speeds are in Hammer units per second. The base is {{stat:player:movement.base_speed}} units per second, which is Recon's run speed.

## What sets your speed

Your class sets your starting speed, and these change it:[[src:src/game/server/neo/neo_player.cpp:844-900]]

- **Weapon in hand.** Each weapon slows you by its own amount. See [[#weapon-speed-scale|below]].
- **Crouching or walking** each slow you by a quarter. Do both and you move at a little over half speed.
- **Sprinting** speeds you up: by 35% for Recon and 60% for Assault. Support can't sprint.
- **Aiming down sights** cuts your speed to 60%.
- **Moving backwards** on the ground slows you by a further quarter.[[src:src/game/shared/gamemovement.cpp:2013-2016]]
- **After a jump**, every class except Recon is slowed for just over a second, most of all on landing.

However slow you get, you never drop below 55 units per second.

??? note "Technical details"
    Each tick, the game recomputes your maximum speed in this order:[[src:src/game/server/neo/neo_player.cpp:844-900]]

    1. Start from the **class run speed**: Recon 200, everyone else 160.
    1. Multiply by the **active weapon's speed scale** (0.675–1.0, see the table below).
    1. **Crouching**: ×0.75. **Walking**: ×0.75. The two stack, so a crouch-walk is ×0.5625.
    1. **Sprinting**: ×1.35 for Recon, ×1.6 for Assault. Support can't sprint.
    1. **Aiming down sights**: ×0.6.
    1. Never below **55 units per second**.
    1. For 1.15 seconds after a jump, every class except Recon is slowed further. The penalty is strongest on landing and fades over that time, with a floor of 75 units per second.

    Moving backwards on the ground is scaled by a further ×0.75.[[src:src/game/shared/gamemovement.cpp:2013-2016]]

### Class speeds

{{table:classes}}

## Weapon speed scale

The weapon in your hands slows you down by a fixed amount. Only the weapon you're holding counts, so switching to your pistol or knife is the standard way to move faster.

{{table:weapon-speed}}

## Sprinting

- Sprinting uses 5 [[aux-power|AUX]] per second, and only while you're actually moving. Recon sprints for free.[[src:src/game/server/hl2/hl2_player.cpp:447-448,2040-2062]]
- You need at least 2 AUX to start.[[src:src/game/shared/neo/neo_player_shared.h:181]]
- You can't aim while sprinting, and you can't sprint while carrying the [[ghost|ghost]].[[src:src/game/shared/neo/neo_player_shared.cpp:476-479; src/game/server/neo/neo_player.cpp:3729-3734]]

## Jumping

A normal jump is 36 units high. Recon jumps 54 units.[[src:src/game/shared/gamemovement.cpp:2645-2656]] Recon's [[recon#super-jump|super jump]] also leaps forward.

Crouch-jumping works as it does in standard Source games. NT;RE adds no bonus of its own.[[src:src/game/shared/gamemovement.cpp:2663-2678]]

??? note "Technical details"
    Recon jumps 1.5× the default height (54 units).[[src:src/game/shared/gamemovement.cpp:2645-2656]]

### Air control

By default you lose no speed in the air. The [[ghost|ghost]] carrier is the exception: they lose any speed above their normal run speed while airborne. That stops them bunny-hopping the objective across the map.[[src:src/game/shared/gamemovement.cpp:1724-1770]]

## Leaning

You can lean while you're alive, on the ground and not sprinting. Pressing both lean keys cancels the lean.[[src:src/game/server/neo/neo_player.cpp:826-842]]

Leans are **asymmetric**, to match the original NEOTOKYO: 7.5 units to the left and 15 to the right. A full lean takes 0.2 seconds.[[src:src/game/shared/neo/neo_predicted_viewmodel.cpp:146-151]] If there's no room, the lean is shortened.

??? note "Technical details"
    A full lean also rolls the camera 20 degrees and lowers your eyes by 2 units.[[src:src/game/shared/neo/neo_predicted_viewmodel.cpp:146-151]]

## Footsteps

Footsteps start at 50 units per second.

While **walking or aiming**, you make no footstep sounds as long as you stay at or below 70% of your class's run speed. When crouched, it's 70% of your crouch speed.[[src:src/game/shared/neo/neo_player_shared.cpp:384-404]]

## Fall damage

Falls hurt once you land faster than 580 units per second. Even a fall at Source's nominal "fatal" speed of 1024 units per second does only about 25 damage.[[src:src/game/shared/neo/neo_gamerules.cpp:4274-4287; src/game/shared/shareddefs.h:465-472]]

Damage keeps rising steadily with speed above that, with no cap.

??? note "Technical details"
    Damage is `(speed − 580) × 100 / 444 × 0.25`, about 0.056 HP for every unit per second over the limit. It's linear and uncapped.[[src:src/game/shared/neo/neo_gamerules.cpp:4274-4287; src/game/shared/shareddefs.h:465-472]]

## For server admins

- `sv_neo_airfriction` sets how much speed above run speed is lost in the air. The default, 0, loses nothing.[[src:src/game/shared/gamemovement.cpp:1724-1770]]
- The ghost carrier uses `sv_neo_airfriction_objective 0.5` instead.[[src:src/game/shared/gamemovement.cpp:1724-1770]]
- `sv_neo_falldmg_scale` is the 0.25 in the fall damage formula. It's why a fall at 1024 units per second does only about 25 damage.[[src:src/game/shared/neo/neo_gamerules.cpp:4274-4287; src/game/shared/shareddefs.h:465-472]]
