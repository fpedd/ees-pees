#include "backend/backend_worker.h"

#include <stdio.h>
#include <string.h>

#include "backend/backend_com.h"

void backend_worker(arg_struct_t *arg_struct) {

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

		/***** 1) Move data via internal message struct to external message struct for transmission *****/
		pthread_mutex_lock(arg_struct->ext_to_bcknd_lock);
		memcpy(&external_ext_to_bcknd, arg_struct->ext_to_bcknd, sizeof(ext_to_bcknd_msg_t));
		pthread_mutex_unlock(arg_struct->ext_to_bcknd_lock);

		/***** 2) Transmit data to backend *****/
		com_send(external_ext_to_bcknd);

		/***** 3) Block to receive data from backend, else time out *****/
		if (com_recv(&external_bcknd_to_ext) > 0) {

			// TODO: catch time out and react accordingly

			// printf("BACKEND_WORKER: heading from backend: %f \n", external_bcknd_to_ext.heading);
			// printf("BACKEND_WORKER: speed from backend: %f \n", external_bcknd_to_ext.speed);

			/***** 4) Move data via internal message struct to external message struct for transmission *****/
			pthread_mutex_lock(arg_struct->bcknd_to_ext_lock);
			memcpy(arg_struct->bcknd_to_ext, &external_bcknd_to_ext, sizeof(bcknd_to_ext_msg_t));
			pthread_mutex_unlock(arg_struct->bcknd_to_ext_lock);
		}

	}

}
