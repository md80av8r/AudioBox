// CrowPanel Advance 4.3" + audio companion diagnostics.
// Display/touch pin map and init from Elecrow's CrowPanel-Advance-4.3 example code.
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/i2c_master.h"
#include "esp_heap_caps.h"
#include "esp_timer.h"
#include "esp_ota_ops.h"
#include "nvs_flash.h"
#include "esp_lcd_panel_ops.h"
#include "esp_lcd_panel_rgb.h"
#include "lvgl.h"
#include "diag_hw.h"
#include "diag_ui.h"
#include "link.h"
#include "codec.h"

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
            return;
        }
        backlight(250);                       // wake touch screen
        gpio_set_direction(PIN_TOUCH_RST, GPIO_MODE_OUTPUT);
        gpio_set_level(PIN_TOUCH_RST, 0);
        vTaskDelay(pdMS_TO_TICKS(120));
        gpio_set_direction(PIN_TOUCH_RST, GPIO_MODE_INPUT);
        vTaskDelay(pdMS_TO_TICKS(100));
    }
    printf("WARNING: 0x30 / 0x5D not both found\n");
}

// Returns 1 pressed, 0 released, -1 no new data.
static int gt911_poll(int *x, int *y)
{
    uint8_t reg[2] = {0x81, 0x4E};
    uint8_t status = 0;
    if (i2c_master_transmit_receive(touch_dev, reg, 2, &status, 1, 20) != ESP_OK) return -1;
    if (!(status & 0x80)) return -1;
    int n = status & 0x0F;
    if (n > 0) {
        uint8_t pt_reg[2] = {0x81, 0x50};
        uint8_t d[4];
        if (i2c_master_transmit_receive(touch_dev, pt_reg, 2, d, 4, 20) == ESP_OK) {
            *x = d[0] | (d[1] << 8);
            *y = d[2] | (d[3] << 8);
        }
    }
    uint8_t clr[3] = {0x81, 0x4E, 0x00};
    i2c_master_transmit(touch_dev, clr, 3, 20);
    return n > 0;
}

static void touch_read_cb(lv_indev_t *indev, lv_indev_data_t *data)
{
    (void)indev;
    static int lx, ly;
    static bool pressed;
    int x, y, r = gt911_poll(&x, &y);
    if (r == 1) { pressed = true; lx = x; ly = y; }
    else if (r == 0) { pressed = false; }
    data->point.x = lx;
    data->point.y = ly;
    data->state = pressed ? LV_INDEV_STATE_PRESSED : LV_INDEV_STATE_RELEASED;
}

static void flush_cb(lv_display_t *disp, const lv_area_t *area, uint8_t *px_map)
{
    esp_lcd_panel_draw_bitmap(panel, area->x1, area->y1, area->x2 + 1, area->y2 + 1, px_map);
    lv_display_flush_ready(disp);
}

static uint32_t tick_cb(void)
{
    return (uint32_t)(esp_timer_get_time() / 1000);
}

static void lvgl_task(void *arg)
{
    (void)arg;
    diag_ui_create();
    while (1) {
        uint32_t wait = lv_timer_handler();
        if (wait < 5) wait = 5;
        if (wait > 30) wait = 30;
        vTaskDelay(pdMS_TO_TICKS(wait));
    }
}

void app_main(void)
{
    esp_err_t nvs = nvs_flash_init();
    if (nvs == ESP_ERR_NVS_NO_FREE_PAGES || nvs == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        nvs = nvs_flash_init();
    }
    ESP_ERROR_CHECK(nvs);
    link_init();   // Wi-Fi station + ESP-NOW crew link

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
    diag_hw_init(bus);
    codec_init(bus);

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
        .in_color_format = LCD_COLOR_FMT_RGB565,
        .out_color_format = LCD_COLOR_FMT_RGB565,
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

    lv_init();
    lv_tick_set_cb(tick_cb);

    // Internal RAM is tight once Wi-Fi is linked in, so keep the draw strips small (20 lines).
    const size_t buf_px = LCD_W * 20;
    void *buf1 = heap_caps_malloc(buf_px * 2, MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
    void *buf2 = heap_caps_malloc(buf_px * 2, MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
    assert(buf1 && buf2);

    lv_display_t *disp = lv_display_create(LCD_W, LCD_H);
    lv_display_set_color_format(disp, LV_COLOR_FORMAT_RGB565);
    lv_display_set_flush_cb(disp, flush_cb);
    lv_display_set_buffers(disp, buf1, buf2, buf_px * 2, LV_DISPLAY_RENDER_MODE_PARTIAL);

    lv_indev_t *indev = lv_indev_create();
    lv_indev_set_type(indev, LV_INDEV_TYPE_POINTER);
    lv_indev_set_read_cb(indev, touch_read_cb);

    backlight(0);                              // brightest
    xTaskCreate(lvgl_task, "lvgl", 8192, NULL, 5, NULL);

    // Everything came up: keep this firmware (otherwise the bootloader rolls back after an update).
    esp_ota_mark_app_valid_cancel_rollback();
}
