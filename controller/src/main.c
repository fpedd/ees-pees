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

	data_to_bcknd_msg_t itc_data_to_backend_worker;
	memset(&itc_data_to_backend_worker, 0, sizeof(data_to_bcknd_msg_t));

	cmd_to_ext_msg_t itc_cmd_to_webot_worker;
	memset(&itc_cmd_to_webot_worker, 0, sizeof(cmd_to_ext_msg_t));

	pthread_mutex_t data_to_backend_worker_lock;
	pthread_mutex_t cmd_to_webot_worker_lock;

	if ((pthread_mutex_init(&data_to_backend_worker_lock, NULL) |
	     pthread_mutex_init(&cmd_to_webot_worker_lock, NULL)) != 0) {
		fprintf(stderr, "MAIN: ERROR on creating mutexes\n");
		return 1;
	}

	arg_struct_t arg_struct;
	arg_struct.data_to_bcknd      = &itc_data_to_backend_worker;
	arg_struct.data_to_backend_worker_lock = &data_to_backend_worker_lock;
	arg_struct.cmd_to_ext      = &itc_cmd_to_webot_worker;
	arg_struct.cmd_to_webot_worker_lock = &cmd_to_webot_worker_lock;

	pthread_t webot_worker_thread, backend_worker_thread;

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
