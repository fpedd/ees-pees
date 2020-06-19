#include "print.h"

#include <stdio.h>

#include "webots/wb_com.h"
#include "backend/backend_com.h"

void print_diff_distance(data_to_ext_msg_t data_to_ext, data_to_bcknd_msg_t data_to_bcknd) {

	for (int i = 0; i < DIST_VECS; i++){
		if (data_to_ext.distance[i] != data_to_bcknd.distance[i]){
			printf("WEBOT_WORKER: data_to_ext.distance[%d] = %f  data_to_bcknd.distance[%d] = %f\n", i, data_to_ext.distance[i], i, data_to_bcknd.distance[i]);
		}
	}

}

void print_data_to_ext(data_to_ext_msg_t data_to_ext, int print_distance) {
	printf("WEBOT_WORKER: =================== data_to_ext ===================\n");
	printf("WEBOT_WORKER: sim_time:      %f\n", data_to_ext.sim_time);
	printf("WEBOT_WORKER: current_speed: %f\n", data_to_ext.current_speed);
	printf("WEBOT_WORKER: actual_gps[0]: %f\n", data_to_ext.actual_gps[0]);
	printf("WEBOT_WORKER: actual_gps[1]: %f\n", data_to_ext.actual_gps[1]);
	printf("WEBOT_WORKER: actual_gps[2]: %f\n", data_to_ext.actual_gps[2]);
	printf("WEBOT_WORKER: compass[0]:    %f\n", data_to_ext.compass[0]);
	printf("WEBOT_WORKER: compass[1]:    %f\n", data_to_ext.compass[1]);
	printf("WEBOT_WORKER: compass[2]:    %f\n", data_to_ext.compass[2]);

	for (int i = 0; i < print_distance; i++){
		printf("WEBOT_WORKER: data_to_ext.distance[%d] = %f\n", i, data_to_ext.distance[i]);
	}

	printf("WEBOT_WORKER: =================================================\n");
}

void print_data_to_bcknd(data_to_bcknd_msg_t data_to_bcknd, int print_distance) {
	printf("WEBOT_WORKER: =================== data_to_bcknd ===================\n");
	printf("WEBOT_WORKER: msg_cnt:        %llu\n", data_to_bcknd.msg_cnt);
	printf("WEBOT_WORKER: time_stmp:      %f\n", data_to_bcknd.time_stmp);
	printf("WEBOT_WORKER: sim_time:       %f\n", data_to_bcknd.sim_time);
	printf("WEBOT_WORKER: speed:          %f\n", data_to_bcknd.speed);
	printf("WEBOT_WORKER: actual_gps[0]:  %f\n", data_to_bcknd.actual_gps[0]);
	printf("WEBOT_WORKER: actual_gps[1]:  %f\n", data_to_bcknd.actual_gps[1]);
	printf("WEBOT_WORKER: heading:        %f\n", data_to_bcknd.heading);
	printf("WEBOT_WORKER: steering:       %f\n", data_to_bcknd.steering);
	printf("WEBOT_WORKER: touching:       %d\n", data_to_bcknd.touching);
	printf("WEBOT_WORKER: action_denied:  %d\n", data_to_bcknd.action_denied);
	printf("WEBOT_WORKER: discr_act_done: %d\n", data_to_bcknd.discr_act_done);

	for (int i = 0; i < print_distance; i++){
		printf("WEBOT_WORKER: data_to_bcknd.distance[%d] = %f\n", i, data_to_bcknd.distance[i]);
	}

	printf("WEBOT_WORKER: =================================================\n");
}

void print_cmd_to_ext(cmd_to_ext_msg_t cmd_to_ext) {
	printf("WEBOT_WORKER: =================== cmd_to_ext ===================\n");
	printf("WEBOT_WORKER: msg_cnt:       %llu\n", cmd_to_ext.msg_cnt);
	printf("WEBOT_WORKER: time_stmp:     %f \n", cmd_to_ext.time_stmp);
	printf("WEBOT_WORKER: request:       %s \n", response_request_str[cmd_to_ext.request]);
	printf("WEBOT_WORKER: discrete_move: %s \n", discrete_move_str[cmd_to_ext.move]);
	printf("WEBOT_WORKER: dir_type:      %s \n", direction_type_str[cmd_to_ext.dir_type]);
	printf("WEBOT_WORKER: heading:       %f \n", cmd_to_ext.heading);
	printf("WEBOT_WORKER: speed:         %f \n", cmd_to_ext.speed);
	printf("WEBOT_WORKER: =================================================\n");
}

void print_cmd_to_wb(cmd_to_wb_msg_t cmd_to_wb) {
	printf("WEBOT_WORKER: =================== cmd_to_wb ===================\n");
	printf("WEBOT_WORKER: heading: %f \n", cmd_to_wb.heading);
	printf("WEBOT_WORKER: speed:   %f \n", cmd_to_wb.speed);
	printf("WEBOT_WORKER: =================================================\n");
}

void print_init_data(init_to_ext_msg_t init_data) {
	printf("WEBOT_WORKER: =================== cmd_to_wb ===================\n");
	printf("WEBOT_WORKER: init_data.timestep: %d\n", init_data.timestep);
	printf("WEBOT_WORKER: init_data.robot_maxspeed: %f\n", init_data.maxspeed);
	printf("WEBOT_WORKER: init_data.lidar_min_range: %f\n", init_data.lidar_min_range);
	printf("WEBOT_WORKER: init_data.lidar_max_range: %f\n", init_data.lidar_max_range);
	printf("WEBOT_WORKER: =================================================\n");
}
