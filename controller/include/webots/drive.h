#ifndef DRIVE_H
#define DRIVE_H

#include "webots/wb_com.h"
#include "backend/backend_com.h"

int drive_init();

int drive(ext_to_wb_msg_t *ext_to_wb, bcknd_to_ext_msg_t bcknd_to_ext,
          ext_to_bcknd_msg_t ext_to_bcknd, init_to_ext_msg_t init_data);

int drive_manual(ext_to_wb_msg_t *ext_to_wb, init_to_ext_msg_t init_data,
                 float speed, float heading);

int drive_automatic(ext_to_wb_msg_t *ext_to_wb, init_to_ext_msg_t init_data,
                    float set_speed, float set_heading,
                    float act_speed, float act_heading,
                    float curr_time);

#endif // DRIVE_H
