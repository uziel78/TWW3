"""Build a PFH5 Mod-type pack from a folder: build_pack.py <src_folder> <out.pack>.

Files are stored uncompressed, and the index is sorted by path, as RPFM writes it.
"""
import os, struct, sys, time

src, out = sys.argv[1], sys.argv[2]
files = {}
for root, _, names in os.walk(src):
    for n in names:
        full = os.path.join(root, n)
        rel = os.path.relpath(full, src).replace(os.sep, '\\')
        files[rel] = open(full, 'rb').read()

files = dict(sorted(files.items(), key=lambda kv: kv[0].lower()))
index = b''.join(struct.pack('<I', len(d)) + b'\x00' + n.encode() + b'\x00' for n, d in files.items())
header = b'PFH5' + struct.pack('<IIIIII', 3, 0, 0, len(files), len(index), int(time.time()))
with open(out, 'wb') as f:
    f.write(header + index + b''.join(files.values()))
print('wrote', out, list(files))
