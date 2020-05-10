#include <stdio.h>
#include <string.h>

#include "udp.h"
#include "com.h"
#include "pid.h"
#include "util.h"


int main(int argc, char **argv) {

    (void) argc;
    (void) argv;

    com_init();

    // testing communication
    while (1) {

        // create outgoing message
        to_bcknd_msg_t first_msg;
        memset(&first_msg, 0, sizeof(to_bcknd_msg_t));

        // add data
        for (int i=0; i<3; i++) {
            first_msg.target_gps[i] = i + 0.1;
        }
        for (int i=0; i<3; i++) {
            first_msg.actual_gps[i] = i + 0.2;
        }
        for (int i=0; i<3; i++) {
            first_msg.compass[i] = i + 0.3;
        }
        for (int i=0; i<DIST_VECS; i++) {
            first_msg.distance[i] = i + 0.4;
        }
        first_msg.touching = 69;

        // send
        com_send(first_msg);

        // wait a little bit
        delay(0.2);

        // create incomming message
        from_bcknd_msg_t first_msg_resp;

        // receive
        com_recv(&first_msg_resp);

        // print incomming message
        printf("cnt %lld, time %f, heading %f, speed %f \n",
               first_msg_resp.msg_cnt, first_msg_resp.time_stmp,
               first_msg_resp.heading, first_msg_resp.speed);

    }

    return 0;
}
