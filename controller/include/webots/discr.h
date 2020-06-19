#ifndef DISCR_H
#define DISCR_H

#include "webots/wb_com.h"
#include "backend/backend_com.h"

int discr_init();

int discr_step(cmd_to_wb_msg_t *cmd_to_wb, cmd_to_ext_msg_t cmd_to_ext,
               data_to_bcknd_msg_t data_to_bcknd, init_to_ext_msg_t init_data, int start);

void print_cood(float actual[2], float target[2]);


#endif  // DISCR_H
