"""Check every reference column of a mod folder's tables against vanilla + other packs + the mod.

refcheck.py <mod folder> [extra pack ...]
"""
import sys, os, re, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Faction_Dark_Elves', '_build_scripts'))
from twpack import Pack, DATA, SCHEMA, parse_db, table

mod = sys.argv[1]
extra = [Pack(p) for p in sys.argv[2:]]
db = Pack(DATA + r'\db.pack')
txt = open(SCHEMA, encoding='utf-8').read()


def fields(t, ver):
    m = re.search(r'^        "%s": \[\n(.*?)^        \],' % t, txt, re.S | re.M)
    for vm in re.finditer(r'version: (\d+),\s*fields: \[(.*?)\n                \],', m.group(1), re.S):
        if int(vm.group(1)) == ver:
            out = []
            for fm in re.finditer(r'\(\s*name: "(\w+)",(.*?)\n                    \)', vm.group(2), re.S):
                ref = re.search(r'is_reference: Some\(\(\s*"(\w+)",\s*"(\w+)",?\s*\)\)', fm.group(2))
                out.append((fm.group(1), ref.groups() if ref else None))
            return out


cache = {}


def values(t, col):
    key = (t, col)
    if key not in cache:
        vals = set()
        for p in [db] + extra:
            try:
                vals |= {r.get(col) for r in table(p, t)}
            except Exception:
                pass
        for f in glob.glob(os.path.join(mod, 'db', t, '*')):
            vals |= {r.get(col) for r in parse_db(t, open(f, 'rb').read())[1]}
        cache[key] = vals
    return cache[key]


bad = 0
for f in sorted(glob.glob(os.path.join(mod, 'db', '*', '*'))):
    t = f.split(os.sep)[-2]
    ver, rows = parse_db(t, open(f, 'rb').read())
    for col, ref in fields(t, ver) or []:
        if not ref:
            continue
        rt, rc = ref[0] + '_tables', ref[1]
        have = values(rt, rc)
        missing = sorted({r[col] for r in rows if r[col] not in ('', None) and r[col] not in have})
        if missing:
            bad += len(missing)
            print(f'{t}.{col} -> {rt}.{rc}: {len(missing)} missing, e.g. {missing[:5]}')
print('missing references:', bad)
