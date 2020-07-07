#include "backend/backend_worker.h"

#include <stdio.h>
#include <string.h>

#include "backend/backend_com.h"

#define TIMESTEP 32

void *backend_worker(void *ptr) {

	arg_struct_t *arg_struct = (arg_struct_t*) ptr;

	printf("BACKEND_WORKER: Initalizing\n");

	data_to_bcknd_msg_t data_to_bcknd;
	memset(&data_to_bcknd, 0, sizeof(data_to_bcknd_msg_t));
	cmd_from_bcknd_msg_t cmd_from_bcknd;
	memset(&cmd_from_bcknd, 0, sizeof(cmd_from_bcknd_msg_t));

	com_init();

	printf("BACKEND_WORKER: Running\n");

	while (1) {

		// printf("BACKEND_WORKER: Waiting to recv \n");
		// printf("BACKEND_WORKER: link_qual %f \n", link_qualitiy(0));
		if (com_recv(&cmd_from_bcknd) < 0) {
			// printf("BACKEND_WORKER: Error on recv\n");  // Already gets printed by com_recv
			continue;
		}

		switch (cmd_from_bcknd.request) {

			case COMMAND_ONLY:
				// printf("BACKEND_WORKER: COMMAND_ONLY msg received\n");

				// Move data to ITC struct for webot_worker to read
				pthread_mutex_lock(arg_struct->itc_cmd_lock);
				memcpy(arg_struct->itc_cmd, &cmd_from_bcknd, sizeof(cmd_from_bcknd_msg_t));
				pthread_mutex_unlock(arg_struct->itc_cmd_lock);
				break;

			case REQUEST_ONLY:
				// printf("BACKEND_WORKER: REQUEST_ONLY msg received\n");

				// Get data from ITC struct for transmission to backend
				while (arg_struct->itc_data->sim_time == data_to_bcknd.sim_time) {
					// wait for new data in rtc struct
				}
				pthread_mutex_lock(arg_struct->itc_data_lock);
				memcpy(&data_to_bcknd, arg_struct->itc_data, sizeof(data_to_bcknd_msg_t));
				arg_struct->itc_data->action_denied = 0;
				arg_struct->itc_data->touching = 0;
				pthread_mutex_unlock(arg_struct->itc_data_lock);

				// Transmit data to backend
				com_send(data_to_bcknd);
				break;

			case COMMAND_REQUEST:
				// printf("BACKEND_WORKER: COMMAND_REQUEST msg received\n");

				// Move data to ITC struct for webot_worker to read
				pthread_mutex_lock(arg_struct->itc_cmd_lock);
				memcpy(arg_struct->itc_cmd, &cmd_from_bcknd, sizeof(cmd_from_bcknd_msg_t));
				pthread_mutex_unlock(arg_struct->itc_cmd_lock);

				// Get data from ITC struct for transmission to backend
				while (arg_struct->itc_data->sim_time == data_to_bcknd.sim_time) {
					// wait for new data in rtc struct
				}
				pthread_mutex_lock(arg_struct->itc_data_lock);
				memcpy(&data_to_bcknd, arg_struct->itc_data, sizeof(data_to_bcknd_msg_t));
				arg_struct->itc_data->action_denied = 0;
				arg_struct->itc_data->touching = 0;
				pthread_mutex_unlock(arg_struct->itc_data_lock);

				// Transmit data to backend
				com_send(data_to_bcknd);
				break;

			case EVERY_X:

			// Move data to ITC struct for webot_worker to read
			pthread_mutex_lock(arg_struct->itc_cmd_lock);
			memcpy(arg_struct->itc_cmd, &cmd_from_bcknd, sizeof(cmd_from_bcknd_msg_t));
			pthread_mutex_unlock(arg_struct->itc_cmd_lock);

			// Get data from ITC struct for transmission to backend
			float next_packet_time = data_to_bcknd.sim_time + TIMESTEP/1000.0 * cmd_from_bcknd.every_x;
			while (arg_struct->itc_data->sim_time <= next_packet_time) {
				// wait for new data in rtc struct
				//
			}
			pthread_mutex_lock(arg_struct->itc_data_lock);
			memcpy(&data_to_bcknd, arg_struct->itc_data, sizeof(data_to_bcknd_msg_t));
			arg_struct->itc_data->action_denied = 0;
			arg_struct->itc_data->touching = 0;
			pthread_mutex_unlock(arg_struct->itc_data_lock);

			// Transmit data to backend
			com_send(data_to_bcknd);
			break;

			case UNDEF:
			default:
				printf("BACKEND_WORKER: Invalid Request from Backend\n");
				break;
		}

	}

	com_deinit();

	return NULL;
}
