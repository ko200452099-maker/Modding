#!/usr/bin/env python3
"""
upgrade_loader.py — ModLoader Loader v1 → v2 migrator / validator

Checks L-01..L-11 (see LOADER_DEEPDIVE_V2.md), and optionally patches
ModLoader.csa to inject Loader_v2 (Label_1835_v2 + Label_5_v2).

Usage:
  python3 tools/upgrade_loader.py --check --in ModLoader.csa
  python3 tools/upgrade_loader.py --apply --in ModLoader.csa --out ModLoader_vNext.csa --backup
  python3 tools/upgrade_loader.py --check --in docs/ModLoader_LoaderV2_Reference.csa
"""
import re, argparse, pathlib, sys, collections, shutil

ISSUES = {
 "L-01": "64-char StrCopy buffer overflow risk",
 "L-02": "Single-slot queue (Static[134] race)",
 "L-03": "No HAS_SCRIPT_LOADED timeout",
 "L-04": "UNK_029D3841 deprecated hash check",
 "L-05": "TERMINATE_ALL kills all instances (over-termination)",
 "L-06": "Dead PS3 .xsc branch bloat",
 "L-07": "No stack validation",
 "L-08": "No loading feedback toast",
 "L-09": "No versioning",
 "L-10": "Magic HUD colour IDs opaque",
 "L-11": "19 locals over-reserved",
}

def load(path):
    with open(path, 'rb') as f:
        data=f.read()
    # detect CRLF
    has_crlf = b'\r\n' in data
    txt=data.decode('utf-8', errors='replace')
    # normalize to \n for internal processing, but keep flag
    if has_crlf:
        txt=txt.replace('\r\n','\n')
    lines=txt.splitlines()
    return txt, lines

def check(path):
    txt, lines = load(path)
    print(f"Checking {path} ({len(lines)} lines) ...\n")
    findings=[]

    # L-01: StrCopy 64 near DOES_SCRIPT_EXIST
    for i,l in enumerate(lines):
        if 'StrCopy 64' in l and i>0 and 'pFrame1 8' in lines[max(0,i-1)]:
            # look back 5 lines for DOES_SCRIPT_EXIST
            ctx="\n".join(lines[max(0,i-5):i+1])
            if 'DOES_SCRIPT_EXIST' in ctx:
                findings.append(("L-01", i+1, "Loader StrCopy 64 — should be 128 for long script names"))
                break

    # L-02: single slot
    if 'StaticSet1 134' in txt and 'StaticSet1 401' not in txt:
        findings.append(("L-02", txt.index('StaticSet1 134'), "Single-slot queue Static[134] — FIFO 4-slot recommended"))

    # L-03: HAS_SCRIPT_LOADED timeout
    if 'HAS_SCRIPT_LOADED' in txt:
        # check if any Push 3000 or timeout nearby
        if 'Push 3000' not in txt:
            findings.append(("L-03", 0, "HAS_SCRIPT_LOADED without timeout — spins forever on corrupt .csc"))

    # L-04: UNK_029D3841
    cnt=txt.count('UNK_029D3841')
    if cnt:
        findings.append(("L-04", 0, f"UNK_029D3841 used {cnt}x — replace with GET_NUMBER_OF_THREADS_RUNNING_THE_SCRIPT_WITH_THIS_HASH"))

    # L-06: PS3 branch
    if 'IS_PS3_VERSION' in txt:
        ps3 = txt.count('IS_PS3_VERSION')
        findings.append(("L-06", 0, f"IS_PS3_VERSION {ps3}x — dead on PC, keep only #ifdef PS3"))

    # L-07: stack validation
    stacks = re.findall(r'PushS\s+(\d+)', txt)
    bad=[]
    for s in stacks:
        v=int(s)
        if v < 128 or v > 8192 or v%128!=0:
            bad.append(v)
    if bad:
        findings.append(("L-07", 0, f"Stack validation missing — {len(stacks)} PushS values, suspicious: {bad[:5]}"))
    else:
        # also if no validation code (no JumpLT/JumpGE on getF1 2)
        if 'getF1 2' in txt and 'JumpLT' not in txt.split('getF1 2')[0][-500:]:
            # heuristic: check loader header for validation
            if 'Label_1835' in txt:
                # look at loader region
                m=re.search(r':Label_1835.*?Return 6 0', txt, re.S)
                if m and 'Push 128' not in m.group(0):
                    findings.append(("L-07", 0, "Loader getF1 2 stack not validated (no 128/8192 clamp)"))

    # L-11: locals
    m=re.search(r':Label_1835\s*\nFunction\s+(\d+)\s+(\d+)\s+(\d+)', txt)
    if m:
        _, params, loc = m.groups()
        if int(loc) >= 15:
            findings.append(("L-11", 0, f"Function 6 {params} {loc} — 19 locals over-reserved (only pFrame1 8 used)"))

    # L-08 / L-09 / L-10 generic if v1 loader present but no v2
    if ':Label_1835_v2' not in txt:
        findings.append(("L-08", 0, "No loading toast — UI gives no 'Loading...' feedback"))
        findings.append(("L-09", 0, "No version param — can't show 'Update available'"))
        findings.append(("L-10", 0, "Magic flag IDs (StaticGet1 17/24) undocumented — need ModLoader_Theme.c"))
        # L-05
        if 'TERMINATE_ALL_SCRIPTS_WITH_THIS_NAME' in txt:
            findings.append(("L-05", 0, "TERMINATE_ALL kills all instances — use narrow terminate"))

    # Print
    if not findings:
        print("✅ No issues found — looks like v2 already!")
        return 0
    print(f"Found {len(findings)} issue(s):\n")
    for code, loc, msg in findings:
        desc=ISSUES.get(code, "")
        where = f"line {loc}" if isinstance(loc,int) and loc>0 and loc<100000 else "global"
        print(f"  {code} [{where}] {msg}")
        print(f"       → {desc}")
    print("\nSeverity: L-01..L-03 crash, L-04..L-05 correctness, rest UX/bloat")
    print("\nFix: python3 tools/upgrade_loader.py --apply --in ModLoader.csa --out ModLoader_vNext.csa")
    return len(findings)

def apply(inp, out, backup):
    ipath=pathlib.Path(inp)
    opath=pathlib.Path(out)
    txt, lines = load(str(ipath))
    if ':Label_1835_v2' in txt:
        print("Already contains v2 loader — skipping inject.")
        return

    # Backup
    if backup and opath.exists():
        shutil.copy2(opath, str(opath)+".bak")
    if backup:
        shutil.copy2(ipath, str(ipath)+".bak")
        print(f"Backup: {ipath}.bak")

    # Find insertion point: after :Label_426 Return 6 0 (end of v1 loader)
    # Locate ":Label_426\nReturn 6 0"
    loc = txt.find(":Label_426\nReturn 6 0")
    if loc == -1:
        # fallback: find "Return 6 0" after Label_1835
        m=re.search(r':Label_1835.*?Return 6 0', txt, re.S)
        if not m:
            print("Could not find v1 loader end — aborting")
            sys.exit(1)
        loc = m.end()

    # Load v2 reference
    v2path = pathlib.Path(__file__).parent.parent / "docs" / "ModLoader_LoaderV2_Reference.csa"
    if not v2path.exists():
        v2path = pathlib.Path("docs/ModLoader_LoaderV2_Reference.csa")
    v2txt = v2path.read_text(encoding='utf-8', errors='replace')

    newtxt = txt[:loc] + "\n\n; ===== vNext Loader injected by upgrade_loader.py =====\n" + v2txt + "\n; ===== end vNext =====\n" + txt[loc:]

    # Also patch 87 call sites optionally? For now we add v2 but keep v1 sites pointing to v1
    # Add a feature flag init in Label_0 or Label_1: Static[150]=1 means use v2 queue
    # Find Label_1 end (Return 0 0 after Label_1) and inject Static[150]=1
    # Label_1 is at ~29860: "... Push_1 ; StaticSet2 373 ; Return 0 0"
    # Simple: append after first Return 0 0 that follows :Label_1
    # Instead, we inject at end of Label_0's statics init block (before pStatic1 71)
    # Look for "\nPush_-1\nStaticSet1 128\n"
    marker = "Push_-1\nStaticSet1 128\n"
    if marker in newtxt:
        newtxt = newtxt.replace(marker, marker + "Push_1\nStaticSet1 402\n; vNext feature flag: 1=use FIFO queue (Static1[402] free; do NOT use 150 - v1 help-bar flag)\n", 1)
        print("Patched Static[402]=1 feature flag into Label_0 init")

    # Now we need to make Label_3 call Label_5_v2 when flag set
    # In Label_3: "Call @Label_5" -> we add conditional
    # Insert after Call @Label_5: check Static[150] -> call v2 pool?
    # Simpler: replace Call @Label_5 with check:
    old = "Call @Label_5\nCall @Label_6"
    if old in newtxt:
        new = "StaticGet1 402\nJumpFalse @Label_upg_use_v1queue\nCall @Label_5_v2\nJump @Label_upg_after_queue\n:Label_upg_use_v1queue\nCall @Label_5\n:Label_upg_after_queue\nCall @Label_6"
        # Need to ensure we have Jump logic — CSA allows JumpFalse
        newtxt = newtxt.replace(old, new, 1)
        print("Patched Label_3 to dispatch to Label_5_v2 when Static[402]==1")

    # preserve CRLF if original had it
    try:
        with open(inp, 'rb') as rf:
            had_crlf = b'\r\n' in rf.read(8192)
    except:
        had_crlf=False
    if had_crlf:
        newtxt = newtxt.replace('\n', '\r\n')
    opath.write_bytes(newtxt.encode('utf-8'))
    print(f"\n✅ Wrote {opath} ({len(newtxt.encode('utf-8'))//1024} KB, +{len(newtxt.encode('utf-8'))-len(txt.encode('utf-8'))} bytes)")
    print(f"   — v2 loader injected, flag Static[402]=1, head/tail Static1[400/401], 4 slots at Static2 434/438")
    print(f"   — Keep original 87× Call @Label_1835 as-is for rollback; new entries should use Call @Label_1835_v2 (8 params)")

    # Also write a report of call sites
    stacks = re.findall(r'PushString\s+"([^"]+)"\s*\nPushString\s+"([^"]+)"\s*\nPushS\s+(\d+)', newtxt)
    print(f"\nCall sites kept: {len(stacks)} (all still v1). To migrate one entry:")
    print('  PushString "MyMod"\n  PushString "MyMod"\n  PushS 1024\n  StaticGet1 17\n  StaticGet1 7\n  Push_1\n  Push 1   ; version\n  Push 1   ; opts=toast\n  Call @Label_1835_v2')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', default='ModLoader.csa')
    ap.add_argument('--out', dest='out', default='ModLoader_vNext.csa')
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--backup', action='store_true')
    args=ap.parse_args()
    if args.check:
        check(args.inp)
    elif args.apply:
        apply(args.inp, args.out, args.backup)
    else:
        check(args.inp)

if __name__=='__main__':
    main()
