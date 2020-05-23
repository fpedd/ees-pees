#ifndef PRINT_H
#define PRINT_H

#include "webots/wb_com.h"
#include "backend/backend_com.h"


void print_diff_distance(wb_to_ext_msg_t wb_to_ext, ext_to_bcknd_msg_t ext_to_bcknd);

void print_wb_to_ext(wb_to_ext_msg_t wb_to_ext, int print_distance);

void print_ext_to_bcknd(ext_to_bcknd_msg_t ext_to_bcknd, int print_distance);

void print_ext_to_wb(ext_to_wb_msg_t ext_to_wb);

void print_bcknd_to_ext(bcknd_to_ext_msg_t bcknd_to_ext);


#endif // PRINT_H
