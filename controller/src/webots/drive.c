#include "webots/drive.h"

#include <stdio.h>
#include <string.h>
#include <math.h>
#include <float.h>

#include "util.h"
#include "webots/pid.h"
#include "backend/backend_com.h"

static double last_time;
static pid_ctrl_t speed_pid;
static pid_ctrl_t heading_pid;

int drive_init() {

	// Initialize time variable
	last_time = 0.0;

	// Initialize PID for speed control
	pid_init(&speed_pid, 3.0, 0.0, 0.0, -1.0, 1.0, 0.0, NORM);

	// Initialize PID for heading control using warp around logic
	pid_init(&heading_pid, 5.0, 0.0, 0.0, -1.0, 1.0, 0.0, WRAP);

	return 0;
}

int drive(cmd_to_wb_msg_t *cmd_to_wb, cmd_from_bcknd_msg_t cmd_from_bcknd,
          data_to_bcknd_msg_t data_to_bcknd, init_to_ext_msg_t init_data) {

	// Check if we should drive in STEERING (Manual) or HEADING (Automatic) mode
	if (cmd_from_bcknd.dir_type == STEERING) {
		drive_manual(cmd_to_wb, init_data,
		             cmd_from_bcknd.speed, cmd_from_bcknd.heading);
	} else {
		drive_automatic(cmd_to_wb, init_data,
		                cmd_from_bcknd.speed, cmd_from_bcknd.heading,
		                data_to_bcknd.speed, data_to_bcknd.heading,
		                data_to_bcknd.sim_time);
	}

	return 0;
}

int drive_manual(cmd_to_wb_msg_t *cmd_to_wb, init_to_ext_msg_t init_data,
                 float speed, float heading) {

	// Set command variables that will be send to robot
	memset(cmd_to_wb, 0, sizeof(cmd_to_wb_msg_t));
	cmd_to_wb->speed = speed * init_data.maxspeed * -0.5;
	cmd_to_wb->heading = heading;

	return 0;
}

int drive_automatic(cmd_to_wb_msg_t *cmd_to_wb, init_to_ext_msg_t init_data,
                    float set_speed, float set_heading,
                    float act_speed, float act_heading,
                    float curr_time) {

	// Ensure that time difference is not to big and not zero when starting
	if (last_time == 0.0) {
		last_time = curr_time;
		return 0;
	}

	// No real need for pid controller here yet (motors have (almost) ideal transfer function)
	(void) act_speed;
	float com_speed = set_speed;
	// float com_speed = 0;

	// Use PID to control robots heading
	float com_heading = 0;
	pid_run(&heading_pid, curr_time - last_time, set_heading, act_heading, &com_heading);

	// Dynamics of robot change when going backwards, adjust PID accordingly
	if (set_speed < 0.0) {
		pid_update(&heading_pid, 3.0, 0.0, 0.0);
		com_heading *= -1.0;
	} else {
		pid_update(&heading_pid, 5.0, 0.0, 0.0);
	}

	// Update time
	last_time = curr_time;

	// Set command variables that will be send to robot
	memset(cmd_to_wb, 0, sizeof(cmd_to_wb_msg_t));
	cmd_to_wb->speed = com_speed * init_data.maxspeed * -0.5;
	cmd_to_wb->heading = com_heading;

	return 0;
}
