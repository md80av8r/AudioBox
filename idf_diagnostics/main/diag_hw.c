#include "diag_hw.h"
#include "driver/gpio.h"
#include "pins_companion.h"

// Set to 1 if the haptic motor is an LRA, 0 for an ERM (coin/cylinder) motor.
#define HAPTIC_IS_LRA 0

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

bool diag_expander_read(uint8_t *bits)
{
    uint8_t reg = 0x00;   // PCA9534 input port register
    return i2c_master_transmit_receive(exp_dev, &reg, 1, bits, 1, 50) == ESP_OK;
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
