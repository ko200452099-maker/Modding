# ModLoader — Deep Dive

**Repo:** `ko200452099-maker/Modding`  
**Branch:** `arena/01a08a4d-modding`  
**Files:**
- `ModLoader.csa` — 480,326 bytes, 29,937 lines, GTA V Script Assembly (CSA/CSC)
- `ModLoader_Statics.c` — 27 statics (colors, flags, scroll settings)

## What is it?
**ModLoader by Tomás (TomásPintos22)** — A *ModLoader / Menu Loader* for GTA V (PS3 / FiveM-era `*.csc` / `*.xsc`).

It doesn't do one mod → it **loads 87 other mod menus/scripts on demand**, acting as a hub. Detected via strings:

```
IncludeStaticFile ModLoader_Statics.c
Function 0 2 0
CallNative "GET_THIS_SCRIPT_NAME" ...
CallNative "UNK_029D3841" // anti-duplicate / script hash check
CallNative "NETWORK_SET_SCRIPT_IS_SAFE_FOR_NETWORK_GAME"
```

Main loop (`:Label_3`): `WAIT(0)` → `NETWORK_SET_THIS_SCRIPT_IS_NETWORK_SCRIPT` → state machine over `Static_130` (menu state, ~60 states).

## The 87 Loadable Menus

Parsed via pattern `PushString "Nice Name" + PushString "script_name" + PushS stackSize + Call @Label_1835`:

| Category | Example |
|----------|---------|
| **Mains / Ultra** | APP II Intense (`rock_menu2`), Inimitable v6.52, ArabicGuy Ultra v2.6, insanity's Ultra, Brodator, Project CL, Revolution |
| **Console Trainer / Classics** | Console Trainer V, K&K Dark Horse, Eternal Darkness v4.6.5, MoonShine v3, Scorpion |
| **Recovery / Stats** | James Reborn Recovery v5.2.3 (`JRrecovery`), 2much4u Recovery, Stat Editor (`CR_Stat`), TattooEditor, GarageEditor |
| **Protections** | Black Protect Saint v5.0, Serendipity, LimoProtex, PrivateProtections |
| **Freezers (grief)** | Freeze V3ND3TT4, FreezeMenuv1, frz2, FreezeTP, etc. (8 variants) |
| **Vehicles / Maps / Misc** | Erootiik Vehicle Spawner, Truck Simulator, North Yankton Menu, Bridge Beach Airport, Funny Car Loader, Heli Bomb, Rocket Car |

Full list extracted to `docs/menu_list.txt` (87 entries). Stack sizes 128–6304 indicate how much script memory each loader reserves.

Loader function `:Label_1835` (6 params: display name, script name, stack, ...):
```c
if (!DOES_SCRIPT_EXIST(script)) {
  print(script + ".csc Not Found!" / ".xsc Not Found!")
} else if (script_not_already_running) {
  START_NEW_SCRIPT(script, stackSize)
  SET_SCRIPT_AS_NO_LONGER_NEEDED
}
```

## Menu Structure (from disassembly)

- **Main:** Mains Mods → Mods Menus / Recovery's / Protections / Freezers / Cars / Mapas / Miscellaneous / Settings + Discord `https://discord.gg/3QMuwbP`
- **Settings:** Language (Spanish/English) → `Static_70`, Color editors (`GET_HUD_COLOUR` + 255s), Draw Rect/Sprite tuning (`0.2788,0.4939,0.3864` = safezone math via `:Label_2`)
- **Credits (`:Label_72`):** Thanks to Louay, Santo Oscuro, UnrestrainedGTA, NotYourDope, IvoAlqaeda, Hackardo, FranCangel, Pablo Modz YT, Erootiik + Instagram `TomasPintos22`
- **Languages:** Entire menu is bilingual — every `PushString "Spanish" / "English"` pair goes through `@Label_163` (language selector = `StaticGet1 70?`).

## Statics File (`ModLoader_Statics.c`)

27 tunable globals — mostly **RGBA colors**:

```c
Static_175 = 10; // HUD color id?
Static_203 = 1;  // toggle
Static_210 = 252; // R
Static_211 = 255; // G ...
Static_215 = 4;  // color preset
...
Static_257 = 1;  // enabled
Static_258 = 250; // scroll bar R
Static_262 = 1;
Static_268 = 255; // selection color
```

Changing these = re-skin menu without recompiling CSA. `0.2788/0.4939/0.3864` in CSA = safe-zone scaling.

## Natives Used (311 distinct)

Rendering: `DRAW_RECT`, `DRAW_SPRITE`, `DRAW_SCALEFORM_MOVIE`, `BEGIN_TEXT_COMMAND_*`, `SET_TEXT_*`, `GET_HUD_COLOUR`
Script Control: `REQUEST_SCRIPT`, `HAS_SCRIPT_LOADED`, `START_NEW_SCRIPT`, `TERMINATE_ALL_SCRIPTS_WITH_THIS_NAME`, `NETWORK_SET_SCRIPT_IS_SAFE_FOR_NETWORK_GAME`
Entity/World: `CREATE_VEHICLE`, `SET_ENTITY_COORDS`, `GET_ENTITY_COORDS`, `APPLY_FORCE_TO_ENTITY`, `CLEAR_AREA_OF_*`
Protections/Freezes: `CLEAR_BIT/SET_BIT/IS_BIT_SET` on bitsets `pStatic1 71/72`, `FREEZE_ENTITY_POSITION`, `SET_ENTITY_INVINCIBLE`, etc.
Input: `IS_DISABLED_CONTROL_PRESSED` (R1+L1+X = suicide hotkey shown in strings)

## Safety & Ethics Note

> This is a **GTA Online mod menu loader**. Using Freezers / Protections / Recovery in online risks bans, corruption, griefing. Analysis here is **for education, offline / FiveM research, and single-player modding preservation only**. Do not use in GTA Online.

Many entries (ArabicGuy Ultra, Brodator, Revolution, etc.) are known historically as online grief tools — included here only as historical documentation.

## What You Can Do Next (pick one)

1. **Browse Interactive** — I can spin up a preview UI that lets you search all 87 menus, see original Spanish/English strings, and jump to their Label in CSA.
2. **Decompile / Reformat** — Pretty-print the 29k-line CSA into pseudo-C with labels resolved, or export to JSON for tooling.
3. **Customize** — Edit `ModLoader_Statics.c` colors, remove freezer/recovery categories, or add your own `PushString "My Mod" / "MyScript"` loader entry.
4. **Safe Offline Fork** — Strip online-grief natives (`APPLY_FORCE_TO_ENTITY`, `FreezeTP`, etc.) and make a single-player-only version.
5. **Explain CSA Bytecode** — Deep dive on how `Function`, `Call`, `StaticGet/Set`, `fPush`, `JumpTrue` map to GTA V script VM.
6. **Extract Textures/Assets** — List `chaos_textures_*`, `TPBackground*`, `commonmenu` dicts and generate preview PNGs.

---
*Generated 2026-09-10 — total: 273 Functions, 2456 Labels, 1618 CallNative, 1802 unique strings. Discord: `3QMuwbP`*
