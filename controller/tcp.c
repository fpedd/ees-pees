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

#define PORT 10200

// Sets up a server socket
// Returns Socket describtor
int init_tcp(){

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
	int socket_fd = socket(server_info->ai_family, server_info->ai_socktype, server_info->ai_protocol);
	if (socket_fd < 0) {
		error("error on socket startup");
	}

	//bind socket to address
	int bind_stat = bind(socket_fd, server_info->ai_addr, server_info->ai_addrlen);
	if (bind_stat != 0) {
		error("error on bind socket");
	}

	freeaddrinfo(server_info);    //not needed anymore

	return socket_fd;
}

// Accecpt incoming Client (Robot)
int accept_(int socket_fd) {

	//client socket
	struct sockaddr_storage their_addr;
	socklen_t addr_size = sizeof(their_addr);

	//listen for connections
	int listen_stat = listen(socket_fd, BACKLOG);
	if(listen_stat != 0)
	error("error on listen");

	//accept new connection with client
	int newsocket_fd = accept(socket_fd, (struct sockaddr *)&their_addr, &addr_size);
	if(newsocket_fd < 0)
	error("error on accept");

	return newsocket_fd;
}
