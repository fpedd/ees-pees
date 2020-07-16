#include "webots/tcp.h"

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <sys/time.h>
#include <errno.h>

#include "util.h"

#define PORT "10200"

static int tcp_socket_fd;

// Sets up a server socket
// Returns Socket describtor
int tcp_init() {

	// Init structs for server_info and getaddrinfo()
	struct addrinfo hints, *server_info;
	memset(&hints, 0, sizeof(hints));
	hints.ai_family = AF_UNSPEC;
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_flags = AI_PASSIVE;

	// Fill server_info struct with parameters
	int stat_addrinfo = getaddrinfo(NULL, PORT, &hints, &server_info);
	if (stat_addrinfo != 0) {
		fprintf(stderr, "ERROR: tcp cant get addrinfo %s\n", strerror(errno));
		return stat_addrinfo;
	}

	// Set up socket
	tcp_socket_fd = socket(server_info->ai_family, server_info->ai_socktype, server_info->ai_protocol);
	if (tcp_socket_fd < 0) {
		fprintf(stderr, "ERROR: tcp open socket %s\n", strerror(errno));
		return tcp_socket_fd;
	}

	int enable = 1;
	if (setsockopt(tcp_socket_fd, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(int)) < 0) {
		fprintf(stderr, "ERROR: udp init setsockopt reuse failed '%s'\n", strerror(errno));
		return -3;
	}

	// Bind socket to address
	int bind_stat = bind(tcp_socket_fd, server_info->ai_addr, server_info->ai_addrlen);
	if (bind_stat != 0) {
		fprintf(stderr, "ERROR: tcp bind %s\n", strerror(errno));
		return bind_stat;
	}

	freeaddrinfo(server_info);

	return 0;
}

// Accecpt incoming Client (Robot)
int tcp_accept() {

	// Client socket
	struct sockaddr_storage their_addr;
	socklen_t addr_size = sizeof(their_addr);

	// Listen for connections
	int listen_stat = listen(tcp_socket_fd, 5);
	if(listen_stat != 0) {
		fprintf(stderr, "ERROR: tcp cant listen %s\n", strerror(errno));
		return listen_stat;
	}

	// Accept new connection with client
	tcp_socket_fd = accept(tcp_socket_fd, (struct sockaddr *)&their_addr, &addr_size);
	if(tcp_socket_fd < 0) {
		fprintf(stderr, "ERROR: tcp cant accept %s\n", strerror(errno));
		return tcp_socket_fd;
	}

	return 0;
}

int tcp_send (char* data, int data_len) {

	int len = send(tcp_socket_fd, data, data_len, 0);
	if (len < 0) {
		fprintf(stderr, "ERROR: tcp send %s\n", strerror(errno));
		return len;
	}
	return len;
}

int tcp_recv (char* buf, int buf_size) {

	int len = recv(tcp_socket_fd, buf, buf_size, 0);
	if (len < 0) {
		fprintf(stderr, "ERROR: tcp recv '%s'\n", strerror(errno));
		return len;
	}
	return len;
}

int tcp_close () {
	
	close(tcp_socket_fd);
	return 0;
}
