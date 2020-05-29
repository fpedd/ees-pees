#include "../include/sv_functions.h"

#include <webots/robot.h>
#include <webots/supervisor.h>

#include <stdio.h>

#include "util.h"

void place_obstacle(int x, int y, WbFieldRef children_field) {
	double coord[3];

	coord[0] = x * 0.25 + 0.125;
	coord[1] = 0.125;
	coord[2] = y * 0.25 + 0.125;

	wb_supervisor_field_import_mf_node(children_field, 0, "../../libraries/objects/obstacle.wbo");
	WbNodeRef new_obstacle_node = wb_supervisor_field_get_mf_node(children_field, 0);
	WbFieldRef new_obstacle_translation_field = wb_supervisor_node_get_field(new_obstacle_node, "translation");

	wb_supervisor_field_set_sf_vec3f(new_obstacle_translation_field, coord);
}

void rand_place_obstacles(int n, WbFieldRef children_field) {
	printf("Test\n");
	for(int i = 0; i < n; i++) {
		int x = rand_int(-10, 9);
		int y = rand_int(-10, 9);
		place_obstacle(x, y, children_field);
	}
}
