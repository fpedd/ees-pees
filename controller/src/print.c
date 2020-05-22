#include "print.h"

#include <stdio.h>


#include "webots/wb_com.h"
#include "backend/backend_com.h"

void print_diff_distance(wb_to_ext_msg_t wb_to_ext, ext_to_bcknd_msg_t ext_to_bcknd) {

	for (int i = 0; i < DIST_VECS; i++){
		if (wb_to_ext.distance[i] != ext_to_bcknd.distance[i]){
			printf("wb_to_ext.distance[%d] = %f \t ext_to_bcknd.distance[%d] = %f\n", i, wb_to_ext.distance[i], i, ext_to_bcknd.distance[i]);
		}
	}

}

void print_wb_to_ext(wb_to_ext_msg_t wb_to_ext) {
	printf("=================== wb_to_ext ===================\n");
	printf("sim_time: \t%f\n", wb_to_ext.sim_time);
	printf("current_speed: \t%f\n", wb_to_ext.current_speed);
	printf("actual_gps[0]: \t%f\n", wb_to_ext.actual_gps[0]);
	printf("actual_gps[1]: \t%f\n", wb_to_ext.actual_gps[1]);
	printf("actual_gps[2]: \t%f\n", wb_to_ext.actual_gps[2]);
	printf("compass[0]: \t%f\n", wb_to_ext.compass[0]);
	printf("compass[1]: \t%f\n", wb_to_ext.compass[1]);
	printf("compass[2]: \t%f\n", wb_to_ext.compass[2]);
	printf("=================================================\n");
}


void print_ext_to_bcknd(ext_to_bcknd_msg_t ext_to_bcknd) {
	printf("=================== ext_to_bcknd ===================\n");
	printf("msg_cnt: \t%llu\n", ext_to_bcknd.msg_cnt);
	printf("time_stmp: \t%f\n", ext_to_bcknd.time_stmp);
	printf("sim_time: \t%f\n", ext_to_bcknd.sim_time);
	printf("sim_speed: \t%f\n", ext_to_bcknd.sim_speed);
	printf("target_gps[0]: \t%f\n", ext_to_bcknd.target_gps[0]);
	printf("target_gps[1]: \t%f\n", ext_to_bcknd.target_gps[1]);
	printf("actual_gps[0]: \t%f\n", ext_to_bcknd.actual_gps[0]);
	printf("actual_gps[1]: \t%f\n", ext_to_bcknd.actual_gps[1]);
	printf("heading: \t%f\n", ext_to_bcknd.heading);
	printf("touching: \t%d\n", ext_to_bcknd.touching);
	printf("=================================================\n");
}

void print_ext_to_wb(ext_to_wb_msg_t ext_to_wb) {
	printf("=================== ext_to_wb ===================\n");
	printf("heading: \t%f \n", ext_to_wb.heading);
	printf("speed: \t%f \n", ext_to_wb.speed);
	printf("=================================================\n");
}

void print_bcknd_to_ext(bcknd_to_ext_msg_t bcknd_to_ext) {
	printf("=================== bcknd_to_ext ===================\n");
	printf("msg_cnt: \t%llu\n", bcknd_to_ext.msg_cnt);
	printf("time_stmp: \t%f \n", bcknd_to_ext.time_stmp);
	printf("heading: \t%f \n", bcknd_to_ext.heading);
	printf("speed: \t%f \n", bcknd_to_ext.speed);
	printf("=================================================\n");
}
