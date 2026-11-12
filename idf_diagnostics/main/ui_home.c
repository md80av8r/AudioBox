// Home screen: status icons for the intercom box. The gear button opens the settings menu
// (audio mixer, diagnostics, firmware update).
#include <stdio.h>
#include "lvgl.h"
#include "diag_hw.h"
#include "codec.h"
#include "ui_home.h"

#define C_OK   lv_color_hex(0x1e9e50)
#define C_WARN lv_color_hex(0xe0a020)
#define C_OFF  lv_color_hex(0x666666)
#define C_BAD  lv_color_hex(0xd33a2c)

typedef struct {
    lv_obj_t *tile, *icon, *name, *state, *bar;
} tile_t;

static lv_obj_t *home_scr, *settings_target;
static tile_t t_mode, t_anr, t_mic, t_link;

static void tile_set(tile_t *t, lv_color_t c, const char *state)
{
    lv_obj_set_style_border_color(t->tile, c, 0);
    lv_obj_set_style_text_color(t->icon, c, 0);
    lv_obj_set_style_text_color(t->state, c, 0);
    lv_label_set_text(t->state, state);
}

static void make_tile(tile_t *t, lv_obj_t *parent, int x, const char *icon, const char *name, lv_event_cb_t cb)
{
    t->tile = lv_obj_create(parent);
    lv_obj_set_size(t->tile, 180, 270);
    lv_obj_set_pos(t->tile, x, 100);
    lv_obj_remove_flag(t->tile, LV_OBJ_FLAG_SCROLLABLE);
    lv_obj_set_style_radius(t->tile, 18, 0);
    lv_obj_set_style_border_width(t->tile, 4, 0);
    lv_obj_set_style_bg_color(t->tile, lv_color_hex(0x1c1c1c), 0);
    if (cb) lv_obj_add_event_cb(t->tile, cb, LV_EVENT_CLICKED, NULL);

    t->icon = lv_label_create(t->tile);
    lv_label_set_text(t->icon, icon);
    lv_obj_set_style_text_font(t->icon, &lv_font_montserrat_48, 0);
    lv_obj_align(t->icon, LV_ALIGN_TOP_MID, 0, 22);

    t->name = lv_label_create(t->tile);
    lv_label_set_text(t->name, name);
    lv_obj_set_style_text_color(t->name, lv_color_hex(0xbbbbbb), 0);
    lv_obj_set_style_text_font(t->name, &lv_font_montserrat_20, 0);
    lv_obj_align(t->name, LV_ALIGN_TOP_MID, 0, 110);

    t->state = lv_label_create(t->tile);
    lv_obj_set_style_text_font(t->state, &lv_font_montserrat_20, 0);
    lv_obj_align(t->state, LV_ALIGN_TOP_MID, 0, 160);
    lv_label_set_text(t->state, "");
    t->bar = NULL;
}

static void mode_cb(lv_event_t *e)
{
    (void)e;
    diag_set_bypass(!diag_bypass_get());
}

static void anr_cb(lv_event_t *e)
{
    (void)e;
    diag_set_anr(!diag_anr_get());
}

static void mic_cb(lv_event_t *e)
{
    (void)e;
    if (codec_tone_playing()) {
        codec_tone_stop();
    } else if (!codec_monitor_start()) {
        codec_set_mic_input(1);
    }
}

static void gear_cb(lv_event_t *e)
{
    (void)e;
    lv_screen_load(settings_target);
}

static void home_timer_cb(lv_timer_t *t)
{
    (void)t;
    if (lv_screen_active() != home_scr) return;

    bool act = diag_bypass_get();
    tile_set(&t_mode, act ? C_OK : C_WARN, act ? "ACTIVE" : "BYPASS");

    bool anr = diag_anr_get();
    tile_set(&t_anr, anr ? C_OK : C_OFF, anr ? "ON" : "OFF");

    int l, r;
    bool clip;
    codec_meter_get(&l, &r, &clip);
    int pk = l > r ? l : r;
    if (!codec_tone_playing()) {
        tile_set(&t_mic, C_OFF, "OFF");
        lv_bar_set_value(t_mic.bar, 0, LV_ANIM_OFF);
    } else {
        tile_set(&t_mic, clip ? C_BAD : C_OK, clip ? "CLIP" : "LIVE");
        int pct = pk * 100 / 32768;
        lv_bar_set_value(t_mic.bar, pct, LV_ANIM_OFF);
    }

    tile_set(&t_link, C_OFF, "NO LINK");   // crew link comes next
}

lv_obj_t *ui_home_screen(void)
{
    return home_scr;
}

lv_obj_t *ui_home_create(lv_obj_t *settings_scr)
{
    settings_target = settings_scr;
    home_scr = lv_obj_create(NULL);
    lv_obj_remove_flag(home_scr, LV_OBJ_FLAG_SCROLLABLE);

    lv_obj_t *title = lv_label_create(home_scr);
    lv_label_set_text(title, "MD-88 Audio Companion");
    lv_obj_set_style_text_font(title, &lv_font_montserrat_20, 0);
    lv_obj_align(title, LV_ALIGN_TOP_LEFT, 20, 26);

    lv_obj_t *gear = lv_button_create(home_scr);
    lv_obj_set_size(gear, 90, 56);
    lv_obj_align(gear, LV_ALIGN_TOP_RIGHT, -16, 10);
    lv_obj_add_event_cb(gear, gear_cb, LV_EVENT_CLICKED, NULL);
    lv_obj_t *gl = lv_label_create(gear);
    lv_label_set_text(gl, LV_SYMBOL_SETTINGS);
    lv_obj_set_style_text_font(gl, &lv_font_montserrat_48, 0);
    lv_obj_center(gl);

    make_tile(&t_mode, home_scr, 15,  LV_SYMBOL_LOOP,        "MODE",  mode_cb);
    make_tile(&t_anr,  home_scr, 210, LV_SYMBOL_POWER,       "ANR",   anr_cb);
    make_tile(&t_mic,  home_scr, 405, LV_SYMBOL_AUDIO,       "MIC",   mic_cb);
    make_tile(&t_link, home_scr, 600, LV_SYMBOL_WIFI,        "LINK",  NULL);

    t_mic.bar = lv_bar_create(t_mic.tile);
    lv_obj_set_size(t_mic.bar, 130, 14);
    lv_bar_set_range(t_mic.bar, 0, 100);
    lv_bar_set_value(t_mic.bar, 0, LV_ANIM_OFF);
    lv_obj_align(t_mic.bar, LV_ALIGN_TOP_MID, 0, 205);

    lv_obj_t *hint = lv_label_create(home_scr);
    lv_label_set_text(hint, "Tap MODE, ANR or MIC to toggle.  Gear = settings.");
    lv_obj_set_style_text_color(hint, lv_color_hex(0x888888), 0);
    lv_obj_align(hint, LV_ALIGN_BOTTOM_LEFT, 20, -20);

    lv_timer_create(home_timer_cb, 150, NULL);
    home_timer_cb(NULL);
    return home_scr;
}
