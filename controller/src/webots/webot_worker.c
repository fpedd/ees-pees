#include "webots/webot_worker.h"

#include <stdio.h>
#include <string.h>
#include <math.h>

#include "util.h"
#include "print.h"
#include "webots/safe.h"
#include "webots/drive.h"
#include "webots/navi.h"
#include "webots/discr.h"
#include "webots/wb_com.h"
#include "backend/backend_com.h"


void *webot_worker(void *ptr) {

	arg_struct_t *arg_struct = (arg_struct_t*) ptr;

	// Init communication with webot
	printf("WEBOT_WORKER: Initalizing\n");
	wb_init_com();
	drive_init();
	navi_init();

	// Get initalization packet from Robot
	init_to_ext_msg_t init_data;
	wb_recv_init(&init_data);

	// Run webot worker
	printf("WEBOT_WORKER: Running\n");

	int discrete_action_done = 0;
	int action_denied = 0;

	while (1) {

		/***** 1) Receive from Webots *****/
		data_from_wb_msg_t data_from_wb;
		memset(&data_from_wb, 0, sizeof(data_from_wb_msg_t));
		wb_recv(&data_from_wb);


		/***** 2) Push message to backend worker *****/
		data_to_bcknd_msg_t data_to_backend_worker;
		memset(&data_to_backend_worker, 0, sizeof(data_to_bcknd_msg_t));
		webot_format_wb_to_bcknd(&data_to_backend_worker, data_from_wb,
		                         action_denied, discrete_action_done);
		pthread_mutex_lock(arg_struct->itc_data_lock);
		if (arg_struct->itc_data->action_denied == 1) {
			data_to_backend_worker.action_denied = 1;
		}
		int touching = arg_struct->itc_data->touching;
		if (touching == -1) {
			data_to_backend_worker.touching = -1;
		} else if (touching > 0) {
			data_to_backend_worker.touching += touching;
		}

		memcpy(arg_struct->itc_data, &data_to_backend_worker, sizeof(data_to_bcknd_msg_t));
		pthread_mutex_unlock(arg_struct->itc_data_lock);


		/***** 3) Get message from backend worker *****/
		cmd_from_bcknd_msg_t cmd_from_backend_worker;
		memset(&cmd_from_backend_worker, 0, sizeof(cmd_from_bcknd_msg_t));
		pthread_mutex_lock(arg_struct->itc_cmd_lock);
		memcpy(&cmd_from_backend_worker, arg_struct->itc_cmd, sizeof(cmd_from_bcknd_msg_t));
		pthread_mutex_unlock(arg_struct->itc_cmd_lock);


		/***** 4) Calculate next command *****/
		cmd_to_wb_msg_t cmd_to_wb;
		memset(&cmd_to_wb, 0, sizeof(cmd_to_wb_msg_t));

		static int start = 1;
		// check if we should do a continous or discrete action
		// TODO: also reset PID controller when switching over
		if (cmd_from_backend_worker.move == NONE) {
			drive(&cmd_to_wb, cmd_from_backend_worker, data_to_backend_worker, init_data);
			start = 1;

		} else {
			discrete_action_done = discr_step(&cmd_to_wb, cmd_from_backend_worker, data_to_backend_worker, init_data, start, action_denied);
			start = 0;
		}

		print_cmd_from_bcknd(cmd_from_backend_worker);

		// TODO: disable/enable according to safety flag from backend
		/***** 5) Do safety checks if we arent using grid moves*****/
		// In grid moves safety is handled by the backend, and we don't want to interfere
		action_denied = safety_check(init_data, data_from_wb, &cmd_to_wb);


		/***** 6) Send command to robot *****/
		wb_send(cmd_to_wb);
	}

	wb_close();
	return NULL;
}


int webot_format_wb_to_bcknd(data_to_bcknd_msg_t* data_to_bcknd,
                             data_from_wb_msg_t data_from_wb,
                             int action_denied,
                             unsigned int discrete_action_done) {

	// cast sim time and robot speed to float, scale speed to [-1, 1]
	data_to_bcknd->sim_time = (float) data_from_wb.sim_time;
	data_to_bcknd->speed = (float) speed_with_dir(data_from_wb) / 0.29;

	// Calculate projections from 3D gps/compass data to backend format
	// (x, z coorinates represent horizontal plane in webots system)
	data_to_bcknd->actual_gps[0] = (float) data_from_wb.actual_gps[0];
	data_to_bcknd->actual_gps[1] = (float) data_from_wb.actual_gps[2];

	double heading = heading_in_norm(data_from_wb.compass[0], data_from_wb.compass[1], data_from_wb.compass[2]);

	data_to_bcknd->heading = (float) heading;
	data_to_bcknd->steer_angle = (float) data_from_wb.steer_angle;

	// Set touching flag and action_denied if the safety intervened critcally
	if (check_for_tipover(data_from_wb) != 0) {
		data_to_bcknd->touching = -1;
	} else {
		data_to_bcknd->touching = touching(data_from_wb);
	}
	data_to_bcknd->action_denied = action_denied;

	// Set flag to tell backend that the discrete step was completed
	data_to_bcknd->discr_act_done = discrete_action_done;

	// Copy lidar data
	memcpy(&data_to_bcknd->distance, data_from_wb.distance, sizeof(float) * DIST_VECS);

	return 0;
}


double heading_in_norm(double x, double y, double z) {

	double heading = -atan2(z, x) / M_PI;

	// Check for invalid heading
	if (heading < -1.0 || heading > 1.0) {
		fprintf(stderr, "WEBOT_WORKER: Error calculating heading. Heading = %f. y= %f\n", heading, y);
	}

	return heading;
}

/* Add the movement direction to the directionless speed the webot sensor provides
 */
float speed_with_dir(data_from_wb_msg_t data_from_wb) {

	static double last_gps[2] = {data_from_wb.actual_gps[0], data_from_wb.actual_gps[2]};

	// Get normalized trajectory vector from gps
	double len = sqrt(pow(data_from_wb.actual_gps[0], 2)
	                + pow(data_from_wb.actual_gps[2], 2));
	double traj[2];
	traj[0] = (data_from_wb.actual_gps[0] - last_gps[0]) / len;
	traj[1] = (data_from_wb.actual_gps[2] - last_gps[1]) / len;

	// Safe prev gps
	last_gps[0] = data_from_wb.actual_gps[0];
	last_gps[1] = data_from_wb.actual_gps[2];

	// Get heading from compass data (already normalized)
	double comp[2];
	comp[0] = data_from_wb.compass[2];
	comp[1] = data_from_wb.compass[0];

	// Dot product
	double dot =  0;
	for (int i=0; i<2; i++) {
		dot += traj[i] * comp[i];
	}

	// Adjust speed direction accordingly and cast to float
	return (float)(dot >= 0 ? data_from_wb.current_speed : -data_from_wb.current_speed);
}
