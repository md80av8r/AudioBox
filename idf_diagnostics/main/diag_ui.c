// Diagnostics screen: I2C device status, control lines, expander inputs, haptic.
#include <stdio.h>
#include <math.h>
#include "lvgl.h"
#include "diag_hw.h"
#include "diag_ui.h"
#include "ota.h"
#include "codec.h"
#include "selftest.h"
#include "ui_home.h"
#include <stdlib.h>

#define COL_OK  lv_color_hex(0x1e9e50)
#define COL_BAD lv_color_hex(0xd33a2c)

static lv_obj_t *dev_status[8];
static lv_obj_t *exp_led[8];
static lv_obj_t *exp_state;
static lv_obj_t *status_line;
static lv_obj_t *enc_line;
static lv_obj_t *update_btn_label;
static lv_obj_t *tone_btn_label;
static lv_obj_t *mon_btn_label;
static lv_obj_t *loop_btn_label;
static lv_obj_t *mic_bar;
static lv_obj_t *gain_label;
static lv_obj_t *vol_label;
static lv_obj_t *set_status, *set_update_lbl;   // settings-menu copies of the update status

static const char *exp_names[8] = {
    "Encoder A", "Encoder B", "Power button", "Inner enc A",
    "Inner enc B", "Encoder push", "Bypass state", "Spare 5",
};

static lv_obj_t *make_panel(lv_obj_t *parent, const char *title, int x, int w)
{
    lv_obj_t *p = lv_obj_create(parent);
    lv_obj_set_size(p, w, 370);
    lv_obj_align(p, LV_ALIGN_TOP_LEFT, x, 50);
    lv_obj_t *t = lv_label_create(p);
    lv_label_set_text(t, title);
    lv_obj_align(t, LV_ALIGN_TOP_LEFT, 0, 0);
    return p;
}

static void refresh_devices(void)
{
    for (int i = 0; i < diag_dev_count(); i++) {
        const diag_dev_t *d = diag_dev(i);
        lv_label_set_text(dev_status[i], d->present ? "OK" : "MISSING");
        lv_obj_set_style_text_color(dev_status[i], d->present ? COL_OK : COL_BAD, 0);
    }
}

static void anr_cb(lv_event_t *e)
{
    lv_obj_t *sw = (lv_obj_t *)lv_event_get_target(e);
    bool on = lv_obj_has_state(sw, LV_STATE_CHECKED);
    diag_set_anr(on);
    lv_label_set_text(status_line, on ? "ANR_POWER_EN on (white LED needs a battery)"
                                      : "ANR_POWER_EN off");
}

static void bypass_cb(lv_event_t *e)
{
    lv_obj_t *sw = (lv_obj_t *)lv_event_get_target(e);
    bool on = lv_obj_has_state(sw, LV_STATE_CHECKED);
    diag_set_bypass(on);
    lv_label_set_text(status_line, on ? "BYPASS_EN on" : "BYPASS_EN off");
}

static void haptic_cb(lv_event_t *e)
{
    (void)e;
    lv_label_set_text(status_line, diag_haptic_buzz() ? "Haptic: buzz sent"
                                                      : "Haptic: I2C error");
}

static void tone_cb(lv_event_t *e)
{
    (void)e;
    if (!codec_tone_playing()) {
        const char *err = codec_tone_start();
        if (!err) {
            lv_label_set_text(tone_btn_label, "Stop tone");
            lv_label_set_text(status_line, "Playing 1 kHz tone (try the Bypass switch if silent)");
        } else {
            lv_label_set_text_fmt(status_line, "Tone failed: %s", err);
        }
    } else {
        codec_tone_stop();
        lv_label_set_text(tone_btn_label, "Play tone");
        lv_label_set_text(status_line, "Tone stopped");
    }
}

static void selftest_cb(lv_event_t *e)
{
    (void)e;
    char *buf = malloc(4096);
    if (!buf) {
        lv_label_set_text(status_line, "Self-test: out of memory");
        return;
    }
    int passed;
    int failed = selftest_run(buf, 4096, &passed);
    printf("%s\n", buf);
    lv_label_set_text_fmt(status_line, "Self-test: %d pass, %d FAIL  (report: 192.168.4.1/report)",
                          passed, failed);
    free(buf);
}

static void monitor_cb(lv_event_t *e)
{
    (void)e;
    if (!codec_tone_playing()) {
        const char *err = codec_monitor_start();
        if (!err) {
            lv_label_set_text(mon_btn_label, "Stop monitor");
            lv_label_set_text(status_line, "Mic monitor on: talk into the mic, both ears");
        } else {
            lv_label_set_text_fmt(status_line, "Monitor failed: %s", err);
        }
    } else {
        codec_tone_stop();
        lv_label_set_text(mon_btn_label, "Mic monitor");
        lv_label_set_text(tone_btn_label, "Play tone");
        lv_label_set_text(status_line, "Stopped");
    }
}

static void loopback_cb(lv_event_t *e)
{
    (void)e;
    if (!codec_tone_playing()) {
        const char *err = codec_loopback_start();
        if (!err) {
            lv_label_set_text(loop_btn_label, "Stop loopback");
            lv_label_set_text(status_line, "Loopback: LINE OUT -> LINE IN. Watch the Mic level bar");
        } else {
            lv_label_set_text_fmt(status_line, "Loopback failed: %s", err);
        }
    } else {
        codec_tone_stop();
        lv_label_set_text(loop_btn_label, "Loopback test");
        lv_label_set_text(mon_btn_label, "Mic monitor");
        lv_label_set_text(tone_btn_label, "Play tone");
        lv_label_set_text(status_line, "Stopped");
    }
}

static void update_cb(lv_event_t *e)
{
    (void)e;
    if (!ota_running()) {
        if (ota_start()) {
            lv_label_set_text(update_btn_label, "Stop update mode");
            lv_label_set_text(status_line, "Wi-Fi " OTA_SSID " / " OTA_PASS " -> 192.168.4.1");
            lv_label_set_text(set_update_lbl, "Stop update mode");
            lv_label_set_text(set_status, "Join Wi-Fi " OTA_SSID " (" OTA_PASS "), open http://192.168.4.1");
        } else {
            lv_label_set_text(status_line, "Update mode failed to start");
            lv_label_set_text(set_status, "Update mode failed to start");
        }
    } else {
        ota_stop();
        lv_label_set_text(update_btn_label, "Firmware update");
        lv_label_set_text(status_line, "Update mode off");
        lv_label_set_text(set_update_lbl, "Firmware update");
        lv_label_set_text(set_status, "Update mode off");
    }
}

static void rescan_cb(lv_event_t *e)
{
    (void)e;
    diag_scan();
    refresh_devices();
    lv_label_set_text(status_line, "I2C rescan done");
}

static void expander_timer_cb(lv_timer_t *t)
{
    (void)t;
    uint8_t bits;
    bool ok = diag_expander_read(&bits);
    lv_label_set_text(exp_state, ok ? "" : "no answer");
    for (int i = 0; i < 8; i++) {
        if (ok && (bits & (1 << i))) lv_led_on(exp_led[i]);
        else                          lv_led_off(exp_led[i]);
    }

    lv_bar_set_value(mic_bar, codec_mic_level(), LV_ANIM_OFF);

    int32_t outer, inner;
    bool pushed;
    diag_enc_get(&outer, &inner, &pushed);
    lv_label_set_text_fmt(enc_line, "Encoder  outer: %d   inner: %d   push: %s",
                          (int)outer, (int)inner, pushed ? "DOWN" : "up");
}

static lv_obj_t *add_button_at(lv_obj_t *parent, const char *text, int x, int y, int w, int h, lv_event_cb_t cb)
{
    lv_obj_t *b = lv_button_create(parent);
    lv_obj_set_size(b, w, h);
    lv_obj_align(b, LV_ALIGN_TOP_LEFT, x, y);
    lv_obj_add_event_cb(b, cb, LV_EVENT_CLICKED, NULL);
    lv_obj_t *l = lv_label_create(b);
    lv_label_set_text(l, text);
    lv_obj_center(l);
    return b;
}

static lv_obj_t *add_button(lv_obj_t *parent, const char *text, int y, lv_event_cb_t cb)
{
    return add_button_at(parent, text, 0, y, 200, 60, cb);
}

static void volume_cb(lv_event_t *e)
{
    lv_obj_t *sl = (lv_obj_t *)lv_event_get_target(e);
    int v = (int)lv_slider_get_value(sl);
    codec_set_out_volume(v);
    lv_label_set_text_fmt(vol_label, "Out vol %d dB", (int)((v - 30) * 3 / 2));
}

static void gain_cb(lv_event_t *e)
{
    lv_obj_t *sl = (lv_obj_t *)lv_event_get_target(e);
    int step = (int)lv_slider_get_value(sl);
    codec_set_mic_gain(step);
    lv_label_set_text_fmt(gain_label, "Mic gain %d dB", step * 3);
}


// ======================= Mixer page =======================
static lv_obj_t *diag_scr, *mix_scr, *settings_scr, *mix_return;
static lv_obj_t *mx_mon_btn, *mx_mon_lbl, *mx_meter[2], *mx_db[2], *mx_clip;
static lv_obj_t *mx_val_gain, *mx_val_side, *mx_val_out;
static lv_obj_t *mx_src_btn[5];
static lv_obj_t *mx_input_btn[2];
static lv_obj_t *mx_status;
static int mx_src = 4, mx_input = 1;

static int level_pct(int pk)
{
    if (pk <= 0) return 0;
    int p = (int)((20.0f * log10f((float)pk / 32768.0f) + 60.0f) / 60.0f * 100.0f);
    return p < 0 ? 0 : (p > 100 ? 100 : p);
}

static int level_db(int pk)
{
    return pk > 0 ? (int)(20.0f * log10f((float)pk / 32768.0f)) : -99;
}

static void mx_set_active(lv_obj_t *b, bool on)
{
    lv_obj_set_style_bg_color(b, on ? lv_color_hex(0x1e9e50) : lv_color_hex(0x555555), 0);
}

static void mx_monitor_cb(lv_event_t *e)
{
    (void)e;
    if (!codec_tone_playing()) {
        const char *err = codec_monitor_start();
        if (err) {
            lv_label_set_text_fmt(mx_status, "Monitor failed: %s", err);
            return;
        }
        codec_set_mic_input(mx_input);
        lv_label_set_text(mx_mon_lbl, "MONITOR ON");
        mx_set_active(mx_mon_btn, true);
        lv_label_set_text(mx_status, "Monitor running. Talk into the mic.");
    } else {
        codec_tone_stop();
        lv_label_set_text(mx_mon_lbl, "MONITOR OFF");
        mx_set_active(mx_mon_btn, false);
        lv_label_set_text(mx_status, "Monitor stopped");
    }
}

static void mx_gain_cb(lv_event_t *e)
{
    int v = (int)lv_slider_get_value((lv_obj_t *)lv_event_get_target(e));
    codec_set_mic_gain(v);
    lv_label_set_text_fmt(mx_val_gain, "%d dB", v * 3);
}

static void mx_side_cb(lv_event_t *e)
{
    int v = (int)lv_slider_get_value((lv_obj_t *)lv_event_get_target(e));
    codec_set_sidetone_db(v);
    lv_label_set_text_fmt(mx_val_side, "%+d dB", v);
}

static void mx_out_cb(lv_event_t *e)
{
    int v = (int)lv_slider_get_value((lv_obj_t *)lv_event_get_target(e));
    codec_set_out_volume(v);
    lv_label_set_text_fmt(mx_val_out, "%d dB", (int)((v - 30) * 3 / 2));
}

static void mx_src_cb(lv_event_t *e)
{
    mx_src = (int)(intptr_t)lv_event_get_user_data(e);
    codec_set_mic_source(mx_src);
    for (int i = 0; i < 5; i++) mx_set_active(mx_src_btn[i], i == mx_src);
}

static void mx_input_cb(lv_event_t *e)
{
    mx_input = (int)(intptr_t)lv_event_get_user_data(e);
    codec_set_mic_input(mx_input);
    for (int i = 0; i < 2; i++) mx_set_active(mx_input_btn[i], i == mx_input - 1);
}

static void mx_phase_cb(lv_event_t *e)
{
    codec_set_mic_invert(lv_obj_has_state((lv_obj_t *)lv_event_get_target(e), LV_STATE_CHECKED));
}

static void mx_dc_cb(lv_event_t *e)
{
    codec_set_mic_dcblock(lv_obj_has_state((lv_obj_t *)lv_event_get_target(e), LV_STATE_CHECKED));
}

static void mx_mute_cb(lv_event_t *e)
{
    codec_set_mic_mute(lv_obj_has_state((lv_obj_t *)lv_event_get_target(e), LV_STATE_CHECKED));
}

static void mx_beep_cb(lv_event_t *e)
{
    codec_set_beep(lv_obj_has_state((lv_obj_t *)lv_event_get_target(e), LV_STATE_CHECKED));
}

static void mx_back_cb(lv_event_t *e)
{
    (void)e;
    lv_screen_load(mix_return ? mix_return : settings_scr);
}

static void mx_open_cb(lv_event_t *e)
{
    (void)e;
    mix_return = lv_screen_active();
    lv_screen_load(mix_scr);
}

static void mx_timer_cb(lv_timer_t *t)
{
    (void)t;
    if (lv_screen_active() != mix_scr) return;
    int l, r;
    bool clip;
    codec_meter_get(&l, &r, &clip);
    int pk[2] = {l, r};
    for (int i = 0; i < 2; i++) {
        lv_bar_set_value(mx_meter[i], level_pct(pk[i]), LV_ANIM_OFF);
        int db = level_db(pk[i]);
        if (db <= -99) lv_label_set_text(mx_db[i], "-inf");
        else lv_label_set_text_fmt(mx_db[i], "%d", db);
    }
    lv_obj_set_style_bg_color(mx_clip, clip ? lv_color_hex(0xd33a2c) : lv_color_hex(0x444444), 0);
    if (!codec_tone_playing()) {
        lv_label_set_text(mx_mon_lbl, "MONITOR OFF");
        mx_set_active(mx_mon_btn, false);
    }
}

static lv_obj_t *mx_button(lv_obj_t *parent, const char *text, int x, int y, int w, int h, lv_event_cb_t cb, void *ud)
{
    lv_obj_t *b = lv_button_create(parent);
    lv_obj_set_size(b, w, h);
    lv_obj_set_pos(b, x, y);
    lv_obj_add_event_cb(b, cb, LV_EVENT_CLICKED, ud);
    lv_obj_t *l = lv_label_create(b);
    lv_label_set_text(l, text);
    lv_obj_center(l);
    return b;
}

// One labelled slider row: name on the left, slider, value on the right.
static lv_obj_t *mx_slider(lv_obj_t *parent, const char *name, int y, int lo, int hi, int init,
                           lv_event_cb_t cb, lv_obj_t **val)
{
    lv_obj_t *n = lv_label_create(parent);
    lv_label_set_text(n, name);
    lv_obj_set_pos(n, 200, y);
    lv_obj_t *sl = lv_slider_create(parent);
    lv_obj_set_size(sl, 400, 22);
    lv_obj_set_pos(sl, 210, y + 30);
    lv_slider_set_range(sl, lo, hi);
    lv_slider_set_value(sl, init, LV_ANIM_OFF);
    lv_obj_add_event_cb(sl, cb, LV_EVENT_VALUE_CHANGED, NULL);
    *val = lv_label_create(parent);
    lv_obj_set_pos(*val, 640, y + 28);
    return sl;
}

static lv_obj_t *mx_switch(lv_obj_t *parent, const char *name, int x, int y, bool on, lv_event_cb_t cb)
{
    lv_obj_t *n = lv_label_create(parent);
    lv_label_set_text(n, name);
    lv_obj_set_pos(n, x, y);
    lv_obj_t *sw = lv_switch_create(parent);
    lv_obj_set_pos(sw, x, y + 24);
    if (on) lv_obj_add_state(sw, LV_STATE_CHECKED);
    lv_obj_add_event_cb(sw, cb, LV_EVENT_VALUE_CHANGED, NULL);
    return sw;
}

static void mixer_create(void)
{
    mix_scr = lv_obj_create(NULL);
    lv_obj_remove_flag(mix_scr, LV_OBJ_FLAG_SCROLLABLE);

    mx_button(mix_scr, "< Back", 10, 8, 110, 44, mx_back_cb, NULL);
    lv_obj_t *t = lv_label_create(mix_scr);
    lv_label_set_text(t, "Audio Mixer");
    lv_obj_set_style_text_font(t, &lv_font_montserrat_20, 0);
    lv_obj_set_pos(t, 140, 18);
    mx_mon_btn = mx_button(mix_scr, "MONITOR OFF", 560, 8, 230, 44, mx_monitor_cb, NULL);
    mx_mon_lbl = lv_obj_get_child(mx_mon_btn, 0);
    mx_set_active(mx_mon_btn, false);

    // Meters (left side): L and R peak, dBFS under each, clip lamp on top
    mx_clip = lv_obj_create(mix_scr);
    lv_obj_set_size(mx_clip, 96, 14);
    lv_obj_set_pos(mx_clip, 30, 64);
    lv_obj_set_style_bg_color(mx_clip, lv_color_hex(0x444444), 0);
    lv_obj_set_style_border_width(mx_clip, 0, 0);
    lv_obj_t *cl = lv_label_create(mix_scr);
    lv_label_set_text(cl, "CLIP");
    lv_obj_set_pos(cl, 140, 62);
    for (int i = 0; i < 2; i++) {
        mx_meter[i] = lv_bar_create(mix_scr);
        lv_obj_set_size(mx_meter[i], 40, 260);
        lv_obj_set_pos(mx_meter[i], 30 + i * 56, 86);
        lv_bar_set_range(mx_meter[i], 0, 100);
        lv_obj_t *nm = lv_label_create(mix_scr);
        lv_label_set_text(nm, i ? "R" : "L");
        lv_obj_set_pos(nm, 44 + i * 56, 350);
        mx_db[i] = lv_label_create(mix_scr);
        lv_label_set_text(mx_db[i], "-inf");
        lv_obj_set_pos(mx_db[i], 28 + i * 56, 374);
    }

    // Sliders
    mx_slider(mix_scr, "Mic preamp gain", 64, 0, 8, 0, mx_gain_cb, &mx_val_gain);
    lv_label_set_text(mx_val_gain, "0 dB");
    mx_slider(mix_scr, "Sidetone level (headphones)", 128, -20, 40, 0, mx_side_cb, &mx_val_side);
    lv_label_set_text(mx_val_side, "+0 dB");
    mx_slider(mix_scr, "Output volume", 192, 0, 33, 21, mx_out_cb, &mx_val_out);
    lv_label_set_text(mx_val_out, "-13 dB");

    // Channel source
    lv_obj_t *sl = lv_label_create(mix_scr);
    lv_label_set_text(sl, "Mic channel");
    lv_obj_set_pos(sl, 200, 258);
    const char *names[5] = {"L+R", "L", "R", "L-R", "Auto"};
    for (int i = 0; i < 5; i++) {
        mx_src_btn[i] = mx_button(mix_scr, names[i], 200 + i * 98, 284, 90, 44, mx_src_cb, (void *)(intptr_t)i);
        mx_set_active(mx_src_btn[i], i == mx_src);
    }
    lv_obj_t *il = lv_label_create(mix_scr);
    lv_label_set_text(il, "Codec input");
    lv_obj_set_pos(il, 200, 340);
    mx_input_btn[0] = mx_button(mix_scr, "Input 1", 200, 364, 90, 44, mx_input_cb, (void *)(intptr_t)1);
    mx_input_btn[1] = mx_button(mix_scr, "Input 2", 298, 364, 90, 44, mx_input_cb, (void *)(intptr_t)2);
    mx_set_active(mx_input_btn[0], true);
    mx_set_active(mx_input_btn[1], false);

    // Switches
    mx_switch(mix_scr, "Phase invert", 420, 340, false, mx_phase_cb);
    mx_switch(mix_scr, "DC block", 540, 340, true, mx_dc_cb);
    mx_switch(mix_scr, "Mute", 640, 340, false, mx_mute_cb);
    mx_switch(mix_scr, "Test beep", 710, 258, false, mx_beep_cb);

    mx_status = lv_label_create(mix_scr);
    lv_label_set_text(mx_status, "Tap MONITOR ON, then talk");
    lv_obj_set_pos(mx_status, 200, 440);

    lv_timer_create(mx_timer_cb, 50, NULL);
}

// ======================= Settings menu =======================
static void go_home_cb(lv_event_t *e) { (void)e; lv_screen_load(ui_home_screen()); }
static void go_settings_cb(lv_event_t *e) { (void)e; lv_screen_load(settings_scr); }
static void go_diag_cb(lv_event_t *e) { (void)e; lv_screen_load(diag_scr); }

static lv_obj_t *settings_button(lv_obj_t *parent, const char *text, int y, lv_event_cb_t cb)
{
    lv_obj_t *b = lv_button_create(parent);
    lv_obj_set_size(b, 420, 64);
    lv_obj_align(b, LV_ALIGN_TOP_MID, 0, y);
    lv_obj_add_event_cb(b, cb, LV_EVENT_CLICKED, NULL);
    lv_obj_t *l = lv_label_create(b);
    lv_label_set_text(l, text);
    lv_obj_set_style_text_font(l, &lv_font_montserrat_20, 0);
    lv_obj_center(l);
    return b;
}

static void settings_create(void)
{
    settings_scr = lv_obj_create(NULL);
    lv_obj_remove_flag(settings_scr, LV_OBJ_FLAG_SCROLLABLE);
    lv_obj_t *back = add_button_at(settings_scr, LV_SYMBOL_LEFT " Home", 10, 8, 130, 44, go_home_cb);
    (void)back;
    lv_obj_t *t = lv_label_create(settings_scr);
    lv_label_set_text(t, LV_SYMBOL_SETTINGS "  Settings");
    lv_obj_set_style_text_font(t, &lv_font_montserrat_20, 0);
    lv_obj_align(t, LV_ALIGN_TOP_MID, 0, 18);

    settings_button(settings_scr, "Audio Mixer", 90, mx_open_cb);
    settings_button(settings_scr, "Diagnostics", 170, go_diag_cb);
    lv_obj_t *ub = settings_button(settings_scr, "Firmware update", 250, update_cb);
    set_update_lbl = lv_obj_get_child(ub, 0);

    set_status = lv_label_create(settings_scr);
    lv_label_set_text(set_status, "");
    lv_obj_align(set_status, LV_ALIGN_BOTTOM_LEFT, 16, -12);
}

void diag_ui_create(void)
{
    lv_obj_t *scr = lv_obj_create(NULL);
    diag_scr = scr;
    mixer_create();
    settings_create();
    add_button_at(scr, LV_SYMBOL_LEFT " Settings", 10, 6, 150, 40, go_settings_cb);
    {
        lv_obj_t *mb = lv_button_create(scr);
        lv_obj_set_size(mb, 170, 40);
        lv_obj_align(mb, LV_ALIGN_TOP_RIGHT, -16, 6);
        lv_obj_add_event_cb(mb, mx_open_cb, LV_EVENT_CLICKED, NULL);
        lv_obj_t *ml2 = lv_label_create(mb);
        lv_label_set_text(ml2, "Audio Mixer >");
        lv_obj_center(ml2);
    }

    lv_obj_t *title = lv_label_create(scr);
    lv_label_set_text(title, "Audio Companion - Diagnostics");
    lv_obj_set_style_text_font(title, &lv_font_montserrat_20, 0);
    lv_obj_align(title, LV_ALIGN_TOP_LEFT, 180, 12);

    // Column 1: I2C devices
    lv_obj_t *p1 = make_panel(scr, "I2C devices", 10, 290);
    lv_obj_remove_flag(p1, LV_OBJ_FLAG_SCROLLABLE);
    for (int i = 0; i < diag_dev_count(); i++) {
        const diag_dev_t *d = diag_dev(i);
        lv_obj_t *name = lv_label_create(p1);
        lv_label_set_text_fmt(name, "%s (0x%02X)", d->name, d->addr);
        lv_obj_align(name, LV_ALIGN_TOP_LEFT, 0, 28 + i * 26);
        dev_status[i] = lv_label_create(p1);
        lv_obj_align(dev_status[i], LV_ALIGN_TOP_LEFT, 200, 28 + i * 26);
    }
    refresh_devices();

    lv_obj_t *ml = lv_label_create(p1);
    lv_label_set_text(ml, "Mic level");
    lv_obj_align(ml, LV_ALIGN_TOP_LEFT, 0, 188);
    mic_bar = lv_bar_create(p1);
    lv_obj_set_size(mic_bar, 250, 16);
    lv_bar_set_range(mic_bar, 0, 100);
    lv_bar_set_value(mic_bar, 0, LV_ANIM_OFF);
    lv_obj_align(mic_bar, LV_ALIGN_TOP_LEFT, 0, 208);
    gain_label = lv_label_create(p1);
    lv_label_set_text(gain_label, "Mic gain 0 dB");
    lv_obj_align(gain_label, LV_ALIGN_TOP_LEFT, 0, 234);
    lv_obj_t *gs = lv_slider_create(p1);
    lv_obj_set_size(gs, 115, 12);
    lv_slider_set_range(gs, 0, 8);
    lv_slider_set_value(gs, 0, LV_ANIM_OFF);
    lv_obj_align(gs, LV_ALIGN_TOP_LEFT, 8, 262);
    lv_obj_add_event_cb(gs, gain_cb, LV_EVENT_VALUE_CHANGED, NULL);

    vol_label = lv_label_create(p1);
    lv_label_set_text(vol_label, "Out vol -15 dB");
    lv_obj_align(vol_label, LV_ALIGN_TOP_LEFT, 140, 234);
    lv_obj_t *vs = lv_slider_create(p1);
    lv_obj_set_size(vs, 115, 12);
    lv_slider_set_range(vs, 0, 33);
    lv_slider_set_value(vs, 20, LV_ANIM_OFF);
    lv_obj_align(vs, LV_ALIGN_TOP_LEFT, 148, 262);
    lv_obj_add_event_cb(vs, volume_cb, LV_EVENT_VALUE_CHANGED, NULL);

    lv_obj_t *tb = add_button_at(p1, "Play tone", 0, 284, 130, 50, tone_cb);
    tone_btn_label = lv_obj_get_child(tb, 0);
    add_button_at(p1, "Self-test", 140, 284, 130, 50, selftest_cb);

    // Column 2: controls
    lv_obj_t *p2 = make_panel(scr, "Controls", 310, 240);
    lv_obj_t *l1 = lv_label_create(p2);
    lv_label_set_text(l1, "ANR power (IO8)");
    lv_obj_align(l1, LV_ALIGN_TOP_LEFT, 0, 40);
    lv_obj_t *sw1 = lv_switch_create(p2);
    lv_obj_align(sw1, LV_ALIGN_TOP_LEFT, 140, 32);
    lv_obj_add_event_cb(sw1, anr_cb, LV_EVENT_VALUE_CHANGED, NULL);

    lv_obj_t *l2 = lv_label_create(p2);
    lv_label_set_text(l2, "Bypass (IO20)");
    lv_obj_align(l2, LV_ALIGN_TOP_LEFT, 0, 100);
    lv_obj_t *sw2 = lv_switch_create(p2);
    lv_obj_align(sw2, LV_ALIGN_TOP_LEFT, 140, 92);
    lv_obj_add_event_cb(sw2, bypass_cb, LV_EVENT_VALUE_CHANGED, NULL);

    lv_obj_t *lb = add_button(p2, "Loopback test", 150, loopback_cb);
    loop_btn_label = lv_obj_get_child(lb, 0);
    lv_obj_t *mb = add_button(p2, "Mic monitor", 220, monitor_cb);
    mon_btn_label = lv_obj_get_child(mb, 0);
    lv_obj_t *ub = add_button(p2, "Firmware update", 290, update_cb);
    update_btn_label = lv_obj_get_child(ub, 0);

    // Column 3: expander inputs
    lv_obj_t *p3 = make_panel(scr, "Expander inputs (lit = high)", 560, 230);
    exp_state = lv_label_create(p3);
    lv_label_set_text(exp_state, "");
    lv_obj_align(exp_state, LV_ALIGN_TOP_LEFT, 0, 20);
    for (int i = 0; i < 8; i++) {
        exp_led[i] = lv_led_create(p3);
        lv_obj_set_size(exp_led[i], 20, 20);
        lv_led_set_color(exp_led[i], lv_color_hex(0x1e9e50));
        lv_led_off(exp_led[i]);
        lv_obj_align(exp_led[i], LV_ALIGN_TOP_LEFT, 0, 44 + i * 36);
        lv_obj_t *n = lv_label_create(p3);
        lv_label_set_text(n, exp_names[i]);
        lv_obj_align(n, LV_ALIGN_TOP_LEFT, 32, 44 + i * 36);
    }
    lv_timer_create(expander_timer_cb, 100, NULL);

    status_line = lv_label_create(scr);
    lv_label_set_text(status_line, "Ready");
    lv_obj_align(status_line, LV_ALIGN_BOTTOM_LEFT, 16, -12);

    enc_line = lv_label_create(scr);
    lv_label_set_text(enc_line, "");
    lv_obj_align(enc_line, LV_ALIGN_BOTTOM_RIGHT, -16, -12);

    ui_home_create(settings_scr);
    lv_screen_load(ui_home_screen());
}
