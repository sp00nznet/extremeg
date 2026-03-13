#!/usr/bin/env python3
"""
Extreme-G Recompilation Progress Tracker
Shows current status of function identification and recompilation.
"""

import os
import sys
import glob


def count_toml_functions(path):
    """Count functions defined in a TOML symbols file."""
    if not os.path.exists(path):
        return 0
    count = 0
    with open(path, "r") as f:
        for line in f:
            if line.strip().startswith("[[functions]]"):
                count += 1
    return count


def count_recompiled_functions(directory):
    """Count recompiled functions in generated C files."""
    if not os.path.isdir(directory):
        return 0
    count = 0
    for f in glob.glob(os.path.join(directory, "*.c")):
        with open(f, "r") as fh:
            for line in fh:
                if "RECOMP_FUNC" in line or "void " in line:
                    count += 1
    return count


def count_stubbed_functions(path):
    """Count stubbed functions in recomp.toml."""
    if not os.path.exists(path):
        return 0
    count = 0
    in_stubs = False
    with open(path, "r") as f:
        for line in f:
            if "stubbed_funcs" in line:
                in_stubs = True
            elif in_stubs:
                if line.strip().startswith('"'):
                    count += 1
                elif line.strip() == "]":
                    in_stubs = False
    return count


def main():
    sym_count = count_toml_functions("symbols.toml")
    recomp_count = count_recompiled_functions("RecompiledFuncs")
    stub_count = count_stubbed_functions("extremeg.recomp.toml")

    print("=" * 50)
    print("  Extreme-G Recompilation Progress")
    print("=" * 50)
    print(f"  Functions identified:   {sym_count}")
    print(f"  Functions recompiled:   {recomp_count}")
    print(f"  Functions stubbed:      {stub_count}")
    print(f"  Total handled:          {recomp_count + stub_count}")

    if sym_count > 0:
        pct = (recomp_count + stub_count) / sym_count * 100
        bar_len = 30
        filled = int(bar_len * pct / 100)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"\n  Progress: [{bar}] {pct:.1f}%")
    else:
        print("\n  Run rom_analyzer.py first to identify functions.")

    print("=" * 50)


if __name__ == "__main__":
    main()
