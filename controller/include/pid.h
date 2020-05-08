#ifndef PID_H
#define PID_H

// http://www.mstarlabs.com/apeng/techniques/pidsoftw.html

typedef struct {
    float k_p;
    float k_i;
    float k_d;
    float out_max;
    float out_min;
    float err_acc;
    float prev_set;
} pid_ctrl_t;

int pid_init(pid_ctrl_t *pid, float k_p, float k_i, float k_d, float out_min, float out_max);

int pid_run(pid_ctrl_t *pid, float dt, float set, float in, float *out);

int pid_reset(pid_ctrl_t *pid);

#endif  // PID_H
