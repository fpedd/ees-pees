#include "webots/pid.h"

#include <stdio.h>
#include <math.h>

int pid_init(pid_ctrl_t *pid, float k_p, float k_i, float k_d,
             float out_min, float out_max, float deadband, enum pid_special special) {

	pid->k_p = k_p;
	pid->k_i = k_i;
	pid->k_d = k_d;

	if (out_min >= out_max) {
		fprintf(stderr, "ERROR: pid init out_min has to be smaller than out_max\n");
		return -1;
	}

	pid->out_min = out_min;
	pid->out_max = out_max;
	pid->deadband = deadband;
	pid->err_acc = 0.0;
	pid->prev_in = 0.0;

	pid->special = special;

	return 0;
}

int pid_run(pid_ctrl_t *pid, float dt, float set, float in, float *out) {

	if (dt <= 0.0) {
		fprintf(stderr, "ERROR: pid run timestep has to be greater than zero\n");
		return -1;
	}

	float err = set - in;

	if (pid->special == EXPO) {
		if (err > 0.0) {
			err = exp(err) - 1;
		} else {
			err = -exp(-err) + 1;
		}
	}

	if (fabs(err) < pid->deadband && pid->deadband != 0.0) {
		*out = 0.0;
		return 1;
	}

	if (pid->special == WRAP) {
		if (err < pid->out_min) {
			err += 2.0 * pid->out_max;
		} else if (err > pid->out_max) {
			err += 2.0 * pid->out_min;
		}
	}

	float integ = err * dt + pid->err_acc;

	float deriv = -(pid->prev_in - in) / dt;

	*out = err * pid->k_p + integ * pid->k_i + deriv * pid->k_d;

	// printf("set: %f\n", set);
	// printf("in: %f\n", in);
	// printf("err: %f\n", err);
	// printf("prop: %f\n", err * pid->k_p);
	// printf("integ: %f\n", integ * pid->k_i);
	// printf("deriv: %f\n", deriv);
	// printf("out: %f\n", *out);

	if (*out < pid->out_min) {
		*out = pid->out_min;
	} else if (*out > pid->out_max) {
		*out = pid->out_max;
	} else {
		pid->err_acc += err * dt;
	}

	pid->prev_in = in;

	return 0;
}

int pid_reset(pid_ctrl_t *pid) {

	pid->err_acc = 0.0;
	pid->prev_in = 0.0;

	return 0;
}

int pid_update(pid_ctrl_t *pid, float k_p, float k_i, float k_d) {

	pid->k_p = k_p;
	pid->k_i = k_i;
	pid->k_d = k_d;

	return 0;
}
