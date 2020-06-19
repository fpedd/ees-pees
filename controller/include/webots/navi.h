#ifndef NAVI_H
#define NAVI_H

#include "webots/wb_com.h"
#include "backend/backend_com.h"

int navi_init();

int navigate(cmd_to_wb_msg_t *cmd_to_wb, data_to_bcknd_msg_t data_to_bcknd,
             init_to_ext_msg_t init_data, float dest[]);

int navi_check_back(float start_heading, float dest_heading);

float navi_get_heading(data_to_bcknd_msg_t data_to_bcknd, float dest[]);

float navi_get_distance(data_to_bcknd_msg_t data_to_bcknd, float dest[]);

float navi_inv_heading(float heading);

#endif // NAVI_H
