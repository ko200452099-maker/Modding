#!/usr/bin/env python3
"""
deep_audit.py — structural analyzer for ModLoader.csa (PRISTINE numbered input).

Builds:
  * function table  : label -> {line, params, locals, calls, natives, strings,
                                statics_read, statics_write, frames, jumps}
  * callers map     : label -> [calling function labels]
  * static table    : id -> read/write sites with surrounding context
  * loader closure  : BFS from given roots over Call edges (+ their jump labels)

Usage:
  python3 tools/deep_audit.py /tmp/ModLoader_pristine.csa \
      --roots Label_0,Label_3,Label_5,Label_1835 --out /tmp/audit
Outputs: /tmp/audit/functions.json, statics.json, closure.json, closure.txt
"""
import re, sys, json, argparse, pathlib
from collections import defaultdict, deque

RE_LABEL   = re.compile(r'^:(\w+)\s*$')
RE_FUNC    = re.compile(r'^Function\s+(\d+)\s+(\d+)\s+(\d+)')
RE_RETURN  = re.compile(r'^Return\b')
RE_CALL    = re.compile(r'^Call\s+@(\w+)')
RE_NATIVE  = re.compile(r'^CallNative\s+"([^"]+)"\s+(\d+)\s+(\d+)')
RE_JUMP    = re.compile(r'^(Jump\w*)\s+@(\w+)')
RE_SWITCH  = re.compile(r'^Switch\s+(.*)$')
RE_SWCASE  = re.compile(r'(\S+?)=@(\w+)')
RE_STATIC  = re.compile(r'^(p?Static(?:Get|Set|PtrGet|PtrSet)?[12])\s+(\d+)(?:\s+(\d+))?')
RE_STRING  = re.compile(r'^PushString(?:Long)?\s+"(.*)"')
RE_GETHASH = re.compile(r'^GetHash\s+"(.*)"')

def parse(path):
    raw = pathlib.Path(path).read_bytes().decode('utf-8', 'replace')
    lines = [l.rstrip('\r').rstrip() for l in raw.replace('\r\n', '\n').split('\n')]
    funcs, order = {}, []
    cur = None            # current function label
    cur_jumps = {}        # jump-target label -> owning function
    statics = defaultdict(lambda: {'read': [], 'write': [], 'ptr': []})
    strings_by_fn = defaultdict(list)

    for i, line in enumerate(lines, 1):
        s = line.strip()
        if not s or s.startswith(';') or s.startswith('//'):
            continue
        m = RE_LABEL.match(s)
        if m:
            lab = m.group(1)
            nxt = lines[i].strip() if i < len(lines) else ''
            fm = RE_FUNC.match(nxt)
            if fm:                      # function definition
                cur = lab
                funcs[lab] = {
                    'line': i, 'params': int(fm.group(1)),
                    'locals': int(fm.group(2)), 'calls': [], 'natives': [],
                    'strings': [], 'statics_r': [], 'statics_w': [],
                    'jumps': [], 'returns': 0, 'switches': [],
                }
                order.append(lab)
            else:                       # internal jump target
                if cur:
                    cur_jumps[lab] = cur
                    funcs[cur]['jumps'].append({'label': lab, 'line': i})
            continue
        if cur is None:
            continue
        f = funcs[cur]
        if RE_RETURN.match(s):
            f['returns'] += 1
            continue
        m = RE_CALL.match(s)
        if m:
            f['calls'].append({'to': m.group(1), 'line': i}); continue
        m = RE_NATIVE.match(s)
        if m:
            f['natives'].append({'name': m.group(1), 'line': i}); continue
        m = RE_JUMP.match(s)
        if m:
            f.setdefault('jump_refs', []).append({'op': m.group(1), 'to': m.group(2), 'line': i}); continue
        m = RE_SWITCH.match(s)
        if m:
            f['switches'] += [{'case': c, 'to': t, 'line': i} for c, t in RE_SWCASE.findall(m.group(1))]
            continue
        m = RE_STATIC.match(s)
        if m:
            op, sid = m.group(1), int(m.group(2))
            bank = '1' if op.endswith('1') else '2'
            kind = 'ptr' if op.startswith('p') else ('write' if 'Set' in op else 'read')
            entry = {'fn': cur, 'line': i, 'op': op,
                     'ctx': ' | '.join(x.strip() for x in lines[max(0,i-3):i+2] if x.strip())}
            statics[f'{bank}:{sid}'][kind].append(entry)
            tgt = f['statics_w'] if kind == 'write' else f['statics_r']
            tgt.append({'bank': bank, 'id': sid, 'op': op, 'line': i})
            continue
        m = RE_STRING.match(s)
        if m:
            f['strings'].append({'str': m.group(1), 'line': i}); continue
        m = RE_GETHASH.match(s)
        if m:
            f['strings'].append({'hash': m.group(1), 'line': i}); continue
    return funcs, order, cur_jumps, statics, lines

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--roots', default='Label_0,Label_3,Label_5,Label_1835')
    ap.add_argument('--out', default='/tmp/audit')
    a = ap.parse_args()

    funcs, order, jump_owner, statics, lines = parse(a.src)
    callers = defaultdict(list)
    for lab, f in funcs.items():
        for c in f['calls']:
            callers[c['to']].append({'fn': lab, 'line': c['line']})
        for sw in f['switches']:
            callers[sw['to']].append({'fn': lab, 'line': sw['line'], 'via': 'switch'})

    roots = [r.strip() for r in a.roots.split(',')]
    seen, q = set(roots), deque(roots)
    while q:
        lab = q.popleft()
        f = funcs.get(lab)
        if not f:
            continue
        for edge in f['calls'] + f['switches']:
            t = edge['to']
            if t not in seen and t in funcs:
                seen.add(t); q.append(t)
    # internal jump labels owned by closure functions
    closure_jumps = {j: o for j, o in jump_owner.items() if o in seen}

    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out/'functions.json').write_text(json.dumps(funcs, indent=1))
    (out/'jump_owner.json').write_text(json.dumps(jump_owner, indent=1))
    (out/'callers.json').write_text(json.dumps(callers, indent=1))
    (out/'statics.json').write_text(json.dumps(statics, indent=1))
    (out/'closure.json').write_text(json.dumps(
        {'functions': sorted(seen), 'jump_labels': closure_jumps}, indent=1))

    with open(out/'closure.txt', 'w') as fh:
        fh.write(f"LOADER CLOSURE: {len(seen)} functions, {len(closure_jumps)} jump labels\n")
        fh.write(f"roots: {roots}\n\n")
        for lab in sorted(seen, key=lambda l: funcs[l]['line']):
            f = funcs[lab]
            fh.write(f"== {lab} (line {f['line']}, Function {f['params']} {f['locals']} 0, callers: {len(callers.get(lab, []))})\n")
            if f['natives']:
                fh.write(f"   natives: {', '.join(n['name'] for n in f['natives'])}\n")
            if f['strings']:
                ss = [x.get('str', '#'+x.get('hash','')) for x in f['strings']]
                fh.write(f"   strings: {ss[:8]}\n")
            if f['statics_r'] or f['statics_w']:
                r = sorted({f"S{x['bank']}[{x['id']}]" for x in f['statics_r']})
                w = sorted({f"S{x['bank']}[{x['id']}]" for x in f['statics_w']})
                fh.write(f"   S-read: {r}\n   S-write: {w}\n")
            if f['calls']:
                fh.write(f"   calls: {sorted({c['to'] for c in f['calls']})}\n")
    print(f"functions: {len(funcs)}  statics: {len(statics)}  closure: {len(seen)} fns / {len(closure_jumps)} jumps")
    print(f"written to {out}")

if __name__ == '__main__':
    main()
