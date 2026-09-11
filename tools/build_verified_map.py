#!/usr/bin/env python3
"""
build_verified_map.py — apply the AUDIT-VERIFIED name corrections on top of the
heuristic rename maps. Every override below was confirmed by reading the actual
code (see docs/LOADER_AUDIT_VERIFIED.md for evidence + line numbers).

Writes updated tools/rename_map.json and tools/rename_map_full.json in place.
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).parent

# ----------------------------------------------------------------------------
# VERIFIED function-label overrides (Label -> correct name)  [evidence in audit]
# ----------------------------------------------------------------------------
LABELS = {
    'Label_1':   'Mod_Init_UITheme',            # inits S223=10 rows, tex names, theme colors (was Mod_Init_TexturesAndLocals)
    'Label_5':   'Tick_InputQueueAndToggles',   # reopen gate, FIFO/queue, help bar, bit toggles
    'Label_6':   'Tick_ApplyToggleEffects',     # per-frame godmode/invis/ammo/etc via IS_BIT_SET(S137..148)
    'Label_9':   'UI_PrepareCleanFrame',        # hides HUD comps 6-9, clears globals, NOT a bg draw (was Draw_BackgroundIfMenuOpen)
    'Label_111': 'Input_HandleScrollNav',       # NAV_UP_DOWN/S199..202/back/pop page-stack (was Func_Label_111)
    'Label_119': 'World_ClearAreaAroundPlayer', # switch S2[370]: CLEAR_AREA_OF_* r=500 (was Func_Label_119)
    'Label_145': 'Entity_TakeControlClosestObject', # GET_CLOSEST_OBJECT_OF_TYPE+net ctrl+detach+move (345 callers)
    'Label_164': 'Help_AddButtonSlot',          # scaleform SET_DATA_SLOT++ (was Func_Label_164)
    'Label_167': 'Help_RenderBar',              # DRAW_INSTRUCTIONAL_BUTTONS on S1[202] (was Func_Label_167)
    'Label_173': 'Stat_ForceIntValue',          # STAT_GET_INT then STAT_SET_INT if differs (77 callers)
    'Label_275': 'Menu_HandleBack',             # saves page/sel, back-key (S204/205), frees 4 scaleforms (was Func)
    'Label_279': 'UI_NextListRow',              # S1[173] += 1 row counter (was Func_Label_279)
    'Label_283': 'Sfx_PlayPhoneSound',          # PLAY_SOUND_FRONTEND(-1,name,"WEB_NAVIGATION_SOUNDS_PHONE") gated by S92
    'Label_314': 'UI_SetTextFormat',            # font+scale0.48+color+wrap+centre+outline (was UI_Set_HudColour)
    'Label_327': 'UI_DrawStreamedSprite',       # requests dict if not streamed, then DRAW_SPRITE
    'Label_331': 'UI_GetRowTextRGB',            # returns 3: selected S241-243 else unselected S2[268-270] (was UI_Set_*)
    'Label_396': 'UI_PrintRow',                 # thin wrapper -> Label_546 (330 callers)
    'Label_418': 'UI_DrawRowHighlight',         # row-Y clamp + calls 436 with isRunning flag (was UI_Update_HighlightRect)
    'Label_427': 'UI_DrawRowIcons',             # icon A sprite, '+' text, icon B sprite (was UI_Draw_IconPlus)
    'Label_436': 'UI_DrawHighlightBar',         # DRAW_SPRITE of themed highlight at S224 (was UI_Draw_HighlightSprite)
    'Label_455': 'Menu_PushPage',               # page/selection stacks S175/S186 at depth S174, depth++
    'Label_458': 'Help_DrawCustomKeys',         # draws page-specific keys + sets S1[150]=1 (was Page_StaticText)
    'Label_481': 'UI_ApplySelectedRowFont',     # SET_TEXT_FONT(S83) when 197==214 (was Func_Label_481)
    'Label_546': 'UI_RenderRow',                # the real row renderer (Y, colors, indent, bars)
    'Label_551': 'UI_SetRowTextXIndent',        # S2[362]=S0(+0.013 if selected) (was Func_Label_551)
    'Label_552': 'UI_ResolveRowTextX',          # final X mask/passthrough gated by S68 (med confidence)
    'Label_1158':'Input_IsAltActionPressed',    # group2 ctrl193 + Click_Special (was UI_Handle_Scroll)
    'Label_1940':'CustomScript_MenuEntry',      # custom-script row: render/remove (ctrl 179) (was Func_Label_1940)
    'Label_2282':'Settings_RowsPerPage',        # switch S2[373] 0-3 -> S223 = 9/10/11/12 (was Func_Label_2282)
}

# ----------------------------------------------------------------------------
# VERIFIED internal jump labels:  label -> (owner, suffix)  ->  Owner__suffix
# ----------------------------------------------------------------------------
INTERNALS = {
    # Loader_AddMenuEntry (Label_1835)  — the two WRONG ones fixed here:
    'Label_423': ('Loader_AddMenuEntry', 'Exists'),        # was __NotFoundBranch (WRONG: this is the FOUND path)
    'Label_424': ('Loader_AddMenuEntry', 'NonPS3Suffix'),  # was __PS3Suffix (WRONG: JumpFalse of IS_PS3_VERSION)
    'Label_425': ('Loader_AddMenuEntry', 'SuffixDone'),
    'Label_426': ('Loader_AddMenuEntry', 'Return'),
    'Label_428': ('Loader_AddMenuEntry', 'QueueLoad'),
    # Input_IsConfirmPressed (Label_397)
    'Label_432': ('Input_IsConfirmPressed', 'ReturnNo'),
    # UI_DrawRowHighlight (Label_418)
    'Label_433': ('UI_DrawRowHighlight', 'ShortPage'),
    'Label_434': ('UI_DrawRowHighlight', 'Skip'),
    'Label_435': ('UI_DrawRowHighlight', 'ComputeY'),
    # UI_DrawRowIcons (Label_427)
    'Label_446': ('UI_DrawRowIcons', 'ShortPage'),
    'Label_447': ('UI_DrawRowIcons', 'Done'),
    'Label_448': ('UI_DrawRowIcons', 'ComputeY'),
    'Label_449': ('UI_DrawRowIcons', 'NoIconA'),
    # Util_LangPick_ES_EN (Label_163)
    'Label_441': ('Util_LangPick_ES_EN', 'English'),
    'Label_442': ('Util_LangPick_ES_EN', 'Done'),
    # Help_AddButtonSlot (Label_164)
    'Label_420': ('Help_AddButtonSlot', 'BarReady'),
    'Label_421': ('Help_AddButtonSlot', 'Draw'),
    'Label_422': ('Help_AddButtonSlot', 'WaitLoad'),
    # Sfx (283/298)
    'Label_431': ('Sfx_PlayPhoneSound', 'Muted'),
    'Label_429': ('Sfx_PlayFrontendDefault', 'Muted'),
    # World_ClearAreaAroundPlayer (Label_119)
    'Label_692': ('World_ClearAreaAroundPlayer', 'ClearAll'),
    'Label_693': ('World_ClearAreaAroundPlayer', 'Vehicles'),
    'Label_694': ('World_ClearAreaAroundPlayer', 'Objects'),
    'Label_695': ('World_ClearAreaAroundPlayer', 'Peds'),
    'Label_696': ('World_ClearAreaAroundPlayer', 'Cops'),
    'Label_697': ('World_ClearAreaAroundPlayer', 'Projectiles'),
    'Label_698': ('World_ClearAreaAroundPlayer', 'Done'),
    # Stat_ForceIntValue (Label_173)
    'Label_251': ('Stat_ForceIntValue', 'Done'),
    # UI_RenderRow (Label_546)
    'Label_547': ('UI_RenderRow', 'ShortPage'),
    'Label_548': ('UI_RenderRow', 'Skip'),
    'Label_549': ('UI_RenderRow', 'ComputeY'),
    'Label_550': ('UI_RenderRow', 'AfterIndent'),
    'Label_553': ('UI_RenderRow', 'Bar2'),
    # UI_GetRowTextRGB / UI_ApplySelectedRowFont / UI_SetRowTextXIndent / UI_ResolveRowTextX
    'Label_565': ('UI_GetRowTextRGB', 'Selected'),
    'Label_566': ('UI_ApplySelectedRowFont', 'Selected'),
    'Label_567': ('UI_ApplySelectedRowFont', 'Done'),
    'Label_568': ('UI_SetRowTextXIndent', 'Selected'),
    'Label_569': ('UI_SetRowTextXIndent', 'Done'),
    'Label_555': ('UI_ResolveRowTextX', 'PassThrough'),
    'Label_556': ('UI_ResolveRowTextX', 'UseMenuLeft'),
    'Label_557': ('UI_ResolveRowTextX', 'Done'),
    # Menu_HandleBack (Label_275)
    'Label_295': ('Menu_HandleBack', 'CheckAltKey'),
    'Label_296': ('Menu_HandleBack', 'Done'),
    'Label_297': ('Menu_HandleBack', 'DoBack'),
    'Label_299': ('Menu_HandleBack', 'FreeMovie2'),
    'Label_300': ('Menu_HandleBack', 'FreeMovie3'),
    'Label_301': ('Menu_HandleBack', 'FreeMovie4'),
    # Tick_InputQueueAndToggles (Label_5) — queue block
    'Label_112': ('Tick_InputQueueAndToggles', 'MenuOpen'),
    'Label_113': ('Tick_InputQueueAndToggles', 'AfterCustomCount'),
    'Label_114': ('Tick_InputQueueAndToggles', 'CustomFull'),
    'Label_115': ('Tick_InputQueueAndToggles', 'QueueDone'),
    'Label_116': ('Tick_InputQueueAndToggles', 'Requested'),
    # CustomScript count (Label_401)
    'Label_413': ('CustomScript_CountDown', 'Done'),
    # CustomScript_MenuEntry (Label_1940)
    'Label_415': ('CustomScript_MenuEntry', 'Done'),
    'Label_416': ('CustomScript_MenuEntry', 'ShowRemoveHint'),
    'Label_417': ('CustomScript_MenuEntry', 'AfterRemove'),
    # Input_HandleScrollNav (Label_111)
    'Label_274': ('Input_HandleScrollNav', 'Done'),
    # Help_DrawCustomKeys (Label_458)
    'Label_2396': ('Help_DrawCustomKeys', 'Done'),
    'Label_2397': ('Help_DrawCustomKeys', 'ChangeTextValues'),
    'Label_2398': ('Help_DrawCustomKeys', 'AfterKey21'),
    'Label_2399': ('Help_DrawCustomKeys', 'NoExtraConfirm'),
    'Label_2400': ('Help_DrawCustomKeys', 'ExitInstead'),
    'Label_2401': ('Help_DrawCustomKeys', 'Render'),
}

# ----------------------------------------------------------------------------
# VERIFIED statics — Static1 (ids 0..255+) / Static2
# ----------------------------------------------------------------------------
S1 = {
    '0': 'gMenu_LeftX', '1': 'gMenu_RightX', '2': 'gMenu_CenterX',
    '28': 'gMenu_SavedPage', '29': 'gMenu_SavedSelection', '30': 'gTheme_TitleScale',
    '31': 'gTheme_TitleR', '32': 'gTheme_TitleG', '33': 'gTheme_TitleB', '34': 'gTheme_TitleA',
    '35': 'gTheme_BgR', '36': 'gTheme_BgG', '37': 'gTheme_BgB', '38': 'gTheme_BgA',
    '39': 'gTheme_Bar1R', '40': 'gTheme_Bar1G', '41': 'gTheme_Bar1B',
    '45': 'gTheme_Bar2R', '46': 'gTheme_Bar2G', '47': 'gTheme_Bar2B',
    '62': 'gTheme_BarAlpha', '64': 'gTheme_RowBarsEnabled', '65': 'gTheme_SelectedIndentEnabled',
    '66': 'gUI_TickIconEnabled', '68': 'gTheme_TextAlignFlag',
    '69': 'gNet_DisableFindNewSession', '70': 'gSettings_LanguageChosen',
    '71': 'gBits_TogglesPage1', '72': 'gBits_TogglesPage2', '73': 'gBits_TogglesPage3',
    '74': 'gMenu_SmoothScroll', '75': 'gUI_ScrollbarEnabled', '76': 'gUI_ScrollbarAlways',
    '77': 'gTheme_RandomOnOpen', '78': 'gTheme_TitleFlashing', '79': 'gTheme_BackgroundFlashing',
    '80': 'gHelp_InstructionalButtons', '81': 'gTheme_FontTitle',
    '82': 'gTheme_FontUnselected', '83': 'gTheme_FontSelected', '84': 'gTheme_FontOptionCount',
    '87': 'gTheme_TextOutline', '88': 'gUI_OptionCountEnabled', '89': 'gUI_ScrollArrowsEnabled',
    '91': 'gHeader_EffectEnabled', '92': 'gSfx_Enabled', '93': 'gCustomScripts_Enabled',
    '94': 'gPlayer_ClearSpecialAbility',
    '95': 'gVehicle_SpawnInside', '96': 'gVehicle_MaxPerformance', '97': 'gVehicle_MaxVisual',
    '98': 'gVehicle_RandomColor', '99': 'gVehicle_PreventDespawn',
    '100': 'gUI_RowHeight',
    '129': 'gTick_InputConsumed', '130': 'gMenu_CurrentPage', '131': 'gTick_InputCooldownUntil',
    '132': 'gCustomScripts_Count', '133': 'gCustomScripts_CanAdd',
    '134': 'gQueue_PendingScript', '135': 'gQueue_RequestSent', '136': 'gQueue_PendingStack',
    '137': 'gBits_Features0', '138': 'gBits_Features1', '139': 'gBits_Features2',
    '140': 'gBits_Features3', '141': 'gBits_Features4', '142': 'gBits_Features5',
    '143': 'gBits_Features6', '144': 'gMenu_SubMode', '145': 'gBits_Features8',
    '146': 'gBits_Features9', '147': 'gBits_Features10',
    '148': 'gMenu_SubMode2', '149': 'gMenu_SubMode3',
    '150': 'gHelp_CustomKeysFrame',               # VERIFIED: per-frame "custom help drawn" flag — NOT free for vNext!
    '173': 'gList_RowCounter', '174': 'gMenu_PageStackDepth',
    '197': 'gInput_SelectedRow', '198': 'gInput_PrevSelectedRow',
    '199': 'gScaleform_Handle0', '200': 'gScaleform_Handle1', '201': 'gScaleform_Handle2',
    '202': 'gScaleform_HelpBar',
    '204': 'gInput_BackKey', '205': 'gInput_BackKeyAlt',
    '214': 'gUI_RowCounter', '223': 'gUI_RowsPerPage', '224': 'gUI_RowY',
    '225': 'gHighlight_Themed', '226': 'gUI_TextPadY',
    '227': 'gHighlight_W', '228': 'gHighlight_H',
    '229': 'gHighlight_R', '230': 'gHighlight_G', '231': 'gHighlight_B',
    '232': 'gIcon_W', '233': 'gIcon_H',
    '234': 'gTheme_HeaderR', '235': 'gTheme_HeaderG', '236': 'gTheme_HeaderB',
    '238': 'gTheme_HeaderR2', '239': 'gTheme_HeaderG2', '240': 'gTheme_HeaderB2',
    '241': 'gTheme_TextSelectedR', '242': 'gTheme_TextSelectedG', '243': 'gTheme_TextSelectedB',
    '244': 'gTheme_TextOutlineHeader',
    # page-stack arrays (verified via Menu_PushPage / Input_HandleScrollNav)
    '175': 'gMenu_PageStack_0', '186': 'gMenu_SelStack_0',
    # v2 queue (post-errata FREE slots — verified unused in v1)
    '400': 'gQueue2_Head', '401': 'gQueue2_Tail', '402': 'gFeature_UseVNextLoader',
}
# icon-id palette slots 3..27 hold button-sprite ids (init 0,4..7,12..16,21..25,30..39)
for _i in range(3, 28):
    S1[str(_i)] = f'gTheme_IconId_{_i:02d}'

S2 = {
    '267': 'gUI_RowWindowMax',
    '268': 'gTheme_TextUnselectedR', '269': 'gTheme_TextUnselectedG', '270': 'gTheme_TextUnselectedB',
    '351': 'gHelp_BarInitialized', '352': 'gHelp_SlotCounter',
    '353': 'gHighlight_TexDict', '354': 'gHighlight_TexName', '355': 'gHighlight_TexPadX',
    '356': 'gHighlight_TexBgName', '357': 'gLang_Spanish',      # 1 = Español (was gLang_IsEnglish — INVERTED!)
    '358': 'gUI_TextRowY', '359': 'gTmp_SpriteNameBuf', '362': 'gUI_TextRowX',  # 362 was gUI_TextWrap (WRONG: it is an X coord)
    '370': 'gWorld_ClearAreaMode', '373': 'gUI_RowsPerPageChoice',
    '390': 'gCustomScript_NameBuf',
    # v2 FIFO slot arrays (verified free in v1)
    '434': 'gQueue2_Script_0', '435': 'gQueue2_Script_1', '436': 'gQueue2_Script_2', '437': 'gQueue2_Script_3',
    '438': 'gQueue2_Stack_0', '439': 'gQueue2_Stack_1', '440': 'gQueue2_Stack_2', '441': 'gQueue2_Stack_3',
    '450': 'gQueue2_LoadStartMs',
}

def apply_overrides(path):
    data = json.loads(path.read_text())
    lab, s1, s2 = data['labels'], data['statics1'], data['statics2']
    renamed_owners = {k: v for k, v in LABELS.items()}
    # 1) function labels
    for old, new in LABELS.items():
        if old in lab or old.startswith('Label_'):
            prev = lab.get(old)
            lab[old] = new
    # 2) internal jump labels (owner__suffix), re-anchored to final owner names
    for jlab, (owner, suffix) in INTERNALS.items():
        lab[jlab] = f'{owner}__{suffix}'
    # 3) re-anchor any old "OldOwner__suffix" names to the new owner name
    old_owner_names = {  # new -> previous heuristic name used as prefix in full map
        'Tick_InputQueueAndToggles': 'Tick_HandleInputAndQueue',
        'UI_PrintRow': 'UI_Draw_TextRow',
        'UI_RenderRow': 'UI_Draw_TextRow_Internal',
        'UI_DrawRowIcons': 'UI_Draw_IconPlus',
        'UI_DrawRowHighlight': 'UI_Update_HighlightRect',
        'Menu_HandleBack': 'Func_Label_275',
    }
    for k, v in list(lab.items()):
        for new_o, old_o in old_owner_names.items():
            if isinstance(v, str) and v.startswith(old_o + '__'):
                lab[k] = new_o + '__' + v[len(old_o) + 2:]
    # 4) statics
    for k, v in S1.items():
        s1[k] = v
    for k, v in S2.items():
        s2[k] = v
    data['meta'] = {
        'verified': 'docs/LOADER_AUDIT_VERIFIED.md',
        'note': 'Names for loader/UI/input/theme cluster audited by code reading; rest heuristic.',
    }
    path.write_text(json.dumps(data, indent=1, sort_keys=True))
    print(f'{path.name}: labels={len(lab)} s1={len(s1)} s2={len(s2)}')

if __name__ == '__main__':
    apply_overrides(ROOT / 'rename_map.json')
    apply_overrides(ROOT / 'rename_map_full.json')
