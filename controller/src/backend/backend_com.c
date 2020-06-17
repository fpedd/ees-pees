#include "backend/backend_com.h"

#include <stdio.h>
#include <string.h>
#include <math.h>
#include <errno.h>

#include "backend/udp.h"
#include "util.h"

#define TIME_OFFSET_ALLOWED 1.0 // in seconds

static unsigned int msg_cnt;
static float link_qual;

const char* response_request_str[] = {"UNDEF", "COMMAND_ONLY", "REQUEST_ONLY", "COMMAND_REQUEST"};
const char* discrete_move_str[] = {"NONE", "UP", "LEFT", "DOWN", "RIGHT"};
const char* direction_type_str[] = {"STEERING", "HEADING"};


int com_init() {

	udp_init();

	msg_cnt = 0;
	link_qual = 1.0;

	return 0;
}

int com_deinit() {

	udp_deinit();

	return 0;
}

float link_qualitiy(float factor) {

	link_qual += factor;

	if (link_qual < 0.0) {
		link_qual = 0.0;
	} else if (link_qual > 1.0) {
		link_qual = 1.0;
	}

	return link_qual;
}


int com_send(ext_to_bcknd_msg_t data) {

	data.msg_cnt = msg_cnt;
	data.time_stmp = get_time();

	int len = udp_send((char *)&data, sizeof(ext_to_bcknd_msg_t));
	if (len < (int)sizeof(ext_to_bcknd_msg_t)) {
		fprintf(stderr, "BACKEND_COM: ERROR: com send too short, is %d, should %ld\n",
		        len, sizeof(ext_to_bcknd_msg_t));
		link_qualitiy(-0.025);
		return -1;
	}

	link_qualitiy(0.1);

	// we sent a message, so increment count
	msg_cnt++;

	return 0;
}

int com_recv(bcknd_to_ext_msg_t *data) {

	memset(data, 0, sizeof(bcknd_to_ext_msg_t));

	int len = udp_recv((char *)data, sizeof(bcknd_to_ext_msg_t));

	if (len < (int)sizeof(bcknd_to_ext_msg_t)) {
		if (errno != 11) { // dont print error if we had a timeout
			fprintf(stderr, "BACKEND_COM: ERROR: com recv too short, is %d, should %ld\n",
			        len, sizeof(bcknd_to_ext_msg_t));
			link_qualitiy(-0.1);
		}
		link_qualitiy(-0.01);
		return -1;
	}

	if (fabs(get_time() - data->time_stmp) > TIME_OFFSET_ALLOWED) {
		fprintf(stderr, "BACKEND_COM: ERROR: com recv time diff to big, local %f, remote %f, diff %f \n",
		        get_time(), data->time_stmp, fabs(get_time() - data->time_stmp));
		link_qualitiy(-0.1);
		return -2;
	}

	if (data->msg_cnt != msg_cnt) {
		fprintf(stderr, "BACKEND_COM: ERROR: com recv msg_cnt %d does not match msg %lld \n",
		        msg_cnt, data->msg_cnt);
		// we got our messages out of sync, but for now lets just resync
		msg_cnt = data->msg_cnt + 1;
		link_qualitiy(-0.1);
		return -3;
	}

	// we received a message, so increment count
	msg_cnt++;

	link_qualitiy(0.1);

	return len;
}
