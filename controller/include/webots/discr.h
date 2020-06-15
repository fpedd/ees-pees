#ifndef DISCR_H
#define DISCR_H

#include "webots/wb_com.h"
#include "backend/backend_com.h"

int discr_init();

int discr_step(ext_to_wb_msg_t *ext_to_wb, bcknd_to_ext_msg_t bcknd_to_ext,
               ext_to_bcknd_msg_t ext_to_bcknd, init_to_ext_msg_t init_data);

#endif  // DISCR_H
