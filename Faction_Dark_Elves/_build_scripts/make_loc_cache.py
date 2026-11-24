"""Write loc_en.pkl: every vanilla English loc entry (key -> text) from the game's local_en.pack.

build_cult.py (and the probe scripts) read it from beside themselves. It is ~36 MB of CA text, so
it is not committed; rebuild it after a game patch or on a new machine:

  python make_loc_cache.py [out.pkl]      (default: loc_en.pkl beside this script)
"""
import os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from twpack import Pack, DATA, parse_loc

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'loc_en.pkl')
pack = Pack(os.path.join(DATA, 'local_en.pack'))
loc = {}
for name in sorted(pack.files):
    if name.endswith('.loc'):
        loc.update(parse_loc(pack.read(name)))
pickle.dump(loc, open(out, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
print('wrote', out, len(loc), 'entries')
