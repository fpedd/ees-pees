#ifndef WEBOT_WORKER_H
#define WEBOT_WORKER_H

#include "util.h"
#include "wb_com.h"

void *webot_worker(void *ptr);

int webot_format_wb_to_bcknd(data_to_bcknd_msg_t* data_to_bcknd,
                             data_from_wb_msg_t data_from_wb,
                             int action_denied,
                             unsigned int discrete_action_done);

double heading_in_norm(double x, double y, double z);

float speed_with_dir(data_from_wb_msg_t data_from_wb);

#endif // WEBOT_WORKER_H
