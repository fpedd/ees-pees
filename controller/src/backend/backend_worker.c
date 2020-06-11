#include "backend/backend_worker.h"

#include <stdio.h>
#include <string.h>

#include "backend/backend_com.h"

void *backend_worker(void *ptr) {

	arg_struct_t *arg_struct = (arg_struct_t*) ptr;

	// Init communication with backend
	printf("BACKEND_WORKER: Initalizing\n");

	ext_to_bcknd_msg_t external_ext_to_bcknd;
	memset(&external_ext_to_bcknd, 0, sizeof(ext_to_bcknd_msg_t));
	bcknd_to_ext_msg_t external_bcknd_to_ext;
	memset(&external_bcknd_to_ext, 0, sizeof(bcknd_to_ext_msg_t));

	com_init();

	// Run backend worker
	printf("BACKEND_WORKER: Running\n");

	while (1) {

		printf("BACKEND_WORKER: Waiting to recv \n");
		// Wait for Message from Backend
		if (com_recv(&external_bcknd_to_ext) < 0) {
			// printf("BACKEND_WORKER: Error on recv");  //Already gets printed by com_recv
			break;
		}

		// Received Message. What Kind of message is it?
		if (external_bcknd_to_ext.request == COMMAND_ONLY) {
			printf("BACKEND_WORKER: COMMAND_ONLY msg received\n");

			// Move data to ITC struct for webot_worker to read
			pthread_mutex_lock(arg_struct->bcknd_to_ext_lock);
			memcpy(arg_struct->bcknd_to_ext, &external_bcknd_to_ext, sizeof(bcknd_to_ext_msg_t));
			pthread_mutex_unlock(arg_struct->bcknd_to_ext_lock);

		} else if (external_bcknd_to_ext.request == REQUEST_ONLY) {
			printf("BACKEND_WORKER: REQUEST_ONLY msg received\n");

			// Get data from ITC struct for transmission to backend
			pthread_mutex_lock(arg_struct->ext_to_bcknd_lock);
			memcpy(&external_ext_to_bcknd, arg_struct->ext_to_bcknd, sizeof(ext_to_bcknd_msg_t));
			pthread_mutex_unlock(arg_struct->ext_to_bcknd_lock);

			printf("BACKEND_WORKER: REQUEST_ONLY answer\n");
			// Transmit data to backend
			com_send(external_ext_to_bcknd);

		} else if (external_bcknd_to_ext.request == COMMAND_REQUEST) {
			printf("BACKEND_WORKER: COMMAND_REQUEST msg received\n");

			// Move data to ITC struct for webot_worker to read
			pthread_mutex_lock(arg_struct->bcknd_to_ext_lock);
			memcpy(arg_struct->bcknd_to_ext, &external_bcknd_to_ext, sizeof(bcknd_to_ext_msg_t));
			pthread_mutex_unlock(arg_struct->bcknd_to_ext_lock);

			// Get data from ITC struct for transmission to backend
			pthread_mutex_lock(arg_struct->ext_to_bcknd_lock);
			memcpy(&external_ext_to_bcknd, arg_struct->ext_to_bcknd, sizeof(ext_to_bcknd_msg_t));
			pthread_mutex_unlock(arg_struct->ext_to_bcknd_lock);

			// Transmit data to backend
			com_send(external_ext_to_bcknd);

		} else {

			printf("BACKEND_WORKER: Invalid Request from Backend\n");
		}
	}

	// for some reason the compiler warns about not having a return value here
	// but doesn't in webot_worker
	return (void *) arg_struct;
}
