// ES8388 codec: playback test tone on the headphone path.
#pragma once
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
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
void codec_set_out_volume(int reg);   // 0..33: ES8388 output volume register (30 = 0 dB, 1.5 dB per step)
bool codec_wait_stopped(int ms);   // true once the tone/monitor/loopback task has fully stopped
void codec_stats_reset(void);
void codec_stats_get(int *peak_l, int *peak_r, int *rms_l, int *rms_r);   // amplitudes 0..32767
void codec_set_mic_input(int input);   // 1 or 2: which codec input pair the mic monitor uses

// Mic diagnostics (the monitor must be running)
void codec_mic_config(int src, int inv, int sw_gain, int dcblock, int mute, int beep);   // -1 = leave unchanged; src 0=L+R 1=L 2=R 3=L-R
void codec_mic_status(char *out, size_t n);   // DC mean / rms / peak per channel, registers, error counters
void codec_stats_reset_all(void);
bool codec_snapshot(const int16_t **l, const int16_t **r);   // 256 raw ADC frames

// Mixer controls
void codec_set_sidetone_db(int db);     // -40..+30 dB digital gain on the monitor path
void codec_set_mic_source(int src);     // 0=L+R 1=L 2=R 3=L-R 4=auto (louder channel)
void codec_set_mic_invert(bool inv);
void codec_set_mic_mute(bool mute);
void codec_set_mic_dcblock(bool on);
void codec_set_beep(bool on);
void codec_meter_get(int *l, int *r, bool *clip);   // decaying peaks 0..32768 per channel

// Crew intercom (needs the mic monitor running): sends the mic to the peer box and plays the peer's voice.
void codec_set_intercom(bool on);
bool codec_intercom_on(void);
void codec_set_remote_volume_db(int db);   // -40..+12 dB on the peer's voice
void codec_set_mic_level_db(int db);   // -30..+24 dB: digital attenuation below 0, analog gain above
