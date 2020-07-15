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

	// Calculate the control error
	float err = set - in;

	// Check for special exponential function
	if (pid->special == EXPO) {
		if (err > 0.0) {
			err = exp(err) - 1;
		} else {
			err = -exp(-err) + 1;
		}
	}

	// Check, when deadband active, if inside deadband
	if (fabs(err) < pid->deadband && pid->deadband != 0.0) {
		*out = 0.0;
		return 1;
	}

	// Check for special warp around function
	if (pid->special == WRAP) {
		if (err < pid->out_min) {
			err += 2.0 * pid->out_max;
		} else if (err > pid->out_max) {
			err += 2.0 * pid->out_min;
		}
	}

	// Calculate integral error
	float integ = err * dt + pid->err_acc;

	// Calculate derivative error
	// Do derivate of only process variable to avoid command glitches
	float deriv = -(pid->prev_in - in) / dt;

	// Calculate overall error
	*out = err * pid->k_p + integ * pid->k_i + deriv * pid->k_d;

	// Prints for showcasing (or debugging)
	// printf("set: %f\n", set);
	// printf("in: %f\n", in);
	// printf("err: %f\n", err);
	// printf("prop: %f\n", err * pid->k_p);
	// printf("integ: %f\n", integ * pid->k_i);
	// printf("deriv: %f\n", deriv * pid->k_d);
	// printf("out: %f\n", *out);

	// Bound output to set limits, this is also our anti windup logic
	if (*out < pid->out_min) {
		*out = pid->out_min;
	} else if (*out > pid->out_max) {
		*out = pid->out_max;
	} else {
		pid->err_acc += err * dt;
	}

	// Store current error in prev variable for next iteration
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
