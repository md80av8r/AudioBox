// ui_home.cpp — Home screen: clock + status icons + env data
#include <lvgl.h>
#include <Arduino.h>
#include "ui.h"
#include "theme.h"
#include "state.h"

// Widgets we update each tick
static lv_obj_t *lbl_zulu, *lbl_local, *lbl_zone;
static lv_obj_t *lbl_batt, *lbl_temp, *lbl_humid;
static lv_obj_t *icon_bt, *icon_net, *icon_headset, *lbl_mode;

lv_obj_t* ui_home_create() {
  lv_obj_t* scr = lv_obj_create(NULL);
  lv_obj_set_style_bg_color(scr, COLOR_BG_PRIMARY, 0);
  lv_obj_set_style_pad_all(scr, 0, 0);
  lv_obj_set_style_border_width(scr, 0, 0);

  // ─── Top status bar ──────────────────────────────────────
  lv_obj_t* bar = lv_obj_create(scr);
  lv_obj_set_size(bar, 320, 30);
  lv_obj_align(bar, LV_ALIGN_TOP_MID, 0, 0);
  lv_obj_set_style_bg_color(bar, COLOR_BG_BAR, 0);
  lv_obj_set_style_border_width(bar, 0, 0);
  lv_obj_set_style_pad_all(bar, 4, 0);
  lv_obj_set_style_radius(bar, 0, 0);

  // status icons (right side)
  icon_headset = lv_label_create(bar);
  lv_label_set_text(icon_headset, LV_SYMBOL_AUDIO);
  lv_obj_set_style_text_color(icon_headset, COLOR_TEXT_DIM, 0);
  lv_obj_align(icon_headset, LV_ALIGN_RIGHT_MID, -8, 0);

  icon_bt = lv_label_create(bar);
  lv_label_set_text(icon_bt, LV_SYMBOL_BLUETOOTH);
  lv_obj_set_style_text_color(icon_bt, COLOR_TEXT_DIM, 0);
  lv_obj_align(icon_bt, LV_ALIGN_RIGHT_MID, -32, 0);

  icon_net = lv_label_create(bar);
  lv_label_set_text(icon_net, LV_SYMBOL_WIFI);
  lv_obj_set_style_text_color(icon_net, COLOR_TEXT_DIM, 0);
  lv_obj_align(icon_net, LV_ALIGN_RIGHT_MID, -56, 0);

  lbl_batt = lv_label_create(bar);
  lv_label_set_text(lbl_batt, LV_SYMBOL_BATTERY_3 " 87%");
  lv_obj_set_style_text_color(lbl_batt, COLOR_ACCENT_GREEN, 0);
  lv_obj_align(lbl_batt, LV_ALIGN_RIGHT_MID, -88, 0);

  // mode badge (left)
  lbl_mode = lv_label_create(bar);
  lv_label_set_text(lbl_mode, "IDLE");
  lv_obj_set_style_text_color(lbl_mode, COLOR_TEXT_PRIMARY, 0);
  lv_obj_align(lbl_mode, LV_ALIGN_LEFT_MID, 8, 0);

  // ─── Clock area ──────────────────────────────────────────
  lbl_zulu = lv_label_create(scr);
  lv_label_set_text(lbl_zulu, "18:24:37");
  lv_obj_set_style_text_color(lbl_zulu, COLOR_ACCENT_AMBER, 0);
  lv_obj_set_style_text_font(lbl_zulu, &lv_font_montserrat_48, 0);
  lv_obj_align(lbl_zulu, LV_ALIGN_TOP_MID, -30, 50);

  lbl_zone = lv_label_create(scr);
  lv_label_set_text(lbl_zone, "Z");
  lv_obj_set_style_text_color(lbl_zone, COLOR_TEXT_SECONDARY, 0);
  lv_obj_set_style_text_font(lbl_zone, &lv_font_montserrat_24, 0);
  lv_obj_align_to(lbl_zone, lbl_zulu, LV_ALIGN_OUT_RIGHT_BOTTOM, 6, -4);

  lbl_local = lv_label_create(scr);
  lv_label_set_text(lbl_local, "14:24 EDT");
  lv_obj_set_style_text_color(lbl_local, COLOR_TEXT_SECONDARY, 0);
  lv_obj_set_style_text_font(lbl_local, &lv_font_montserrat_20, 0);
  lv_obj_align(lbl_local, LV_ALIGN_TOP_MID, 0, 115);

  // ─── Bottom env bar ──────────────────────────────────────
  lv_obj_t* envbar = lv_obj_create(scr);
  lv_obj_set_size(envbar, 320, 50);
  lv_obj_align(envbar, LV_ALIGN_BOTTOM_MID, 0, 0);
  lv_obj_set_style_bg_color(envbar, COLOR_BG_TILE, 0);
  lv_obj_set_style_border_width(envbar, 0, 0);
  lv_obj_set_style_pad_all(envbar, 8, 0);
  lv_obj_set_style_radius(envbar, 0, 0);

  lbl_temp = lv_label_create(envbar);
  lv_label_set_text(lbl_temp, LV_SYMBOL_WARNING " 23.4°C");
  lv_obj_set_style_text_color(lbl_temp, COLOR_TEXT_PRIMARY, 0);
  lv_obj_align(lbl_temp, LV_ALIGN_LEFT_MID, 8, 0);

  lbl_humid = lv_label_create(envbar);
  lv_label_set_text(lbl_humid, LV_SYMBOL_TINT " 45%");
  lv_obj_set_style_text_color(lbl_humid, COLOR_TEXT_PRIMARY, 0);
  lv_obj_align(lbl_humid, LV_ALIGN_LEFT_MID, 130, 0);

  // Volume preview on right
  lv_obj_t* lbl_vol = lv_label_create(envbar);
  lv_label_set_text(lbl_vol, LV_SYMBOL_VOLUME_MAX " 72");
  lv_obj_set_style_text_color(lbl_vol, COLOR_ACCENT_CYAN, 0);
  lv_obj_align(lbl_vol, LV_ALIGN_RIGHT_MID, -8, 0);

  return scr;
}

// Called from ui_tick() — pull g_state into widgets
void ui_home_update() {
  if (!lbl_batt) return;
  char buf[32];

  // Battery
  int pct = constrain((int)((g_state.batt_v - 3.3f) / (4.2f - 3.3f) * 100.0f), 0, 100);
  const char* sym = pct > 75 ? LV_SYMBOL_BATTERY_FULL :
                    pct > 50 ? LV_SYMBOL_BATTERY_3 :
                    pct > 25 ? LV_SYMBOL_BATTERY_2 :
                    pct > 10 ? LV_SYMBOL_BATTERY_1 : LV_SYMBOL_BATTERY_EMPTY;
  snprintf(buf, sizeof(buf), "%s %d%%", sym, pct);
  lv_label_set_text(lbl_batt, buf);
  lv_obj_set_style_text_color(lbl_batt,
    pct > 30 ? COLOR_ACCENT_GREEN : pct > 10 ? COLOR_ACCENT_AMBER : COLOR_ACCENT_RED, 0);

  // Env
  snprintf(buf, sizeof(buf), LV_SYMBOL_WARNING " %.1f°C", g_state.temp_c);
  lv_label_set_text(lbl_temp, buf);
  snprintf(buf, sizeof(buf), LV_SYMBOL_TINT " %.0f%%", g_state.humidity);
  lv_label_set_text(lbl_humid, buf);

  // Headset detect color
  lv_obj_set_style_text_color(icon_headset,
    g_state.headset_in ? COLOR_ACCENT_GREEN : COLOR_TEXT_DIM, 0);

  // Mode badge
  static const char* mode_names[] = {"BOOT","IDLE","COMMS","MUSIC","ATC","SETUP"};
  lv_color_t mode_col[] = {COLOR_TEXT_DIM, COLOR_TEXT_PRIMARY, COLOR_ACCENT_GREEN,
                           COLOR_ACCENT_CYAN, COLOR_ACCENT_AMBER, COLOR_TEXT_SECONDARY};
  uint8_t m = (uint8_t)g_state.mode;
  if (m < 6) {
    lv_label_set_text(lbl_mode, mode_names[m]);
    lv_obj_set_style_text_color(lbl_mode, mode_col[m], 0);
  }

  // Clock — placeholder until we wire the DS3231
  uint32_t t = millis() / 1000;
  uint32_t h = (t / 3600) % 24;
  uint32_t mi = (t / 60) % 60;
  uint32_t s = t % 60;
  snprintf(buf, sizeof(buf), "%02lu:%02lu:%02lu", h, mi, s);
  lv_label_set_text(lbl_zulu, buf);
}
