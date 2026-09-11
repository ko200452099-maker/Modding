# Loader Name Audit — VERIFIED (code-read, with evidence)

> **Date:** 2026-09-11 · **Source:** pristine `ModLoader.csa` (29,937 lines; line numbers identical in the annotated `ModLoader.csa` since comments are appended at line ends).
> **Method:** every name below was confirmed **by reading the actual code** (`tools/deep_audit.py` call-graph + static cross-reference, then manual reading of each function). Verdicts: ✔ confirmed · ✗ corrected (old name was wrong) · ★ newly named (was `Func_Label_X` / `gUnk`) · ~ medium confidence (strong pattern evidence, marked).

---

## 1. The Loading Subsystem (as verified)

```
Menu page (48×) ──Call──> Label_1835 Loader_AddMenuEntry          [L5557, 87 call sites]
   │  params: visible, scriptFile, stackSize, iconA, iconB, enabled
   ├─> Label_396  UI_PrintRow ─> Label_546 UI_RenderRow            [L6951 / L5855]
   │        └─ Label_331 UI_GetRowTextRGB · Label_481 UI_ApplySelectedRowFont
   │           Label_551 UI_SetRowTextXIndent · Label_552 UI_ResolveRowTextX · Label_327 UI_DrawStreamedSprite
   ├─> Label_427  UI_DrawRowIcons                                  [L5810]
   │        └─ Label_450 Util_BuildButtonSpriteName ("button_"+id → S2[359]) · Label_327 · Label_314 UI_SetTextFormat
   ├─> Label_418  UI_DrawRowHighlight(isRunning)                   [L5665] ─> Label_436 UI_DrawHighlightBar
   └─> Label_397  Input_IsConfirmPressed                           [L5642] ─> Label_283 Sfx_PlayPhoneSound
   writes: S1[134]=script, S1[136]=stack        (single-slot queue, v1)

Label_3 Main_Tick [L286] ─ every frame: WAIT(0); S129=0; Label_5; Label_6; page dispatch...
   └─> Label_5 Tick_InputQueueAndToggles [L472]
         ├─ reopen gate (S130==0 & timer S131) → SET_INPUT_EXCLUSIVE(0,178)
         ├─ custom-script count → S133
         ├─ QUEUE CONSUME: if S134: → REQUEST_SCRIPT once (S135) → HAS_SCRIPT_LOADED →
         │                 START_NEW_SCRIPT(S134,S136) → SET_SCRIPT_AS_NO_LONGER_NEEDED → S134=0,S135=0
         ├─ bit toggles: S137 bit0 PTFX-clear · S138 bit12 → Label_119 World_ClearAreaAroundPlayer
         │                S139 bit9 mem-patch · ...
         └─ help bar (S80 bit0): default/called keys via Label_163/164 → Label_167 Help_RenderBar → S150=0
```

## 2. Queue protocol (v1) — statics VERIFIED

| Static | Verified name | Evidence |
|---|---|---|
| S1[134] | `gQueue_PendingScript` ✔ | Written by L1835 (L5600); L508: `if S134==0 skip`; L515: `REQUEST_SCRIPT(S134)`; zeroed after START (L533) |
| S1[135] | `gQueue_RequestSent` ✔ | Only Label_5 touches it: set 1 after REQUEST (L517), 0 after START (L535) |
| S1[136] | `gQueue_PendingStack` ✔ | Written L5602 by L1835; read L526 as arg2 of `START_NEW_SCRIPT` |
| S1[129] | `gTick_InputConsumed` ✗ | (was gTick_LastFrame) L291: zeroed every frame in Main_Tick; Label_111: `if S129 return` then sets 1 |
| S1[130] | `gMenu_CurrentPage` ✔ | Switch dispatch L303 (48 pages); L1835 confirm requires menu open |
| S1[131] | `gTick_InputCooldownUntil` ~ | L476: `if S131 < GET_GAME_TIMER()` gate before reopen (SET_INPUT_EXCLUSIVE) |

## 3. Label verdicts (loader cluster)

| Label | Old name | Verdict | Verified name | Evidence (pristine lines) |
|---|---|---|---|---|
| Label_1835 | Loader_AddMenuEntry | ✔ | same | 87 identical call sites; DOES_SCRIPT_EXIST L5559 |
| Label_423 | `__NotFoundBranch` | ✗ **WRONG** | `Loader_AddMenuEntry__Exists` | JumpTrue of DOES_SCRIPT_EXIST lands here = the **found** path (L5562→L5577) |
| Label_424 | `__PS3Suffix` | ✗ **WRONG** | `Loader_AddMenuEntry__NonPS3Suffix` | JumpFalse of IS_PS3_VERSION → pushes `.xsc` (L5567-5570); PS3 fall-through pushes `.csc` |
| Label_425/426/428 | `__AppendSuffix/__Return/__Queue` | ✔ | `__SuffixDone/__Return/__QueueLoad` | L5571/L5606/L5599 |
| Label_396 | UI_Draw_TextRow | ✔ | `UI_PrintRow` | wrapper: `546(text,flag,0)` (L6951) |
| Label_546 | UI_Draw_TextRow_Internal | ✔ | `UI_RenderRow` | the real renderer: S214+=1.0 row counter, Y→S2[358]=row·S100+0.1985, colors, indent, bars (L5855+) |
| Label_397 | Input_IsConfirmPressed | ✔ (impl refined) | same | Requires **S197==S214**; **202/203 pressed ⇒ SUPPRESSED (returns 0)** — not an R1+L1 combo as deep-dive claimed; else ctrl 177 JUST_PRESSED → `Click_Special` → 1 (L5642-5663) |
| Label_418 | UI_Update_HighlightRect | ✔→renamed | `UI_DrawRowHighlight` | Receives **isRunning** flag (CmpNe of UNK_029D3841), computes S224=Y(clamp 197/214/223·S100+0.2165), calls 436(isRunning) (L5665-5700) |
| Label_427 | UI_Draw_IconPlus | ✗ incomplete | `UI_DrawRowIcons` | Draws iconA sprite `erootiik:button_<id>` at X=S1[1]−0.066, optional `+` text (font S82, white), and iconB at X=S1[1]−0.036 (L5810-5888) |
| Label_436 | UI_Draw_HighlightSprite | ✔ | `UI_DrawHighlightBar` | draws themed highlight sprite (dict S2[353], name S2[354], W/H S227/228, RGB S229-231) at S224 (L5701…) |
| Label_450 | Util_MakeButtonSpriteName | ✔ | `Util_BuildButtonSpriteName` | `"button_"+id` → buffer S2[359], returns ptr (L5889) |
| Label_314 | UI_Set_HudColour | ✗ **WRONG** | `UI_SetTextFormat` | SET_TEXT_FONT(f0), SET_TEXT_SCALE(0,0.48), SET_TEXT_COLOUR(f1..f3,255), wrap/centre, outline if f4 (L6822…) |
| Label_331 | UI_Set_TextColorFromStatic | ✗ **WRONG** | `UI_GetRowTextRGB` | **Returns 3 values**: if S197==S214 → S241..243 else S2[268..270] — the selected/unselected row text RGB (L7322…) |
| Label_481 | Func_Label_481 | ★ | `UI_ApplySelectedRowFont` | if S197==S214: SET_TEXT_FONT(S83) (L7402…) |
| Label_551/552 | Func_Label_551/552 | ★ | `UI_SetRowTextXIndent` / `UI_ResolveRowTextX`~ | 551: X=S0(+0.013 selected)→S2[362]; 552: passthrough gated by S68 |
| Label_358 | Input_GetSelectedIndex | ✔ | same | `FtoI(S197)` (L3878) |
| Label_1158 | UI_Handle_Scroll | ✗ **WRONG** | `Input_IsAltActionPressed` | group **2** ctrl **193** JUST_PRESSED + 202/203 suppress → `Click_Special` → 1 (L3878-3899) |
| Label_163 | Util_LangPick_ES_EN | ✔ | same | returns getF1 0 (ES) if S2[357]==1 else getF1 1 (EN) (L5772) |
| Label_164 | Func_Label_164 | ★ | `Help_AddButtonSlot` | INSTRUCTIONAL_BUTTONS scaleform: requests S202, CLEAR_ALL once (S2[351]), SET_DATA_SLOT++ (S2[352]) (L5778…) |
| Label_167 | Func_Label_167 | ★ | `Help_RenderBar` | `DRAW_INSTRUCTIONAL_BUTTONS` method on handle S1[202] |
| Label_458 | Page_StaticText_Label_458 | ✗ **WRONG** | `Help_DrawCustomKeys` | if S197==S214 draws "Change Values"/"Select"/"Scroll"/Back-Exit keys → **S1[150]=1** (L29110…) |
| Label_275 | Func_Label_275 | ★ | `Menu_HandleBack` | saves S130→S28, S197→S29; back keys (ctrl from S204/S205) → "BACK" sound, S130=0, frees scaleforms S199-202 (L3766…) |
| Label_455 | (curated other) | ★✔ | `Menu_PushPage` | S175[depth]=page, S186[depth]=selection, sets new page, S197=1.0, depth++ (L5941…) |
| Label_111 | Func_Label_111 | ★ | `Input_HandleScrollNav` | NAV scroll (S197±1, wrap via S198 restore), **page POP** (depth-1 → S130=S175[d], S197=S186[d], L3653), scaleform cleanup |
| Label_119 | Func_Label_119 | ★ | `World_ClearAreaAroundPlayer` | switch S2[370] 0-5 → CLEAR_AREA(_OF_VEHICLES/OBJECTS/PEDS/COPS/PROJECTILES) r=500 (L3362…) |
| Label_173 | Func_Label_173 | ★ | `Stat_ForceIntValue` | STAT_GET_INT(hash,&v); if ok && v≠want → STAT_SET_INT (77 callers) (L3270) |
| Label_1940 | Func_Label_1940 | ★ | `CustomScript_MenuEntry` | custom-script row: draw name; if selected shows "Remove" (ctrl 179) → clears buf, S132−−; else loader behavior (L5432…) |
| Label_2282 | Func_Label_2282 | ★ | `Settings_RowsPerPage` | switch S2[373] 0..3 → S223 = 9/10/11/12 (L8531…) |
| Label_401/402 | Func | ★ | `CustomScript_CountDown/Up` | S132 = min(S132±1, 10) (L5397/L5404) |
| Label_9 | Draw_BackgroundIfMenuOpen | ✗ **WRONG** | `UI_PrepareCleanFrame` | no drawing at all: hides HUD comps 6-9, hides help, clears globals 10434/13245, kills special ability (S94) & stealth (L3814…) |
| Label_1 | Mod_Init_TexturesAndLocals | ✗ imprecise | `Mod_Init_UITheme` | S223=10 rows, S2[267]=11, tex names S2[353-356], theme RGBs… |
| Label_5/6/3/0/2 | Tick_HandleInputAndQueue / …Preparations / Main_Tick / Mod_Init_Main / Util_GetSafeZoneHalf | ✔ | `Tick_InputQueueAndToggles` / `Tick_ApplyToggleEffects` / Main_Tick / Mod_Init_Main / same | refined but same roles |
| Label_283 | Sfx_Play_ClickSpecial | ✗ over-specific | `Sfx_PlayPhoneSound` | generic 1-param: PLAY_SOUND_FRONTEND(-1, name, "WEB_NAVIGATION_SOUNDS_PHONE") if S92 |
| Label_298 | Sfx_Play_FrontendDefault | ✔ | same | same shape, soundset `HUD_FRONTEND_DEFAULT_SOUNDSET` (called with "BACK") |
| Label_145 | Entity_GetClosestObjectInFront | ~ refine | `Entity_TakeControlClosestObject` | net-control + DETACH + SET_ENTITY_COORDS of closest object (345 callers) |

## 4. Static verdicts (highlights; full set applied in `tools/rename_map.json`)

| Static | Old name | Verdict | Verified name | Evidence |
|---|---|---|---|---|
| S1[150] | gFeature_UseVNextQueue | ✗ **WRONG + DANGEROUS** | `gHelp_CustomKeysFrame` | per-frame flag: Label_5 zeroes after help render (L1721); Label_458 sets 1 when custom keys drawn; read L1691 to suppress default keys |
| S1[141] | gQueue_Head | ✗ **WRONG** | `gBits_Features4` | `IS_BIT_SET(S141,1)` in Label_5 detacher block — a toggle bitfield like its neighbors |
| S1[142] | gQueue_Tail | ✗ **WRONG** | `gBits_Features5` | 21 bit-ops (bits 4/16/23…) across Label_5/6/104 — vehicle & misc toggles |
| S1[82] | gMenu_SelectedColorId | ✗ | `gTheme_FontUnselected` | init 6; passed as SET_TEXT_FONT arg to 314 (L5810 icon text; L7402 nearby); settings string "Font Unselected Text" |
| S1[83/84/81] | gMenu_*ColorId | ✗ | `gTheme_FontSelected` / `gTheme_FontOptionCount` / `gTheme_FontTitle` | Label_481 uses S83 via SET_TEXT_FONT; settings strings |
| S2[357] | gLang_IsEnglish | ✗ **INVERTED** | `gLang_Spanish` | language page: "Español"→**1**, "English"→**0** (L10734/10739); Label_163 picks ES when 1 |
| S1[28/29] | gToggle_DisabledFlag / gAlpha_Global | ✗ | `gMenu_SavedPage` / `gMenu_SavedSelection` | saved by Menu_HandleBack L3769/3771, restored by Page_Splash L3749-3753 |
| S1[30] | gSafeZone_Multiplier | ✗ | `gTheme_TitleScale` | only read at L4668: SET_TEXT_SCALE(0, S30) |
| S1[214] | gUI_CursorY | ✗ | `gUI_RowCounter` | float++ per rendered row (L5857); compared to S197 for "is selected row" |
| S1[223] | gUI_MaxVisibleRows | ~ | `gUI_RowsPerPage` | init 10.0; 9-12 via Settings_RowsPerPage; used in row-window clamp |
| S1[224] | gUI_HighlightX | ✗ (it's a Y!) | `gUI_RowY` | Y = row·S100 + 0.2165, consumed by 427 icons & 436 highlight bar |
| S1[197] | gInput_SelectedIndex | ✔ | `gInput_SelectedRow` (float!) | scrolled by Label_111 ±1.0; FtoI in Label_358 |
| S1[198] | gUI_VisibleCount | ✗ | `gInput_PrevSelectedRow` | L3673: `S197 = S198` restore on scroll-wrap |
| S1[174/175/186] | various | ✗/★ | `gMenu_PageStackDepth` / `gMenu_PageStack_0..` / `gMenu_SelStack_0..` | Menu_PushPage ArraySet1; pop in Label_111 L3653 |
| S1[132/133] | gMenu_ScrollSpeedRaw / gMenu_ScrollDir | ✗ | `gCustomScripts_Count` / `gCustomScripts_CanAdd` | 401/402 inc/dec capped 10; Label_71: "Agregar Un Script Personalizado" hidden when full (L18197) |
| S1[93] | gInput_HoldTimer | ✗ | `gCustomScripts_Enabled`~ | gates the S132/S133 logic in Label_5 L487 |
| S1[60..99 block] | assorted ColorId/etc | ✗ | theme/settings toggles — see map | settings-page strings: S74 SmoothScroll, S75/76 scrollbar, S77 random theme, S78/79 flashing, S80 instructional buttons, S88 option count, S89 scroll arrows, S95-99 vehicle spawn defaults |
| S1[199..202] | (mixed) | ★ | `gScaleform_Handle0..2` + `gScaleform_HelpBar` | HAS_SCALEFORM_MOVIE_LOADED/free in 111/275; S202 = INSTRUCTIONAL_BUTTONS movie |
| S2[353..356] | gTexDict_* (mis-assigned) | ~ | `gHighlight_TexDict/TexName/TexPadX/TexBgName` | Label_1 init L29866+; consumed in 436 as DRAW_SPRITE args |
| S2[362] | gUI_TextWrap | ✗ | `gUI_TextRowX` | set by 551 (S0 +0.013 selected), consumed as END_TEXT x |
| S2[358] | gUI_TextY | ✔ | `gUI_TextRowY` | Y = row·S100 + 0.1985 in 546 |
| S2[370] | — | ★ | `gWorld_ClearAreaMode` | switch selector in Label_119 |
| S2[373] | gUI_SpriteToggleEnabled | ✗ | `gUI_RowsPerPageChoice` | 0..3 switch index → 9..12 rows (L8530) |
| S1[241..243] | gUI_BG_R… | ✗ | `gTheme_TextSelectedR/G/B` | returned by 331 when row selected |
| S2[268..270] | gUnk2_268 | ★ | `gTheme_TextUnselectedR/G/B` | returned by 331 otherwise |
| S1[244] | gUnk1_244 | ★ | `gTheme_TextOutlineHeader` | 5th param (outline flag) to 314 in 326/512 |

## 5. ⛔ vNext Errata — 3 REAL bugs found & fixed during this audit

### E-01 · Dead jump refs in the v2 dispatch — the update could not assemble
`Label_3` patch jumps to `@L_upg_use_v1queue` / `@L_upg_after_queue`, but the labels are **defined** as `:Label_upg_use_v1queue` / `:Label_upg_after_queue`. `L_upg…` ≠ `Label_upg…` → undefined reference (best case assembler error; worst case silent jump to 0).
**Fixed** in `ModLoader_vNext.csa` + `tools/upgrade_loader.py`.

### E-02 · FIFO head/tail statics collide with v1 toggle bitfields
v2 spec/impl used **S1[141]=head, S1[142]=tail** — but v1 already uses both as **bitmask words**:
- S1[142]: 21 bit operations (`IS_BIT_SET/SET_BIT/CLEAR_BIT` bits 4, 16, 23…) in Label_5 / Label_6 / Label_104 (vehicle options etc.)
- S1[141]: `IS_BIT_SET(S141,1)` in the Label_5 detach-closest block
Every enqueue would have **corrupted vehicle toggles**, and every toggle flip would have **corrupted the queue indices** → scripts never starting / starting garbage.
**Fixed:** head → **S1[400]**, tail → **S1[401]** (verified 100 % unused across the whole 29,937-line script; S1[400..511] is completely free).

### E-03 · Feature flag collides with help-bar frame flag
v2 used **S1[150]** as "use vNext" flag — but v1 uses S150 every frame: Label_458 sets it when a page draws custom help keys; Label_5 clears it after rendering the help bar. The flag would **randomly flip mid-game**, bouncing dispatch between v1 queue and FIFO.
**Fixed:** feature flag → **S1[402]** (free).

### Corrected v2 resource map (as now shipped)
| Resource | Slot | Status |
|---|---|---|
| queueHead | **S1[400]** | ✅ verified free |
| queueTail | **S1[401]** | ✅ verified free |
| featureFlag (`1=use v2`) | **S1[402]** | ✅ verified free |
| queueScript[0..3] | S2[434..437] | ✅ verified free |
| queueStack[0..3] | S2[438..441] | ✅ verified free |
| queue_version[0..3] | S2[442..445] | ✅ verified free (used by enqueue code, previously undocumented) |
| loadStartTime | S2[450] | ✅ verified free |

> Note: earlier docs claimed FIFO slots at `Static[134..140]` — that was never the implementation; the real arrays are in Static2 (above). Docs corrected.

### Free real estate for the next update (verified)
- **Static1: 400-511 — all 112 slots free.** (Audit scanned every `Static*[12]` access.)
- **Static2: 442-599 — 158 slots free** (plus 434-441/450 now taken by v2).
- v1 max used: S1[255], S2[420].

## 6. Regenerated artifacts (from pristine, verified maps)

| File | How verified |
|---|---|
| `ModLoader.csa` (annotated) | stripping comments ≡ pristine, line-for-line (29,938 lines) |
| `docs/ModLoader_Annotated.csa` | same build |
| `docs/ModLoader_Annotated_Full.csa` | same, full map (all 2,466 labels incl. internals) |
| `ModLoader_Renamed.csa` / `ModLoader_Renamed_Full.csa` | every `@ref` resolves; only label identifiers changed (8,805 lines); strings untouched |
| `tools/rename_map.json` / `rename_map_full.json` | verified overrides applied by `tools/build_verified_map.py` |
| `ModLoader_vNext.csa` | regenerated by fixed `tools/upgrade_loader.py`; `--check` → only the 4 expected legacy v1 findings |

Tooling: `tools/deep_audit.py` (call graph + static cross-ref) · `tools/build_verified_map.py` (verified overrides) · `tools/apply_names.py --map` · `tools/upgrade_loader.py` (fixed) · `tools/loader_v2_test.py`.

— Audit performed with evidence; anything marked ~ is medium confidence and safe to refine later.
