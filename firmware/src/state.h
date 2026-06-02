// state.h — global app state + mode machine
#pragma once
#include <Arduino.h>

enum class Mode : uint8_t {
  Boot,      // splash + init
  Idle,      // clock screen, audio passthrough
  Comms,     // ESP-NOW crew comms active
  Music,     // BT music streaming
  ATC,       // ATC playback from PSRAM/SD
  Settings   // menu via encoder
};

struct AppState {
  Mode      mode      = Mode::Boot;
  uint8_t   volume    = 50;          // 0..100
  float     batt_v    = 0.0f;        // LiPo volts
  float     temp_c    = 0.0f;        // BME280
  float     humidity  = 0.0f;        // BME280
  uint32_t  uptime_ms = 0;
  bool      ptt_held  = false;
  bool      headset_in = false;      // J3_DETECT
};

extern AppState g_state;
