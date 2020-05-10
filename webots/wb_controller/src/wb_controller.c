#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <time.h>
#include <arpa/inet.h>  /* definition of inet_ntoa */
#include <netdb.h>      /* definition of gethostbyname */
#include <netinet/in.h> /* definition of struct sockaddr_in */
#include <sys/socket.h>
#include <sys/time.h>
#include <unistd.h> /* definition of close */

#include "tcp.h"
#include "wb_controller.h"
#include "util.h"

int wb_controller_init(){
	tcp_connect();
	return 0;
}

int wb_controller_test(){

	printf("Starting Coms on Webots Controller\n");
	wb_controller_init();

	from_bcknd_msg_t test_buf;
	memset(&test_buf, 0, sizeof(from_bcknd_msg_t));

	printf("receiving test_msg on Webots Controller\n");
	wb_recv(&test_buf);

	printf("===========RECEIVED=========\n");
	printf("Heading: %f\n", test_buf.heading);
	printf("Speed: %f\n", test_buf.speed);
	printf("============================\n");

	to_bcknd_msg_t test_msg;
	memset(&test_msg, 0, sizeof(to_bcknd_msg_t));

	test_msg.target_gps[0] = 5.55;
	test_msg.target_gps[1] = 6.66;
	test_msg.target_gps[2] = 7.77;


	printf("Sending test_msg on Webots Controller\n");
	wb_send(test_msg);

	return 0;
}

int wb_send(to_bcknd_msg_t data) {

	data.msg_cnt = 0;
	data.time_stmp = 0;

    int len = tcp_send((char *) &data, sizeof(to_bcknd_msg_t));
	if (len < (int) sizeof(to_bcknd_msg_t)) {
		error("wb_send: Did not send complete struct");
	}

    return 0;
}

int wb_recv(from_bcknd_msg_t *data) {

	memset(data, 0, sizeof(from_bcknd_msg_t));

    int len = tcp_recv((char *)data, sizeof(from_bcknd_msg_t));
    if (len < (int) sizeof(from_bcknd_msg_t)) {
        error("wb_recv: did not receive complete data");
    }

    return 0;
}
