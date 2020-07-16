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

	// Initialize time variable
	last_time = 0.0;

	// The PID was tuned in a way that minimizes rise time and avoids overshoot
	// Since we dont encounter any significant disturbance from the environment
	// there was no real need to include I or D gains at this point

	// Initialize PID for navigation speed control using a deadband
	pid_init(&pos_pid, 4.5,   // k_p
	                   0.0,   // k_i
	                   0.0,   // k_d
	                  -1.0,   // min
	                   1.0,   // max
	                   0.03,  // deadband
	                   NORM); // special functions deactivated

	return 0;
}

// This function can be used to tell the robot to drive to dest[] coorinates
int navigate(cmd_to_wb_msg_t *cmd_to_wb, data_to_bcknd_msg_t data_to_bcknd,
             init_to_ext_msg_t init_data, float dest[], int reset) {

	// If needed, reset the controllers internal state
	if (reset == 1) {
		pid_reset(&pos_pid);
	}

	// Ensure that time difference is not to big and not zero when starting
	if (last_time == 0.0) {
		last_time = data_to_bcknd.sim_time;
		return 0;
	}

	// Get the heading we need to drive in
	float com_heading = navi_get_heading(data_to_bcknd, dest);

	// Get the actual distance to the target field
	float act_distance = navi_get_distance(data_to_bcknd, dest);

	// Run PID for navigation speed control
	float com_speed = 0;
	int done = pid_run(&pos_pid, data_to_bcknd.sim_time - last_time, 0, act_distance, &com_speed);

	// Should we drive backwards of forwards?
	if (navi_check_back(data_to_bcknd.heading, com_heading)) {
		com_speed *= 1.0;
		com_heading = navi_inv_heading(com_heading);
	} else {
		com_speed *= -1.0;
	}

	// Command robot to drive to the target
	drive_automatic(cmd_to_wb, init_data,
	                com_speed, com_heading,
	                data_to_bcknd.speed, data_to_bcknd.heading,
	                data_to_bcknd.sim_time, reset);

	return done;
}

int navi_check_back(float start_heading, float dest_heading) {

	// Get the absolute heading difference
	float diff = fabs(start_heading - dest_heading);

	// If bigger than 1, use wrap around logic
	if (diff > 1.0) {
		diff = fabs(diff - 2.0);
	}

	// Check whether we should drive backwards or forwards
	if (diff > 0.5) {
		// Backwards is faster
		return 1;
	} else {
		// Forwards is faster
		return 0;
	}
}

float navi_get_heading(data_to_bcknd_msg_t data_to_bcknd, float dest[]) {

	// Get the two distance vectors and use arctan to calculate the correct angle
	// Weird coorinate system in webots...
	float dx = data_to_bcknd.actual_gps[0] - dest[0];
	float dy = dest[1] - data_to_bcknd.actual_gps[1];
	float he = atan2(dx, dy) / M_PI;

	return he;
}

float navi_get_distance(data_to_bcknd_msg_t data_to_bcknd, float dest[]) {

	// Get the two distance vectors and do pythagorean
	float dx = dest[0] - data_to_bcknd.actual_gps[0];
	float dy = dest[1] - data_to_bcknd.actual_gps[1];
	float di = sqrt(pow(dx, 2) + pow(dy, 2));

	return di;
}

float navi_inv_heading(float heading) {

	// Invert the heading
	if (heading > 0.0) {
		return heading - 1.0;
	} else {
		return heading + 1.0;
	}
}
