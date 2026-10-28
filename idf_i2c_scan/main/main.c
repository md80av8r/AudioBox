// I2C bus scan for the audio companion board.
// Expected: ES8388 (0x10/0x11), PCA9534A (0x38-0x3F), DRV2605L (0x5A).
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/i2c_master.h"
#include "pins_companion.h"

static const char *name_for(uint8_t addr)
{
    if (addr == 0x10 || addr == 0x11) return "ES8388 codec";
    if (addr >= 0x38 && addr <= 0x3F) return "PCA9534 expander";
    if (addr == 0x5A) return "DRV2605L haptic";
    return "unknown";
}

void app_main(void)
{
    i2c_master_bus_config_t cfg = {
        .i2c_port = I2C_NUM_0,
        .sda_io_num = PIN_I2C_SDA,
        .scl_io_num = PIN_I2C_SCL,
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = 7,
        .flags.enable_internal_pullup = true,
    };
    i2c_master_bus_handle_t bus;
    ESP_ERROR_CHECK(i2c_new_master_bus(&cfg, &bus));

    while (1) {
        int found = 0;
        printf("\nScanning I2C (SDA=%d SCL=%d)...\n", PIN_I2C_SDA, PIN_I2C_SCL);
        for (uint8_t addr = 0x08; addr < 0x78; addr++) {
            if (i2c_master_probe(bus, addr, 50) == ESP_OK) {
                printf("  0x%02X  %s\n", addr, name_for(addr));
                found++;
            }
        }
        printf("Found %d device(s)\n", found);
        vTaskDelay(pdMS_TO_TICKS(3000));
    }
}
