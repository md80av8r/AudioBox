// ui_task.cpp — LVGL init, display driver, screen manager
#include <Arduino.h>
#include <lvgl.h>
#include <TFT_eSPI.h>
#include "ui.h"
#include "theme.h"
#include "pins.h"
#include "state.h"

// Forward decls of per-screen updaters
extern void ui_home_update();
extern void ui_audio_update();

// ───────────────────────────────────────────────────────────
// TFT_eSPI + LVGL plumbing
// ───────────────────────────────────────────────────────────
static TFT_eSPI tft;
static const uint16_t SCREEN_W = 320, SCREEN_H = 240;

// Two small DMA-able draw buffers
static lv_color_t buf1[SCREEN_W * 20];
static lv_color_t buf2[SCREEN_W * 20];
static lv_disp_draw_buf_t draw_buf;
static lv_disp_drv_t disp_drv;

static void disp_flush(lv_disp_drv_t* drv, const lv_area_t* a, lv_color_t* px) {
  uint32_t w = a->x2 - a->x1 + 1, h = a->y2 - a->y1 + 1;
  tft.startWrite();
  tft.setAddrWindow(a->x1, a->y1, w, h);
  tft.pushColors((uint16_t*)px, w * h, true);
  tft.endWrite();
  lv_disp_flush_ready(drv);
}

// ───────────────────────────────────────────────────────────
// Screen manager
// ───────────────────────────────────────────────────────────
static lv_obj_t* cur_screen = nullptr;

void ui_goto(lv_obj_t* screen) {
  cur_screen = screen;
  lv_scr_load_anim(screen, LV_SCR_LOAD_ANIM_FADE_ON, 200, 0, false);
}

// ───────────────────────────────────────────────────────────
// Per-tick: pull state into widgets (call ~10Hz)
// ───────────────────────────────────────────────────────────
void ui_tick() {
  // Each updater is safe to call any time — only writes if its screen is built
  ui_home_update();
  ui_audio_update();
}

// ───────────────────────────────────────────────────────────
// Task entry
// ───────────────────────────────────────────────────────────
void ui_task(void*) {
  Serial.println("[ui] init TFT_eSPI");
  tft.begin();
  tft.setRotation(1);   // landscape
  tft.fillScreen(TFT_BLACK);

  Serial.println("[ui] init LVGL");
  lv_init();
  lv_disp_draw_buf_init(&draw_buf, buf1, buf2, SCREEN_W * 20);
  lv_disp_drv_init(&disp_drv);
  disp_drv.hor_res = SCREEN_W;
  disp_drv.ver_res = SCREEN_H;
  disp_drv.flush_cb = disp_flush;
  disp_drv.draw_buf = &draw_buf;
  lv_disp_drv_register(&disp_drv);

  // Decide boot screen based on headset detect
  lv_obj_t* home = ui_home_create();
  ui_goto(home);

  if (g_state.headset_in) {
    Serial.println("[ui] headset detected at boot → Audio Mixer");
    ui_goto(ui_audio_create());
  } else {
    Serial.println("[ui] no headset → Home screen");
  }

  uint32_t last_tick = 0;
  for (;;) {
    lv_timer_handler();
    uint32_t now = millis();
    if (now - last_tick >= 100) {
      ui_tick();
      last_tick = now;
    }
    vTaskDelay(pdMS_TO_TICKS(5));
  }
}
