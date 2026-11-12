#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_event.h"
#include "esp_http_server.h"
#include "esp_netif.h"
#include "esp_ota_ops.h"
#include "esp_app_desc.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "ota.h"
#include "codec.h"
#include "diag_hw.h"
#include "driver/gpio.h"
#include "selftest.h"

static httpd_handle_t server;
static bool wifi_ready;
static bool running;

static const char page_head[] =
    "<!doctype html><meta name=viewport content=\"width=device-width,initial-scale=1\">"
    "<title>Audio Companion update</title>"
    "<h2>Audio Companion firmware update</h2><p>Current version: ";
static const char page_tail[] =
    "</p><input type=file id=f accept=\".bin\"><br><br>"
    "<button onclick=up()>Upload and install</button>"
    "<p><progress id=p value=0 max=100 style=\"width:300px\"></progress></p><p id=s></p>"
    "<script>function up(){var f=document.getElementById('f').files[0];if(!f){return}"
    "var x=new XMLHttpRequest();x.open('POST','/update');"
    "x.upload.onprogress=function(e){document.getElementById('p').value=e.loaded*100/e.total};"
    "x.onload=function(){document.getElementById('s').textContent=x.responseText};"
    "x.onerror=function(){document.getElementById('s').textContent='Upload failed'};"
    "x.send(f)}</script>"
    "<hr><p>Bench tools: <a href=/report>self-test report</a>, "
    "/i2c?dev=0x10&amp;reg=0x08 (add &amp;val=0x00 to write), "
    "/gpio?pin=5&amp;mode=out&amp;level=0 (mode in, out or release), "
    "/tone?on=1, <a href=/micscan>mic scan</a>, <a href=/mic>/mic</a> (input, gain, src, inv, sw, dc, mute, raw)</p>";

static esp_err_t index_get(httpd_req_t *req)
{
    httpd_resp_set_type(req, "text/html");
    httpd_resp_send_chunk(req, page_head, HTTPD_RESP_USE_STRLEN);
    httpd_resp_send_chunk(req, esp_app_get_description()->version, HTTPD_RESP_USE_STRLEN);
    httpd_resp_send_chunk(req, page_tail, HTTPD_RESP_USE_STRLEN);
    return httpd_resp_send_chunk(req, NULL, 0);
}

static void reboot_task(void *arg)
{
    (void)arg;
    vTaskDelay(pdMS_TO_TICKS(1500));
    esp_restart();
}

static esp_err_t update_post(httpd_req_t *req)
{
    const esp_partition_t *part = esp_ota_get_next_update_partition(NULL);
    if (!part) {
        httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "No update partition");
        return ESP_FAIL;
    }
    esp_ota_handle_t handle;
    if (esp_ota_begin(part, OTA_SIZE_UNKNOWN, &handle) != ESP_OK) {
        httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "Could not start update");
        return ESP_FAIL;
    }
    char *buf = malloc(4096);
    if (!buf) {
        esp_ota_abort(handle);
        httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "Out of memory");
        return ESP_FAIL;
    }
    int remaining = req->content_len;
    while (remaining > 0) {
        int r = httpd_req_recv(req, buf, remaining < 4096 ? remaining : 4096);
        if (r == HTTPD_SOCK_ERR_TIMEOUT) continue;
        if (r <= 0 || esp_ota_write(handle, buf, r) != ESP_OK) {
            free(buf);
            esp_ota_abort(handle);
            httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "Transfer failed");
            return ESP_FAIL;
        }
        remaining -= r;
    }
    free(buf);
    if (esp_ota_end(handle) != ESP_OK) {
        httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "Not a valid firmware image");
        return ESP_FAIL;
    }
    if (esp_ota_set_boot_partition(part) != ESP_OK) {
        httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "Could not select new firmware");
        return ESP_FAIL;
    }
    httpd_resp_sendstr(req, "Installed. Restarting...");
    xTaskCreate(reboot_task, "reboot", 2048, NULL, 5, NULL);
    return ESP_OK;
}


// ---- Bench tools: read the self-test report, poke I2C registers and pins from a browser ----

static bool qint(httpd_req_t *req, const char *key, long *val)
{
    char q[96], v[24];
    if (httpd_req_get_url_query_str(req, q, sizeof(q)) != ESP_OK) return false;
    if (httpd_query_key_value(q, key, v, sizeof(v)) != ESP_OK) return false;
    *val = strtol(v, NULL, 0);
    return true;
}

static bool qstr(httpd_req_t *req, const char *key, char *val, size_t n)
{
    char q[96];
    if (httpd_req_get_url_query_str(req, q, sizeof(q)) != ESP_OK) return false;
    return httpd_query_key_value(q, key, val, n) == ESP_OK;
}

static esp_err_t report_get(httpd_req_t *req)
{
    char *buf = malloc(4096);
    if (!buf) return httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "Out of memory");
    int passed;
    selftest_run(buf, 4096, &passed);
    httpd_resp_set_type(req, "text/plain");
    httpd_resp_sendstr(req, buf);
    free(buf);
    return ESP_OK;
}

static esp_err_t i2c_get(httpd_req_t *req)
{
    long dev, reg, val;
    char msg[96];
    httpd_resp_set_type(req, "text/plain");
    if (!qint(req, "dev", &dev) || !qint(req, "reg", &reg)) {
        return httpd_resp_sendstr(req, "usage: /i2c?dev=0x10&reg=0x08   (add &val=0x00 to write)");
    }
    bool write = qint(req, "val", &val);
    uint8_t out = 0;
    bool ok = diag_i2c_rw((uint8_t)dev, (uint8_t)reg, write ? (int)val : -1, &out);
    snprintf(msg, sizeof(msg), "dev 0x%02lX reg 0x%02lX %s %s 0x%02X\n", dev, reg,
             write ? "write" : "read", ok ? "ok" : "FAILED", out);
    return httpd_resp_sendstr(req, msg);
}

static esp_err_t gpio_get_handler(httpd_req_t *req)
{
    static const int allowed[] = {4, 5, 6, 19};   // the I2S pins only
    long pin, level;
    char mode[12], msg[96];
    httpd_resp_set_type(req, "text/plain");
    if (!qint(req, "pin", &pin) || !qstr(req, "mode", mode, sizeof(mode))) {
        return httpd_resp_sendstr(req, "usage: /gpio?pin=5&mode=out&level=0   (mode: in, out, release; pins 4 5 6 19)");
    }
    bool pin_ok = false;
    for (size_t i = 0; i < sizeof(allowed) / sizeof(allowed[0]); i++) pin_ok |= (allowed[i] == pin);
    if (!pin_ok) return httpd_resp_sendstr(req, "pin not allowed");

    if (!strcmp(mode, "out")) {
        gpio_reset_pin((int)pin);
        gpio_set_direction((int)pin, GPIO_MODE_INPUT_OUTPUT);
        gpio_set_level((int)pin, qint(req, "level", &level) ? (int)level : 0);
    } else if (!strcmp(mode, "in") || !strcmp(mode, "release")) {
        gpio_reset_pin((int)pin);
        gpio_set_direction((int)pin, GPIO_MODE_INPUT);
    }
    snprintf(msg, sizeof(msg), "IO%ld mode %s, pad reads %d\n", pin, mode, gpio_get_level((int)pin));
    return httpd_resp_sendstr(req, msg);
}

static esp_err_t tone_get(httpd_req_t *req)
{
    long on;
    char msg[96];
    httpd_resp_set_type(req, "text/plain");
    if (!qint(req, "on", &on)) return httpd_resp_sendstr(req, "usage: /tone?on=1  or  /tone?on=0");
    if (on) {
        const char *err = codec_tone_start();
        snprintf(msg, sizeof(msg), "%s\n", err ? err : "tone playing");
    } else {
        codec_tone_stop();
        snprintf(msg, sizeof(msg), "tone stopping\n");
    }
    return httpd_resp_sendstr(req, msg);
}

static int peak_db(int p)
{
    return p > 0 ? (int)(20.0f * log10f((float)p / 32768.0f)) : -99;
}

// Talk into the mic the whole time this runs (about 10 s): it listens on each codec input in turn.
static esp_err_t micscan_get(httpd_req_t *req)
{
    char out[600];
    int n = 0;
    httpd_resp_set_type(req, "text/plain");
    if (codec_tone_playing()) {
        codec_tone_stop();
        codec_wait_stopped(800);
    }
    const char *err = codec_monitor_start();
    if (err) {
        snprintf(out, sizeof(out), "could not start: %s\n", err);
        return httpd_resp_sendstr(req, out);
    }
    codec_write_reg(0x09, 0x44);              // 12 dB on both channels
    vTaskDelay(pdMS_TO_TICKS(1500));          // let the start-up thump die away
    n += snprintf(out + n, sizeof(out) - n,
                  "Mic input scan (dB below full scale; avg is the steady level)\n");
    int score[2] = {0, 0};
    for (int i = 0; i < 2; i++) {
        codec_set_mic_input(i + 1);
        vTaskDelay(pdMS_TO_TICKS(700));
        codec_stats_reset();
        vTaskDelay(pdMS_TO_TICKS(3000));
        int pl, pr, rl, rr;
        codec_stats_get(&pl, &pr, &rl, &rr);
        score[i] = rl > rr ? rl : rr;
        n += snprintf(out + n, sizeof(out) - n,
                      "input %d:  left avg %d peak %d   right avg %d peak %d\n",
                      i + 1, peak_db(rl), peak_db(pl), peak_db(rr), peak_db(pr));
    }
    int pick = score[1] > score[0] * 2 ? 2 : 1;
    codec_set_mic_input(pick);
    uint8_t v10 = 0xEE;
    codec_read_reg(0x10, &v10);
    n += snprintf(out + n, sizeof(out) - n, "Mic monitor will use input %d. (r10=%02X)\n", pick, v10);
    codec_tone_stop();
    return httpd_resp_sendstr(req, out);
}


static int qdef(httpd_req_t *req, const char *key, int def)
{
    char q[96], v[16];
    if (httpd_req_get_url_query_str(req, q, sizeof(q)) != ESP_OK) return def;
    if (httpd_query_key_value(q, key, v, sizeof(v)) != ESP_OK) return def;
    return atoi(v);
}

// /mic?input=1|2&gain=0..8&src=0..3&inv=0|1&sw=1..16&dc=0|1&mute=0|1&reset=1&raw=1
// Starts the monitor if needed. Every parameter is optional. Reports levels, DC offset, registers.
static esp_err_t mic_get(httpd_req_t *req)
{
    static char out[3000];
    httpd_resp_set_type(req, "text/plain");
    if (!codec_tone_playing()) {
        const char *err = codec_monitor_start();
        if (err) {
            snprintf(out, sizeof(out), "could not start: %s\n", err);
            return httpd_resp_sendstr(req, out);
        }
        vTaskDelay(pdMS_TO_TICKS(500));
    }
    int v;
    if ((v = qdef(req, "input", 0)) == 1 || v == 2) codec_set_mic_input(v);
    if ((v = qdef(req, "gain", -1)) >= 0) codec_set_mic_gain(v);
    codec_mic_config(qdef(req, "src", -1), qdef(req, "inv", -1), qdef(req, "sw", -1),
                     qdef(req, "dc", -1), qdef(req, "mute", -1));
    if (qdef(req, "reset", 1)) codec_stats_reset_all();
    vTaskDelay(pdMS_TO_TICKS(qdef(req, "ms", 2000)));     // stats window: talk into the mic
    int n = 0;
    codec_mic_status(out, sizeof(out));
    n = strlen(out);
    if (qdef(req, "raw", 0)) {
        const int16_t *l, *r;
        if (codec_snapshot(&l, &r)) {
            n += snprintf(out + n, sizeof(out) - n, "raw L,R (256 frames):\n");
            for (int i = 0; i < 256 && n < (int)sizeof(out) - 16; i++)
                n += snprintf(out + n, sizeof(out) - n, "%d,%d\n", l[i], r[i]);
        }
    }
    return httpd_resp_sendstr(req, out);
}

static bool wifi_init_once(void)
{
    if (wifi_ready) return true;
    if (esp_netif_init() != ESP_OK) return false;
    esp_err_t e = esp_event_loop_create_default();
    if (e != ESP_OK && e != ESP_ERR_INVALID_STATE) return false;
    esp_netif_create_default_wifi_ap();
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    if (esp_wifi_init(&cfg) != ESP_OK) return false;
    wifi_ready = true;
    return true;
}

bool ota_start(void)
{
    if (running) return true;
    if (!wifi_init_once()) return false;

    wifi_config_t ap = {0};
    strcpy((char *)ap.ap.ssid, OTA_SSID);
    strcpy((char *)ap.ap.password, OTA_PASS);
    ap.ap.ssid_len = strlen(OTA_SSID);
    ap.ap.channel = 6;
    ap.ap.max_connection = 2;
    ap.ap.authmode = WIFI_AUTH_WPA2_PSK;
    if (esp_wifi_set_mode(WIFI_MODE_AP) != ESP_OK) return false;
    if (esp_wifi_set_config(WIFI_IF_AP, &ap) != ESP_OK) return false;
    if (esp_wifi_start() != ESP_OK) return false;

    httpd_config_t hc = HTTPD_DEFAULT_CONFIG();
    hc.stack_size = 8192;
    hc.max_uri_handlers = 16;
    hc.recv_wait_timeout = 20;
    if (httpd_start(&server, &hc) != ESP_OK) {
        esp_wifi_stop();
        return false;
    }
    httpd_uri_t idx = {.uri = "/", .method = HTTP_GET, .handler = index_get};
    httpd_uri_t upd = {.uri = "/update", .method = HTTP_POST, .handler = update_post};
    httpd_register_uri_handler(server, &idx);
    httpd_register_uri_handler(server, &upd);
    httpd_uri_t rep = {.uri = "/report", .method = HTTP_GET, .handler = report_get};
    httpd_uri_t i2c = {.uri = "/i2c", .method = HTTP_GET, .handler = i2c_get};
    httpd_uri_t gpi = {.uri = "/gpio", .method = HTTP_GET, .handler = gpio_get_handler};
    httpd_uri_t ton = {.uri = "/tone", .method = HTTP_GET, .handler = tone_get};
    httpd_register_uri_handler(server, &rep);
    httpd_register_uri_handler(server, &i2c);
    httpd_register_uri_handler(server, &gpi);
    httpd_register_uri_handler(server, &ton);
    httpd_uri_t msc = {.uri = "/micscan", .method = HTTP_GET, .handler = micscan_get};
    httpd_register_uri_handler(server, &msc);
    httpd_uri_t mic = {.uri = "/mic", .method = HTTP_GET, .handler = mic_get};
    httpd_register_uri_handler(server, &mic);
    running = true;
    return true;
}

void ota_stop(void)
{
    if (!running) return;
    httpd_stop(server);
    esp_wifi_stop();
    running = false;
}

bool ota_running(void) { return running; }
