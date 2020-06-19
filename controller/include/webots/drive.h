#ifndef DRIVE_H
#define DRIVE_H

#include "webots/wb_com.h"
#include "backend/backend_com.h"

int drive_init();

int drive(cmd_to_wb_msg_t *cmd_to_wb, cmd_to_ext_msg_t cmd_to_ext,
          data_to_bcknd_msg_t data_to_bcknd, init_to_ext_msg_t init_data);

int drive_manual(cmd_to_wb_msg_t *cmd_to_wb, init_to_ext_msg_t init_data,
                 float speed, float heading);

int drive_automatic(cmd_to_wb_msg_t *cmd_to_wb, init_to_ext_msg_t init_data,
                    float set_speed, float set_heading,
                    float act_speed, float act_heading,
                    float curr_time);

#endif // DRIVE_H
