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
} pid_t;

// TODO: only feed "in" changes into derivative part of controller, not "err"

int pid_init(pid_t *pid, float k_p, float k_i, float k_d, float out_min, float out_max);

int pid_run(pid_t *pid, float dt, float set, float in, float *out);

int pid_reset(pid_t *pid);

#endif  // PID_H
