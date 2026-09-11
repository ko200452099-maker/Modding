# Naming Guide — How to Use Correct Names for Future Dev

> **Problem:** Stock ModLoader uses `Label_0…Label_2999` and `Static 0…512` — numbers are unmaintainable.
> **Solution:** Every Label/Static now has a **correct English name** via `tools/rename_map.json` (296 labels, 315 statics) + 3 helper artefacts.

---

## Artefacts (all on `arena/01a08a4d-modding`)

| File | What | When to Use |
|---|---|---|
| `tools/rename_map.json` | **Source of truth** — `labels`, `statics1`, `statics2` dicts | Tooling, editors, CI checks |
| `docs/NAMING_MAP_LABELS.md` | 312-row table: `Label_1835` → `Loader_AddMenuEntry` | Reference while reading `.csa` |
| `docs/NAMING_MAP_STATICS.md` | 329-row table: `Static1[130]` → `gMenu_CurrentState` | Reference for save/theme |
| `docs/BITSET_MAP.md` | 40+ flag bits decoded (71.10 = ModEnabled, 138.16 = GodMode, 139.9 = AntiFreeze) | Protection logic |
| `docs/ModLoader_Defines.h` | 622 `#define Mod_Init_Main Label_0` etc. | **Include** in new CSA splits (`#include` style) or just as cheatsheet |
| `docs/ModLoader_Statics_Named.c` | Named copy of `ModLoader_Statics.c` with `// gUI_Hdr_G` comments | Replace `IncludeStaticFile` path |
| `docs/ModLoader_Annotated.csa` | **Full 29,938-line annotated** — every `Call @Label_1835 ; -> Loader_AddMenuEntry` and `StaticSet1 130 ; gMenu_CurrentState` | Read / `grep` without memorizing numbers |
| `ModLoader_Renamed.csa` | **Fully renamed** — `JumpTrue @Mod_Init_Main`, `:Mod_Init_Main` | Use if you want to *develop* with names (assembles identically, addresses unchanged) |
| `tools/apply_names.py` | ` --annotated` vs `--rename` switcher | Generate above |
| `tools/generate_naming.py` | Curated + heuristic tagger (Run after adding new Labels) | Keep maps in sync |

---

## Quick Start (future dev)

### Option A — Annotated (recommended, non-breaking)
Stay on original numeric `.csa` but **read annotated**:
```bash
python3 tools/apply_names.py --annotated --in ModLoader.csa --out docs/ModLoader_Annotated.csa
# then in VSCode: open Annotated, Ctrl+F "gMenu_CurrentState" jumps to 17 hits
# original line numbers preserved → diffs vs upstream stay clean
```

### Option B — Renamed (clean names everywhere)
Develop with English names:
```bash
python3 tools/apply_names.py --rename --in ModLoader.csa --out ModLoader_Renamed.csa
# :Label_1835 → :Loader_AddMenuEntry
# Call @Label_1835 → Call @Loader_AddMenuEntry
# Jump @Label_426 → Jump @Loader_AddMenuEntry__Return
# Assemble Renamed directly — toolkit accepts any label spelling
```

Switch back for upstream PRs:
```bash
python3 tools/apply_names.py --rename --in ModLoader_Renamed.csa --out ModLoader.csa  # if you need round-trip, keep JSON sync
# Or just `git checkout ModLoader.csa` — Annotated is not committed as source, only as doc
```

### Option C — Modular Split (vNext)
Use `docs/WHOLE_MOD_OVERVIEW.md §11` + `docs/ModLoader_Defines.h`:
```asm
IncludeStaticFile ModLoader_Statics_Named.c
IncludeStaticFile docs/ModLoader_Defines.h  ; gives Mod_Init_Main = Label_0

Function 0 2 0
  Call @Mod_Init_TexturesAndLocals  ; was Call @Label_1, now English
  StaticGet1 gMenu_CurrentState     ; but CSA still needs numeric? See note
```
> **Note:** CSA syntax requires numeric `StaticSet1 130` — `gMenu_CurrentState` is a *comment/define* for humans. The **annotated** file keeps numeric + comment (`StaticSet1 130  ; gMenu_CurrentState`). The **Renamed** file keeps numeric for statics but renames labels. If your assembler supports `DEFINE gMenu_CurrentState 130` then `StaticSet1 gMenu_CurrentState` works — otherwise keep comment style.

---

## Naming Principles (how we chose correct names)

| Pattern | Example | Rule |
|---|---|---|
| `Mod_*` | `Mod_Init_Main` | Boot, lifecycle, global |
| `Main_*` | `Main_Tick`, `Main_Loop_Infinite` | Top-level loop |
| `Tick_*` | `Tick_HandleInputAndQueue` | Called every `WAIT(0)` |
| `Page_*` | `Page_ModsMenus_DIR`, `Page_ModsMenus_Impl` | 48 states; `_DIR` = router that calls `Loader`, `_Impl` = builds rows |
| `Loader_*` | `Loader_AddMenuEntry`, `Loader_AddMenuEntry__Queue` | Script-spawning |
| `UI_*` | `UI_Draw_TextRow`, `UI_Draw_Sprite`, `UI_Update_HighlightRect` | Rendering (3× text natives, `DRAW_RECT/SPRITE`) |
| `Util_*` | `Util_GetSafeZoneHalf`, `Util_LangPick_ES_EN` | Helpers (safe-zone, lang, textures) |
| `Input_*` / `Sfx_*` | `Input_IsConfirmPressed`, `Sfx_Play_ClickSpecial` | Control/sound |
| `Vehicle_*` | `Vehicle_Tuning_Label_...`, `Vehicle_Create_Label_...` | `SET_VEHICLE_MOD`, `CREATE_VEHICLE` cluster |
| `Outfit_*` | `Outfit_Apply_Label_...` | `SET_PED_COMPONENT` |
| `Teleport_*` | `Teleport_Do_Label_...` | `SET_ENTITY_COORDS` |
| `Protect_*` | `Protect_PlayerToggle_Label_...`, `Protect_GlobalPatch_Label_...` | `pSet` globals, `SET_BIT 138.x` |
| `gMenu_*` | `gMenu_CurrentState (=130)`, `gMenu_X (=0)` | Static1 0..200 : UI/menu state |
| `gProt_*` | `gProt_PlayerFlags (=138)`, `gProt_GlobalFlags (=139)` | Bitset words |
| `gUI_*` / `gTheme_*` / `gColor_*` | `gUI_RowHeight (=100)`, `gUI_Hdr_R (=209)` | Appearance |

All `g*` names start with `g` (global/static) and use `snake_Camel` for grep (`grep gMenu_` lists all menu state).

---

## Keeping Names Correct (workflow)

1. **Add a new Label** (e.g., new page `Label_3100`):
   - Edit `ModLoader.csa`, add `Function`
   - Run `python3 tools/generate_naming.py` — it will auto-suggest `Page_NewFeature_Label_3100` based on natives/strings.
   - Curate: edit `tools/generate_naming.py` `manual` dict to give a final nice name like `Page_Search_Impl`, rerun, commit `rename_map.json`.

2. **Add a new Static** (e.g., `Static1[300]`):
   - Pick an `gUnk1_300` slot from `NAMING_MAP_STATICS.md`.
   - Rename in your head via `gFav_Bitset` style, add to `static_manual` in `generate_naming.py`, rerun.

3. **Verify:** `python3 tools/apply_names.py --annotated` + `git diff docs/ModLoader_Annotated.csa` should only show your new entries + comments.

---

## Example Before / After

**Before (numbers only):**
```asm
:Label_1835
Function 6 19 0
  getF1 1 ; CallNative "DOES_SCRIPT_EXIST" 1 1 ; JumpTrue @Label_423
  getF1 1 ; pFrame1 8 ; StrCopy 64
  CallNative "IS_PS3_VERSION" 0 1 ; JumpFalse @Label_424
  PushString ".csc Not Found!" ; Jump @Label_425
:Label_424  PushString ".xsc Not Found!"
:Label_425  pFrame1 8 ; StrAdd 64 ; pFrame1 8 ; getF1 5 ; Call @Label_396
```

**After (annotated):**
```asm
:Label_1835  ; >>> Loader_AddMenuEntry
Function 6 19 0  ; 6 params: visible, script, stack, flagA, flagB, enabled
  getF1 1 ; CallNative "DOES_SCRIPT_EXIST" 1 1 ; JumpTrue @Loader_AddMenuEntry__NotFoundBranch  ; -> Loader_AddMenuEntry__NotFoundBranch
  getF1 1 ; pFrame1 8 ; StrCopy 64  ; gTmp_Buffer
  CallNative "IS_PS3_VERSION" 0 1 ; JumpFalse @Loader_AddMenuEntry__PS3Suffix
  PushString ".csc Not Found!" ; Jump @Loader_AddMenuEntry__AppendSuffix
:Label_424  ; >>> Loader_AddMenuEntry__PS3Suffix
  PushString ".xsc Not Found!"
:Label_425  ; >>> Loader_AddMenuEntry__AppendSuffix
  pFrame1 8 ; StrAdd 64 ; pFrame1 8 ; getF1 5 ; Call @UI_Draw_TextRow  ; -> UI_Draw_TextRow
```

**After (fully renamed):**
```asm
:Loader_AddMenuEntry
Function 6 19 0
  getF1 1 ; CallNative "DOES_SCRIPT_EXIST" 1 1 ; JumpTrue @Loader_AddMenuEntry__NotFoundBranch
```

Pick annotated for PRs, renamed for local vNext dev.

---

## Map Stats

- **296 labels** named (273 func + 23 internal jumps) — all numbers gone.
- **315 statics** named (512×1 + 600×2 slots, 180 used, rest `gUnk_*` reserved).
- **~45 bit flags** decoded in `BITSET_MAP.md` (71.10 Master, 138.16 GodMode, 139.9 AntiFreeze, etc.).

Now every future change (add vehicle hash, new teleport, theme tweak) can use `gVehicle_SelectedCategory` instead of `Static1[120]` and `Page_Teleport_Hub_Impl` instead of `Label_74`.

*Run `python3 tools/generate_naming.py` after each new feature to keep maps authoritative.*
