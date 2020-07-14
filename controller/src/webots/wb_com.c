#include "webots/wb_com.h"

#include <stdio.h>
#include <string.h>
#include <errno.h>

#include "webots/tcp.h"


int wb_init_com(){
	tcp_init();
	tcp_accept();
	return 0;
}

int wb_close(){
	tcp_close();
	return 0;
}

int wb_send(cmd_to_wb_msg_t data) {

	int len = tcp_send((char *) &data, sizeof(cmd_to_wb_msg_t));
	if (len < (int) sizeof(cmd_to_wb_msg_t)) {
		fprintf(stderr, "WB_COM: wb_send did not send complete data, is %d, should %ld \n",
		       len, sizeof(cmd_to_wb_msg_t));
	}

	return 0;
}

int wb_recv_init(init_to_ext_msg_t *data){

	memset(data, 0, sizeof(init_to_ext_msg_t));

	int len = tcp_recv((char *)data, sizeof(init_to_ext_msg_t));
	if (len != (int) sizeof(init_to_ext_msg_t)) {
		fprintf(stderr, "WB_COM: wb_recv did not receive complete data, is %d, should %ld \n",
		       len, sizeof(cmd_to_wb_msg_t));
	}

	return 0;
}

int wb_recv(data_from_wb_msg_t *data) {

	memset(data, 0, sizeof(data_from_wb_msg_t));

	int len = tcp_recv((char *)data, sizeof(data_from_wb_msg_t));
	if (len != (int) sizeof(data_from_wb_msg_t)) {
		fprintf(stderr, "WB_COM: wb_recv did not receive complete data, is %d, should %ld \n",
		       len, sizeof(data_from_wb_msg_t));
	}

	return 0;
}
