#!/usr/bin/env python3
"""Extract DTBO entries from a Xiaomi dtbo.img.

Usage:
  dtbo_tool.py dtbo.img OUTDIR

Each entry in the image is a flattened DTB with a 32-byte DTBO header
(magic 0x76, version, header_size, entries_off, dtb_size, etc.).
Layout (big-endian):
  0x00: magic (0x76)
  0x01: version
  0x04: header size
  0x08: entries offset
  0x14: dtb_size
Then per entry: name (null-terminated ASCII), then the actual DTB
(possibly compressed with LZ4).

Xiaomi dtbo images commonly use uncompressed DTBs with the "Android DTBO"
header layout: 48-byte header followed by entries. We parse generically.
"""
import struct, sys, os, zlib

DTBO_MAGIC = 0x76


def read_entries(path):
    data = open(path, 'rb').read()
    magic = data[0]
    version = data[1]
    hdr_size = struct.unpack('>I', data[4:8])[0]
    entries_off = struct.unpack('>I', data[8:12])[0]
    print(f'magic=0x{magic:02x} version={version} hdr_size={hdr_size} '
          f'entries_off=0x{entries_off:x} total={len(data)}')
    entries = []
    p = entries_off
    while p < len(data):
        name_end = data.find(b'\0', p)
        if name_end < 0:
            break
        name = data[p:name_end].decode('ascii', 'replace')
        p = name_end + 1
        p = (p + 3) & ~3  # align to 4
        # next 4 bytes = offset to dtb within entry block? Try common layout:
        # after name, 8 bytes = dtb_off, dtb_size
        if p + 8 <= len(data):
            dtb_off = struct.unpack('>I', data[p:p+4])[0]
            dtb_size = struct.unpack('>I', data[p+4:p+8])[0]
            entries.append((name, dtb_off, dtb_size))
            p += 8
            p = (p + 3) & ~3
        else:
            break
    return entries


def main():
    img = sys.argv[1]
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    entries = read_entries(img)
    data = open(img, 'rb').read()
    for name, off, size in entries:
        dtb = data[off:off + size]
        # Check for DTB magic (0xd00dfeed big-endian) or gzip
        if dtb[:4] == b'\xd0\x0d\xfe\xed':
            raw = dtb
        elif dtb[:2] == b'\x1f\x8b':
            raw = zlib.decompress(dtb, 31)
        else:
            # maybe lz4-framed
            import lz4.frame as lzf
            raw = lzf.decompress(dtb)
        safe = name.replace('/', '_')
        with open(os.path.join(out, safe + '.dtb'), 'wb') as f:
            f.write(raw)
        print(f'{name}: {len(raw)} bytes -> {safe}.dtb')


if __name__ == '__main__':
    main()
