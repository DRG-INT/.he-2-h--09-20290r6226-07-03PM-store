#ifndef MACOS9_TOOLBOX_H
#define MACOS9_TOOLBOX_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Classic Macintosh 1984-2001 Toolbox Data Primitives */
typedef struct {
    int16_t v;
    int16_t h;
} Point;

typedef struct {
    int16_t top;
    int16_t left;
    int16_t bottom;
    int16_t right;
} Rect;

/* Macintosh Event Types */
enum {
    nullEvent    = 0,
    mouseDown    = 1,
    mouseUp      = 2,
    keyDown      = 3,
    keyUp        = 4,
    autoKey      = 5,
    updateEvt    = 6,
    diskEvt      = 7,
    activateEvt  = 8,
    osEvt        = 15,
    kHighLevelEvent = 23 /* AppleEvents */
};

typedef struct {
    uint16_t what;
    uint32_t message;
    uint32_t when;
    Point    where;
    uint16_t modifiers;
} EventRecord;

/* SIOUX (Simple Input Output User eXchange) Configuration */
typedef struct {
    char     window_title[64];
    int16_t  rows;
    int16_t  columns;
    int16_t  font_size;      /* Typically 9 pt */
    char     font_name[32];   /* "Monaco" */
    bool     auto_scroll;
    bool     autonomous_mode; /* Runs commands automatically without prompting */
} SIOUXSettings;

#ifdef __cplusplus
}
#endif

#endif /* MACOS9_TOOLBOX_H */
