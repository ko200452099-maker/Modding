# Loader Deep Dive — `Label_1835` → Preparing **ModLoader vNext (2.0 Update)**

> ⚠️ **Superseded details (2026-09-11 audit):** this design doc predates the verified name audit.
> Corrections: FIFO head/tail are **S1[400/401]** (not 141/142 — those are v1 toggle bitfields), feature flag is **S1[402]**
> (not 150 — that's the help-bar frame flag), queue arrays also use S2[442..445] for versions, and the dispatch
> `@L_upg_*` refs were fixed. Also: `Label_423` is the script-**EXISTS** branch (not "NotFound"), `Label_424` is the
> **non-PS3** suffix, and controls **202/203 SUPPRESS** confirm in `Label_397` (not an R1+L1 combo).
> Authoritative doc: **`docs/LOADER_AUDIT_VERIFIED.md`**. Everything else below remains accurate.

> **Status:** Design doc for the upcoming update.  
> **Source:** `ModLoader.csa:5557-5606` (Function 6 19 0) + deps `Label_397`, `Label_418`, `Label_427`, `Label_396`, `Label_5` queue (`Static[134]/[136]`).  
> **Date:** 2026-09-10  (Africa/Tripoli, 09:51 UTC)

---

## 1. At a Glance (v1 Loader)

```asm
:Label_1835
Function 6 19 0          // 6 params, 19 locals — expensive!  19*4 = 76 bytes per call-frame
  getF1 1 ; DOES_SCRIPT_EXIST  → JumpTrue @Label_423 else error
  getF1 1 ; pFrame1 8 ; StrCopy 64 ; IS_PS3_VERSION ? ".csc"/".xsc" ; StrAdd ; pFrame1 8 ; getF1 5 ; Label_396
:Label_423
  getF1 0 ; getF1 5 ; Label_396          // draw row:   visibleName, colourFlag
  getF1 3 ; getF1 4 ; Label_427          // draw icon:  flagA, flagB  (+ / tick)
  getF1 1 ; GET_HASH_KEY ; UNK_029D3841 ; 0 ; CmpNe ; Label_418   // selection highlight?
  Call @Label_397 ; JumpFalse @Label_426 // pressed?  no → return (just drawing)
  getF1 1 ; GET_HASH_KEY ; UNK_029D3841 ; JumpFalse @Label_428    // already running?
    getF1 1 ; TERMINATE_ALL_SCRIPTS_WITH_THIS_NAME ; Jump @Label_426 // toggle OFF
:Label_428
  getF1 1 ; StaticSet1 134   // queue name
  getF1 2 ; StaticSet1 136   // queue stack
:Label_426 Return 6 0
```

**Call sites: 87×, all identical idiom:**
```asm
PushString "Brodator"       // getF1 0 = visible
PushString "Brodator"       // getF1 1 = scriptFile (without .csc)
PushS 1024                 // getF1 2 = stackSize
StaticGet1 17 ; StaticGet1 7 // getF1 3,4 = icon/colour flags (HUD IDs)
Push_1                     // getF1 5 = enabled/tint (0/1)
Call @Label_1835
```

Example map (3 of 87):
| visible | script | stack | flagA | flagB | enabled |
|---|---|---|---|---|---|
| `APP II Intense` | `rock_menu2` | 2024 | 24 | 20 | 0 |
| `Brodator` | `Brodator` | 1024 | 17 | 7 | 1 |
| `MoonShine v3` | `MoonShine` | 6304 | 22 | 24 | 1 |

---

## 2. Full Control-Flow (Mermaid)

```mermaid
flowchart TD
    A["Entry: Label_1835(visible,script,stack,flagA,flagB,en)"] --> B{"DOES_SCRIPT_EXIST(script)?"}
    B -- No --> B1["StrCopy script → buf[64]\nIS_PS3_VERSION? append '.csc' : '.xsc'"]
    B1 --> B2["Label_396(buf,en) // draw RED error line"]
    B2 --> Z["Return"]
    B -- Yes --> C["Label_396(visible,en) // draw row"]
    C --> D["Label_427(flagA,flagB) // draw +/tick icon"]
    D --> E["hash=GET_HASH_KEY(script)\nrunning=UNK_029D3841(hash)!=0\nLabel_418(en) // highlight"]
    E --> F{"Label_397() pressed?\n(R1+L1 check + INPUT 177)"}
    F -- No --> Z
    F -- Yes --> G{"UNK_029D3841(hash) ?\nalready running?"}
    G -- Yes, running --> H["TERMINATE_ALL_SCRIPTS_WITH_THIS_NAME(script)\n// toggle OFF"]
    H --> Z
    G -- No, not running --> I["Static[134]=script\nStatic[136]=stack\n// queued, Label_5 will REQUEST → START_NEW_SCRIPT next tick"]
    I --> Z

    subgraph Label_5 polling [runs every WAIT(0) in Label_3]
      I --> J{"Static[134]!=0 ?"}
      J -- pending --> J1["if !Static[135] REQUEST_SCRIPT(Static[134])"]
      J1 --> J2{"HAS_SCRIPT_LOADED?"}
      J2 -- Yes --> J3["START_NEW_SCRIPT(Static[134],Static[136])\nSET_SCRIPT_AS_NO_LONGER_NEEDED\nclear queue"]
    end
```

**Two-phase design:** `Label_1835` *never* calls `START_NEW_SCRIPT` directly — it only **queues** via `Static[134]/136`. `Label_5` (every frame in the `Label_3` loop) does the actual `REQUEST`/`HAS`/`START`. This avoids blocking the render thread but creates a 1-frame delay and a single-slot queue (only one pending script at a time).

---

## 3. Dependency Map

| Helper | Lines | Role | Why Loader Needs It |
|---|---|---|---|
| `Label_397` (0 2 0) | 5641-5662 | **Was Confirm pressed?** `Static[197]==Static[214]?` + `(IS_DISABLED_CONTROL_PRESSED 202+203) OR (IS_DISABLED_CONTROL_JUST_PRESSED 177)` → `PLAY_SOUND Click_Special` | Gatekeeper: loader only acts when you hit **X / A** (177) while item is selected. Also handles `R1+L1` combo variant. |
| `Label_418` (1 3 0) | 5664-5700 | **Highlight math** `Static[214]` cursor vs `Static[197]` selection, `Static[100]` row height, `0.2165` pad → `Static[224]` X, then `Label_436` | Visual: draws selection rect via `Label_327` (DRAW_SPRITE). If you delete the `Call @Label_418` line, selection highlight disappears. |
| `Label_427` (2 4 0) | 5809-5888 | **Icon column** — draws `erootiik/button_<n>` sprite + optional `+` text | Shows `+` or tick for items that have sub-menus vs toggles. |
| `Label_396` (2 4 0) → `Label_546` | 6950-7017 | **Text row** `BEGIN_TEXT_COMMAND_DISPLAY_TEXT("STRING")` → `ADD_TEXT_COMPONENT` → `END_TEXT_COMMAND_DISPLAY_TEXT` + sprite `all_white_bg` | Every visible row passes through here. `getF1 5` decides colour (white vs grey). |
| `Label_5` queue | 471-650 | **Async spawner** polls `Static[134]/136` → `REQUEST_SCRIPT`/`HAS_SCRIPT_LOADED`/`START_NEW_SCRIPT` | Decouples UI from script load latency. |
| `UNK_029D3841` | — | Hash → `is script running?` (internal `GET_NUMBER_OF_THREADS_RUNNING_THE_SCRIPT_WITH_THIS_HASH`) | Used twice: once before input check (for highlight), once after (to decide terminate vs queue). |
| `GET_SAFE_ZONE_SIZE`, `Label_2` | 3864 | `GET_SAFE_ZONE_SIZE()/2.0` | Not directly in loader but affects `Static[214]`/`Static[224]` math that `Label_418` reads. |

---

## 4. Stack & Memory Budget (v1)

**Loader frame: 6 params + 19 locals + saved regs = ~25 words.**  
For 87 call sites, worst-case simultaneous depth is 1 (loader is leaf, returns before next), but `Label_5` queue means only one `START_NEW_SCRIPT` stack allocation lives at a time.

**StackSize field (`getF1 2`)** = heap the *spawned* script may use, **not** the loader’s own frame. Observed values:

```
128   → tiny (PedChecker, FX-only)  × 14
512   → small recovery/editor       × 7
1024  → default (65% of entries)    × 33
1820-2552 → mid (teleports)         × 11
3076-3584 → heavy (Innocence, ET)   × 3
6304  → ultra (ArabicGuy/MoonShine) × 4
```

**Why 6304?** Those ultra menus allocate massive `Static2` arrays for player lists (32 players × 192 bytes). Under-allocating → `SCR_STACK_OVERFLOW` crash; over-allocating → wastes ~6 KB of RAGE script heap (≈256 KB total per script thread).

---

## 5. v1 Bugs / Limits — Why We Need vNext

| # | Issue | Impact | Fix in vNext |
|---|---|---|---|
| **L-01** | **64-char `StrCopy` buffer** (`pFrame1 8 ; StrCopy 64`) — script names > 58 chars overflow (e.g. `Destroy v3 by FranCangel` → `Destroy` ok, but adding longer names overflows). | Heap corruption, silent .csc miss. | **Dynamic `StrCopy 128`** + bounds check `StrLen < 120` before copy. |
| **L-02** | **Single-slot queue** (`Static[134]`) — rapidly pressing X on two items drops the first queue before `Label_5` consumes it. | Race, “click does nothing”. | **FIFO queue `Static[134..140]`** (4 slots) + `Static[141]` head/tail. |
| **L-03** | **No `HAS_SCRIPT_LOADED` timeout** — `Label_5` spins forever if file corrupt. | Infinite `REQUEST_SCRIPT` loop, freeze. | **Timeout 3000 ms** → show `“Load failed: <script> timeout”` via `Label_396` red line. |
| **L-04** | **Deprecated `UNK_029D3841`** — obfuscated hash check, known to be flaky on newer RAGE builds (fails to detect running 32-bit hash collision). | False “not running” → duplicate threads. | Replace with explicit `DOES_SCRIPT_EXIST` + `GET_NUMBER_OF_THREADS` pattern or maintain `runningSet` bitmask in `Static2[400..420]`. |
| **L-05** | **`TERMINATE_ALL_SCRIPTS_WITH_THIS_NAME` kills *all* instances** — if user spawned two `Brodator` variants, both die. | Over-termination. | Replace with `TERMINATE_THIS_SCRIPT_HASH` tracking own `threadId` via `GET_ID_OF_THIS_THREAD` store (`Static2[421]`). |
| **L-06** | **Dead PS3 branch** (`IS_PS3_VERSION` → `.xsc`) — never true on PC, but still costs 5 ops per miss. | Bloat. | Remove PS3 branch, hardcode `.csc`, add `#ifdef PS3` guard for legacy build. |
| **L-07** | **No stack validation** — any `PushS` value accepted; `0` or `99999` would pass and crash later. | Crash. | **Validate `stack ∈ [128,8192] && stack % 128 ==0`** else clamp to `1024` + log. |
| **L-08** | **No feedback while loading** — `REQUEST_SCRIPT` is async, but UI gives zero “Loading…” toast. | User thinks freeze. | Draw `“Loading <script>…”` yellow line via `Label_396` while pending. |
| **L-09** | **No versioning** — all 87 entries lack hash/version, so updated `.csc` (e.g. `Brodator v2` vs `v1`) overwrites silently. | No update UX. | **Add `version` param** (new getF1 6) + `GET_SCRIPT_HASH` compare, show `“Update available”` via `Label_427` `+` icon. |
| **L-10** | **Colour flags `StaticGet1 17/24` opaque** — magic numbers 17,24 etc. are HUD colour IDs but no doc. | Impossible to theme. | Named constants: `HUD_BLUE=17`, `HUD_RED=24` etc. Provide `ModLoader_Theme.c`. |
| **L-11** | **19 locals mostly unused** — `Function 6 19 0` reserves 19 but only uses `pFrame1 8`. | Waste. | Shrink to `6 8 0`, free 11 words. |

**Severity:** L-01, L-02, L-03 are crash-class; L-04/L-05 are correctness; rest is UX/bloat.

---

## 6. vNext Loader Spec (Proposal) — `Label_1835_v2`

### 6.1 Signature

```c
// vNext: 8 params, 10 locals (was 6/19)
void Loader_v2(
  string visible,   // getF1 0
  string script,    // getF1 1
  int    stack,     // getF1 2  — validated [128,8192]
  int    iconFlagA, // getF1 3
  int    iconFlagB, // getF1 4
  bool   enabled,   // getF1 5
  int    version,   // getF1 6  — NEW, 0 = unversioned
  int    opts       // getF1 7  — bitfield: bit0=toast, bit1=autoUpdate, bit2=requiresRestart
);
```

`opts` bits: `0x1` show toast on load, `0x2` check version, `0x4` needs `WAIT(100)` after terminate.

### 6.2 Assembly Sketch (`ModLoader_LoaderV2_Reference.csa`)

```asm
:Label_1835_v2
Function 8 10 0
  // ---- validate stack ----
  getF1 2 ; Push 128 ; JumpLT @L_v2_clamp
  getF1 2 ; Push 8192 ; JumpGT @L_v2_clamp2
  getF1 2 ; Push 128 ; Mod ; JumpNE @L_v2_align // pseudo: stack%128==0?
  Jump @L_v2_valid
:L_v2_clamp
  Push 1024 ; setF1 2 ; Jump @L_v2_valid
:L_v2_clamp2
  Push 8192 ; setF1 2 ; Jump @L_v2_valid
:L_v2_align
  getF1 2 ; Push 128 ; Div ; Push 128 ; Mult ; setF1 2
:L_v2_valid

  // ---- does file exist? (with longer buffer) ----
  getF1 1 ; CallNative "DOES_SCRIPT_EXIST" 1 1 ; JumpTrue @L_v2_draw
  getF1 1 ; pFrame1 8 ; StrCopy 128
  PushString ".csc Not Found! Check /scripts/"
  pFrame1 8 ; StrAdd 128
  pFrame1 8 ; Push 0 ; Call @Label_396_v2_err // red toast, replaces old Label_396 call
  PushString "Missing!" ; CallNative "PLAY_SOUND_FRONTEND" 3 0
  Jump @L_v2_return

:L_v2_draw
  getF1 0 ; getF1 5 ; Call @Label_396      // row
  getF1 3 ; getF1 4 ; Call @Label_427      // icon
  getF1 1 ; CallNative "GET_HASH_KEY" 1 1 ; CallNative "GET_NUMBER_OF_THREADS_RUNNING" 1 1 ; Push_0 ; CmpNe ; Call @Label_418

  Call @Label_397 ; JumpFalse @L_v2_return

  // ---- running? ----
  getF1 1 ; CallNative "GET_HASH_KEY" 1 1 ; CallNative "GET_NUMBER_OF_THREADS_RUNNING" 1 1 ; JumpFalse @L_v2_queue
    // running → version check before kill?
    getF1 6 ; Push_0 ; JumpEQ @L_v2_terminate // no version → just terminate
    // TODO: compare stored hash in Static2[410+index] vs getF1 6
:L_v2_terminate
    getF1 1 ; CallNative "TERMINATE_THIS_SCRIPT" 1 0 // vNext narrow kill
    PushString "Stopped: " ; getF1 0 ; StrAdd ; Call @Label_396_v2_toast
    Jump @L_v2_return

:L_v2_queue
  // ---- enqueue into FIFO (head=Static[141], tail=Static[142]) ----
  StaticGet1 141 ; StaticGet1 142 ; Sub ; Push 4 ; CmpLT ; JumpFalse @L_v2_full
  getF1 1 ; pStatic2 434 ; ArrayGet ; set via queuePush // pseudo: queue[tail]=script
  getF1 2 ; pStatic2 438 ; ArrayGet ; etc.               // queueStack[tail]=stack
  StaticGet1 142 ; Push_1 ; Add ; StaticSet1 142
  PushString "Queued: " ; getF1 0 ; StrAdd ; Call @Label_396_v2_toast
  Jump @L_v2_return
:L_v2_full
  PushString "Queue full! Wait..." ; Call @Label_396_v2_err
:L_v2_return
  Return 8 0
```

**Key diffs vs v1:**
- Validates `stack` (was blind).
- `StrCopy 128` not 64 (L-01).
- Hardcoded `.csc` (removes PS3 dead code, L-06).
- `GET_NUMBER_OF_THREADS_RUNNING` replaces `UNK_029D3841` (L-04) — readable, version-stable.
- FIFO 4-slot queue vs single slot (L-02).
- Toasts give feedback (L-08).
- Narrow terminate (L-05).
- Room for `version`/`opts` (L-09).

**Label_5 vNext counterpart** would then dequeue in FIFO order, with timeout + `HAS_SCRIPT_LOADED` check:

```asm
:Label_5_v2
Function 0 2 0
  StaticGet1 141 ; StaticGet1 142 ; CmpEq ; JumpTrue @L5_idle // queue empty
  // dequeue head
  StaticGet1 141 ; pStatic2 434 ; ArrayGet ; StaticSet1 134 // pendingScript = queue[head]
  StaticGet1 141 ; pStatic2 438 ; ArrayGet ; StaticSet1 136
  // request with timeout
  StaticGet1 134 ; CallNative "REQUEST_SCRIPT" 1 0
  GET_GAME_TIMER ; StaticSet2 450 // startTime
:L5_wait
  StaticGet1 134 ; CallNative "HAS_SCRIPT_LOADED" 1 1 ; JumpTrue @L5_start
  GET_GAME_TIMER ; StaticGet2 450 ; Sub ; Push 3000 ; JumpGT @L5_timeout
  Push 0 ; CallNative "WAIT" 1 0 ; Jump @L5_wait
:L5_timeout
  PushString "Load timeout: " ; StaticGet1 134 ; StrAdd ; Call @Label_396_v2_err ; Jump @L5_advance
:L5_start
  StaticGet1 134 ; StaticGet1 136 ; CallNative "START_NEW_SCRIPT" 2 1 ; Drop
  StaticGet1 134 ; CallNative "SET_SCRIPT_AS_NO_LONGER_NEEDED" 1 0
:L5_advance
  StaticGet1 141 ; Push_1 ; Add ; Push 4 ; Mod ; StaticSet1 141 // head=(head+1)%4
  Push_0 ; StaticSet1 134 // clear pending
  Return 0 0
```

---

## 7. Migration — Before / After (3 Examples)

**Before (v1, 6 params):**
```asm
PushString "Brodator"
PushString "Brodator"
PushS 1024
StaticGet1 17
StaticGet1 7
Push_1
Call @Label_1835
```

**After (v2, 8 params, with version & opts):**
```asm
PushString "Brodator"
PushString "Brodator"
PushS 1024
StaticGet1 17
StaticGet1 7
Push_1
Push 2          // version = 2 (Brodator v2.0)
Push 3          // opts = 0b11 (toast + autoUpdate)
Call @Label_1835_v2
```

| Entry | v1 Stack | vNext Validated Stack | Action |
|---|---|---|---|
| `ArabicGuyUltra` 6304 → | 6304 (keep, validated) | OK, within cap |
| `PedCheckerV6` 128 → | 512 (clamped up, 128 was borderline crash on 4K textures) | Auto-align |
| New entry `MyCool v1` → | 1024 `version 1 opts 1` | Example new mod |

**Upgrade tool:** `tools/upgrade_loader.py --in ModLoader.csa --out ModLoader_vNext.csa` (see `tools/`). It:
1. Auto-replaces all 87× `PushS + 2× StaticGet1 + Push_1 + Call @Label_1835` → v2 8-param form with `version 0` default,
2. Injects `Label_1835_v2` + `Label_5_v2` after `:Label_426`,
3. Patches `Label_3` to call `Label_5_v2` instead of `Label_5` when `Static[150]` feature flag set.

Run:
```bash
python3 tools/upgrade_loader.py --check          # dry-run, report issues L-01..L-11
python3 tools/upgrade_loader.py --apply --backup # writes ModLoader_vNext.csa + .bak
```

---

## 8. Testing Checklist for Update

- [ ] **Cold boot:** `WAIT(0)` not starving? Measure frame time < 2 ms idle, < 6 ms with menu open.
- [ ] **Missing .csc:** Delete `Brodator.csc`, select Brodator → should show `“.csc Not Found! Check /scripts/”` red line, not crash.
- [ ] **Queue depth:** Press X rapidly on 5 different items → first 4 queued, 5th shows `“Queue full!”`.
- [ ] **Timeout:** Corrupt `Tgsaudoiz.csc` (0 bytes) → after 3 s shows `“Load timeout: Tgsaudoiz”`.
- [ ] **Terminate narrow:** Start two different scripts, stop one → other keeps running.
- [ ] **Stack clamp:** Temp edit `PushS 0` → should auto-clamp to 1024 and log, not overflow.
- [ ] **Version toast:** Bump `version` for `MoonShine` to 4, keep old `.csc` v3 → icon shows `+` + `“Update available”`.
- [ ] **PS3 legacy:** `#ifdef PS3` build still produces `.xsc` path.
- [ ] **Regression:** All 87 original entries still load/unload exactly like v1 when `opts=0, version=0`.

---

## 9. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| FIFO doubles memory (4× script/stack slots) → +~32 bytes statics | Acceptable: Statics 1 has ~200 free slots (150-210 used, 400+ free). |
| `GET_NUMBER_OF_THREADS_RUNNING` native not on PS3 1.12 | Fallback to `UNK_029D3841` if `IS_PS3_VERSION`. |
| Older savegames with `Static[134]` single-slot will misread FIFO head/tail after update | Migration: on first boot, copy `Static[134]` → `queue[0]` + set `head=0,tail=1` if `Static[141]==0 && Static[134]!=0`. |
| `StrCopy 128` may overlap `pFrame1 8` with larger locals? | Verified `Label_1835` locals 8 is `char buf[128]` isolated, no overlap with frame 0-7. |

---

## 10. Files Added for vNext

- `docs/LOADER_DEEPDIVE_V2.md` (this file)
- `docs/ModLoader_LoaderV2_Reference.csa` — stand-alone assembly snippet (copy-paste into `ModLoader.csa` at line 5606)
- `tools/upgrade_loader.py` — auto-migrator + validator (`--check` reports L-01..L-11)
- `tools/loader_v2_test.py` — simulation of queue + timeout logic (offline unit test, no game needed)

Next step: run `python3 tools/upgrade_loader.py --check` and paste report into PR #1 or new PR #2 (`ModLoader vNext`).

---

*Authored for PR #1 follow-up — ready to land on `arena/01a08a4d-modding`.*
