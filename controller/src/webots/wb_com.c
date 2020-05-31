#include "webots/wb_com.h"

#include <stdio.h>
#include <string.h>
#include <errno.h>

#include "webots/tcp.h"
#include "util.h"

void wb_init_com(){

	tcp_init();
	tcp_accept();

}


int wb_send(ext_to_wb_msg_t data) {

	int len = tcp_send((char *) &data, sizeof(ext_to_wb_msg_t));
	if (len < (int) sizeof(ext_to_wb_msg_t)) {
		fprintf(stderr, "WB_COM: wb_send did not send complete data, is %d, should %ld \n",
		       len, sizeof(ext_to_wb_msg_t));
	}

	return 0;
}

int wb_recv_init(init_to_ext_msg_t *data){

	memset(data, 0, sizeof(init_to_ext_msg_t));

	int len = tcp_recv((char *)data, sizeof(init_to_ext_msg_t));
	if (len != (int) sizeof(init_to_ext_msg_t)) {
		fprintf(stderr, "WB_COM: wb_recv did not receive complete data, is %d, should %ld \n",
		       len, sizeof(ext_to_wb_msg_t));
	}

	return 0;
}


int wb_recv(wb_to_ext_msg_t *data) {

	memset(data, 0, sizeof(wb_to_ext_msg_t));

	int len = tcp_recv((char *)data, sizeof(wb_to_ext_msg_t));
	if (len != (int) sizeof(wb_to_ext_msg_t)) {
		fprintf(stderr, "WB_COM: wb_recv did not receive complete data, is %d, should %ld \n",
		       len, sizeof(wb_to_ext_msg_t));
	}

	return 0;
}

void wb_test_com(){

	// printf("Starting Coms on ext Controller\n");
	wb_init_com();

	while(1) {

		wb_to_ext_msg_t test_buf;
		memset(&test_buf, 0, sizeof(wb_to_ext_msg_t));

		// printf("receiving test_msg on ext Controller\n");
		wb_recv(&test_buf);

		printf("===========RECEIVED=========\n");
		printf("actual_gps: x=%f, y=%f, z=%f\n", test_buf.actual_gps[0], test_buf.actual_gps[1], test_buf.actual_gps[2]);
		printf("============================\n");


		ext_to_wb_msg_t test_msg;
		memset(&test_msg, 0, sizeof(ext_to_wb_msg_t));

		test_msg.heading = 0.8;
		test_msg.speed = -0.20;

		// printf("Sending test_msg on ext Controller\n");
		wb_send(test_msg);
	}

	tcp_close ();

}
