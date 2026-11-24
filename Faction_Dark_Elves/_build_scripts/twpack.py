"""Minimal read-only reader for TW:WH3 PFH5 packs, DB tables and loc files.

Dependencies (pylib/ with zstandard, schemas/schema_wh3.ron from RPFM's rpfm-schemas) are looked
up beside this file first, then in the TWW3 repo's shared tools/ folder (../../tools, filled by
tools/setup.sh). Environment overrides: TWW3_DATA (game data folder), TWPACK_SCHEMA (schema file).
"""
import re, struct, sys, os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _find(rel):
    for base in (_HERE, os.path.join(_HERE, '..', '..', 'tools')):
        path = os.path.normpath(os.path.join(base, rel))
        if os.path.exists(path):
            return path
    return os.path.join(_HERE, rel)


sys.path.insert(0, _find('pylib'))
import zstandard, lzma

DATA = os.environ.get('TWW3_DATA', r"D:\SteamLibrary\steamapps\common\Total War WARHAMMER III\data")
SCHEMA = os.environ.get('TWPACK_SCHEMA') or _find(os.path.join('schemas', 'schema_wh3.ron'))


class Pack:
    def __init__(self, path):
        self.f = open(path, 'rb')
        h = self.f.read(0x1c)
        n, isz = struct.unpack('<II', h[0x10:0x18])
        idx = self.f.read(isz)
        p, off, self.files = 0, 0x1c + isz, {}
        while p < len(idx):
            sz = struct.unpack('<I', idx[p:p + 4])[0]
            c = idx[p + 4]
            e = idx.index(b'\0', p + 5)
            self.files[idx[p + 5:e].decode().replace('\\', '/')] = (off, sz, c)
            off += sz
            p = e + 1

    def read(self, name):
        off, sz, c = self.files[name]
        self.f.seek(off)
        d = self.f.read(sz)
        if not c:
            return d
        usz = struct.unpack('<I', d[:4])[0]
        body = d[4:]
        if body[:4] == b'\x28\xb5\x2f\xfd':
            return zstandard.ZstdDecompressor().decompress(body, max_output_size=usz)
        # legacy LZMA alone: 5 byte props, no size
        props = body[:5]
        filt = lzma._decode_filter_properties(lzma.FILTER_LZMA1, props)
        return lzma.LZMADecompressor(lzma.FORMAT_RAW, filters=[filt]).decompress(body[5:])


_schema = None
def schema():
    global _schema
    if _schema is None:
        txt = open(SCHEMA, encoding='utf-8').read()
        _schema = {}
        for m in re.finditer(r'^        "(\w+)": \[\n(.*?)^        \],', txt, re.S | re.M):
            vers = {}
            for vm in re.finditer(r'version: (\d+),\s*fields: \[(.*?)\n                \],', m.group(2), re.S):
                fields = re.findall(r'name: "(\w+)",\s*field_type: (\w+)', vm.group(2))
                vers[int(vm.group(1))] = fields
            _schema[m.group(1)] = vers
    return _schema


def parse_db(table, data):
    p = 0
    if data[:4] == b'\xfd\xfe\xfc\xff':
        ln = struct.unpack('<H', data[4:6])[0]
        p = 6 + ln * 2
    ver = 0
    if data[p:p + 4] == b'\xfc\xfd\xfe\xff':
        ver = struct.unpack('<I', data[p + 4:p + 8])[0]
        p += 8
    p += 1
    rows = struct.unpack('<I', data[p:p + 4])[0]
    p += 4
    fields = schema()[table][ver]

    def s8():
        nonlocal p
        ln = struct.unpack('<H', data[p:p + 2])[0]
        v = data[p + 2:p + 2 + ln].decode('utf-8', 'replace'); p += 2 + ln; return v

    def s16():
        nonlocal p
        ln = struct.unpack('<H', data[p:p + 2])[0]
        v = data[p + 2:p + 2 + ln * 2].decode('utf-16-le', 'replace'); p += 2 + ln * 2; return v

    out = []
    for _ in range(rows):
        r = {}
        for name, t in fields:
            if t == 'Boolean': r[name] = data[p] != 0; p += 1
            elif t == 'I16': r[name] = struct.unpack('<h', data[p:p + 2])[0]; p += 2
            elif t == 'I32': r[name] = struct.unpack('<i', data[p:p + 4])[0]; p += 4
            elif t == 'I64': r[name] = struct.unpack('<q', data[p:p + 8])[0]; p += 8
            elif t == 'F32': r[name] = round(struct.unpack('<f', data[p:p + 4])[0], 4); p += 4
            elif t == 'F64': r[name] = struct.unpack('<d', data[p:p + 8])[0]; p += 8
            elif t == 'ColourRGB': r[name] = data[p:p + 4].hex(); p += 4
            elif t == 'StringU8': r[name] = s8()
            elif t == 'StringU16': r[name] = s16()
            elif t == 'OptionalStringU8':
                b = data[p]; p += 1; r[name] = s8() if b else ''
            elif t == 'OptionalStringU16':
                b = data[p]; p += 1; r[name] = s16() if b else ''
            else:
                raise ValueError(f'{table}: unsupported type {t}')
        out.append(r)
    return ver, out


def encode_db(table_name, version, rows):
    """Encode rows (dicts keyed by column name) using the schema's column order and types."""
    import uuid as _uuid
    fields = schema()[table_name][version]

    def s8(v):
        b_ = str(v).encode('utf-8')
        return struct.pack('<H', len(b_)) + b_

    def s16(v):
        return struct.pack('<H', len(str(v))) + str(v).encode('utf-16-le')

    g = str(_uuid.uuid4())
    out = b'\xfd\xfe\xfc\xff' + struct.pack('<H', len(g)) + g.encode('utf-16-le')
    if version:
        out += b'\xfc\xfd\xfe\xff' + struct.pack('<I', version)
    out += b'\x01' + struct.pack('<I', len(rows))
    for r in rows:
        missing = [n for n, _ in fields if n not in r]
        if missing:
            raise ValueError(f'{table_name}: row missing columns {missing}')
        for name, t in fields:
            v = r[name]
            if t == 'Boolean': out += b'\x01' if v else b'\x00'
            elif t == 'I16': out += struct.pack('<h', int(v))
            elif t == 'I32': out += struct.pack('<i', int(v))
            elif t == 'I64': out += struct.pack('<q', int(v))
            elif t == 'F32': out += struct.pack('<f', float(v))
            elif t == 'F64': out += struct.pack('<d', float(v))
            elif t == 'StringU8': out += s8(v)
            elif t == 'StringU16': out += s16(v)
            elif t == 'OptionalStringU8': out += (b'\x01' + s8(v)) if v else b'\x00'
            elif t == 'OptionalStringU16': out += (b'\x01' + s16(v)) if v else b'\x00'
            elif t == 'ColourRGB': out += bytes.fromhex(v)
            else: raise ValueError(f'{table_name}: unsupported type {t}')
    return out


def table_version(pack, name):
    """Version of the vanilla table, so mod fragments are written in the same format."""
    fn = next(f for f in pack.files if f.startswith(f'db/{name}/'))
    return parse_db(name, pack.read(fn))[0]


def parse_loc(data):
    p = 2 + 4 + 4  # BOM, 'LOC\0', version
    n = struct.unpack('<I', data[p:p + 4])[0]; p += 4
    out = {}
    for _ in range(n):
        vals = []
        for _ in range(2):
            ln = struct.unpack('<H', data[p:p + 2])[0]
            vals.append(data[p + 2:p + 2 + ln * 2].decode('utf-16-le', 'replace')); p += 2 + ln * 2
        p += 1
        out[vals[0]] = vals[1]
    return out


def table(pack, name):
    rows = []
    for fn in pack.files:
        if fn.startswith(f'db/{name}/'):
            rows += parse_db(name, pack.read(fn))[1]
    return rows
