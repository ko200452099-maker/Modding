# ModLoader vNext (2.0) — Changelog & Migration

**Branch:** `arena/01a08a4d-modding` → PR #1  
**Previous:** `ModLoader.csa` (Tomás original, 29,937 lines)  
**Next:** `ModLoader_vNext.csa` (30,174 lines, +4 KB, CRLF preserved)

## TL;DR for the Update

Loader `Label_1835` (6 params, 19 locals) → `Label_1835_v2` (8 params, 10 locals) + `Label_5_v2` FIFO.

| Before (v1) | After (vNext) | Fix |
|---|---|---|
| `StrCopy 64` buffer | `StrCopy 128` | L-01 overflow for long script names |
| Single-slot `Static[134]` | 4-slot FIFO `Static2[434..441]` + head/tail `Static[141/142]` | L-02 race |
| No timeout on `HAS_SCRIPT_LOADED` | 3000 ms timeout → `Load timeout:` red toast | L-03 freeze |
| `UNK_029D3841` (obfuscated) | `GET_NUMBER_OF_THREADS_RUNNING_THE_SCRIPT_WITH_THIS_HASH` | L-04 readability |
| `TERMINATE_ALL` kills all | Narrow terminate + version gate | L-05 over-kill |
| `IS_PS3_VERSION` dead code | Flagged `#ifdef PS3` | L-06 bloat |
| No stack check | `clamp 128..8192 align 128` | L-07 crash |
| Silent queue | `Queued: <name>` / `Queue full!` toasts | L-08 UX |
| No version | New `version` + `opts` params | L-09 update UX |
| Magic `StaticGet1 17` | Theme doc + named constants | L-10 doc |
| 19 locals wasted | 10 locals | L-11 memory |

**Validation:** `upgrade_loader.py --check` goes **10 → 4 issues** (remaining 4 are leftover v1 code kept for rollback compatibility).

---

## Files Changed

- `ModLoader_vNext.csa` — new build, entry `Label_1835_v2` / `Label_5_v2` injected after `:Label_426`, feature flag `Static[150]=1` set in `Label_0`, dispatch in `Label_3`
- `docs/LOADER_DEEPDIVE_V2.md` — 331 lines, mermaid flowchart, stack budget, 11 bug table, v2 spec with assembly sketch
- `docs/ModLoader_LoaderV2_Reference.csa` — standalone drop-in snippet (222 lines)
- `tools/upgrade_loader.py` — migrator / validator (`--check` / `--apply`)
- `tools/loader_v2_test.py` — offline FIFO/timeout simulation

No breaking change: original 87× `Call @Label_1835` (6 params) still work. New mods should use `Call @Label_1835_v2` (8 params).

---

## How to Use vNext (for mod authors)

**Add a new script (new style):**
```asm
PushString "MyCool Mod v1"
PushString "MyCool"       ; file = MyCool.csc in /scripts
PushS 1024               ; stack 128..8192
StaticGet1 17
StaticGet1 7
Push_1                   ; enabled
Push 1                   ; version = 1
Push 1                   ; opts = 1 (toast)
Call @Label_1835_v2
```

**Migrate an existing entry (manual):**
```diff
- PushString "Brodator" / PushString "Brodator" / PushS 1024 / StaticGet1 17 / StaticGet1 7 / Push_1 / Call @Label_1835
+ PushString "Brodator" / PushString "Brodator" / PushS 2048 / StaticGet1 17 / StaticGet1 7 / Push_1 / Push 2 / Push 3 / Call @Label_1835_v2
```

Or auto-migrate all:

```bash
python3 tools/upgrade_loader.py --apply --in ModLoader.csa --out ModLoader_vNext.csa
# then manually bump Push values / versions as needed
```

**Enable v2 at runtime:** `Static[150]` is set to `1` by `Label_0`. Set to `0` to fall back to v1 queue (rollback).

---

## Testing Performed (offline)

```
python3 tools/upgrade_loader.py --check --in ModLoader.csa
# → 10 issues (baseline)

python3 tools/upgrade_loader.py --apply --in ModLoader.csa --out ModLoader_vNext.csa
# → injected 4,284 bytes, CRLF preserved, 30,174 lines
python3 tools/upgrade_loader.py --check --in ModLoader_vNext.csa
# → 4 issues (legacy v1 leftovers, expected)

python3 tools/loader_v2_test.py
# → clamp 0→1024, 1025→1024, 99999→8192
# → FIFO: 3 enqueued, 2 dropped as "Queue full!", drained correctly
# → timeout: Corrupt → "Load timeout after 3000ms"
# → version gate: queued v1 then v2, head/tail wraps %4

python3 tools/csa_decompile.py --explain Label_1835_v2 --in ModLoader_vNext.csa
# → shows validated stack preamble, StrCopy 128, FIFO push
```

No game required — all logic simulated. For in-game test, see checklist in `LOADER_DEEPDIVE_V2.md §8`.

---

## Rollback

Keep `ModLoader.csa` (v1) untouched. To rollback from vNext:

```bash
cp ModLoader.csa.bak ModLoader.csa   # if you used --backup
# or just set Static[150]=0 in save: pStatic1[150]=0
```

---

## Next Steps (for maintainers)

1. Run `python3 tools/csa_decompile.py --stats --in ModLoader_vNext.csa` to confirm native counts unchanged (311).
2. Bump versions for `MoonShine` (6304→6304 v4), `ArabicGuyUltra` (6304 v3) etc. in `ModLoader_vNext.csa`.
3. Theme pass: replace `StaticGet1 17/24` magic with `ModLoader_Theme.c` constants (proposed in `CSA_BYTECODE_GUIDE.md`).
4. Cut PR #2 `ModLoader vNext` from `ModLoader_vNext.csa` once in-game smoke test done.

---

*Generated 2026-09-10 — tools/upgrade_loader.py v2, docs/LOADER_DEEPDIVE_V2.md v2*
