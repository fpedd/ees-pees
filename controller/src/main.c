#include <stdio.h>
#include <string.h>

#include "backend/backend_com.h"
#include "webots/wb_com.h"
#include "pid.h"
#include "util.h"


int main(int argc, char **argv) {

	(void) argc;
	(void) argv;

	com_init();

	// testing communication
	while (1) {
		ext_to_bcknd_msg_t first_msg;
		memset(&first_msg, 0, sizeof(ext_to_bcknd_msg_t));

		for (int i=0; i<2; i++) {
			first_msg.actual_gps[i] = i + 0.69;
		}

		for (int i=0; i<DIST_VECS; i++) {
			first_msg.distance[i] = i + 0.1;
		}

		com_send(first_msg);
		delay(0.2);

		bcknd_to_ext_msg_t first_msg_resp;
		com_recv(&first_msg_resp);

		printf("cnt %lld, time %f, heading %f, speed %f \n",
		first_msg_resp.msg_cnt, first_msg_resp.time_stmp,
		first_msg_resp.heading, first_msg_resp.speed);
	}

	return 0;
}
