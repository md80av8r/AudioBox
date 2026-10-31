// Wi-Fi hotspot firmware update: the board hosts its own network and a web page
// where a new .bin can be uploaded from a phone or laptop.
#pragma once
#include <stdbool.h>

#define OTA_SSID "AudioBox-Update"
#define OTA_PASS "audiobox1"      // WPA2 needs at least 8 characters

bool ota_start(void);
void ota_stop(void);
bool ota_running(void);
