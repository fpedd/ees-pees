#include "../include/internal_com.h"

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

#include "../include/tcp.h"

int internal_connect(){
	int ret_connect = tcp_connect();
	return ret_connect;
}

int internal_send_init(init_to_ext_msg_t data) {
	int len = tcp_send((char *) &data, sizeof(init_to_ext_msg_t));
	if (len < (int) sizeof(init_to_ext_msg_t)) {
		fprintf(stderr, "ERROR(internal_com): Did not send complete init data. Bytes send: %d'\n", len);
		return -1;
	}

	return 0;
}

int internal_send(wb_to_ext_msg_t data) {

	int len = tcp_send((char *) &data, sizeof(wb_to_ext_msg_t));
	if (len < (int) sizeof(wb_to_ext_msg_t)) {
		fprintf(stderr, "ERROR(internal_com): Did not send complete data. Bytes send: %d'\n", len);
		return -1;
	}

	return 0;
}

int internal_recv(ext_to_wb_msg_t *data) {

	memset(data, 0, sizeof(ext_to_wb_msg_t));

	int len = tcp_recv((char *)data, sizeof(ext_to_wb_msg_t));
	if (len < (int) sizeof(ext_to_wb_msg_t)) {
		fprintf(stderr, "ERROR(internal_com): Did not receive complete data. Bytes received: %d'\n", len);
		return -1;
	}

	return 0;
}
