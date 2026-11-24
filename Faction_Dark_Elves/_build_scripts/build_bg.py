"""Build BlackGuard_MOD.pack (PFH5, type Mod) with two add-only junction tables."""
import struct, sys, time, uuid

out = sys.argv[1]
FRAG = 'BlackGuard_MOD'


def s8(s):
    b = s.encode('utf-8')
    return struct.pack('<H', len(b)) + b


def db_file(version, rows):
    g = str(uuid.uuid4())
    d = b'\xfd\xfe\xfc\xff' + struct.pack('<H', len(g)) + g.encode('utf-16-le')
    d += b'\xfc\xfd\xfe\xff' + struct.pack('<I', version)
    d += b'\x01' + struct.pack('<I', len(rows))
    for r in rows:
        d += r
    return d


files = {
    # attribute (StringU8), attribute_group (OptionalStringU8)
    f'db/unit_attributes_to_groups_junctions_tables/{FRAG}':
        db_file(2, [s8('contempt') + b'\x01' + s8('wh2_main_def_inf_black_guard_0')]),
    # ability, land_unit, culture (all StringU8)
    f'db/land_units_to_unit_abilites_junctions_tables/{FRAG}':
        db_file(1, [s8('wh2_dlc09_unit_passive_guardian') + s8('wh2_main_def_inf_black_guard_0') + s8('*')]),
}

# The game expects the pack index sorted by path, as RPFM writes it.
files = dict(sorted(files.items(), key=lambda kv: kv[0].lower()))

index = b''.join(struct.pack('<I', len(d)) + b'\x00' + n.replace('/', '\\').encode() + b'\x00'
                 for n, d in files.items())
header = b'PFH5' + struct.pack('<IIIIII', 3, 0, 0, len(files), len(index), int(time.time()))
with open(out, 'wb') as f:
    f.write(header + index + b''.join(files.values()))
print('wrote', out)
