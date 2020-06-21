#ifndef UTIL_H
#define UTIL_H


#define min(X, Y) (((X) < (Y)) ? (X) : (Y))
#define max(X, Y) (((X) > (Y)) ? (X) : (Y))

int time_diff_start(double *time);

int time_diff_stop(double *time);

int delay(double s);

double get_time();

int rand_int(int max);

#endif // UTIL_H
