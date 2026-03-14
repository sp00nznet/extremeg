// Section table for Extreme-G N64 recomp
// Includes the auto-generated overlay data from N64Recomp

// Temporarily redefine 'static' to nothing so section_table is non-static
#pragma warning(push)
#pragma warning(disable: 4005)
#define static
#include "../RecompiledFuncs/recomp_overlays.inl"
#undef static
#pragma warning(pop)

// num_sections has const (internal linkage in C++), re-export it
extern const size_t num_sections_export = sizeof(section_table) / sizeof(section_table[0]);
