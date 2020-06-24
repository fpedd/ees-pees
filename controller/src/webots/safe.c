#include "webots/safe.h"

#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <math.h>
#include <float.h>

#include "backend/backend_com.h"
#include "silhouette.h"
#include "util.h"

#define CONDENSE_WIDTH 11   // (should be odd for symmetry!) number of entries combined to one sensor datum

#define SPEED_PREDICT 0.0
#define STEERING_PREDICT 45.0

#define STEPS_STOP 30.0        // if number of steps till obstacle lower than this, STOP
#define CLOSEST_ALLOWED 0.04   // if distance in move direction lower than this, STOP

// angles with longest distańce in silhoutte (corners of hitbox)
#define FRONT_LEFT    127
#define FRONT         179
#define FRONT_RIGHT   232
#define BACK_LEFT     39
#define BACK          0
#define BACK_RIGHT    320

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

	int direction = compare_direction(move_vec, compass, 2);

	int angle = predict_angle(direction, data_from_wb.current_speed/init_data.maxspeed,
		cmd_to_wb->heading);

	// printf("SAFE: predict_angle %d\n", angle);

	float dist_in_direction = condense_data(distance, angle, CONDENSE_WIDTH);

	// calculate time till obstacle if command is send
	float steps_till_crash = fabs(dist_in_direction / data_from_wb.current_speed) * 1000 / init_data.timestep;

	if (steps_till_crash <= 0.0) {
		printf("SAFE: we crashed!\n");
		cmd_to_wb->speed = 0;
		action_denied = 1;

	} else if (steps_till_crash <= STEPS_STOP) {
		fprintf(stderr, "SAFE: Close to obstacle. steps_till_crash = %f\n", steps_till_crash);
		cmd_to_wb->speed = 0;
		action_denied = 1;
	} else {
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

	float front_left  = condense_data(distance, FRONT_LEFT,  CONDENSE_WIDTH);
	float front       = condense_data(distance, FRONT,       CONDENSE_WIDTH);
	float front_right = condense_data(distance, FRONT_RIGHT, CONDENSE_WIDTH);
	float back_left   = condense_data(distance, BACK_LEFT,   CONDENSE_WIDTH);
	float back        = condense_data(distance, BACK,        CONDENSE_WIDTH);
	float back_right  = condense_data(distance, BACK_RIGHT,  CONDENSE_WIDTH);

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

float condense_data(float *distance, int angle, int width) {

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
