#include "util.h"

#include <time.h>
#include <stdio.h>
#include <math.h>


int time_diff_start(double *time) {
	*time = get_time();
	return 0;
}

int time_diff_stop(double *time) {
	*time = get_time() - *time;
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


float round_with_factor(float number, float factor) {
	return (((float) round((number - factor / 2.0) / factor))  * factor) + (factor / 2.0);
}


/*********** Functions below this point should not be here (in util) ***********/

double heading_in_norm(double x, double y, double z) {

	double heading = -atan2(z, x) / M_PI;

	// Error check
	if (heading < -1.0 || heading > 1.0) {
		printf("UTIL: Error calculating heading. Heading = %f. y= %f\n", heading, y);
		return -1.0;
	}

	return heading;
}

float speed_with_dir(data_from_wb_msg_t data_from_wb) {

	static double prev_gps[2] = {data_from_wb.actual_gps[0], data_from_wb.actual_gps[2]};

	// get normalized trajectory vector from gps
	double len = sqrt(pow(data_from_wb.actual_gps[0], 2)
	                + pow(data_from_wb.actual_gps[2], 2));
	double traj[2];
	traj[0] = (data_from_wb.actual_gps[0] - prev_gps[0]) / len;
	traj[1] = (data_from_wb.actual_gps[2] - prev_gps[1]) / len;

	// safe prev gps
	prev_gps[0] = data_from_wb.actual_gps[0];
	prev_gps[1] = data_from_wb.actual_gps[2];

	// get heading from compass data (already normalized)
	double comp[2];
	comp[0] = data_from_wb.compass[2];
	comp[1] = data_from_wb.compass[0];

	// dot product
	double dot =  0;
	for (int i=0; i<2; i++) {
		dot += traj[i] * comp[i];
	}

	// adjust speed direction accordingly and cast to float
	return (float)(dot >= 0 ? data_from_wb.current_speed : -data_from_wb.current_speed);
}
