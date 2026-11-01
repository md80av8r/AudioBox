#include <math.h>
#include <stdint.h>
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
static volatile bool playing;
static volatile bool task_alive;

static esp_err_t cw(uint8_t reg, uint8_t val)
{
    uint8_t b[2] = {reg, val};
    return i2c_master_transmit(codec_dev, b, 2, 50);
}

void codec_init(i2c_master_bus_handle_t bus)
{
    i2c_device_config_t cfg = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = CODEC_ADDR,
        .scl_speed_hz = 400000,
    };
    ESP_ERROR_CHECK(i2c_master_bus_add_device(bus, &cfg, &codec_dev));
}

// Playback setup: slave mode, 16-bit I2S, single speed with MCLK = 256 x fs.
static bool codec_configure(void)
{
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
    e |= cw(0x1A, 0x00);   // DAC digital volume left, 0 dB
    e |= cw(0x1B, 0x00);   // DAC digital volume right, 0 dB
    e |= cw(0x2E, OUT_VOLUME);   // LOUT1
    e |= cw(0x2F, OUT_VOLUME);   // ROUT1
    e |= cw(0x30, OUT_VOLUME);   // LOUT2
    e |= cw(0x31, OUT_VOLUME);   // ROUT2
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
        int16_t s = (int16_t)(TONE_AMP * sinf(2.0f * (float)M_PI * i / N));
        cycle[2 * i] = s;
        cycle[2 * i + 1] = s;
    }
    static int16_t buf[N * 2 * 8];
    for (int k = 0; k < 8; k++) {
        for (int i = 0; i < N * 2; i++) buf[k * N * 2 + i] = cycle[i];
    }
    while (playing) {
        size_t written;
        i2s_channel_write(tx, buf, sizeof(buf), &written, 200);
    }
    cw(0x19, 0x04);          // mute
    cw(0x04, 0xC0);          // outputs off
    i2s_channel_disable(tx);
    i2s_del_channel(tx);
    tx = NULL;
    task_alive = false;
    vTaskDelete(NULL);
}

bool codec_tone_start(void)
{
    if (playing) return true;
    if (task_alive) return false;   // previous run still shutting down

    i2s_chan_config_t cc = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
    cc.auto_clear = true;
    if (i2s_new_channel(&cc, &tx, NULL) != ESP_OK) return false;

    i2s_std_config_t std = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(SAMPLE_RATE),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_STEREO),
        .gpio_cfg = {
            .mclk = PIN_I2S_MCLK,
            .bclk = PIN_I2S_BCLK,
            .ws   = PIN_I2S_LRCK,
            .dout = PIN_I2S_DOUT,
            .din  = I2S_GPIO_UNUSED,
        },
    };
    if (i2s_channel_init_std_mode(tx, &std) != ESP_OK || i2s_channel_enable(tx) != ESP_OK) {
        i2s_del_channel(tx);
        tx = NULL;
        return false;
    }

    vTaskDelay(pdMS_TO_TICKS(20));   // let MCLK settle before talking to the codec
    if (!codec_configure()) {
        i2s_channel_disable(tx);
        i2s_del_channel(tx);
        tx = NULL;
        return false;
    }

    playing = true;
    task_alive = true;
    xTaskCreate(tone_task, "tone", 4096, NULL, 4, NULL);
    return true;
}

void codec_tone_stop(void) { playing = false; }
bool codec_tone_playing(void) { return playing; }
