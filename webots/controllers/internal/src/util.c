#include "../include/util.h"

#include <time.h>
#include <stdio.h>



int time_diff_start(double *time) {
    get_time(time);
    return 0;
}

int time_diff_stop(double *time) {
    double time_stop;
    get_time(&time_stop);
    *time = time_stop - *time;
    return 0;
}

int delay(double sec) {
    double start_time = get_time();
    while (get_time() < (start_time + sec));
    return 0;
}

double get_time() {
    struct timespec time_raw;
    clock_gettime(CLOCK_REALTIME, &time_raw);
    return (double)time_raw.tv_sec + ((double)time_raw.tv_nsec / (double)1000000000);
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

void error(char* reason){
	printf("ERROR: %s\n", reason);
}
