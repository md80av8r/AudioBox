// sensor_task.cpp — poll BME280 every 1s, update g_state
#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_BME280.h>
#include "pins.h"
#include "state.h"

static Adafruit_BME280 bme;
static bool bme_ok = false;

void sensor_task(void*) {
  // BME280 at 0x76 (project memory) — falls back to 0x77 just in case
  if (bme.begin(0x76, &Wire) || bme.begin(0x77, &Wire)) {
    bme_ok = true;
    Serial.println("[sensor] BME280 OK");
  } else {
    Serial.println("[sensor] BME280 NOT FOUND");
  }

  for (;;) {
    if (bme_ok) {
      g_state.temp_c   = bme.readTemperature();
      g_state.humidity = bme.readHumidity();
    }
    // Battery: ADC on PIN_BATT_SENSE through divider (R8/R9 100k/100k = ÷2)
    int raw = analogRead(PIN_BATT_SENSE);
    g_state.batt_v = (raw / 4095.0f) * 3.3f * 2.0f;  // ÷2 divider → ×2
    vTaskDelay(pdMS_TO_TICKS(1000));
  }
}
