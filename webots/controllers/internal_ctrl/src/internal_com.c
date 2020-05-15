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
#include "../include/util.h"


int internal_send(wb_to_ext_msg_t data) {

    int len = tcp_send((char *) &data, sizeof(wb_to_ext_msg_t));
	if (len < (int) sizeof(wb_to_ext_msg_t)) {
		error("wb_send: Did not send complete struct");
	}

    return 0;
}

int internal_recv(ext_to_wb_msg_t *data) {

	memset(data, 0, sizeof(ext_to_wb_msg_t));

    int len = tcp_recv((char *)data, sizeof(ext_to_wb_msg_t));
    if (len < (int) sizeof(ext_to_wb_msg_t)) {
        error("wb_recv: did not receive complete data");
    }

    return 0;
}
