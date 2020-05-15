#include "webots/tcp.h"

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

#include "util.h"

#define PORT "10200"

static int tcp_socket_fd;

// Sets up a server socket
// Returns Socket describtor
int tcp_init() {

	// init structs for server_info and getaddrinfo()
	struct addrinfo hints, *server_info;
	memset(&hints, 0, sizeof(hints));
	hints.ai_family = AF_UNSPEC;
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_flags = AI_PASSIVE;

	//fill server_info struct with parameters
	int stat_addrinfo = getaddrinfo(NULL, PORT, &hints, &server_info);
	if (stat_addrinfo != 0) {
		error("cant get addrinfo");
	}

	//set up socket
	tcp_socket_fd = socket(server_info->ai_family, server_info->ai_socktype, server_info->ai_protocol);
	if (tcp_socket_fd < 0) {
		error("error on socket startup");
	}

	//bind socket to address
	int bind_stat = bind(tcp_socket_fd, server_info->ai_addr, server_info->ai_addrlen);
	if (bind_stat != 0) {
		error("error on bind socket");
	}

	freeaddrinfo(server_info);    //not needed anymore

	return 0;
}

// Accecpt incoming Client (Robot)
int tcp_accept() {

	//client socket
	struct sockaddr_storage their_addr;
	socklen_t addr_size = sizeof(their_addr);

	//listen for connections
	int listen_stat = listen(tcp_socket_fd, 5);
	if(listen_stat != 0)
	error("error on listen");

	//accept new connection with client
	printf("TCP: Waiting for webot to connect...\n");
	tcp_socket_fd = accept(tcp_socket_fd, (struct sockaddr *)&their_addr, &addr_size);
	if(tcp_socket_fd < 0)
	error("error on accept");

	return 0;
}

int tcp_send (char* data, int data_len) {

	int len = send(tcp_socket_fd, data, data_len, 0);
	if (len < 0) {
		error("error on tcp_send");
	}
	return len;
}

int tcp_recv (char* buf, int buf_size) {

	int received = recv(tcp_socket_fd, buf, buf_size, 0);
	if (received < 0) {
		error("error on tcp_send");
	}
	return received;
}

int tcp_close () {
	close(tcp_socket_fd);
	return 0;
}
