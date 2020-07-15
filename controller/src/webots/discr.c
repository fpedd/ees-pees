#include "webots/discr.h"

#include <stdio.h>
#include <string.h>
#include <math.h>
#include <float.h>

#include "util.h"
#include "webots/pid.h"
#include "webots/drive.h"
#include "webots/wb_com.h"
#include "webots/navi.h"
#include "backend/backend_com.h"

// The step size we want to in the webots world [in meters]
#define STEP_SIZE 0.5

// The current target destination the drive function will drive us to
// Its a 2d vector on our "virtual" grid inside the webots world
static float target[2];

// The previous target, needed to revert action in case of action denied
static float last_target[2];

int discr_init() {

	memset(target, 0, sizeof(target));
	memset(last_target, 0, sizeof(target));

	return 0;
}

int discr_step(cmd_to_wb_msg_t *cmd_to_wb, cmd_from_bcknd_msg_t cmd_from_bcknd,
               data_to_bcknd_msg_t data_to_bcknd, init_to_ext_msg_t init_data,
               int reset, int action_denied) {

	// Start where the robot currently is at
	if (reset == 1) {

		// Use rounding to align the target to "nearest" point on "virtual" grid
		target[0] = round_with_factor(data_to_bcknd.actual_gps[0], STEP_SIZE);
		target[1] = round_with_factor(data_to_bcknd.actual_gps[1], STEP_SIZE);

		// Last target and current target are the same for first step
		last_target[0] = target[0];
		last_target[1] = target[1];
	}

	// Make sure we only do actions once per message
	static unsigned long long last_msg_cnt = -1;
	if (cmd_from_bcknd.msg_cnt != last_msg_cnt) {

		// Update last_target in case we need to revert the move because of safety violations
		last_target[0] = target[0];
		last_target[1] = target[1];

		// Do the move coming from backend by adjusting the target accordingly
		switch (cmd_from_bcknd.move) {
			case UP:
				target[1] += STEP_SIZE;
				break;
			case LEFT:
				target[0] += STEP_SIZE;
				break;
			case DOWN:
				target[1] -= STEP_SIZE;
				break;
			case RIGHT:
				target[0] -= STEP_SIZE;
				break;
			case NONE:
			default:
				fprintf(stderr, "ERROR: discr step invalid step command\n");
				break;
		}

		// Save message count to for check above
		last_msg_cnt = cmd_from_bcknd.msg_cnt;
	}

	// When we did an illegal move and the backend did not disable the safety
	// revert the move to the last "safe" move location
	if (cmd_from_bcknd.disable_safety != 1 && action_denied != 0) {
		// TODO remove print?
		printf("DISCR: Reverted from target [%.2f,%.2f] to [%.2f,%.2f]\n",
		       target[0], target[1], last_target[0], last_target[1]);
		target[0] = last_target[0];
		target[1] = last_target[1];
	}

	// Let the navigate function navigate the robot to the destination
	// It will return 1 when its done (has reached its destination)
	return navigate(cmd_to_wb, data_to_bcknd, init_data, target, reset);
}
