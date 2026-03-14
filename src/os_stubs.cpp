// Stub implementations for internal N64 OS functions
// These are internal libultra helpers that N64Recomp generates redirects for,
// but ultramodern reimplements at a higher level (e.g., osSendMesg reimplements
// the full logic without calling __osEnqueueThread/__osPopThread internally).
// The stubs exist only to satisfy the linker for code paths that should never
// be reached at runtime.

#include <cstdio>
#include <cstdint>
#include "recomp.h"

#define STUB(name) \
    extern "C" void name##_recomp(uint8_t* rdram, recomp_context* ctx) { \
        fprintf(stderr, "[ExtremeG] STUB called: " #name "_recomp\n"); \
    }

// Thread scheduling internals (ultramodern handles threading natively)
STUB(__osEnqueueThread)
STUB(__osPopThread)
STUB(__osDequeueThread)

// Timer internals (ultramodern has its own timer system)
STUB(__osTimerServicesInit)
STUB(__osTimerInterrupt)
STUB(__osInsertTimer)
STUB(__osSetTimerIntr)

// VI internals (RT64 handles video)
STUB(__osViInit)
STUB(__osViGetCurrentContext)
STUB(__osViSwapContext)

// SP/RSP internals (RT64 handles RSP)
STUB(__osSpSetStatus)
STUB(__osSpRawStartDma)
STUB(__osSpDeviceBusy)

// SI internals (ultramodern handles controller/SI)
STUB(__osSiRawReadIo)
STUB(__osSiRawStartDma)
STUB(__osSiCreateAccessQueue)
STUB(__osSiGetAccess)
STUB(__osSiRelAccess)

// PI internals (ultramodern handles PI/DMA)
STUB(osPiRawReadIo)
STUB(__osPiRawStartDma)
STUB(__osPiDeviceBusy)
STUB(__osPiCreateAccessQueue)
STUB(osEPiRawReadIo)
STUB(osEPiRawWriteIo)

// AI internals (audio handled by SDL)
STUB(__osAiDeviceBusy)

// Interrupt internals
// NOTE: __osDisableInt, __osRestoreInt, __osSetFpcCsr already in ultramodern
STUB(__osSetGlobalIntMask)
STUB(__osResetGlobalIntMask)
STUB(__osGetCause)

// COP0 / status register (not applicable on PC)
STUB(__osGetSR)
STUB(__osSetSR)
STUB(__osSetCompare)
STUB(__osGetFpcCsr)
// NOTE: __osSetFpcCsr already in ultramodern

// Cache operations (no-op on PC)
// NOTE: osWritebackDCache, osWritebackDCacheAll, osInvalDCache, osInvalICache already in ultramodern

// Thread internals
STUB(__osEnqueueAndYield)
STUB(__osDispatchThread)
STUB(__osCleanupThread)
