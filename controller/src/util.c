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
