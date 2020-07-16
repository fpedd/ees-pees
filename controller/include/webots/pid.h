#ifndef PID_H
#define PID_H

enum pid_special {
	NORM = 0, // Normal PID controller
	WRAP = 1, // Use wrap around logic
	EXPO = 2, // Use an exponential error function
};

typedef struct {
	float k_p;            // P Gain
	float k_i;            // I Gain
	float k_d;            // D Gain
	float out_min;        // Min and
	float out_max;        // Max output bounds
	float deadband;       // Deadband to allow for response in finite time
	float err_acc;        // Error accumulator, for integral
	float prev_in;        // Previous error, for derivative
	pid_special special;  // Special function flag
} pid_ctrl_t;

int pid_init(pid_ctrl_t *pid, float k_p, float k_i, float k_d,
             float out_min, float out_max, float deadband, enum pid_special special);

int pid_run(pid_ctrl_t *pid, float dt, float set, float in, float *out);

int pid_reset(pid_ctrl_t *pid);

int pid_update(pid_ctrl_t *pid, float k_p, float k_i, float k_d);

#endif  // PID_H
