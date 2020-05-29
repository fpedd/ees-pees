#include "webots/pid.h"

#include <stdio.h>

int pid_init(pid_ctrl_t *pid, float k_p, float k_i, float k_d, float out_min, float out_max) {

	pid->k_p = k_p;
	pid->k_i = k_i;
	pid->k_d = k_d;

	if (out_min >= out_max) {
		fprintf(stderr, "\nERROR: pid init out_min has to smaller than out_max\n");
		return -1;
	}

	pid->out_min = out_min;
	pid->out_max = out_max;
	pid->err_acc = 0.0;
	pid->prev_set = 0.0;

	return 0;
}

int pid_run(pid_ctrl_t *pid, float dt, float set, float in, float *out) {

	if (dt <= 0.0) {
		fprintf(stderr, "\nERROR: pid run timestep has to be greater than zero\n");
		return -1;
	}

	float err = set - in;

	float integ = err * dt + pid->err_acc;

	float deriv = err / (set - pid->prev_set);

	*out = err * pid->k_p + integ * pid->k_i + deriv * pid->k_d;

	if (*out < pid->out_min) {
		*out = pid->out_min;
	} else if (*out > pid->out_max) {
		*out = pid->out_max;
	} else {
		pid->err_acc += err * dt;
	}

	pid->prev_set = set;

	return 0;
}

int pid_reset(pid_ctrl_t *pid) {

	pid->err_acc = 0.0;
	pid->prev_set = 0.0;

	return 0;
}