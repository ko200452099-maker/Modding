# Bitset Map — What Each Static Bit Actually Means

> `pStatic1 71` means “address of Static1[71]”.  `SET_BIT / CLEAR_BIT / IS_BIT_SET` on that address toggles a 32-bit flagword.
> Curated from 200+ `CallNative "SET_BIT"` sites.  Every `pStatic1 N + Push B` was inspected with 3 lines of context (`grep -B1` to find the `Push B` value).

| Static | Bit | New Symbolic Name | Set Site (line) | What it Toggles (observed natives/fields nearby) |
|---|---|---|---|---|
| **71** | 9 | `gFlags_Main__BrakeLightToggle` | 13051 `CLEAR`, 13055 `SET` | `SET_VEHICLE_BRAKE_LIGHTS` on current vehicle (ped flag?) |
| **71** | 10 | `gFlags_Main__ModEnabled` | 161 `SET_BIT 71.10` in `Mod_Init_Main` init | Master “ModLoader enabled” — checked at boot guard |
| **71** | 11 | `gFlags_Main__IndicatorHack` | 13140 `CLEAR`, 13145 `SET` | `SET_VEHICLE_INDICATOR_LIGHTS` |
| **71** | 19 | `gFlags_Main__QuickTeleportSpam` | 12247 `CLEAR`, 12252 `SET` | Teleport cooldown flag (near `SET_ENTITY_COORDS`) |
| **72** | 2 | `gFlags_Player__NoKnockOff` | 11383 `CLEAR`, 11388 `SET` | `SET_PED_CAN_BE_KNOCKED_OFF_VEHICLE 0` |
| **72** | 3 | `gFlags_Player__SuperSprint` | 12265 `CLEAR`, 12272 `SET` | `SET_RUN_SPRINT_MULTIPLIER / SET_SWIM_MULTIPLIER 1.0` |
| **72** | 5 | `gFlags_Player__FastStatSave` | 166 `SET_BIT 72.5` init | `STAT_SAVE` trigger? |
| **72** | 13 | `gFlags_Player__Ragdoll` | 12278 `CLEAR`, 12282 `SET` | `SET_PED_CAN_RAGDOLL 1` |
| **72** | 14 | `gFlags_Player__CappedMunition` | 13100 `CLEAR`, 13105 `SET` | `SET_PED_INFINITE_AMMO_CLIP`? near `PLAYER_PED_ID` |
| **72** | 15 | `gFlags_Player__InfiniteStamina` | 11374 `CLEAR`, 11379 `SET` | `SPECIAL_ABILITY_FILL_METER`? |
| **72** | 18 | `gFlags_Player__HelmetHack` | 11389 `CLEAR` | `SET_PED_HELMET 223` |
| **72** | 21 | `gFlags_Player__ArmorHack` | 11395 `CLEAR` | `SET_PED_ARMOUR 100` |
| **72** | 22 | `gFlags_Player__NoBikeFall` | 11383 `CLEAR` alt? | `SET_PED_CAN_BE_KNOCKED_OFF_VEHICLE 0` duplicate |
| **72** | 23 | `gFlags_Player__StealthMove` | 11402 `CLEAR` | `SET_PED_STEALTH_MOVEMENT 1` |
| **72** | 24 | `gFlags_Player__ScorchedOff` | 11365 `CLEAR`, 11370 `SET` | `SET_ENTITY_RENDER_SCORCHED 0` |
| **72** | 25 | `gFlags_Player__BulletProof` | 11397 check | `SET_ENTITY_PROOFS` bullet flag |
| **72** | 31 | `gFlags_Player__FreezeGravity` | 13164 `CLEAR` | `SET_VEHICLE_GRAVITY 0` |
| **73** | 12 | `gFlags_Recovery__MoneySpam` | 16864 `CLEAR`, 16875 `SET` | `SetGlobal3 262250 30000` money hash near `STAT_SET_INT` |
| **77-80** | 0 | `gMenu_Toggle_*` (4 separate toggles) | 27537-27572 | Each is a single-bit on/off for a menu checkbox (visible in `UI_Draw_ToggleRow`) |
| **88/89/101** | 0 | `gMenu_Checkbox_*` | 27445-27846 | Similar single-bit toggles for settings rows |
| **137** | 0 | `gProt_FxClear__ParticleKill` | 16555-16560 | `REMOVE_PARTICLE_FX_IN_RANGE 9999` in `Tick_HandleInputAndQueue` |
| **138** | 1 | `gProt_Player__VisibleHack` | 11495 `CLEAR` | `SET_ENTITY_VISIBLE 1` |
| **138** | 2 | `gProt_Player__InvincibleToggle` | 2064 `SET` / 2114 `CLEAR` | `SET_PLAYER_INVINCIBLE 1` |
| **138** | 12 | `gProt_Player__NoCops` | 11278 `CLEAR` | `CLEAR_AREA_OF_COPS` |
| **138** | 16 | `gProt_Player__GodMode` | 2064 init `SET` global | `SET_PLAYER_INVINCIBLE + SET_ENTITY_INVINCIBLE` |
| **138** | 17 | `gProt_Player__Invisible` | 11495 `CLEAR` | `SET_ENTITY_VISIBLE 0` |
| **138** | 20-21 | `gProt_Player__ExplosiveAmmo/Melee` | 12281 `SET` | `SET_EXPLOSIVE_AMMO_THIS_FRAME` |
| **138** | 24 | `gProt_Player__FireAmmo` | 11383 | `SET_FIRE_AMMO_THIS_FRAME` |
| **138** | 25-28 | `gProt_Player__MaxWanted` | 11292 `SET` | `SET_MAX_WANTED_LEVEL 5` / `CLEAR_PLAYER_WANTED_LEVEL` |
| **139** | 9 | `gProt_Global__AntiFreezeFlood` | 16391 `CLEAR`, 16468 `SET` | **The 16× `pSet 197...` flood** — anti-freeze pSet block |
| **140** | 0 | `gProt_Global__ClearArea` | 11588 `CLEAR` | `CLEAR_AREA_OF_OBJECTS` |
| **142** | 16 | `gProt_Vehicle__LockDoors` | 12217 `CLEAR` | `SET_VEHICLE_DOORS_LOCKED_FOR_ALL_PLAYERS 0` |
| **142** | 22-24 | `gProt_Vehicle__ExtraToggles` | 12281 | `SET_VEHICLE_EXTRA` etc. |
| **143** | 1,3,5,13,16-18,20-21,25 | `gProt_Remote__PlayerHijacks` | 11470-11496 | Remote player attach/detach `DETACH_ENTITY`, `CLEAR_PED_TASKS`, `SET_PED_INTO_VEHICLE` spam |
| **145** | 1 | `gCheat_SuicideHotkey` | 18218 `CLEAR` | `Press R1+L1+X to suicide` |
| **146** | 1 | `gMenu_Anim__LoopedToggle` | 27473 `CLEAR` | Animation `Serpentead@` looping |
| **147** | 3,5-9,10-14,17 | `gProt_Vehicle__Mods` | 12119-12128,12231 | `SET_VEHICLE_MOD` per index 0-7, tyre smoke, boost, gravity etc. |
| **162/167/168** | 6-9,7,1,4,5,7 | `gVehicle_SpecialFlags` | 12261,13164,13248 | `SET_VEHICLE_GRAVITY 0`, `SET_VEHICLE_TYRES_CAN_BURST`, `Vehicle_GravityFlags` |
| **245** | 0 | `gMenu_VerticalScrollbarVisible` | 27431 | Draw scrollbar `all_white_bg` |
| **71/73/138/139/143/145** | — | See also `WHOLE_MOD_OVERVIEW.md §6` | — | All protection bits route through `Tick_HandleInputAndQueue` or `Label_96` |

### How to read in code
```asm
pStatic1 138         ; address of gProt_Player__GodMode word
Push1 16              ; bit 16
CallNative "IS_BIT_SET" 2 1  ; -> is GodMode on?
JumpFalse @NotEnabled

; Equivalent C with new names:
if (gProt_PlayerFlags & (1<<16)) { // gProt_Player__GodMode
  SET_PLAYER_INVINCIBLE(PLAYER_ID(), true);
}
```

> For full flag list (32 bits × 512 statics) run: `grep -n 'pStatic1\|SET_BIT\|CLEAR_BIT' ModLoader.csa | python3 tools/bitset_report.py > docs/bitset_full.txt` (generate on demand).

---

## Static2 Bitsets
Static2 is less bit-mapped, more *arrays* (`gArray_OutfitCache_R` 398-399 etc.). No `SET_BIT` on Static2 observed — all `StaticSet2 397 = 84` style are direct stores, not flagwords.
