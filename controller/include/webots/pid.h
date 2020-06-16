#ifndef PID_H
#define PID_H

// http://www.mstarlabs.com/apeng/techniques/pidsoftw.html

enum pid_special {
	NORM = 0,           // Dont do a discrete move at all, do continous
	WRAP = 1,           // Use wrap around logic
	EXPO = 2,           // Use an expoential error function
};

typedef struct {
	float k_p;
	float k_i;
	float k_d;
	float out_min;
	float out_max;
	float deadband;
	float err_acc;
	float prev_in;
	pid_special special;
} pid_ctrl_t;


int pid_init(pid_ctrl_t *pid, float k_p, float k_i, float k_d,
             float out_min, float out_max, float deadband, enum pid_special special);

int pid_run(pid_ctrl_t *pid, float dt, float set, float in, float *out);

int pid_reset(pid_ctrl_t *pid);

int pid_update(pid_ctrl_t *pid, float k_p, float k_i, float k_d);

#endif  // PID_H
