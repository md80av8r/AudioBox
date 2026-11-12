// Crew link between two companion boxes: ESP-NOW heartbeat on a fixed channel (shared with the update hotspot).
#pragma once
#include <stdbool.h>
#include <stdint.h>

#define LINK_CHANNEL 6

// Local state flags carried in every heartbeat and shown on the peer box.
#define LINK_F_ACTIVE 0x01   // processing path ACTIVE (IO20 high); clear = BYPASS
#define LINK_F_ANR    0x02   // 12 V / ANR power on
#define LINK_F_MIC    0x04   // mic monitor live
#define LINK_F_COMMS  0x08   // intercom on (sending and playing crew voice)

bool link_wifi_prepare(void);                       // one-time Wi-Fi driver init (shared with the update hotspot)
void link_init(void);                               // Wi-Fi station + ESP-NOW + 2 Hz heartbeat
bool link_ap_start(const char *ssid, const char *pass, int channel);   // update hotspot, keeps the link running
void link_ap_stop(void);

void link_set_flags(uint8_t flags);                 // what this box reports to its peer
bool link_connected(void);                          // heard the peer in the last 2.5 s
int  link_rssi(void);                               // dBm of the last peer packet
uint8_t link_peer_flags(void);
uint32_t link_rx_count(void);

// Crew voice: 16 kHz mono, G.711 u-law, 160 samples (10 ms) per ESP-NOW packet.
#define LINK_AUDIO_SAMPLES 160
uint8_t link_ulaw_encode(int16_t pcm);
void link_send_audio(const uint8_t *ulaw);          // exactly LINK_AUDIO_SAMPLES bytes
int  link_audio_read(int16_t *out, int max);        // decoded samples from the jitter buffer (0 = nothing yet / underrun)
void link_audio_reset(void);
void link_audio_stats(uint32_t *rx_pkts, uint32_t *drops, uint32_t *underruns);
