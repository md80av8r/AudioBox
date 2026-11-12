// Diagnostics screen: I2C device status, control lines, expander inputs, haptic.
#include <stdio.h>
#include "lvgl.h"
#include "diag_hw.h"
#include "diag_ui.h"
#include "ota.h"
#include "codec.h"
#include "selftest.h"
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
        } else {
            lv_label_set_text(status_line, "Update mode failed to start");
        }
    } else {
        ota_stop();
        lv_label_set_text(update_btn_label, "Firmware update");
        lv_label_set_text(status_line, "Update mode off");
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

void diag_ui_create(void)
{
    lv_obj_t *scr = lv_screen_active();

    lv_obj_t *title = lv_label_create(scr);
    lv_label_set_text(title, "Audio Companion - Diagnostics");
    lv_obj_set_style_text_font(title, &lv_font_montserrat_20, 0);
    lv_obj_align(title, LV_ALIGN_TOP_LEFT, 16, 12);

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
}
