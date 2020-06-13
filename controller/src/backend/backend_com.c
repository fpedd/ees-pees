#include "backend/backend_com.h"

#include <stdio.h>
#include <string.h>
#include <math.h>

#include "backend/udp.h"
#include "util.h"

#define TIME_OFFSET_ALLOWED 1.0 // in seconds

// static unsigned int msg_cnt_out;
static unsigned int msg_cnt_expected;

int com_init() {

	udp_init();

	msg_cnt_expected = 0;

	// msg_cnt_out = 0;
	// msg_cnt_in = (unsigned int)-1;

	// ext_to_bcknd_msg_t first_msg;
	// memset(&first_msg, 0, sizeof(ext_to_bcknd_msg_t));
	// com_send(first_msg);
	//
	// bcknd_to_ext_msg_t first_msg_resp;
	// com_recv(&first_msg_resp);

	return 0;
}

int com_deinit() {

	udp_deinit();

	return 0;
}

int com_send(ext_to_bcknd_msg_t data) {

	data.msg_cnt = msg_cnt_expected;
	data.time_stmp = get_time();

	// We send a message, so next package should be one higher than this
	msg_cnt_expected++;

	int len = udp_send((char *)&data, sizeof(ext_to_bcknd_msg_t));
	if (len < (int)sizeof(ext_to_bcknd_msg_t)) {
		fprintf(stderr, "BACKEND_COM: ERROR: com send too short, is %d, should %ld\n",
		        len, sizeof(ext_to_bcknd_msg_t));
		return -1;
	}

	return 0;
}

int com_recv(bcknd_to_ext_msg_t *data) {
	memset(data, 0, sizeof(bcknd_to_ext_msg_t));

	int len = udp_recv((char *)data, sizeof(bcknd_to_ext_msg_t));

	if (len < (int)sizeof(bcknd_to_ext_msg_t)) {
		fprintf(stderr, "BACKEND_COM: ERROR: com recv too short, is %d, should %ld\n",
		        len, sizeof(bcknd_to_ext_msg_t));
		return -1;
	}

	if (fabs(get_time() - data->time_stmp) > TIME_OFFSET_ALLOWED) {
		fprintf(stderr, "BACKEND_COM: ERROR: com recv time diff to big, local %f, remote %f, diff %f \n",
		        get_time(), data->time_stmp, fabs(get_time() - data->time_stmp));
		return -2;
	}

	if (data->msg_cnt != msg_cnt_expected) {
		fprintf(stderr, "BACKEND_COM: ERROR: com recv msg_cnt_expected %d does not match msg %lld \n",
		msg_cnt_expected, data->msg_cnt);
		// mgs_cnt wasn't right, but next shoud be one higher (unless we send before)
		msg_cnt_expected = data->msg_cnt + 1;
		return -3;
	}

	// Next message shoud have a count one higher (unless we send before)
	msg_cnt_expected++;

	return len;
}
