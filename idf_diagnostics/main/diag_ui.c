// Diagnostics screen: I2C device status, control lines, expander inputs, haptic.
#include <stdio.h>
#include "lvgl.h"
#include "diag_hw.h"
#include "diag_ui.h"

#define COL_OK  lv_color_hex(0x1e9e50)
#define COL_BAD lv_color_hex(0xd33a2c)

static lv_obj_t *dev_status[8];
static lv_obj_t *exp_led[8];
static lv_obj_t *exp_state;
static lv_obj_t *status_line;
static lv_obj_t *enc_line;

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

    int32_t outer, inner;
    bool pushed;
    diag_enc_get(&outer, &inner, &pushed);
    lv_label_set_text_fmt(enc_line, "Encoder  outer: %d   inner: %d   push: %s",
                          (int)outer, (int)inner, pushed ? "DOWN" : "up");
}

static lv_obj_t *add_button(lv_obj_t *parent, const char *text, int y, lv_event_cb_t cb)
{
    lv_obj_t *b = lv_button_create(parent);
    lv_obj_set_size(b, 200, 60);
    lv_obj_align(b, LV_ALIGN_TOP_LEFT, 0, y);
    lv_obj_add_event_cb(b, cb, LV_EVENT_CLICKED, NULL);
    lv_obj_t *l = lv_label_create(b);
    lv_label_set_text(l, text);
    lv_obj_center(l);
    return b;
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
    for (int i = 0; i < diag_dev_count(); i++) {
        const diag_dev_t *d = diag_dev(i);
        lv_obj_t *name = lv_label_create(p1);
        lv_label_set_text_fmt(name, "%s (0x%02X)", d->name, d->addr);
        lv_obj_align(name, LV_ALIGN_TOP_LEFT, 0, 34 + i * 40);
        dev_status[i] = lv_label_create(p1);
        lv_obj_align(dev_status[i], LV_ALIGN_TOP_LEFT, 0, 52 + i * 40);
    }
    refresh_devices();

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

    add_button(p2, "Haptic buzz", 170, haptic_cb);
    add_button(p2, "Rescan I2C", 250, rescan_cb);

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
