#!/usr/bin/env python3
"""
Extreme-G (N64) LZSS Decompressor

Decompresses LZSS-compressed sections from the Extreme-G ROM.
The game uses custom LZSS compression for code and asset storage.

Header format:
  [header_size: u32]  (bytes before LZSS magic, from start of block)
  "LZSS" (4 bytes magic)
  [decompressed_size: u32]
  [compressed_size: u32]
  [compressed data...]

Based on the decompression routine found in the boot code at RAM 0x80000498+.
"""

import struct
import sys
import os


def find_lzss_blocks(data):
    """Find all LZSS block headers in the ROM."""
    blocks = []
    i = 0
    while i < len(data) - 12:
        if data[i:i+4] == b'LZSS':
            decomp_size = struct.unpack('>I', data[i+4:i+8])[0]
            comp_size = struct.unpack('>I', data[i+8:i+12])[0]
            # Sanity check sizes
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


def decompress_lzss(data, comp_size, decomp_size):
    """
    LZSS decompression matching the Extreme-G boot code algorithm.

    The algorithm:
    - Read a flag byte; each bit determines literal (1) or reference (0)
    - Literal: copy one byte from input to output
    - Reference: read 2 bytes for (offset, length) pair
      - offset: 12 bits (sliding window)
      - length: 4 bits + 2 (minimum match = 2)
    """
    output = bytearray()
    src = 0

    while src < comp_size and len(output) < decomp_size:
        # Read flag byte
        if src >= len(data):
            break
        flags = data[src]
        src += 1

        for bit in range(8):
            if src >= comp_size or len(output) >= decomp_size:
                break

            if flags & (1 << (7 - bit)):
                # Literal byte
                output.append(data[src])
                src += 1
            else:
                # Back reference
                if src + 1 >= len(data):
                    break
                b1 = data[src]
                b2 = data[src + 1]
                src += 2

                # High nibble of b2 + all of b1 = offset (12 bits)
                offset = ((b2 & 0xF0) << 4) | b1
                # Low nibble of b2 + 2 = length
                length = (b2 & 0x0F) + 2

                # Copy from sliding window
                for j in range(length):
                    if offset < len(output):
                        pos = len(output) - offset - 1
                        if pos >= 0:
                            output.append(output[pos])
                        else:
                            output.append(0)
                    else:
                        output.append(0)

    return bytes(output)


def decompress_lzss_v2(data, comp_size, decomp_size):
    """
    Alternative LZSS variant - LSB-first flags, different offset encoding.
    """
    output = bytearray()
    src = 0

    while src < comp_size and len(output) < decomp_size:
        if src >= len(data):
            break
        flags = data[src]
        src += 1

        for bit in range(8):
            if src >= comp_size or len(output) >= decomp_size:
                break

            if flags & (1 << bit):
                # Literal byte
                output.append(data[src])
                src += 1
            else:
                if src + 1 >= len(data):
                    break
                b1 = data[src]
                b2 = data[src + 1]
                src += 2

                offset = ((b2 & 0xF0) << 4) | b1
                length = (b2 & 0x0F) + 3

                for j in range(length):
                    pos = len(output) - offset
                    if 0 <= pos < len(output):
                        output.append(output[pos])
                    else:
                        output.append(0)

    return bytes(output)


def decompress_lzss_v3(data, comp_size, decomp_size):
    """
    Another LZSS variant - matching common N64 game patterns.
    Flag bits MSB first, offset = b1 | (b2 & 0xF0) << 4, length = (b2 & 0xF) + 3
    Copy from ring buffer position.
    """
    output = bytearray(decomp_size)
    ring = bytearray(4096)
    ring_pos = 4096 - 18  # Common starting position
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
                # Literal
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


def analyze_decompressed(data, label=""):
    """Check if decompressed data looks like MIPS code."""
    if len(data) < 16:
        return 0
    jr_ra = 0
    addiu_sp = 0
    jal = 0
    for i in range(0, len(data) - 4, 4):
        word = struct.unpack('>I', data[i:i+4])[0]
        if word == 0x03E00008:
            jr_ra += 1
        if (word & 0xFFFF0000) == 0x27BD0000 and (word & 0xFFFF) >= 0x8000:
            addiu_sp += 1
        if (word >> 26) == 0x03:
            jal += 1
    return addiu_sp


def main():
    rom_file = "Extreme-G (U) [!].z64"
    if not os.path.exists(rom_file):
        print(f"Error: ROM file '{rom_file}' not found.")
        sys.exit(1)

    with open(rom_file, "rb") as f:
        data = f.read()

    blocks = find_lzss_blocks(data)
    print(f"Found {len(blocks)} LZSS blocks")
    print()

    os.makedirs("extracted", exist_ok=True)

    for idx, block in enumerate(blocks):
        comp_data = data[block['data_offset']:block['data_offset'] + block['comp_size']]

        # Try all decompression variants
        best = None
        best_funcs = -1
        best_variant = ""

        for name, func in [("v1", decompress_lzss), ("v2", decompress_lzss_v2), ("v3", decompress_lzss_v3)]:
            try:
                result = func(comp_data, block['comp_size'], block['decomp_size'])
                funcs = analyze_decompressed(result)
                if funcs > best_funcs:
                    best = result
                    best_funcs = funcs
                    best_variant = name
            except Exception:
                pass

        if best:
            is_code = best_funcs > 5
            status = f"CODE ({best_funcs} funcs, {best_variant})" if is_code else f"data ({best_variant})"
            print(f"  Block {idx:3d} @ 0x{block['offset']:06X}: "
                  f"{block['comp_size']:7d} -> {block['decomp_size']:7d} "
                  f"(got {len(best):7d}) [{status}]")

            # Save code blocks
            if is_code:
                outpath = f"extracted/block_{idx:03d}_code.bin"
                with open(outpath, "wb") as f:
                    f.write(best)
                print(f"         -> Saved to {outpath}")
        else:
            print(f"  Block {idx:3d} @ 0x{block['offset']:06X}: FAILED to decompress")


if __name__ == "__main__":
    main()
