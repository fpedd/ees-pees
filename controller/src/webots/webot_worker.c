#include "webots/webot_worker.h"

#include <stdio.h>
#include <string.h>

void webot_worker(arg_struct_t *arg_struct) {

	// get pointer to interprocess communication structs
	ext_to_bcknd_msg_t *internal_ext_to_bcknd = arg_struct->ext_to_bcknd;
	bcknd_to_ext_msg_t *internal_bcknd_to_ext = arg_struct->bcknd_to_ext;

	// init structs for webot <--> ext controller messages
	wb_to_ext_msg_t external_wb_to_ext;
	memset(&external_wb_to_ext, 0, sizeof(wb_to_ext_msg_t));

	ext_to_wb_msg_t external_ext_to_wb;
	memset(&external_ext_to_wb, 0, sizeof(ext_to_wb_msg_t));

	// Init communication with webot
	printf("WEBOT_WORKER: Initalizing\n");
	wb_init_com();
	printf("WEBOT_WORKER: Running\n");


	while (1) {

		printf("WEBOT_WORKER: receiving external_wb_to_ext on ext Controller\n");
		wb_recv(&external_wb_to_ext);

		printf("========WB_WORKER: RECEIVED=========\n");
		printf("WEBOT_WORKER: actual_gps: x=%f, y=%f, z=%f\n", external_wb_to_ext.actual_gps[0],
				external_wb_to_ext.actual_gps[1], external_wb_to_ext.actual_gps[2]);
		printf("====================================\n");

		ext_to_bcknd_msg_t buffer_ext_to_bcknd;
		memset(&buffer_ext_to_bcknd, 0, sizeof(ext_to_bcknd_msg_t));

		// TODO: format to internal_ext_to_bcknd_t
		// TODO: do this inside the conversion function, just some test values here
		buffer_ext_to_bcknd.actual_gps[0] = (float) external_wb_to_ext.actual_gps[0];
		buffer_ext_to_bcknd.actual_gps[1] = (float) external_wb_to_ext.actual_gps[1];

		// TODO: lock mutex internal_ext_to_bcknd
		memcpy(internal_ext_to_bcknd, &buffer_ext_to_bcknd, sizeof(ext_to_bcknd_msg_t));
		// TODO: unlock mutex


		bcknd_to_ext_msg_t buffer_bcknd_to_ext;
		memset(&buffer_bcknd_to_ext, 0, sizeof(bcknd_to_ext_msg_t));

		// TODO: lock mutex internal_bcknd_to_ext
		memcpy(&buffer_bcknd_to_ext, internal_bcknd_to_ext, sizeof(bcknd_to_ext_msg_t));
		// TODO: unlock mutex


		// TODO: run safety and control loops
		// TODO: use funtions form the drive.c / drive.h to convert to webots format
		// TODO: do this inside the conversion function, just some test values here
		external_ext_to_wb.heading = (buffer_bcknd_to_ext.heading - 180) / 180;
		external_ext_to_wb.speed = buffer_bcknd_to_ext.speed /100;

		printf("WEBOT_WORKER: heading to webot: %f \n", external_ext_to_wb.heading);
		printf("WEBOT_WORKER: speed to webot: %f \n", external_ext_to_wb.speed);

		printf("WEBOT_WORKER: Sending external_ext_to_wb on ext Controller\n");
		wb_send(external_ext_to_wb);
	}

}
