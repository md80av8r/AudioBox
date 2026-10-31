// CrowPanel Advance 4.3" bring-up: backlight, color bars, touch coordinates.
// Pin map and init sequence from Elecrow's CrowPanel-Advance-4.3 example code.
#include <stdio.h>
#include <stdlib.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/i2c_master.h"
#include "esp_lcd_panel_ops.h"
#include "esp_lcd_panel_rgb.h"

#define LCD_W 800
#define LCD_H 480

#define PIN_I2C_SDA   15
#define PIN_I2C_SCL   16
#define PIN_TOUCH_RST  1   // pulsed low to wake the touch controller

#define ADDR_BL_MCU  0x30  // backlight MCU: one byte, 0 = brightest, 245 = off, 250 = wake touch
#define ADDR_GT911   0x5D

static i2c_master_bus_handle_t bus;
static i2c_master_dev_handle_t bl_dev, touch_dev;
static esp_lcd_panel_handle_t panel;

static void backlight(uint8_t value)
{
    i2c_master_transmit(bl_dev, &value, 1, 100);
}

static void wait_for_i2c_devices(void)
{
    for (int i = 0; i < 20; i++) {
        if (i2c_master_probe(bus, ADDR_BL_MCU, 50) == ESP_OK &&
            i2c_master_probe(bus, ADDR_GT911, 50) == ESP_OK) {
            printf("Found backlight MCU (0x30) and GT911 (0x5D)\n");
            return;
        }
        printf("Waiting for 0x30 / 0x5D...\n");
        backlight(250);                       // wake touch screen
        gpio_set_direction(PIN_TOUCH_RST, GPIO_MODE_OUTPUT);
        gpio_set_level(PIN_TOUCH_RST, 0);
        vTaskDelay(pdMS_TO_TICKS(120));
        gpio_set_direction(PIN_TOUCH_RST, GPIO_MODE_INPUT);
        vTaskDelay(pdMS_TO_TICKS(100));
    }
    printf("WARNING: 0x30 / 0x5D not both found; continuing anyway\n");
}

static void draw_color_bars(void)
{
    static const uint16_t bars[8] = {
        0xFFFF, 0xFFE0, 0x07FF, 0x07E0, 0xF81F, 0xF800, 0x001F, 0x0000,
    };
    const int strip = 20;
    uint16_t *buf = malloc(LCD_W * strip * sizeof(uint16_t));
    if (!buf) { printf("no memory for strip\n"); return; }
    for (int x = 0; x < LCD_W; x++) {
        uint16_t c = bars[x / (LCD_W / 8)];
        for (int y = 0; y < strip; y++) buf[y * LCD_W + x] = c;
    }
    for (int y = 0; y < LCD_H; y += strip) {
        esp_lcd_panel_draw_bitmap(panel, 0, y, LCD_W, y + strip, buf);
    }
    free(buf);
}

static void draw_dot(int cx, int cy)
{
    static uint16_t dot[16 * 16];
    for (int i = 0; i < 16 * 16; i++) dot[i] = 0x0000;   // black dot on the bars
    int x0 = cx - 8, y0 = cy - 8;
    if (x0 < 0) x0 = 0;
    if (y0 < 0) y0 = 0;
    if (x0 > LCD_W - 16) x0 = LCD_W - 16;
    if (y0 > LCD_H - 16) y0 = LCD_H - 16;
    esp_lcd_panel_draw_bitmap(panel, x0, y0, x0 + 16, y0 + 16, dot);
}

static bool gt911_read_touch(int *x, int *y)
{
    uint8_t reg[2] = {0x81, 0x4E};
    uint8_t status = 0;
    if (i2c_master_transmit_receive(touch_dev, reg, 2, &status, 1, 50) != ESP_OK) return false;
    bool touched = false;
    if ((status & 0x80) && (status & 0x0F) > 0) {
        uint8_t pt_reg[2] = {0x81, 0x50};
        uint8_t d[4];
        if (i2c_master_transmit_receive(touch_dev, pt_reg, 2, d, 4, 50) == ESP_OK) {
            *x = d[0] | (d[1] << 8);
            *y = d[2] | (d[3] << 8);
            touched = true;
        }
    }
    if (status & 0x80) {                       // clear the ready flag
        uint8_t clr[3] = {0x81, 0x4E, 0x00};
        i2c_master_transmit(touch_dev, clr, 3, 50);
    }
    return touched;
}

void app_main(void)
{
    i2c_master_bus_config_t bus_cfg = {
        .i2c_port = I2C_NUM_0,
        .sda_io_num = PIN_I2C_SDA,
        .scl_io_num = PIN_I2C_SCL,
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = 7,
        .flags.enable_internal_pullup = true,
    };
    ESP_ERROR_CHECK(i2c_new_master_bus(&bus_cfg, &bus));

    i2c_device_config_t dev_cfg = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .scl_speed_hz = 400000,
    };
    dev_cfg.device_address = ADDR_BL_MCU;
    ESP_ERROR_CHECK(i2c_master_bus_add_device(bus, &dev_cfg, &bl_dev));
    dev_cfg.device_address = ADDR_GT911;
    ESP_ERROR_CHECK(i2c_master_bus_add_device(bus, &dev_cfg, &touch_dev));

    wait_for_i2c_devices();

    esp_lcd_rgb_panel_config_t cfg = {
        .clk_src = LCD_CLK_SRC_DEFAULT,
        .timings = {
            .pclk_hz = 18000000,
            .h_res = LCD_W,
            .v_res = LCD_H,
            .hsync_pulse_width = 4,
            .hsync_back_porch = 8,
            .hsync_front_porch = 8,
            .vsync_pulse_width = 4,
            .vsync_back_porch = 8,
            .vsync_front_porch = 8,
            .flags.pclk_active_neg = 1,
            .flags.pclk_idle_high = 1,
        },
        .data_width = 16,
        .bits_per_pixel = 16,
        .num_fbs = 1,
        .bounce_buffer_size_px = LCD_W * 20,
        .dma_burst_size = 64,
        .hsync_gpio_num = 40,
        .vsync_gpio_num = 41,
        .de_gpio_num = 42,
        .pclk_gpio_num = 39,
        .disp_gpio_num = -1,
        // D0-D4 = B0-B4, D5-D10 = G0-G5, D11-D15 = R0-R4
        .data_gpio_nums = {21, 47, 48, 45, 38, 9, 10, 11, 12, 13, 14, 7, 17, 18, 3, 46},
        .flags.fb_in_psram = 1,
    };
    ESP_ERROR_CHECK(esp_lcd_new_rgb_panel(&cfg, &panel));
    ESP_ERROR_CHECK(esp_lcd_panel_reset(panel));
    ESP_ERROR_CHECK(esp_lcd_panel_init(panel));

    draw_color_bars();
    backlight(0);                              // brightest
    printf("Display on. Touch the screen.\n");

    while (1) {
        int x, y;
        if (gt911_read_touch(&x, &y)) {
            printf("touch x=%d y=%d\n", x, y);
            draw_dot(x, y);
        }
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}
