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

// Defines to fine tune the angle prediction for hitbox calculation (not used)
#define SPEED_PREDICT 0.0
#define STEERING_PREDICT 45.0

#define STEPS_MAX  1000000.0
#define STEPS_STOP 10.0        // if number of steps till obstacle lower than this, deny action
#define STEPS_SLOW 25.0        // if number of steps till obstacle lower than this, slow down
#define CLOSEST_ALLOWED 0.04   // if distance in move direction lower than this, STOP

// hitbox size to each side of the robot
#define SIDE_WIDTH 0.08
#define MAX_DISTANCE 3.4


/* Safety layer on the external controller side
 * Checks how long the robot will take until it hits an obstacle and reacts accordingly
 */
int safety_check(init_to_ext_msg_t init_data, data_from_wb_msg_t data_from_wb, cmd_to_wb_msg_t* cmd_to_wb) {

	/***** Initialize safety *****/
	// Initialize flag whether we intervened for safety reasons
	int action_denied = 0;

	// Get lidar distance array and subtract silhouette from it
	float distance[DIST_VECS];
	memcpy(&distance, data_from_wb.distance, sizeof(float) * DIST_VECS);
	subtract_silhouette(distance);

	// Calculate the zone in which obstacles should be regarded as "dangerous"
	float hitbox[DIST_VECS];
	calc_hitbox(hitbox, 0);


	/***** Determine direction the robot is moving in *****/
	// Initialize last gps position
	static double last_gps[2] = {data_from_wb.actual_gps[0], data_from_wb.actual_gps[2]};

	// Get movement direction vector from gps data
	double move_vec[2];
	move_vec[0] = data_from_wb.actual_gps[0] - last_gps[0];
	move_vec[1] = data_from_wb.actual_gps[2] - last_gps[1];

	// Normalize movement vector
	double length = sqrt(pow(move_vec[0], 2) + pow(move_vec[1], 2));
	move_vec[0] = move_vec[0] / length;
	move_vec[1] = move_vec[1] / length;

	// Get roboter heading from compass data to compare it to movement vector
	double compass[2];
	compass[0] = data_from_wb.compass[2];
	compass[1] = data_from_wb.compass[0];

	// Determine direction the robot is moving in
	int direction = compare_direction(move_vec, compass, 2);


	/***** Check how many timesteps we will take  *****/
	// Calculate how far we move in one timestep at the current speed
	float steps_till_crash[DIST_VECS/2];
	double movement_per_step = data_from_wb.current_speed * init_data.timestep / 1000;

	// Determine which part of the lidar array is relevant due to our movement direction
	int start, stop;
	if (direction == FORWARDS) {
		start = 90;
		stop = 269;
	} else {
		start = 270;
		stop = 89 + DIST_VECS;
	}

	// Calculate the timesteps until we will collide with a obstacle (in direction of movement)
	for (int i = start, j = 0; i <= stop ; i++, j++) {
		if (distance[i%DIST_VECS] < hitbox[i%DIST_VECS]) {
			steps_till_crash[j] = distance[i%DIST_VECS] / movement_per_step;
		} else {
			steps_till_crash[j] = STEPS_MAX;
		}
	}

	// Determine lowest number of timesteps till collision
	int min_i = 0;
	float min_steps = FLT_MAX;
	for (int i = 0; i < DIST_VECS/2; i++) {
		if (steps_till_crash[i] < min_steps) {
			min_steps = min_floor(steps_till_crash[i], min_steps);
			min_i = i;
		}
	}
	min_i = (min_i + start) % DIST_VECS;


	/***** React to the "danger level" to avoid crash *****/
	// Robot is extremly close to obstacle --> Overwrite speed command
	// and send action_denied to backend
	if (min_steps <= 0.0) {
		// printf("SAFE: Obstacle is in silhouette!\n");
		cmd_to_wb->speed = 0;
		action_denied = 1;

	// Robot is close to obstacle --> Overwrite speed command
	// and send action_denied to backend
	} else if (min_steps <= STEPS_STOP) {
		// fprintf(stderr, "SAFE: Close to obstacle. MIN_STEPS: %f\n", min_steps);
		cmd_to_wb->speed = 0;
		action_denied = 1;

	// Robot is approaching to obstacle --> Overwrite speed command to slow down
	} else if (min_steps <= STEPS_SLOW){
		// fprintf(stderr, "SAFE: Slowing down. MIN_STEPS: %f\n", min_steps);
		cmd_to_wb->speed = 0;
	}


	/***** Stop robot if very close to obstacle *****/
	// Stop robot from moving very slowly towards very close obstacles
	if (too_close_to_obstacle(distance, cmd_to_wb->speed, direction) == 1) {
		cmd_to_wb->speed = 0;
		action_denied = 1;
		// Stops robot from "wiggling" into an obstacle, but makes training harder
		// cmd_to_wb->heading = 0;
	}

	// Update last_gps with current position
	last_gps[0] = data_from_wb.actual_gps[0];
	last_gps[1] = data_from_wb.actual_gps[2];

	return action_denied;
}


/* Calculates a (somewhat) rectangular zone around the robot, with a width of
 * SIDE_WIDTH to each side and MAX_DISTANCE, which is the maximum range of the
 * lidar sensor minus a small deadband to the front and back.
 * Angle parameter can be used to turn this hitbox in the steering direction to
 * predict obstacles in the path, but is not used by us in our implementation
 */
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

/* Predicts the angle the robot is going to move in based on the current movement command.
 * STEERING_PREDICT and SPEED_PREDICT can be used to fine tune the scaling of each.
 */
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


/* Acts as a failsafe to stop the robot from moving very slowly into an obstacle.
 * This is necessary because our safety works relative to the speed and would not
 * stop the robot at low speeds, until obstacles can get closer than the minimum
 * lidar range. This leads to the robot not recognizing the obstacle and speeding
 * up again
 */
int too_close_to_obstacle(float *distance, double cmd_speed, int direction) {

	// Get averaged sensor data at the corners, frontside  and backside of the silhouette
	float front_left  = condense_data(distance, 20, 127);
	float front       = condense_data(distance, 20, 179);
	float front_right = condense_data(distance, 20, 232);
	float back_left   = condense_data(distance, 20, 39);
	float back        = condense_data(distance, 20, 0);
	float back_right  = condense_data(distance, 20, 320);

	// Check whether an obstacle in movement direction is closer than allowed
	if (direction == FORWARDS && cmd_speed < 0.0) {
		if(front_left < CLOSEST_ALLOWED || front_right < CLOSEST_ALLOWED || front < CLOSEST_ALLOWED) {
			// fprintf(stderr, "SAFE: Obstacle in front, cant drive forwards\n");
			return 1; // deny action
		}
	} else if (direction == BACKWARDS && cmd_speed > 0.0) {
		if(back_left < CLOSEST_ALLOWED || back_right < CLOSEST_ALLOWED || back < CLOSEST_ALLOWED) {
			// fprintf(stderr, "SAFE: Obstacle in back, cant drive backwards\n");
			return 1; // deny action
		}
	}
	return 0; // action is safe
}


int subtract_silhouette(float *distance) {

	for (int i = 0; i < DIST_VECS; i++) {
		distance[i] -= silhouette[i];
	}
	return 0;
}


/* Calculate average from sensor data in direction of 'angle' with a width of 'width'
 */
float condense_data(float *distance, int width, int angle) {

	if (angle < 0 || angle > 359) {
		fprintf(stderr, "SAFE: Invalid angle: %d\n", angle);
		return 0.0;
	}

	float sum = 0.0;
	int angle_plus = angle + DIST_VECS;    // To facilitate traversing the array boundaries

	for (int i = angle_plus - width/2; i <= angle_plus + width/2; i++) {
		sum += distance[i%DIST_VECS];
	}

	return sum / width;
}


/* Determine whether to vectors show in the same general direction
 */
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


/* Determine whether an obstacle is closer than the defined silhouette
 */
int touching(data_from_wb_msg_t data_from_wb) {

	int touching = 0;
	for (int i=0; i<DIST_VECS; i++) {
		if (data_from_wb.distance[i] < silhouette[i]) {
			touching = 1;
		}
	}

	return touching;
}


/* Determine whether the robot tipped over
 */
int check_for_tipover(data_from_wb_msg_t data_from_wb) {

	if (fabs(data_from_wb.actual_gps[1] - 0.026) > 0.02) {
		return -1;
	} else {
		return 0;
	}
}
