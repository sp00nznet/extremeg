#!/usr/bin/env python3
"""
Extreme-G (N64) ROM Analyzer
Extracts function boundaries, strings, and structural information from the ROM.
"""

import struct
import sys
import os
import gzip
from io import BytesIO

ROM_FILE = "Extreme-G (U) [!].z64"
ENTRY_POINT = 0x8004B400
ROM_CODE_START = 0x1000


def read_rom(path):
    with open(path, "rb") as f:
        return f.read()


def parse_header(data):
    """Parse the N64 ROM header."""
    header = {
        "pi_regs": struct.unpack(">I", data[0:4])[0],
        "clock_rate": struct.unpack(">I", data[4:8])[0],
        "entry_point": struct.unpack(">I", data[8:12])[0],
        "release": struct.unpack(">I", data[12:16])[0],
        "crc1": struct.unpack(">I", data[16:20])[0],
        "crc2": struct.unpack(">I", data[20:24])[0],
        "title": data[0x20:0x34].decode("ascii", errors="replace").strip(),
        "game_code": data[0x3B:0x3F].decode("ascii", errors="replace"),
        "rom_size": len(data),
    }
    return header


def find_gzip_sections(data):
    """Find all gzip-compressed sections in the ROM."""
    sections = []
    i = 0
    while i < len(data) - 2:
        if data[i] == 0x1F and data[i + 1] == 0x8B:
            sections.append(i)
        i += 1
    return sections


def try_decompress_gzip(data, offset, max_size=1024 * 1024):
    """Try to decompress a gzip section from the ROM."""
    end = min(offset + max_size, len(data))
    for size in range(100, end - offset, 1000):
        try:
            decompressed = gzip.decompress(data[offset : offset + size])
            return decompressed, size
        except Exception:
            continue
    return None, 0


def find_functions_in_code(code_data, base_addr):
    """Find function boundaries by looking for MIPS prologues/epilogues."""
    functions = []
    i = 0
    while i < len(code_data) - 4:
        word = struct.unpack(">I", code_data[i : i + 4])[0]
        # ADDIU SP, SP, -imm (function prologue)
        if (word & 0xFFFF0000) == 0x27BD0000:
            imm = word & 0xFFFF
            if imm >= 0x8000:  # Negative immediate = stack allocation
                addr = base_addr + i
                functions.append(addr)
        i += 4
    return functions


def extract_strings(data, min_length=6):
    """Extract ASCII strings from binary data."""
    strings = []
    current = b""
    start = 0
    for i, b in enumerate(data):
        if 32 <= b < 127:
            if not current:
                start = i
            current += bytes([b])
        else:
            if len(current) >= min_length:
                strings.append((start, current.decode("ascii")))
            current = b""
    return strings


def main():
    if not os.path.exists(ROM_FILE):
        print(f"Error: ROM file '{ROM_FILE}' not found.")
        print("Place your legally obtained ROM in the project root.")
        sys.exit(1)

    data = read_rom(ROM_FILE)
    header = parse_header(data)

    print("=" * 60)
    print("  Extreme-G (N64) ROM Analysis")
    print("=" * 60)
    print(f"  Title:       {header['title']}")
    print(f"  Game Code:   {header['game_code']}")
    print(f"  Entry Point: 0x{header['entry_point']:08X}")
    print(f"  CRC1:        0x{header['crc1']:08X}")
    print(f"  CRC2:        0x{header['crc2']:08X}")
    print(f"  ROM Size:    {header['rom_size']} bytes ({header['rom_size'] // 1024} KB)")
    print()

    # Find gzip sections
    gzip_offsets = find_gzip_sections(data)
    print(f"  GZIP sections found: {len(gzip_offsets)}")
    print()

    # Analyze boot code (pre-compression area)
    first_gzip = gzip_offsets[0] if gzip_offsets else len(data)
    boot_code = data[ROM_CODE_START:first_gzip]
    boot_funcs = find_functions_in_code(boot_code, 0x80000400)
    print(f"  Boot code region: 0x{ROM_CODE_START:06X} - 0x{first_gzip:06X}")
    print(f"  Boot code functions: {len(boot_funcs)}")
    print()

    # Try to decompress and analyze code sections
    total_decompressed = 0
    total_functions = len(boot_funcs)
    code_sections = 0

    print("  Analyzing compressed sections...")
    for idx, offset in enumerate(gzip_offsets[:30]):
        decompressed, comp_size = try_decompress_gzip(data, offset)
        if decompressed:
            funcs = find_functions_in_code(decompressed, 0x80000000)
            if len(funcs) > 5:
                code_sections += 1
                total_functions += len(funcs)
                print(
                    f"    Section {idx:3d} @ 0x{offset:06X}: "
                    f"{comp_size:6d} -> {len(decompressed):7d} bytes, "
                    f"{len(funcs)} functions"
                )
            total_decompressed += len(decompressed)

    print()
    print(f"  Total code sections: {code_sections}")
    print(f"  Total functions found: {total_functions}")
    print(f"  Total decompressed data: {total_decompressed} bytes")
    print()

    # Extract strings from boot area
    strings = extract_strings(data[0x80000:0x100000], min_length=8)
    interesting = [
        s
        for _, s in strings
        if any(
            x in s.lower()
            for x in [
                "bike",
                "track",
                "race",
                "weapon",
                "menu",
                "game",
                "player",
                "speed",
                "sound",
                "level",
                "cheat",
                "bonus",
                "extreme",
                "turbo",
                "shield",
                "nitro",
                ".c",
                ".h",
                "error",
                "debug",
            ]
        )
    ]

    if interesting:
        print("  Interesting strings found:")
        for s in interesting[:30]:
            print(f"    {s}")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
