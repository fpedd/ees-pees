#include "webots/drive.h"

#include <stdio.h>
#include <string.h>

#include "util.h"
#include "webots/pid.h"

static double last_time;
static pid_ctrl_t speed_pid;
static pid_ctrl_t heading_pid;

int drive_init() {
        last_time = get_time();
        pid_init(&speed_pid, 0.0, 0, 0, -1.0, 1.0, 0);
        pid_init(&heading_pid, 5.0, 0.0, 0, -1.0, 1.0, 1);
        return 0;
}

int drive_manual(init_to_ext_msg_t init_data, float speed, float heading) {
    ext_to_wb_msg_t ext_to_wb;
    memset(&ext_to_wb, 0, sizeof(ext_to_wb_msg_t));

    ext_to_wb.speed = speed * init_data.maxspeed * -1;
    ext_to_wb.heading = heading;

    printf("DRIVE: speed %f, heading %f \n", ext_to_wb.speed, ext_to_wb.heading);

    return wb_send(ext_to_wb);
}

int drive_automatic(init_to_ext_msg_t init_data,
                    float set_speed,
                    float set_heading,
                    float act_speed,
                    float act_heading) {

    (void) act_speed;
    // No need for PID controller on speed yet
    float com_speed = set_speed;
    // pid_run(&speed_pid, get_time() - last_time, set_speed, act_speed, &com_speed);
    // printf("DRIVE: speed set: %f  act: %f com: %f \n", set_speed, act_speed, com_speed);

    float com_heading = 0;
    pid_run(&heading_pid, get_time() - last_time, set_heading, act_heading, &com_heading);

    // TODO: fix controller when driving backwards
    // this should be act_speed and not set speed
    if (set_speed < 0.0) {
        com_heading *= -1.0;
    }

    // printf("DRIVE: heading set: %f  act: %f com: %f \n", set_heading, act_heading, com_heading);

    last_time = get_time();

    ext_to_wb_msg_t ext_to_wb;
    memset(&ext_to_wb, 0, sizeof(ext_to_wb_msg_t));

    ext_to_wb.speed = com_speed * init_data.maxspeed * -1;
    ext_to_wb.heading = com_heading;

    // printf("DRIVE: speed %f, heading %f \n", ext_to_wb.speed, ext_to_wb.heading);

    return wb_send(ext_to_wb);
}
