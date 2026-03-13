#!/usr/bin/env python3
"""
Extreme-G (N64) String Dumper
Extracts and categorizes strings from the ROM binary.
"""

import sys
import os

ROM_FILE = "Extreme-G (U) [!].z64"

CATEGORIES = {
    "source_files": [".c", ".h", ".s", ".asm"],
    "game_assets": ["bike", "track", "level", "texture", "model", "mesh", "sprite", "pal", "chr"],
    "gameplay": ["weapon", "shield", "turbo", "nitro", "speed", "boost", "race", "lap", "finish", "player"],
    "ui_menu": ["menu", "select", "option", "press", "start", "continue", "score", "time", "name"],
    "audio": ["sound", "music", "sfx", "audio", "voice", "sample"],
    "debug": ["debug", "error", "assert", "warn", "fail", "test", "dump", "printf", "log"],
    "system": ["malloc", "free", "alloc", "stack", "heap", "dma", "cache", "thread"],
}


def extract_strings(data, min_length=6):
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


def categorize(s):
    sl = s.lower()
    for cat, keywords in CATEGORIES.items():
        if any(kw in sl for kw in keywords):
            return cat
    return "other"


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    if not os.path.exists(ROM_FILE):
        print(f"Error: ROM file '{ROM_FILE}' not found.")
        sys.exit(1)

    with open(ROM_FILE, "rb") as f:
        data = f.read()

    strings = extract_strings(data, min_length=6)
    print(f"Total strings found: {len(strings)}\n")

    if mode == "all":
        for offset, s in strings:
            cat = categorize(s)
            print(f"  0x{offset:06X} [{cat:12s}] {s}")
    elif mode in CATEGORIES:
        filtered = [(o, s) for o, s in strings if categorize(s) == mode]
        print(f"Category: {mode} ({len(filtered)} strings)\n")
        for offset, s in filtered:
            print(f"  0x{offset:06X}: {s}")
    elif mode == "summary":
        counts = {}
        for _, s in strings:
            cat = categorize(s)
            counts[cat] = counts.get(cat, 0) + 1
        for cat, count in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"  {cat:15s}: {count}")
    else:
        print(f"Usage: {sys.argv[0]} [all|summary|{' | '.join(CATEGORIES.keys())}]")


if __name__ == "__main__":
    main()
