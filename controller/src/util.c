#include "util.h"

#include <time.h>


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
    double start_time;
    get_time(&start_time);
    double current_time;
    do {
        get_time(&current_time);
    } while (current_time < (start_time + sec));
    return 0;
}

int get_time(double *time) {
    struct timespec time_raw;
    clock_gettime(CLOCK_REALTIME, &time_raw);
    *time = (double)time_raw.tv_sec + ((double)time_raw.tv_nsec / (double)1000000000);
    return 0;
}
