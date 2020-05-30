#include "webots/webot_worker.h"

#include <stdio.h>
#include <string.h>

#include "util.h"
#include "print.h"
#include "webots/safe.h"
#include "webots/drive.h"

void *webot_worker(void *ptr) {

	arg_struct_t *arg_struct = (arg_struct_t*) ptr;

	// Init communication with webot
	printf("WEBOT_WORKER: Initalizing\n");

	wb_init_com();
	drive_init();

	init_to_ext_msg_t init_data;
	wb_recv_init(&init_data);

	printf("init_data.timestep: %d\n", init_data.timestep);
	printf("init_data.robot_maxspeed: %f\n", init_data.maxspeed);
	printf("init_data.lidar_min_range: %f\n", init_data.lidar_min_range);
	printf("init_data.lidar_max_range: %f\n", init_data.lidar_max_range);
	printf("init_data.target_gps[0]: %f\n", init_data.target_gps[0]);
	printf("init_data.target_gps[1]: %f\n", init_data.target_gps[1]);
	printf("init_data.target_gps[2]: %f\n", init_data.target_gps[2]);

	// Run webot worker
	printf("WEBOT_WORKER: Running\n");

	while (1) {

		/***** 1) Receive from Webots *****/
		wb_to_ext_msg_t external_wb_to_ext;
		memset(&external_wb_to_ext, 0, sizeof(wb_to_ext_msg_t));
		wb_recv(&external_wb_to_ext);

		// print_wb_to_ext(external_wb_to_ext, 0);

		/***** 2) Push message to backend worker *****/
		ext_to_bcknd_msg_t buffer_ext_to_bcknd;
		memset(&buffer_ext_to_bcknd, 0, sizeof(ext_to_bcknd_msg_t));
		webot_format_wb_to_bcknd(&buffer_ext_to_bcknd, external_wb_to_ext, init_data);
		pthread_mutex_lock(arg_struct->ext_to_bcknd_lock);
		memcpy(arg_struct->ext_to_bcknd, &buffer_ext_to_bcknd, sizeof(ext_to_bcknd_msg_t));
		pthread_mutex_unlock(arg_struct->ext_to_bcknd_lock);

		// print_ext_to_bcknd(buffer_ext_to_bcknd, 0);

		/***** 3) Get message from backend worker *****/
		bcknd_to_ext_msg_t buffer_bcknd_to_ext;
		memset(&buffer_bcknd_to_ext, 0, sizeof(bcknd_to_ext_msg_t));
		pthread_mutex_lock(arg_struct->bcknd_to_ext_lock);
		memcpy(&buffer_bcknd_to_ext, arg_struct->bcknd_to_ext, sizeof(bcknd_to_ext_msg_t));
		pthread_mutex_unlock(arg_struct->bcknd_to_ext_lock);

		/***** 4) Prepare and send to Webots *****/
		// TODO: run safety checks
		safety_check(&buffer_bcknd_to_ext);

		// Do all the driving for the bot
		// drive_manual(init_data, buffer_bcknd_to_ext.speed, buffer_bcknd_to_ext.heading);
		drive_automatic(init_data, buffer_bcknd_to_ext.speed, buffer_bcknd_to_ext.heading,
		                           buffer_ext_to_bcknd.speed, buffer_ext_to_bcknd.heading);

		// +++ OLD STUFF +++
		// ext_to_wb_msg_t external_ext_to_wb;
		// memset(&external_ext_to_wb, 0, sizeof(ext_to_wb_msg_t));
		// // webot_format_bcknd_to_wb(&external_ext_to_wb, buffer_bcknd_to_ext, init_data);
		// // print_ext_to_wb(external_ext_to_wb);
		// // printf("WEBOT_WORKER: Sending external_ext_to_wb on ext Controller\n");
		// wb_send(external_ext_to_wb);
	}

}


int webot_format_wb_to_bcknd(ext_to_bcknd_msg_t* ext_to_bcknd, wb_to_ext_msg_t wb_to_ext, init_to_ext_msg_t init_data) {

	// cast sim time and robot speed to float
	ext_to_bcknd->sim_time = (float) wb_to_ext.sim_time;
	ext_to_bcknd->speed = (float) wb_to_ext.current_speed / init_data.maxspeed;

	// calculate projecions for 3D gps/compass data to bcknd format
	// (x, z coorinates represent horizontal plane in webots system)
	ext_to_bcknd->actual_gps[0] = (float) wb_to_ext.actual_gps[0];
	ext_to_bcknd->actual_gps[1] = (float) wb_to_ext.actual_gps[2];

	double heading = heading_in_norm(wb_to_ext.compass[0], wb_to_ext.compass[1], wb_to_ext.compass[2]);
	ext_to_bcknd->heading = (float) heading;

	// TODO set touching according to logic
	// ext_to_bcknd->touching = 0;

	// copy lidar data
	memcpy(&ext_to_bcknd->distance, wb_to_ext.distance, sizeof(float) * DIST_VECS);

	return 0;

}

// This is not up to date anymore
// int webot_format_bcknd_to_wb(ext_to_wb_msg_t* ext_to_wb, bcknd_to_ext_msg_t bcknd_to_ext, init_to_ext_msg_t init_data) {
//
// 	// 0.25 links / 0.5 gerade / 0.75 rechts
// 	ext_to_wb->heading = (bcknd_to_ext.heading - 180) / 180;
// 	ext_to_wb->heading *= -1;
//
// 	// expected -maxspeed / +maxspeed
// 	ext_to_wb->speed = bcknd_to_ext.speed * init_data.maxspeed;
//
// 	return 0;
// }
