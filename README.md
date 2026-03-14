# Extreme-G Recompiled

> **"Welcome to the future of racing. Again."**

A **static recompilation** of [Extreme-G](https://en.wikipedia.org/wiki/Extreme-G) (Nintendo 64, 1998) — the brutally fast, weapon-packed futuristic bike racer by Probe Entertainment — rebuilt to run **natively on modern PCs** without emulation.

No interpreter. No JIT. No mercy. Just raw, recompiled MIPS-to-x86-64 at 500mph.

---

## What Is This?

Remember screaming down neon-lit anti-gravity tracks at speeds that made your CRT blur? Dodging plasma bolts while your N64 controller's analog stick fought for its life? **That's Extreme-G** — and we're bringing it back from 1998, one MIPS instruction at a time.

This project uses [N64Recomp](https://github.com/N64Recomp/N64Recomp) to statically recompile the original N64 binary into native C code, which then compiles into a Windows executable. The result runs directly on your CPU — no emulation layer, no accuracy tradeoffs, just **native speed** with the door wide open for HD rendering, widescreen, and modern input.

### Why Static Recompilation?

```
  Traditional Emulation:
  ┌─────────────┐     ┌──────────────┐     ┌─────────┐
  │  N64 ROM    │ --> │  Interpreter  │ --> │  Screen  │
  │  (MIPS)     │     │  (per-instr)  │     │  Output  │
  └─────────────┘     └──────────────┘     └─────────┘
                         ^ slow, but compatible

  Static Recompilation:
  ┌─────────────┐     ┌──────────────┐     ┌──────────┐     ┌─────────┐
  │  N64 ROM    │ --> │  N64Recomp   │ --> │  Native  │ --> │  Screen  │
  │  (MIPS)     │     │  (offline)   │     │  C code  │     │  Output  │
  └─────────────┘     └──────────────┘     └──────────┘     └─────────┘
                                              ^ FAST, native, moddable
```

Every MIPS instruction becomes equivalent C at **build time**. Your CPU runs the game natively. This is how [Zelda64Recomp](https://github.com/Zelda64Recomp/Zelda64Recomp) brought Majora's Mask to PC — and now we're doing it for the fastest racer the N64 ever saw.

---

## The Game

**Extreme-G** (1998, Probe Entertainment / Acclaim) is a futuristic combat racing game for the Nintendo 64. You pilot sleek cyberbikes through twisting, looping tracks at insane speeds while blasting opponents with an arsenal of weapons.

**What made it legendary:**
- **Pure speed** — one of the fastest games on N64, with a sensation of velocity that still holds up
- **Weapons everywhere** — homing missiles, mines, plasma cannons, rear-fire rockets
- **Iconic soundtrack** — pounding techno/drum & bass that defined late-90s gaming
- **Track design** — loops, corkscrews, tunnels, and stomach-dropping vertical drops
- **4-player split-screen** — friendships tested, controllers thrown
- **Sonic boom** — break the sound barrier and the audio literally cuts out. *Chef's kiss.*

---

## ROM Info

| Field | Value |
|-------|-------|
| **Title** | `extremeg` |
| **Game Code** | `NEGE` |
| **Region** | USA (NTSC) |
| **Entry Point** | `0x8004B8A0` |
| **CRC1** | `0xFDA245D2` |
| **CRC2** | `0xA74A3D47` |
| **ROM Size** | 8 MB (8,388,608 bytes) |
| **Compression** | 51 LZSS blocks (custom, not gzip) |
| **Code Size** | 320 KB decompressed (184 KB compressed) |
| **Functions** | 726 recompiled (93 libultra identified) |
| **Code Range** | `0x8004B8A0` - `0x8009B898` |
| **Developer** | Probe Entertainment |
| **Publisher** | Acclaim Entertainment |
| **Release** | 1998 |
| **Build Path** | `d:\screen` (found in binary) |
| **Dev Names** | Justin, Darren, Fergus |

---

## Status

| Milestone | Status |
|-----------|--------|
| ROM Analysis | **COMPLETE** |
| LZSS Decompression (51 blocks) | **COMPLETE** |
| Boot Code Analysis | **COMPLETE** |
| Function Discovery (726 functions) | **COMPLETE** |
| Symbol File Generation | **COMPLETE** |
| RAM Base Identification (`0x8004B8A0`) | **COMPLETE** |
| N64Recomp Config | **COMPLETE** |
| N64Recomp Integration (726 recompiled functions) | **COMPLETE** |
| Build System (CMake) | **COMPLETE** |
| N64ModernRuntime Integration | **COMPLETE** |
| RT64 Renderer Integration | **COMPLETE** |
| SDL2 Window + Input | **COMPLETE** |
| libultra Identification (93 functions) | **COMPLETE** |
| ROM Mapping Fix (VRAM-to-ROM) | **COMPLETE** |
| BSS Clearing (3 regions) | **COMPLETE** |
| Custom Entrypoint Patch | **COMPLETE** |
| OS Stubs (33 internal functions) | **COMPLETE** |
| Game Boot (heap, threads, VI) | **WORKING** |
| Audio Driver Init | **CRASHING** |
| Audio Reimplementation | IN PROGRESS |
| RSP Microcode Handling | TODO |
| Playable Build | **THE DREAM** |

**Current Phase: Audio Driver Debugging**

**The game boots.** SDL window opens, RT64 initializes (tested on RTX 5070), ROM validates, heap allocator works correctly, game threads are created, and VI events fire. The game gets all the way into its main initialization before crashing in the audio driver.

**What's working:**
- Full static recompilation: 726 functions recompiled from MIPS to native C
- 93 libultra functions identified and properly named (osCreateThread, osCreateMesgQueue, osSendMesg, osViSwapBuffer, osSpTaskLoad, osAiSetNextBuffer, etc.)
- ROM mapping corrected: decompressed code placed at ROM offset 0x1000, loaded to RDRAM at the correct VRAM address
- Custom entrypoint clears 3 BSS regions and calls game init (bypassing COP0 hardware setup)
- 33 internal OS function stubs for helpers ultramodern doesn't reimplement
- SDL2 audio backend with 48kHz output
- Keyboard input mapped to N64 controller

**Current crash:** Access violation in `func_800888D0` during audio driver initialization. The call chain is `func_8004DE78` (game logic thread) -> `func_80053978` -> `func_80058890` -> `func_80082420` -> `func_800888D0`. The audio driver code in the 0x80082000-0x80089000 range needs further reverse engineering.

**Key technical details:**
- The ROM uses custom **LZSS compression** (51 blocks total — 1 code, 50 asset)
- Main code: 184 KB compressed -> 320 KB decompressed, mapped to `0x8004B8A0` - `0x8009B898`
- ROM mapping: `VRAM_TO_ROM = vram - 0x8004B8A0 + 0x1000`
- Boot code at `0x80000400` decompresses LZSS, clears BSS, jumps to `0x8004DC8C`

---

## Getting Started

### Prerequisites

- Python 3.x (for analysis tools)
- [N64Recomp](https://github.com/N64Recomp/N64Recomp) (for recompilation)
- Visual Studio 2022 with C++ workload
- CMake 3.20+
- Your own **legally obtained** ROM: `Extreme-G (U) [!].z64`

### Quick Start

```bash
# Clone the repo
git clone https://github.com/sp00nznet/extremeg.git
cd extremeg

# Place your ROM in the project root
cp /path/to/your/rom.z64 "Extreme-G (U) [!].z64"

# Run ROM analysis
py tools/rom_analyzer.py

# Dump strings from the ROM
py tools/string_dumper.py summary

# Check recomp progress
py tools/progress.py
```

### Building

```bash
# 1. Place your ROM in the project root
cp /path/to/your/rom.z64 "Extreme-G (U) [!].z64"

# 2. Build the patched recomp ROM (decompresses LZSS, fixes mapping)
py tools/build_recomp_rom.py

# 3. Run N64Recomp to generate native C from MIPS
N64Recomp.exe extremeg.recomp.toml

# 4. Re-apply the custom entrypoint patch in RecompiledFuncs/funcs_0.c
#    (replaces the generated recomp_entrypoint with BSS-clearing version)

# 5. Build the native executable
cmake -B build -G "Visual Studio 17 2022"
cmake --build build --config Release

# 6. Run (place extremeg_recomp.z64 in the build/Release directory)
build/Release/ExtremeGRecompiled.exe
```

> **Note:** Step 4 must be done after every N64Recomp run. The custom entrypoint skips COP0 hardware init, clears 3 BSS regions, and calls the game's real init function.

---

## Project Structure

```
extremeg/
├── README.md                 # You are here, going 500mph
├── CMakeLists.txt            # CMake build configuration
├── extremeg.recomp.toml      # N64Recomp configuration
├── symbols.toml              # Function symbols (93 libultra + 633 game functions)
├── .gitignore                # Keeps ROMs out of git
├── src/
│   ├── main.cpp              # Entry point, SDL window, runtime init
│   ├── audio.cpp             # SDL2 audio backend (48kHz)
│   ├── os_stubs.cpp          # Internal OS function stubs (33 functions)
│   ├── rt64_render_context.cpp  # RT64 D3D12/Vulkan renderer bridge
│   └── section_table.cpp     # Recompiled function lookup tables
├── include/                  # Project headers
├── tools/
│   ├── rom_analyzer.py       # ROM structure & function discovery
│   ├── lzss_decompress.py    # LZSS decompressor
│   ├── build_recomp_rom.py   # Builds patched ROM for recompilation
│   ├── string_dumper.py      # String extraction & categorization
│   └── progress.py           # Recompilation progress tracker
├── extracted/                # Decompressed code/data blocks (generated)
├── RecompiledFuncs/          # N64Recomp output (726 functions, generated)
├── rsp/                      # RSP microcode reimplementation
├── lib/                      # Dependencies (N64ModernRuntime, RT64, etc.)
└── screenshots/              # Progress screenshots
```

---

## Things We've Found In The ROM

Cracking the LZSS compression and disassembling the code revealed some gems:

- **Build path `d:\screen`** — Probe Entertainment was building from a `screen` directory on a D: drive. Classic late-90s dev setup
- **Developer names: Justin, Darren, Fergus** — the crew who built this speed demon left their names in the binary
- **`%s%d.tga`** — TGA texture loading format strings, confirming the asset pipeline
- **`p_bikeen_a_BOX_*_pal`** / **`c_bikeen_a_BOX_*_chr`** — bike texture palettes and character data, at least 23 texture boxes per bike
- **`Vrtbikeen_a_*`** — vertex data for bike 3D models
- **`Strike`** — weapon/attack reference found in the game code
- **51 LZSS blocks** — custom compression with the `LZSS` magic header. 1 code block (320KB), 50 asset blocks. Everything is packed tight to fit in 8MB
- **707 functions** in the main code block — from tiny 28-byte leaf functions to a massive 24KB monster (probably the main game loop or renderer)

---

## The Tech Stack

| Component | Purpose |
|-----------|---------|
| [N64Recomp](https://github.com/N64Recomp/N64Recomp) | MIPS → C static recompiler |
| [N64ModernRuntime](https://github.com/N64Recomp/N64ModernRuntime) | libultra reimplementation (ultramodern + librecomp) |
| [RT64](https://github.com/rt64/rt64) | N64 RDP → D3D12/Vulkan renderer |
| [SDL2](https://github.com/libsdl-org/SDL) | Window, input, audio |
| CMake + MSVC | Build system |

---

## Related Projects

Other N64 static recompilation projects by [sp00nznet](https://github.com/sp00nznet):

| Project | Game | Status |
|---------|------|--------|
| [diddykongracing](https://github.com/sp00nznet/diddykongracing) | Diddy Kong Racing (N64) | Boots, renders, playable scenes |
| [racer](https://github.com/sp00nznet/racer) | Star Wars Episode I: Racer (N64) | Compiles, linking RT64 |
| [Rampage](https://github.com/sp00nznet/Rampage) | Rampage World Tour / Rampage 2 (N64) | Fully playable at 60fps |

And the broader recomp family: [Zelda64Recomp](https://github.com/Zelda64Recomp/Zelda64Recomp) (Majora's Mask), which proved this whole approach works.

---

## Contributing

This is an active research & development project. If you're into:
- N64 reverse engineering
- MIPS assembly
- Futuristic combat racing games from 1998
- Making old things go fast on new hardware

...then you're in the right place. Open an issue, submit a PR, or just star the repo and vibe.

---

## Legal

This project contains **no copyrighted game code or assets**. You must provide your own legally obtained ROM. Extreme-G is a trademark of Acclaim Entertainment (RIP). Game developed by Probe Entertainment.

This is a **clean-room reimplementation** of the runtime environment. The recompiled output is a mechanical transformation of legally obtained binaries for personal use.

---

<p align="center">
<i>"The future of racing isn't emulated. It's recompiled."</i>
<br><br>
<b>Break the sound barrier. Break the recompilation barrier.</b>
</p>
