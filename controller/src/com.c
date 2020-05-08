#include "com.h"

#include <stdio.h>
#include <string.h>
#include <math.h>

#include "udp.h"
#include "util.h"

#define TIME_OFFSET_ALLOWED 1.0 // in seconds

static unsigned int msg_cnt_out;
static unsigned int msg_cnt_in;

int com_init() {

    udp_init();

    msg_cnt_out = 0;
    msg_cnt_in = (unsigned int)-1;

    // to_bcknd_msg_t first_msg;
    // memset(&first_msg, 0, sizeof(to_bcknd_msg_t));
    // com_send(first_msg);
    //
    // from_bcknd_msg_t first_msg_resp;
    // com_recv(&first_msg_resp);

    return 0;
}

int com_run(from_bcknd_msg_t *data) {
    // TODO
}

int com_send(to_bcknd_msg_t data) {

    data.msg_cnt = msg_cnt_out;
    data.time_stmp = get_time();

    int len = udp_send((char *)&data, sizeof(to_bcknd_msg_t));
    if (len < (int)sizeof(to_bcknd_msg_t)) {
        fprintf(stderr, "ERROR: com send too short, is %d, should %ld\n",
                len, sizeof(to_bcknd_msg_t));
        return -1;
    }

    msg_cnt_out += 2;

    return 0;
}

int com_recv(from_bcknd_msg_t *data) {
    memset(data, 0, sizeof(from_bcknd_msg_t));

    int len = udp_recv((char *)data, sizeof(from_bcknd_msg_t));
    if (len < (int)sizeof(from_bcknd_msg_t)) {
        fprintf(stderr, "ERROR: com recv too short, is %d, should %ld\n",
                len, sizeof(from_bcknd_msg_t));
        return -1;
    }

    if (fabs(get_time() - data->time_stmp) > TIME_OFFSET_ALLOWED) {
        fprintf(stderr, "ERROR: com recv time diff to big, local %f, remote %f, diff %f \n",
                get_time(), data->time_stmp, fabs(get_time() - data->time_stmp));
        return -2;
    }

    msg_cnt_in += 2;

    if (data->msg_cnt != msg_cnt_in) {
        fprintf(stderr, "ERROR: com recv msg_cnt_in %d does not match msg %lld \n",
                msg_cnt_in, data->msg_cnt);
        msg_cnt_in = data->msg_cnt;
        return -3;
    }

    return 0;
}
