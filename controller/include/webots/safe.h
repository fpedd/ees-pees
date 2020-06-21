#ifndef SAFE_H
#define SAFE_H

// This will contain all code to check if the robot collides with some object.
// This will then also provide funtions that help to keep the robot safe.

#include "webots/wb_com.h"
#include "backend/backend_com.h"



int safety_check(init_to_ext_msg_t init_data, data_from_wb_msg_t data_from_wb,
	             data_to_bcknd_msg_t* data_to_bcknd, cmd_to_wb_msg_t* cmd_to_wb);

int direction_from_speed(double speed);

int subtract_silhouette(float *distance);

float condense_data(float *distance, int direction);

int touching(data_from_wb_msg_t data_from_wb);

int check_for_tipover(data_from_wb_msg_t data_from_wb);


#endif // SAFE_H
