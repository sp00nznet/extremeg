#!/usr/bin/env python3
"""
Extreme-G — Build Recomp-Ready ROM

Creates a modified ROM image where the LZSS-compressed game code has been
decompressed and placed at the correct offset for N64Recomp to process.

N64Recomp reads code from the ROM using the standard N64 mapping:
  rom_offset = vram_address - 0x80000400 + 0x1000

Since the original ROM has compressed code at these offsets, we need to
create a patched version with decompressed code in the right place.
"""

import struct
import sys
import os
import gzip

ROM_FILE = "Extreme-G (U) [!].z64"
OUTPUT_FILE = "extremeg_recomp.z64"

# Code mapping
# librecomp's init() loads ROM[0x1000..] to RDRAM[entrypoint & 0x7FFFFFF]
# Since entrypoint = RAM_BASE, the ROM offset for VRAM X is:
#   rom_offset = X - RAM_BASE + 0x1000
RAM_BASE = 0x8004B8A0
VRAM_TO_ROM = lambda vram: vram - RAM_BASE + 0x1000


def find_lzss_blocks(data):
    blocks = []
    i = 0
    while i < len(data) - 12:
        if data[i:i+4] == b'LZSS':
            decomp_size = struct.unpack('>I', data[i+4:i+8])[0]
            comp_size = struct.unpack('>I', data[i+8:i+12])[0]
            if 0 < decomp_size < 0x800000 and 0 < comp_size < 0x800000 and comp_size <= decomp_size:
                blocks.append({
                    'offset': i,
                    'data_offset': i + 12,
                    'decomp_size': decomp_size,
                    'comp_size': comp_size,
                })
            i += 12
        else:
            i += 1
    return blocks


def decompress_lzss_v3(data, comp_size, decomp_size):
    output = bytearray(decomp_size)
    ring = bytearray(4096)
    ring_pos = 4096 - 18
    dst = 0
    src = 0

    while src < comp_size and dst < decomp_size:
        if src >= len(data):
            break
        flags = data[src]
        src += 1

        for bit in range(8):
            if src >= comp_size or dst >= decomp_size:
                break

            if flags & (1 << bit):
                c = data[src]
                src += 1
                output[dst] = c
                ring[ring_pos] = c
                ring_pos = (ring_pos + 1) & 0xFFF
                dst += 1
            else:
                if src + 1 >= len(data):
                    break
                b1 = data[src]
                b2 = data[src + 1]
                src += 2

                offset = b1 | ((b2 & 0xF0) << 4)
                length = (b2 & 0x0F) + 3

                for j in range(length):
                    if dst >= decomp_size:
                        break
                    c = ring[(offset + j) & 0xFFF]
                    output[dst] = c
                    ring[ring_pos] = c
                    ring_pos = (ring_pos + 1) & 0xFFF
                    dst += 1

    return bytes(output[:dst])


def main():
    if not os.path.exists(ROM_FILE):
        print(f"Error: '{ROM_FILE}' not found.")
        sys.exit(1)

    with open(ROM_FILE, "rb") as f:
        rom = bytearray(f.read())

    print(f"Original ROM: {len(rom)} bytes")

    # Find and decompress the first LZSS block (main code)
    blocks = find_lzss_blocks(rom)
    if not blocks:
        print("Error: No LZSS blocks found!")
        sys.exit(1)

    block = blocks[0]
    print(f"Code block at ROM 0x{block['offset']:06X}")
    print(f"  Compressed:   {block['comp_size']} bytes")
    print(f"  Decompressed: {block['decomp_size']} bytes")

    comp_data = rom[block['data_offset']:block['data_offset'] + block['comp_size']]
    code = decompress_lzss_v3(comp_data, block['comp_size'], block['decomp_size'])
    print(f"  Actually got: {len(code)} bytes")

    # Calculate where to place the decompressed code
    rom_offset = VRAM_TO_ROM(RAM_BASE)
    rom_end = rom_offset + len(code)
    print(f"\nPlacing code at ROM offset 0x{rom_offset:06X} - 0x{rom_end:06X}")
    print(f"  (VRAM 0x{RAM_BASE:08X} - 0x{RAM_BASE + len(code):08X})")

    # Create output ROM — copy original and overlay decompressed code
    output = bytearray(rom)

    # Ensure ROM is large enough
    if rom_end > len(output):
        output.extend(b'\x00' * (rom_end - len(output)))

    # Write decompressed code at the correct offset
    output[rom_offset:rom_offset + len(code)] = code

    # Update ROM header entry point to match our RAM base
    struct.pack_into('>I', output, 8, RAM_BASE)

    # Recalculate CRC (simplified — N64Recomp may not check CRC)
    # For now, leave CRC as-is

    with open(OUTPUT_FILE, "wb") as f:
        f.write(output)

    print(f"\nWrote {len(output)} bytes to {OUTPUT_FILE}")
    print("Ready for N64Recomp!")

    # Verify by checking for MIPS code at the expected offset
    jr_ra = 0
    for i in range(rom_offset, rom_end - 4, 4):
        word = struct.unpack('>I', output[i:i+4])[0]
        if word == 0x03E00008:
            jr_ra += 1
    print(f"Verification: {jr_ra} JR RA instructions found in placed code")


if __name__ == "__main__":
    main()
