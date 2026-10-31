idf_component_register(SRCS "main.c" "diag_hw.c" "diag_ui.c"
                       INCLUDE_DIRS "."
                       PRIV_INCLUDE_DIRS "../../firmware/src"
                       PRIV_REQUIRES esp_lcd esp_driver_i2c esp_driver_gpio esp_psram esp_timer lvgl__lvgl)
