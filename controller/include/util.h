#ifndef UTIL_H
#define UTIL_H

#include <pthread.h>

#include "webots/wb_com.h"
#include "backend/backend_com.h"

#define min(X, Y) (((X) < (Y)) ? (X) : (Y))
#define min_floor(X, Y) ((min(X, Y) < 0) ? 0 : min(X, Y))
#define max(X, Y) (((X) > (Y)) ? (X) : (Y))

typedef struct {
	data_to_bcknd_msg_t  *itc_data;       // Data going from webot to backend worker
	pthread_mutex_t      *itc_data_lock;  // Mutex to mitigate race condition
	cmd_from_bcknd_msg_t *itc_cmd;        // Commands going from backend to webot worker
	pthread_mutex_t      *itc_cmd_lock;   // Mutex to mitigate race condition
} arg_struct_t;

int time_diff_start(double *time);

int time_diff_stop(double *time);

int delay(double s);

double get_time();

float round_with_factor(float number, float factor);

#endif // UTIL_H
