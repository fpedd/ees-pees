#include "com.h"

#include <stdio.h>

#include "udp.h"


int com_init() {

    udp_init();
    // printf("sizeof struct %ld \n", sizeof(to_bcknd_msg_t));

    return 0;
}

int com_send(to_bcknd_msg_t data);

int com_recv(from_bcknd_msg_t data);
