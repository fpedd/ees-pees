#include "webots/safe.h"

#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <math.h>
#include <float.h>

#include "backend/backend_com.h"
#include "silhouette.h"
#include "util.h"
#include "print.h"

#define CONDENSE_WIDTH 20   // number of entries combined to one sensor datum

#define SPEED_PREDICT 0.0
#define STEERING_PREDICT 45.0

#define STEPS_STOP 10.0        // if number of steps till obstacle lower than this, deny action
#define STEPS_SLOW 25.0        // if number of steps till obstacle lower than this, slow down
#define CLOSEST_ALLOWED 0.04   // if distance in move direction lower than this, STOP

// angles with longest distańce in silhoutte (corners of hitbox)
#define FRONT_LEFT    127
#define FRONT         179
#define FRONT_RIGHT   232
#define BACK_LEFT     39
#define BACK          0
#define BACK_RIGHT    320

// hitbox size to each side of the robot
#define SIDE_WIDTH 0.8
#define MAX_DISTANCE 3.4

// [1.151645, 1.173023, 1.195581, 1.219402, 1.244579, 1.271213, 1.299415, 1.329312, 1.361041, 1.394757, 1.430633, 1.468863, 1.509664, 1.553283, 1.600000, 1.650132, 1.704044, 1.762151, 1.824938, 1.892961, 1.966875, 2.047444, 2.135574, 2.232342, 2.339044, 2.457243, 2.588854, 2.736243, 2.902364, 3.090963, 3.306852, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.306852, 3.090963, 2.902364, 2.736243, 2.588854, 2.457243, 2.339044, 2.232342, 2.135574, 2.047444, 1.966875, 1.892961, 1.824938, 1.762151, 1.704044, 1.650132, 1.600000, 1.553283, 1.509664, 1.468863, 1.430633, 1.394757, 1.361041, 1.329312, 1.299415, 1.271213, 1.244579, 1.219402, 1.195581, 1.173023, 1.151645, 1.131371, 1.112131, 1.093862, 1.076506, 1.060010, 1.044326, 1.029408, 1.015215, 1.001709, 0.988854, 0.976620, 0.964974, 0.953891, 0.943343, 0.933307, 0.923760, 0.914683, 0.906056, 0.897861, 0.890082, 0.882702, 0.875709, 0.869088, 0.862828, 0.856916, 0.851342, 0.846097, 0.841170, 0.836553, 0.832240, 0.828221, 0.824491, 0.821043, 0.817872, 0.814973, 0.812341, 0.809972, 0.807862, 0.806008, 0.804407, 0.803056, 0.801953, 0.801098, 0.800488, 0.800122, 0.800000, 0.800122, 0.800488, 0.801098, 0.801953, 0.803056, 0.804407, 0.806008, 0.807862, 0.809972, 0.812341, 0.814973, 0.817872, 0.821043, 0.824491, 0.828221, 0.832240, 0.836553, 0.841170, 0.846097, 0.851342, 0.856916, 0.862828, 0.869088, 0.875709, 0.882702, 0.890082, 0.897861, 0.906056, 0.914683, 0.923760, 0.933307, 0.943343, 0.953891, 0.964974, 0.976620, 0.988854, 1.001709, 1.015215, 1.029408, 1.044326, 1.060010, 1.076506, 1.093862, 1.112131, 1.131371, 1.151645, 1.173023, 1.195581, 1.219402, 1.244579, 1.271213, 1.299415, 1.329312, 1.361041, 1.394757, 1.430633, 1.468863, 1.509664, 1.553283, 1.600000, 1.650132, 1.704044, 1.762151, 1.824938, 1.892961, 1.966875, 2.047444, 2.135574, 2.232342, 2.339044, 2.457243, 2.588854, 2.736243, 2.902364, 3.090963, 3.306852, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.400000, 3.306852, 3.090963, 2.902364, 2.736243, 2.588854, 2.457243, 2.339044, 2.232342, 2.135574, 2.047444, 1.966875, 1.892961, 1.824938, 1.762151, 1.704044, 1.650132, 1.600000, 1.553283, 1.509664, 1.468863, 1.430633, 1.394757, 1.361041, 1.329312, 1.299415, 1.271213, 1.244579, 1.219402, 1.195581, 1.173023, 1.151645, 1.131371, 1.112131, 1.093862, 1.076506, 1.060010, 1.044326, 1.029408, 1.015215, 1.001709, 0.988854, 0.976620, 0.964974, 0.953891, 0.943343, 0.933307, 0.923760, 0.914683, 0.906056, 0.897861, 0.890082, 0.882702, 0.875709, 0.869088, 0.862828, 0.856916, 0.851342, 0.846097, 0.841170, 0.836553, 0.832240, 0.828221, 0.824491, 0.821043, 0.817872, 0.814973, 0.812341, 0.809972, 0.807862, 0.806008, 0.804407, 0.803056, 0.801953, 0.801098, 0.800488, 0.800122, 0.800000, 0.800122, 0.800488, 0.801098, 0.801953, 0.803056, 0.804407, 0.806008, 0.807862, 0.809972, 0.812341, 0.814973, 0.817872, 0.821043, 0.824491, 0.828221, 0.832240, 0.836553, 0.841170, 0.846097, 0.851342, 0.856916, 0.862828, 0.869088, 0.875709, 0.882702, 0.890082, 0.897861, 0.906056, 0.914683, 0.923760, 0.933307, 0.943343, 0.953891, 0.964974, 0.976620, 0.988854, 1.001709, 1.015215, 1.029408, 1.044326, 1.060010, 1.076506, 1.093862, 1.112131, 1.131371]


int safety_check(init_to_ext_msg_t init_data, data_from_wb_msg_t data_from_wb, cmd_to_wb_msg_t* cmd_to_wb) {

	int action_denied = 0;


	static double last_gps[2] = {data_from_wb.actual_gps[0], data_from_wb.actual_gps[2]};

	// get distance array subtract shiloutte
	float distance[DIST_VECS];
	memcpy(&distance, data_from_wb.distance, sizeof(float) * DIST_VECS);


	subtract_silhouette(distance);

	// get movement direction from gps data
	double move_vec[2];
	move_vec[0] = data_from_wb.actual_gps[0] - last_gps[0];
	move_vec[1] = data_from_wb.actual_gps[2] - last_gps[1];

	// norm move_vec
	double length = sqrt(pow(move_vec[0], 2) + pow(move_vec[1], 2));
	move_vec[0] = move_vec[0] / length;
	move_vec[1] = move_vec[1] / length;
	// printf("SAFE: move_vec[0] = %f, move_vec[1] = %f\n", move_vec[0], move_vec[1]);

	// get roboter heading from compass data
	double compass[2];
	compass[0] = data_from_wb.compass[2];
	compass[1] = data_from_wb.compass[0];
	// printf("SAFE: compass[0] = %f, compass[1] = %f\n", compass[0], compass[1]);


	// get three condensed sensor values in moving direction
	int direction = compare_direction(move_vec, compass, 2);

	float hitbox[DIST_VECS];
	calc_hitbox(hitbox, 0);
	printf("\ncmd_to_wb->heading: %f \n\n", cmd_to_wb->heading);
	print_dist_to_python(hitbox);

	float dist_left = FLT_MAX;
	float dist_straight = FLT_MAX;
	float dist_right = FLT_MAX;

	if (direction == FORWARDS) {
		dist_left     = condense_data(distance, CONDENSE_WIDTH, FRONT_LEFT);
		dist_straight = condense_data(distance, CONDENSE_WIDTH, FRONT);
		dist_right    = condense_data(distance, CONDENSE_WIDTH, FRONT_RIGHT);
	} else if (direction == BACKWARDS) {
		dist_left     = condense_data(distance, CONDENSE_WIDTH, BACK_LEFT);
		dist_straight = condense_data(distance, CONDENSE_WIDTH, BACK);
		dist_right    = condense_data(distance, CONDENSE_WIDTH, BACK_RIGHT);
	} else {
		// not moving
	}
	// printf("SAVE: Dist: l: %f \t s: %f \t r: %f\n", dist_left, dist_straight, dist_right);

	// calculate time till obstacle if command is send
	double movement_per_step = data_from_wb.current_speed * init_data.timestep / 1000;

	float steps_left     = fabs(dist_left / movement_per_step);
	float steps_straight = fabs(dist_straight / movement_per_step);
	float steps_right    = fabs(dist_right / movement_per_step);

	// printf("SAVE: Steps: l: %f \t s: %f \t r: %f v: %f\n", steps_left, steps_straight, steps_right, movement_per_step);
	float steps_till_crash = min(steps_straight, min(steps_left, steps_right));

	if (steps_till_crash <= 0.0) {
		printf("SAFE: we crashed!\n");
		cmd_to_wb->speed = 0;
		action_denied = 1;

	} else if (steps_till_crash <= STEPS_STOP) {
		fprintf(stderr, "SAFE: Close to obstacle. STEPS: l= %f\t s=%f\t r=%f\n", steps_left, steps_straight, steps_right);
		cmd_to_wb->speed = 0;
		action_denied = 1;
	} else if (steps_till_crash <= STEPS_SLOW){
		fprintf(stderr, "SAFE: Slowing down. STEPS: l= %f\t s=%f\t r=%f\n", steps_left, steps_straight, steps_right);
		cmd_to_wb->speed = 0;
		// printf("SAFE: steps = %f dist =  %f current speed = %f direction: %d\n", steps_till_crash, dist_in_direction, data_from_wb.current_speed, direction);
	}

	// check if distance falls below CLOSEST_ALLOWED in any direction
	if (too_close(distance, cmd_to_wb->speed, direction) == 1) {
		cmd_to_wb->speed = 0;
		action_denied = 1;
	}

	last_gps[0] = data_from_wb.actual_gps[0];
	last_gps[1] = data_from_wb.actual_gps[2];

	return action_denied;
}

// int safety_init() {
// 	calc_hitbox(hitbox, 10);
// 	print_dist_to_python(hitbox);
// 	return 0;
// }


int calc_hitbox(float *hitbox, int angle) {

	if (angle < 0 || angle > 359) {
		fprintf(stderr, "SAFE (calc_hitbox): Invalid angle: %d\n", angle);
		return 0.0;
	}

	for (int i = 0; i < DIST_VECS; i++) {
		float value = fabs(SIDE_WIDTH / cos(((float)i - angle + 90.0) / 180.0 * M_PI));
		hitbox[i] = min(value, MAX_DISTANCE);
	}
	return 0;
}

int predict_angle(int direction, double speed, double steering) {

	int angle = -1;

	if (direction == FORWARDS) {
		angle = (DIST_VECS - 1) / 2;
		angle += (int) (STEERING_PREDICT * steering) * (1 + SPEED_PREDICT * speed/0.58);

	} else if (direction == BACKWARDS) {
		angle = 0;
		angle += (int) (STEERING_PREDICT * steering) * (1 + SPEED_PREDICT * speed/0.58);

	} else {
		return (DIST_VECS - 1) / 2;
	}

	return (angle + DIST_VECS) % DIST_VECS;
}

int too_close(float *distance, double cmd_speed, int direction) {

	float front_left  = condense_data(distance, CONDENSE_WIDTH, FRONT_LEFT);
	float front       = condense_data(distance, CONDENSE_WIDTH, FRONT);
	float front_right = condense_data(distance, CONDENSE_WIDTH, FRONT_RIGHT);
	float back_left   = condense_data(distance, CONDENSE_WIDTH, BACK_LEFT);
	float back        = condense_data(distance, CONDENSE_WIDTH, BACK);
	float back_right  = condense_data(distance, CONDENSE_WIDTH, BACK_RIGHT);

	// printf("SAFE: dist_in_direction %f \n", dist_in_direction);
	if (direction == FORWARDS && cmd_speed < 0.0) {
		if(front_left < CLOSEST_ALLOWED || front_right < CLOSEST_ALLOWED || front < CLOSEST_ALLOWED) {
			fprintf(stderr, "SAFE: Obstacle in front, cant drive forwards\n");
			return 1; // deny action
		}
	} else if (direction == BACKWARDS && cmd_speed > 0.0) {
		if(back_left < CLOSEST_ALLOWED || back_right < CLOSEST_ALLOWED || back < CLOSEST_ALLOWED) {
			fprintf(stderr, "SAFE: Obstacle in back, cant drive backwards\n");
			return 1; // deny action
		}
	}
	return 0;	// action is safe
}

int subtract_silhouette(float *distance) {

	for (int i = 0; i < DIST_VECS; i++) {
		distance[i] -= silhouette[i];
	}
	return 0;
}

float condense_data(float *distance, int width, int angle) {

	if (angle < 0 || angle > 359) {
		fprintf(stderr, "SAFE: Invalid angle: %d\n", angle);
		return 0.0;
	}

	float sum = 0.0;

	int angle_plus = angle + DIST_VECS;

	for (int i = angle_plus - width/2; i <= angle_plus + width/2; i++) {
		// printf("i%%DIST_VECS: %d \n", i%DIST_VECS);
		sum += distance[i%DIST_VECS];
	}
	// printf("\n\n");

	return sum / width;
}


int compare_direction(double *vec1, double *vec2, int size) {

	double skalarprod =  0;
	for (int i = 0; i < size; i++) {
		skalarprod += vec1[i] * vec2[i];
	}

	if (skalarprod > 0.0) {
		return FORWARDS;
	} else if (skalarprod < 0.0){
		return BACKWARDS;
	} else {
		return STOPPED;
	}
}

int touching(data_from_wb_msg_t data_from_wb) {

	int touching = 0;
	int currently_touching = 0;
	for (int i=0; i<DIST_VECS; i++) {
		if (data_from_wb.distance[i] < silhouette[i] && currently_touching == 0) {
			currently_touching = 1;
		} else if (!(data_from_wb.distance[i] < silhouette[i]) && currently_touching == 1) {
			currently_touching = 0;
			touching ++;
		}
	}
	if (touching != 0) {
		printf("SAFE: !CRASH! !CRASH! !CRASH! !CRASH! !CRASH! \n");
	}
	return touching;
}


int check_for_tipover(data_from_wb_msg_t data_from_wb) {

	if (fabs(data_from_wb.actual_gps[1] - 0.026) > 0.02) {
		return -1;
	} else {
		return 0;
	}
}
