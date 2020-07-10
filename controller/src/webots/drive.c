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
	last_time = 0.0;
	pid_init(&speed_pid, 3.0, 0.0, 0.0, -1.0, 1.0, 0.0, NORM);
	pid_init(&heading_pid, 5.0, 0.0, 0.0, -1.0, 1.0, 0.0, WRAP);
	return 0;
}

int drive(cmd_to_wb_msg_t *cmd_to_wb, cmd_from_bcknd_msg_t cmd_from_bcknd,
          data_to_bcknd_msg_t data_to_bcknd, init_to_ext_msg_t init_data) {

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

	memset(cmd_to_wb, 0, sizeof(cmd_to_wb_msg_t));
	cmd_to_wb->speed = speed * init_data.maxspeed * -0.5;
	cmd_to_wb->heading = heading;

	// printf("DRIVE MAN: speed %f, heading %f \n", cmd_to_wb.speed, cmd_to_wb.heading);

	return 0;
}

int drive_automatic(cmd_to_wb_msg_t *cmd_to_wb, init_to_ext_msg_t init_data,
                    float set_speed, float set_heading,
                    float act_speed, float act_heading,
                    float curr_time) {

	// ensure that time difference is not to big and not zero when starting
	if (last_time == 0.0) {
		last_time = curr_time;
		return 0;
	}

	// no real need for pid controller here yet
	(void) act_speed;
	float com_speed = set_speed;
	// float com_speed = 0;
	// pid_run(&speed_pid, curr_time - last_time, set_speed, act_speed, &com_speed);
	// printf("DRIVE AUTO: speed set: %f  act: %f com: %f \n", set_speed, act_speed, com_speed);

	float com_heading = 0;
	pid_run(&heading_pid, curr_time - last_time, set_heading, act_heading, &com_heading);

	// TODO: fix controller when driving backwards
	// this should be act_speed and not set speed
	printf("DRIVE: set_speed: %f , act_speed: %f \n", set_speed, act_speed);
	// if (act_speed < 0.0) {
	if (set_speed < 0.0) {
		pid_update(&heading_pid, 3.0, 0.0, 0.0);
		com_heading *= -1.0;
	} else {
		pid_update(&heading_pid, 5.0, 0.0, 0.0);
	}

	// printf("DRIVE AUTO: heading set: %f  act: %f com: %f \n", set_heading, act_heading, com_heading);

	last_time = curr_time;

	memset(cmd_to_wb, 0, sizeof(cmd_to_wb_msg_t));
	cmd_to_wb->speed = com_speed * init_data.maxspeed * -0.5;
	cmd_to_wb->heading = com_heading;

	// printf("DRIVE AUTO: speed %f, heading %f \n", cmd_to_wb.speed, cmd_to_wb.heading);

	return 0;
}
