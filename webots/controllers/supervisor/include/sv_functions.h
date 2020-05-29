#ifndef SV_FUNCTIONS_H
#define SV_FUNCTIONS_H


#include <webots/robot.h>
#include <webots/supervisor.h>

void place_obstacle(int x, int y, WbFieldRef children_field);

void rand_place_obstacles(int n, WbFieldRef children_field);

#endif //SV_FUNCTIONS_H
