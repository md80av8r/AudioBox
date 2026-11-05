// ES8388 codec: playback test tone on the headphone path.
#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "driver/i2c_master.h"

void codec_init(i2c_master_bus_handle_t bus);
const char *codec_tone_start(void);   // NULL on success, otherwise a short reason it failed
void codec_tone_stop(void);
bool codec_tone_playing(void);
bool codec_read_reg(uint8_t reg, uint8_t *val);   // for diagnostics
