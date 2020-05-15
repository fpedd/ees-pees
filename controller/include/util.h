#ifndef UTIL_H
#define UTIL_H

#include "webots/wb_com.h"
#include "backend/backend_com.h"

#define min(X, Y) (((X) < (Y)) ? (X) : (Y))
#define max(X, Y) (((X) > (Y)) ? (X) : (Y))

typedef struct {
	ext_to_bcknd_msg_t *ext_to_bcknd;
	bcknd_to_ext_msg_t *bcknd_to_ext;
} arg_struct_t;

int time_diff_start(double *time);

int time_diff_stop(double *time);

int delay(double s);

double get_time();

void error(char* reason);

#endif // UTIL_H
