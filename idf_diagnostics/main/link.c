#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_now.h"
#include "esp_timer.h"
#include "esp_wifi.h"
#include "link.h"

static const char *TAG = "link";

#define PKT_MAGIC0 0xAB
#define PKT_MAGIC1 0x01   // protocol version
#define PKT_HELLO  0x01
#define PKT_AUDIO  0x02
#define RING       4096          // samples, power of two
#define PREFILL    480           // 30 ms of 16 kHz audio before playback starts
#define MAXBUF     1600          // above 100 ms buffered: drop back to PREFILL (bounds latency, absorbs clock drift)
#define LINK_TIMEOUT_US 2500000

typedef struct __attribute__((packed)) {
    uint8_t magic0, magic1, type, flags;
    uint16_t seq;
} hello_pkt_t;

static bool wifi_ready, link_up;
static volatile uint8_t local_flags, peer_flags;
static volatile int64_t peer_seen_us;
static volatile int peer_rssi = -127;
static volatile uint32_t rx_count;
static int16_t ring[RING];
static volatile uint32_t rw, rr;
static bool primed;
static volatile uint32_t a_rx, a_drop, a_under;
static uint16_t audio_seq;
static const uint8_t bcast[6] = {0xff, 0xff, 0xff, 0xff, 0xff, 0xff};

bool link_wifi_prepare(void)
{
    if (wifi_ready) return true;
    if (esp_netif_init() != ESP_OK) return false;
    esp_err_t e = esp_event_loop_create_default();
    if (e != ESP_OK && e != ESP_ERR_INVALID_STATE) return false;
    esp_netif_create_default_wifi_sta();
    esp_netif_create_default_wifi_ap();
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    if (esp_wifi_init(&cfg) != ESP_OK) return false;
    esp_wifi_set_storage(WIFI_STORAGE_RAM);
    wifi_ready = true;
    return true;
}

uint8_t link_ulaw_encode(int16_t pcm)
{
    int s = pcm, sign = (s >> 8) & 0x80;
    if (sign) s = -s;
    if (s > 32635) s = 32635;
    s += 0x84;
    int ex = 7;
    for (int m = 0x4000; (s & m) == 0 && ex > 0; ex--, m >>= 1) {}
    int mant = (s >> (ex + 3)) & 0x0F;
    return (uint8_t)~(sign | (ex << 4) | mant);
}

static int16_t ulaw_decode(uint8_t u)
{
    u = ~u;
    int ex = (u >> 4) & 7, mant = u & 0x0F;
    int s = (((mant << 3) + 0x84) << ex) - 0x84;
    return (int16_t)((u & 0x80) ? -s : s);
}

static void recv_cb(const esp_now_recv_info_t *info, const uint8_t *data, int len)
{
    if (len < (int)sizeof(hello_pkt_t)) return;
    const hello_pkt_t *p = (const hello_pkt_t *)data;
    if (p->magic0 != PKT_MAGIC0 || p->magic1 != PKT_MAGIC1) return;
    if (p->type == PKT_HELLO || p->type == PKT_AUDIO) {
        peer_flags = p->flags;
        peer_rssi = info->rx_ctrl ? info->rx_ctrl->rssi : -127;
        peer_seen_us = esp_timer_get_time();
        rx_count++;
    }
    if (p->type == PKT_AUDIO && len >= (int)sizeof(hello_pkt_t) + LINK_AUDIO_SAMPLES) {
        const uint8_t *u = data + sizeof(hello_pkt_t);
        uint32_t w = rw;
        for (int i = 0; i < LINK_AUDIO_SAMPLES; i++) ring[(w + i) & (RING - 1)] = ulaw_decode(u[i]);
        rw = w + LINK_AUDIO_SAMPLES;
        a_rx++;
    }
}

static void hello_task(void *arg)
{
    uint16_t seq = 0;
    for (;;) {
        hello_pkt_t p = {PKT_MAGIC0, PKT_MAGIC1, PKT_HELLO, local_flags, seq++};
        esp_now_send(bcast, (const uint8_t *)&p, sizeof(p));
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

void link_init(void)
{
    if (link_up || !link_wifi_prepare()) return;
    if (esp_wifi_set_mode(WIFI_MODE_STA) != ESP_OK) return;
    if (esp_wifi_start() != ESP_OK) return;
    esp_wifi_set_channel(LINK_CHANNEL, WIFI_SECOND_CHAN_NONE);
    esp_wifi_set_ps(WIFI_PS_NONE);
    if (esp_now_init() != ESP_OK) {
        ESP_LOGE(TAG, "esp_now_init failed");
        return;
    }
    esp_now_register_recv_cb(recv_cb);
    esp_now_peer_info_t peer = {0};
    memcpy(peer.peer_addr, bcast, 6);
    peer.channel = 0;            // follow the current channel
    peer.ifidx = WIFI_IF_STA;
    peer.encrypt = false;
    esp_now_add_peer(&peer);
    esp_now_rate_config_t rc = {.phymode = WIFI_PHY_MODE_11G, .rate = WIFI_PHY_RATE_24M};   // faster than the 1 Mbit/s default: less airtime per voice packet
    esp_now_set_peer_rate_config(bcast, &rc);
    xTaskCreate(hello_task, "link_hello", 3072, NULL, 4, NULL);
    link_up = true;
    ESP_LOGI(TAG, "link up on channel %d", LINK_CHANNEL);
}

bool link_ap_start(const char *ssid, const char *pass, int channel)
{
    if (!link_wifi_prepare()) return false;
    wifi_config_t ap = {0};
    strncpy((char *)ap.ap.ssid, ssid, sizeof(ap.ap.ssid) - 1);
    strncpy((char *)ap.ap.password, pass, sizeof(ap.ap.password) - 1);
    ap.ap.ssid_len = strlen(ssid);
    ap.ap.channel = channel;
    ap.ap.max_connection = 2;
    ap.ap.authmode = WIFI_AUTH_WPA2_PSK;
    if (esp_wifi_set_mode(WIFI_MODE_APSTA) != ESP_OK) return false;
    if (esp_wifi_set_config(WIFI_IF_AP, &ap) != ESP_OK) return false;
    if (esp_wifi_start() != ESP_OK) return false;   // no-op if already started
    return true;
}

void link_ap_stop(void)
{
    esp_wifi_set_mode(WIFI_MODE_STA);
}

void link_send_audio(const uint8_t *ulaw)
{
    uint8_t buf[sizeof(hello_pkt_t) + LINK_AUDIO_SAMPLES];
    hello_pkt_t h = {PKT_MAGIC0, PKT_MAGIC1, PKT_AUDIO, local_flags, audio_seq++};
    memcpy(buf, &h, sizeof(h));
    memcpy(buf + sizeof(h), ulaw, LINK_AUDIO_SAMPLES);
    esp_now_send(bcast, buf, sizeof(buf));
}

int link_audio_read(int16_t *out, int max)
{
    uint32_t w = rw, r = rr, avail = w - r;
    if (!primed) {
        if (avail < PREFILL) return 0;
        primed = true;
    }
    if (avail == 0) {
        primed = false;
        a_under++;
        return 0;
    }
    if (avail > MAXBUF) {
        r = w - PREFILL;
        avail = PREFILL;
        a_drop++;
    }
    int n = (int)avail < max ? (int)avail : max;
    for (int i = 0; i < n; i++) out[i] = ring[(r + i) & (RING - 1)];
    rr = r + n;
    return n;
}

void link_audio_reset(void)
{
    rr = rw;
    primed = false;
}

void link_audio_stats(uint32_t *rx_pkts, uint32_t *drops, uint32_t *underruns)
{
    *rx_pkts = a_rx; *drops = a_drop; *underruns = a_under;
}

void link_set_flags(uint8_t flags) { local_flags = flags; }
bool link_connected(void) { return peer_seen_us && (esp_timer_get_time() - peer_seen_us) < LINK_TIMEOUT_US; }
int  link_rssi(void) { return peer_rssi; }
uint8_t link_peer_flags(void) { return peer_flags; }
uint32_t link_rx_count(void) { return rx_count; }
