#!/usr/bin/env python3
"""
regen_defines.py — regenerate docs/ModLoader_Defines.h from the existing header
(preserving prior curation) with AUDIT-VERIFIED overrides applied on top.
Source of truth for overrides: tools/build_verified_map.py (LABELS/S1/S2).
"""
import re, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build_verified_map import LABELS, S1, S2

ROOT = pathlib.Path(__file__).parent.parent
HDR = ROOT / 'docs' / 'ModLoader_Defines.h'
old = HDR.read_bytes().decode('utf-8', 'replace').replace('\r\r\n', '\n').replace('\r\n', '\n').replace('\r', '\n')

labels, s1, s2 = {}, {}, {}
for name, num in re.findall(r'#define\s+(\w+)\s+Label_(\d+)', old):
    labels[int(num)] = name
for name, num in re.findall(r'#define\s+(\w+)\s+Static1\[(\d+)\]', old):
    s1[int(num)] = name
for name, num in re.findall(r'#define\s+(\w+)\s+Static2\[(\d+)\]', old):
    s2[int(num)] = name

# verified overrides
for lab, nm in LABELS.items():
    labels[int(lab.split('_')[1])] = nm
for k, nm in S1.items():
    s1[int(k)] = nm
for k, nm in S2.items():
    s2[int(k)] = nm
# v2 version slots (used by enqueue: pStatic2 442 + tail)
for i in range(4):
    s2[442 + i] = f'gQueue2_VersionSlot{i}'

def emit(path):
    out = []
    out.append('// ModLoader_Defines.h — human names for all labels/statics')
    out.append('// Regenerated from VERIFIED audit (docs/LOADER_AUDIT_VERIFIED.md) — do not edit manually')
    out.append('// Include in your CSA via: IncludeStaticFile ModLoader_Defines.h  // or just use as reference')
    out.append('')
    out.append('#pragma once')
    out.append('')
    out.append('// ---------- Labels (Functions) ----------')
    for n in sorted(labels):
        out.append(f'#define {labels[n]}  Label_{n}  // call via Call @{labels[n]} or :{labels[n]}')
    out.append('')
    out.append('// ---------- Static1 (512) ----------')
    for n in range(512):
        out.append(f'#define {s1.get(n, f"gUnk1_{n}")}  Static1[{n}]  // StaticSet1/StaticGet1 {n}')
    out.append('')
    out.append('// ---------- Static2 (600) ----------')
    for n in range(600):
        out.append(f'#define {s2.get(n, f"gUnk2_{n}")}  Static2[{n}]  // StaticSet2/StaticGet2 {n}')
    path.write_bytes(('\r\n'.join(out)).encode('utf-8'))

if __name__ == '__main__':
    emit(HDR)
    print(f'{HDR}: {len(labels)} labels, Static1 512, Static2 600 (CRLF, clean)')
