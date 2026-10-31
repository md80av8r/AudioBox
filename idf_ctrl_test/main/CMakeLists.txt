idf_component_register(SRCS "main.c"
                       INCLUDE_DIRS "."
                       PRIV_INCLUDE_DIRS "../../firmware/src"
                       PRIV_REQUIRES esp_driver_gpio)
