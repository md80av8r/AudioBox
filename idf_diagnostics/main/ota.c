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
    "x.send(f)}</script>";

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
    hc.recv_wait_timeout = 20;
    if (httpd_start(&server, &hc) != ESP_OK) {
        esp_wifi_stop();
        return false;
    }
    httpd_uri_t idx = {.uri = "/", .method = HTTP_GET, .handler = index_get};
    httpd_uri_t upd = {.uri = "/update", .method = HTTP_POST, .handler = update_post};
    httpd_register_uri_handler(server, &idx);
    httpd_register_uri_handler(server, &upd);
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
