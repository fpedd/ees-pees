#include "../include/sv_functions.h"

#include <webots/robot.h>
#include <webots/supervisor.h>

#define _USE_MATH_DEFINES
// #define NDEBUG //uncomment to enable assertions

#include <math.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>

#include "util.h"

#define SUPERVISOR_ROBOT_HEIGHT_OFFSET 0.02
#define SUPERVISOR_MIN_SCALE 0.25 //~0.17 would be the size of robot


//QA-TODO: assert multiple things given by world:
// -target/robot spawned?
// -supervisor robot has supervisor enabled and synchro disabled? !!

/*
 Todays schedule:
 - do tcp parsing and forwarding to sv_functions
 - send target to backend after start and each reset
synchronization: if timestep triggers while obejects are moved, robot might get stuck in a block
*/

/*
 * Calculates the center of a checker field
 */
double sv_to_coord(sv_world_def *world, int xy) {
	return xy * world->scale + 0.5 * world->scale;
}

/*
 * Calculates the internal coordinate of a checker field given a Webots coordinate
 */
int sv_from_coord(sv_world_def *world, double xy) {
	return xy / world->scale;
}

/*
 * Move a single obstacle in the arena grid
 */
void sv_obstacle_put(sv_world_def *world, int x, int y, int id) {
	double coord[3];

	coord[0] = sv_to_coord(world, x);	//x in Webots
	coord[1] = sv_to_coord(world, 0);	//y in Webots
	coord[2] = sv_to_coord(world, y);	//z in Webots

	WbNodeRef obstacle_node = wb_supervisor_field_get_mf_node(world->children_field, id);
	WbFieldRef obstacle_translation_field = wb_supervisor_node_get_field(obstacle_node, "translation");

	// adjust block position
	wb_supervisor_field_set_sf_vec3f(obstacle_translation_field, coord);
}

/*
 * Place all requested obstacles in the arena grid without overlap
 */
void sv_obstacle_put_all(sv_world_def *world) {
	 // using an array to check occupancy of a discrete coordinate
	int *world_array = (int *) calloc(world->size * world->size, sizeof(int));
	if(world_array == NULL) {
		sv_simulation_stop();
		abort();
	}
	int x, y, id;
	 // set start and target as occupied
	x = sv_from_coord(world, world->start[0]);
	y = sv_from_coord(world, world->start[1]);
	world_array[x*world->size + y] = 1;
	x = sv_from_coord(world, world->target[0]);
	y = sv_from_coord(world, world->target[1]);
	world_array[x*world->size + y] = 1;

	id = 0;
	 // place all obstacle on individual coordinates
	while(id < world->num_obstacles) {
		x = rand_int(0, world->size - 1);
		y = rand_int(0, world->size - 1);
		if(world_array[x*world->size + y] == 0) {
			world_array[x*world->size + y] = 1;
			sv_obstacle_put(world, x, y, id);
			id++;
		}
	}
	free(world_array);
}

/*
 * Spawn a single obstacle in the arena grid
 */
void sv_obstacle_spawn(sv_world_def *world) {
	double coord[3], scale[3];

	 // spawn outside of the grid
	coord[0] = sv_to_coord(world, -1);	//x in Webots
	coord[1] = sv_to_coord(world, 0);	//y in Webots
	coord[2] = sv_to_coord(world, -1);	//z in Webots

	scale[0] = world->scale;
	scale[1] = world->scale;
	scale[2] = world->scale;

	wb_supervisor_field_import_mf_node(world->children_field, -1, "../../libraries/objects/obstacle.wbo");
	WbNodeRef new_obstacle_node = wb_supervisor_field_get_mf_node(world->children_field, -1);
	WbFieldRef new_obstacle_translation_field = wb_supervisor_node_get_field(new_obstacle_node, "translation");
	WbFieldRef new_obstacle_scale_field = wb_supervisor_node_get_field(new_obstacle_node, "scale");

	// adjust block position and scale
	wb_supervisor_field_set_sf_vec3f(new_obstacle_scale_field, scale);
	wb_supervisor_field_set_sf_vec3f(new_obstacle_translation_field, coord);
}

/*
 * Inits the world struct and sets the Webots arena accordingly
 * (use sv_world_clear before if reinit)
 */
void sv_world_init(sv_world_def *world, int world_size, double scale, int num_obstacles, int fast) {
	 // assert inputs
	assert(world_size > 0 && scale >= SUPERVISOR_MIN_SCALE);
	assert(num_obstacles >= 0 && num_obstacles <= world_size * world_size);
	assert(target[0] > 0 && target[0] < world_size && target[1] > 0 && target[1] < world_size); //assert target in arena

	 // init struct
	world->size          = world_size;
	world->num_obstacles = num_obstacles;
	world->scale         = scale;
	world->fast          = fast;

	 //change arena size, scaling and position in webots
	WbNodeRef arena_node = wb_supervisor_node_get_from_def("Arena");
	WbFieldRef arena_size_field = wb_supervisor_node_get_field(arena_node, "floorSize");
	WbFieldRef arena_scale_field = wb_supervisor_node_get_field(arena_node, "floorTileSize");
	WbFieldRef arena_translation_field = wb_supervisor_node_get_field(arena_node, "translation");

	double size_vec[2]        = {world->size*world->scale, world->size*world->scale};
	double scale_vec[2]       = {2*world->scale, 2*world->scale}; //2* factor only for checkered grid alignment
	double translation_vec[3] = {world->size*world->scale/2.0, 0.0, world->size*world->scale/2.0};

	wb_supervisor_field_set_sf_vec2f(arena_size_field, size_vec);
	wb_supervisor_field_set_sf_vec2f(arena_scale_field, scale_vec);
	wb_supervisor_field_set_sf_vec3f(arena_translation_field, translation_vec);

	 // spawn in all obstacles needed
	for(int i = 0; i < world->num_obstacles; i++) {
		sv_obstacle_spawn(world);
	}

	 // (Maybe TODO: adjust camera position to new arena)
}


/*
 * Places start, target and obstacles randomly
 */
void sv_world_generate(sv_world_def *world, int seed) {
	srand(seed);

	double translation_vec[3] = {0.0, 0.0, 0.0};
	double rotation_vec[4]    = {0.0, 1.0, 0.0, 0};

	 // place target randomly in arena

	world->target[0] = sv_to_coord(world, rand_int(0, world->size - 1));
	world->target[1] = sv_to_coord(world, rand_int(0, world->size - 1));

	translation_vec[0] = world->target[0];
	translation_vec[2] = world->target[1];

	wb_supervisor_field_set_sf_vec3f(world->target_translation_field, translation_vec);

	 // place robot randomly with random rotation
	world->start[0] = sv_to_coord(world, rand_int(0, world->size - 1));
	world->start[1] = sv_to_coord(world, rand_int(0, world->size - 1));

	translation_vec[0] = world->start[0];
	translation_vec[1] = SUPERVISOR_ROBOT_HEIGHT_OFFSET;
	translation_vec[2] = world->start[1];
	rotation_vec[3] = rand_int(0, 359)*M_PI/180; //1-deg resolution

	WbFieldRef robot_translation_field = wb_supervisor_node_get_field(world->robot_node, "translation");
	WbFieldRef robot_rotation_field = wb_supervisor_node_get_field(world->robot_node, "rotation");

	wb_supervisor_field_set_sf_vec3f(robot_translation_field, translation_vec);
	wb_supervisor_field_set_sf_rotation(robot_rotation_field, rotation_vec);

	 // place obstacles
	sv_obstacle_put_all(world);
}


/*
 * Delete obstacles and place start/target to default position (only to reinit world)
 */
void sv_world_clear(sv_world_def *world) {
	double translation_vec[3] = {0.0, 0.0, 0.0};
	double rotation_vec[4]    = {0.0, 1.0, 0.0, 0};

	for(int i = 0; i < world->num_obstacles; i++) {
		wb_supervisor_field_remove_mf(world->children_field, -1);
	}

	world->start[0] = sv_to_coord(world, 0);
	world->start[1] = sv_to_coord(world, 0);

	WbFieldRef robot_translation_field = wb_supervisor_node_get_field(world->robot_node, "translation");
	WbFieldRef robot_rotation_field = wb_supervisor_node_get_field(world->robot_node, "rotation");

	wb_supervisor_field_set_sf_vec3f(robot_translation_field, translation_vec);
	wb_supervisor_field_set_sf_rotation(robot_rotation_field, rotation_vec);

	//wb_supervisor_simulation_reset();
}

/*
 * Prepare environment to start simulation on command
 */
sv_world_def *sv_simulation_init() {
	  // stop first ongoing simulation
	wb_supervisor_simulation_set_mode(WB_SUPERVISOR_SIMULATION_MODE_PAUSE);

	 //malloc struct
	sv_world_def *world = (sv_world_def *) malloc(sizeof(sv_world_def));
	if(world == NULL) {
		sv_simulation_stop();
		abort();
	}

	 //get information of the simulation tree
	WbNodeRef obstacles_group_node = wb_supervisor_node_get_from_def("Obstacles");
	WbFieldRef obstacles_children_field = wb_supervisor_node_get_field(obstacles_group_node, "children");

	WbNodeRef target_node = wb_supervisor_node_get_from_def("Target");
	WbFieldRef target_translation_field = wb_supervisor_node_get_field(target_node, "translation");

	WbNodeRef robot_node = wb_supervisor_node_get_from_def("Smitty");

	world->children_field = obstacles_children_field;
	world->robot_node = robot_node;
	world->target_translation_field = target_translation_field;

	return world;
}


void sv_simulation_start(sv_world_def *world) {
	// starts simulation (fast if given) and (re)starts the controller
	WbSimulationMode mode = world->fast ? WB_SUPERVISOR_SIMULATION_MODE_FAST : WB_SUPERVISOR_SIMULATION_MODE_REAL_TIME;
	wb_robot_step(0);
	wb_supervisor_simulation_set_mode(mode);
	wb_supervisor_node_restart_controller(world->robot_node);
}

//-Wrapper functions-
void sv_simulation_stop() {
	wb_supervisor_simulation_set_mode(WB_SUPERVISOR_SIMULATION_MODE_PAUSE);
}


void sv_simulation_cleanup(sv_world_def *world) {
	free(world);
}
