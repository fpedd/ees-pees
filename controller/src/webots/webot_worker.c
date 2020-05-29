#include "webots/webot_worker.h"

#include <stdio.h>
#include <string.h>

#include "util.h"
#include "print.h"

void webot_worker(arg_struct_t *arg_struct) {

	// Init communication with webot
	printf("WEBOT_WORKER: Initalizing\n");

	// init structs for webot <--> ext controller messages
	wb_to_ext_msg_t external_wb_to_ext;
	memset(&external_wb_to_ext, 0, sizeof(wb_to_ext_msg_t));

	ext_to_wb_msg_t external_ext_to_wb;
	memset(&external_ext_to_wb, 0, sizeof(ext_to_wb_msg_t));

	wb_init_com();

	init_to_ext_msg_t init_data;
	wb_recv_init(&init_data);

	printf("init_data.timestep: %d\n", init_data.timestep);
	printf("init_data.robot_maxspeed: %f\n", init_data.maxspeed);
	printf("init_data.lidar_min_range: %f\n", init_data.lidar_min_range);
	printf("init_data.lidar_max_range: %f\n", init_data.lidar_max_range);
	printf("init_data.target_gps[0]: %f\n", init_data.target_gps[0]);
	printf("init_data.target_gps[1]: %f\n", init_data.target_gps[1]);
	printf("init_data.target_gps[2]: %f\n", init_data.target_gps[2]);

	printf("WEBOT_WORKER: Running\n");

	while (1) {

		// printf("WEBOT_WORKER: receiving external_wb_to_ext on ext Controller\n");
		wb_recv(&external_wb_to_ext);

		// printf("========WB_WORKER: RECEIVED=========\n");
		// print_wb_to_ext(external_wb_to_ext);
		// printf("====================================\n");

		ext_to_bcknd_msg_t buffer_ext_to_bcknd;
		memset(&buffer_ext_to_bcknd, 0, sizeof(ext_to_bcknd_msg_t));

		// format to internal_ext_to_bcknd_t
		webot_format_wb_to_bcknd(&buffer_ext_to_bcknd, external_wb_to_ext, init_data);

		// printf("WEBOT_WORKER: ======== Compare formatted shit=========\n");
		// print_wb_to_ext(external_wb_to_ext, 1);
		// print_ext_to_bcknd(buffer_ext_to_bcknd, 1);
		// print_diff_distance(external_wb_to_ext, buffer_ext_to_bcknd);


		pthread_mutex_lock(arg_struct->ext_to_bcknd_lock);
		memcpy(arg_struct->ext_to_bcknd, &buffer_ext_to_bcknd, sizeof(ext_to_bcknd_msg_t));
		pthread_mutex_unlock(arg_struct->ext_to_bcknd_lock);

		bcknd_to_ext_msg_t buffer_bcknd_to_ext;
		memset(&buffer_bcknd_to_ext, 0, sizeof(bcknd_to_ext_msg_t));

		pthread_mutex_lock(arg_struct->bcknd_to_ext_lock);
		memcpy(&buffer_bcknd_to_ext, arg_struct->bcknd_to_ext, sizeof(bcknd_to_ext_msg_t));
		pthread_mutex_unlock(arg_struct->bcknd_to_ext_lock);

		// TODO: run safety and control loops
		// TODO: use funtions form the drive.c / drive.h to convert to webots format

		// Fill ext_to_wb struct
		webot_format_bcknd_to_wb(&external_ext_to_wb, buffer_bcknd_to_ext, init_data);

		print_ext_to_wb(external_ext_to_wb);



		// printf("WEBOT_WORKER: Sending external_ext_to_wb on ext Controller\n");
		wb_send(external_ext_to_wb);
	}

}


int webot_format_wb_to_bcknd(ext_to_bcknd_msg_t* ext_to_bcknd, wb_to_ext_msg_t wb_to_ext, init_to_ext_msg_t init_data) {

	// cast sim time and robot speed to float
	ext_to_bcknd->sim_time = (float) wb_to_ext.sim_time;
	ext_to_bcknd->speed = (float) wb_to_ext.current_speed / init_data.maxspeed;

	// TODO where does the target come from?

	// calculate projecions for 3D gps/compass data to bcknd format
	// (x, z coorinates represent horizontal plane in webots system)
	ext_to_bcknd->actual_gps[0] = (float) wb_to_ext.actual_gps[0];
	ext_to_bcknd->actual_gps[1] = (float) wb_to_ext.actual_gps[2];

	double heading = heading_in_degrees(wb_to_ext.compass[0], wb_to_ext.compass[1], wb_to_ext.compass[2]);
	ext_to_bcknd->heading = (float) heading;

	// TODO set touching according to logic

	// copy lidar data
	memcpy(&ext_to_bcknd->distance, wb_to_ext.distance, sizeof(float) * DIST_VECS);

	return 0;

}

int webot_format_bcknd_to_wb(ext_to_wb_msg_t* ext_to_wb, bcknd_to_ext_msg_t bcknd_to_ext, init_to_ext_msg_t init_data) {

	ext_to_wb->heading = (bcknd_to_ext.heading - 180) / 180;
	ext_to_wb->heading *= -1;

	ext_to_wb->speed = bcknd_to_ext.speed * init_data.maxspeed;

	return 0;
}
