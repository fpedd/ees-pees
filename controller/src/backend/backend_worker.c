#include "backend/backend_worker.h"

#include <stdio.h>
#include <string.h>

#include "backend/backend_com.h"

void *backend_worker(void *ptr) {

	arg_struct_t *arg_struct = (arg_struct_t*) ptr;

	printf("BACKEND_WORKER: Initalizing\n");

	data_to_bcknd_msg_t external_data_to_bcknd;
	memset(&external_data_to_bcknd, 0, sizeof(data_to_bcknd_msg_t));
	cmd_from_bcknd_msg_t external_cmd_from_bcknd;
	memset(&external_cmd_from_bcknd, 0, sizeof(cmd_from_bcknd_msg_t));

	com_init();

	printf("BACKEND_WORKER: Running\n");

	while (1) {

		// printf("BACKEND_WORKER: Waiting to recv \n");
		// printf("BACKEND_WORKER: link_qual %f \n", link_qualitiy(0));
		if (com_recv(&external_cmd_from_bcknd) < 0) {
			// printf("BACKEND_WORKER: Error on recv\n");  // Already gets printed by com_recv
			continue;
		}

		switch (external_cmd_from_bcknd.request) {

			case COMMAND_ONLY:
				// printf("BACKEND_WORKER: COMMAND_ONLY msg received\n");

				// Move data to ITC struct for webot_worker to read
				pthread_mutex_lock(arg_struct->cmd_to_webot_worker_lock);
				memcpy(arg_struct->cmd_from_bcknd, &external_cmd_from_bcknd, sizeof(cmd_from_bcknd_msg_t));
				pthread_mutex_unlock(arg_struct->cmd_to_webot_worker_lock);
				break;

			case REQUEST_ONLY:
				// printf("BACKEND_WORKER: REQUEST_ONLY msg received\n");

				// Get data from ITC struct for transmission to backend
				pthread_mutex_lock(arg_struct->data_to_backend_worker_lock);
				memcpy(&external_data_to_bcknd, arg_struct->data_to_bcknd, sizeof(data_to_bcknd_msg_t));
				pthread_mutex_unlock(arg_struct->data_to_backend_worker_lock);

				// Transmit data to backend
				com_send(external_data_to_bcknd);
				break;

			case COMMAND_REQUEST:
				// printf("BACKEND_WORKER: COMMAND_REQUEST msg received\n");

				// Move data to ITC struct for webot_worker to read
				pthread_mutex_lock(arg_struct->cmd_to_webot_worker_lock);
				memcpy(arg_struct->cmd_from_bcknd, &external_cmd_from_bcknd, sizeof(cmd_from_bcknd_msg_t));
				pthread_mutex_unlock(arg_struct->cmd_to_webot_worker_lock);

				// Get data from ITC struct for transmission to backend
				pthread_mutex_lock(arg_struct->data_to_backend_worker_lock);
				memcpy(&external_data_to_bcknd, arg_struct->data_to_bcknd, sizeof(data_to_bcknd_msg_t));
				pthread_mutex_unlock(arg_struct->data_to_backend_worker_lock);

				// Transmit data to backend
				com_send(external_data_to_bcknd);
				break;

			default:
				printf("BACKEND_WORKER: Invalid Request from Backend\n");
				break;
		}

	}

	com_deinit();

	return NULL;
}
