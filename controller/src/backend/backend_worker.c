#include "backend/backend_worker.h"

#include <stdio.h>
#include <string.h>

#include "backend/backend_com.h"

void backend_worker(arg_struct_t *arg_struct) {

	printf("BACKEND_WORKER: Initalizing\n");

	ext_to_bcknd_msg_t *internal_ext_to_bcknd = arg_struct->ext_to_bcknd;
	bcknd_to_ext_msg_t *internal_bcknd_to_ext = arg_struct->bcknd_to_ext;

	ext_to_bcknd_msg_t external_ext_to_bcknd;
	memset(&external_ext_to_bcknd, 0, sizeof(ext_to_bcknd_msg_t));

	bcknd_to_ext_msg_t external_bcknd_to_ext;
	memset(&external_bcknd_to_ext, 0, sizeof(bcknd_to_ext_msg_t));

	com_init();

	printf("BACKEND_WORKER: Running\n");


	while (1) {

		// TODO: lock internal_ext_to_bcknd mutex

		// move data via internal message struct to external message struct for transmission
		memcpy(&external_ext_to_bcknd, internal_ext_to_bcknd, sizeof(ext_to_bcknd_msg_t));

		// TODO: unlock internal_ext_to_bcknd mutex

		// printf("BACKEND_WORKER: ========WB_WORKER: RECEIVED=========\n");
		printf("BACKEND_WORKER: actual_gps: x=%f, y=%f\n", external_ext_to_bcknd.actual_gps[0],
				external_ext_to_bcknd.actual_gps[1]);
		// printf("BACKEND_WORKER: ====================================\n");

		// transmit data to backend
		com_send(external_ext_to_bcknd);

		// block to receive data from backend, else time out
		if (com_recv(&external_bcknd_to_ext) > 0) {

			// TODO: catch time out and react accordingly

			// printf("BACKEND_WORKER: heading from backend: %f \n", external_bcknd_to_ext.heading);
			// printf("BACKEND_WORKER: speed from backend: %f \n", external_bcknd_to_ext.speed);

			// TODO: lock internal_bcknd_to_ext mutex

			// move data via internal message struct to external message struct for transmission
			memcpy(internal_bcknd_to_ext, &external_bcknd_to_ext, sizeof(bcknd_to_ext_msg_t));

			// TODO: unlock internal_bcknd_to_ext mutex
		}

	}

}
