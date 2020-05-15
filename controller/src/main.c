#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>

#include "backend/backend_worker.h"
#include "backend/backend_com.h"
#include "webots/webot_worker.h"
#include "webots/wb_com.h"
#include "util.h"


int main(int argc, char **argv) {

	(void) argc;
	(void) argv;

	ext_to_bcknd_msg_t ext_to_bcknd_msg;
	memset(&ext_to_bcknd_msg, 0, sizeof(ext_to_bcknd_msg_t));

	bcknd_to_ext_msg_t bcknd_to_ext_msg;
	memset(&bcknd_to_ext_msg, 0, sizeof(bcknd_to_ext_msg_t));

	arg_struct_t arg_struct;
	arg_struct.ext_to_bcknd = &ext_to_bcknd_msg;
	arg_struct.bcknd_to_ext = &bcknd_to_ext_msg;

	printf("Starting threads from main \n");

	pthread_t webot_worker_thread, backend_worker_thread;

	int ret1 = pthread_create(&webot_worker_thread, NULL, (void *) &webot_worker, &arg_struct);
	int ret2 = pthread_create(&backend_worker_thread, NULL, (void *) &backend_worker, &arg_struct);

	if (ret1 != 0 || ret2 != 0){
		fprintf(stderr, "MAIN: ERROR on creating threads\n");
		exit(1);
	} else {
		pthread_join(webot_worker_thread, NULL);
		pthread_join(backend_worker_thread, NULL);
	}


	// testing communication
	while (1) {
		// ext_to_bcknd_msg_t first_msg;
		// memset(&first_msg, 0, sizeof(ext_to_bcknd_msg_t));
		//
		// for (int i=0; i<2; i++) {
		// 	first_msg.actual_gps[i] = i + 0.69;
		// }
		// for (int i=0; i<DIST_VECS; i++) {
		// 	first_msg.distance[i] = i + 0.1;
		// }
		//
		// com_send(first_msg);
		// delay(0.2);
		//
		// bcknd_to_ext_msg_t first_msg_resp;
		// com_recv(&first_msg_resp);
		//
		// printf("cnt %lld, time %f, heading %f, speed %f \n",
		//        first_msg_resp.msg_cnt, first_msg_resp.time_stmp,
		//        first_msg_resp.heading, first_msg_resp.speed);
	}

	return 0;
}

// WB THREAD
//
// holen webots <<<<
// umrechen
// senden backend (inter prozess)
// holen backend (inter prozess)
//
// pid loops
// safety
// motor moves
//
// send webots
//
//
// BACKEND THREAD
//
// holen webots (inter prozess)
// senden backend
// holen backend <<<<
// senden webots (inter prozess)
