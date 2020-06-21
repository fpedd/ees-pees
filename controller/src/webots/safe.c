#include "webots/safe.h"

#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <math.h>
#include <float.h>

#include "backend/backend_com.h"
#include "silhouette.h"
#include "util.h"

// (should be odd for symmetry!) number of entries combined to one sensor datum
#define CONDENSE_WIDTH 31

#define STEPS_STOP 30.0
#define CLOSEST_ALLOWED 0.04


int safety_check(init_to_ext_msg_t init_data, data_from_wb_msg_t data_from_wb,
	             cmd_to_wb_msg_t* cmd_to_wb) {


	int action_denied = 0;


	// get distance array subtract shiloutte
	float distance[DIST_VECS];
	memcpy(&distance, data_from_wb.distance, sizeof(float) * DIST_VECS);
	subtract_silhouette(distance);

	// get condensed sensor data in moving direction
	float dist_front, dist_back;
	dist_front = condense_data(distance, FORWARDS);
	dist_back = condense_data(distance, BACKWARDS);

	static float last_dist_front = dist_front;
	static float last_dist_back = dist_back;

	int direction = STOPPED;

	float diff_front = dist_front - last_dist_front;
	float diff_back = dist_back - last_dist_back;
	// printf("SAFE: diff_front: %f diff_back %f\n", diff_front, diff_back);
	if (diff_front <= 0.0 && diff_back >= 0.0) {
		direction = FORWARDS;
	} else if (diff_back <= 0.0 && diff_front >= 0.0) {
		direction = BACKWARDS;
	}

	float dist_in_direction = FLT_MAX;
	if (direction == FORWARDS) {
		// printf("SAFE: direction = FORWARDS\n");
		dist_in_direction = dist_front;
	} else if (direction == BACKWARDS) {
		// printf("SAFE: direction = BACKWARDS\n");
		dist_in_direction = dist_back;
		// printf("SAFE: direction = %d\n", direction);
	} else {
		// dist_in_direction = min(dist_front, dist_back);
	}

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

	// Failsafe: dont drive forwards/backwards if obstacle is close
	if (dist_front < CLOSEST_ALLOWED && cmd_to_wb->speed < 0.0) {
		// printf("SAFE: Cant drive forward!\n");
		cmd_to_wb->speed = 0;
		action_denied = 1;

	} else if (dist_back < CLOSEST_ALLOWED && cmd_to_wb->speed > 0.0) {
		// printf("SAFE: Cant drive backward!\n");
		cmd_to_wb->speed = 0;
		action_denied = 1;

	}

	// last_gps[0] = data_from_wb.actual_gps[0];
	// last_gps[1] = data_from_wb.actual_gps[2];

	last_dist_front = dist_front;
	last_dist_back = dist_back;


	return action_denied;
}

int direction_from_speed(double speed) {
	if (speed < 0) {
		return FORWARDS;
	} else if (speed > 0){
		return BACKWARDS;
	} else {
		return STOPPED;
	}
}

int subtract_silhouette(float *distance) {

	for (int i = 0; i < DIST_VECS; i++) {
		distance[i] -= silhouette[i];
	}
	return 0;
}

float condense_data(float *distance, int direction) {

	int start;
	float sum = 0.0;

	if (direction == FORWARDS) { // front of robot --> values around index 179

		start = (DIST_VECS - 1) / 2 - CONDENSE_WIDTH / 2;

		for (int i = start; i <= start + CONDENSE_WIDTH; i++) {
			sum += distance[i];
		}

		return sum / CONDENSE_WIDTH;

	} else if (direction == BACKWARDS) { // back of robot --> values around 0

		start = DIST_VECS - CONDENSE_WIDTH / 2;

		// "left" side of 0
		for (int i = start; i < DIST_VECS; i++) {
			sum += distance[i];
		}

		// "right" side of 0
		for (int i = 0; i <= CONDENSE_WIDTH / 2; i++) {
			sum += distance[i];
		}

		return sum / CONDENSE_WIDTH;
	} else {
		return -1.0;
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
