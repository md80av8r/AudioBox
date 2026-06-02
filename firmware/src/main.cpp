// main.cpp — MD-88 Crew Audio Breakout rev C
// Boots, spawns FreeRTOS tasks, never returns from loop().

#include <Arduino.h>
#include <Wire.h>
#include "pins.h"
#include "state.h"

AppState g_state;

// Forward declarations from task files
void ui_task(void*);
void sensor_task(void*);
void state_task(void*);

void setup() {
  Serial.begin(115200);
  delay(200);
  Serial.println("\n=== MD-88 Audio Breakout rev C booting ===");

  // Soft-latch power hold ON — keeps us alive after power button release
  pinMode(PIN_PWR_HOLD, OUTPUT);
  digitalWrite(PIN_PWR_HOLD, HIGH);

  // I2C for touch panel + BME280 + DS3231 (shared bus)
  Wire.begin(PIN_TOUCH_SDA, PIN_TOUCH_SCL);
  Wire.setClock(400000);

  // Button + sense pins
  pinMode(PIN_PWR_BTN,   INPUT_PULLUP);
  pinMode(PIN_PTT_BTN,   INPUT_PULLUP);
  pinMode(PIN_ATC_BTN,   INPUT_PULLUP);
  pinMode(PIN_J3_DETECT, INPUT_PULLUP);

  // Read headset state BEFORE spawning ui_task — UI's boot screen depends on it
  delay(50);
  g_state.headset_in = digitalRead(PIN_J3_DETECT) == LOW;
  Serial.printf("[boot] headset_in=%d\n", g_state.headset_in);

  // Spawn tasks — pinned to cores per the architecture plan
  xTaskCreatePinnedToCore(ui_task,     "ui",     8192, nullptr, 2, nullptr, 0);
  xTaskCreatePinnedToCore(sensor_task, "sensor", 4096, nullptr, 1, nullptr, 0);
  xTaskCreatePinnedToCore(state_task,  "state",  4096, nullptr, 1, nullptr, 0);

  g_state.mode = Mode::Idle;
  Serial.println("setup() done — tasks running");
}

void loop() {
  // Nothing to do here — work happens in tasks.
  // 1s heartbeat for debug.
  static uint32_t last = 0;
  uint32_t now = millis();
  if (now - last >= 1000) {
    last = now;
    g_state.uptime_ms = now;
    Serial.printf("[%lus] mode=%u vol=%u temp=%.1fC batt=%.2fV\n",
                  now/1000, (uint8_t)g_state.mode, g_state.volume,
                  g_state.temp_c, g_state.batt_v);
  }
  delay(50);
}
