#ifndef PRINT_H
#define PRINT_H

#include "webots/wb_com.h"
#include "backend/backend_com.h"

void print_diff_distance(data_from_wb_msg_t data_from_wb, data_to_bcknd_msg_t data_to_bcknd);

void print_data_from_wb(data_from_wb_msg_t data_from_wb, int print_distance);

void print_data_to_bcknd(data_to_bcknd_msg_t data_to_bcknd, int print_distance);

void print_cmd_from_bcknd(cmd_from_bcknd_msg_t cmd_from_bcknd);

void print_cmd_to_wb(cmd_to_wb_msg_t cmd_to_wb);

void print_init_data(init_to_ext_msg_t init_data);

void print_silhouette();

void print_dist_to_python(float *dist);

#endif // PRINT_H
