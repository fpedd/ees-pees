#ifndef WEBOT_WORKER_H
#define WEBOT_WORKER_H

#include "util.h"
#include "wb_com.h"

void *webot_worker(void *ptr);

int webot_format_wb_to_bcknd(ext_to_bcknd_msg_t* ext_to_bcknd,
                             wb_to_ext_msg_t wb_to_ext,
                             init_to_ext_msg_t init_data,
                             unsigned int action_denied,
                             unsigned int discrete_action_done);

#endif // WEBOT_WORKER_H
