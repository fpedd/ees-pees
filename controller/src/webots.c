#include <stdio.h>
#include <string.h>

#include "com.h"
#include "webots.h"
#include "tcp.h"
#include "util.h"


void wb_init_com(){

	tcp_init();
	tcp_accept();

}

void wb_test_com(){

	printf("Starting Coms on ext Controller\n");
	wb_init_com();

	from_bcknd_msg_t test_msg;
	memset(&test_msg, 0, sizeof(from_bcknd_msg_t));

	test_msg.heading = 5.55;
	test_msg.speed = 6.66;

	printf("Sending test_msg on ext Controller\n");
	wb_send(test_msg);

	to_bcknd_msg_t test_buf;
	memset(&test_buf, 0, sizeof(to_bcknd_msg_t));

	printf("receiving test_msg on ext Controller\n");
	wb_recv(&test_buf);

	printf("===========RECEIVED=========\n");
	printf("Target_gps: x=%f, y=%f, z=%f\n", test_buf.target_gps[0], test_buf.target_gps[1], test_buf.target_gps[2]);
	printf("============================\n");




}

int wb_send(from_bcknd_msg_t data) {

	data.msg_cnt = 0;
	data.time_stmp = 0;

    int len = tcp_send((char *) &data, sizeof(from_bcknd_msg_t));
	if (len < (int) sizeof(from_bcknd_msg_t)) {
		error("wb_send: Did not send complete struct");
	}

    return 0;
}

int wb_recv(to_bcknd_msg_t *data) {

	memset(data, 0, sizeof(to_bcknd_msg_t));

    int len = tcp_recv((char *)data, sizeof(to_bcknd_msg_t));
    if (len < (int) sizeof(to_bcknd_msg_t)) {
        error("wb_recv: did not receive complete data");
    }

    return 0;
}
