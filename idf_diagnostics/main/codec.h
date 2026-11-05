// ES8388 codec: playback test tone on the headphone path.
#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "driver/i2c_master.h"

void codec_init(i2c_master_bus_handle_t bus);
const char *codec_tone_start(void);   // NULL on success, otherwise a short reason it failed
const char *codec_monitor_start(void);   // mic -> headphones through the codec's analog mixer (no I2S audio)
const char *codec_loopback_start(void);   // tone out of LINE OUT, listen on LINE IN (needs a jumper wire patch)
void codec_tone_stop(void);   // stops the tone or the monitor
bool codec_tone_playing(void);
bool codec_read_reg(uint8_t reg, uint8_t *val);   // for diagnostics
bool codec_write_reg(uint8_t reg, uint8_t val);   // for diagnostics

// Mic input (active while the mic monitor runs)
int codec_mic_level(void);            // 0..100, roughly -60 dB..0 dBFS, with a slow fall-off
void codec_set_mic_gain(int step);    // 0..8 = 0..24 dB in 3 dB steps
