#ifndef UTIL_H
#define UTIL_H

#include <pthread.h>


#include "webots/wb_com.h"
#include "backend/backend_com.h"

#define min(X, Y) (((X) < (Y)) ? (X) : (Y))
#define max(X, Y) (((X) > (Y)) ? (X) : (Y))

typedef struct {
	ext_to_bcknd_msg_t *ext_to_bcknd;
	pthread_mutex_t    *ext_to_bcknd_lock;
	bcknd_to_ext_msg_t *bcknd_to_ext;
	pthread_mutex_t    *bcknd_to_ext_lock;
} arg_struct_t;

int time_diff_start(double *time);

int time_diff_stop(double *time);

int delay(double s);

double get_time();

double heading_in_degrees(double x, double y, double z);

#endif // UTIL_H
