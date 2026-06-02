// theme.h — Pro-Pilot color scheme (ForeFlight / Garmin Pilot inspired)
#pragma once
#include <lvgl.h>

// Backgrounds
#define COLOR_BG_PRIMARY   lv_color_hex(0x0F141A)  // page background
#define COLOR_BG_TILE      lv_color_hex(0x1F2932)  // tile / card body
#define COLOR_BG_TILE_SEL  lv_color_hex(0x2563EB)  // tile when selected/hovered
#define COLOR_BG_BAR       lv_color_hex(0x161D24)  // top status bar

// Text
#define COLOR_TEXT_PRIMARY   lv_color_hex(0xE8EEF4)  // off-white main text
#define COLOR_TEXT_SECONDARY lv_color_hex(0x8B97A3)  // grey labels
#define COLOR_TEXT_DIM       lv_color_hex(0x4A5562)  // very dim labels

// Accents
#define COLOR_ACCENT_CYAN   lv_color_hex(0x4A9EFF)  // primary action / status OK
#define COLOR_ACCENT_AMBER  lv_color_hex(0xFFB347)  // time, attention
#define COLOR_ACCENT_GREEN  lv_color_hex(0x4AFF7F)  // success / connected
#define COLOR_ACCENT_RED    lv_color_hex(0xFF4A4A)  // warning / disconnected

// Border
#define COLOR_BORDER       lv_color_hex(0x2D3744)
#define COLOR_BORDER_HOT   lv_color_hex(0x4A9EFF)
