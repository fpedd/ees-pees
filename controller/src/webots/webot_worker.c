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

	wb_init_com();
	drive_init();
	navi_init();

	init_to_ext_msg_t init_data;
	wb_recv_init(&init_data);
	// print_init_data(init_data);

	// Run webot worker
	printf("WEBOT_WORKER: Running\n");

	int discrete_action_done = 0;
	int action_denied = 0;

	while (1) {

		/***** 1) Receive from Webots *****/
		wb_to_ext_msg_t wb_to_ext;
		memset(&wb_to_ext, 0, sizeof(wb_to_ext_msg_t));
		wb_recv(&wb_to_ext);

		// print_wb_to_ext(wb_to_ext, 0);

		/***** 2) Push message to backend worker *****/
		ext_to_bcknd_msg_t ext_to_bcknd;
		memset(&ext_to_bcknd, 0, sizeof(ext_to_bcknd_msg_t));
		webot_format_wb_to_bcknd(&ext_to_bcknd, wb_to_ext, init_data,
		                         action_denied, discrete_action_done);
		pthread_mutex_lock(arg_struct->ext_to_bcknd_lock);
		memcpy(arg_struct->ext_to_bcknd, &ext_to_bcknd, sizeof(ext_to_bcknd_msg_t));
		pthread_mutex_unlock(arg_struct->ext_to_bcknd_lock);

		// print_ext_to_bcknd(ext_to_bcknd, 0);
		// printf("WEBOT_WORKER: backend link_qual %f \n", link_qualitiy(0));

		/***** 3) Get message from backend worker *****/
		bcknd_to_ext_msg_t bcknd_to_ext;
		memset(&bcknd_to_ext, 0, sizeof(bcknd_to_ext_msg_t));
		pthread_mutex_lock(arg_struct->bcknd_to_ext_lock);
		memcpy(&bcknd_to_ext, arg_struct->bcknd_to_ext, sizeof(bcknd_to_ext_msg_t));
		pthread_mutex_unlock(arg_struct->bcknd_to_ext_lock);

		// print_bcknd_to_ext(bcknd_to_ext);

		/***** 4) Prepare and send to Webots *****/
		// TODO: implement safety checks
		action_denied = safety_check(init_data, ext_to_bcknd, &bcknd_to_ext);

		ext_to_wb_msg_t ext_to_wb;
		memset(&ext_to_wb, 0, sizeof(ext_to_wb_msg_t));

		static int start = 1;
		// check if we should do a continous or discrete action
		// TODO: also reset PID controller when switching over
		if (bcknd_to_ext.move == NONE) {
			drive(&ext_to_wb, bcknd_to_ext, ext_to_bcknd, init_data);
			start = 1;
		} else {
			discrete_action_done = discr_step(&ext_to_wb, bcknd_to_ext, ext_to_bcknd, init_data, start);
			start = 0;
		}

		// print_ext_to_wb(ext_to_wb);
		wb_send(ext_to_wb);

	}

	return NULL;
}


int webot_format_wb_to_bcknd(ext_to_bcknd_msg_t* ext_to_bcknd,
                             wb_to_ext_msg_t wb_to_ext,
                             init_to_ext_msg_t init_data,
                             unsigned int action_denied,
                             unsigned int discrete_action_done) {

	// cast sim time and robot speed to float
	ext_to_bcknd->sim_time = (float) wb_to_ext.sim_time;
	ext_to_bcknd->speed = (float) wb_to_ext.current_speed / init_data.maxspeed;

	// calculate projecions for 3D gps/compass data to bcknd format
	// (x, z coorinates represent horizontal plane in webots system)
	ext_to_bcknd->actual_gps[0] = (float) wb_to_ext.actual_gps[0];
	ext_to_bcknd->actual_gps[1] = (float) wb_to_ext.actual_gps[2];

	double heading = heading_in_norm(wb_to_ext.compass[0], wb_to_ext.compass[1], wb_to_ext.compass[2]);
	ext_to_bcknd->heading = (float) heading;

	if (check_for_tipover(wb_to_ext) != 0) {
		ext_to_bcknd->touching = -1;
	} else {
		ext_to_bcknd->touching = touching(wb_to_ext.distance);
	}

	ext_to_bcknd->action_denied = action_denied;

	ext_to_bcknd->discr_act_done = discrete_action_done;

	// copy lidar data
	memcpy(&ext_to_bcknd->distance, wb_to_ext.distance, sizeof(float) * DIST_VECS);

	return 0;

}
