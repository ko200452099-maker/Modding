# Naming Map — Statics (Numbers → Correct Names)

> ⚠️ **2026-09-11 audit:** several curated names were found WRONG by code reading — corrected in `tools/rename_map.json`. Notably: `S1[141/142]` are **toggle bitfields** (not queue head/tail), `S1[150]` is the **help-bar frame flag** (not free), `S1[82]` is `gTheme_FontUnselected` (not a color id), `S2[357]` is `gLang_Spanish` (was inverted), `S1[28/29]` = saved page/selection, `S1[214]` = row counter, `S1[224]` = row **Y**. Verdicts + evidence: **`docs/LOADER_AUDIT_VERIFIED.md`**.


> 512 Static1 + 600 Static2 slots. Only ~180 used — rest `gUnk_*` reserved.  
> Curated from `Label_0` init (27 fixed), `ModLoader_Statics.c` (27), usage counts, and cross-ref with natives.

## Static1 — 512 int/float slots

| Id | New Name | Init | Sets | Gets | Meaning |
|---|---|---|---|---|---|
| 0 | `gMenu_X` | ? | 4 | 15 | Menu X anchor (safe-zone) |
| 1 | `gMenu_Y` | ? | 4 | 31 | Menu Y anchor |
| 2 | `gMenu_W` | ? | 4 | 39 | Menu W |
| 3 | `gTheme_HudId_Primary` | ? | 1 | 45 | curated |
| 4 | `gTheme_HudId_Secondary` | ? | 1 | 0 | curated |
| 5 | `gTheme_HudId_Tertiary` | ? | 1 | 7 | curated |
| 6 | `gTheme_HudId_Accent` | ? | 1 | 11 | curated |
| 7 | `gTheme_HudId_Background` | ? | 1 | 12 | curated |
| 8 | `gTheme_HudId_A` | ? | 1 | 0 | curated |
| 9 | `gTheme_HudId_B` | ? | 1 | 0 | curated |
| 10 | `gTheme_HudId_C` | ? | 1 | 0 | curated |
| 11 | `gTheme_HudId_D` | ? | 1 | 0 | curated |
| 12 | `gTheme_HudId_E` | ? | 1 | 7 | curated |
| 13 | `gTheme_HudId_F` | ? | 1 | 0 | curated |
| 14 | `gTheme_HudId_Green` | ? | 1 | 0 | curated |
| 15 | `gTheme_HudId_Yellow` | ? | 1 | 0 | curated |
| 16 | `gTheme_HudId_Orange` | ? | 1 | 0 | curated |
| 17 | `gTheme_HudId_H` | ? | 1 | 6 | curated |
| 18 | `gTheme_HudId_I` | ? | 1 | 12 | curated |
| 19 | `gTheme_HudId_J` | ? | 1 | 4 | curated |
| 20 | `gTheme_HudId_K` | ? | 1 | 20 | curated |
| 21 | `gTheme_HudId_L` | ? | 1 | 5 | curated |
| 22 | `gTheme_HudId_M` | ? | 1 | 18 | curated |
| 23 | `gTheme_HudId_N` | ? | 1 | 2 | curated |
| 24 | `gTheme_HudId_Selected` | ? | 1 | 25 | curated |
| 25 | `gTheme_HudId_Unselected` | ? | 1 | 0 | curated |
| 26 | `gTheme_HudId_Title` | ? | 1 | 0 | curated |
| 27 | `gTheme_HudId_Title2` | ? | 1 | 0 | curated |
| 28 | `gToggle_DisabledFlag` | ? | 2 | 2 | curated |
| 29 | `gAlpha_Global` | ? | 2 | 1 | curated |
| 30 | `gSafeZone_Multiplier` | ? | 1 | 1 | curated |
| 31 | `gColor_R_White` | ? | 1 | 1 | curated |
| 32 | `gColor_G_White` | ? | 1 | 1 | curated |
| 33 | `gColor_B_White` | ? | 1 | 1 | curated |
| 34 | `gColor_A_White` | ? | 4 | 5 | curated |
| 35 | `gColor_R_Select` | ? | 1 | 1 | curated |
| 36 | `gColor_G_Select` | ? | 1 | 1 | curated |
| 37 | `gColor_B_Select` | ? | 1 | 1 | curated |
| 38 | `gColor_R_Background` | ? | 9 | 7 | curated |
| 39 | `gColor_G_Background` | ? | 5 | 6 | curated |
| 40 | `gColor_B_Background` | ? | 5 | 6 | curated |
| 41 | `gColor_A_Background` | ? | 5 | 6 | curated |
| 42 | `gColor_R_Title` | ? | 3 | 1 | curated |
| 43 | `gColor_R_Shadow` | ? | 1 | 3 | curated |
| 44 | `gColor_G_Shadow` | ? | 1 | 2 | curated |
| 45 | `gColor_Scroll_R` | ? | 5 | 6 | curated |
| 46 | `gColor_Scroll_G` | ? | 5 | 6 | curated |
| 47 | `gColor_Scroll_B` | ? | 5 | 6 | curated |
| 48 | `gColor_Row_R` | ? | 3 | 1 | curated |
| 49 | `gColor_Row_G` | ? | 1 | 3 | curated |
| 50 | `gColor_Row_B` | ? | 1 | 6 | curated |
| 51 | `gColor_Row_A` | ? | 1 | 6 | curated |
| 52 | `gColor_Border_R` | ? | 1 | 6 | curated |
| 53 | `gColor_Border_G` | ? | 3 | 2 | curated |
| 54 | `gColor_Border_B` | ? | 1 | 3 | curated |
| 55 | `gColor_Border_A` | ? | 1 | 2 | curated |
| 56 | `gColor_Header_R` | ? | 1 | 2 | curated |
| 57 | `gColor_Header_G` | ? | 1 | 2 | curated |
| 58 | `gColor_Header_B` | ? | 1 | 1 | curated |
| 59 | `gColor_Header_A` | ? | 1 | 1 | curated |
| 60 | `gColor_TextUnselected_R` | ? | 1 | 1 | curated |
| 61 | `gColor_TextUnselected_G` | ? | 3 | 1 | curated |
| 62 | `gColor_TextUnselected_B` | ? | 3 | 2 | curated |
| 63 | `gColor_TextSelected_R` | ? | 1 | 2 | curated |
| 64 | `gColor_TextSelected_G` | ? | 3 | 1 | curated |
| 65 | `gColor_TextSelected_B` | ? | 3 | 1 | curated |
| 66 | `gColor_Icon_R` | ? | 3 | 1 | curated |
| 67 | `gColor_Icon_G` | ? | 3 | 1 | curated |
| 68 | `gColor_Icon_B` | ? | 3 | 1 | curated |
| 69 | `gColor_Icon_A` | ? | 3 | 3 | curated |
| 70 | `gLanguage` | ? | 3 | 1 | 0=ES 1=EN |
| 71 | `gFlags_Main` | ? | 0 | 12 | curated |
| 72 | `gFlags_Player` | ? | 0 | 37 | curated |
| 73 | `gFlags_Recovery` | ? | 0 | 3 | curated |
| 74 | `gMenu_TmpIsVisible` | ? | 3 | 3 | curated |
| 75 | `gMenu_PrevState` | ? | 3 | 5 | curated |
| 76 | `gMenu_IsTransitioning` | ? | 3 | 3 | curated |
| 77 | `gMenu_FadeAlpha` | ? | 1 | 3 | curated |
| 78 | `gMenu_ScrollOffsetY` | ? | 1 | 3 | curated |
| 79 | `gMenu_NeedsRedraw` | ? | 1 | 3 | curated |
| 80 | `gMenu_ForceRefresh` | ? | 1 | 3 | curated |
| 81 | `gMenu_PageStackDepth` | ? | 1 | 1 | curated |
| 82 | `gMenu_SelectedColorId` | ? | 1 | 15 | curated |
| 83 | `gMenu_UnselectedColorId` | ? | 1 | 1 | curated |
| 84 | `gMenu_TitleColorId` | ? | 1 | 4 | curated |
| 85 | `gMenu_HeaderColorId` | ? | 1 | 7 | curated |
| 86 | `gMenu_FooterColorId` | ? | 1 | 1 | curated |
| 87 | `gMenu_BorderColorId` | ? | 1 | 7 | curated |
| 88 | `gMenu_ToggleOnColor` | ? | 1 | 3 | curated |
| 89 | `gMenu_ToggleOffColor` | ? | 1 | 3 | curated |
| 90 | `gMenu_DisabledColor` | ? | 1 | 0 | curated |
| 91 | `gMenu_HighlightAlpha` | ? | 1 | 1 | curated |
| 92 | `gSfx_Enabled` | ? | 1 | 3 | curated |
| 93 | `gInput_HoldTimer` | ? | 1 | 1 | curated |
| 94 | `gUnk1_94` | ? | 1 | 1 | auto |
| 95 | `gUnk1_95` | ? | 3 | 4 | auto |
| 96 | `gUnk1_96` | ? | 3 | 3 | auto |
| 97 | `gUnk1_97` | ? | 3 | 3 | auto |
| 98 | `gUnk1_98` | ? | 3 | 4 | auto |
| 99 | `gUnk1_99` | ? | 3 | 3 | auto |
| 100 | `gUI_RowHeight` | ? | 1 | 13 | curated |
| 101 | `gUI_TmpCounter` | ? | 1 | 4 | curated |
| 102 | `gUI_WrapMode` | ? | 1 | 3 | curated |
| 103 | `gUI_ScaleX` | ? | 1 | 1 | curated |
| 104 | `gUI_ScaleY` | ? | 1 | 1 | curated |
| 105 | `gUI_MaxRows` | ? | 1 | 1 | curated |
| 106 | `gUI_TextSizeSmall` | ? | 5 | 7 | curated |
| 107 | `gUI_TextSizeMedium` | ? | 5 | 7 | curated |
| 108 | `gUI_TextSizeLarge` | ? | 5 | 7 | curated |
| 109 | `gUI_HeaderHeight` | ? | 5 | 7 | curated |
| 110 | `gUI_FooterHeight` | ? | 5 | 7 | curated |
| 111 | `gUI_Padding` | ? | 5 | 7 | curated |
| 112 | `gUI_Margin` | ? | 5 | 7 | curated |
| 113 | `gUI_BorderWidth` | ? | 5 | 7 | curated |
| 114 | `gUI_ShadowOffset` | ? | 5 | 7 | curated |
| 115 | `gUI_IconSize` | ? | 5 | 7 | curated |
| 116 | `gUI_AnimationSpeed` | ? | 5 | 7 | curated |
| 117 | `gUI_FadeSpeed` | ? | 5 | 7 | curated |
| 118 | `gUI_ScrollSpeed` | ? | 5 | 7 | curated |
| 119 | `gUI_SoundVolume` | ? | 5 | 7 | curated |
| 120 | `gVehicle_SelectedCategory` | ? | 5 | 7 | curated |
| 121 | `gVehicle_SelectedModelIdx` | ? | 5 | 7 | curated |
| 122 | `gVehicle_SelectedColorIdx` | ? | 5 | 7 | curated |
| 123 | `gVehicle_SelectedModIdx` | ? | 5 | 7 | curated |
| 124 | `gVehicle_SpawnDistance` | ? | 5 | 7 | curated |
| 125 | `gVehicle_SpawnHeading` | ? | 5 | 7 | curated |
| 126 | `gVehicle_UseGroundProperly` | ? | 5 | 7 | curated |
| 127 | `gVehicle_AutoFix` | ? | 5 | 7 | curated |
| 128 | `gVehicle_TmpHandle` | ? | 1 | 0 | curated |
| 129 | `gTick_LastFrame` | ? | 2 | 1 | curated |
| 130 | `gMenu_CurrentState` | ? | 5 | 12 | Current page id (Switch) |
| 131 | `gTick_NextInputAllowedTime` | ? | 1 | 1 | curated |
| 132 | `gMenu_ScrollSpeedRaw` | ? | 2 | 6 | curated |
| 133 | `gMenu_ScrollDir` | ? | 2 | 2 | curated |
| 134 | `gQueue_PendingScript` | ? | 3 | 5 | Pending script (v1 queue) |
| 135 | `gQueue_RequestSent` | ? | 2 | 1 | curated |
| 136 | `gQueue_PendingStack` | ? | 2 | 1 | curated |
| 137 | `gProt_FxClearFlags` | ? | 0 | 3 | curated |
| 138 | `gProt_PlayerFlags` | ? | 0 | 38 | Player protections bitset 0..28 |
| 139 | `gProt_GlobalFlags` | ? | 0 | 3 | Global flood bitset |
| 140 | `gUI_Unk_140` | ? | 0 | 4 | auto |
| 141 | `gQueue_Head` | ? | 0 | 1 | curated |
| 142 | `gQueue_Tail` | ? | 0 | 13 | curated |
| 143 | `gProt_RemoteFlags` | ? | 0 | 30 | curated |
| 144 | `gMenu_StackSizeOverride` | ? | 18 | 1 | curated |
| 145 | `gCheat_FastKillFlags` | ? | 0 | 3 | curated |
| 146 | `gMenu_AnimFlags` | ? | 0 | 3 | curated |
| 147 | `gProt_VehicleFlags` | ? | 0 | 28 | curated |
| 148 | `gUI_Unk_148` | ? | 2 | 1 | auto |
| 149 | `gUI_Unk_149` | ? | 5 | 2 | auto |
| 150 | `gFeature_UseVNextQueue` | ? | 2 | 1 | curated |
| 151 | `gPlayer_WantedLevelBackup` | ? | 4 | 2 | curated |
| 152 | `gUI_Unk_152` | ? | 2 | 1 | auto |
| 153 | `gPlayer_GodModeCached` | ? | 2 | 2 | curated |
| 155 | `gUI_Unk_155` | ? | 0 | 4 | auto |
| 157 | `gUI_Unk_157` | ? | 0 | 1 | auto |
| 159 | `gUI_Unk_159` | ? | 0 | 3 | auto |
| 160 | `gUI_Unk_160` | ? | 0 | 2 | auto |
| 162 | `gVehicle_GravityFlags` | ? | 0 | 8 | curated |
| 163 | `gUI_Unk_163` | ? | 3 | 1 | auto |
| 165 | `gUI_Unk_165` | ? | 1 | 1 | auto |
| 166 | `gUI_Unk_166` | ? | 2 | 3 | auto |
| 167 | `gProt_SpawnFlags` | ? | 0 | 3 | curated |
| 168 | `gProt_NetworkFlags` | ? | 0 | 9 | curated |
| 169 | `gUI_Unk_169` | ? | 1 | 9 | auto |
| 170 | `gUI_Unk_170` | ? | 0 | 1 | auto |
| 171 | `gUI_Unk_171` | ? | 4 | 4 | auto |
| 172 | `gUI_Unk_172` | ? | 1 | 0 | auto |
| 173 | `gMenu_PageHistoryDepth` | ? | 11 | 6 | curated |
| 174 | `gMenu_HistoryTop` | ? | 2 | 4 | curated |
| 175 | `gTheme_Custom_R1` | ? | 0 | 0 | curated |
| 186 | `gTheme_Custom_R2` | ? | 0 | 0 | curated |
| 197 | `gInput_SelectedIndex` | ? | 10 | 65 | Selected index |
| 198 | `gUI_VisibleCount` | ? | 1 | 12 | curated |
| 199 | `gUnk1_199` | ? | 1 | 5 | auto |
| 200 | `gUnk1_200` | ? | 0 | 2 | auto |
| 201 | `gUnk1_201` | ? | 1 | 5 | auto |
| 202 | `gUnk1_202` | ? | 1 | 10 | auto |
| 203 | `gTheme_PaletteId` | ? | 1 | 1 | curated |
| 204 | `gTheme_Handle1` | ? | 15 | 2 | curated |
| 205 | `gTheme_Handle2` | ? | 15 | 3 | curated |
| 206 | `gUnk1_206` | ? | 2 | 6 | auto |
| 207 | `gUnk1_207` | ? | 1 | 1 | auto |
| 208 | `gUnk1_208` | ? | 6 | 2 | auto |
| 209 | `gUI_Hdr_R` | ? | 0 | 1 | curated |
| 210 | `gUI_Hdr_G` | ? | 0 | 1 | curated |
| 211 | `gUI_Hdr_B` | ? | 0 | 1 | curated |
| 212 | `gUI_Hdr_A` | ? | 0 | 1 | curated |
| 213 | `gUI_TextBaseY` | ? | 1 | 7 | curated |
| 214 | `gUI_CursorY` | ? | 2 | 62 | Cursor Y |
| 215 | `gUnk1_215` | ? | 0 | 1 | auto |
| 216 | `gUnk1_216` | ? | 0 | 1 | auto |
| 217 | `gUnk1_217` | ? | 0 | 1 | auto |
| 218 | `gUnk1_218` | ? | 0 | 1 | auto |
| 219 | `gUnk1_219` | ? | 0 | 1 | auto |
| 220 | `gUnk1_220` | ? | 0 | 5 | auto |
| 221 | `gUnk1_221` | ? | 0 | 5 | auto |
| 222 | `gUnk1_222` | ? | 0 | 5 | auto |
| 223 | `gUI_MaxVisibleRows` | ? | 8 | 43 | Max visible rows |
| 224 | `gUI_HighlightX` | ? | 4 | 13 | curated |
| 225 | `gUI_ShowBorders` | ? | 3 | 8 | curated |
| 226 | `gUnk1_226` | ? | 2 | 2 | auto |
| 227 | `gUI_SpriteW_Selected` | ? | 10 | 4 | curated |
| 228 | `gUI_SpriteH_Selected` | ? | 10 | 4 | curated |
| 229 | `gUI_ColR_Selected` | ? | 1 | 4 | curated |
| 230 | `gUI_ColG_Selected` | ? | 1 | 4 | curated |
| 231 | `gUI_ColB_Selected` | ? | 1 | 4 | curated |
| 232 | `gUI_SpriteW_Normal` | ? | 11 | 4 | curated |
| 233 | `gUI_SpriteH_Normal` | ? | 11 | 4 | curated |
| 234 | `gUI_ColR_Normal` | ? | 11 | 2 | curated |
| 235 | `gUI_ColG_Normal` | ? | 11 | 2 | curated |
| 236 | `gUI_ColB_Normal` | ? | 11 | 2 | curated |
| 237 | `gUnk1_237` | ? | 2 | 2 | auto |
| 238 | `gUI_ColR_SpriteOn` | ? | 11 | 2 | curated |
| 239 | `gUI_ColG_SpriteOn` | ? | 11 | 2 | curated |
| 240 | `gUI_ColB_SpriteOn` | ? | 11 | 2 | curated |
| 241 | `gUI_BG_R` | ? | 0 | 9 | curated |
| 242 | `gUI_BG_G` | ? | 0 | 9 | curated |
| 243 | `gUI_BG_B` | ? | 0 | 9 | curated |
| 244 | `gUnk1_244` | ? | 0 | 7 | auto |
| 245 | `gUnk1_245` | ? | 0 | 3 | auto |
| 246 | `gUnk1_246` | ? | 1 | 6 | auto |
| 247 | `gUI_FG_R` | ? | 0 | 1 | curated |
| 248 | `gUI_FG_G` | ? | 0 | 1 | curated |
| 249 | `gUI_FG_B` | ? | 0 | 1 | curated |
| 250 | `gUnk1_250` | ? | 1 | 6 | auto |
| 251 | `gUnk1_251` | ? | 1 | 6 | auto |
| 252 | `gUnk1_252` | ? | 8 | 1 | auto |
| 253 | `gOutfit_CurrentIdx` | ? | 14 | 1 | curated |
| 254 | `gUnk1_254` | ? | 1 | 5 | auto |
| 255 | `gUnk1_255` | ? | 1 | 1 | auto |
| 257 | `gOutfit_Filter_Show` | ? | 0 | 0 | curated |
| 258 | `gOutfit_Scroll_R` | ? | 0 | 0 | curated |
| 259 | `gOutfit_Scroll_G` | ? | 0 | 0 | curated |
| 260 | `gOutfit_Scroll_B` | ? | 0 | 0 | curated |
| 262 | `gOutfit_PreviewEnabled` | ? | 0 | 0 | curated |
| 268 | `gText_R_Selected` | ? | 0 | 0 | curated |
| 269 | `gText_G_Selected` | ? | 0 | 0 | curated |
| 270 | `gText_B_Selected` | ? | 0 | 0 | curated |

## Static2 — 600 slots

| Id | New Name | Sets | Gets | Meaning |
|---|---|---|---|---|
| 256 | `gUnk2_256` | 1 | 1 | auto |
| 257 | `gUnk2_257` | 0 | 3 | auto |
| 258 | `gUnk2_258` | 0 | 2 | auto |
| 259 | `gUnk2_259` | 0 | 2 | auto |
| 260 | `gUnk2_260` | 0 | 2 | auto |
| 261 | `gUnk2_261` | 2 | 3 | auto |
| 262 | `gUnk2_262` | 0 | 3 | auto |
| 263 | `gUnk2_263` | 2 | 1 | auto |
| 264 | `gUnk2_264` | 3 | 1 | auto |
| 265 | `gUnk2_265` | 1 | 1 | auto |
| 266 | `gSprite_Width` | 1 | 10 | curated |
| 267 | `gSprite_Height` | 8 | 1 | curated |
| 268 | `gUnk2_268` | 0 | 2 | auto |
| 269 | `gUnk2_269` | 0 | 2 | auto |
| 270 | `gUnk2_270` | 0 | 2 | auto |
| 351 | `gUnk2_351` | 2 | 2 | auto |
| 352 | `gUnk2_352` | 2 | 2 | auto |
| 353 | `gTexDict_Punisher` | 11 | 5 | curated |
| 354 | `gTexDict_GlobeBG` | 11 | 3 | curated |
| 355 | `gTexDict_GlobeOffsetX` | 11 | 4 | curated |
| 356 | `gTexDict_Globe` | 11 | 3 | curated |
| 357 | `gLang_IsEnglish` | 2 | 2 | curated |
| 358 | `gUI_TextY` | 4 | 8 | curated |
| 359 | `gTmp_BufferPtrForButtonName` | 0 | 0 | curated |
| 362 | `gUI_TextWrap` | 2 | 2 | curated |
| 363 | `gUnk2_363` | 0 | 1 | auto |
| 364 | `gUI_RowColorSetA_R` | 4 | 3 | curated |
| 365 | `gUI_RowColorSetA_G` | 4 | 3 | curated |
| 366 | `gUI_RowColorSetA_B` | 4 | 7 | curated |
| 367 | `gUI_RowColorSetB_R` | 4 | 7 | curated |
| 368 | `gUI_RowColorSetB_G` | 0 | 4 | curated |
| 369 | `gUI_RowColorSetB_B` | 4 | 7 | curated |
| 370 | `gUI_RowColorSetC_R` | 4 | 7 | curated |
| 371 | `gUI_ScrollbarId1` | 1 | 2 | curated |
| 372 | `gUI_ScrollbarId2` | 1 | 2 | curated |
| 373 | `gUI_SpriteToggleEnabled` | 1 | 2 | curated |
| 374 | `gArray_Unk_374` | 0 | 2 | auto |
| 375 | `gArray_Unk_375` | 1 | 1 | auto |
| 376 | `gArray_Unk_376` | 1 | 2 | auto |
| 377 | `gUI_ScaleformHandle` | 1 | 34 | curated |
| 378 | `gArray_Unk_378` | 2 | 3 | auto |
| 379 | `gArray_Unk_379` | 2 | 3 | auto |
| 380 | `gArray_Unk_380` | 0 | 2 | auto |
| 391 | `gAnim_WasSelected` | 0 | 7 | curated |
| 392 | `gAnim_Looped` | 2 | 3 | curated |
| 393 | `gAnim_UpperOnly` | 2 | 3 | curated |
| 394 | `gAnim_AllowMove` | 2 | 3 | curated |
| 395 | `gAnim_Contorted` | 2 | 3 | curated |
| 396 | `gNet_PlayerActiveCheck` | 0 | 8 | curated |
| 397 | `gArray_OutfitCache_R` | 84 | 2 | curated |
| 398 | `gArray_OutfitCache_G` | 84 | 2 | curated |
| 399 | `gArray_OutfitCache_B` | 84 | 2 | curated |
| 400 | `gArray_Unk_400` | 0 | 1 | auto |
| 401 | `gArray_VehicleCache_A` | 4 | 8 | curated |
| 402 | `gArray_VehicleCache_B` | 26 | 7 | curated |
| 403 | `gArray_VehicleCache_C` | 26 | 7 | curated |
| 404 | `gArray_VehicleCache_D` | 26 | 7 | curated |
| 405 | `gArray_VehicleCache_E` | 26 | 7 | curated |
| 406 | `gArray_Unk_406` | 1 | 3 | auto |
| 407 | `gArray_Unk_407` | 0 | 1 | auto |
| 409 | `gArray_Unk_409` | 0 | 1 | auto |
| 410 | `gNet_IsSessionHost` | 0 | 5 | curated |
| 411 | `gProt_PlayerListCache` | 2 | 7 | curated |
| 412 | `gUnk2_412` | 0 | 1 | auto |
| 413 | `gUnk2_413` | 1 | 1 | auto |
| 414 | `gUnk2_414` | 1 | 0 | auto |
| 415 | `gUnk2_415` | 1 | 2 | auto |
| 416 | `gUnk2_416` | 1 | 2 | auto |
| 417 | `gUnk2_417` | 1 | 2 | auto |
| 418 | `gUnk2_418` | 0 | 1 | auto |
| 420 | `gTmp_StrBuffer_100` | 0 | 0 | curated |
| 434 | `gQueue_ScriptSlot0` | 0 | 0 | curated |
| 438 | `gQueue_StackSlot0` | 0 | 0 | curated |
| 442 | `gQueue_VersionSlot0` | 0 | 0 | curated |
| 450 | `gQueue_StartTime` | 0 | 0 | curated |
| 460 | `gFav_Bitset` | 0 | 0 | curated |
