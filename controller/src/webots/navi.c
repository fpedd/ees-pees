#include "webots/navi.h"

#include <stdio.h>
#include <string.h>
#include <math.h>
#include <float.h>

#include "util.h"
#include "webots/pid.h"
#include "webots/drive.h"
#include "backend/backend_com.h"

static double last_time;
static pid_ctrl_t pos_pid;

int navi_init() {
	last_time = 0.0;
	pid_init(&pos_pid, 1.8,   // k_p
	                   0.0,   // k_i
	                   0.0,   // k_d
	                  -1.0,   // min
	                   1.0,   // max
	                   0.01,  // deadband
	                   NORM); // special function?

	return 0;
}

// this function can be used to tell the robot to drive to dest[] coorinates
int navigate(cmd_to_wb_msg_t *cmd_to_wb, data_to_bcknd_msg_t data_to_bcknd,
             init_to_ext_msg_t init_data, float dest[]) {

	// ensure that time difference is not to big and not zero when starting
	if (last_time == 0.0) {
		last_time = data_to_bcknd.sim_time;
		return 0;
	}

	// get the heading we need to drive in
	float com_heading = navi_get_heading(data_to_bcknd.actual_gps, dest);

	// get the actual distance to the target field
	float act_distance = navi_get_distance(data_to_bcknd.actual_gps, dest);

	// run the pid controller for speed control
	float com_speed = 0;
	int active = pid_run(&pos_pid, data_to_bcknd.sim_time - last_time, 0, act_distance, &com_speed);

	// should we drive backwards of forwards?
	if (navi_check_back(data_to_bcknd.heading, com_heading)) {
		com_speed *= 1.0;
		com_heading = navi_inv_heading(com_heading);
	} else {
		com_speed *= -1.0;
	}

	// command robot to drive to the target
	drive_automatic(cmd_to_wb, init_data,
	                com_speed, com_heading,
	                data_to_bcknd.speed, data_to_bcknd.heading,
	                data_to_bcknd.sim_time);

	return active;
}

int navi_check_back(float start_heading, float dest_heading) {

	float diff = fabs(start_heading - dest_heading);

	if (diff > 1) {
		diff = fabs(diff - 2);
	}

	if (diff > 0.5) {
		return 1;
	} else {
		return 0;
	}
}

float navi_get_heading(float start[], float dest[]) {

	// weird coorinate system in webots...
	float dx = start[0] - dest[0];
	float dy = dest[1] - start[1];
	float he = atan2(dx, dy) / M_PI;

	return he;
}

float navi_get_distance(float start[], float dest[]) {

	float dx = dest[0] - start[0];
	float dy = dest[1] - start[1];
	float di = sqrt(pow(dx, 2) + pow(dy, 2));

	return di;
}

float navi_inv_heading(float heading) {

	if (heading > 0) {
		return heading - 1.0;
	} else {
		return heading + 1.0;
	}
}
