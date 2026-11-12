// Crew link between two companion boxes: ESP-NOW heartbeat on a fixed channel (shared with the update hotspot).
#pragma once
#include <stdbool.h>
#include <stdint.h>

#define LINK_CHANNEL 6

// Local state flags carried in every heartbeat and shown on the peer box.
#define LINK_F_ACTIVE 0x01   // processing path ACTIVE (IO20 high); clear = BYPASS
#define LINK_F_ANR    0x02   // 12 V / ANR power on
#define LINK_F_MIC    0x04   // mic monitor live

bool link_wifi_prepare(void);                       // one-time Wi-Fi driver init (shared with the update hotspot)
void link_init(void);                               // Wi-Fi station + ESP-NOW + 2 Hz heartbeat
bool link_ap_start(const char *ssid, const char *pass, int channel);   // update hotspot, keeps the link running
void link_ap_stop(void);

void link_set_flags(uint8_t flags);                 // what this box reports to its peer
bool link_connected(void);                          // heard the peer in the last 2.5 s
int  link_rssi(void);                               // dBm of the last peer packet
uint8_t link_peer_flags(void);
uint32_t link_rx_count(void);
