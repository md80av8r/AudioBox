#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "esp_err.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/i2s_std.h"
#include "codec.h"
#include "pins_companion.h"

#define CODEC_ADDR   0x10
#define SAMPLE_RATE  48000
#define TONE_HZ      1000
#define TONE_AMP     3000      // out of 32767: quiet, protects ears and the headset
#define OUT_VOLUME   0x14      // ES8388 output volume (0x1E = 0 dB, 1.5 dB per step)

static i2c_master_dev_handle_t codec_dev;
static i2s_chan_handle_t tx;
static i2s_chan_handle_t rx;
static volatile int mic_level;
static volatile int hold_l, hold_r;
static uint64_t sum_l, sum_r;
static uint32_t sum_n;
static uint8_t mic_sel_reg = 0x00;   // ADC input select: 0x00 = input 1, 0x50 = input 2
static uint8_t mic_gain_reg = 0x00;   // 0 dB (the board's preamp already adds gain)
static uint8_t out_vol_reg = OUT_VOLUME;
static volatile bool monitor_mode;
// Mic diagnostics / processing (software, applied in the sidetone path)
static volatile int mic_src = 0;        // 0 = L+R, 1 = L only, 2 = R only, 3 = L-R (differential)
static volatile bool mic_inv = false;   // invert polarity of the sidetone
static volatile int mic_sw_gain = 1;    // extra digital gain, 1..16x
static volatile bool mic_mute = false;
static volatile bool mic_beep = false;   // mix a 1 kHz beep into the sidetone (proves the output path)
static volatile bool mic_dcblock = true;
static int64_t dc_sum_l, dc_sum_r;      // for the mean (DC offset) readout
static volatile uint32_t rd_err, wr_err, rd_short, frames_total;
static int16_t snap[2][256];
static volatile int snap_req;           // set to 256 to capture; counts down to 0 as it fills
static int snap_pos;
static volatile bool loopback_mode;
static volatile bool playing;
static volatile bool task_alive;

static uint8_t fail_reg;
static esp_err_t fail_err;
static char fail_msg[56];

// Write one codec register, retrying a few times; remembers the first one that fails.
static esp_err_t cw(uint8_t reg, uint8_t val)
{
    uint8_t b[2] = {reg, val};
    esp_err_t e = ESP_FAIL;
    for (int i = 0; i < 3; i++) {
        e = i2c_master_transmit(codec_dev, b, 2, 100);
        if (e == ESP_OK) return ESP_OK;
        vTaskDelay(pdMS_TO_TICKS(5));
    }
    if (fail_err == ESP_OK) {
        fail_reg = reg;
        fail_err = e;
    }
    return e;
}

void codec_init(i2c_master_bus_handle_t bus)
{
    i2c_device_config_t cfg = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = CODEC_ADDR,
        .scl_speed_hz = 400000,
    };
    ESP_ERROR_CHECK(i2c_master_bus_add_device(bus, &cfg, &codec_dev));
    // The ES8388 powers up as clock master and drives BCLK/LRCK. Make it a slave right away
    // so it stops fighting the ESP32 on those pins.
    cw(0x08, 0x00);
}

// Playback setup: slave mode, 16-bit I2S, single speed with MCLK = 256 x fs.
static bool codec_configure(void)
{
    fail_err = ESP_OK;
    esp_err_t e = ESP_OK;
    e |= cw(0x19, 0x04);   // DAC mute while configuring
    e |= cw(0x01, 0x50);   // control 2
    e |= cw(0x02, 0x00);   // chip power up
    e |= cw(0x08, 0x00);   // slave mode (the ESP32 supplies the clocks)
    e |= cw(0x04, 0xC0);   // DAC and outputs off for now
    e |= cw(0x00, 0x12);   // control 1: play and record mode
    e |= cw(0x17, 0x18);   // DAC: I2S format, 16-bit
    e |= cw(0x18, 0x02);   // DAC: single speed, MCLK/fs = 256
    e |= cw(0x26, 0x00);   // mixer input select
    e |= cw(0x27, 0x90);   // left DAC to left mixer
    e |= cw(0x2A, 0x90);   // right DAC to right mixer
    e |= cw(0x2B, 0x80);   // ADC and DAC share LRCK
    e |= cw(0x2D, 0x00);
    e |= cw(0x10, 0x00);   // ADC digital volume left, 0 dB (power-on default is -96 dB)
    e |= cw(0x11, 0x00);   // ADC digital volume right, 0 dB
    e |= cw(0x1A, 0x00);   // DAC digital volume left, 0 dB
    e |= cw(0x1B, 0x00);   // DAC digital volume right, 0 dB
    e |= cw(0x2E, out_vol_reg);   // LOUT1
    e |= cw(0x2F, out_vol_reg);   // ROUT1
    e |= cw(0x30, out_vol_reg);   // LOUT2
    e |= cw(0x31, out_vol_reg);   // ROUT2
    if (loopback_mode) {
        e |= cw(0x03, 0x00);   // ADC powered
        e |= cw(0x09, 0x00);   // line level: PGA 0 dB
        e |= cw(0x0A, 0x00);   // inputs: LIN1 / RIN1 (the LINE IN connector)
        e |= cw(0x0C, 0x0C);   // ADC: I2S format, 16-bit
        e |= cw(0x0D, 0x02);   // ADC: single speed, MCLK/fs = 256
        e |= cw(0x2E, 0x1E);   // outputs at 0 dB so the loopback level is easy to see
        e |= cw(0x2F, 0x1E);
        e |= cw(0x30, 0x1E);
        e |= cw(0x31, 0x1E);
    }
    if (monitor_mode) {
        e |= cw(0x03, 0x00);   // ADC input stage powered
        e |= cw(0x09, mic_gain_reg);   // mic PGA gain
        e |= cw(0x0C, 0x0C);   // ADC: I2S format, 16-bit
        e |= cw(0x0D, 0x02);   // ADC: single speed, MCLK/fs = 256
        e |= cw(0x0A, mic_sel_reg);   // which input pair the ADC listens to
        // Sidetone is digital: the ESP32 copies the ADC samples to the DAC, both ears.
    }
    e |= cw(0x04, 0x3C);   // DACs and all four outputs on
    e |= cw(0x19, 0x00);   // unmute
    return e == ESP_OK;
}

static void tone_task(void *arg)
{
    (void)arg;
    enum { N = SAMPLE_RATE / TONE_HZ };   // 48 samples per cycle
    static int16_t cycle[N * 2];
    for (int i = 0; i < N; i++) {
        int16_t s = monitor_mode ? 0 : (int16_t)(TONE_AMP * sinf(2.0f * (float)M_PI * i / N));
        cycle[2 * i] = s;
        cycle[2 * i + 1] = s;
    }
    static int16_t buf[N * 2 * 8];
    for (int k = 0; k < 8; k++) {
        for (int i = 0; i < N * 2; i++) buf[k * N * 2 + i] = cycle[i];
    }
    enum { BLK = 64 };                       // frames per pass: ~1.3 ms
    static int16_t rbuf[BLK * 2];
    int32_t dcl = 0, dcr = 0;                // one-pole DC trackers (Q8)
    int errs_in_row = 0;
    uint32_t beep_i = 0;
    while (playing) {
        size_t written = 0, got = 0;
        if (monitor_mode || loopback_mode) {
            esp_err_t re = rx ? i2s_channel_read(rx, rbuf, sizeof(rbuf), &got, 100) : ESP_FAIL;
            if (re != ESP_OK || got < 4) {
                rd_err++;
                got = 0;
                if (++errs_in_row > 20) {      // codec clock probably lost: stop instead of spinning
                    playing = false;
                    break;
                }
                if (monitor_mode) {            // keep the TX fed with silence
                    memset(rbuf, 0, sizeof(rbuf));
                    i2s_channel_write(tx, rbuf, sizeof(rbuf), &written, 50);
                }
                continue;
            }
            errs_in_row = 0;
            if (got < sizeof(rbuf)) rd_short++;
            int peak = 0;
            size_t frames = got / 4;
            frames_total += frames;
            for (size_t i = 0; i < frames; i++) {
                int l = rbuf[2 * i], r = rbuf[2 * i + 1];
                dc_sum_l += l;
                dc_sum_r += r;
                sum_l += (uint64_t)((int64_t)l * l);
                sum_r += (uint64_t)((int64_t)r * r);
                int al = l < 0 ? -l : l, ar = r < 0 ? -r : r;
                if (al > hold_l) hold_l = al;
                if (ar > hold_r) hold_r = ar;
                if (al > peak) peak = al;
                if (ar > peak) peak = ar;
                if (snap_req > 0) {
                    snap[0][snap_pos] = (int16_t)l;
                    snap[1][snap_pos] = (int16_t)r;
                    snap_pos++;
                    if (--snap_req == 0) snap_pos = 0;
                }
                if (monitor_mode) {
                    if (mic_dcblock) {         // remove the bias DC so it cannot thump or eat headroom
                        dcl += ((l << 8) - dcl) >> 9;
                        dcr += ((r << 8) - dcr) >> 9;
                        l -= dcl >> 8;
                        r -= dcr >> 8;
                    }
                    int v;
                    switch (mic_src) {
                    case 1:  v = l; break;
                    case 2:  v = r; break;
                    case 3:  v = l - r; break;
                    default: v = l + r; break;
                    }
                    v *= mic_sw_gain;
                    if (mic_inv) v = -v;
                    if (mic_mute) v = 0;
                    if (mic_beep) v += (int)(TONE_AMP * sinf(2.0f * (float)M_PI * (beep_i++ % N) / N));
                    if (v > 32767) v = 32767;
                    if (v < -32768) v = -32768;
                    rbuf[2 * i] = (int16_t)v;
                    rbuf[2 * i + 1] = (int16_t)v;
                }
            }
            sum_n += (uint32_t)frames;
            int lvl = 0;
            if (peak > 0) {
                float db = 20.0f * log10f((float)peak / 32768.0f);
                lvl = (int)((db + 60.0f) / 60.0f * 100.0f);
                if (lvl < 0) lvl = 0;
                if (lvl > 100) lvl = 100;
            }
            int fall = mic_level - 1;
            mic_level = lvl > fall ? lvl : fall;
        }
        esp_err_t we;
        if (monitor_mode && got) {
            we = i2s_channel_write(tx, rbuf, got, &written, 200);
        } else {
            we = i2s_channel_write(tx, buf, sizeof(buf), &written, 200);
        }
        if (we != ESP_OK) wr_err++;
    }
    mic_level = 0;
    cw(0x19, 0x04);          // mute
    cw(0x04, 0xC0);          // outputs off
    if (rx) {
        i2s_channel_disable(rx);
        i2s_del_channel(rx);
        rx = NULL;
    }
    i2s_channel_disable(tx);
    i2s_del_channel(tx);
    tx = NULL;
    task_alive = false;
    vTaskDelete(NULL);
}

static const char *start_common(void)
{
    if (playing) return NULL;
    for (int i = 0; i < 50 && task_alive; i++) vTaskDelay(pdMS_TO_TICKS(20));   // previous run shutting down
    if (task_alive) return "previous tone still running";

    cw(0x08, 0x00);   // slave mode before the ESP32 starts driving the clocks
    i2s_chan_config_t cc = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
    cc.auto_clear = true;
    cc.dma_desc_num = 4;      // small buffers: 4 x 64 frames = ~5 ms, keeps the sidetone delay short
    cc.dma_frame_num = 64;
    if (i2s_new_channel(&cc, &tx, (monitor_mode || loopback_mode) ? &rx : NULL) != ESP_OK) return "I2S channel create";

    i2s_std_config_t std = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(SAMPLE_RATE),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_STEREO),
        .gpio_cfg = {
            .mclk = PIN_I2S_MCLK,
            .bclk = PIN_I2S_BCLK,
            .ws   = PIN_I2S_LRCK,
            .dout = PIN_I2S_DOUT,
            .din  = (monitor_mode || loopback_mode) ? PIN_I2S_DIN : I2S_GPIO_UNUSED,
        },
    };
    if (i2s_channel_init_std_mode(tx, &std) != ESP_OK ||
        (rx && i2s_channel_init_std_mode(rx, &std) != ESP_OK)) {
        if (rx) { i2s_del_channel(rx); rx = NULL; }
        i2s_del_channel(tx);
        tx = NULL;
        return "I2S init (pins/clock)";
    }
    if (i2s_channel_enable(tx) != ESP_OK || (rx && i2s_channel_enable(rx) != ESP_OK)) {
        if (rx) { i2s_del_channel(rx); rx = NULL; }
        i2s_del_channel(tx);
        tx = NULL;
        return "I2S enable";
    }

    vTaskDelay(pdMS_TO_TICKS(20));   // let MCLK settle before talking to the codec
    if (!codec_configure()) {
        if (rx) { i2s_channel_disable(rx); i2s_del_channel(rx); rx = NULL; }
        i2s_channel_disable(tx);
        i2s_del_channel(tx);
        tx = NULL;
        snprintf(fail_msg, sizeof(fail_msg), "codec I2C reg 0x%02X: %s", fail_reg, esp_err_to_name(fail_err));
        return fail_msg;
    }

    playing = true;
    task_alive = true;
    xTaskCreate(tone_task, "tone", 4096, NULL, 4, NULL);
    return NULL;
}

const char *codec_tone_start(void)
{
    if (playing) return NULL;
    monitor_mode = false;
    loopback_mode = false;
    return start_common();
}

const char *codec_loopback_start(void)
{
    if (playing) return NULL;
    monitor_mode = false;
    loopback_mode = true;
    return start_common();
}

const char *codec_monitor_start(void)
{
    if (playing) return NULL;
    monitor_mode = true;
    loopback_mode = false;
    return start_common();
}

void codec_tone_stop(void) { playing = false; }
bool codec_tone_playing(void) { return playing; }

bool codec_read_reg(uint8_t reg, uint8_t *val)
{
    return i2c_master_transmit_receive(codec_dev, &reg, 1, val, 1, 100) == ESP_OK;
}

bool codec_write_reg(uint8_t reg, uint8_t val)
{
    return cw(reg, val) == ESP_OK;
}

int codec_mic_level(void) { return mic_level; }

void codec_set_mic_gain(int step)
{
    if (step < 0) step = 0;
    if (step > 8) step = 8;
    mic_gain_reg = (uint8_t)(step * 0x11);
    cw(0x09, mic_gain_reg);
}

void codec_set_out_volume(int reg)
{
    if (reg < 0) reg = 0;
    if (reg > 33) reg = 33;
    out_vol_reg = (uint8_t)reg;
    cw(0x2E, out_vol_reg);
    cw(0x2F, out_vol_reg);
    cw(0x30, out_vol_reg);
    cw(0x31, out_vol_reg);
}

bool codec_wait_stopped(int ms)
{
    for (int t = 0; t < ms && (task_alive || playing); t += 20) vTaskDelay(pdMS_TO_TICKS(20));
    return !task_alive && !playing;
}

void codec_stats_reset(void)
{
    hold_l = 0;
    hold_r = 0;
    sum_l = 0;
    sum_r = 0;
    sum_n = 0;
}

// Peak and average (RMS) amplitude per channel since the last reset, 0..32767.
void codec_stats_get(int *peak_l, int *peak_r, int *rms_l, int *rms_r)
{
    uint32_t n = sum_n ? sum_n : 1;
    *peak_l = hold_l;
    *peak_r = hold_r;
    *rms_l = (int)sqrtf((float)(sum_l / n));
    *rms_r = (int)sqrtf((float)(sum_r / n));
}

void codec_set_mic_input(int input)
{
    mic_sel_reg = (input == 2) ? 0x50 : 0x00;
    cw(0x0A, mic_sel_reg);
}

// ---- mic diagnostics ----
void codec_mic_config(int src, int inv, int sw_gain, int dcblock, int mute, int beep)
{
    if (beep >= 0) mic_beep = beep != 0;
    if (src >= 0 && src <= 3) mic_src = src;
    if (inv >= 0) mic_inv = inv != 0;
    if (sw_gain >= 1 && sw_gain <= 16) mic_sw_gain = sw_gain;
    if (dcblock >= 0) mic_dcblock = dcblock != 0;
    if (mute >= 0) mic_mute = mute != 0;
}

void codec_mic_status(char *out, size_t n)
{
    int pl, pr, rl, rr;
    codec_stats_get(&pl, &pr, &rl, &rr);
    uint32_t cnt = sum_n ? sum_n : 1;
    uint8_t r09 = 0xEE, r0a = 0xEE, r10 = 0xEE, r11 = 0xEE, r03 = 0xEE;
    codec_read_reg(0x09, &r09); codec_read_reg(0x0A, &r0a);
    codec_read_reg(0x10, &r10); codec_read_reg(0x11, &r11); codec_read_reg(0x03, &r03);
    snprintf(out, n,
        "running=%d frames=%u (window %u)\n"
        "L: mean(DC) %d  rms %d  peak %d\n"
        "R: mean(DC) %d  rms %d  peak %d\n"
        "src=%d inv=%d swgain=%dx dcblock=%d mute=%d beep=%d\n"
        "regs: 03=%02X 09(PGA)=%02X 0A(sel)=%02X 10=%02X 11=%02X\n"
        "errors: read=%u short=%u write=%u\n",
        (int)playing, (unsigned)frames_total, (unsigned)sum_n,
        (int)(dc_sum_l / cnt), rl, pl, (int)(dc_sum_r / cnt), rr, pr,
        mic_src, mic_inv, mic_sw_gain, mic_dcblock, mic_mute, mic_beep,
        r03, r09, r0a, r10, r11, (unsigned)rd_err, (unsigned)rd_short, (unsigned)wr_err);
}

void codec_stats_reset_all(void)
{
    codec_stats_reset();
    dc_sum_l = dc_sum_r = 0;
    rd_err = wr_err = rd_short = 0;
}

// Capture 256 frames of raw ADC data (L,R) into the snapshot. Returns false on timeout.
bool codec_snapshot(const int16_t **l, const int16_t **r)
{
    snap_pos = 0;
    snap_req = 256;
    for (int t = 0; t < 500 && snap_req > 0; t += 10) vTaskDelay(pdMS_TO_TICKS(10));
    if (snap_req > 0) { snap_req = 0; return false; }
    *l = snap[0];
    *r = snap[1];
    return true;
}
