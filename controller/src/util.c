#include "util.h"

#include <time.h>
#include <stdio.h>
#include <math.h>


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

double heading_in_degrees(double x, double y, double z) {

	double rad = atan2(x, z);
	double heading = (rad-M_PI/2) * 180.0  / M_PI;

	if (heading < 0.0) {
		heading = heading + 360.0;
	}

	// Error check
	if (heading < 0.0 || heading >= 360.0) {
		printf("UTIL: Error calculating heading. Heading = %f. y= %f\n", heading, y);
		return -1.0;
	}


	return heading;
}
