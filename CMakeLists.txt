cmake_minimum_required(VERSION 3.20)
project(ExtremeGRecompiled LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED True)

# Fetch SDL2
include(FetchContent)
FetchContent_Declare(
    SDL2
    URL https://github.com/libsdl-org/SDL/releases/download/release-2.30.3/SDL2-2.30.3.zip
    DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)
FetchContent_MakeAvailable(SDL2)

# N64ModernRuntime (ultramodern + librecomp)
add_subdirectory(lib/N64ModernRuntime)

# Recompiled functions static library
file(GLOB RECOMP_SOURCES "RecompiledFuncs/*.c" "RecompiledFuncs/*.cpp")
if(RECOMP_SOURCES)
    add_library(RecompiledFuncs STATIC ${RECOMP_SOURCES})
    target_include_directories(RecompiledFuncs PRIVATE
        include
        lib/N64ModernRuntime/ultramodern/include
        lib/N64ModernRuntime/librecomp/include
        lib/N64ModernRuntime/N64Recomp/include
    )
    target_compile_options(RecompiledFuncs PRIVATE
        $<$<C_COMPILER_ID:MSVC>:/w>
        $<$<C_COMPILER_ID:Clang>:-fno-strict-aliasing -Wno-unused-variable -Wno-implicit-function-declaration>
        $<$<C_COMPILER_ID:GNU>:-fno-strict-aliasing -Wno-unused-variable -Wno-implicit-function-declaration>
    )
    if(MSVC)
        target_compile_options(RecompiledFuncs PRIVATE /w /Zi)
    endif()
endif()

# Main executable
add_executable(ExtremeGRecompiled
    src/main.cpp
    src/stubs.cpp
)

target_include_directories(ExtremeGRecompiled PRIVATE
    include
    RecompiledFuncs
    lib/N64ModernRuntime/ultramodern/include
    lib/N64ModernRuntime/librecomp/include
    lib/N64ModernRuntime/N64Recomp/include
)

target_link_libraries(ExtremeGRecompiled PRIVATE
    librecomp
    ultramodern
    SDL2::SDL2
    SDL2::SDL2main
)

if(RECOMP_SOURCES)
    target_link_libraries(ExtremeGRecompiled PRIVATE RecompiledFuncs)
endif()

if(WIN32)
    target_link_libraries(ExtremeGRecompiled PRIVATE Winmm.lib Dbghelp.lib)
    target_compile_options(ExtremeGRecompiled PRIVATE /Zi)
    target_link_options(ExtremeGRecompiled PRIVATE $<$<CONFIG:Release>:/DEBUG /OPT:REF /OPT:ICF /MAP>)
    set_target_properties(ExtremeGRecompiled PROPERTIES
        VS_DEBUGGER_WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
    )
    add_custom_command(TARGET ExtremeGRecompiled POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "$<TARGET_FILE_DIR:SDL2::SDL2>/SDL2.dll"
            "$<TARGET_FILE_DIR:ExtremeGRecompiled>/SDL2.dll"
    )
endif()

target_compile_definitions(ExtremeGRecompiled PRIVATE
    EXTREMEG_VERSION_MAJOR=0
    EXTREMEG_VERSION_MINOR=1
    EXTREMEG_VERSION_PATCH=0
    NOMINMAX
)
