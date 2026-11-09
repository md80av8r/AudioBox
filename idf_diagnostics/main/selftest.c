#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include "driver/gpio.h"
#include "esp_app_desc.h"
#include "esp_rom_sys.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "codec.h"
#include "diag_hw.h"
#include "pins_companion.h"
#include "selftest.h"

static char *out;
static size_t cap, len;
static int npass, nfail;

static void put(const char *fmt, ...)
{
    if (len + 1 >= cap) return;
    va_list ap;
    va_start(ap, fmt);
    int n = vsnprintf(out + len, cap - len, fmt, ap);
    va_end(ap);
    if (n > 0) len += (size_t)n;
    if (len >= cap) len = cap - 1;
}

static void check(bool ok, const char *fmt, ...)
{
    char line[160];
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(line, sizeof(line), fmt, ap);
    va_end(ap);
    put("[%s] %s\n", ok ? "PASS" : "FAIL", line);
    if (ok) npass++; else nfail++;
}

static bool pin_follows(int pin, int level)
{
    gpio_set_level(pin, level);
    esp_rom_delay_us(300);
    return gpio_get_level(pin) == level;
}

// Drives a pin low then high and reads the pad back: a pin held by something else will not follow.
static void test_pin(const char *name, int pin)
{
    gpio_reset_pin(pin);
    gpio_set_direction(pin, GPIO_MODE_INPUT_OUTPUT);
    bool lo = pin_follows(pin, 0);
    bool hi = pin_follows(pin, 1);
    gpio_set_level(pin, 0);
    gpio_set_direction(pin, GPIO_MODE_INPUT);   // release
    check(lo && hi, "%-5s IO%-2d  low:%s  high:%s", name, pin,
          lo ? "ok" : "STUCK HIGH", hi ? "ok" : "STUCK LOW");
}

int selftest_run(char *buf, size_t size, int *passed)
{
    out = buf;
    cap = size;
    len = 0;
    npass = nfail = 0;
    buf[0] = 0;

    put("Audio companion self-test\nfirmware %s\n\n", esp_app_get_description()->version);
    if (codec_tone_playing()) {
        put("Stop the tone first.\n");
        *passed = 0;
        return 1;
    }

    put("I2C devices\n");
    diag_scan();
    for (int i = 0; i < diag_dev_count(); i++) {
        const diag_dev_t *d = diag_dev(i);
        check(d->present, "%-18s 0x%02X", d->name, d->addr);
    }

    put("\nCodec (ES8388) registers\n");
    static const uint8_t regs[] = {0x00, 0x01, 0x02, 0x03, 0x04, 0x08, 0x17, 0x18, 0x19, 0x2E, 0x30};
    for (size_t i = 0; i < sizeof(regs); i++) {
        uint8_t v;
        if (codec_read_reg(regs[i], &v)) put("  r%02X = %02X\n", regs[i], v);
        else put("  r%02X read failed\n", regs[i]);
    }
    uint8_t r08;
    if (codec_read_reg(0x08, &r08)) {
        check(!(r08 & 0x80), "clock mode is %s (must be slave)", (r08 & 0x80) ? "MASTER" : "slave");
    } else {
        check(false, "could not read the codec clock mode");
    }
    uint8_t orig, back;
    if (codec_read_reg(0x30, &orig) && codec_write_reg(0x30, 0x15) && codec_read_reg(0x30, &back)) {
        check(back == 0x15, "register write/readback (wrote 15, read %02X)", back);
        codec_write_reg(0x30, orig);
    } else {
        check(false, "register write/readback (I2C error)");
    }

    put("\nExpander (PCA9534) inputs\n");
    uint8_t bits;
    bool ok = diag_expander_read(&bits);
    check(ok, "expander read");
    if (ok) put("  bits = %02X (bit0 encA, 1 encB, 2 power, 3 inA, 4 inB, 5 push, 6 bypass, 7 spare)\n", bits);

    put("\nI2S pins (driven low and high, read back)\n");
    test_pin("MCLK", PIN_I2S_MCLK);
    test_pin("BCLK", PIN_I2S_BCLK);
    test_pin("LRCK", PIN_I2S_LRCK);
    test_pin("DOUT", PIN_I2S_DOUT);

    put("\nBypass control pin (IO20)\n");
    check(!diag_usb_pad_override(), "USB block is not overriding IO19/IO20");
    {
        gpio_set_direction(PIN_BYPASS_EN, GPIO_MODE_INPUT_OUTPUT);
        gpio_set_level(PIN_BYPASS_EN, 1);
        esp_rom_delay_us(500);
        int hi = gpio_get_level(PIN_BYPASS_EN);
        gpio_set_level(PIN_BYPASS_EN, 0);
        esp_rom_delay_us(500);
        int lo = gpio_get_level(PIN_BYPASS_EN);
        check(hi == 1 && lo == 0, "IO20 pad follows the output (high reads %d, low reads %d)", hi, lo);
    }

    put("\nLoopback (needs LINE OUT jumpered to LINE IN: L to L, G to G)\n");
    const char *err = codec_loopback_start();
    if (err) {
        check(false, "loopback could not start: %s", err);
    } else {
        vTaskDelay(pdMS_TO_TICKS(700));
        int level = codec_mic_level();
        codec_tone_stop();
        codec_wait_stopped(600);
        check(level >= 40, "tone heard on LINE IN: level %d%% (needs 40%% or more)", level);
        if (level < 40) {
            put("  If the jumper wires are on, the problem is between the codec output and the connectors.\n");
        }
    }

    put("\nResult: %d pass, %d FAIL\n", npass, nfail);
    *passed = npass;
    return nfail;
}
