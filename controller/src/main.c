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

	pthread_mutex_t ext_to_bcknd_lock;
	pthread_mutex_t bcknd_to_ext_lock;

	if ((pthread_mutex_init(&ext_to_bcknd_lock, NULL) |
	     pthread_mutex_init(&bcknd_to_ext_lock, NULL)) != 0) {
		fprintf(stderr, "MAIN: ERROR on creating mutexes\n");
		return 1;
	}

	arg_struct_t arg_struct;
	arg_struct.ext_to_bcknd      = &ext_to_bcknd_msg;
	arg_struct.ext_to_bcknd_lock = &ext_to_bcknd_lock;
	arg_struct.bcknd_to_ext      = &bcknd_to_ext_msg;
	arg_struct.bcknd_to_ext_lock = &bcknd_to_ext_lock;

	pthread_t webot_worker_thread, backend_worker_thread;

	printf("MAIN: Starting threads from main \n");
	printf("MAIN: Starting threads from main \n");

	int ret1 = pthread_create(&webot_worker_thread, NULL, &webot_worker, &arg_struct);
	int ret2 = pthread_create(&backend_worker_thread, NULL, &backend_worker, &arg_struct);

	if (ret1 != 0 || ret2 != 0){
		fprintf(stderr, "MAIN: ERROR on creating threads\n");
		return 2;
	} else {
		pthread_join(webot_worker_thread, NULL);
		pthread_join(backend_worker_thread, NULL);
	}

	while (1) {
		// TODO: put this boi to sleep
	}

	return 0;
}
