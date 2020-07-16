#include "backend/backend_com.h"

#include <stdio.h>
#include <string.h>
#include <math.h>
#include <errno.h>

#include "backend/udp.h"
#include "util.h"

// The maximum delay we allow on our com between transmission and reception
#define TIME_OFFSET_ALLOWED 1.0 // in seconds

// We keep a continuous count of the messages send and received to and from the backend
static unsigned int msg_cnt;

// This is an "easy to use" indicator in percent [0, 1] for the current link quality
static float link_qual;

// Some string arrays that make the prints look nicer
const char* response_request_str[] = {"UNDEF", "COMMAND_ONLY", "REQUEST_ONLY", "COMMAND_REQUEST", "GRID_MOVE"};
const char* discrete_move_str[] = {"NONE", "UP", "LEFT", "DOWN", "RIGHT"};
const char* direction_type_str[] = {"STEERING", "HEADING"};

int com_init() {

	udp_init();

	// Start with message 0
	msg_cnt = 0;

	// Dont know anything about the link at this point, so start in the middle
	link_qual = 0.5;

	return 0;
}

int com_deinit() {

	udp_deinit();

	return 0;
}

float link_quality(float amt) {

	link_qual += amt;

	if (link_qual < 0.0) {
		link_qual = 0.0;
	} else if (link_qual > 1.0) {
		link_qual = 1.0;
	}

	return link_qual;
}


int com_send(data_to_bcknd_msg_t data) {

	data.msg_cnt = msg_cnt;
	data.time_stmp = get_time();

	int len = udp_send((char *)&data, sizeof(data_to_bcknd_msg_t));
	if (len < (int)sizeof(data_to_bcknd_msg_t)) {
		fprintf(stderr, "BACKEND_COM: ERROR: com send too short, is %d, should %ld\n",
		        len, sizeof(data_to_bcknd_msg_t));

		// There was a serious error in the com, big link_qual penalty
		link_quality(-0.1);

		return -1;
	}

	// We successfully transmitted a message, so increment message count and increase link_qual
	msg_cnt++;
	link_quality(0.1);

	return 0;
}

int com_recv(cmd_from_bcknd_msg_t *data) {

	memset(data, 0, sizeof(cmd_from_bcknd_msg_t));

	int len = udp_recv((char *)data, sizeof(cmd_from_bcknd_msg_t));

	if (len < (int)sizeof(cmd_from_bcknd_msg_t)) {
		if (errno != 11) { // dont print error if we had a timeout
			fprintf(stderr, "BACKEND_COM: ERROR: com recv too short, is %d, should %ld\n",
			        len, sizeof(cmd_from_bcknd_msg_t));

			// There was a serious error in the com, big link_qual penalty
			link_quality(-0.1);
		}

		// There was "only" a timeout in the com, small link_qual penalty
		link_quality(-0.01);

		return -1;
	}

	if (fabs(get_time() - data->time_stmp) > TIME_OFFSET_ALLOWED) {
		fprintf(stderr, "BACKEND_COM: ERROR: com recv time diff to big, local %f, remote %f, diff %f \n",
		        get_time(), data->time_stmp, fabs(get_time() - data->time_stmp));

		// The message is very old, indication for big delays in the com, therefore big link_qual penalty
		link_quality(-0.1);
		return -2;
	}

	if (data->msg_cnt != msg_cnt) {
		fprintf(stderr, "BACKEND_COM: ERROR: com recv msg_cnt %d does not match msg %lld \n",
		        msg_cnt, data->msg_cnt);

		// We got our messages out of sync, lets resync and give big link_qual penalty
		msg_cnt = data->msg_cnt + 1;
		link_quality(-0.1);

		return -3;
	}

	// We successfully received a message, so increment message count and increase link_qual
	msg_cnt++;
	link_quality(0.1);

	return len;
}
