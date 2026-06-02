// ui_audio.cpp — Audio Mixer (master volume + per-source levels)
#include <lvgl.h>
#include "ui.h"
#include "theme.h"
#include "state.h"

static lv_obj_t *bar_master, *lbl_master_val;

lv_obj_t* ui_audio_create() {
  lv_obj_t* scr = lv_obj_create(NULL);
  lv_obj_set_style_bg_color(scr, COLOR_BG_PRIMARY, 0);
  lv_obj_set_style_pad_all(scr, 0, 0);
  lv_obj_set_style_border_width(scr, 0, 0);

  // Top bar
  lv_obj_t* bar = lv_obj_create(scr);
  lv_obj_set_size(bar, 320, 30);
  lv_obj_align(bar, LV_ALIGN_TOP_MID, 0, 0);
  lv_obj_set_style_bg_color(bar, COLOR_BG_BAR, 0);
  lv_obj_set_style_border_width(bar, 0, 0);
  lv_obj_set_style_radius(bar, 0, 0);

  lv_obj_t* title = lv_label_create(bar);
  lv_label_set_text(title, LV_SYMBOL_VOLUME_MAX "  Audio Mixer");
  lv_obj_set_style_text_color(title, COLOR_ACCENT_CYAN, 0);
  lv_obj_align(title, LV_ALIGN_LEFT_MID, 8, 0);

  // Big master volume number, center
  lbl_master_val = lv_label_create(scr);
  lv_label_set_text(lbl_master_val, "50");
  lv_obj_set_style_text_color(lbl_master_val, COLOR_ACCENT_AMBER, 0);
  lv_obj_set_style_text_font(lbl_master_val, &lv_font_montserrat_48, 0);
  lv_obj_align(lbl_master_val, LV_ALIGN_TOP_MID, 0, 50);

  lv_obj_t* lbl_master_lbl = lv_label_create(scr);
  lv_label_set_text(lbl_master_lbl, "MASTER VOLUME");
  lv_obj_set_style_text_color(lbl_master_lbl, COLOR_TEXT_SECONDARY, 0);
  lv_obj_align(lbl_master_lbl, LV_ALIGN_TOP_MID, 0, 110);

  // Master volume bar
  bar_master = lv_bar_create(scr);
  lv_obj_set_size(bar_master, 280, 16);
  lv_obj_align(bar_master, LV_ALIGN_TOP_MID, 0, 145);
  lv_bar_set_range(bar_master, 0, 100);
  lv_bar_set_value(bar_master, 50, LV_ANIM_OFF);
  lv_obj_set_style_bg_color(bar_master, COLOR_BG_TILE, 0);
  lv_obj_set_style_bg_color(bar_master, COLOR_ACCENT_CYAN, LV_PART_INDICATOR);
  lv_obj_set_style_radius(bar_master, 4, LV_PART_MAIN);
  lv_obj_set_style_radius(bar_master, 4, LV_PART_INDICATOR);

  // Hint at bottom
  lv_obj_t* hint = lv_label_create(scr);
  lv_label_set_text(hint, "Turn encoder to adjust  •  Press to return");
  lv_obj_set_style_text_color(hint, COLOR_TEXT_DIM, 0);
  lv_obj_align(hint, LV_ALIGN_BOTTOM_MID, 0, -10);

  return scr;
}

void ui_audio_update() {
  if (!bar_master) return;
  lv_bar_set_value(bar_master, g_state.volume, LV_ANIM_ON);
  char buf[8];
  snprintf(buf, sizeof(buf), "%d", g_state.volume);
  lv_label_set_text(lbl_master_val, buf);
}
