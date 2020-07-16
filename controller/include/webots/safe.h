#ifndef SAFE_H
#define SAFE_H

#include "webots/wb_com.h"
#include "backend/backend_com.h"

enum direction {
	FORWARDS = -1,
	STOPPED = 0,
	BACKWARDS = 1,
};

int safety_check(init_to_ext_msg_t init_data, data_from_wb_msg_t data_from_wb,
	             cmd_to_wb_msg_t* cmd_to_wb);

int check_hitbox(float *distance, float *hitbox);

int calc_hitbox(float *hitbox, int angle);

int predict_angle(int direction, double speed, double steering);

int too_close_to_obstacle(float *distance, double cmd_speed);

int subtract_silhouette(float *distance);

float condense_data(float *distance, int width, int angle);

int compare_direction(double *vec1, double *vec2, int size);

int touching(data_from_wb_msg_t data_from_wb);

int check_for_tipover(data_from_wb_msg_t data_from_wb);


#endif // SAFE_H
