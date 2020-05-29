#include "print.h"

#include <stdio.h>


#include "webots/wb_com.h"
#include "backend/backend_com.h"

void print_diff_distance(wb_to_ext_msg_t wb_to_ext, ext_to_bcknd_msg_t ext_to_bcknd) {

	for (int i = 0; i < DIST_VECS; i++){
		if (wb_to_ext.distance[i] != ext_to_bcknd.distance[i]){
			printf("WEBOT_WORKER: wb_to_ext.distance[%d] = %f \t ext_to_bcknd.distance[%d] = %f\n", i, wb_to_ext.distance[i], i, ext_to_bcknd.distance[i]);
		}
	}

}



void print_wb_to_ext(wb_to_ext_msg_t wb_to_ext, int print_distance) {
	printf("WEBOT_WORKER: =================== wb_to_ext ===================\n");
	printf("WEBOT_WORKER: sim_time: \t%f\n", wb_to_ext.sim_time);
	printf("WEBOT_WORKER: current_speed: \t%f\n", wb_to_ext.current_speed);
	printf("WEBOT_WORKER: actual_gps[0]: \t%f\n", wb_to_ext.actual_gps[0]);
	printf("WEBOT_WORKER: actual_gps[1]: \t%f\n", wb_to_ext.actual_gps[1]);
	printf("WEBOT_WORKER: actual_gps[2]: \t%f\n", wb_to_ext.actual_gps[2]);
	printf("WEBOT_WORKER: compass[0]: \t%f\n", wb_to_ext.compass[0]);
	printf("WEBOT_WORKER: compass[1]: \t%f\n", wb_to_ext.compass[1]);
	printf("WEBOT_WORKER: compass[2]: \t%f\n", wb_to_ext.compass[2]);
	if (print_distance > 0){
		for (int i = 0; i < DIST_VECS; i++){
			printf("WEBOT_WORKER: wb_to_ext.distance[%d] = %f\n", i, wb_to_ext.distance[i]);
		}
	}
	printf("WEBOT_WORKER: =================================================\n");
}


void print_ext_to_bcknd(ext_to_bcknd_msg_t ext_to_bcknd, int print_distance) {
	printf("WEBOT_WORKER: =================== ext_to_bcknd ===================\n");
	printf("WEBOT_WORKER: msg_cnt: \t%llu\n", ext_to_bcknd.msg_cnt);
	printf("WEBOT_WORKER: time_stmp: \t%f\n", ext_to_bcknd.time_stmp);
	printf("WEBOT_WORKER: sim_time: \t%f\n", ext_to_bcknd.sim_time);
	printf("WEBOT_WORKER: speed: \t%f\n", ext_to_bcknd.speed);
	printf("WEBOT_WORKER: target_gps[0]: \t%f\n", ext_to_bcknd.target_gps[0]);
	printf("WEBOT_WORKER: target_gps[1]: \t%f\n", ext_to_bcknd.target_gps[1]);
	printf("WEBOT_WORKER: actual_gps[0]: \t%f\n", ext_to_bcknd.actual_gps[0]);
	printf("WEBOT_WORKER: actual_gps[1]: \t%f\n", ext_to_bcknd.actual_gps[1]);
	printf("WEBOT_WORKER: heading: \t%f\n", ext_to_bcknd.heading);
	printf("WEBOT_WORKER: touching: \t%d\n", ext_to_bcknd.touching);

	if (print_distance > 0) {
		for (int i = 0; i < DIST_VECS; i++){
			printf("WEBOT_WORKER: ext_to_bcknd.distance[%d] = %f\n", i, ext_to_bcknd.distance[i]);
		}
	}
	printf("WEBOT_WORKER: =================================================\n");
}

void print_ext_to_wb(ext_to_wb_msg_t ext_to_wb) {
	printf("WEBOT_WORKER: =================== ext_to_wb ===================\n");
	printf("WEBOT_WORKER: heading: \t%f \n", ext_to_wb.heading);
	printf("WEBOT_WORKER: speed: \t%f \n", ext_to_wb.speed);
	printf("WEBOT_WORKER: =================================================\n");
}

void print_bcknd_to_ext(bcknd_to_ext_msg_t bcknd_to_ext) {
	printf("WEBOT_WORKER: =================== bcknd_to_ext ===================\n");
	printf("WEBOT_WORKER: msg_cnt: \t%llu\n", bcknd_to_ext.msg_cnt);
	printf("WEBOT_WORKER: time_stmp: \t%f \n", bcknd_to_ext.time_stmp);
	printf("WEBOT_WORKER: heading: \t%f \n", bcknd_to_ext.heading);
	printf("WEBOT_WORKER: speed: \t%f \n", bcknd_to_ext.speed);
	printf("WEBOT_WORKER: =================================================\n");
}
