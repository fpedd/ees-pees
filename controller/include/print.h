#ifndef PRINT_H
#define PRINT_H

#include "webots/wb_com.h"
#include "backend/backend_com.h"


void print_diff_distance(data_to_ext_msg_t data_to_ext, data_to_bcknd_msg_t data_to_bcknd);

void print_data_to_ext(data_to_ext_msg_t data_to_ext, int print_distance);

void print_data_to_bcknd(data_to_bcknd_msg_t data_to_bcknd, int print_distance);

void print_cmd_to_ext(cmd_to_ext_msg_t cmd_to_ext);

void print_cmd_to_wb(cmd_to_wb_msg_t cmd_to_wb);

void print_init_data(init_to_ext_msg_t init_data);

#endif // PRINT_H
