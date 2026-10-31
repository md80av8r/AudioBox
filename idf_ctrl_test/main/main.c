// Control line test for the audio companion board.
// Steps through ANR_POWER_EN (IO8) and BYPASS_EN (IO20) while you watch the LEDs:
//   ANR on    -> white D6 (+12V) lights
//   BYPASS on -> yellow D5 lights, red D7 goes out (relay coil driven)
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "pins_companion.h"

static void set_pin(int pin, int level, const char *what)
{
    gpio_set_level(pin, level);
    printf("%-14s %s\n", what, level ? "ON" : "OFF");
}

void app_main(void)
{
    gpio_config_t cfg = {
        .pin_bit_mask = (1ULL << PIN_ANR_POWER_EN) | (1ULL << PIN_BYPASS_EN),
        .mode = GPIO_MODE_OUTPUT,
    };
    ESP_ERROR_CHECK(gpio_config(&cfg));
    gpio_set_level(PIN_ANR_POWER_EN, 0);
    gpio_set_level(PIN_BYPASS_EN, 0);

    while (1) {
        printf("\n--- cycle ---\n");
        set_pin(PIN_ANR_POWER_EN, 1, "ANR_POWER_EN");
        vTaskDelay(pdMS_TO_TICKS(3000));
        set_pin(PIN_ANR_POWER_EN, 0, "ANR_POWER_EN");
        vTaskDelay(pdMS_TO_TICKS(2000));
        set_pin(PIN_BYPASS_EN, 1, "BYPASS_EN");
        vTaskDelay(pdMS_TO_TICKS(3000));
        set_pin(PIN_BYPASS_EN, 0, "BYPASS_EN");
        vTaskDelay(pdMS_TO_TICKS(2000));
    }
}
