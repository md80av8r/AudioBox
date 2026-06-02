// ui.h — screen declarations
#pragma once
#include <lvgl.h>

// Each screen returns its root lv_obj_t and registers any timers/handlers
lv_obj_t* ui_home_create();   // clock + status idle screen
lv_obj_t* ui_menu_create();   // 3×2 tile main menu
lv_obj_t* ui_audio_create();  // audio mixer / volume

// Navigate to a screen with a slide animation
void ui_goto(lv_obj_t* screen);

// Update tick (called from ui_task every ~100ms) — pulls g_state into widgets
void ui_tick();
