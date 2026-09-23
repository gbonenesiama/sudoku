#!/usr/bin/env python3
"""Build puzzles.js from a clone of https://github.com/iturki/nyt-sudoku-archive.

Usage: git clone --depth 1 https://github.com/iturki/nyt-sudoku-archive /tmp/nyt
       python3 scripts/build-puzzles.py /tmp/nyt

Every puzzle is checked for a unique solution before it is included.
"""
import os, re, json, glob
import sys
root=sys.argv[1] if len(sys.argv)>1 else 'nyt-sudoku-archive'
def solve_count(g, limit=2):
    g=list(g); cnt=[0]
    rows=[set() for _ in range(9)]; cols=[set() for _ in range(9)]; boxes=[set() for _ in range(9)]
    for i,v in enumerate(g):
        if v:
            r,c=divmod(i,9); b=r//3*3+c//3
            if v in rows[r] or v in cols[c] or v in boxes[b]: return 0
            rows[r].add(v); cols[c].add(v); boxes[b].add(v)
    def rec():
        best=None;bc=None
        for i in range(81):
            if not g[i]:
                r,c=divmod(i,9); b=r//3*3+c//3
                cand=[n for n in range(1,10) if n not in rows[r] and n not in cols[c] and n not in boxes[b]]
                if best is None or len(cand)<len(bc):
                    best,bc=i,cand
                    if len(cand)<=1: break
        if best is None: cnt[0]+=1; return
        r,c=divmod(best,9); b=r//3*3+c//3
        for n in bc:
            g[best]=n; rows[r].add(n); cols[c].add(n); boxes[b].add(n)
            rec()
            g[best]=0; rows[r].discard(n); cols[c].discard(n); boxes[b].discard(n)
            if cnt[0]>=limit: return
    rec(); return cnt[0]
out={}
for lvl in ['easy','medium','hard']:
    items=[]
    for f in sorted(glob.glob(f'{root}/nyt-sudoku-{lvl}/*.sdk')):
        date=re.search(r'(\d{4}-\d{2}-\d{2})',f).group(1)
        lines=[l.strip() for l in open(f) if l.strip() and not l.startswith('#')]
        s=''.join(lines).replace('.','0')
        assert len(s)==81 and s.isdigit(), (f,s)
        n=solve_count([int(ch) for ch in s])
        if n!=1: print('skip',f,n); continue
        items.append([date,s])
    out[lvl]=items
    print(lvl,len(items),'givens avg',sum(81-s.count('0') for _,s in items)/len(items))
js='/* NYT Sudoku archive (puzzle grids only). Source: github.com/iturki/nyt-sudoku-archive\n   Format: [date, 81-char grid with 0 for blanks]. Regenerate with scripts/build-puzzles.py */\n'
js+='window.PUZZLES = {\n'+',\n'.join(f'  {k}: [\n'+',\n'.join(f'    ["{d}","{s}"]' for d,s in v)+'\n  ]' for k,v in out.items())+'\n};\n'
open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','puzzles.js'),'w').write(js)
