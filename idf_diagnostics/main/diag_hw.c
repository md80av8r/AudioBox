#include "diag_hw.h"
#include "driver/gpio.h"
#include "pins_companion.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// Set to 1 if the haptic motor is an LRA, 0 for an ERM (coin/cylinder) motor.
#define HAPTIC_IS_LRA 0

// Quadrature transitions per detent: 4 for most EC11-style encoders, 2 for some.
#define ENC_STEPS_PER_DETENT 4

static i2c_master_bus_handle_t bus;
static i2c_master_dev_handle_t exp_dev, haptic_dev;

static diag_dev_t devs[] = {
    {"ES8388 codec",       0x10, false},
    {"PCA9534 expander",   0x38, false},
    {"DRV2605L haptic",    0x5A, false},
    {"Backlight MCU",      0x30, false},
    {"GT911 touch",        0x5D, false},
    {"Elecrow chip",       0x51, false},
};
#define NDEV (sizeof(devs) / sizeof(devs[0]))

static void poll_task(void *arg);

void diag_hw_init(i2c_master_bus_handle_t b)
{
    bus = b;
    i2c_device_config_t cfg = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .scl_speed_hz = 400000,
    };
    cfg.device_address = 0x38;
    ESP_ERROR_CHECK(i2c_master_bus_add_device(bus, &cfg, &exp_dev));
    cfg.device_address = 0x5A;
    ESP_ERROR_CHECK(i2c_master_bus_add_device(bus, &cfg, &haptic_dev));

    gpio_config_t out = {
        .pin_bit_mask = (1ULL << PIN_ANR_POWER_EN) | (1ULL << PIN_BYPASS_EN),
        .mode = GPIO_MODE_OUTPUT,
    };
    ESP_ERROR_CHECK(gpio_config(&out));
    gpio_set_level(PIN_ANR_POWER_EN, 0);
    gpio_set_level(PIN_BYPASS_EN, 0);

    diag_scan();
    xTaskCreate(poll_task, "exp_poll", 3072, NULL, 4, NULL);
}

int diag_dev_count(void) { return (int)NDEV; }
const diag_dev_t *diag_dev(int i) { return &devs[i]; }

void diag_scan(void)
{
    for (size_t i = 0; i < NDEV; i++) {
        devs[i].present = (i2c_master_probe(bus, devs[i].addr, 50) == ESP_OK);
    }
}

void diag_set_anr(bool on)    { gpio_set_level(PIN_ANR_POWER_EN, on); }
void diag_set_bypass(bool on) { gpio_set_level(PIN_BYPASS_EN, on); }

static volatile uint8_t last_bits;
static volatile bool last_ok;
static volatile int32_t outer_count, inner_count;
static volatile bool push_down;

bool diag_expander_read(uint8_t *bits)
{
    *bits = last_bits;
    return last_ok;
}

void diag_enc_get(int32_t *outer, int32_t *inner, bool *pushed)
{
    *outer = outer_count / ENC_STEPS_PER_DETENT;
    *inner = inner_count / ENC_STEPS_PER_DETENT;
    *pushed = push_down;
}

void diag_enc_reset(void)
{
    outer_count = 0;
    inner_count = 0;
}

// Gray-code transition table, indexed by (previous AB << 2) | current AB.
static const int8_t quad_tbl[16] = {0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0};

static void poll_task(void *arg)
{
    (void)arg;
    uint8_t o_prev = 0, i_prev = 0;
    bool primed = false;
    while (1) {
        uint8_t reg = 0x00;   // PCA9534 input port register
        uint8_t v = 0;
        bool ok = i2c_master_transmit_receive(exp_dev, &reg, 1, &v, 1, 20) == ESP_OK;
        last_ok = ok;
        if (ok) {
            last_bits = v;
            uint8_t o = (v >> EXP_BIT_ENC_A) & 0x3;
            uint8_t i = (v >> EXP_BIT_ENC_IA) & 0x3;
            if (!primed) {
                o_prev = o;
                i_prev = i;
                primed = true;
            }
            outer_count += quad_tbl[(o_prev << 2) | o];
            inner_count += quad_tbl[(i_prev << 2) | i];
            o_prev = o;
            i_prev = i;
            push_down = !(v & (1 << EXP_BIT_ENC_PUSH));
        }
        vTaskDelay(pdMS_TO_TICKS(2));
    }
}

static esp_err_t drv_write(uint8_t reg, uint8_t val)
{
    uint8_t b[2] = {reg, val};
    return i2c_master_transmit(haptic_dev, b, 2, 50);
}

bool diag_haptic_buzz(void)
{
    esp_err_t e = ESP_OK;
    e |= drv_write(0x01, 0x00);                          // out of standby, internal trigger
    e |= drv_write(0x1A, HAPTIC_IS_LRA ? 0xB6 : 0x36);   // feedback: motor type
    e |= drv_write(0x03, HAPTIC_IS_LRA ? 6 : 1);         // effect library
    e |= drv_write(0x04, 47);                            // waveform: buzz
    e |= drv_write(0x05, 0);                             // end of sequence
    e |= drv_write(0x0C, 1);                             // GO
    return e == ESP_OK;
}
