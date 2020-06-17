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

int discr_step(ext_to_wb_msg_t *ext_to_wb, bcknd_to_ext_msg_t bcknd_to_ext,
               ext_to_bcknd_msg_t ext_to_bcknd, init_to_ext_msg_t init_data, int start) {

	// lets start where the robot currently is at
	if (start == 1) {
		memcpy(target, ext_to_bcknd.actual_gps, sizeof(target));
	}

	// make sure we only do actions once per message
	static unsigned long long last_msg_cnt = -1;
	if (bcknd_to_ext.msg_cnt != last_msg_cnt) {

		switch (bcknd_to_ext.move) {
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

		last_msg_cnt = bcknd_to_ext.msg_cnt;

	}

	//print_cood(ext_to_bcknd.actual_gps, target);

	return navigate(ext_to_wb, ext_to_bcknd, init_data, target);
}

void print_cood(float actual[2], float target[2]) {
	printf("actual: %f %f \n", actual[0], actual[1]);
	printf("target: %f %f \n", target[0], target[1]);
}
