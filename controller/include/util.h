#ifndef UTIL_H
#define UTIL_H

#include <pthread.h>


#include "webots/wb_com.h"
#include "backend/backend_com.h"

#define min(X, Y) (((X) < (Y)) ? (X) : (Y))
#define max(X, Y) (((X) > (Y)) ? (X) : (Y))

enum direction {
	FORWARDS = -1,
	STOPPED = 0,
	BACKWARDS = 1
};

typedef struct {
	data_to_bcknd_msg_t *itc_data;
	pthread_mutex_t    *itc_data_lock;
	cmd_from_bcknd_msg_t *itc_cmd;
	pthread_mutex_t    *itc_cmd_lock;
} arg_struct_t;

int time_diff_start(double *time);

int time_diff_stop(double *time);

int delay(double s);

double get_time();

double heading_in_norm(double x, double y, double z);

int compare_direction(double *vec1, double *vec2, int size);

float round_with_factor(float number, float factor);

#endif // UTIL_H
