#include "webots/webot_worker.h"

#include <stdio.h>
#include <string.h>

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
	// print_silhouette();

	wb_init_com();
	drive_init();
	navi_init();
	// safety_init();

	init_to_ext_msg_t init_data;
	wb_recv_init(&init_data);
	// print_init_data(init_data);

	// Run webot worker
	printf("WEBOT_WORKER: Running\n");

	int discrete_action_done = 0;
	int action_denied = 0;

	while (1) {

		/***** 1) Receive from Webots *****/
		data_from_wb_msg_t data_from_wb;
		memset(&data_from_wb, 0, sizeof(data_from_wb_msg_t));
		wb_recv(&data_from_wb);

		// print_data_from_wb(data_from_wb, 0);

		/***** 2) Push message to backend worker *****/
		data_to_bcknd_msg_t data_to_backend_worker;
		memset(&data_to_backend_worker, 0, sizeof(data_to_bcknd_msg_t));
		webot_format_wb_to_bcknd(&data_to_backend_worker, data_from_wb, init_data,
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

		// print_data_to_bcknd(data_to_backend_worker, 0);
		// printf("WEBOT_WORKER: backend link_qual %f \n", link_qualitiy(0));

		/***** 3) Get message from backend worker *****/
		cmd_from_bcknd_msg_t cmd_from_backend_worker;
		memset(&cmd_from_backend_worker, 0, sizeof(cmd_from_bcknd_msg_t));
		pthread_mutex_lock(arg_struct->itc_cmd_lock);
		memcpy(&cmd_from_backend_worker, arg_struct->itc_cmd, sizeof(cmd_from_bcknd_msg_t));
		pthread_mutex_unlock(arg_struct->itc_cmd_lock);

		// print_cmd_from_bcknd(cmd_from_backend_worker);

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

		/***** 5) Do safety checks *****/
		action_denied = safety_check(init_data, data_from_wb, &cmd_to_wb);

		/***** 6) Send command to robot *****/
		wb_send(cmd_to_wb);

	}

	return NULL;
}


int webot_format_wb_to_bcknd(data_to_bcknd_msg_t* data_to_bcknd,
                             data_from_wb_msg_t data_from_wb,
                             init_to_ext_msg_t init_data,
                             int action_denied,
                             unsigned int discrete_action_done) {

	// cast sim time and robot speed to float
	data_to_bcknd->sim_time = (float) data_from_wb.sim_time;
	data_to_bcknd->speed = (float) speed_with_dir(data_from_wb) / init_data.maxspeed;

	// calculate projecions for 3D gps/compass data_to_bcknd to bcknd format
	// (x, z coorinates represent horizontal plane in webots system)
	data_to_bcknd->actual_gps[0] = (float) data_from_wb.actual_gps[0];
	data_to_bcknd->actual_gps[1] = (float) data_from_wb.actual_gps[2];

	double heading = heading_in_norm(data_from_wb.compass[0], data_from_wb.compass[1], data_from_wb.compass[2]);
	data_to_bcknd->heading = (float) heading;
	data_to_bcknd->steer_angle = (float) data_from_wb.steer_angle;

	if (check_for_tipover(data_from_wb) != 0) {
		data_to_bcknd->touching = -1;
	} else {
		data_to_bcknd->touching = touching(data_from_wb);
	}

	data_to_bcknd->action_denied = action_denied;

	data_to_bcknd->discr_act_done = discrete_action_done;

	// copy lidar data_to_bcknd
	memcpy(&data_to_bcknd->distance, data_from_wb.distance, sizeof(float) * DIST_VECS);

	return 0;

}
