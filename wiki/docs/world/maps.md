---
description: "The official NT;RE map list"
---

# Maps

The official map list includes:

- 24 for [[capture-the-ghost|Capture the Ghost]]
- 1 for [[team-deathmatch|Team Deathmatch]]
- 2 tutorials
- 2 menu backgrounds

!!! info "Prototype"
    Each map would get its own page, with an overhead layout, ghost spawns, capture zones and callouts. That needs someone to inspect the map files, which hasn't been done yet.

## Official maps

{{table:maps}}

## Other map files

The [neoAssets](https://github.com/NeotokyoRebuild/neoAssets) repository (commit `467c146`) has every official map, plus two that aren't on the official list:

- `ntre_apparatus_dm`: a [[deathmatch|Deathmatch]] map. It has its own soundscape file in the main repository.
- `devbox`: a development test map.

!!! warning "Unconfirmed: original NEOTOKYO maps"
    The game also loads content from the original NEOTOKYO, so its `nt_*` maps may work. Which game mode they run in hasn't been checked. A map without a game-config entity falls back to Free Roam.[[src:src/game/shared/neo/neo_gamerules.cpp:1092]]
