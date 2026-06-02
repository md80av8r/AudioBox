// lv_conf.h — minimal LVGL 8.x configuration for MD-88
// Picked up because -DLV_CONF_INCLUDE_SIMPLE is in platformio.ini build flags

#ifndef LV_CONF_H
#define LV_CONF_H

#include <stdint.h>

// Color depth: 16-bit RGB565 to match TFT_eSPI default
#define LV_COLOR_DEPTH        16
#define LV_COLOR_16_SWAP      1

// Memory: use heap_caps_malloc through stdlib
#define LV_MEM_CUSTOM         0
#define LV_MEM_SIZE           (64U * 1024U)

// Display refresh tick — driven by Arduino millis()
#define LV_TICK_CUSTOM        1
#define LV_TICK_CUSTOM_INCLUDE "Arduino.h"
#define LV_TICK_CUSTOM_SYS_TIME_EXPR  (millis())

// Default refresh / input device read period
#define LV_DISP_DEF_REFR_PERIOD  16     // ~60 fps cap
#define LV_INDEV_DEF_READ_PERIOD 30

// Enable features we use
#define LV_USE_LOG            1
#define LV_LOG_LEVEL          LV_LOG_LEVEL_WARN
#define LV_LOG_PRINTF         1

#define LV_USE_LABEL          1
#define LV_USE_BAR            1
#define LV_USE_BTN            1
#define LV_USE_IMG            1
#define LV_USE_LINE           1
#define LV_USE_ARC            1
#define LV_USE_SLIDER         1
#define LV_USE_SWITCH         1

// Fonts we reference
#define LV_FONT_MONTSERRAT_14  1
#define LV_FONT_MONTSERRAT_16  1
#define LV_FONT_MONTSERRAT_20  1
#define LV_FONT_MONTSERRAT_24  1
#define LV_FONT_MONTSERRAT_48  1

#define LV_FONT_DEFAULT      &lv_font_montserrat_14

// Themes
#define LV_USE_THEME_DEFAULT 1
#define LV_THEME_DEFAULT_DARK 1

#endif // LV_CONF_H
