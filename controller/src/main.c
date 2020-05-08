
#include <stdio.h>

#include "udp.h"
#include "com.h"


int main(int argc, char **argv) {

    (void) argc;
    (void) argv;


    if (argc < 2) {
        fprintf(stderr, "\nERROR: not enough args\n");
    }

    com_init();
    // udp_init();
    to_bcknd_msg_t msg;
    msg.msg_cnt = 123456;
    msg.time_stmp = 69696969;
    msg.target_gps[0] = 69.6969;
    msg.target_gps[1] = 6969.69;
    msg.target_gps[2] = 6969696.9;
    udp_send((char *)&msg, 20);
    // udp_send((char *)&msg, sizeof(to_bcknd_msg_t));

    // udp_send(argv[1], 10);
    char buf[20];
    int len = udp_recv(buf, 20);
    udp_deinit();

    for(int i=0; i<len; i++) {
        printf("%c", buf[i]);
    }
    printf("\n");

    return 0;
}
