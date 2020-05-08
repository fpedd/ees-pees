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
#include <errno.h>


#define IP              "127.0.0.1"
#define CONTROL_PORT    6969
#define BACKEND_PORT    6970
#define SEND_TIMEOUT    100 // in ms
#define RECV_TIMEOUT    100 // in ms

static int sock_fd;
static struct sockaddr_in backend_addr;
static struct sockaddr_in controller_addr;

int udp_init() {

    backend_addr.sin_family = AF_INET;
    backend_addr.sin_port = htons(BACKEND_PORT);
    if (inet_aton(IP, &backend_addr.sin_addr) == 0) {
        fprintf(stderr, "\nERROR: udp init invalid backend_addr '%s'\n", IP);
        return -1;
    }

    sock_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock_fd < 0) {
        fprintf(stderr, "\nERROR: udp init socket '%s'\n", strerror(errno));
        return -2;
    }

    if (setsockopt(sock_fd, SOL_SOCKET, SO_REUSEADDR, &(int){1}, sizeof(int)) < 0) {
        fprintf(stderr, "\nERROR: udp init setsockopt reuse failed '%s'\n", strerror(errno));
        return -3;
    }

    struct timeval timeout;
    timeout.tv_sec = RECV_TIMEOUT / 1000;
    timeout.tv_usec = RECV_TIMEOUT * 1000;
    if (setsockopt(sock_fd, SOL_SOCKET, SO_RCVTIMEO, (char *)&timeout, sizeof(timeout)) < 0)  {
        fprintf(stderr, "\nERROR: udp init setsockopt timeout rcv failed '%s'\n", strerror(errno));
        return -4;
    }

    timeout.tv_sec = SEND_TIMEOUT / 1000;
    timeout.tv_usec = SEND_TIMEOUT * 1000;
    if (setsockopt(sock_fd, SOL_SOCKET, SO_SNDTIMEO, (char *)&timeout, sizeof(timeout)) < 0) {
        fprintf(stderr, "\nERROR: udp init setsockopt timeout snd failed '%s'\n", strerror(errno));
        return -5;
    }

    controller_addr.sin_family = AF_INET;
    controller_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    controller_addr.sin_port = htons(CONTROL_PORT);
    if (bind(sock_fd, (struct sockaddr *)(&controller_addr),
        sizeof(controller_addr)) < 0) {
        fprintf(stderr, "\nERROR: udp bind socket '%s'\n", strerror(errno));
        return -6;
    }

    return 0;
}

int udp_deinit() {
    close(sock_fd);
    return 0;
}

int udp_send(char *data, int data_len) {
    // TODO: add timeout
    int len = sendto(sock_fd, data, data_len, 0,
                     (struct sockaddr *)&backend_addr, sizeof(struct sockaddr_in));
    if (len < 0) {
        fprintf(stderr, "ERROR: udp send %s\n", strerror(errno));
        return len;
    }
    return len;
}

int udp_recv(char *buf, int buf_size) {
    // TODO: add timeout
    // struct timeval read_timeout;
    // read_timeout.tv_sec = 0;
    // read_timeout.tv_usec = 10;
    // setsockopt(socketfd, SOL_SOCKET, SO_RCVTIMEO, &read_timeout, sizeof read_timeout);

    int len = recvfrom(sock_fd, buf, buf_size, 0, NULL, NULL);
    if (len < 0) {
        fprintf(stderr, "\nERROR: udp recv '%s'\n", strerror(errno));
        return len;
    }
    return len;
}
