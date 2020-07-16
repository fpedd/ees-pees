#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <time.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <unistd.h>
#include <errno.h>

#include "../include/tcp.h"
#include "../include/util.h"

#define PORT "10201"
#define ADDR "127.0.0.1"

static int tcp_socket_fd;

// Sets up socket and connects to server with address in met
// Returns socket_fd
int tcp_connect() {

	struct addrinfo hints, *server_info;
	memset(&hints, 0, sizeof(hints));
	hints.ai_family = AF_UNSPEC;
	hints.ai_socktype = SOCK_STREAM;

	int stat_addrinfo = getaddrinfo(ADDR, PORT, &hints, &server_info);
	if (stat_addrinfo != 0) {
		fprintf(stderr, "ERROR(tcp): get addrinfo: %s'\n", strerror(errno));
		return -1;
	}

	// Set up socket for client
	tcp_socket_fd = socket(server_info->ai_family, server_info->ai_socktype, server_info->ai_protocol);
	if (tcp_socket_fd < 0) {
		fprintf(stderr, "ERROR(tcp): setup socket: %s'\n", strerror(errno));
		return -2;
	}

	// Connect client to server
	int connect_stat = connect(tcp_socket_fd, server_info->ai_addr, server_info->ai_addrlen);
	if (connect_stat != 0) {
		fprintf(stderr, "ERROR(tcp): connect to server: %s'\n", strerror(errno));
		return -3;
	}

	freeaddrinfo(server_info);

	return 0;
}

int tcp_send (char* data, int data_len) {

	int len = send(tcp_socket_fd, data, data_len, 0);
	if (len < 0) {
		fprintf(stderr, "ERROR(tcp): Error on send: %s'\n", strerror(errno));
		return -1;
	}
	return len;
}

int tcp_recv (char* buf, int buf_size) {

	int received = recv(tcp_socket_fd, buf, buf_size, 0);
	if (received < 0) {
		fprintf(stderr, "ERROR(tcp): Error on recv: %s'\n", strerror(errno));
		return -1;
	}
	return received;
}

int tcp_close () {

	close(tcp_socket_fd);
	return 0;
}
