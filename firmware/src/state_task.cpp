// state_task.cpp — buttons, encoder, mode transitions
#include <Arduino.h>
#include <ESP32Encoder.h>
#include <Bounce2.h>
#include "pins.h"
#include "state.h"

static ESP32Encoder encoder;
static Bounce  pwr_btn, ptt_btn, atc_btn, enc_sw;
static int64_t last_enc = 0;

void state_task(void*) {
  encoder.attachHalfQuad(PIN_ENC_A, PIN_ENC_B);
  encoder.clearCount();

  pwr_btn.attach(PIN_PWR_BTN, INPUT_PULLUP); pwr_btn.interval(25);
  ptt_btn.attach(PIN_PTT_BTN, INPUT_PULLUP); ptt_btn.interval(15);
  atc_btn.attach(PIN_ATC_BTN, INPUT_PULLUP); atc_btn.interval(25);
  enc_sw.attach (PIN_ENC_SW,  INPUT_PULLUP); enc_sw.interval(25);

  Serial.println("[state] inputs initialized");

  for (;;) {
    pwr_btn.update(); ptt_btn.update(); atc_btn.update(); enc_sw.update();

    // Encoder → volume (clamped 0..100)
    int64_t now_enc = encoder.getCount();
    int64_t delta   = now_enc - last_enc;
    if (delta) {
      int v = (int)g_state.volume + (int)delta;
      g_state.volume = constrain(v, 0, 100);
      last_enc = now_enc;
      Serial.printf("[enc] vol=%u\n", g_state.volume);
    }

    // PTT
    g_state.ptt_held = (ptt_btn.read() == LOW);

    // ATC button — toggle ATC mode
    if (atc_btn.fell()) {
      g_state.mode = (g_state.mode == Mode::ATC) ? Mode::Idle : Mode::ATC;
      Serial.printf("[btn] ATC → mode=%u\n", (uint8_t)g_state.mode);
    }

    // Encoder switch — enter Settings mode
    if (enc_sw.fell()) {
      g_state.mode = (g_state.mode == Mode::Settings) ? Mode::Idle : Mode::Settings;
      Serial.printf("[btn] ENC_SW → mode=%u\n", (uint8_t)g_state.mode);
    }

    // Power button long-press → release latch (shutdown)
    if (pwr_btn.read() == LOW && pwr_btn.currentDuration() > 2000) {
      Serial.println("[pwr] long-press → shutdown");
      digitalWrite(PIN_PWR_HOLD, LOW);   // releases AO3401A → box powers off
      vTaskDelay(pdMS_TO_TICKS(500));
    }

    // Headset detect
    g_state.headset_in = digitalRead(PIN_J3_DETECT) == LOW;

    vTaskDelay(pdMS_TO_TICKS(10));
  }
}
