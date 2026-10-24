#!/usr/bin/env python3
"""Extract DTBs from a Xiaomi dtbo.img by scanning for DTB magic."""
import struct, sys, os

def scan(path, outdir):
    data = open(path, 'rb').read()
    os.makedirs(outdir, exist_ok=True)
    magic = b'\xd0\x0d\xfe\xed'
    pos = 0
    idx = 0
    while True:
        off = data.find(magic, pos)
        if off < 0:
            break
        total = struct.unpack('>I', data[off + 4:off + 8])[0]
        if total < 40 or off + total > len(data):
            pos = off + 4
            continue
        dtb = data[off:off + total]
        str_off = struct.unpack('>I', dtb[32:36])[0]
        struct_off = struct.unpack('>I', dtb[36:40])[0]
        if str_off >= total or struct_off >= total:
            pos = off + 4
            continue
        # walk the first few struct tokens to find root node name
        name = f'entry{idx}'
        p = struct_off
        tokens = []
        for _ in range(8):
            if p + 4 > total:
                break
            t = struct.unpack('>I', dtb[p:p + 4])[0]
            tokens.append(t)
            p += 4
        # tokens: 1=BEGIN_NODE, 2=END_NODE, 3=PROP, 4=NOP, 9=END
        if len(tokens) >= 2 and tokens[0] == 1:
            # the string after the token IS the node name
            e = dtb.find(b'\0', p)
            if 0 < p < total:
                name = dtb[p:e].decode('utf-8', 'replace')
        safe = name.replace('/', '_')
        outfile = os.path.join(outdir, f'{idx:03d}_{safe}.dtb')
        with open(outfile, 'wb') as f:
            f.write(dtb)
        print(f'[{idx}] at 0x{off:08x} total={total} root={name!r}')
        idx += 1
        pos = off + max(total, 8)
    print(f'total: {idx} DTBs')

if __name__ == '__main__':
    scan(sys.argv[1], sys.argv[2])
