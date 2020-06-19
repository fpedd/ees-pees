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

#define STEP_SIZE 0.5

float target[2];

int discr_init() {

	memset(target, 0, sizeof(target));

	return 0;
}

int discr_step(cmd_to_wb_msg_t *cmd_to_wb, cmd_from_bcknd_msg_t cmd_from_bcknd,
               data_to_bcknd_msg_t data_to_bcknd, init_to_ext_msg_t init_data, int start) {

	// lets start where the robot currently is at
	if (start == 1) {
		target[0] = round_with_factor(data_to_bcknd.actual_gps[0], STEP_SIZE);
		target[1] = round_with_factor(data_to_bcknd.actual_gps[1], STEP_SIZE);
	}

	// make sure we only do actions once per message
	static unsigned long long last_msg_cnt = -1;
	if (cmd_from_bcknd.msg_cnt != last_msg_cnt) {

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

		last_msg_cnt = cmd_from_bcknd.msg_cnt;

	}

	//print_cood(data_to_bcknd.actual_gps, target);

	return navigate(cmd_to_wb, data_to_bcknd, init_data, target);
}

void print_cood(float actual[2], float target[2]) {
	printf("actual: %f %f \n", actual[0], actual[1]);
	printf("target: %f %f \n", target[0], target[1]);
}
