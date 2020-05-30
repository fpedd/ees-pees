#ifndef DRIVE_H
#define DRIVE_H

#include "webots/wb_com.h"

int drive_init();

int drive_manual(init_to_ext_msg_t init_data, float speed, float heading);

int drive_automatic(init_to_ext_msg_t init_data,
                    float set_speed,
                    float set_heading,
                    float act_speed,
                    float act_heading);

#endif // DRIVE_H
