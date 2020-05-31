#ifndef WEBOT_WORKER_H
#define WEBOT_WORKER_H

#include "util.h"
#include "wb_com.h"

void webot_worker(arg_struct_t *arg_struct);

int webot_format_wb_to_bcknd(ext_to_bcknd_msg_t* ext_to_bcknd, wb_to_ext_msg_t wb_to_ext, init_to_ext_msg_t init_data);

int webot_format_bcknd_to_wb(ext_to_wb_msg_t* ext_to_wb, bcknd_to_ext_msg_t bcknd_to_ext, init_to_ext_msg_t init_data);

#endif // WEBOT_WORKER_H
