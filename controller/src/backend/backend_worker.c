#include "backend/backend_worker.h"

#include <stdio.h>
#include <string.h>

#include "backend/backend_com.h"


#define TIMESTEP 32.0

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

		if (com_recv(&cmd_from_bcknd) < 0) {
			// Dont do any special error handling concerning the backend communication
			continue;
		}

		switch (cmd_from_bcknd.request) {

			case COMMAND_ONLY:

				// Move data to ITC struct for webot_worker to read
				pthread_mutex_lock(arg_struct->itc_cmd_lock);
				memcpy(arg_struct->itc_cmd, &cmd_from_bcknd, sizeof(cmd_from_bcknd_msg_t));
				pthread_mutex_unlock(arg_struct->itc_cmd_lock);
				break;

			case REQUEST_ONLY:

				// Get data from ITC struct for transmission to backend
				pthread_mutex_lock(arg_struct->itc_data_lock);
				memcpy(&data_to_bcknd, arg_struct->itc_data, sizeof(data_to_bcknd_msg_t));
				arg_struct->itc_data->action_denied = 0;
				arg_struct->itc_data->touching = 0;
				pthread_mutex_unlock(arg_struct->itc_data_lock);

				// Transmit data to backend
				com_send(data_to_bcknd);
				break;

			case COMMAND_REQUEST: {

				// Move data to ITC struct for webot_worker to read
				pthread_mutex_lock(arg_struct->itc_cmd_lock);
				memcpy(arg_struct->itc_cmd, &cmd_from_bcknd, sizeof(cmd_from_bcknd_msg_t));
				pthread_mutex_unlock(arg_struct->itc_cmd_lock);

				// Wait for new data in ITC struct according to backends every_x request
				float next_packet_time = arg_struct->itc_data->sim_time + TIMESTEP/1000.0 * cmd_from_bcknd.every_x;
				while (arg_struct->itc_data->sim_time < next_packet_time - (TIMESTEP*0.2)/1000.0);

				// Get data from ITC struct for transmission to backend
				pthread_mutex_lock(arg_struct->itc_data_lock);
				memcpy(&data_to_bcknd, arg_struct->itc_data, sizeof(data_to_bcknd_msg_t));
				arg_struct->itc_data->action_denied = 0;
				arg_struct->itc_data->touching = 0;
				pthread_mutex_unlock(arg_struct->itc_data_lock);

				// Transmit data to backend
				com_send(data_to_bcknd);
				break;
			}

			case GRID_MOVE: {

				// Move data to ITC struct for webot_worker to read
				pthread_mutex_lock(arg_struct->itc_cmd_lock);
				memcpy(arg_struct->itc_cmd, &cmd_from_bcknd, sizeof(cmd_from_bcknd_msg_t));
				pthread_mutex_unlock(arg_struct->itc_cmd_lock);

				// Wait for new data in ITC struct
				float next_packet_time = arg_struct->itc_data->sim_time + TIMESTEP/1000.0 * 3;
				while (arg_struct->itc_data->sim_time < next_packet_time - (TIMESTEP*0.2)/1000.0);

				// Wait till the discrete move is done by the PID controller
				while (arg_struct->itc_data->discr_act_done == false);

				// Get data from ITC struct for transmission to backend
				pthread_mutex_lock(arg_struct->itc_data_lock);
				memcpy(&data_to_bcknd, arg_struct->itc_data, sizeof(data_to_bcknd_msg_t));
				arg_struct->itc_data->action_denied = 0;
				arg_struct->itc_data->touching = 0;
				pthread_mutex_unlock(arg_struct->itc_data_lock);

				// Transmit data to backend
				com_send(data_to_bcknd);
				break;
			}

			case UNDEF:
			default:
				fprintf(stderr, "BACKEND_WORKER: Invalid Request from Backend\n");
				break;
		}

	}

	com_deinit();

	return NULL;
}
