---
description: "Jinrai and the NSF"
---

# Factions

NT;RE matches are fought between two teams: <b class="team-jinrai">Jinrai</b> and the <b class="team-nsf">NSF</b>. They **play exactly the same**. No health, speed, AUX, cloak or vision value differs between them.

The only differences are how they look and which side they spawn on.

|   | <span class="team-jinrai">Jinrai</span> | <span class="team-nsf">NSF</span> |
| --- | --- | --- |
| Team index | 2[[src:src/game/shared/neo/neo_player_shared.h:400-403]] | 3 |
| HUD colour | <span class="team-jinrai">■</span> `154 255 154`[[src:src/game/shared/neo/neo_player_shared.h:253-258]] | <span class="team-nsf">■</span> `154 205 255` |
| Recon model | `jinrai_msf` | `nsf_gsf`[[src:src/game/server/neo/neo_model_manager.cpp:16-48]] |
| Assault model | `jinrai_mam` | `nsf_gam` |
| Support model | `jinrai_mhm` | `nsf_ghm` |
| Spawn, even rounds | Attacker | Defender[[src:src/game/server/neo/neo_player.cpp:3027,3042-3057]] |
| Spawn, odd rounds | Defender | Attacker |

Each class has **three skins** per team.[[src:src/game/shared/neo/neo_enums.h:3-9]]

Teams swap spawn sides and [[capture-the-ghost|capture zones]] every round, so neither keeps an advantage from the map.

!!! info "Lore"
    The factions' background and story belong here. This prototype covers gameplay only.
