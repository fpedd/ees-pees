#include "udp.h"

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

#define IP              "127.0.0.1"
#define PORT            6969
#define SEND_TIMEOUT    100
#define RECV_TIMEOUT    100

static int socket = -1;
static sockaddr_in backend_addr;

int udp_init(int port, char *ip, int *sock) {

    struct addrinfo hints;
    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_DGRAM;
    hints.ai_flags = 0;
    hints.ai_protocol = 0;

    struct addrinfo *serv_info;
    int ret = getaddrinfo(NULL, port, &hints, &serv_info);
    if (ret != 0) {
        fprintf(stderr, "ERROR: udp init getaddrinfo: %s\n", gai_strerror(ret));
        return -1;
    }

    for(struct addrinfo *serv_info_itr = serv_info;
        serv_info_itr != NULL;
        serv_info_itr = serv_info_itr->ai_next) {

        if ((*sock = socket(serv_info_itr->ai_family, serv_info_itr->ai_socktype,
            serv_info_itr->ai_protocol)) < 0) {
            fprintf(stderr, "udp init socket try next %s\n", strerror(errno));
            continue;
        }

        if (bind(*sock, serv_info_itr->ai_addr, serv_info_itr->ai_addrlen) < 0) {
            close(*sock);
            fprintf(stderr, "udp init bind try next %s\n", strerror(errno));
            continue;
        }

        break;
    }

    if (serv_info_itr == NULL) {
        fprintf(stderr, "ERROR: udp init failed install socket\n");
        return -1;
    }

    freeaddrinfo(serv_info);



}

int udp_deinit(int sock) {
    close(sock);
    return 0;
}

int udp_send(int sock, char *data, int data_len) {
    int len = sendto(sock, data, data_len, 0, p->ai_addr, p->ai_addrlen);
    if (len  < 0) {
        fprintf(stderr, "ERROR: udp send %s\n", strerror(errno));
        return len;
    }
    return len;
}

int udp_recv(int sock, char **buf, int buf_size) {
    // struct timeval read_timeout;
    // read_timeout.tv_sec = 0;
    // read_timeout.tv_usec = 10;
    // setsockopt(socketfd, SOL_SOCKET, SO_RCVTIMEO, &read_timeout, sizeof read_timeout);

    struct sockaddr_storage addr;       // not using the receivers information yet
    socklen_t addr_len; = sizeof addr;  // ^

    int len = recvfrom(sock, buf, MAXBUFLEN, 0, (struct sockaddr *)&addr, &addr_len));
    if (len < 0) {
        fprintf(stderr, "ERROR: udp recv %s\n", strerror(errno));
        return len;
    }
    return len;
}
