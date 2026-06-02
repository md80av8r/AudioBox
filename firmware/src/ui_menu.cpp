// ui_menu.cpp — Main Menu (3×2 tile grid, Garmin-style)
#include <lvgl.h>
#include "ui.h"
#include "theme.h"
#include "state.h"

struct Tile { const char* label; const char* icon; lv_color_t color; };
static const Tile TILES[6] = {
  { "Audio Mixer",   LV_SYMBOL_VOLUME_MAX, COLOR_ACCENT_CYAN  },
  { "Crew Comms",    LV_SYMBOL_WIFI,       COLOR_ACCENT_GREEN },
  { "Bluetooth",     LV_SYMBOL_BLUETOOTH,  COLOR_ACCENT_CYAN  },
  { "ATC Playback",  LV_SYMBOL_AUDIO,      COLOR_ACCENT_AMBER },
  { "Cabin Env",     LV_SYMBOL_WARNING,    COLOR_ACCENT_GREEN },
  { "Settings",      LV_SYMBOL_SETTINGS,   COLOR_TEXT_SECONDARY }
};

static lv_obj_t* tiles[6];
static int sel = 0;  // currently-highlighted tile (encoder navigation)

static void tile_click_cb(lv_event_t* e) {
  int idx = (int)(intptr_t)lv_event_get_user_data(e);
  // For now just log — wire actual screens later
  Serial.printf("[menu] tile %d (%s) clicked\n", idx, TILES[idx].label);
  if (idx == 0) ui_goto(ui_audio_create());
}

lv_obj_t* ui_menu_create() {
  lv_obj_t* scr = lv_obj_create(NULL);
  lv_obj_set_style_bg_color(scr, COLOR_BG_PRIMARY, 0);
  lv_obj_set_style_pad_all(scr, 0, 0);
  lv_obj_set_style_border_width(scr, 0, 0);

  // Top bar with title
  lv_obj_t* bar = lv_obj_create(scr);
  lv_obj_set_size(bar, 320, 30);
  lv_obj_align(bar, LV_ALIGN_TOP_MID, 0, 0);
  lv_obj_set_style_bg_color(bar, COLOR_BG_BAR, 0);
  lv_obj_set_style_border_width(bar, 0, 0);
  lv_obj_set_style_radius(bar, 0, 0);
  lv_obj_set_style_pad_all(bar, 4, 0);

  lv_obj_t* title = lv_label_create(bar);
  lv_label_set_text(title, LV_SYMBOL_LIST "  Main Menu");
  lv_obj_set_style_text_color(title, COLOR_TEXT_PRIMARY, 0);
  lv_obj_align(title, LV_ALIGN_LEFT_MID, 8, 0);

  // 3 columns × 2 rows of tiles in 320×210 area below status bar
  const int W = 320, TILE_W = 100, TILE_H = 90;
  const int gx = (W - 3 * TILE_W) / 4;   // gutter between tiles
  const int gy = 12;
  const int y0 = 40;

  for (int i = 0; i < 6; i++) {
    int row = i / 3, col = i % 3;
    int x = gx + col * (TILE_W + gx);
    int y = y0 + row * (TILE_H + gy);

    lv_obj_t* tile = lv_obj_create(scr);
    lv_obj_set_size(tile, TILE_W, TILE_H);
    lv_obj_set_pos(tile, x, y);
    lv_obj_set_style_bg_color(tile, COLOR_BG_TILE, 0);
    lv_obj_set_style_border_color(tile, COLOR_BORDER, 0);
    lv_obj_set_style_border_width(tile, 1, 0);
    lv_obj_set_style_radius(tile, 8, 0);
    lv_obj_set_style_pad_all(tile, 4, 0);
    lv_obj_clear_flag(tile, LV_OBJ_FLAG_SCROLLABLE);
    lv_obj_add_event_cb(tile, tile_click_cb, LV_EVENT_CLICKED, (void*)(intptr_t)i);

    // Icon (top of tile)
    lv_obj_t* icn = lv_label_create(tile);
    lv_label_set_text(icn, TILES[i].icon);
    lv_obj_set_style_text_color(icn, TILES[i].color, 0);
    lv_obj_set_style_text_font(icn, &lv_font_montserrat_24, 0);
    lv_obj_align(icn, LV_ALIGN_TOP_MID, 0, 8);

    // Label (bottom)
    lv_obj_t* lbl = lv_label_create(tile);
    lv_label_set_text(lbl, TILES[i].label);
    lv_obj_set_style_text_color(lbl, COLOR_TEXT_PRIMARY, 0);
    lv_obj_set_style_text_align(lbl, LV_TEXT_ALIGN_CENTER, 0);
    lv_label_set_long_mode(lbl, LV_LABEL_LONG_WRAP);
    lv_obj_set_width(lbl, TILE_W - 8);
    lv_obj_align(lbl, LV_ALIGN_BOTTOM_MID, 0, -4);

    tiles[i] = tile;
  }

  // Highlight first tile
  lv_obj_set_style_border_color(tiles[0], COLOR_BORDER_HOT, 0);
  lv_obj_set_style_border_width(tiles[0], 2, 0);
  sel = 0;

  return scr;
}

// Encoder rotation moves the highlight
void ui_menu_move_selection(int delta) {
  // Clear old
  lv_obj_set_style_border_color(tiles[sel], COLOR_BORDER, 0);
  lv_obj_set_style_border_width(tiles[sel], 1, 0);
  // New
  sel = (sel + delta + 6) % 6;
  lv_obj_set_style_border_color(tiles[sel], COLOR_BORDER_HOT, 0);
  lv_obj_set_style_border_width(tiles[sel], 2, 0);
}

int ui_menu_get_selection() { return sel; }
