idf_component_register(SRCS "main.c" "diag_hw.c" "diag_ui.c" "ota.c" "codec.c"
                       INCLUDE_DIRS "."
                       PRIV_INCLUDE_DIRS "../../firmware/src"
                       PRIV_REQUIRES esp_lcd esp_driver_i2c esp_driver_gpio esp_driver_i2s esp_psram esp_timer esp_wifi esp_netif esp_event esp_http_server nvs_flash app_update esp_app_format lvgl__lvgl)
